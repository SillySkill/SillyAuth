package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.text.TextUtils;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.jcoding.aiactivity.utils.PreferenceUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * 答题奖品配置管理器
 * 管理答题奖励规则、奖品推送配置
 */
public class QuizPrizeConfigManager {

    private static final String PREF_PRIZE_ENABLED = "quiz_prize_enabled";
    private static final String PREF_REQUIRE_LOGIN = "quiz_require_login";
    private static final String PREF_PUSH_TO_INNER = "quiz_push_to_inner";
    private static final String PREF_PRIZE_THRESHOLD = "quiz_prize_threshold";

    private static QuizPrizeConfigManager instance;
    private Context context;
    private Gson gson;

    private QuizPrizeConfigManager(Context context) {
        this.context = context.getApplicationContext();
        this.gson = new Gson();
    }

    public static synchronized QuizPrizeConfigManager getInstance(Context context) {
        if (instance == null) {
            instance = new QuizPrizeConfigManager(context);
        }
        return instance;
    }

    /**
     * 奖品规则实体
     */
    public static class PrizeRule {
        public String id;           // 奖品ID
        public int minCorrect;      // 最小答对数量
        public String name;         // 奖品名称
        public String description;  // 奖品描述
        public String imageUrl;     // 奖品图片URL
        public String level;        // 奖品等级

        public PrizeRule() {
        }

        public PrizeRule(String id, int minCorrect, String name, String description, String imageUrl, String level) {
            this.id = id;
            this.minCorrect = minCorrect;
            this.name = name;
            this.description = description;
            this.imageUrl = imageUrl;
            this.level = level;
        }
    }

    /**
     * 奖品配置
     */
    public static class PrizeConfig {
        public boolean enabled;           // 是否启用奖品
        public boolean requireLogin;      // 是否需要登录
        public boolean pushToInner;       // 是否推送到内场
        public List<PrizeRule> rewardRules; // 奖励规则列表

        public PrizeConfig() {
            this.enabled = true;
            this.requireLogin = false;
            this.pushToInner = false;
            this.rewardRules = new ArrayList<>();
        }
    }

    /**
     * 加载奖品配置（简化版）
     */
    public PrizeConfig loadPrizeConfig() {
        PrizeConfig config = new PrizeConfig();

        try {
            // 从ConfigManager读取question配置
            ConfigManager configManager = ConfigManager.getInstance(context);
            JsonObject questionConfig = configManager.getQuestionConfig();

            if (questionConfig != null && questionConfig.has("prizes")) {
                JsonObject prizesObj = questionConfig.getAsJsonObject("prizes");

                // 读取基础配置
                config.enabled = prizesObj.has("enabled") && prizesObj.get("enabled").getAsBoolean();

                // 读取默认门槛和奖品图片
                int defaultThreshold = prizesObj.has("default_threshold") ? prizesObj.get("default_threshold").getAsInt() : 3;
                // 默认奖品图片路径：使用question目录下的prize.jpg
                String imageConfig = prizesObj.has("default_prize_image") ? prizesObj.get("default_prize_image").getAsString() : "question/prize.jpg";
                // 构建完整的assets路径
                String defaultImage;
                if (imageConfig.startsWith("file:///")) {
                    defaultImage = imageConfig;
                } else if (imageConfig.contains("/")) {
                    // 已包含路径，如 "question/prize.png"
                    defaultImage = "file:///android_asset/" + imageConfig;
                } else {
                    // 只有文件名，默认放在 question 目录
                    defaultImage = "file:///android_asset/question/" + imageConfig;
                }

                // 创建默认奖品规则
                PrizeRule defaultRule = new PrizeRule();
                defaultRule.id = "default_prize";
                defaultRule.minCorrect = defaultThreshold;
                defaultRule.name = "精美礼品";
                defaultRule.description = "恭喜您达到答题门槛！";
                defaultRule.imageUrl = defaultImage;
                defaultRule.level = "奖品";

                config.rewardRules.add(defaultRule);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return config;
    }

    /**
     * 根据答对数量获取奖品
     */
    public PrizeRule getPrizeByCorrectCount(int correctCount) {
        PrizeConfig config = loadPrizeConfig();

        if (!config.enabled || config.rewardRules.isEmpty()) {
            return null;
        }

        // 找到满足条件的最小答对数的奖品（按minCorrect降序排列）
        PrizeRule bestPrize = null;
        for (PrizeRule rule : config.rewardRules) {
            if (correctCount >= rule.minCorrect) {
                if (bestPrize == null || rule.minCorrect > bestPrize.minCorrect) {
                    bestPrize = rule;
                }
            }
        }

        return bestPrize;
    }

    // ========== 配置保存和读取 ==========

    /**
     * 是否启用奖品功能
     */
    public boolean isPrizeEnabled() {
        return PreferenceUtils.getBoolean(context, PREF_PRIZE_ENABLED, true);
    }

    /**
     * 设置启用奖品功能
     */
    public void setPrizeEnabled(boolean enabled) {
        PreferenceUtils.putBoolean(context, PREF_PRIZE_ENABLED, enabled);
    }

    /**
     * 是否需要登录才能答题
     */
    public boolean isRequireLogin() {
        return PreferenceUtils.getBoolean(context, PREF_REQUIRE_LOGIN, false);
    }

    /**
     * 设置是否需要登录
     */
    public void setRequireLogin(boolean requireLogin) {
        PreferenceUtils.putBoolean(context, PREF_REQUIRE_LOGIN, requireLogin);
    }

    /**
     * 是否推送到内场设备
     */
    public boolean isPushToInner() {
        return PreferenceUtils.getBoolean(context, PREF_PUSH_TO_INNER, false);
    }

    /**
     * 设置是否推送到内场设备
     */
    public void setPushToInner(boolean pushToInner) {
        PreferenceUtils.putBoolean(context, PREF_PUSH_TO_INNER, pushToInner);
    }

    /**
     * 获取答对题数阈值（用于判断是否有奖品）
     */
    public int getCorrectAnswerThreshold() {
        PrizeConfig config = loadPrizeConfig();
        if (config.enabled && !config.rewardRules.isEmpty()) {
            // 返回最小的minCorrect值
            int minThreshold = Integer.MAX_VALUE;
            for (PrizeRule rule : config.rewardRules) {
                if (rule.minCorrect < minThreshold) {
                    minThreshold = rule.minCorrect;
                }
            }
            return minThreshold == Integer.MAX_VALUE ? 0 : minThreshold;
        }
        return 0;
    }

    /**
     * 根据答对题数获取奖品图片URL
     */
    public String getPrizeImageUrl(int correctCount) {
        PrizeRule prize = getPrizeByCorrectCount(correctCount);
        return prize != null ? prize.imageUrl : null;
    }

    /**
     * 获取用户设置的奖品门槛（优先使用SharedPreferences中的值）
     */
    public int getPrizeThreshold() {
        // 如果用户设置了门槛，使用用户设置的值
        int userThreshold = PreferenceUtils.getInt(context, PREF_PRIZE_THRESHOLD, -1);
        if (userThreshold > 0) {
            return userThreshold;
        }
        // 否则从JSON配置中读取
        return getCorrectAnswerThreshold();
    }

    /**
     * 设置奖品门槛
     */
    public void setPrizeThreshold(int threshold) {
        PreferenceUtils.putInt(context, PREF_PRIZE_THRESHOLD, threshold);
    }

    /**
     * 重置奖品门槛为JSON配置中的值
     */
    public void resetPrizeThreshold() {
        PreferenceUtils.putInt(context, PREF_PRIZE_THRESHOLD, -1);
    }
}
