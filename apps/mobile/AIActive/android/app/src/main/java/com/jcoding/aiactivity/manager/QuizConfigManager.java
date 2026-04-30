package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.text.TextUtils;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;
import com.jcoding.aiactivity.entity.QuestionBank;
import com.jcoding.aiactivity.utils.PreferenceUtils;
import com.jcoding.aiactivity.utils.FileUtils;

/**
 * 知识问答配置管理器
 * 管理答题模式、语音设置等
 */
public class QuizConfigManager {

    private static final String PREF_QUESTION_ORDER = "quiz_question_order";
    private static final String PREF_VOICE_ENABLED = "quiz_voice_enabled";
    private static final String PREF_AUTO_SUBMIT = "quiz_auto_submit";
    private static final String PREF_ROUND_QTY = "quiz_round_qty";
    private static final String PREF_ROUND_CHOICE = "quiz_round_choice";
    private static final String PREF_ROUND_JUDGEMENT = "quiz_round_judgement";
    private static final String PREF_QUIZ_TITLE = "quiz_title";
    private static final String PREF_COLOR_THEME = "quiz_color_theme";

    private static QuizConfigManager instance;
    private Context context;
    private Gson gson;

    /**
     * 出题顺序枚举
     */
    public enum QuestionOrder {
        MIXED("mixed", "混合随机", "选择题和判断题混合随机出现"),
        CHOICE_FIRST("choice_first", "先选择题", "先出所有选择题，再出判断题"),
        JUDGEMENT_FIRST("judgement_first", "先判断题", "先出所有判断题，再出选择题");

        private String code;
        private String displayName;
        private String description;

        QuestionOrder(String code, String displayName, String description) {
            this.code = code;
            this.displayName = displayName;
            this.description = description;
        }

        public String getCode() {
            return code;
        }

        public String getDisplayName() {
            return displayName;
        }

        public String getDescription() {
            return description;
        }

        public static QuestionOrder fromCode(String code) {
            for (QuestionOrder order : values()) {
                if (order.code.equals(code)) {
                    return order;
                }
            }
            return MIXED;  // 默认混合
        }
    }

    /**
     * 色彩风格枚举
     */
    public enum ColorTheme {
        // ===== 原有主题 =====
        // 格式：code, displayName, primary, dark, text, bg, overlay(80%透明度的底纹颜色)
        TECH_BLUE("tech_blue", "科技蓝", 0xFF2196F3, 0xFF1976D2, 0xFFFFFFFF, 0xFFE3F2FD, 0xCC1976D2),
        BLACK("black", "黑色", 0xFF000000, 0xFF212121, 0xFFFFFFFF, 0xFFF5F5F5, 0xCC000000),
        RED("red", "红色", 0xFFF44336, 0xFFD32F2F, 0xFFFFFFFF, 0xFFFFEBEE, 0xCCD32F2F),
        PINK("pink", "粉色", 0xFFE91E63, 0xFFC2185B, 0xFFFFFFFF, 0xFFFCE4EC, 0xCC7B1FA2),
        WHITE("white", "白色", 0xFFFFFFFF, 0xFFFAFAFA, 0xFF000000, 0xFFECEFF1, 0xCCBDBDBD),
        PURPLE("purple", "紫色", 0xFF9C27B0, 0xFF7B1FA2, 0xFFFFFFFF, 0xFFF3E5F5, 0xCC7B1FA2),
        GREEN("green", "绿色", 0xFF4CAF50, 0xFF388E3C, 0xFFFFFFFF, 0xFFE8F5E9, 0xCC388E3C),
        ORANGE("orange", "橙色", 0xFFFF9800, 0xFFF57C00, 0xFFFFFFFF, 0xFFFFF3E0, 0xCCF57C00),

