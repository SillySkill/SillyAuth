package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.text.TextUtils;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

/**
 * 数字人管理器
 * 负责数字人动作展示和语音播报
 */
public class DigitalHumanManager {

    private static final String TAG = "DigitalHumanManager";

    private static DigitalHumanManager instance;
    private Context context;
    private ConfigManager configManager;
    private VoiceManager voiceManager;
    private Gson gson;

    // 数字人配置
    private String projectId = "JC2026012100001";
    private String defaultOperate = "10.gif";
    private String humanName = "方小松";
    private JsonObject aibeingConfig;

    private DigitalHumanManager(Context context) {
        this.context = context.getApplicationContext();
        this.configManager = ConfigManager.getInstance(context);
        this.voiceManager = VoiceManager.getInstance(context);
        this.gson = new Gson();
        loadConfig();
    }

    public static synchronized DigitalHumanManager getInstance(Context context) {
        if (instance == null) {
            instance = new DigitalHumanManager(context);
        }
        return instance;
    }

    /**
     * 加载配置
     */
    private void loadConfig() {
        try {
            String configStr = readAssetFile("aibeing/config.json");
            if (!TextUtils.isEmpty(configStr)) {
                aibeingConfig = gson.fromJson(configStr, JsonObject.class);
                if (aibeingConfig != null && aibeingConfig.has("Aibeing")) {
                    JsonObject aibeing = aibeingConfig.getAsJsonObject("Aibeing");
                    if (aibeing.has("project")) {
                        JsonObject project = aibeing.getAsJsonObject("project");
                        if (project.has(projectId)) {
                            JsonObject projectData = project.getAsJsonObject(projectId);
                            defaultOperate = projectData.get("default_operate").getAsString();
                            humanName = projectData.get("name").getAsString();
                        }
                    }
                }
            }

            Log.i(TAG, "Digital human config loaded: " + humanName);
        } catch (Exception e) {
            Log.e(TAG, "Failed to load config", e);
        }
    }

