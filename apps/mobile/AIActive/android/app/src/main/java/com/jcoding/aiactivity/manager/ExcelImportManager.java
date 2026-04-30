package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.util.Log;

import com.jcoding.aiactivity.entity.ProgramItem;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * Excel导入管理器
 *
 * 功能：
 * 1. 解析Excel文件（.xlsx格式）
 * 2. 提取节目表数据
 * 3. 自动匹配数字人动作
 * 4. 数据验证和错误处理
 *
 * Excel格式要求：
 * | 序号 | 时间 | 内容 | 备注 |
 * |------|------|------|------|
 * | 1 | 10:00 | 欢迎各位来宾 | 开场 |
 * | 2 | 10:05 | 介绍活动流程 | 介绍 |
 * | 3 | 10:10 | 有请第一位嘉宾 | 引导 |
 */
public class ExcelImportManager {

    private static final String TAG = "ExcelImportManager";
    private static ExcelImportManager instance;

    private Context context;
    private ActionMatcher actionMatcher;

    // Excel列索引（从0开始）
    private static final int COL_SEQUENCE = 0;    // 序号列
    private static final int COL_TIME = 1;        // 时间列
    private static final int COL_CONTENT = 2;      // 内容列
    private static final int COL_REMARK = 3;       // 备注列

    private ExcelImportManager(Context context) {
        this.context = context.getApplicationContext();
        this.actionMatcher = ActionMatcher.getInstance(context);
    }

    public static synchronized ExcelImportManager getInstance(Context context) {
        if (instance == null) {
            instance = new ExcelImportManager(context);
        }
        return instance;
    }

    /**
     * 解析Excel文件
     *
     * @param inputStream Excel文件输入流
     * @return 解析后的节目列表
     */
    public List<ProgramItem> parseExcel(InputStream inputStream) {
        List<ProgramItem> programs = new ArrayList<>();

        try {
            // 注意：这里需要Apache POI库
            // 由于Android项目可能没有包含POI库，这里提供简化实现
            // 实际项目中需要添加Apache POI依赖

            Log.i(TAG, "开始解析Excel文件");

            // 简化实现：CSV格式解析（作为降级方案）
            programs = parseCSV(inputStream);

            // 自动匹配动作
            actionMatcher.matchActions(programs);

            Log.i(TAG, "解析完成，共 " + programs.size() + " 个节目");

        } catch (Exception e) {
            Log.e(TAG, "解析Excel失败", e);
        }

        return programs;
    }

    /**
     * 解析CSV格式（降级方案）
     *
     * CSV格式：序号,时间,内容,备注
     */
    private List<ProgramItem> parseCSV(InputStream inputStream) {
        List<ProgramItem> programs = new ArrayList<>();

        try {
            java.io.BufferedReader reader = new java.io.BufferedReader(
                new java.io.InputStreamReader(inputStream, "UTF-8"));

            String line;
            boolean isFirstLine = true;

            while ((line = reader.readLine()) != null) {
                // 跳过标题行
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }

                // 解析行
                String[] parts = line.split(",");
                if (parts.length >= 3) {
                    try {
                        int sequence = Integer.parseInt(parts[0].trim());
                        String time = parts[1].trim();
                        String content = parts[2].trim();
                        String remark = parts.length > 3 ? parts[3].trim() : "";

                        ProgramItem item = new ProgramItem(sequence, time, content, remark);
                        programs.add(item);

                    } catch (NumberFormatException e) {
                        Log.w(TAG, "跳过无效行: " + line);
                    }
                }
            }

            reader.close();

        } catch (Exception e) {
            Log.e(TAG, "解析CSV失败", e);
        }

        return programs;
    }

    /**
     * 验证节目列表
     *
     * @param programs 节目列表
     * @return 验证结果
     */
    public ValidationResult validate(List<ProgramItem> programs) {
        ValidationResult result = new ValidationResult();

        if (programs == null || programs.isEmpty()) {
            result.valid = false;
            result.errors.add("节目列表为空");
            return result;
        }

        // 检查序号连续性
        for (int i = 0; i < programs.size(); i++) {
            ProgramItem item = programs.get(i);

            if (item.getSequence() != i + 1) {
                result.warnings.add("第 " + (i + 1) + " 行：序号不连续（期望 " + (i + 1) + "，实际 " + item.getSequence() + "）");
            }

            // 检查必填字段
            if (item.getTime() == null || item.getTime().isEmpty()) {
                result.errors.add("第 " + (i + 1) + " 行：时间为空");
                result.valid = false;
            }

            if (item.getContent() == null || item.getContent().isEmpty()) {
                result.errors.add("第 " + (i + 1) + " 行：内容为空");
                result.valid = false;
            }
        }

        if (result.valid) {
            result.message = "验证通过，共 " + programs.size() + " 个节目";
        } else {
            result.message = "验证失败，发现 " + result.errors.size() + " 个错误";
        }

        return result;
    }

    /**
     * 验证结果
     */
    public static class ValidationResult {
        public boolean valid = true;
        public String message = "";
        public List<String> errors = new ArrayList<>();
        public List<String> warnings = new ArrayList<>();
    }

    /**
     * 导入结果
     */
    public static class ImportResult {
        public boolean success;
        public String message;
        public List<ProgramItem> programs = new ArrayList<>();
        public int importedCount = 0;
        public int errorCount = 0;

        public static ImportResult success(List<ProgramItem> programs) {
            ImportResult result = new ImportResult();
            result.success = true;
            result.programs = programs;
            result.importedCount = programs.size();
            result.message = "成功导入 " + programs.size() + " 个节目";
            return result;
        }

        public static ImportResult failure(String error) {
            ImportResult result = new ImportResult();
            result.success = false;
            result.message = error;
            return result;
        }
    }

    /**
     * 生成示例CSV文件内容
     */
    public static String generateSampleCSV() {
        StringBuilder sb = new StringBuilder();
        sb.append("序号,时间,内容,备注\n");
        sb.append("1,10:00,欢迎大家参加本次活动,开场\n");
        sb.append("2,10:05,我是AI主持人方小松,介绍\n");
        sb.append("3,10:10,首先有请领导致辞,引导\n");
        sb.append("4,10:15,接下来进行精彩表演,介绍\n");
        sb.append("5,10:30,恭喜获奖者,祝贺\n");
        sb.append("6,10:35,感谢大家的参与,结束\n");
        return sb.toString();
    }

    /**
     * 保存示例CSV文件
     */
    public void saveSampleCSV(java.io.File file) {
        try {
            java.io.FileWriter writer = new java.io.FileWriter(file);
            writer.write(generateSampleCSV());
            writer.close();
            Log.i(TAG, "示例CSV已保存: " + file.getAbsolutePath());
        } catch (Exception e) {
            Log.e(TAG, "保存示例CSV失败", e);
        }
    }
}
