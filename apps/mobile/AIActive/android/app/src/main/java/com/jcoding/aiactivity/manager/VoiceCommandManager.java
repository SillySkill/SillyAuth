package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.util.Log;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 语音命令管理器
 * 解析语音命令，提供语义理解功能
 *
 * 功能：
 * 1. 识别设置命令关键词
 * 2. 提取设置项目和参数
 * 3. 提供命令类型判断
 */
public class VoiceCommandManager {

    private static final String TAG = "VoiceCommandManager";
    private static VoiceCommandManager instance;

    private Context context;

    // 命令关键词
    private static final String[] SETTINGS_KEYWORDS = {
        "设置", "调整", "配置", "修改", "更改", "打开设置", "进入设置"
    };

    // 设置项目关键词映射
    private static final Map<String, String> MODULE_KEYWORDS = new HashMap<String, String>() {{
        put("数字人", "digital_human");
        put("语音", "voice");
        put("声音", "voice");
        put("说话", "voice");
        put("AI百变秀", "ai_show");
        put("AI", "ai_show");
        put("换装", "ai_show");
        put("问答", "quiz");
        put("答题", "quiz");
        put("题目", "quiz");
        put("抽奖", "lottery");
        put("幸运", "lottery");
        put("内场", "inner");
        put("大屏", "inner");
        put("通用", "general");
    }};

    // 数字人参数关键词
    private static final Map<String, String> DIGITAL_HUMAN_PARAMS = new HashMap<String, String>() {{
        put("位置", "position");
        put("大小", "size");
        put("尺寸", "size");
        put("缩放", "scale_type");
        put("开关", "enabled");
        put("启用", "enabled");
        put("显示", "enabled");
    }};

    // 语音参数关键词
    private static final Map<String, String> VOICE_PARAMS = new HashMap<String, String>() {{
        put("语速", "tts_speed");
        put("速度", "tts_speed");
        put("音调", "tts_pitch");
        put("音量", "tts_volume");
        put("发音", "tts_voice_type");
        put("识别", "asr_engine");
        put("过滤", "asr_filter");
    }};

    // 参数值映射
    private static final Map<String, String> POSITION_VALUES = new HashMap<String, String>() {{
        put("左上", "left_top");
        put("左边上面", "left_top");
        put("左下", "left_bottom");
        put("左边下面", "left_bottom");
        put("右上", "right_top");
        put("右边上面", "right_top");
        put("右下", "right_bottom");
        put("右边下面", "right_bottom");
    }};

    private static final Map<String, Boolean> BOOLEAN_VALUES = new HashMap<String, Boolean>() {{
        put("开", true);
        put("开启", true);
        put("启用", true);
        put("打开", true);
        put("是", true);
        put("要", true);
        put("关", false);
        put("关闭", false);
        put("禁用", false);
        put("不", false);
        put("否", false);
        put("不要", false);
    }};

    private VoiceCommandManager(Context context) {
        this.context = context.getApplicationContext();
    }

    public static synchronized VoiceCommandManager getInstance(Context context) {
        if (instance == null) {
            instance = new VoiceCommandManager(context);
        }
        return instance;
    }

    /**
     * 解析语音命令
     * @param text 语音识别文本
     * @return 解析后的命令对象
     */
    public VoiceCommand parseCommand(String text) {
        if (text == null || text.isEmpty()) {
            return null;
        }

        Log.i(TAG, "解析语音命令: " + text);

        // 检查是否包含设置关键词
        if (!containsSettingKeyword(text)) {
            return null;
        }

        VoiceCommand command = new VoiceCommand();
        command.originalText = text;

        // 提取设置模块
        command.module = extractModule(text);
        if (command.module == null) {
            command.module = "general"; // 默认为通用设置
        }

        // 提取参数类型
        command.paramType = extractParamType(text, command.module);

        // 提取参数值
        command.paramValue = extractParamValue(text, command.paramType);

        // 生成命令描述
        command.description = generateDescription(command);

        Log.i(TAG, "解析结果: " + command.toString());
        return command;
    }

