package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.text.TextUtils;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.reflect.TypeToken;
import com.jcoding.aiactivity.entity.Question;
import com.jcoding.aiactivity.entity.QuestionBank;
import com.jcoding.aiactivity.entity.StyleConfig;
import com.jcoding.aiactivity.utils.ConfigCrypto;
import com.jcoding.aiactivity.utils.PreferenceUtils;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 配置管理器
 * 负责从assets加载配置文件和资源
 */
public class ConfigManager {

    // 原有常量
    private static final String CONFIG_FILE = "config.json";
    private static final String STYLE_CONFIG_FILE = "style/style.json";
    private static final String QUESTION_CONFIG_FILE = "question/config.json";
    private static final String LOTTERY_CONFIG_FILE = "lottery/config.json";
    private static final String AIBEING_CONFIG_FILE = "aibeing/config.json";

    // 新增常量：外部配置目录
    private static final String CONFIG_DIR = "config";
    private static final String CONFIG_DEFAULT = "config/default_config.json";

    private static ConfigManager instance;
    private Context context;
    private JsonObject mainConfig;
    private Map<String, StyleConfig> styleConfigs;
    private Map<String, QuestionBank> questionBanks;
    private JsonObject lotteryConfig;
    private JsonObject aibeingConfig;
    private Gson gson;

    // 新增：解密后的 API 密钥缓存（线程安全访问）
    private final Object apiKeysLock = new Object();
    private volatile JsonObject decryptedApiKeys;
    private volatile String currentVersion;

    private ConfigManager(Context context) {
        this.context = context.getApplicationContext();
        this.gson = new Gson();
        this.styleConfigs = new HashMap<>();
        this.questionBanks = new HashMap<>();
        loadConfigs();
    }

    public static synchronized ConfigManager getInstance(Context context) {
        if (instance == null) {
            instance = new ConfigManager(context);
        }
        return instance;
    }

    /**
     * 加载所有配置文件
     */
    private void loadConfigs() {
        try {
            // 优先级 1: 从外部存储读取主配置（远程更新的配置）
            String mainConfigStr = readExternalConfig(CONFIG_FILE);

            if (mainConfigStr == null) {
                // 优先级 2: 从 assets 读取默认配置
                android.util.Log.i("ConfigManager", "Using default config from assets: " + CONFIG_DEFAULT);
                mainConfigStr = readAssetFile(CONFIG_DEFAULT);
            } else {
                android.util.Log.i("ConfigManager", "Using external config from: " + CONFIG_DIR + "/" + CONFIG_FILE);
            }

            if (!TextUtils.isEmpty(mainConfigStr)) {
                JsonObject rawConfig = gson.fromJson(mainConfigStr, JsonObject.class);

                // 验证配置完整性
                if (validateConfig(rawConfig)) {
                    // 解析并解密配置
                    mainConfig = parseAndDecryptConfig(rawConfig);
                    android.util.Log.i("ConfigManager", "Config loaded and decrypted successfully");
                } else {
                    android.util.Log.e("ConfigManager", "Config validation failed, trying fallback");
                    // 尝试回退到旧的 config.json
                    String fallbackConfigStr = readAssetFile(CONFIG_FILE);
                    if (!TextUtils.isEmpty(fallbackConfigStr)) {
                        mainConfig = gson.fromJson(fallbackConfigStr, JsonObject.class);
                    }
                }
            } else {
                // 最后的回退：尝试读取旧的 config.json
                String fallbackConfigStr = readAssetFile(CONFIG_FILE);
                if (!TextUtils.isEmpty(fallbackConfigStr)) {
                    mainConfig = gson.fromJson(fallbackConfigStr, JsonObject.class);
                }
            }

            // 加载风格配置
            loadStyleConfigs();

            // 加载题库配置
            loadQuestionConfigs();

            // 加载抽奖配置
            android.util.Log.d("ConfigManager", "开始加载抽奖配置: " + LOTTERY_CONFIG_FILE);
            String lotteryConfigStr = readExternalConfigFile(LOTTERY_CONFIG_FILE);
            if (lotteryConfigStr == null) {
                lotteryConfigStr = readAssetFile(LOTTERY_CONFIG_FILE);
            }
            android.util.Log.d("ConfigManager", "lotteryConfigStr = " + (lotteryConfigStr != null ? lotteryConfigStr.substring(0, Math.min(100, lotteryConfigStr.length())) + "..." : "null"));
            if (!TextUtils.isEmpty(lotteryConfigStr)) {
                lotteryConfig = gson.fromJson(lotteryConfigStr, JsonObject.class);
                android.util.Log.d("ConfigManager", "lotteryConfig解析成功: " + (lotteryConfig != null ? lotteryConfig.toString() : "null"));
            } else {
                android.util.Log.e("ConfigManager", "lotteryConfigStr为空，读取失败");
            }

            // 加载数字人配置
            String aibeingConfigStr = readExternalConfigFile(AIBEING_CONFIG_FILE);
            if (aibeingConfigStr == null) {
                aibeingConfigStr = readAssetFile(AIBEING_CONFIG_FILE);
            }
            if (!TextUtils.isEmpty(aibeingConfigStr)) {
                aibeingConfig = gson.fromJson(aibeingConfigStr, JsonObject.class);
            }
        } catch (Exception e) {
            android.util.Log.e("ConfigManager", "Failed to load configs", e);
            e.printStackTrace();
        }
    }

    /**
     * 加载风格配置
     */
    private void loadStyleConfigs() {
        try {
            android.util.Log.d("ConfigManager", "开始加载风格配置: " + STYLE_CONFIG_FILE);
            String styleConfigStr = readExternalConfigFile(STYLE_CONFIG_FILE);
            if (styleConfigStr == null) {
                styleConfigStr = readAssetFile(STYLE_CONFIG_FILE);
            }

            if (TextUtils.isEmpty(styleConfigStr)) {
                android.util.Log.e("ConfigManager", "风格配置文件为空或不存在: " + STYLE_CONFIG_FILE);
                return;
            }

            android.util.Log.d("ConfigManager", "风格配置文件内容长度: " + styleConfigStr.length());

            JsonObject jsonObject = gson.fromJson(styleConfigStr, JsonObject.class);
            if (jsonObject != null && jsonObject.has("style")) {
                JsonObject styleObj = jsonObject.getAsJsonObject("style");
                android.util.Log.d("ConfigManager", "找到 " + styleObj.size() + " 个风格配置");

                for (String styleId : styleObj.keySet()) {
                    JsonObject styleData = styleObj.getAsJsonObject(styleId);
                    StyleConfig config = new StyleConfig();
                    config.setStyleId(styleId);
                    config.setName(styleData.has("name") ? styleData.get("name").getAsString() : "");
                    config.setPrompt(styleData.has("prompt") ? styleData.get("prompt").getAsString() : "");
                    config.setPreviewImage(styleData.has("preview") ? styleData.get("preview").getAsString() : "");

                    // 解析背景图（KV图，backImage），如果没有配置则使用默认背景
                    if (styleData.has("backImage")) {
                        config.setBackImage(styleData.get("backImage").getAsString());
                    } else {
                        config.setBackImage("background/styleBk.png"); // 默认背景图
                    }

                    // 解析遮罩图片 (maskImage)
                    if (styleData.has("maskImage")) {
                        config.setMaskImage(styleData.get("maskImage").getAsString());
                        android.util.Log.d("ConfigManager", "加载风格 " + styleId + " 的maskImage: " + config.getMaskImage());
                    }

                    config.setStatus(styleData.has("status") ? styleData.get("status").getAsInt() : 1);

                    if (styleData.has("reference_images")) {
                        Type listType = new TypeToken<List<String>>() {}.getType();
                        List<String> images = gson.fromJson(styleData.get("reference_images"), listType);
                        config.setReferenceImages(images.toArray(new String[0]));
                    }

                    styleConfigs.put(styleId, config);
                    android.util.Log.d("ConfigManager", "加载风格: " + config.getName() + " (" + styleId + ")");
                }
            } else {
                android.util.Log.e("ConfigManager", "风格配置文件格式错误：缺少 'style' 字段");
            }
        } catch (Exception e) {
            android.util.Log.e("ConfigManager", "加载风格配置失败", e);
            e.printStackTrace();
        }

        android.util.Log.i("ConfigManager", "风格配置加载完成，共 " + styleConfigs.size() + " 个风格");
    }

