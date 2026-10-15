#!/usr/bin/env python3
"""Open-loop planar quadruped trot, dry-run by default; optional Hiwonder Board SDK."""
import argparse
import importlib
import json
import math
import time
from dataclasses import dataclass

LEGS = ('FL', 'FR', 'RL', 'RR')
OFFSETS = {'FL': 0.0, 'RR': 0.0, 'FR': 0.5, 'RL': 0.5}


@dataclass
class Gait:
    upper: float = 80.0
    lower: float = 80.0
    height: float = 125.0
    stride: float = 20.0
    lift: float = 10.0
    frequency: float = 1.0
    duty: float = 0.60

    def validate(self):
        if not all(math.isfinite(v) for v in vars(self).values()):
            raise ValueError('Non-finite gait parameter')
        if not (self.upper > 0 and self.lower > 0 and self.height > self.lift >= 0
                and self.stride >= 0 and 0 < self.frequency <= 4 and 0.5 <= self.duty < 1):
            raise ValueError('Invalid dimensions or gait settings')
        for i in range(2001):
            self.joints(i / 2000, 1.0)

    def foot(self, phase, amplitude=1.0):
        p = phase % 1.0
        if p < self.duty:
            x = self.stride * (0.5 - p / self.duty)
            z = self.height
        else:
            u = (p - self.duty) / (1 - self.duty)
            # Match stance velocity at both ends (small swing overshoot is intentional).
            blend = 10*u**3 - 15*u**4 + 6*u**5
            v = self.stride * (1 - self.duty) / self.duty
            x = -self.stride/2 - v*u + (self.stride + v)*blend
            z = self.height - amplitude*self.lift*math.sin(math.pi*u)**4
        return amplitude*x, z

    def joints(self, phase, amplitude=1.0):
        # Hip origin; x forward, z down. Knee=0 means straight leg.
        x, z = self.foot(phase, amplitude)
        r = math.hypot(x, z)
        if not abs(self.upper-self.lower)+1 < r < self.upper+self.lower-1:
            raise ValueError(f'Foot outside IK workspace: ({x:.2f}, {z:.2f})')
        c = (r*r-self.upper**2-self.lower**2)/(2*self.upper*self.lower)
        knee = math.acos(max(-1, min(1, c)))
        hip = math.atan2(x, z)-math.atan2(self.lower*math.sin(knee),
                                        self.upper+self.lower*math.cos(knee))
        return math.degrees(hip), math.degrees(knee)


def pose(gait, phase, amplitude):
    return {leg: gait.joints(phase+OFFSETS[leg], amplitude) for leg in LEGS}


class ServoOutput:
    """Map geometric degrees to HTD-35H position units, then call documented SDK."""
    def __init__(self, calibration, board=None):
        self.cal, self.board = calibration, board
        ids = []
        for leg in LEGS:
            for joint in ('hip', 'knee'):
                c = calibration[leg][joint]
                if (type(c['id']) is not int or not 0 <= c['id'] <= 253
                    or c['direction'] not in (-1, 1)
                    or not all(math.isfinite(c[k]) for k in ('zero', 'min', 'max'))
                    or not 0 <= c['min'] < c['max'] <= 1000
                    or not 0 <= c['zero'] <= 1000):
                    raise ValueError(f'Invalid calibration: {leg}/{joint}')
                ids.append(c['id'])
        if len(set(ids)) != 8:
            raise ValueError('Eight unique servo IDs are required')

    def angles(self, positions):
        commands = []
        for leg in LEGS:
            for joint, angle in zip(('hip', 'knee'), positions[leg]):
                c = self.cal[leg][joint]
                target = c['zero']+c['direction']*angle/0.24
                if not math.isfinite(target) or not c['min'] <= target <= c['max']:
                    raise ValueError(f'{leg}/{joint}: position {target:.2f} exceeds limits')
                target = round(target)
                if not c['min'] <= target <= c['max']:
                    raise ValueError('Rounded position exceeds limits')
                commands.append((c['id'], target))
        return commands

    def write(self, positions, duration_ms=40):
        commands = self.angles(positions)  # Validate every target before first transmission.
        if self.board is not None:
            for servo_id, target in commands:
                self.board.setBusServoPulse(servo_id, target, duration_ms)
        return commands


def preflight(gait, output):
    gait.validate()
    for amplitude in (0, .25, .5, .75, 1):
        for i in range(1000):
            output.angles(pose(gait, i/1000, amplitude))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', help='Gait and servo calibration JSON')
    parser.add_argument('--hardware', action='store_true')
    parser.add_argument('--seconds', type=float, default=10)
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds < 4:
        parser.error('--seconds must be finite and at least 4 (includes start/stop ramps)')
    config = {}
    if args.config:
        with open(args.config, encoding='utf-8') as f:
            config = json.load(f)
    gait = Gait(**config.get('gait', {}))
    gait.validate()
    output = ServoOutput(config['servos']) if 'servos' in config else None
    if output:
        preflight(gait, output)
    if args.hardware:
        if output is None or config.get('calibrated') is not True:
            parser.error('Hardware requires measured config with calibrated=true')
        # No reads here: timeout behavior of the supplied SDK must first be verified on Pi.
        # User must support robot in the documented initial stand before starting.
        board = importlib.import_module('Board')
        if not callable(getattr(board, 'setBusServoPulse', None)):
            parser.error('Board SDK lacks documented setBusServoPulse API')
        output.board = board
        output.write(pose(gait, 0, 0), duration_ms=2000)
        time.sleep(2)
    print('Hiwonder SDK output active' if args.hardware else 'Dry run; no hardware output')
    print('Initial stand:', pose(gait, 0, 0))
    phase = 0.0
    started = last = time.monotonic()
    next_report = 0
    try:
        while True:
            cycle_start = time.monotonic()
            elapsed, dt = cycle_start-started, cycle_start-last
            last = cycle_start
            if elapsed >= args.seconds:
                break
            if args.hardware and dt > .15:
                raise RuntimeError('Loop delayed >150 ms; stopped sending targets')
            ramp = max(0, min(1, elapsed/2, (args.seconds-elapsed)/2))
            amplitude = ramp*ramp*(3-2*ramp)
            phase = (phase+dt*gait.frequency) % 1
            positions = pose(gait, phase, amplitude)
            commands = output.write(positions) if output else None
            if elapsed >= next_report:
                print(f't={elapsed:.1f}s amplitude={amplitude:.2f} FL={positions["FL"]} targets={commands}')
                next_report += 1
            # 25 Hz; avoid bursts of catch-up commands after overruns.
            time.sleep(max(0, .04-(time.monotonic()-cycle_start)))
        if output:
            output.write(pose(gait, 0, 0), duration_ms=500)
    except KeyboardInterrupt:
        print('Interrupted: no more commands; servos retain their last targets.')
    # Do not automatically unload: a supported robot may collapse when torque is removed.
    # Communication failure can leave a partial frame of eight joints. Use physical power stop.


if __name__ == '__main__':
    main()