        // ===== Material Design 3 配色 =====
        GOLD("gold", "金色", 0xFFFFD700, 0xFFFFA000, 0xFFFFFFFF, 0xFFFFF9C4, 0xCCFFA000),
        INDIGO("indigo", "靛蓝", 0xFF3F51B5, 0xFF303F9F, 0xFFFFFFFF, 0xFFC5CAE9, 0xCC303F9F),
        CYAN("cyan", "青色", 0xFF00BCD4, 0xFF0097A7, 0xFFFFFFFF, 0xFFB2EBF2, 0xCC0097A7),
        BROWN("brown", "棕色", 0xFF795548, 0xFF5D4037, 0xFFFFFFFF, 0xFFD7CCC8, 0xCC5D4037),
        SKY_BLUE("sky_blue", "天蓝", 0xFF03A9F4, 0xFF0288D1, 0xFFFFFFFF, 0xFFB3E5FC, 0xCC0288D1),

        // ===== 渐变色彩 =====
        SUNSET("sunset", "夕阳", 0xFFFF5722, 0xFFE64A19, 0xFFFFFFFF, 0xFFFFCCBC, 0xCCE64A19),
        OCEAN("ocean", "海洋", 0xFF006064, 0xFF004D40, 0xFFFFFFFF, 0xFFB2DFDB, 0xCC004D40),
        GRAPE("grape", "葡萄", 0xFF673AB7, 0xFF512DA8, 0xFFFFFFFF, 0xFFD1C4E9, 0xCC512DA8);

        private String code;
        private String displayName;
        private int primaryColor;      // 主色调
        private int darkColor;         // 深色调
        private int textColor;         // 文字颜色
        private int backgroundColor;   // 背景色
        private int overlayColor;      // 底纹颜色（包含透明度）

        ColorTheme(String code, String displayName, int primary, int dark, int text, int bg, int overlay) {
            this.code = code;
            this.displayName = displayName;
            this.primaryColor = primary;
            this.darkColor = dark;
            this.textColor = text;
            this.backgroundColor = bg;
            this.overlayColor = overlay;
        }

        public String getCode() {
            return code;
        }

        public String getDisplayName() {
            return displayName;
        }

        public int getPrimaryColor() {
            return primaryColor;
        }

        public int getDarkColor() {
            return darkColor;
        }

        public int getTextColor() {
            return textColor;
        }

        public int getBackgroundColor() {
            return backgroundColor;
        }

        public int getOverlayColor() {
            return overlayColor;
        }

        public static ColorTheme fromCode(String code) {
            for (ColorTheme theme : values()) {
                if (theme.code.equals(code)) {
                    return theme;
                }
            }
            return TECH_BLUE;  // 默认科技蓝
        }
    }

    private QuizConfigManager(Context context) {
        this.context = context.getApplicationContext();
        this.gson = new Gson();
    }

    public static synchronized QuizConfigManager getInstance(Context context) {
        if (instance == null) {
            instance = new QuizConfigManager(context);
        }
        return instance;
    }

    // ========== 出题顺序 ==========

    /**
     * 获取出题顺序
     */
    public QuestionOrder getQuestionOrder() {
        String code = PreferenceUtils.getString(context, PREF_QUESTION_ORDER, QuestionOrder.MIXED.getCode());
        return QuestionOrder.fromCode(code);
    }

    /**
     * 设置出题顺序
     */
    public void setQuestionOrder(QuestionOrder order) {
        PreferenceUtils.putString(context, PREF_QUESTION_ORDER, order.getCode());
    }

    // ========== 语音出题开关 ==========

    /**
     * 是否启用语音出题
     * 默认启用（如果有语音配置）
     */
    public boolean isVoiceEnabled() {
        return PreferenceUtils.getBoolean(context, PREF_VOICE_ENABLED, true);
    }