    /**
     * 加载题库配置
     */
    private void loadQuestionConfigs() {
        try {
            String questionConfigStr = readExternalConfigFile(QUESTION_CONFIG_FILE);
            if (questionConfigStr == null) {
                questionConfigStr = readAssetFile(QUESTION_CONFIG_FILE);
            }
            if (TextUtils.isEmpty(questionConfigStr)) {
                return;
            }

            JsonObject jsonObject = gson.fromJson(questionConfigStr, JsonObject.class);
            if (jsonObject != null && jsonObject.has("catalog")) {
                Type listType = new TypeToken<List<JsonObject>>() {}.getType();
                List<JsonObject> catalog = gson.fromJson(jsonObject.get("catalog"), listType);

                for (JsonObject bankData : catalog) {
                    String qid = bankData.has("qid") ? bankData.get("qid").getAsString() : "";
                    String name = bankData.has("catalog_name") ? bankData.get("catalog_name").getAsString() : "";
                    String file = bankData.has("file") ? bankData.get("file").getAsString() : "";
                    int status = bankData.has("status") ? bankData.get("status").getAsInt() : 1;

                    QuestionBank bank = new QuestionBank(qid, name, file, status);

                    // 加载题库文件
                    List<Question> questions = loadQuestionFile("question/" + file);
                    bank.setQuestions(questions);

                    questionBanks.put(qid, bank);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * 加载题库文件
     */
    private List<Question> loadQuestionFile(String filePath) {
        List<Question> questions = new ArrayList<>();
        try {
            String questionDataStr = readAssetFile(filePath);
            if (TextUtils.isEmpty(questionDataStr)) {
                return questions;
            }

            // 尝试解析为数组
            try {
                Type listType = new TypeToken<List<JsonObject>>() {}.getType();
                List<JsonObject> questionList = gson.fromJson(questionDataStr, listType);

                for (JsonObject qData : questionList) {
                    Question question = parseQuestion(qData);
                    if (question != null) {
                        questions.add(question);
                    }
                }
            } catch (Exception e) {
                // 如果解析数组失败，尝试解析为对象格式 {"choice_question": [...]}
                try {
                    JsonObject jsonObject = gson.fromJson(questionDataStr, JsonObject.class);
                    if (jsonObject != null && jsonObject.has("choice_question")) {
                        Type listType = new TypeToken<List<JsonObject>>() {}.getType();
                        List<JsonObject> questionList = gson.fromJson(jsonObject.get("choice_question"), listType);

                        for (JsonObject qData : questionList) {
                            Question question = parseQuestion(qData);
                            if (question != null) {
                                questions.add(question);
                            }
                        }
                    }
                } catch (Exception e2) {
                    e2.printStackTrace();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return questions;
    }

    /**
     * 解析单个题目
     */
    private Question parseQuestion(JsonObject qData) {
        try {
            Question question = new Question();
            question.setQuestionId(qData.has("id") ? qData.get("id").getAsString() : "");
            question.setType(qData.has("type") ? qData.get("type").getAsString() : "choice");

            // 兼容"choice"和"question"字段
            String content = qData.has("question") ? qData.get("question").getAsString() :
                            qData.has("choice") ? qData.get("choice").getAsString() : "";
            question.setContent(content);

            // 加载选项
            if (question.isChoice() && qData.has("options")) {
                Type optionsType = new TypeToken<List<String>>() {}.getType();
                List<String> options = gson.fromJson(qData.get("options"), optionsType);
                question.setOptions(options.toArray(new String[0]));
            }

            // 加载答案（支持字符串和数组格式）
            if (qData.has("answer")) {
                String answer;
                try {
                    // 尝试作为数组解析 ["公益事业"]
                    Type listType = new TypeToken<List<String>>() {}.getType();
                    List<String> answerList = gson.fromJson(qData.get("answer"), listType);
                    answer = answerList != null && !answerList.isEmpty() ? answerList.get(0) : "";
                } catch (Exception e) {
                    // 作为字符串解析
                    answer = qData.get("answer").getAsString();
                }
                question.setCorrectAnswer(parseAnswerIndex(answer));
            }

            // 加载解析
            question.setExplanation(qData.has("explanation") ? qData.get("explanation").getAsString() : "");

            return question;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 解析答案索引
     */
    private int parseAnswerIndex(String answer) {
        if (TextUtils.isEmpty(answer)) {
            return 0;
        }

        answer = answer.toUpperCase().trim();
        switch (answer) {
            case "A":
            case "对":
            case "正确":
            case "T":
            case "TRUE":
                return 0;
            case "B":
            case "错":
            case "错误":
            case "F":
            case "FALSE":
                return 1;
            case "C":
                return 2;
            case "D":
                return 3;
            default:
                try {
                    return Integer.parseInt(answer);
                } catch (NumberFormatException e) {
                    return 0;
                }
        }
    }

    /**
     * 读取assets文件
     */
    private String readAssetFile(String filePath) {
        try {
            android.util.Log.d("ConfigManager", "读取assets文件: " + filePath);
            InputStream is = context.getAssets().open(filePath);
            int size = is.available();
            android.util.Log.d("ConfigManager", "文件大小: " + size + " 字节");
            byte[] buffer = new byte[size];
            is.read(buffer);
            is.close();
            String result = new String(buffer, StandardCharsets.UTF_8);
            android.util.Log.d("ConfigManager", "读取成功: " + filePath);
            return result;
        } catch (IOException e) {
            android.util.Log.e("ConfigManager", "读取assets文件失败: " + filePath, e);
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 从外部存储读取配置（远程更新的配置）
     */
    private String readExternalConfig(String fileName) {
        try {
            File configDir = new File(context.getExternalFilesDir(null), CONFIG_DIR);
            File configFile = new File(configDir, fileName);

            if (!configFile.exists()) {
                android.util.Log.d("ConfigManager", "External config not found: " + configFile.getAbsolutePath());
                return null;
            }

            StringBuilder sb = new StringBuilder();
            BufferedReader reader = new BufferedReader(new FileReader(configFile));
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            reader.close();

            android.util.Log.i("ConfigManager", "External config loaded: " + configFile.getAbsolutePath());
            return sb.toString();

        } catch (IOException e) {
            android.util.Log.e("ConfigManager", "Failed to read external config: " + fileName, e);
            return null;
        }
    }

    /**
     * 从外部存储读取配置文件（独立配置文件）
     */
    private String readExternalConfigFile(String relativePath) {
        return readExternalConfig(relativePath);
    }

    /**
     * 验证配置文件完整性
     *
     * 验证项：
     * - _meta 部分存在
     * - version 字段存在且格式正确（v1.2.3 格式）
     * - _encrypted 部分是可选的（向后兼容）
     *
     * @param config 待验证的配置对象
     * @return true 如果配置有效，false 否则
     */
    private boolean validateConfig(JsonObject config) {
        if (config == null) {
            android.util.Log.e("ConfigManager", "Config validation failed: config is null");
            return false;
        }

        if (!config.has("_meta")) {
            android.util.Log.e("ConfigManager", "Config validation failed: missing _meta section");
            return false;
        }

        JsonObject meta = config.getAsJsonObject("_meta");
        if (!meta.has("version")) {
            android.util.Log.e("ConfigManager", "Config validation failed: missing version in _meta");
            return false;
        }

        // 验证版本号格式（v1.2.3 或 v1.2.30 等）
        String version = meta.get("version").getAsString();
        if (!version.matches("^v\\d+\\.\\d+\\.\\d+$")) {
            android.util.Log.e("ConfigManager", "Config validation failed: invalid version format: " + version);
            return false;
        }

        // _encrypted 是可选的，用于向后兼容
        if (!config.has("_encrypted")) {
            android.util.Log.w("ConfigManager", "No _encrypted section in config, plain text mode");
        }

        android.util.Log.i("ConfigManager", "Config validation passed: version=" + version);
        return true;
    }

    /**
     * 解析并解密配置
     *
     * 安全说明：
     * - 任何解密失败都会抛出异常，不会使用损坏的配置
     * - 线程安全：使用 synchronized 块保护 decryptedApiKeys 访问
     *
     * @param rawConfig 原始配置对象（包含加密字段）
     * @return 解密后的配置对象
     * @throws RuntimeException 如果配置验证或解密失败
     */
    private JsonObject parseAndDecryptConfig(JsonObject rawConfig) {
        try {
            // 验证并获取版本号
            if (rawConfig.has("_meta")) {
                JsonObject meta = rawConfig.getAsJsonObject("_meta");
                String version = meta.get("version").getAsString();

                // 验证版本号格式（v1.2.3 或 v1.2.30 等）
                if (!version.matches("^v\\d+\\.\\d+\\.\\d+$")) {
                    throw new IllegalArgumentException("Invalid version format: " + version);
                }

                synchronized (apiKeysLock) {
                    currentVersion = version;
                }
            } else {
                throw new IllegalArgumentException("Missing _meta.version in config");
            }

            android.util.Log.i("ConfigManager", "Config version: " + currentVersion);

            // 解密 _encrypted 部分
            android.util.Log.d("ConfigManager", "Checking for _encrypted section...");
            if (rawConfig.has("_encrypted")) {
                android.util.Log.d("ConfigManager", "_encrypted section found");
                JsonObject encrypted = rawConfig.getAsJsonObject("_encrypted");

                // 解密 API 密钥（线程安全）
                android.util.Log.d("ConfigManager", "Checking for api_keys in _encrypted...");
                if (encrypted.has("api_keys")) {
                    android.util.Log.d("ConfigManager", "api_keys found, starting decryption...");
                    JsonObject apiKeys = encrypted.getAsJsonObject("api_keys");
                    JsonObject decrypted = decryptApiKeys(apiKeys, currentVersion);

                    synchronized (apiKeysLock) {
                        decryptedApiKeys = decrypted;
                    }

                    android.util.Log.i("ConfigManager", "API keys decrypted for " + decrypted.size() + " services");
                }

                // 解密管理员密码
                if (encrypted.has("admin")) {
                    JsonObject admin = encrypted.getAsJsonObject("admin");
                    // TODO: 解密并缓存管理员密码
                }

                // 解密 LLM 配置
                if (encrypted.has("llm")) {
                    JsonObject llm = encrypted.getAsJsonObject("llm");
                    // TODO: 解密并缓存 LLM 配置
                }
            } else {
                android.util.Log.w("ConfigManager", "No _encrypted section in config");
                synchronized (apiKeysLock) {
                    decryptedApiKeys = new JsonObject();
                }
            }

            return rawConfig;

        } catch (Exception e) {
            android.util.Log.e("ConfigManager", "CRITICAL: Failed to parse/decrypt config. " +
                "This may indicate: 1) Corrupted config file, 2) Version mismatch, 3) Tampering detected", e);
            // 不再静默失败 - 抛出异常让调用方处理
            throw new RuntimeException("Failed to decrypt configuration", e);
        }
    }

    /**
     * 解密 API 密钥
     *
     * 安全说明：
     * - 任何密钥解密失败都会抛出异常
     * - SERVER_ENC: 字段会抛出异常（当前未实现服务器解密）
     * - 不会使用部分解密的配置
     *
     * @param encryptedKeys 加密的 API 密钥对象
     * @param version 版本号
     * @return 解密后的 API 密钥对象
     * @throws RuntimeException 如果任何密钥解密失败
     */
    private JsonObject decryptApiKeys(JsonObject encryptedKeys, String version) {
        android.util.Log.d("ConfigManager", "decryptApiKeys called with " + encryptedKeys.keySet().size() + " services");
        JsonObject decrypted = new JsonObject();
        int successCount = 0;
        int failureCount = 0;

        for (String service : encryptedKeys.keySet()) {
            android.util.Log.d("ConfigManager", "Decrypting service: " + service);
            JsonObject serviceKeys = encryptedKeys.getAsJsonObject(service);
            JsonObject decryptedService = new JsonObject();

            for (String key : serviceKeys.keySet()) {
                try {
                    String encryptedValue = serviceKeys.get(key).getAsString();

                    // 检查是否为服务器额外加密
                    if (encryptedValue.startsWith("SERVER_ENC:")) {
                        // 服务器额外加密，需要特殊处理
                        String serverEncrypted = encryptedValue.substring("SERVER_ENC:".length());
                        try {
                            String decryptedValue = ConfigCrypto.decryptServerEncrypted(serverEncrypted, null);
                            decryptedService.addProperty(key, decryptedValue);
                            successCount++;
                        } catch (UnsupportedOperationException e) {
                            // SERVER_ENC 解密未实现 - 记录并继续抛出
                            android.util.Log.e("ConfigManager",
                                "SERVER_ENC field detected in " + service + "." + key +
                                " but server decryption not implemented");
                            throw e;
                        }
                    } else {
                        // 常规版本号加密
                        String decryptedValue = ConfigCrypto.decrypt(encryptedValue, version);
                        decryptedService.addProperty(key, decryptedValue);
                        successCount++;
                    }

                } catch (Exception e) {
                    failureCount++;
                    android.util.Log.e("ConfigManager",
                        "CRITICAL: Failed to decrypt " + service + "." + key +
                        ". Possible causes: 1) Corrupted config, 2) Wrong version: " + version, e);
                    // 不再静默失败 - 抛出异常
                    throw new RuntimeException("Failed to decrypt API key: " + service + "." + key, e);
                }
            }

            decrypted.add(service, decryptedService);
        }

        android.util.Log.i("ConfigManager",
            "API key decryption: " + successCount + " succeeded, " + failureCount + " failed");

        return decrypted;
    }

    /**
     * 获取解密后的 API 密钥
     */
    /**
     * 获取解密后的 API 密钥（线程安全）
     *
     * @param service 服务名称（如 "minimax", "tencent_tts"）
     * @param key 密钥名称（如 "api_key", "secret_id"）
     * @return 解密后的密钥值，如果不存在返回 null
     */
    private String getDecryptedApiKey(String service, String key) {
        synchronized (apiKeysLock) {
            if (decryptedApiKeys != null && decryptedApiKeys.has(service)) {
                JsonObject serviceConfig = decryptedApiKeys.getAsJsonObject(service);
                if (serviceConfig.has(key)) {
                    return serviceConfig.get(key).getAsString();
                }
            }
            return null;
        }
    }

    // ========== 公共方法 ==========

    /**
     * 重载配置（远程更新后调用）
     */
    public void reload() {
        android.util.Log.i("ConfigManager", "Reloading configuration...");
        styleConfigs.clear();
        questionBanks.clear();
        loadConfigs();
    }

    /**
     * 获取所有风格配置（仅启用状态）
     */
    public List<StyleConfig> getStyleConfigs() {
        List<StyleConfig> list = new ArrayList<>();
        for (StyleConfig config : styleConfigs.values()) {
            if (config.isEnabled()) {
                list.add(config);
            }
        }
        return list;
    }

    /**
     * 获取所有风格配置（包括禁用的）
     */
    public List<StyleConfig> getAllStyleConfigs() {
        List<StyleConfig> list = new ArrayList<>();
        for (StyleConfig config : styleConfigs.values()) {
            list.add(config);
        }
        return list;
    }

    /**
     * 根据ID获取风格配置
     */
    public StyleConfig getStyleConfig(String styleId) {
        return styleConfigs.get(styleId);
    }

    /**
     * 设置风格启用状态
     * @param styleId 风格ID
     * @param enabled true=启用，false=禁用
     */
    public void setStyleEnabled(String styleId, boolean enabled) {
        StyleConfig config = styleConfigs.get(styleId);
        if (config != null) {
            config.setStatus(enabled ? 1 : 0);
            // 保存到SharedPreferences
            String key = "style_enabled_" + styleId;
            PreferenceUtils.putBoolean(context, key, enabled);
            android.util.Log.d("ConfigManager", "Style " + styleId + " enabled: " + enabled);
        }
    }

    /**
     * 获取风格启用状态
     * @param styleId 风格ID
     * @return true=启用，false=禁用
     */
    public boolean isStyleEnabled(String styleId) {
        // 先检查SharedPreferences中的用户设置
        String key = "style_enabled_" + styleId;
        Boolean userSetting = PreferenceUtils.getBooleanObject(context, key, null);
        if (userSetting != null) {
            return userSetting;
        }

        // 如果用户没有设置，返回配置文件中的状态
        StyleConfig config = styleConfigs.get(styleId);
        return config != null && config.isEnabled();
    }

    /**
     * 获取所有题库
     */
    public List<QuestionBank> getQuestionBanks() {
        List<QuestionBank> list = new ArrayList<>();
        for (QuestionBank bank : questionBanks.values()) {
            if (bank.isEnabled()) {
                list.add(bank);
            }
        }
        return list;
    }

    /**
     * 根据ID获取题库
     */
    public QuestionBank getQuestionBank(String bankId) {
        return questionBanks.get(bankId);
    }

    /**
     * 获取默认题库
     */
    public QuestionBank getDefaultQuestionBank() {
        if (questionBanks.isEmpty()) {
            return null;
        }
        for (QuestionBank bank : questionBanks.values()) {
            if (bank.isEnabled()) {
                return bank;
            }
        }
        return null;
    }

    /**
     * 从assets加载图片
     */
    public Bitmap loadImageFromAssets(String filePath) {
        InputStream is = null;
        try {
            // 尝试直接打开路径
            try {
                android.util.Log.d("ConfigManager", "Trying to load: " + filePath);
                is = context.getAssets().open(filePath);
                Bitmap bitmap = BitmapFactory.decodeStream(is);
                if (bitmap != null) {
                    android.util.Log.d("ConfigManager", "Successfully loaded: " + filePath);
                } else {
                    android.util.Log.w("ConfigManager", "BitmapFactory.decodeStream returned null for: " + filePath);
                }
                return bitmap;
            } catch (IOException e) {
                android.util.Log.w("ConfigManager", "Failed to open " + filePath + ", trying alternative path");
                // 如果失败且是style图片，尝试添加images/子目录
                if (filePath.startsWith("style/") && !filePath.contains("/images/")) {
                    String alternativePath = filePath.replace("style/", "style/images/");
                    android.util.Log.d("ConfigManager", "Trying alternative path: " + alternativePath);
                    try {
                        is = context.getAssets().open(alternativePath);
                        Bitmap bitmap = BitmapFactory.decodeStream(is);
                        if (bitmap != null) {
                            android.util.Log.d("ConfigManager", "Successfully loaded from alternative: " + alternativePath);
                        } else {
                            android.util.Log.w("ConfigManager", "BitmapFactory.decodeStream returned null for alternative: " + alternativePath);
                        }
                        return bitmap;
                    } catch (IOException e2) {
                        android.util.Log.e("ConfigManager", "Failed to load from both paths: " + filePath + " and " + alternativePath, e2);
                    }
                }
                throw e;
            }
        } catch (IOException e) {
            android.util.Log.e("ConfigManager", "Error loading image from assets: " + filePath, e);
            return null;
        } finally {
            if (is != null) {
                try {
                    is.close();
                } catch (IOException e) {
                    android.util.Log.e("ConfigManager", "Error closing InputStream", e);
                }
            }
        }
    }

    /**
     * 获取抽奖配置
     */
    public JsonObject getLotteryConfig() {
        return lotteryConfig;
    }

    /**
     * 获取数字人配置
     */
    public JsonObject getAibeingConfig() {
        return aibeingConfig;
    }

    /**
     * 获取题库配置
     */
    public JsonObject getQuestionConfig() {
        try {
            String questionConfigStr = readAssetFile(QUESTION_CONFIG_FILE);
            if (!TextUtils.isEmpty(questionConfigStr)) {
                return gson.fromJson(questionConfigStr, JsonObject.class);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    // ==================== AI百变秀配置方法 ====================

    /**
     * 检查AI百变秀模块是否启用
     */
    public boolean isAiShowEnabled() {
        // 先检查SharedPreferences中的用户设置
        Boolean userSetting = PreferenceUtils.getBooleanObject(context, "ai_show_enabled", null);
        if (userSetting != null) {
            return userSetting;
        }

        // 如果用户没有设置，读取配置文件的默认值
        if (mainConfig != null && mainConfig.has("features")) {
            JsonObject features = mainConfig.getAsJsonObject("features");
            if (features.has("ai_show")) {
                JsonObject aiShow = features.getAsJsonObject("ai_show");
                return aiShow.has("enabled") ? aiShow.get("enabled").getAsBoolean() : true;
            }
        }
        return true; // 默认启用
    }

    /**
     * 设置AI百变秀模块启用状态
     */
    public void setAiShowEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "ai_show_enabled", enabled);
    }

    /**
     * 获取AI百变秀默认风格ID
     */
    public String getAiShowDefaultStyle() {
        return PreferenceUtils.getString(context, "ai_show_default_style", "");
    }

    /**
     * 设置AI百变秀默认风格ID
     */
    public void setAiShowDefaultStyle(String styleId) {
        PreferenceUtils.putString(context, "ai_show_default_style", styleId);
    }

    /**
     * 获取AI百变秀轮播间隔（毫秒）
     */
    public int getAiShowCarouselInterval() {
        return PreferenceUtils.getInt(context, "ai_show_carousel_interval", 5000); // 默认5秒
    }

    /**
     * 设置AI百变秀轮播间隔（毫秒）
     */
    public void setAiShowCarouselInterval(int intervalMillis) {
        PreferenceUtils.putInt(context, "ai_show_carousel_interval", intervalMillis);
    }

    /**
     * 检查邀请码模式是否启用
     */
    public boolean isInviteCodeModeEnabled() {
        Boolean userSetting = PreferenceUtils.getBooleanObject(context, "invite_code_mode_enabled", null);
        if (userSetting != null) {
            return userSetting;
        }

        if (mainConfig != null && mainConfig.has("features")) {
            JsonObject features = mainConfig.getAsJsonObject("features");
            if (features.has("ai_show")) {
                JsonObject aiShow = features.getAsJsonObject("ai_show");
                return aiShow.has("invite_code_mode") ? aiShow.get("invite_code_mode").getAsBoolean() : true;
            }
        }
        return true;
    }

    /**
     * 设置邀请码模式启用状态
     */
    public void setInviteCodeModeEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "invite_code_mode_enabled", enabled);
    }

    /**
     * 检查支付模式是否启用
     */
    public boolean isPaymentModeEnabled() {
        Boolean userSetting = PreferenceUtils.getBooleanObject(context, "payment_mode_enabled", null);
        if (userSetting != null) {
            return userSetting;
        }

        if (mainConfig != null && mainConfig.has("features")) {
            JsonObject features = mainConfig.getAsJsonObject("features");
            if (features.has("ai_show")) {
                JsonObject aiShow = features.getAsJsonObject("ai_show");
                return aiShow.has("payment_mode") ? aiShow.get("payment_mode").getAsBoolean() : true;
            }
        }
        return true;
    }

    /**
     * 设置支付模式启用状态
     */
    public void setPaymentModeModeEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "payment_mode_enabled", enabled);
    }

    /**
     * 检查员工模式是否启用
     */
    public boolean isEmployeeModeEnabled() {
        Boolean userSetting = PreferenceUtils.getBooleanObject(context, "employee_mode_enabled", null);
        if (userSetting != null) {
            return userSetting;
        }

        if (mainConfig != null && mainConfig.has("features")) {
            JsonObject features = mainConfig.getAsJsonObject("features");
            if (features.has("ai_show")) {
                JsonObject aiShow = features.getAsJsonObject("ai_show");
                return aiShow.has("employee_mode") ? aiShow.get("employee_mode").getAsBoolean() : true;
            }
        }
        return true;
    }

    /**
     * 设置员工模式启用状态
     */
    public void setEmployeeModeEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "employee_mode_enabled", enabled);
    }

    /**
     * 获取生成照片自动关闭时间（秒）
     */
    public int getAutoCloseTime() {
        Integer userSetting = PreferenceUtils.getInt(context, "auto_close_time", null);
        if (userSetting != null) {
            return userSetting;
        }

        if (mainConfig != null && mainConfig.has("features")) {
            JsonObject features = mainConfig.getAsJsonObject("features");
            if (features.has("ai_show")) {
                JsonObject aiShow = features.getAsJsonObject("ai_show");
                return aiShow.has("auto_close_time") ? aiShow.get("auto_close_time").getAsInt() : 20;
            }
        }
        return 20; // 默认20秒
    }

    /**
     * 设置生成照片自动关闭时间（秒）
     */
    public void setAutoCloseTime(int seconds) {
        PreferenceUtils.putInt(context, "auto_close_time", seconds);
    }

    /**
     * 检查语音指引是否启用
     */
    public boolean isVoiceGuidanceEnabled() {
        return PreferenceUtils.getBoolean(context, "voice_guidance_enabled", true);
    }

    /**
     * 设置语音指引启用状态
     */
    public void setVoiceGuidanceEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "voice_guidance_enabled", enabled);
    }

    /**
     * 检查数字人是否启用
     */
    public boolean isDigitalHumanEnabled() {
        return PreferenceUtils.getBoolean(context, "digital_human_enabled", true);
    }

    /**
     * 设置数字人启用状态
     */
    public void setDigitalHumanEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "digital_human_enabled", enabled);
    }

    /**
     * 获取默认数字人ID
     */
    public String getDefaultDigitalHumanId() {
        return PreferenceUtils.getString(context, "digital_human_id", "");
    }

    /**
     * 设置默认数字人ID
     */
    public void setDefaultDigitalHumanId(String digitalHumanId) {
        PreferenceUtils.putString(context, "digital_human_id", digitalHumanId);
    }

    /**
     * 检查语音命令是否启用
     */
    public boolean isVoiceCommandEnabled() {
        return PreferenceUtils.getBoolean(context, "voice_command_enabled", true);
    }

    /**
     * 设置语音命令启用状态
     */
    public void setVoiceCommandEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "voice_command_enabled", enabled);
    }

