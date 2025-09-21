import re
import math
import numpy as np
from tqdm import tqdm

def parse_slime_file(filename):
    """
    解析史莱姆区块文件，返回所有区块坐标 (chunkX, chunkZ)
    """
    slime_chunks = []
    pattern = re.compile(r"Chunk\s+\((-?\d+),(-?\d+)\)")
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                x, z = int(match.group(1)), int(match.group(2))
                slime_chunks.append((x, z))
    return slime_chunks


def build_prefix_matrix(slime_chunks):
    """
    构建二维前缀和矩阵
    """
    xs = [c[0] for c in slime_chunks]
    zs = [c[1] for c in slime_chunks]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)

    width = max_x - min_x + 1
    height = max_z - min_z + 1

    grid = np.zeros((width, height), dtype=np.int32)
    for cx, cz in slime_chunks:
        grid[cx - min_x, cz - min_z] = 1

    prefix = grid.cumsum(axis=0).cumsum(axis=1)
    return prefix, min_x, min_z, grid


def query_prefix(prefix, min_x, min_z, x0, z0, w, h):
    """
    用前缀和查询窗口 (x0,z0) → (x0+w-1, z0+h-1) 内史莱姆区块数量
    """
    x1 = x0 - min_x
    z1 = z0 - min_z
    x2 = x1 + w - 1
    z2 = z1 + h - 1

    total = prefix[x2, z2]
    if x1 > 0:
        total -= prefix[x1 - 1, z2]
    if z1 > 0:
        total -= prefix[x2, z1 - 1]
    if x1 > 0 and z1 > 0:
        total += prefix[x1 - 1, z1 - 1]
    return total


def find_best_area_with_constraint(slime_chunks, area_w, area_h, mode="max", align=1):
    prefix, min_x, min_z, grid = build_prefix_matrix(slime_chunks)

    width = prefix.shape[0]
    height = prefix.shape[1]

    best_count = None
    candidates = []  # 存储所有最优解候选
    total_windows = (width - area_w + 1) * (height - area_h + 1)

    with tqdm(total=total_windows, desc="扫描进度") as pbar:
        for x0 in range(min_x, min_x + width - area_w + 1):
            for z0 in range(min_z, min_z + height - area_h + 1):

                # 整除约束
                if x0 % align != 0 or z0 % align != 0:
                    pbar.update(1)
                    continue

                count = query_prefix(prefix, min_x, min_z, x0, z0, area_w, area_h)

                if best_count is None:
                    best_count = count
                    candidates = [(x0, z0)]
                else:
                    if mode == "max" and count > best_count:
                        best_count = count
                        candidates = [(x0, z0)]
                    elif mode == "max" and count == best_count:
                        candidates.append((x0, z0))
                    elif mode == "min" and count < best_count:
                        best_count = count
                        candidates = [(x0, z0)]
                    elif mode == "min" and count == best_count:
                        candidates.append((x0, z0))

                pbar.update(1)

    # 在候选里选距离原点最近的
    best_area = min(candidates, key=lambda pos: math.sqrt(pos[0]**2 + pos[1]**2))

    # 收集最佳区域内的史莱姆区块
    best_chunks = []
    bx, bz = best_area
    for cx, cz in slime_chunks:
        if bx <= cx < bx + area_w and bz <= cz < bz + area_h:
            best_chunks.append((cx, cz))

    return best_area, best_count, best_chunks, candidates

def format_chunk_output(chunks):
    """
    把区块坐标转换成字符串，包括区块坐标和方块范围
    """
    lines = []
    for cx, cz in sorted(chunks):
        x1, z1 = cx * 16, cz * 16
        x2, z2 = x1 + 15, z1 + 15
        lines.append(f"Chunk ({cx},{cz}) - Blocks ({x1},{z1}) to ({x2},{z2})")
    return "\n".join(lines)


if __name__ == "__main__":
    filename = "slime_chunks.txt"
    slime_chunks = parse_slime_file(filename)

    # 示例：找 17x17 内最多史莱姆区块的区域
    #best_area, best_count, best_chunks = find_best_area(slime_chunks, 17, 17, mode="max")
    #print(f"\n最多史莱姆区块区域左上角: {best_area}, 数量: {best_count}")
    #print("该区域内的史莱姆区块如下：")
    #print(format_chunk_output(best_chunks))

    #print("\n" + "="*50 + "\n")

    # 示例：找 16x8 内最少史莱姆区块的区域
    #best_area, best_count, best_chunks = find_best_area(slime_chunks, 16, 8, mode="min")
    #print(f"最少史莱姆区块区域左上角: {best_area}, 数量: {best_count}")
    #print("该区域内的史莱姆区块如下：")
    #print(format_chunk_output(best_chunks))

    # 示例：找 16x8 内最少史莱姆区块的区域,并且左上角区块可以被八整除
    #best_area, best_count, best_chunks = find_best_area_with_constraint(
    #slime_chunks,
    #area_w=16,
    #area_h=8,
    #mode="min",
    #align=8  # 要求左上角能被8整除
    #)

    #print(f"最少史莱姆区块区域左上角: {best_area}, 数量: {best_count}")
    #print("该区域内的史莱姆区块如下：")
    #print(format_chunk_output(best_chunks))
    
    
    #找出16*8范围内史莱姆区块最少的区域,同时左上角坐标可以被8整除,同时标出欧几里得距离距原点最近的
    #best_area, best_count, best_chunks, candidates = find_best_area_with_constraint(
    #slime_chunks,
    #area_w=16,
    #area_h=8,
    #mode="min",
    #align=8
    #)

    #print(f"最少史莱姆区块区域左上角: {best_area}, 数量: {best_count}")
    #print("该区域内的史莱姆区块如下：")
    #print(format_chunk_output(best_chunks))

    #print("\n所有候选最优区域：")
    #for c in candidates:
        #print(c, "距离原点:", math.sqrt(c[0]**2 + c[1]**2))


    best_area, best_count, best_chunks = find_best_area(slime_chunks, 17, 17, mode="max")
    print(f"最少史莱姆区块区域左上角: {best_area}, 数量: {best_count}")
    print("该区域内的史莱姆区块如下：")
    print(format_chunk_output(best_chunks))

    print("\n所有候选最优区域：")
    for c in candidates:
        print(c, "距离原点:", math.sqrt(c[0]**2 + c[1]**2))

