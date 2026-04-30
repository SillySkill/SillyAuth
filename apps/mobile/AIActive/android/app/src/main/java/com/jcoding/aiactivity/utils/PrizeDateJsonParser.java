package com.jcoding.aiactivity.utils;

import android.content.Context;
import android.util.Log;

import com.google.gson.JsonObject;
import com.jcoding.aiactivity.entity.Candidate;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * prizeDate.json解析器
 * 从prizeDate.json读取抽奖数据
 *
 * 文件格式：
 * {
 *   "店铺名": {
 *     "礼品": "礼品描述",
 *     "数量": 数量
 *   }
 * }
 */
public class PrizeDateJsonParser {

    private static final String TAG = "PrizeDateJsonParser";
    private static final String FILE_PATH = "lottery/prizeDate.json";

    /**
     * 读取assets文件
     */
    private static String readAssetFile(Context context, String filePath) {
        try {
            InputStream is = context.getAssets().open(filePath);
            int size = is.available();
            byte[] buffer = new byte[size];
            is.read(buffer);
            is.close();
            return new String(buffer, StandardCharsets.UTF_8);
        } catch (Exception e) {
            Log.e(TAG, "读取文件失败: " + filePath, e);
            return null;
        }
    }

    /**
     * 从prizeDate.json解析候选人数据
     * 每个店铺按照"数量"展开成多个候选人
     *
     * @param context 上下文
     * @return 候选人列表，失败返回null
     */
    public static List<Candidate> parse(Context context) {
        List<Candidate> candidates = new ArrayList<>();

        try {
            // 读取JSON文件
            String jsonStr = readAssetFile(context, FILE_PATH);
            if (jsonStr == null || jsonStr.isEmpty()) {
                Log.e(TAG, "读取文件失败: " + FILE_PATH);
                return null;
            }

            // 解析JSON
            com.google.gson.Gson gson = new com.google.gson.Gson();
            JsonObject jsonObject = gson.fromJson(jsonStr, JsonObject.class);

            if (jsonObject == null || jsonObject.size() == 0) {
                Log.e(TAG, "JSON数据为空");
                return null;
            }

            // 遍历每个店铺
            int idCounter = 1;
            for (Map.Entry<String, com.google.gson.JsonElement> entry : jsonObject.entrySet()) {
                String shopName = entry.getKey();
                com.google.gson.JsonElement element = entry.getValue();

                if (!element.isJsonObject()) {
                    Log.w(TAG, "跳过无效数据: " + shopName);
                    continue;
                }

                JsonObject shopData = element.getAsJsonObject();

                // 读取礼品
                String gift = "";
                if (shopData.has("礼品")) {
                    gift = shopData.get("礼品").getAsString();
                }

                // 读取数量
                int quantity = 1;
                if (shopData.has("数量")) {
                    try {
                        quantity = shopData.get("数量").getAsInt();
                    } catch (Exception e) {
                        Log.w(TAG, "数量解析失败: " + shopName + ", 使用默认值1");
                    }
                }

                // 按数量展开候选人
                for (int i = 0; i < quantity; i++) {
                    Candidate candidate = new Candidate();
                    candidate.setId(String.format("PD%04d", idCounter++));
                    candidate.setName(shopName);
                    candidate.setDepartment(gift); // 将礼品信息放在部门字段
                    candidates.add(candidate);
                }

                Log.d(TAG, "店铺: " + shopName + ", 礼品: " + gift + ", 数量: " + quantity);
            }

            Log.i(TAG, "成功解析 " + candidates.size() + " 个候选人（从prizeDate.json）");
            return candidates;

        } catch (Exception e) {
            Log.e(TAG, "解析prizeDate.json失败", e);
            return null;
        }
    }

    /**
     * 获取数据摘要信息
     *
     * @param context 上下文
     * @return 摘要信息字符串
     */
    public static String getSummary(Context context) {
        try {
            List<Candidate> candidates = parse(context);
            if (candidates == null || candidates.isEmpty()) {
                return "暂无数据";
            }

            // 统计每个店铺的数量
            java.util.Map<String, Integer> shopCount = new java.util.LinkedHashMap<>();
            for (Candidate candidate : candidates) {
                String shopName = candidate.getName();
                shopCount.put(shopName, shopCount.getOrDefault(shopName, 0) + 1);
            }

            StringBuilder sb = new StringBuilder();
            sb.append("共 ").append(candidates.size()).append(" 个抽奖机会\n");
            sb.append("包含 ").append(shopCount.size()).append(" 个店铺:\n");

            for (Map.Entry<String, Integer> entry : shopCount.entrySet()) {
                sb.append("  • ").append(entry.getKey())
                  .append(": ").append(entry.getValue()).append(" 份\n");
            }

            return sb.toString();

        } catch (Exception e) {
            return "数据加载失败: " + e.getMessage();
        }
    }
}
