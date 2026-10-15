# 叉形轴承支撑入门

## 先看这些图片

以下均为 SpotMicroESP32 原项目链接，未复制其文件。

1. 舵盘驱动侧装配：
https://github.com/michaelkubina/SpotMicroESP32/blob/master/assembly/images/006_servohornmount_post_sideview.png
2. 另一侧轴承装配前：
https://github.com/michaelkubina/SpotMicroESP32/blob/master/assembly/images/007_ballbearingmount_pre.png
3. 另一侧轴承装配后：
https://github.com/michaelkubina/SpotMicroESP32/blob/master/assembly/images/007_ballbearingmount_post_sideview.png
4. 分步装配教程 Upper Leg：
https://github.com/michaelkubina/SpotMicroESP32/blob/master/assembly/README.md#upper-leg
5. 可编辑 FreeCAD 零件：
https://github.com/michaelkubina/SpotMicroESP32/tree/master/parts/SpotMicroESP32_parts_v1_0_0/freecad

在 FreeCAD 目录查找 Limb_Ball_Bearing_Mount、Limb_Servohorn_Mount、Shoulder_Joint_Ball_Bearing_Pin。
项目使用 MG996R 和 625ZZ 轴承（5×16×5 mm），不是已验证适配 HTD-35H 的方案。
图中是舵盘驱动侧＋同轴从动轴承侧，说明双侧支撑原理；不是两个完全独立外部轴承的通用叉耳接头。

## 两种结构，不要混淆

A. 舵机驱动关节：舵机固定在一个构件上，舵盘固定另一个构件的叉臂；另一侧用同轴的从动轴/轴承支撑。不能用一根螺栓横穿舵机壳体。
外部从动轴必须与输出轴同轴，但不能假设舵机背面现成孔就是承力轴；按 CAD 与厂家结构确认或另做支架。

B. 连杆之间的被动转动关节：固定叉耳两侧支撑一根光轴或肩螺栓，中间连杆中的轴承外圈随连杆转动。
光轴与内圈配合，轴承外圈装入中间连杆的轴承座；转动来自内外圈相对运动，不是螺纹摩擦。
两个轴承之间可设置与内圈匹配的精确隔套，端部垫圈仅接触内圈；正确尺寸的隔套和止挡避免锁紧后给轴承施加过大轴向预载。
螺纹段不能作为轴承运行配合面。轴端可用挡圈/轴端螺钉限位，或使用肩长与夹持堆叠匹配的肩螺栓。

## SolidWorks 最小建模顺序

1. 新建骨架草图，画唯一的旋转轴线与两根连杆的中心线。
2. 先确定轴承规格，再建立轴承座、轴肩、外圈挡肩/压盖。
3. 建立 U 形叉耳，确保两侧孔同轴；根部做圆角与加强筋，尺寸需受力校核。
4. 插入轴承、隔套、轴和锁紧件，检查锁紧力路径与轴向空间。
5. 装配中固定一个连杆，只保留一个绕轴旋转自由度，转完整个所需角度并检查干涉。
6. 先打印轴承座与叉耳试件，验证配合、同轴度和锁紧后的自由转动，再做整条腿。

轴承外圈轴向定位与内圈轴向定位需要分别设计。不要用锁紧螺母把整个轴承跨内外圈硬夹，也不要让垫圈摩擦轴承密封盖或旋转连杆。
打印孔不应凭标称尺寸直接确定过盈量；需试件校准，过盈过大会使轴承变形、打印座开裂或转动发涩。

## 可搜索的术语

叉耳转动关节、双剪切销轴连接、舵机双侧支撑、舵机同轴从动轴承、肩螺栓轴承连接。
英文：clevis pivot bearing、double shear pivot、servo idler bearing、shoulder bolt bearing pivot。

这些图纸可借鉴结构，不能照搬原项目的螺丝规格到 HTD-35H 舵盘。舵盘中心螺纹与紧固深度应按厂家说明确认。
