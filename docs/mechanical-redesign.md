# 机械改版参考：抽拉托盘与连杆腿

## 建议方案

保留 HTD-35H 时，先设计刚性箱形机身、抽拉式电池/电子托盘、带独立轴承支撑的可拆腿模块。
不要把抽拉维护托盘与运行中主动伸缩的躯干混为一谈：后者需要额外执行器、位置检测与变化的机身运动学，目前不建议作为首版。
抽拉式承力机身可以做停机调长，但运动前必须用定位销/止口和螺栓锁紧；运动过程中依赖松配滑轨承受四腿交变力，容易产生扭转和间隙。

## 已核对的开源入口

### SpotMicroESP32：先学舵机安装、轴承和打印结构

https://github.com/michaelkubina/SpotMicroESP32

零件：https://github.com/michaelkubina/SpotMicroESP32/tree/master/parts/SpotMicroESP32_parts_v1_0_0

装配：https://github.com/michaelkubina/SpotMicroESP32/tree/master/assembly

已核对仓库含 FreeCAD .FCStd 源文件、STL、装配教程和少量改装 STEP。
关键零件名：Limb_Ball_Bearing_Mount、Limb_Servohorn_Mount、Shoulder_Joint_Servomount、Chassis_Side、Foot_Tip。
FreeCAD 源文件可用 FreeCAD 打开后导出 STEP，再导入 SolidWorks。STL 更适合打印和观察，不适合作为精确参数化改版起点。
原舵机与 HTD-35H 不同，安装孔、轴高、舵盘及活动间隙均须重建，不能照比例放大直接用。

### Stanford Doggo：两驱动关节的闭链连杆腿

https://github.com/Nate711/StanfordDoggoProject

模型入口记录：https://github.com/Nate711/StanfordDoggoProject/blob/master/DoggoHardware/FullCAD

仓库中该文件链接 Version 2 Fusion 360 模型：https://a360.co/30j7ANn
已核对 Git 文件中的链接，但没有验证 Autodesk 外部页面的下载可用性。
适合研究驱动靠近髋部、减轻腿部远端重量、闭链机构的工作空间与装配。
原项目采用无刷电机和 ODrive，不能把其动态性能套用到 HTD-35H 上。
该旧项目已标明停止维护，不影响其机械方案的参考价值。

### mjbots quad：机身模块、托盘和远端传动

https://github.com/mjbots/quad

硬件目录：https://github.com/mjbots/quad/tree/master/hw （若默认分支变化，从仓库根目录进入 hw）

已核对存在 hw/chassis_a2/battery_tray.3mf、computer_tray.3mf、rail_carrier.3mf，以及腿部、张紧器、皮带轮相关打印文件。
这些文件可供观察模块化结构，不能仅凭文件名认定它采用你所需的抽拉/锁止结构。
README 给出 Fusion 360 总装入口：https://a360.co/4bPBs6g （外部模型下载未验证）。
此项目使用专用关节执行器，不是 HTD-35H 的直接替换设计。

### Stanford Pupper：整机布局和控制架构补充

https://github.com/stanfordroboticsclub/StanfordQuadruped

装配文档：https://pupper.readthedocs.io/en/latest/

已核对上述 Git 仓库主要是代码，机械文件需要从装配文档继续查找，不应当把该仓库说成完整 CAD 包。
旧版 Pupper 已停止维护。

## 抽拉式托盘如何建模

先建立机身骨架：四个髋轴的位置、上下承力板、横梁和螺栓连接。
固定四个髋部承力接口；让电池和计算板从机身前/后方抽出，不让托盘承担腿部主要载荷。
托盘采用双侧导向、端部止挡、防脱结构及螺钉/锁扣；电池另设固定带。
连接器尽量不承担机械定位力；活动线束保留弯曲半径和防磨空间。
IMU 刚性安装在固定机身、靠近参考重心处，不装在有间隙的抽拉托盘上。
打印滑配间隙不能一概而论，先打印短段试配件，再确定整机间隙。

## 连杆腿如何建模

先在二维草图中建关节中心和固定长度连杆，再加旋转配合、驱动和限位；确认自由度以后再画实体外形。
可选串联髋膝、平行四边形远端传动、五杆并联。连杆数不能直接等同自由度，需检查约束和装配分支。
如果保留串联髋膝模型但用传动连杆远置膝电机，仍需额外计算“膝关节角→电机角”的传动映射。
若改为五杆机构，需要重写闭链正逆运动学，不能沿用 quadruped.py 的二连杆解直接下发。

设计检查：全周期运动干涉、闭链死点、连杆共线奇异点、机械限位、轴承同轴度、传动间隙、线束和脚端防滑。
让关节由独立轴承/轴承座承担弯矩，避免把所有冲击载荷交给舵机输出轴。
远置驱动的收益是减少远端惯量，但会增加传动件、摩擦和间隙；不一定提高最高速度。
打印件应按受力方向安排层纹和加强筋，轴/螺栓/轴承继续使用金属件。

## 推荐迭代顺序

1. 先完成刚性机身与可抽托盘布局。
2. 做一条腿的二维机构与工作空间检查。
3. 打印单腿，在台架上完成标定、受载跟踪和温升测试。
4. 根据测试结果再复制四腿；不要先打印整机再发现传动比例或轴距不合适。

如果主要目标仍是侧向移动，需要先确定各腿运动平面：侧向两自由度腿可用于优先横移，三自由度腿更适合前进、横移与转向兼顾。
这些开源参考不构成 HTD-35H 达到 50 m/min 的证据。修改与分发第三方文件时分别遵守其原许可证。
