# 四足机器人开发进度与交接

## 当前成果

目标：树莓派控制四足机器人，每腿 2 个 HTD-35H 舵机，实现小跑。
已完成对角小跑开环原型、足端轨迹、平面二连杆逆运动学、舵机位置映射、配置预检、官方 Board SDK 输出适配。

- 程序：../quadruped.py
- 配置模板：../robot.example.json
- 测试：../test_quadruped.py
- 标定与运行说明：running.md
- CAD 测量及硬件资料摘要：hardware-analysis.md
- 零件三视投影：leg_geometry.png

## 验证结果

执行 `python3 -m unittest -v test_quadruped.py`，7 项测试全部通过。
执行 `python3 quadruped.py --config robot.example.json --seconds 4`，完整离线运行通过。
默认模板执行 --hardware 会被拒绝，因为 calibrated=false。
SDK 测试使用模拟对象，未验证真实树莓派、SDK、串口、电源或负载。

## 已确认

HTD-35H 使用 115200 波特率半双工 UART，不适用 PCA9685 PWM。
位置 0–1000 对应 0–240°；SDK 写接口为 Board.setBusServoPulse(id, position, time_ms)。
开发 PDF 第 4 页代码截图使用 import Board，第 9 页代码截图明确三参数写接口。
上传的装配截图提供连接关系参考，不含可用于精确测量的尺寸。
上下腿 STEP 已解析；112.015 mm 是下腿轴线到局部 Y 极点的距离，不能未经确认就当作最终有效腿长。

## 明早继续

1. 确认髋膝两轴是否平行；当前运动学要求每条腿在前后竖直平面运动。
2. 测量髋轴到膝轴、膝轴到实际足端接触点的距离，填入配置；80/80 mm 是示例。
3. 提供官方 Raspberry_BusServo_demo 中 Board.py 及依赖，并确认实际用的是对应扩展板还是 BusLinker USB 板。
4. 逐只设置 8 个独立舵机 ID，标定四腿关节方向、数学零位对应的位置值及机械限位。
5. 在支架托起机身时验证单关节、静止站姿，再小幅低速试步；完成标定后才设置 calibrated=true。

## 已知限制

本程序是开环小跑原型，不是已验证的动态跑步控制器。
没有 IMU 稳定、接触检测、温度/电压保护、反馈位置监测或独立硬件看门狗。
SDK 是逐只下发，非严格同步；需要实测 8 只舵机的通信时延和循环频率。
Ctrl+C 仅停止发送后续目标，舵机会继续保持/完成最后目标；应配备物理舵机电源断开装置。

## 原始资料记录

本次提交保存生成的代码、配置、测试、投影图和分析结果，不包含聊天附件原件。
已收到的附件包括 CAD.zip、装配体1.zip、装配体1.STEP、上下腿 SLDPRT、上下腿 STEP、
HTD-35H.stp.STEP、HTD-35H Bus Servo User Manual.pdf、04 Raspberry Pi Development.pdf。
大型整机 ZIP/STEP 超过读取工具 32 MiB 限制；SolidWorks 原生文件无法可靠解析。
原始 CAD 和厂家 PDF 请保留本地备份；厂家 SDK 尚未收到。
