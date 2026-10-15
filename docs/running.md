# 树莓派四足小跑原型

程序采用平面二连杆模型：髋、膝轴应平行；不包含髋外展自由度。
截图可帮助核对连接方向，但不能可靠给出轴距、四腿镜像关系或转向。
若实际关节轴不平行，需更换运动学模型再运行。

- FL 左前与 RR 右后同相，FR 右前与 RL 左后相差半周期。
- 支撑相占 60%，足端向后匀速运动；摆动相用五次曲线向前回摆，并匹配两端速度，抬脚使用 sin⁴ 曲线。
- 髋坐标原点，x 向前、z 向下；膝角为 0 时腿伸直，当前选择正膝角解。
- 目标更新 25 Hz，首尾各 2 秒渐变。示例频率 1 Hz、步长 20 mm、抬脚 10 mm。
- 开环运动，不保证平衡或实机跑步；没有 IMU 稳定、地面接触检测和动力学控制。

## 离线运行

```sh
cd /workspace/git
python3 quadruped.py --config robot.example.json --seconds 8
python3 -m unittest -v test_quadruped.py
```

## 标定配置

复制 robot.example.json 为 robot.local.json。示例的 80/80 mm 腿长、ID 1–8、zero=500 和方向全 +1 都是演示值，不是从装配确定的参数。

- gait.upper / lower：实际两轴间距离与膝轴到选定足端点距离，单位 mm；若有平面外偏移需重新建模。
- height：髋轴到水平地面的竖直距离；stride 是完整前后行程，不是半行程。
- id：先用厂家工具逐只设置不同 ID，再串接；程序不改写 ID。
- zero：该关节数学角度为 0 时对应的总线位置值，不一定是 500。
- direction：数学正转使位置值增加则 +1，否则 -1。
- min / max：实测无碰撞的总线位置限制，范围 0–1000。
- calibrated：完成结构、零位、方向、角度范围核对后才改为 true。

换算：position = zero + direction × angle_deg / 0.24。
镜像安装可用 direction 和 zero 映射，但不能用方向参数修正非平行轴机构。
预检会采样整周期和渐变幅度，超限直接报错，不静默裁剪。采样不等于连续碰撞或速度/力矩验证。

## 树莓派接入

04 Raspberry Pi Development.pdf 第 4 页截图使用 import Board；第 9 页明确 setBusServoPulse(id, position, time_ms)。
本程序通过这套 SDK 控制，不自行构造串口帧。第 10–12 页正文有把读写 API 名混用的文字错误，不能照抄作为底层协议。

将官方 Raspberry_BusServo_demo 中的 Board.py 及其依赖放在程序旁边，或加入 PYTHONPATH。
SDK 不是本项目自带文件；需要使用与实际扩展板兼容的官方版本。BusLinker USB 板是否兼容此 SDK 尚未验证。

先按厂家示例验证单舵机位置回读、ID、温度、电压，确保 SDK 读操作有可用超时。
本程序尚未集成读反馈，也不能检测舵机失联、温升或低压；Linux/SDK 阻塞时没有独立硬件看门狗。

完成配置后，在支架上托起机身、使各关节靠近程序打印的 Initial stand；准备可直接切断舵机电源的开关，再运行：

```sh
python3 quadruped.py --config robot.local.json --hardware --seconds 8
```

首次用更小 stride/lift 和更低 frequency。初始站姿给 2000 ms 到位时间，但不是从实测当前位置闭环规划，不能从任意折叠姿态启动。
正常结束发送静止站姿并保留力矩；Ctrl+C 停止后续目标，舵机仍可能完成最后一次目标运动。
异常不会自动卸力，避免机身掉落；需要操作者托住机身或使用物理断电。
八只舵机由 SDK 逐个写入，不是严格同步启动；总线时延和 SDK 内部 sleep 需要在树莓派实测。
若一帧发送耗时超过 40 ms，不能达到目标更新率；程序不补发积压帧，循环间隔超过 150 ms 会报错停止后续目标。

## 验证范围

云端可验证 IK、轨迹连续性、限位预检及 SDK 参数映射；模拟 SDK 测试不证明实际总线可用。
实际腿长、硬件兼容性、受载速度和稳定性仍需完成标定与台架测试。
