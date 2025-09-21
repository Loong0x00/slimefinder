# SlimeFinder Mod for Fabric 1.21

一个用于查找史莱姆区块的Fabric模组，适用于Minecraft 1.21。

## 功能特性

- 使用原版Minecraft的史莱姆区块算法
- 基于世界种子准确检测史莱姆区块
- 支持指定半径范围扫描（**无上限限制**）
- **流式处理技术**：实时写入硬盘，避免内存溢出
- 将结果保存到文件中，包含详细的区块和方块坐标信息
- 附带Python分析工具，用于优化史莱姆农场位置

## 使用方法

### 命令

```
/slimefinder save <radius>
```

- `<radius>`: 扫描半径（最小值为1，**无上限限制**）
- 以玩家当前位置为中心进行扫描
- 结果保存到 `.minecraft/saves/<world_name>/slime_chunks.txt`

### 示例

```
/slimefinder save 10
```

这将扫描玩家周围10个区块半径内的所有史莱姆区块。

## 输出格式

文件包含详细的史莱姆区块信息，格式如下：
```
Slime Chunks found around chunk (0,0) with radius 1000
Format: Chunk (x,z) - Block coordinates (x1,z1) to (x2,z2)
=====================================
Chunk (-15,23) - Blocks (-240,368) to (-225,383)
Chunk (42,-8) - Blocks (672,-128) to (687,-113)
...
=====================================
Total slime chunks found: 1247
```

### 性能优化

- **流式处理**：不将所有数据存储在内存中，支持任意大的扫描范围
- **实时写入**：每找到一个史莱姆区块立即写入文件
- **进度反馈**：每处理100个史莱姆区块在日志中显示进度
- **数据安全**：即使程序中断，已处理的数据也已保存

## 史莱姆区块算法

本模组使用Minecraft原版的史莱姆区块检测算法：

```java
Random random = new Random(worldSeed
    + (long) (chunkX * chunkX * 0x4c1906)
    + (long) (chunkX * 0x5ac0db)
    + (long) (chunkZ * chunkZ) * 0x4307a7L
    + (long) (chunkZ * 0x5f24f) ^ 0x3ad8025fL);
return random.nextInt(10) == 0;
```

这确保了与原版游戏完全一致的史莱姆区块检测结果。

## 史莱姆区块分析工具

项目包含一个Python分析工具 `slime_analyzer.py`，用于分析史莱姆区块分布并优化农场位置。

### 功能特性

- **区域优化分析**：在指定大小的区域内找到史莱姆区块最多或最少的位置
- **约束条件支持**：支持坐标整除约束（如区块对齐）
- **距离优化**：在多个最优解中选择距离原点最近的位置
- **高性能算法**：使用二维前缀和算法，支持大范围快速扫描
- **进度显示**：使用tqdm显示扫描进度

### 使用方法

1. **安装依赖**：
```bash
pip install numpy tqdm
```

2. **运行分析**：
```python
# 导入工具
from slime_analyzer import *

# 解析史莱姆区块文件
slime_chunks = parse_slime_file("slime_chunks.txt")

# 找到17x17区域内史莱姆区块最多的位置
best_area, best_count, best_chunks = find_best_area(slime_chunks, 17, 17, mode="max")
print(f"最多史莱姆区块区域左上角: {best_area}, 数量: {best_count}")

# 找到16x8区域内史莱姆区块最少的位置（适合建造非史莱姆农场）
best_area, best_count, best_chunks = find_best_area(slime_chunks, 16, 8, mode="min")
print(f"最少史莱姆区块区域左上角: {best_area}, 数量: {best_count}")

# 带约束条件的搜索（左上角坐标必须能被8整除）
best_area, best_count, best_chunks, candidates = find_best_area_with_constraint(
    slime_chunks, area_w=16, area_h=8, mode="min", align=8
)
```

### 应用场景

- **史莱姆农场优化**：找到史莱姆区块密度最高的区域建造农场
- **建筑规划**：找到史莱姆区块最少的区域避免史莱姆干扰
- **区块对齐**：确保农场或建筑与区块边界对齐
- **多方案比较**：获取所有最优解候选进行比较

## 技术要求

- Minecraft 1.21
- Fabric Loader 0.17.2+
- Fabric API 0.102.0+1.21
- Java 21+

## 编译

```bash
./gradlew build
```

## 安装

1. 确保已安装Fabric Loader
2. 将编译好的jar文件放入 `.minecraft/mods/` 目录
3. 启动游戏

## 许可证

CC0-1.0