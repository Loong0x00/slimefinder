# SlimeFinder Mod for Fabric 1.21

一个用于查找史莱姆区块的Fabric模组，适用于Minecraft 1.21。

## 功能特性

- 使用原版Minecraft的史莱姆区块算法
- 基于世界种子准确检测史莱姆区块
- 支持指定半径范围扫描
- 将结果保存到文件中

## 使用方法

### 命令

```
/slimefinder save <radius>
```

- `<radius>`: 扫描半径（1-100个区块）
- 以玩家当前位置为中心进行扫描
- 结果保存到 `.minecraft/saves/<world_name>/slime_chunks.txt`

### 示例

```
/slimefinder save 10
```

这将扫描玩家周围10个区块半径内的所有史莱姆区块。

## 输出格式

文件中每行包含一个史莱姆区块的坐标：
```
Chunk (x,z)
Chunk (x,z)
...
```

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