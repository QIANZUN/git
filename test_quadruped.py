import json
import math
import unittest
from pathlib import Path
from unittest.mock import Mock
from quadruped import Gait, ServoOutput, pose, preflight


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(Path(__file__).with_name('robot.example.json').read_text())

    def test_ik_forward_round_trip(self):
        gait = Gait()
        for amplitude in (0, .5, 1):
            for i in range(1000):
                x, z = gait.foot(i/1000, amplitude)
                h, k = map(math.radians, gait.joints(i/1000, amplitude))
                self.assertAlmostEqual(x, gait.upper*math.sin(h)+gait.lower*math.sin(h+k))
                self.assertAlmostEqual(z, gait.upper*math.cos(h)+gait.lower*math.cos(h+k))

    def test_contact_boundary_velocity(self):
        gait = Gait()
        eps = 1e-6
        for boundary in (0, gait.duty):
            at = gait.foot(boundary)
            before, after = gait.foot(boundary-eps), gait.foot(boundary+eps)
            for j in (0, 1):
                self.assertAlmostEqual((at[j]-before[j])/eps,
                                       (after[j]-at[j])/eps, delta=.01)

    def test_documented_sdk_mapping(self):
        board = Mock()
        out = ServoOutput(self.config['servos'], board)
        out.write({l:(0,24) for l in ('FL','FR','RL','RR')}, 40)
        self.assertEqual(board.setBusServoPulse.call_count,8)
        self.assertEqual(board.setBusServoPulse.call_args_list[0].args,(1,500,40))
        self.assertEqual(board.setBusServoPulse.call_args_list[1].args,(2,600,40))

    def test_invalid_last_joint_sends_nothing(self):
        board=Mock()
        out=ServoOutput(self.config['servos'],board)
        positions=pose(Gait(),0,0)
        positions['RR']=(0,240)
        with self.assertRaises(ValueError):
            out.write(positions)
        board.setBusServoPulse.assert_not_called()

    def test_duplicate_ids_rejected(self):
        self.config['servos']['RR']['knee']['id']=1
        with self.assertRaises(ValueError):
            ServoOutput(self.config['servos'])

    def test_full_preflight(self):
        preflight(Gait(**self.config['gait']),ServoOutput(self.config['servos']))

    def test_unreachable_rejected(self):
        with self.assertRaises(ValueError):
            Gait(height=200).validate()


if __name__=='__main__':
    unittest.main()
