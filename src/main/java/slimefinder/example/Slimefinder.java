package slimefinder.example;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.server.command.CommandManager;
import net.minecraft.server.command.ServerCommandSource;
import net.minecraft.text.Text;
import net.minecraft.util.math.ChunkPos;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.WorldSavePath;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

public class Slimefinder implements ModInitializer {
	public static final String MOD_ID = "slimefinder";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	@Override
	public void onInitialize() {
		LOGGER.info("SlimeFinder mod initialized!");
		
		// 注册命令
		CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {
			dispatcher.register(CommandManager.literal("slimefinder")
				.then(CommandManager.literal("save")
					.then(CommandManager.argument("radius", IntegerArgumentType.integer(1))
						.executes(this::executeSlimeFinderCommand))));
		});
	}

	private int executeSlimeFinderCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
		ServerCommandSource source = context.getSource();
		int radius = IntegerArgumentType.getInteger(context, "radius");
		
		// 获取玩家位置和世界
		BlockPos playerPos = BlockPos.ofFloored(source.getPosition());
		ServerWorld world = source.getWorld();
		long worldSeed = world.getSeed();
		
		// 获取玩家所在区块
		ChunkPos playerChunk = new ChunkPos(playerPos);
		
		// 流式查找并保存史莱姆区块
		try {
			int slimeChunkCount = findAndSaveSlimeChunks(worldSeed, playerChunk, radius, world);
			source.sendFeedback(() -> Text.literal("找到 " + slimeChunkCount + " 个史莱姆区块，结果已保存到文件"), false);
		} catch (IOException e) {
			source.sendFeedback(() -> Text.literal("保存文件时出错: " + e.getMessage()), false);
			LOGGER.error("Failed to save slime chunks to file", e);
		}
		
		return 1;
	}

	/**
	 * 基于Minecraft原版算法检测史莱姆区块
	 * 算法来源: https://minecraft.fandom.com/wiki/Slime
	 */
	private boolean isSlimeChunk(long worldSeed, int chunkX, int chunkZ) {
		Random random = new Random(worldSeed
			+ (long) (chunkX * chunkX * 0x4c1906)
			+ (long) (chunkX * 0x5ac0db)
			+ (long) (chunkZ * chunkZ) * 0x4307a7L
			+ (long) (chunkZ * 0x5f24f) ^ 0x3ad8025fL);
		return random.nextInt(10) == 0;
	}

	/**
	 * 在指定半径内查找史莱姆区块并直接写入文件（流式处理，避免内存溢出）
	 */
	private int findAndSaveSlimeChunks(long worldSeed, ChunkPos centerChunk, int radius, ServerWorld world) throws IOException {
		// 获取世界保存目录
		File worldDir = world.getServer().getSavePath(WorldSavePath.ROOT).toFile();
		File outputFile = new File(worldDir, "slime_chunks.txt");
		
		int slimeChunkCount = 0;
		
		try (FileWriter writer = new FileWriter(outputFile)) {
			// 写入文件头信息
			writer.write("Slime Chunks found around chunk (" + centerChunk.x + "," + centerChunk.z + ") with radius " + radius + "\n");
			writer.write("Format: Chunk (x,z) - Block coordinates (x1,z1) to (x2,z2)\n");
			writer.write("=====================================\n");
			
			// 流式处理：逐个检查区块并立即写入文件
			for (int x = centerChunk.x - radius; x <= centerChunk.x + radius; x++) {
				for (int z = centerChunk.z - radius; z <= centerChunk.z + radius; z++) {
					if (isSlimeChunk(worldSeed, x, z)) {
						// 计算区块对应的方块坐标范围
						int blockX1 = x * 16;
						int blockZ1 = z * 16;
						int blockX2 = blockX1 + 15;
						int blockZ2 = blockZ1 + 15;
						
						// 立即写入文件，不存储在内存中
						writer.write("Chunk (" + x + "," + z + ") - Blocks (" + blockX1 + "," + blockZ1 + ") to (" + blockX2 + "," + blockZ2 + ")\n");
						slimeChunkCount++;
						
						// 每处理100个史莱姆区块就刷新一次缓冲区，确保数据及时写入磁盘
						if (slimeChunkCount % 100 == 0) {
							writer.flush();
							LOGGER.info("Processed {} slime chunks so far...", slimeChunkCount);
						}
					}
				}
			}
			
			// 写入统计信息
			writer.write("=====================================\n");
			writer.write("Total slime chunks found: " + slimeChunkCount + "\n");
		}
		
		LOGGER.info("Saved {} slime chunks to {}", slimeChunkCount, outputFile.getAbsolutePath());
		return slimeChunkCount;
	}


}