    /**
     * 设置语音出题开关
     */
    public void setVoiceEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, PREF_VOICE_ENABLED, enabled);
    }

    // ========== 自动提交开关 ==========

    /**
     * 是否自动提交答案（默认启用）
     */
    public boolean isAutoSubmit() {
        return PreferenceUtils.getBoolean(context, PREF_AUTO_SUBMIT, true);
    }

    /**
     * 设置自动提交开关
     */
    public void setAutoSubmit(boolean autoSubmit) {
        PreferenceUtils.putBoolean(context, PREF_AUTO_SUBMIT, autoSubmit);
    }

    // ========== 轮次配置 ==========

    /**
     * 获取每轮题目总数
     */
    public int getRoundQty() {
        return PreferenceUtils.getInt(context, PREF_ROUND_QTY, 10);
    }

    /**
     * 设置每轮题目总数
     */
    public void setRoundQty(int qty) {
        PreferenceUtils.putInt(context, PREF_ROUND_QTY, qty);
    }

    /**
     * 获取每轮选择题数量
     */
    public int getRoundChoice() {
        return PreferenceUtils.getInt(context, PREF_ROUND_CHOICE, 6);
    }

    /**
     * 设置每轮选择题数量
     */
    public void setRoundChoice(int choice) {
        PreferenceUtils.putInt(context, PREF_ROUND_CHOICE, choice);
    }

    /**
     * 获取每轮判断题数量
     */
    public int getRoundJudgement() {
        return PreferenceUtils.getInt(context, PREF_ROUND_JUDGEMENT, 4);
    }

    /**
     * 设置每轮判断题数量
     */
    public void setRoundJudgement(int judgement) {
        PreferenceUtils.putInt(context, PREF_ROUND_JUDGEMENT, judgement);
    }

    // ========== 重置配置 ==========

    /**
     * 重置为默认配置
     */
    public void resetToDefault() {
        setQuestionOrder(QuestionOrder.MIXED);
        setVoiceEnabled(true);
        setAutoSubmit(true);
        setRoundQty(10);
        setRoundChoice(6);
        setRoundJudgement(4);
    }

    // ========== 题库配置 ==========

    /**
     * 获取题库配置
     */
    public JsonObject getQuestionConfig() {
        try {
            String configContent = FileUtils.readAssetFile(context, "question/config.json");
            if (configContent != null) {
                return gson.fromJson(configContent, JsonObject.class);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new JsonObject();
    }

    /**
     * 获取默认题库
     */
    public QuestionBank getDefaultQuestionBank() {
        try {
            JsonObject config = getQuestionConfig();
            android.util.Log.d("QuizConfigManager", "config: " + config);

            if (config.has("catalog") && config.get("catalog").isJsonArray()) {
                // 返回第一个题库
                JsonObject catalogItem = config.getAsJsonArray("catalog").get(0).getAsJsonObject();
                String file = catalogItem.get("file").getAsString();
                String bankName = catalogItem.has("catalog_name") ? catalogItem.get("catalog_name").getAsString() : "默认题库";
                String bankId = catalogItem.has("qid") ? catalogItem.get("qid").getAsString() : "default";
                int status = catalogItem.has("status") ? catalogItem.get("status").getAsInt() : 1;

                android.util.Log.d("QuizConfigManager", "Loading question file: question/" + file);

                String content = FileUtils.readAssetFile(context, "question/" + file);
                android.util.Log.d("QuizConfigManager", "Content length: " + (content != null ? content.length() : 0));

                if (content != null) {
                    // 尝试解析为QuestionBank格式
                    try {
                        QuestionBank qb = gson.fromJson(content, QuestionBank.class);
                        android.util.Log.d("QuizConfigManager", "Parsed as QuestionBank, questions: " + qb.getQuestionCount());

                        // 如果解析成功但没有题目，尝试旧格式
                        if (qb.getQuestionCount() == 0) {
                            android.util.Log.d("QuizConfigManager", "QuestionBank empty, trying legacy format");
                            qb = parseLegacyQuestionBank(content, bankId, bankName, file, status);
                            android.util.Log.d("QuizConfigManager", "Parsed legacy format, questions: " + qb.getQuestionCount());
                        }

                        return qb;
                    } catch (Exception e) {
                        android.util.Log.d("QuizConfigManager", "Not QuestionBank format, trying legacy format", e);
                        // 如果失败，尝试解析为旧格式 {"choice_question": [...]}
                        QuestionBank qb = parseLegacyQuestionBank(content, bankId, bankName, file, status);
                        android.util.Log.d("QuizConfigManager", "Parsed legacy format, questions: " + qb.getQuestionCount());
                        return qb;
                    }
                }
            }
        } catch (Exception e) {
            android.util.Log.e("QuizConfigManager", "Error loading question bank", e);
            e.printStackTrace();
        }
        // 返回空题库
        android.util.Log.d("QuizConfigManager", "Returning empty QuestionBank");
        return new QuestionBank();
    }

    /**
     * 根据题库ID获取题库
     */
    public QuestionBank getQuestionBankById(String bankId) {
        if (bankId == null || bankId.isEmpty()) {
            android.util.Log.d("QuizConfigManager", "bankId is null or empty, returning default");
            return getDefaultQuestionBank();
        }

        try {
            JsonObject config = getQuestionConfig();
            android.util.Log.d("QuizConfigManager", "config: " + config);

            if (config.has("catalog") && config.get("catalog").isJsonArray()) {
                JsonArray catalogArray = config.getAsJsonArray("catalog");

                // 遍历题库列表，查找匹配的ID
                for (int i = 0; i < catalogArray.size(); i++) {
                    JsonObject catalogItem = catalogArray.get(i).getAsJsonObject();
                    String currentId = catalogItem.has("qid") ? catalogItem.get("qid").getAsString() : "";

                    if (bankId.equals(currentId)) {
                        // 找到匹配的题库
                        String file = catalogItem.get("file").getAsString();
                        String bankName = catalogItem.has("catalog_name") ? catalogItem.get("catalog_name").getAsString() : "默认题库";
                        int status = catalogItem.has("status") ? catalogItem.get("status").getAsInt() : 1;

                        android.util.Log.d("QuizConfigManager", "Loading question file: question/" + file + " for bank: " + bankName);

                        String content = FileUtils.readAssetFile(context, "question/" + file);
                        android.util.Log.d("QuizConfigManager", "Content length: " + (content != null ? content.length() : 0));

                        if (content != null) {
                            // 尝试解析为QuestionBank格式
                            try {
                                QuestionBank qb = gson.fromJson(content, QuestionBank.class);
                                android.util.Log.d("QuizConfigManager", "Parsed as QuestionBank, questions: " + qb.getQuestionCount());

                                // 如果解析成功但没有题目，尝试旧格式
                                if (qb.getQuestionCount() == 0) {
                                    android.util.Log.d("QuizConfigManager", "QuestionBank empty, trying legacy format");
                                    qb = parseLegacyQuestionBank(content, bankId, bankName, file, status);
                                    android.util.Log.d("QuizConfigManager", "Parsed legacy format, questions: " + qb.getQuestionCount());
                                }

                                return qb;
                            } catch (Exception e) {
                                android.util.Log.d("QuizConfigManager", "Not QuestionBank format, trying legacy format", e);
                                // 如果失败，尝试解析为旧格式 {"choice_question": [...]}
                                QuestionBank qb = parseLegacyQuestionBank(content, bankId, bankName, file, status);
                                android.util.Log.d("QuizConfigManager", "Parsed legacy format, questions: " + qb.getQuestionCount());
                                return qb;
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
            android.util.Log.e("QuizConfigManager", "Error loading question bank by id: " + bankId, e);
            e.printStackTrace();
        }

        // 如果找不到指定的题库，返回默认题库
        android.util.Log.d("QuizConfigManager", "Question bank not found for id: " + bankId + ", returning default");
        return getDefaultQuestionBank();
    }

    /**
     * 解析旧格式题库文件 {"choice_question": [...]}
     */
    public QuestionBank parseLegacyQuestionBank(String content, String bankId, String bankName, String fileName, int status) {
        try {
            android.util.Log.d("QuizConfigManager", "parseLegacyQuestionBank: Starting parse");
            QuestionBank questionBank = new QuestionBank();
            questionBank.setBankId(bankId);
            questionBank.setBankName(bankName);
            questionBank.setFileName(fileName);
            questionBank.setStatus(status);

            // 直接解析JSON
            com.google.gson.JsonObject root = gson.fromJson(content, com.google.gson.JsonObject.class);
            android.util.Log.d("QuizConfigManager", "Parsed JSON root, keys: " + root.keySet());

            java.util.List<com.jcoding.aiactivity.entity.Question> questions = new java.util.ArrayList<>();

            // 处理选择题（支持两种格式：choice_question 和 choice_questions）
            com.google.gson.JsonArray choiceArray = null;
            if (root.has("choice_questions") && root.get("choice_questions").isJsonArray()) {
                choiceArray = root.getAsJsonArray("choice_questions");
                android.util.Log.d("QuizConfigManager", "Found choice_questions array, size: " + choiceArray.size());
            } else if (root.has("choice_question") && root.get("choice_question").isJsonArray()) {
                choiceArray = root.getAsJsonArray("choice_question");
                android.util.Log.d("QuizConfigManager", "Found choice_question array, size: " + choiceArray.size());
            }

            if (choiceArray != null) {

                for (int i = 0; i < choiceArray.size(); i++) {
                    com.google.gson.JsonObject qJson = choiceArray.get(i).getAsJsonObject();

                    // 跳过没有"choice"字段的项（可能是判断题格式错误）
                    if (!qJson.has("choice")) {
                        continue;
                    }

                    com.jcoding.aiactivity.entity.Question question = new com.jcoding.aiactivity.entity.Question();

                    // 设置基本信息
                    question.setQuestionId(bankId + "_choice_" + i);
                    question.setType("choice");

                    // 从"choice"字段读取题目内容
                    question.setContent(qJson.get("choice").getAsString());

                    // 从"options"字段读取选项
                    if (qJson.has("options") && qJson.get("options").isJsonArray()) {
                        com.google.gson.JsonArray optionsArray = qJson.getAsJsonArray("options");
                        String[] options = new String[optionsArray.size()];
                        for (int j = 0; j < optionsArray.size(); j++) {
                            options[j] = optionsArray.get(j).getAsString();
                        }
                        question.setOptions(options);
                    }

                    // 从"answer"字段读取答案（数组格式如["公益事业"]）
                    if (qJson.has("answer")) {
                        try {
                            com.google.gson.JsonArray answerArray = qJson.getAsJsonArray("answer");
                            if (answerArray.size() > 0) {
                                String answerText = answerArray.get(0).getAsString();
                                int answerIndex = findAnswerIndex(answerText, question.getOptions());
                                question.setCorrectAnswer(answerIndex);
                            }
                        } catch (Exception e) {
                            // 如果answer不是数组，可能是整数
                            question.setCorrectAnswer(qJson.get("answer").getAsInt());
                        }
                    }

                    questions.add(question);
                    android.util.Log.d("QuizConfigManager", "Added choice question " + i + ": " + question.getContent());
                }
            }

            // 处理判断题（支持judgment_question、judgement_question、judgement_questions等多种字段名）
            com.google.gson.JsonArray judgmentArray = null;

            // 优先检查judgement_questions（英国拼写，复数）
            if (root.has("judgement_questions") && root.get("judgement_questions").isJsonArray()) {
                judgmentArray = root.getAsJsonArray("judgement_questions");
                android.util.Log.d("QuizConfigManager", "Found judgement_questions array, size: " + judgmentArray.size());
            }
            // 检查judgment_questions（美国拼写，复数）
            else if (root.has("judgment_questions") && root.get("judgment_questions").isJsonArray()) {
                judgmentArray = root.getAsJsonArray("judgment_questions");
                android.util.Log.d("QuizConfigManager", "Found judgment_questions array, size: " + judgmentArray.size());
            }
            // 检查judgement_question（英国拼写，单数）
            else if (root.has("judgement_question") && root.get("judgement_question").isJsonArray()) {
                judgmentArray = root.getAsJsonArray("judgement_question");
                android.util.Log.d("QuizConfigManager", "Found judgement_question array, size: " + judgmentArray.size());
            }
            // 检查judgment_question（美国拼写，单数）
            else if (root.has("judgment_question") && root.get("judgment_question").isJsonArray()) {
                judgmentArray = root.getAsJsonArray("judgment_question");
                android.util.Log.d("QuizConfigManager", "Found judgment_question array, size: " + judgmentArray.size());
            }

            if (judgmentArray != null && judgmentArray.size() > 0) {
                for (int i = 0; i < judgmentArray.size(); i++) {
                    com.google.gson.JsonObject qJson = judgmentArray.get(i).getAsJsonObject();
                    com.jcoding.aiactivity.entity.Question question = new com.jcoding.aiactivity.entity.Question();

                    question.setQuestionId(bankId + "_judgment_" + i);
                    question.setType("judgement");

                    // 从"panduan"或"question"字段读取题目内容
                    if (qJson.has("panduan")) {
                        question.setContent(qJson.get("panduan").getAsString());
                    } else if (qJson.has("question")) {
                        question.setContent(qJson.get("question").getAsString());
                    }

                    // 判断题选项
                    question.setOptions(new String[]{"对", "错"});

                    // 从"answer"字段读取答案（整数：1=对，0=错）
                    if (qJson.has("answer")) {
                        int answer = qJson.get("answer").getAsInt();
                        question.setCorrectAnswer(answer == 1 ? 0 : 1); // 转换：1->0(对), 0->1(错)
                    }

                    questions.add(question);
                    android.util.Log.d("QuizConfigManager", "Added judgment question " + i + ": " + question.getContent());
                }
            }

            questionBank.setQuestions(questions);
            android.util.Log.d("QuizConfigManager", "Total questions loaded: " + questions.size());

            return questionBank;
        } catch (Exception e) {
            android.util.Log.e("QuizConfigManager", "Error in parseLegacyQuestionBank", e);
            e.printStackTrace();
            return new QuestionBank();
        }
    }

    /**
     * 根据答案文本在选项中查找索引
     */
    private int findAnswerIndex(String answerText, String[] options) {
        if (options == null || answerText == null) {
            return 0;
        }

        for (int i = 0; i < options.length; i++) {
            if (answerText.equals(options[i])) {
                return i;
            }
        }

        return 0;
    }

    /**
     * 解析答案索引
     */
    private int parseAnswerIndex(String answer) {
        if (TextUtils.isEmpty(answer)) {
            return 0;
        }

        // 常见答案映射
        java.util.Map<String, Integer> answerMap = new java.util.HashMap<>();
        answerMap.put("A", 0);
        answerMap.put("B", 1);
        answerMap.put("C", 2);
        answerMap.put("D", 3);
        answerMap.put("对", 0);
        answerMap.put("错", 1);
        answerMap.put("正确", 0);
        answerMap.put("错误", 1);
        answerMap.put("√", 0);
        answerMap.put("×", 1);

        if (answerMap.containsKey(answer)) {
            return answerMap.get(answer);
        }

        // 如果是数字，返回数字
        try {
            return Integer.parseInt(answer);
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    /**
     * 检查指定模块是否启用数字人
     */
    public boolean isDigitalHumanEnabledForModule(String module) {
        // 通过ConfigManager检查数字人配置
        ConfigManager configManager = ConfigManager.getInstance(context);
        return configManager.isDigitalHumanEnabled() && configManager.isDigitalHumanEnabledForModule(module);
    }

    // ========== 标题配置 ==========

    /**
     * 获取问答标题
     */
    public String getQuizTitle() {
        return PreferenceUtils.getString(context, PREF_QUIZ_TITLE, "知识问答");
    }

    /**
     * 设置问答标题
     */
    public void setQuizTitle(String title) {
        PreferenceUtils.putString(context, PREF_QUIZ_TITLE, title);
    }

    // ========== 色彩风格配置 ==========

    /**
     * 获取色彩风格
     */
    public ColorTheme getColorTheme() {
        String code = PreferenceUtils.getString(context, PREF_COLOR_THEME, ColorTheme.TECH_BLUE.getCode());
        return ColorTheme.fromCode(code);
    }

    /**
     * 设置色彩风格
     */
    public void setColorTheme(ColorTheme theme) {
        PreferenceUtils.putString(context, PREF_COLOR_THEME, theme.getCode());
    }

    /**
     * 获取当前主题的主色调
     */
    public int getPrimaryColor() {
        return getColorTheme().getPrimaryColor();
    }

    /**
     * 获取当前主题的深色调
     */
    public int getDarkColor() {
        return getColorTheme().getDarkColor();
    }

    /**
     * 获取当前主题的文字颜色
     */
    public int getTextColor() {
        return getColorTheme().getTextColor();
    }

    /**
     * 获取当前主题的背景色
     */
    public int getBackgroundColor() {
        return getColorTheme().getBackgroundColor();
    }
}