    /**
     * 检查自动推送到内场秀是否启用
     */
    public boolean isAutoPushInnerEnabled() {
        return PreferenceUtils.getBoolean(context, "auto_push_inner_enabled", false);
    }

    /**
     * 设置自动推送到内场秀启用状态
     */
    public void setAutoPushInnerEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "auto_push_inner_enabled", enabled);
    }

    /**
     * 检查是否显示生成时间
     */
    public boolean isShowGenerationTimeEnabled() {
        return PreferenceUtils.getBoolean(context, "show_generation_time_enabled", true);
    }

    /**
     * 设置显示生成时间
     */
    public void setShowGenerationTimeEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "show_generation_time_enabled", enabled);
    }

    /**
     * 检查是否启用离线模式
     */
    public boolean isOfflineModeEnabled() {
        return PreferenceUtils.getBoolean(context, "offline_mode_enabled", false);
    }

    /**
     * 设置离线模式
     */
    public void setOfflineModeEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "offline_mode_enabled", enabled);
    }

    /**
     * 检查是否签名提醒
     */
    public boolean isSignatureReminderEnabled() {
        return PreferenceUtils.getBoolean(context, "signature_reminder_enabled", true);
    }

    /**
     * 设置签名提醒
     */
    public void setSignatureReminderEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, "signature_reminder_enabled", enabled);
    }

    /**
     * 获取拍照倒计时时间（秒）
     * @return 倒计时秒数，默认20秒
     */
    public int getPhotoCountdownSeconds() {
        return PreferenceUtils.getInt(context, "photo_countdown_seconds", 20);
    }

    /**
     * 设置拍照倒计时时间（秒）
     * @param seconds 倒计时秒数，建议范围5-60秒
     */
    public void setPhotoCountdownSeconds(int seconds) {
        PreferenceUtils.putInt(context, "photo_countdown_seconds", seconds);
    }

    // ==================== 数字人高级配置 ====================

    /**
     * 检查指定模块的数字人是否启用
     * @param module 模块名称: "ai_show", "quiz", "lottery", "inner"
     */
    public boolean isDigitalHumanEnabledForModule(String module) {
        String prefKey = "digital_human_enabled_" + module;
        Boolean userSetting = PreferenceUtils.getBooleanObject(context, prefKey, null);
        if (userSetting != null) {
            return userSetting;
        }
        // AI百变秀默认关闭数字人
        if ("ai_show".equals(module)) {
            return false;
        }
        // 其他模块默认跟随总开关
        return isDigitalHumanEnabled();
    }

    /**
     * 设置指定模块的数字人启用状态
     * @param module 模块名称: "ai_show", "quiz", "lottery", "inner"
     */
    public void setDigitalHumanEnabledForModule(String module, boolean enabled) {
        String prefKey = "digital_human_enabled_" + module;
        PreferenceUtils.putBoolean(context, prefKey, enabled);
    }

    /**
     * 获取数字人显示位置
     * @return 位置: "top", "middle", "bottom", "bottom_right"
     */
    public String getDigitalHumanPosition() {
        String position = PreferenceUtils.getString(context, "digital_human_position", null);
        if (position != null) {
            return position;
        }
        // 从配置文件读取
        if (mainConfig != null && mainConfig.has("digital_human")) {
            JsonObject digitalHumanConfig = mainConfig.getAsJsonObject("digital_human");
            if (digitalHumanConfig.has("position")) {
                return digitalHumanConfig.get("position").getAsString();
            }
        }
        // 默认位置：底部
        return "bottom";
    }

    /**
     * 设置数字人显示位置
     * @param position 位置: "top", "middle", "bottom", "bottom_right"
     */
    public void setDigitalHumanPosition(String position) {
        PreferenceUtils.putString(context, "digital_human_position", position);
    }

    /**
     * 获取数字人显示大小（高度dp）
     * @return 高度值（100-400dp）
     */
    public int getDigitalHumanSize() {
        Integer size = PreferenceUtils.getInt(context, "digital_human_size", null);
        if (size != null) {
            return size;
        }
        // 从配置文件读取
        if (mainConfig != null && mainConfig.has("digital_human")) {
            JsonObject digitalHumanConfig = mainConfig.getAsJsonObject("digital_human");
            if (digitalHumanConfig.has("size_dp")) {
                return digitalHumanConfig.get("size_dp").getAsInt();
            }
        }
        // 默认大小：200dp
        return 200;
    }

    /**
     * 设置数字人显示大小
     * @param sizeDp 高度值（100-400dp）
     */
    public void setDigitalHumanSize(int sizeDp) {
        PreferenceUtils.putInt(context, "digital_human_size", sizeDp);
    }

    /**
     * 获取数字人缩放模式
     * @return 缩放模式: "fit_center", "center_crop", "center"
     */
    public String getDigitalHumanScaleType() {
        String scaleType = PreferenceUtils.getString(context, "digital_human_scale_type", null);
        if (scaleType != null) {
            return scaleType;
        }
        // 默认缩放模式：fit_center
        return "fit_center";
    }

    /**
     * 设置数字人缩放模式
     * @param scaleType 缩放模式: "fit_center", "center_crop", "center"
     */
    public void setDigitalHumanScaleType(String scaleType) {
        PreferenceUtils.putString(context, "digital_human_scale_type", scaleType);
    }

    /**
     * 获取数字人X轴位置（百分比 0-100）
     * @return X轴位置百分比，默认85（右下角区域）
     */
    public int getDigitalHumanPositionX() {
        Integer posX = PreferenceUtils.getInt(context, "digital_human_position_x", null);
        if (posX != null) {
            return posX;
        }
        // 默认X位置：85%（右侧）
        return 85;
    }

    /**
     * 设置数字人X轴位置
     * @param posX X轴位置百分比（0-100）
     */
    public void setDigitalHumanPositionX(int posX) {
        PreferenceUtils.putInt(context, "digital_human_position_x", posX);
    }

    /**
     * 获取数字人Y轴位置（百分比 0-100）
     * @return Y轴位置百分比，默认85（底部区域）
     */
    public int getDigitalHumanPositionY() {
        Integer posY = PreferenceUtils.getInt(context, "digital_human_position_y", null);
        if (posY != null) {
            return posY;
        }
        // 默认Y位置：85%（底部）
        return 85;
    }

    /**
     * 设置数字人Y轴位置
     * @param posY Y轴位置百分比（0-100）
     */
    public void setDigitalHumanPositionY(int posY) {
        PreferenceUtils.putInt(context, "digital_human_position_y", posY);
    }

    /**
     * 获取数字人是否锁定（禁止拖拽和缩放）
     * @return true=锁定，false=未锁定
     */
    public boolean isDigitalHumanLocked() {
        return PreferenceUtils.getBoolean(context, "digital_human_locked", false);
    }

    /**
     * 设置数字人锁定状态
     * @param locked true=锁定，false=未锁定
     */
    public void setDigitalHumanLocked(boolean locked) {
        PreferenceUtils.putBoolean(context, "digital_human_locked", locked);
    }

    // ==================== 语音参数配置 ====================

    /**
     * 获取TTS发音人
     * @return 发音人代码: 1001=智瑜, 1002=智云, 1003=智莉, 1004=智言
     */
    public int getTTSVoiceType() {
        Integer voiceType = PreferenceUtils.getInt(context, "tts_voice_type", null);
        if (voiceType != null) {
            return voiceType;
        }
        // 默认发音人：智瑜
        return 1001;
    }

    /**
     * 设置TTS发音人
     * @param voiceType 发音人代码
     */
    public void setTTSVoiceType(int voiceType) {
        PreferenceUtils.putInt(context, "tts_voice_type", voiceType);
    }

    /**
     * 获取TTS语速
     * @return 语速值（0.5-2.0）
     */
    public float getTTSSpeed() {
        Float speed = PreferenceUtils.getFloat(context, "tts_speed", null);
        if (speed != null) {
            return speed;
        }
        // 默认语速：1.0
        return 1.0f;
    }

    /**
     * 设置TTS语速
     * @param speed 语速值（0.5-2.0）
     */
    public void setTTSSpeed(float speed) {
        PreferenceUtils.putFloat(context, "tts_speed", speed);
    }

    /**
     * 获取TTS音调
     * @return 音调值（0.5-2.0）
     */
    public float getTTSPitch() {
        Float pitch = PreferenceUtils.getFloat(context, "tts_pitch", null);
        if (pitch != null) {
            return pitch;
        }
        // 默认音调：1.0
        return 1.0f;
    }

    /**
     * 设置TTS音调
     * @param pitch 音调值（0.5-2.0）
     */
    public void setTTSPitch(float pitch) {
        PreferenceUtils.putFloat(context, "tts_pitch", pitch);
    }

    /**
     * 获取TTS音量
     * @return 音量值（0.0-1.0）
     */
    public float getTTSVolume() {
        Float volume = PreferenceUtils.getFloat(context, "tts_volume", null);
        if (volume != null) {
            return volume;
        }
        // 默认音量：1.0
        return 1.0f;
    }

    /**
     * 设置TTS音量
     * @param volume 音量值（0.0-1.0）
     */
    public void setTTSVolume(float volume) {
        PreferenceUtils.putFloat(context, "tts_volume", volume);
    }

    /**
     * 获取ASR引擎模型类型
     * @return 引擎类型: "16k_zh", "8k_zh", "16k_en"
     */
    public String getASREngineModelType() {
        String engineType = PreferenceUtils.getString(context, "asr_engine_model_type", null);
        if (engineType != null) {
            return engineType;
        }
        // 默认引擎：16k中文
        return "16k_zh";
    }

    /**
     * 设置ASR引擎模型类型
     * @param engineType 引擎类型: "16k_zh", "8k_zh", "16k_en"
     */
    public void setASREngineModelType(String engineType) {
        PreferenceUtils.putString(context, "asr_engine_model_type", engineType);
    }

    /**
     * 检查是否过滤脏话
     */
    public boolean isASRFilterDirty() {
        return PreferenceUtils.getBoolean(context, "asr_filter_dirty", false);
    }

    /**
     * 设置是否过滤脏话
     */
    public void setASRFilterDirty(boolean filter) {
        PreferenceUtils.putBoolean(context, "asr_filter_dirty", filter);
    }

    /**
     * 检查是否过滤语气词
     */
    public boolean isASRFilterModal() {
        return PreferenceUtils.getBoolean(context, "asr_filter_modal", true);
    }

    /**
     * 设置是否过滤语气词
     */
    public void setASRFilterModal(boolean filter) {
        PreferenceUtils.putBoolean(context, "asr_filter_modal", filter);
    }

    /**
     * 检查是否转换数字为阿拉伯数字
     */
    public boolean isASRConvertNumMode() {
        return PreferenceUtils.getBoolean(context, "asr_convert_num_mode", true);
    }

    /**
     * 设置是否转换数字为阿拉伯数字
     */
    public void setASRConvertNumMode(boolean convert) {
        PreferenceUtils.putBoolean(context, "asr_convert_num_mode", convert);
    }

    // ==================== 内场秀控制器配置 ====================

    /**
     * 获取控制器连接的服务器地址
     * @return 服务器地址，格式：192.168.1.100:8888
     */
    public String getControllerServerHost(String defaultValue) {
        return PreferenceUtils.getString(context, "controller_server_host", defaultValue);
    }

    /**
     * 设置控制器连接的服务器地址
     * @param host 服务器地址，格式：192.168.1.100:8888
     */
    public void setControllerServerHost(String host) {
        PreferenceUtils.putString(context, "controller_server_host", host);
    }

    /**
     * 获取控制器的服务器密码
     * @return 服务器密码
     */
    public String getControllerServerPassword(String defaultValue) {
        return PreferenceUtils.getString(context, "controller_server_password", defaultValue);
    }

    /**
     * 设置控制器的服务器密码
     * @param password 服务器密码
     */
    public void setControllerServerPassword(String password) {
        PreferenceUtils.putString(context, "controller_server_password", password);
    }

    // ==================== 内场秀服务器配置 ====================

    /**
     * 获取内场秀服务器密码
     * @return 服务器密码，默认值：123456
     */
    public String getInnerShowServerPassword() {
        return PreferenceUtils.getString(context, "inner_show_server_password", "123456");
    }

    /**
     * 设置内场秀服务器密码
     * @param password 服务器密码
     */
    public void setInnerShowServerPassword(String password) {
        PreferenceUtils.putString(context, "inner_show_server_password", password);
    }

    /**
     * 获取内场秀服务器端口
     * @return 端口号，默认值：8888
     */
    public int getInnerShowServerPort(int defaultValue) {
        return PreferenceUtils.getInt(context, "inner_show_server_port", defaultValue);
    }

    /**
     * 设置内场秀服务器端口
     * @param port 端口号
     */
    public void setInnerShowServerPort(int port) {
        PreferenceUtils.putInt(context, "inner_show_server_port", port);
    }

    // ==================== 内场秀模块配置 ====================

    /**
     * 获取内场秀模块是否接受广播
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public boolean getInnerShowAcceptBroadcast(String moduleId) {
        return PreferenceUtils.getBoolean(context, "inner_show_" + moduleId + "_accept_broadcast", true);
    }

    /**
     * 设置内场秀模块是否接受广播
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowAcceptBroadcast(String moduleId, boolean accept) {
        PreferenceUtils.putBoolean(context, "inner_show_" + moduleId + "_accept_broadcast", accept);
    }

    /**
     * 获取内场秀模块广播是否静音
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public boolean getInnerShowBroadcastMuted(String moduleId) {
        return PreferenceUtils.getBoolean(context, "inner_show_" + moduleId + "_broadcast_muted", false);
    }

    /**
     * 设置内场秀模块广播是否静音
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowBroadcastMuted(String moduleId, boolean muted) {
        PreferenceUtils.putBoolean(context, "inner_show_" + moduleId + "_broadcast_muted", muted);
    }

    /**
     * 获取内场秀模块是否开启语音
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public boolean getInnerShowVoiceEnabled(String moduleId) {
        return PreferenceUtils.getBoolean(context, "inner_show_" + moduleId + "_voice_enabled", true);
    }

    /**
     * 设置内场秀模块是否开启语音
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowVoiceEnabled(String moduleId, boolean enabled) {
        PreferenceUtils.putBoolean(context, "inner_show_" + moduleId + "_voice_enabled", enabled);
    }

    /**
     * 获取内场秀模块背景图片
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public String getInnerShowBackground(String moduleId) {
        return PreferenceUtils.getString(context, "inner_show_" + moduleId + "_background", null);
    }

    /**
     * 设置内场秀模块背景图片
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowBackground(String moduleId, String backgroundPath) {
        PreferenceUtils.putString(context, "inner_show_" + moduleId + "_background", backgroundPath);
    }

    /**
     * 获取内场秀模块背景视频
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public String getInnerShowBackgroundVideo(String moduleId) {
        return PreferenceUtils.getString(context, "inner_show_" + moduleId + "_background_video", null);
    }

    /**
     * 设置内场秀模块背景视频
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowBackgroundVideo(String moduleId, String videoPath) {
        PreferenceUtils.putString(context, "inner_show_" + moduleId + "_background_video", videoPath);
    }

    /**
     * 获取内场秀模块背景音乐
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public String getInnerShowBackgroundMusic(String moduleId) {
        return PreferenceUtils.getString(context, "inner_show_" + moduleId + "_background_music", null);
    }

    /**
     * 设置内场秀模块背景音乐
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowBackgroundMusic(String moduleId, String musicPath) {
        PreferenceUtils.putString(context, "inner_show_" + moduleId + "_background_music", musicPath);
    }

    /**
     * 获取内场秀模块贴纸ID
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public String getInnerShowSticker(String moduleId) {
        return PreferenceUtils.getString(context, "inner_show_" + moduleId + "_sticker", null);
    }

    /**
     * 设置内场秀模块贴纸ID
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowSticker(String moduleId, String stickerId) {
        PreferenceUtils.putString(context, "inner_show_" + moduleId + "_sticker", stickerId);
    }

    /**
     * 获取内场秀模块贴纸X坐标
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public int getInnerShowStickerX(String moduleId) {
        return PreferenceUtils.getInt(context, "inner_show_" + moduleId + "_sticker_x", 0);
    }

    /**
     * 设置内场秀模块贴纸X坐标
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowStickerX(String moduleId, int x) {
        PreferenceUtils.putInt(context, "inner_show_" + moduleId + "_sticker_x", x);
    }

    /**
     * 获取内场秀模块贴纸Y坐标
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public int getInnerShowStickerY(String moduleId) {
        return PreferenceUtils.getInt(context, "inner_show_" + moduleId + "_sticker_y", 0);
    }

    /**
     * 设置内场秀模块贴纸Y坐标
     * @param moduleId 模块ID: warmup, hosting, tea_break
     */
    public void setInnerShowStickerY(String moduleId, int y) {
        PreferenceUtils.putInt(context, "inner_show_" + moduleId + "_sticker_y", y);
    }

    /**
     * 获取内场秀Excel导入路径
     * @return Excel文件路径
     */
    public String getInnerShowExcelPath() {
        return PreferenceUtils.getString(context, "inner_show_excel_path", null);
    }

    /**
     * 设置内场秀Excel导入路径
     * @param excelPath Excel文件路径
     */
    public void setInnerShowExcelPath(String excelPath) {
        PreferenceUtils.putString(context, "inner_show_excel_path", excelPath);
    }

    // ==================== 敏感配置管理 ====================

    /**
     * 设置管理员密码
     */
    public void setAdminPassword(String password) {
        PreferenceUtils.putString(context, "admin_password", password);
    }

    /**
     * 获取大模型API_KEY
     * 默认值：REDACTED_LLM_API_KEY
     */
    public String getLlmApiKey() {
        // 优先从解密配置中获取
        String apiKey = getDecryptedApiKey("llm", "api_key");
        if (apiKey != null) {
            return apiKey;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "llm_api_key", "REDACTED_LLM_API_KEY");
    }

    /**
     * 设置大模型API_KEY
     */
    public void setLlmApiKey(String apiKey) {
        PreferenceUtils.putString(context, "llm_api_key", apiKey);
    }

    /**
     * 获取大模型模型ID
     * 默认值：doubao-seedream-4-5-251128
     */
    public String getLlmModelId() {
        // 优先从解密配置中获取
        String modelId = getDecryptedApiKey("llm", "model_id");
        if (modelId != null) {
            return modelId;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "llm_model_id", "doubao-seedream-4-5-251128");
    }

    /**
     * 设置大模型模型ID
     */
    public void setLlmModelId(String modelId) {
        PreferenceUtils.putString(context, "llm_model_id", modelId);
    }

    /**
     * 获取TTS LicenseID
     */
    public String getTtsLicenseId() {
        // 优先从解密配置中获取
        String licenseId = getDecryptedApiKey("tencent_tts", "secret_id");
        if (licenseId != null) {
            return licenseId;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "tts_license_id", "");
    }

    /**
     * 设置TTS LicenseID
     */
    public void setTtsLicenseId(String licenseId) {
        PreferenceUtils.putString(context, "tts_license_id", licenseId);
    }

    /**
     * 获取TTS LicenseKey
     */
    public String getTtsLicenseKey() {
        // 优先从解密配置中获取
        String licenseKey = getDecryptedApiKey("tencent_tts", "secret_key");
        if (licenseKey != null) {
            return licenseKey;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "tts_license_key", "");
    }

    /**
     * 设置TTS LicenseKey
     */
    public void setTtsLicenseKey(String licenseKey) {
        PreferenceUtils.putString(context, "tts_license_key", licenseKey);
    }

    /**
     * 获取TTS LicensePk
     */
    public String getTtsLicensePk() {
        // 优先从解密配置中获取
        String licensePk = getDecryptedApiKey("tencent_tts", "license_pk");
        if (licensePk != null) {
            return licensePk;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "tts_license_pk", "");
    }

    /**
     * 设置TTS LicensePk
     */
    public void setTtsLicensePk(String licensePk) {
        PreferenceUtils.putString(context, "tts_license_pk", licensePk);
    }

    /**
     * 获取ASR LicenseID
     */
    public String getAsrLicenseId() {
        // 优先从解密配置中获取
        String licenseId = getDecryptedApiKey("tencent_asr", "secret_id");
        if (licenseId != null) {
            return licenseId;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "asr_license_id", "");
    }

    /**
     * 设置ASR LicenseID
     */
    public void setAsrLicenseId(String licenseId) {
        PreferenceUtils.putString(context, "asr_license_id", licenseId);
    }

    /**
     * 获取ASR LicenseKey
     */
    public String getAsrLicenseKey() {
        // 优先从解密配置中获取
        String licenseKey = getDecryptedApiKey("tencent_asr", "secret_key");
        if (licenseKey != null) {
            return licenseKey;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "asr_license_key", "");
    }

    /**
     * 设置ASR LicenseKey
     */
    public void setAsrLicenseKey(String licenseKey) {
        PreferenceUtils.putString(context, "asr_license_key", licenseKey);
    }

    /**
     * 获取TTS License (完整license字符串)
     */
    public String getTtsLicense() {
        // 优先从解密配置中获取
        String license = getDecryptedApiKey("tencent_tts", "license");
        if (license != null) {
            return license;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "tts_license", "");
    }

    /**
     * 设置TTS License
     */
    public void setTtsLicense(String license) {
        PreferenceUtils.putString(context, "tts_license", license);
    }

    /**
     * 获取管理员密码
     */
    public String getAdminPassword() {
        // 优先从解密配置中获取
        String password = getDecryptedApiKey("admin", "password");
        if (password != null) {
            return password;
        }
        // 向后兼容：从 SharedPreferences 读取
        return PreferenceUtils.getString(context, "admin_password", "123456");
    }

    /**
     * 获取ASR LicensePk
     */
    public String getAsrLicensePk() {
        return PreferenceUtils.getString(context, "asr_license_pk", "");
    }

    /**
     * 设置ASR LicensePk
     */
    public void setAsrLicensePk(String licensePk) {
        PreferenceUtils.putString(context, "asr_license_pk", licensePk);
    }

    // ==================== 默认抽奖程序配置 ====================

    /**
     * 获取默认抽奖程序ID
     * @return 程序ID，null表示显示选择页面
     */
    public String getDefaultLotteryProgram() {
        return PreferenceUtils.getString(context, "default_lottery_program", null);
    }

    /**
     * 设置默认抽奖程序ID
     * @param programId 程序ID（如"lottery_3d"），null表示显示选择页面
     */
    public void setDefaultLotteryProgram(String programId) {
        if (programId == null) {
            PreferenceUtils.remove(context, "default_lottery_program");
        } else {
            PreferenceUtils.putString(context, "default_lottery_program", programId);
        }
    }

    /**
     * 获取默认抽奖程序名称
     * @return 程序名称，如果未设置则返回null
     */
    public String getDefaultLotteryProgramName() {
        String programId = getDefaultLotteryProgram();
        if (programId == null) {
            return null;
        }

        // 根据programId返回程序名称
        switch (programId) {
            case "lottery_3d":
                return "3D球体抽奖";
            case "jlot10001":
                return "旋转球";
            case "jlot10002":
                return "网格抽奖";
            case "jlot10003":
                return "随机抽取";
            default:
                return programId;
        }
    }

    // ==================== MiniMax TTS配置 ====================

    /**
     * 获取TTS引擎类型
     * @return "tencent" 或 "minimax"
     * 默认使用MiniMax（如果配置了MiniMax）
     */
    public String getTTSEngine() {
        String engine = PreferenceUtils.getString(context, "tts_engine", null);
        if (TextUtils.isEmpty(engine)) {
            // 如果未设置过，检查MiniMax是否可用
            String apiKey = getMiniMaxApiKey();
            String groupId = getMiniMaxGroupId();
            if (!TextUtils.isEmpty(apiKey) && !TextUtils.isEmpty(groupId)) {
                return "minimax";
            }
            return "tencent";
        }
        return engine;
    }

    /**
     * 设置TTS引擎类型
     * @param engine "tencent" 或 "minimax"
     */
    public void setTTSEngine(String engine) {
        PreferenceUtils.putString(context, "tts_engine", engine);
    }

    /**
     * 获取MiniMax API Key
     * 优先从assets加载，然后解密配置，最后SharedPreferences
     */
    public String getMiniMaxApiKey() {
        // 优先从assets加载（如果有新文件）
        String apiKey = com.jcoding.aiactivity.utils.ApiKeyLoader.loadMiniMaxApiKey(context);
        if (!TextUtils.isEmpty(apiKey)) {
            // 缓存到SharedPreferences
            PreferenceUtils.putString(context, "minimax_api_key", apiKey);
            return apiKey;
        }

        // 从解密配置中获取
        apiKey = getDecryptedApiKey("minimax", "api_key");
        if (apiKey != null) {
            return apiKey;
        }

        // 向后兼容：从 SharedPreferences 读取
        apiKey = PreferenceUtils.getString(context, "minimax_api_key", null);
        return apiKey != null ? apiKey : "";
    }

    /**
     * 设置MiniMax API Key
     */
    public void setMiniMaxApiKey(String apiKey) {
        PreferenceUtils.putString(context, "minimax_api_key", apiKey);
    }

    /**
     * 获取MiniMax Group ID
     * 优先从assets加载，然后解密配置，最后SharedPreferences
     */
    public String getMiniMaxGroupId() {
        // 优先从assets加载（如果有新文件）
        String groupId = com.jcoding.aiactivity.utils.ApiKeyLoader.loadMiniMaxGroupId(context);
        if (!TextUtils.isEmpty(groupId)) {
            // 缓存到SharedPreferences
            PreferenceUtils.putString(context, "minimax_group_id", groupId);
            return groupId;
        }

        // 从解密配置中获取
        groupId = getDecryptedApiKey("minimax", "group_id");
        if (groupId != null) {
            return groupId;
        }

        // 向后兼容：从 SharedPreferences 读取
        groupId = PreferenceUtils.getString(context, "minimax_group_id", null);
        return groupId != null ? groupId : "";
    }

    /**
     * 设置MiniMax Group ID
     */
    public void setMiniMaxGroupId(String groupId) {
        PreferenceUtils.putString(context, "minimax_group_id", groupId);
    }

    /**
     * 获取MiniMax发音人ID
     */
    public String getMiniMaxVoiceId() {
        return PreferenceUtils.getString(context, "minimax_voice_id", "Chinese (Mandarin)_Reliable_Executive");
    }

    /**
     * 设置MiniMax发音人ID
     */
    public void setMiniMaxVoiceId(String voiceId) {
        PreferenceUtils.putString(context, "minimax_voice_id", voiceId);
    }

    /**
     * 获取MiniMax语速
     * @return 语速值，默认1.0
     */
    public float getMiniMaxSpeed() {
        return PreferenceUtils.getFloat(context, "minimax_speed", 1.0f);
    }

    /**
     * 设置MiniMax语速
     * @param speed 语速值，范围0.5-2.0
     */
    public void setMiniMaxSpeed(float speed) {
        PreferenceUtils.putFloat(context, "minimax_speed", speed);
    }

    /**
     * 获取MiniMax音量
     * @return 音量值，默认1.0
     */
    public float getMiniMaxVolume() {
        return PreferenceUtils.getFloat(context, "minimax_volume", 1.0f);
    }

    /**
     * 设置MiniMax音量
     * @param volume 音量值，范围0.0-1.0
     */
    public void setMiniMaxVolume(float volume) {
        PreferenceUtils.putFloat(context, "minimax_volume", volume);
    }

    // ==================== Quiz模块数字人配置 ====================

    /**
     * 获取Quiz模块的数字人缩放比例
     * @return 缩放比例，默认3.0
     */
    public float getQuizDigitalHumanScale() {
        Float scale = PreferenceUtils.getFloat(context, "quiz_digital_human_scale", null);
        return scale != null ? scale : 3.0f;
    }

    /**
     * 设置Quiz模块的数字人缩放比例
     * @param scale 缩放比例
     */
    public void setQuizDigitalHumanScale(float scale) {
        PreferenceUtils.putFloat(context, "quiz_digital_human_scale", scale);
    }

    /**
     * 获取Quiz模块的数字人X位置（百分比）
     * @return X位置百分比，默认85
     */
    public int getQuizDigitalHumanPositionX() {
        Integer posX = PreferenceUtils.getInt(context, "quiz_digital_human_position_x", null);
        return posX != null ? posX : 85;
    }

    /**
     * 设置Quiz模块的数字人X位置（百分比）
     * @param posX X位置百分比（0-100）
     */
    public void setQuizDigitalHumanPositionX(int posX) {
        PreferenceUtils.putInt(context, "quiz_digital_human_position_x", posX);
    }

    /**
     * 获取Quiz模块的数字人Y位置（百分比）
     * @return Y位置百分比，默认85
     */
    public int getQuizDigitalHumanPositionY() {
        Integer posY = PreferenceUtils.getInt(context, "quiz_digital_human_position_y", null);
        return posY != null ? posY : 85;
    }

    /**
     * 设置Quiz模块的数字人Y位置（百分比）
     * @param posY Y位置百分比（0-100）
     */
    public void setQuizDigitalHumanPositionY(int posY) {
        PreferenceUtils.putInt(context, "quiz_digital_human_position_y", posY);
    }

    // ==================== AiShow模块数字人配置 ====================

    /**
     * 获取AiShow模块的数字人缩放比例
     * @return 缩放比例，默认1.5
     */
    public float getAiShowDigitalHumanScale() {
        Float scale = PreferenceUtils.getFloat(context, "aishow_digital_human_scale", null);
        return scale != null ? scale : 1.5f;
    }

    /**
     * 设置AiShow模块的数字人缩放比例
     * @param scale 缩放比例
     */
    public void setAiShowDigitalHumanScale(float scale) {
        PreferenceUtils.putFloat(context, "aishow_digital_human_scale", scale);
    }

    /**
     * 获取AiShow模块的数字人X位置（百分比）
     * @return X位置百分比，默认85（右侧）
     */
    public int getAiShowDigitalHumanPositionX() {
        Integer posX = PreferenceUtils.getInt(context, "aishow_digital_human_position_x", null);
        return posX != null ? posX : 85;
    }

    /**
     * 设置AiShow模块的数字人X位置（百分比）
     * @param posX X位置百分比（0-100）
     */
    public void setAiShowDigitalHumanPositionX(int posX) {
        PreferenceUtils.putInt(context, "aishow_digital_human_position_x", posX);
    }

    /**
     * 获取AiShow模块的数字人Y位置（百分比）
     * @return Y位置百分比，默认75（下方）
     */
    public int getAiShowDigitalHumanPositionY() {
        Integer posY = PreferenceUtils.getInt(context, "aishow_digital_human_position_y", null);
        return posY != null ? posY : 75;
    }

    /**
     * 设置AiShow模块的数字人Y位置（百分比）
     * @param posY Y位置百分比（0-100）
     */
    public void setAiShowDigitalHumanPositionY(int posY) {
        PreferenceUtils.putInt(context, "aishow_digital_human_position_y", posY);
    }

    /**
     * 获取生成质量（720p/1080p/2k/4k）
     * @return 质量设置，默认4k
     */
    public String getGenerationQuality() {
        String quality = PreferenceUtils.getString(context, "generation_quality", null);
        return quality != null ? quality : "4k";
    }

    /**
     * 设置生成质量
     * @param quality 质量设置（720p/1080p/2k/4k）
     */
    public void setGenerationQuality(String quality) {
        PreferenceUtils.putString(context, "generation_quality", quality);
    }

    // ==================== 存储策略相关 ====================

    /**
     * 存储策略类型
     */
    public static final class StorageStrategy {
        public static final String TOS = "tos";      // 火山引擎TOS
        public static final String OSS = "oss";      // 阿里云OSS
    }

    /**
     * 获取当前存储策略
     * @return 存储策略（tos或oss），默认tos
     */
    public String getStorageStrategy() {
        String strategy = PreferenceUtils.getString(context, "storage_strategy", null);
        // 默认使用TOS
        return strategy != null ? strategy : StorageStrategy.TOS;
    }

    /**
     * 设置存储策略
     * @param strategy 存储策略（tos或oss）
     */
    public void setStorageStrategy(String strategy) {
        if (StorageStrategy.TOS.equals(strategy) || StorageStrategy.OSS.equals(strategy)) {
            PreferenceUtils.putString(context, "storage_strategy", strategy);
            android.util.Log.i("ConfigManager", "Storage strategy set to: " + strategy);
        } else {
            android.util.Log.e("ConfigManager", "Invalid storage strategy: " + strategy);
        }
    }

    /**
     * 获取存储自定义域名
     * @param strategy 存储策略（tos或oss）
     * @return 自定义域名URL
     */
    public String getStorageDomain(String strategy) {
        // 从配置读取，如果未设置则返回默认值
        if (StorageStrategy.TOS.equals(strategy)) {
            String domain = PreferenceUtils.getString(context, "tos_custom_domain", null);
            return domain != null ? domain : "https://ykb.jcoding.chat";
        } else if (StorageStrategy.OSS.equals(strategy)) {
            String domain = PreferenceUtils.getString(context, "oss_custom_domain", null);
            return domain != null ? domain : "https://file.jcoding.chat";
        }
        return "https://ykb.jcoding.chat"; // 默认TOS
    }

    /**
     * 获取当前使用的存储域名
     * @return 当前存储策略的自定义域名
     */
    public String getCurrentStorageDomain() {
        return getStorageDomain(getStorageStrategy());
    }

    /**
     * 设置TOS自定义域名
     * @param domain TOS自定义域名
     */
    public void setTosCustomDomain(String domain) {
        PreferenceUtils.putString(context, "tos_custom_domain", domain);
        android.util.Log.i("ConfigManager", "TOS自定义域名已设置: " + domain);
    }

    /**
     * 获取TOS自定义域名
     * @return TOS自定义域名
     */
    public String getTosCustomDomain() {
        return PreferenceUtils.getString(context, "tos_custom_domain", "https://ykb.jcoding.chat");
    }

    /**
     * 设置OSS自定义域名
     * @param domain OSS自定义域名
     */
    public void setOssCustomDomain(String domain) {
        PreferenceUtils.putString(context, "oss_custom_domain", domain);
        android.util.Log.i("ConfigManager", "OSS自定义域名已设置: " + domain);
    }

    /**
     * 获取OSS自定义域名
     * @return OSS自定义域名
     */
    public String getOssCustomDomain() {
        return PreferenceUtils.getString(context, "oss_custom_domain", "https://file.jcoding.chat");
    }

    /**
     * 获取TOS配置信息
     * @return TOS配置JSON对象
     */
    public JsonObject getTosConfig() {
        JsonObject config = new JsonObject();
        config.addProperty("access_key_id", "REDACTED_TOS_ACCESS_KEY");
        config.addProperty("secret_access_key", "REDACTED_TOS_SECRET_KEY");
        config.addProperty("region", "cn-shanghai");
        config.addProperty("endpoint", "tos-cn-shanghai.volces.com");
        config.addProperty("bucket", "ykb-image-store");
        config.addProperty("custom_domain", getTosCustomDomain());
        return config;
    }

    /**
     * 获取OSS配置信息
     * @return OSS配置JSON对象
     */
    public JsonObject getOssConfig() {
        JsonObject config = new JsonObject();
        config.addProperty("access_key_id", "REDACTED_ALIYUN_ACCESS_KEY");
        config.addProperty("secret_access_key", "REDACTED_ALIYUN_SECRET_KEY");
        config.addProperty("region", "cn-shanghai");
        config.addProperty("endpoint", "oss-cn-shanghai.aliyuncs.com");
        config.addProperty("bucket", "jc-st");
        config.addProperty("custom_domain", getOssCustomDomain());
        return config;
    }
}