    /**
     * 检查是否包含设置关键词
     */
    private boolean containsSettingKeyword(String text) {
        for (String keyword : SETTINGS_KEYWORDS) {
            if (text.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 提取设置模块
     */
    private String extractModule(String text) {
        for (Map.Entry<String, String> entry : MODULE_KEYWORDS.entrySet()) {
            if (text.contains(entry.getKey())) {
                return entry.getValue();
            }
        }
        return null;
    }

    /**
     * 提取参数类型
     */
    private String extractParamType(String text, String module) {
        Map<String, String> params = null;

        switch (module) {
            case "digital_human":
                params = DIGITAL_HUMAN_PARAMS;
                break;
            case "voice":
                params = VOICE_PARAMS;
                break;
            default:
                break;
        }

        if (params != null) {
            for (Map.Entry<String, String> entry : params.entrySet()) {
                if (text.contains(entry.getKey())) {
                    return entry.getValue();
                }
            }
        }

        return null;
    }

    /**
     * 提取参数值
     */
    private String extractParamValue(String text, String paramType) {
        if (paramType == null) {
            return null;
        }

        switch (paramType) {
            case "position":
                // 提取位置值
                for (Map.Entry<String, String> entry : POSITION_VALUES.entrySet()) {
                    if (text.contains(entry.getKey())) {
                        return entry.getValue();
                    }
                }
                break;

            case "enabled":
                // 提取布尔值
                for (Map.Entry<String, Boolean> entry : BOOLEAN_VALUES.entrySet()) {
                    if (text.contains(entry.getKey())) {
                        return String.valueOf(entry.getValue());
                    }
                }
                break;

            case "size":
                // 提取数字（大小）
                Pattern sizePattern = Pattern.compile("(\\d+)\\s*(dp|像素|厘米|厘米)");
                Matcher sizeMatcher = sizePattern.matcher(text);
                if (sizeMatcher.find()) {
                    String size = sizeMatcher.group(1);
                    try {
                        int sizeValue = Integer.parseInt(size);
                        // 限制在100-400范围内
                        if (sizeValue < 100) sizeValue = 100;
                        if (sizeValue > 400) sizeValue = 400;
                        return String.valueOf(sizeValue);
                    } catch (NumberFormatException e) {
                        // 忽略
                    }
                }
                break;

            case "scale_type":
                // 提取缩放类型
                if (text.contains("居中裁剪") || text.contains("裁剪")) {
                    return "center_crop";
                } else if (text.contains("居中")) {
                    return "center";
                } else if (text.contains("适应") || text.contains("适配")) {
                    return "fit_center";
                }
                break;

            case "tts_speed":
            case "tts_pitch":
                // 提取语速/音调（0.5-2.0）
                Pattern speedPattern = Pattern.compile("(0\\.[5-9]|1\\.\\d|2\\.0)\\s*倍");
                Matcher speedMatcher = speedPattern.matcher(text);
                if (speedMatcher.find()) {
                    return speedMatcher.group(1);
                }
                break;

            case "tts_volume":
                // 提取音量（0.0-1.0）
                if (text.contains("最大") || text.contains("100%")) {
                    return "1.0";
                } else if (text.contains("最小") || text.contains("静音")) {
                    return "0.0";
                } else if (text.contains("一半") || text.contains("50%")) {
                    return "0.5";
                }
                break;
        }

        return null;
    }

    /**
     * 生成命令描述
     */
    private String generateDescription(VoiceCommand command) {
        StringBuilder sb = new StringBuilder();

        // 模块名称
        String moduleName = getModuleName(command.module);
        sb.append(moduleName);

        // 参数名称
        if (command.paramType != null) {
            String paramName = getParamName(command.paramType);
            sb.append(" - ").append(paramName);

            // 参数值
            if (command.paramValue != null) {
                String valueName = getParamValueName(command.paramType, command.paramValue);
                sb.append(": ").append(valueName);
            }
        }

        return sb.toString();
    }

    private String getModuleName(String module) {
        switch (module) {
            case "digital_human": return "数字人设置";
            case "voice": return "语音设置";
            case "ai_show": return "AI百变秀设置";
            case "quiz": return "知识问答设置";
            case "lottery": return "幸运抽奖设置";
            case "inner": return "内场秀设置";
            case "general": return "通用设置";
            default: return "设置";
        }
    }

    private String getParamName(String paramType) {
        switch (paramType) {
            case "position": return "显示位置";
            case "size": return "显示大小";
            case "scale_type": return "缩放类型";
            case "enabled": return "开关";
            case "tts_speed": return "语速";
            case "tts_pitch": return "音调";
            case "tts_volume": return "音量";
            case "tts_voice_type": return "发音人";
            case "asr_engine": return "识别引擎";
            case "asr_filter": return "过滤选项";
            default: return paramType;
        }
    }

    private String getParamValueName(String paramType, String value) {
        if (value == null) return "未指定";

        switch (paramType) {
            case "position":
                switch (value) {
                    case "left_top": return "左上角";
                    case "left_bottom": return "左下角";
                    case "right_top": return "右上角";
                    case "right_bottom": return "右下角";
                }
                break;
            case "enabled":
                return "true".equals(value) ? "开启" : "关闭";
            case "scale_type":
                switch (value) {
                    case "center_crop": return "居中裁剪";
                    case "center": return "居中";
                    case "fit_center": return "适应";
                }
                break;
        }

        return value;
    }

    /**
     * 语音命令数据类
     */
    public static class VoiceCommand {
        public String originalText;      // 原始文本
        public String module;            // 设置模块
        public String paramType;         // 参数类型
        public String paramValue;        // 参数值
        public String description;       // 命令描述

        @Override
        public String toString() {
            return "VoiceCommand{" +
                    "module='" + module + '\'' +
                    ", paramType='" + paramType + '\'' +
                    ", paramValue='" + paramValue + '\'' +
                    ", description='" + description + '\'' +
                    '}';
        }
    }

    /**
     * 命令监听接口
     */
    public interface CommandListener {
        /**
         * 识别到设置命令
         * @param command 命令对象
         */
        void onSettingCommand(VoiceCommand command);

        /**
         * 识别失败
         * @param error 错误信息
         */
        void onError(String error);
    }
}