    /**
     * 读取assets文件
     */
    private String readAssetFile(String filePath) {
        try {
            InputStream is = context.getAssets().open(filePath);
            int size = is.available();
            byte[] buffer = new byte[size];
            is.read(buffer);
            is.close();
            return new String(buffer, StandardCharsets.UTF_8);
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 获取动作GIF路径
     */
    public String getActionGif(String actionType) {
        if (aibeingConfig == null) {
            return defaultOperate;
        }

        try {
            JsonObject aibeing = aibeingConfig.getAsJsonObject("Aibeing");
            JsonObject project = aibeing.getAsJsonObject("project");
            JsonObject projectData = project.getAsJsonObject(projectId);
            JsonObject operate = projectData.getAsJsonObject("operate");

            if (operate.has(actionType)) {
                return operate.get(actionType).getAsString();
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to get action gif", e);
        }

        return defaultOperate;
    }

    /**
     * 获取默认动作GIF路径
     */
    public String getDefaultGif() {
        return defaultOperate;
    }

    /**
     * 获取数字人名称
     */
    public String getHumanName() {
        return humanName;
    }

    /**
     * 执行动作并播报
     */
    public void performActionAndSpeak(String actionType, String text,
                                       DigitalHumanCallback callback) {
        // 从ConfigManager检查是否启用
        if (!configManager.isDigitalHumanEnabled()) {
            Log.d(TAG, "数字人全局未启用");
            if (callback != null) {
                callback.onComplete();
            }
            return;
        }

        // 获取动作GIF
        String gifPath = getActionGif(actionType);

        // 播报语音
        if (!TextUtils.isEmpty(text)) {
            voiceManager.speakText(text, new VoiceManager.VoiceSynthesisCallback() {
                @Override
                public void onSpeakStart() {
                    if (callback != null) {
                        callback.onSpeakStart(gifPath);
                    }
                }

                @Override
                public void onSpeakPaused() {
                }

                @Override
                public void onSpeakResumed() {
                }

                @Override
                public void onSpeakComplete() {
                    if (callback != null) {
                        callback.onComplete();
                    }
                }

                @Override
                public void onError(String error) {
                    Log.e(TAG, "Speak error: " + error);
                    if (callback != null) {
                        callback.onError(error);
                    }
                }
            });
        } else {
            if (callback != null) {
                callback.onSpeakStart(gifPath);
                callback.onComplete();
            }
        }
    }

    /**
     * 仅播报语音
     */
    public void speak(String text, DigitalHumanCallback callback) {
        performActionAndSpeak(null, text, callback);
    }

    /**
     * 仅执行动作
     */
    public void performAction(String actionType, DigitalHumanCallback callback) {
        performActionAndSpeak(actionType, null, callback);
    }

    // ========== 预定义动作方法 ==========

    /**
     * 欢迎手势
     */
    public void welcome(DigitalHumanCallback callback) {
        performActionAndSpeak(Constants.AIBEING_ACTION_OPEN_HAND,
                "欢迎来到AI活动秀", callback);
    }

    /**
     * 打招呼
     */
    public void sayHello(String userName, DigitalHumanCallback callback) {
        String text = "你好" + (TextUtils.isEmpty(userName) ? "" : "，" + userName);
        performActionAndSpeak(Constants.AIBEING_ACTION_SAY_HELLO, text, callback);
    }

    /**
     * 鼓掌祝贺
     */
    public void applaud(String winnerName, DigitalHumanCallback callback) {
        String text = "恭喜" + winnerName + "中奖！";
        performActionAndSpeak(Constants.AIBEING_ACTION_APPLAUD, text, callback);
    }

    /**
     * 敬礼
     */
    public void salute(DigitalHumanCallback callback) {
        performActionAndSpeak(Constants.AIBEING_ACTION_SALUTE, "谢谢参与", callback);
    }

    /**
     * 祝贺
     */
    public void congratulate(String message, DigitalHumanCallback callback) {
        performActionAndSpeak(Constants.AIBEING_ACTION_CONGRATULATE, message, callback);
    }

    /**
     * 祝贺中奖者
     */
    public void congratulate(String winnerName, String prizeName, DigitalHumanCallback callback) {
        String message = "恭喜" + winnerName + "获得" + prizeName + "！";
        performActionAndSpeak(Constants.AIBEING_ACTION_CONGRATULATE, message, callback);
    }

    /**
     * 左手指引
     */
    public void leftPoint(String direction, DigitalHumanCallback callback) {
        String text = "请往" + direction + "走";
        performActionAndSpeak(Constants.AIBEING_ACTION_LEFT_POINT, text, callback);
    }

    /**
     * 自我介绍
     */
    public void introduce(DigitalHumanCallback callback) {
        String text = "我是" + humanName + "，很高兴为您服务";
        performActionAndSpeak(Constants.AIBEING_ACTION_INTRODUCE, text, callback);
    }

    /**
     * 播报题目
     */
    public void announceQuestion(String question, String[] options,
                                  DigitalHumanCallback callback) {
        StringBuilder text = new StringBuilder(question);
        if (options != null && options.length > 0) {
            for (int i = 0; i < options.length; i++) {
                char label = (char) ('A' + i);
                text.append("。").append(label).append("选项，").append(options[i]);
            }
        }
        performActionAndSpeak(null, text.toString(), callback);
    }

    /**
     * 播报中奖结果
     */
    public void announceWinner(String winnerName, String prizeName,
                                DigitalHumanCallback callback) {
        String text = "恭喜" + winnerName + "获得" + prizeName;
        performActionAndSpeak(Constants.AIBEING_ACTION_CONGRATULATE, text, callback);
    }

    /**
     * 设置全局启用状态
     */
    public void setEnabled(boolean enabled) {
        configManager.setDigitalHumanEnabled(enabled);
    }

    /**
     * 是否全局启用
     */
    public boolean isEnabled() {
        return configManager.isDigitalHumanEnabled();
    }

    /**
     * 检查指定模块是否启用数字人
     */
    public boolean isEnabledForModule(String module) {
        return configManager.isDigitalHumanEnabledForModule(module);
    }

    /**
     * 数字人回调接口
     */
    public interface DigitalHumanCallback {
        /**
         * 开始说话（返回GIF路径）
         */
        void onSpeakStart(String gifPath);

        /**
         * 完成
         */
        void onComplete();

        /**
         * 错误
         */
        void onError(String error);
    }

    /**
     * 停止数字人展示和语音播报
     */
    public void stop() {
        if (voiceManager != null) {
            voiceManager.stop();
        }
        // 停止GIF动画等其他清理工作
    }

    /**
     * 动作常量
     */
    public static class Constants {
        public static final String AIBEING_ACTION_OPEN_HAND = "open_hand";
        public static final String AIBEING_ACTION_SAY_HELLO = "say_hello";
        public static final String AIBEING_ACTION_APPLAUD = "applaud";
        public static final String AIBEING_ACTION_SALUTE = "salute";
        public static final String AIBEING_ACTION_INTRODUCE = "introduce";
        public static final String AIBEING_ACTION_CONGRATULATE = "congratulate";
        public static final String AIBEING_ACTION_LEFT_POINT = "left_point";
    }
}
