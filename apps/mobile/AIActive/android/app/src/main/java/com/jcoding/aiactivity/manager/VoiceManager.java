package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.text.TextUtils;
import android.util.Log;

import com.jcoding.aiactivity.utils.ApiKeyLoader;
import com.jcoding.aiactivity.utils.PreferenceUtils;

/**
 * 语音功能管理器
 * 统一管理ASR和TTS功能，简化调用
 */
public class VoiceManager {

    private static final String TAG = "VoiceManager";
    private static final String PREF_TTS_ENABLED = "tts_enabled";
    private static final String PREF_ASR_ENABLED = "asr_enabled";

    private static VoiceManager instance;
    private Context context;
    private SpeechRecognizerManager recognizer;
    private SpeechSynthesizerManager synthesizer;
    private MiniMaxTTSManager miniMaxTTS;
    private ConfigManager configManager;
    private boolean isInitialized = false;
    private boolean configApplied = false;

    private VoiceManager(Context context) {
        this.context = context.getApplicationContext();
        this.recognizer = SpeechRecognizerManager.getInstance(context);
        this.synthesizer = SpeechSynthesizerManager.getInstance(context);
        this.miniMaxTTS = MiniMaxTTSManager.getInstance(context);
        this.configManager = ConfigManager.getInstance(context);
        initialize();
    }

    public static synchronized VoiceManager getInstance(Context context) {
        if (instance == null) {
            instance = new VoiceManager(context);
        }
        return instance;
    }

    /**
     * 初始化语音功能
     */
    private void initialize() {
        try {
            // 从ConfigManager读取腾讯云ASR/TTS密钥，如果为空则从assets加载
            String asrAppId = configManager.getAsrLicenseId();
            String asrSecretId = configManager.getAsrLicenseKey();
            String asrSecretKey = configManager.getAsrLicensePk();

            // 从ConfigManager读取腾讯云TTS凭证
            String ttsAppId = configManager.getTtsLicenseId();
            String ttsSecretId = configManager.getTtsLicenseKey();
            String ttsSecretKey = configManager.getTtsLicensePk();

            // 如果SharedPreferences为空，从assets加载
            if (TextUtils.isEmpty(ttsAppId) || TextUtils.isEmpty(ttsSecretId) || TextUtils.isEmpty(ttsSecretKey)) {
                ApiKeyLoader.TencentTTSCredentials credentials = ApiKeyLoader.loadTencentTTSCredentials(context);
                if (credentials != null) {
                    // 优先使用在线认证参数（如果有）
                    if (credentials.hasOnlineAuthParams()) {
                        ttsAppId = credentials.licKey;  // LicenseKey作为appId
                        ttsSecretId = credentials.secretId;
                        ttsSecretKey = credentials.secretKey;
                        Log.i(TAG, "Loaded TTS credentials (online auth) from assets");
                    }
                    // 离线认证参数不完整，使用默认值
                    else {
                        ttsAppId = credentials.licKey;
                        ttsSecretId = "";
                        ttsSecretKey = credentials.licPk2;
                        Log.w(TAG, "Loaded incomplete TTS credentials from assets (missing SecretId/Key or AuthSign)");
                    }
                }
            }

            // 检查是否配置了TTS
            boolean hasTtsConfig = !TextUtils.isEmpty(ttsAppId) && !TextUtils.isEmpty(ttsSecretKey);

            // 检查是否配置了ASR
            boolean hasAsrConfig = !TextUtils.isEmpty(asrAppId) && !TextUtils.isEmpty(asrSecretId) && !TextUtils.isEmpty(asrSecretKey);

            if (hasTtsConfig) {
                // 初始化TTS
                synthesizer.setConfig(ttsAppId, ttsSecretId, ttsSecretKey);
                Log.i(TAG, "TTS initialized");
            }

            if (hasAsrConfig) {
                // 初始化ASR
                recognizer.setConfig(asrAppId, asrSecretId, asrSecretKey);
                Log.i(TAG, "ASR initialized");
            }

            // 初始化MiniMax TTS
            String miniMaxApiKey = configManager.getMiniMaxApiKey();
            String miniMaxGroupId = configManager.getMiniMaxGroupId();
            boolean hasMiniMaxConfig = false;
            if (!TextUtils.isEmpty(miniMaxApiKey)) {
                // API Key存在，先尝试初始化（即使没有Group ID）
                if (!TextUtils.isEmpty(miniMaxGroupId)) {
                    miniMaxTTS.setConfig(miniMaxApiKey, miniMaxGroupId);
                    hasMiniMaxConfig = true;
                    Log.i(TAG, "MiniMax TTS initialized with GroupId");
                } else {
                    // API Key存在但Group ID为空，记录警告
                    Log.w(TAG, "MiniMax API Key found but Group ID is missing");
                }
            }

            // 如果TTS、ASR或MiniMax任一配置成功，则认为语音管理器已初始化
            if (hasTtsConfig || hasAsrConfig || hasMiniMaxConfig) {
                isInitialized = true;
                Log.i(TAG, "Voice manager initialized successfully");
            } else {
                Log.w(TAG, "No voice credentials configured");
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize voice manager", e);
        }
    }

    /**
     * 初始化配置（在应用启动时调用）
     */
    public void initConfig(String asrAppId, String asrSecretId, String asrSecretKey,
                           String ttsAppId, String ttsSecretId, String ttsSecretKey) {
        // 保存配置
        PreferenceUtils.putString(context, "tencent_asr_app_id", asrAppId);
        PreferenceUtils.putString(context, "tencent_secret_id", asrSecretId);
        PreferenceUtils.putString(context, "tencent_secret_key", asrSecretKey);

        // 初始化ASR
        recognizer.setConfig(asrAppId, asrSecretId, asrSecretKey);

        // 初始化TTS
        if (!TextUtils.isEmpty(ttsAppId)) {
            synthesizer.setConfig(ttsAppId, ttsSecretId, ttsSecretKey);
        } else {
            synthesizer.setConfig(asrAppId, asrSecretId, asrSecretKey);
        }

        isInitialized = true;
    }

    /**
     * 应用语音配置参数（从ConfigManager读取）
     */
    private void applyVoiceConfig() {
        if (configApplied) {
            return; // 只应用一次
        }

        try {
            // 应用TTS配置
            int voiceType = configManager.getTTSVoiceType();
            float speed = configManager.getTTSSpeed();
            float pitch = configManager.getTTSPitch();
            float volume = configManager.getTTSVolume();
            synthesizer.applyConfig(voiceType, speed, pitch, volume);

            // 应用ASR配置
            String engineModelType = configManager.getASREngineModelType();
            boolean filterDirty = configManager.isASRFilterDirty();
            boolean filterModal = configManager.isASRFilterModal();
            boolean convertNumMode = configManager.isASRConvertNumMode();
            recognizer.applyConfig(engineModelType, filterDirty, filterModal, convertNumMode);

            configApplied = true;
            Log.i(TAG, "Voice config applied");
        } catch (Exception e) {
            Log.e(TAG, "Failed to apply voice config", e);
        }
    }

    /**
     * 应用MiniMax TTS配置参数
     */
    private void applyMiniMaxConfig() {
        try {
            String voiceId = configManager.getMiniMaxVoiceId();
            // 使用通用的TTS配置（语速、音量）
            float speed = configManager.getTTSSpeed();
            float volume = configManager.getTTSVolume();
            miniMaxTTS.applyConfig(voiceId, speed, volume);
            Log.i(TAG, "MiniMax TTS config applied: voiceId=" + voiceId + ", speed=" + speed + ", volume=" + volume);
        } catch (Exception e) {
            Log.e(TAG, "Failed to apply MiniMax config", e);
        }
    }

    /**
     * 语音识别 - 开始监听
     */
    public void startVoiceRecognition(final VoiceRecognitionCallback callback) {
        if (!isInitialized) {
            if (callback != null) {
                callback.onError("语音功能未初始化");
            }
            return;
        }

        // 应用配置参数
        applyVoiceConfig();

        boolean success = recognizer.startListening(new SpeechRecognizerManager.RecognitionListener() {
            @Override
            public void onResult(String result, boolean isFinal) {
                if (callback != null) {
                    if (isFinal) {
                        callback.onRecognitionResult(result);
                    } else {
                        callback.onIntermediateResult(result);
                    }
                }
            }

            @Override
            public void onError(int errorCode, String errorMsg) {
                if (callback != null) {
                    callback.onError("识别失败: " + errorMsg);
                }
            }
        });

        if (!success) {
            callback.onError("启动语音识别失败");
        }
    }

    /**
     * 语音识别 - 停止监听
     */
    public void stopVoiceRecognition() {
        recognizer.stopListening();
    }

    /**
     * 语音合成 - 播放文本
     */
    public void speakText(String text, final VoiceSynthesisCallback callback) {
        Log.i(TAG, "speakText() called, text: " + text);

        if (TextUtils.isEmpty(text)) {
            if (callback != null) {
                callback.onError("文本为空");
            }
            return;
        }

        // 根据TTS引擎选择使用哪个TTS
        String ttsEngine = configManager.getTTSEngine();
        // DEBUG: 强制使用MiniMax TTS
        ttsEngine = "minimax";
        Log.i(TAG, "TTS Engine: " + ttsEngine + " (DEBUG: forced to MiniMax)");

        if ("minimax".equals(ttsEngine)) {
            Log.i(TAG, "Using MiniMax TTS engine");

            // 检查MiniMax是否已初始化
            if (!miniMaxTTS.isInitialized()) {
                // 检查具体缺少什么配置
                String miniMaxApiKey = configManager.getMiniMaxApiKey();
                String miniMaxGroupId = configManager.getMiniMaxGroupId();

                Log.e(TAG, "MiniMax TTS not initialized. API Key: " +
                        (miniMaxApiKey.isEmpty() ? "EMPTY" : "LOADED (" + miniMaxApiKey.length() + " chars)") +
                        ", Group ID: " + (miniMaxGroupId.isEmpty() ? "EMPTY" : "LOADED (" + miniMaxGroupId.length() + " chars)"));

                if (TextUtils.isEmpty(miniMaxApiKey)) {
                    if (callback != null) {
                        callback.onError("MiniMax API Key未配置，请先在语音设置中配置");
                    }
                    Log.e(TAG, "MiniMax API Key is empty");
                } else if (TextUtils.isEmpty(miniMaxGroupId)) {
                    if (callback != null) {
                        callback.onError("MiniMax Group ID未配置，请先在语音设置中填写Group ID");
                    }
                    Log.e(TAG, "MiniMax Group ID is empty");
                } else {
                    if (callback != null) {
                        callback.onError("MiniMax TTS初始化失败");
                    }
                    Log.e(TAG, "MiniMax TTS initialization failed for unknown reason");
                }
                return;
            }

            Log.i(TAG, "MiniMax TTS initialized, calling speak()");

            // 使用MiniMax TTS
            applyMiniMaxConfig();
            miniMaxTTS.speak(text, new MiniMaxTTSManager.SynthesisListener() {
                @Override
                public void onSpeakStart() {
                    Log.i(TAG, "MiniMax TTS onSpeakStart() called");
                    if (callback != null) {
                        callback.onSpeakStart();
                    }
                }

                @Override
                public void onSpeakComplete() {
                    if (callback != null) {
                        callback.onSpeakComplete();
                    }
                }

                @Override
                public void onError(int errorCode, String errorMessage) {
                    if (callback != null) {
                        callback.onError("MiniMax TTS错误: " + errorMessage);
                    }
                }
            });
            return;
        }

        // 使用腾讯云TTS
        if (!isInitialized) {
            if (callback != null) {
                callback.onError("腾讯云TTS未配置，请在语音设置中配置腾讯云密钥或切换到MiniMax TTS");
            }
            Log.e(TAG, "Tencent TTS not initialized");
            return;
        }

        // 应用配置参数
        applyVoiceConfig();

        synthesizer.speak(text, new SpeechSynthesizerManager.SynthesisListener() {
            @Override
            public void onSpeakStart() {
                if (callback != null) {
                    callback.onSpeakStart();
                }
            }

            @Override
            public void onSpeakComplete() {
                if (callback != null) {
                    callback.onSpeakComplete();
                }
            }

            @Override
            public void onError(int errorCode, String errorMsg) {
                if (callback != null) {
                    callback.onError("腾讯云TTS错误: " + errorMsg);
                }
            }
        });
    }

    /**
     * 语音合成 - 停止播放
     */
    public void stopSpeaking() {
        synthesizer.stop();
        miniMaxTTS.stop();
    }

    /**
     * 语音合成 - 暂停播放
     */
    public void pauseSpeaking() {
        synthesizer.pause();
    }

    /**
     * 语音合成 - 恢复播放
     */
    public void resumeSpeaking() {
        synthesizer.resume();
    }

    /**
     * 是否正在识别
     */
    public boolean isRecognizing() {
        return recognizer.isListening();
    }

    /**
     * 是否正在播放
     */
    public boolean isSpeaking() {
        return synthesizer.isSpeaking() || miniMaxTTS.isSpeaking();
    }

    /**
     * 是否已初始化
     */
    /**
     * 重新初始化语音功能（在配置更改后调用）
     */
    public void reinitialize() {
        Log.i(TAG, "Reinitializing voice manager...");
        isInitialized = false;
        configApplied = false;
        initialize();
    }

    public boolean isInitialized() {
        return isInitialized;
    }

    /**
     * 停止所有语音功能（识别和合成）
     */
    public void stop() {
        if (recognizer != null) {
            recognizer.stopListening();
        }
        if (synthesizer != null) {
            synthesizer.stop();
        }
        if (miniMaxTTS != null) {
            miniMaxTTS.stop();
        }
    }

    /**
     * 释放资源
     */
    public void release() {
        if (recognizer != null) {
            recognizer.release();
        }
        if (synthesizer != null) {
            synthesizer.release();
        }
        if (miniMaxTTS != null) {
            miniMaxTTS.release();
        }
    }

    // ========== 回调接口 ==========

    /**
     * 语音合成回调（别名，兼容旧代码）
     */
    public interface SynthesisListener extends VoiceSynthesisCallback {
        // 默认方法继承自VoiceSynthesisCallback
    }

    /**
     * 语音识别回调
     */
    public interface VoiceRecognitionCallback {
        /**
         * 中间结果（实时返回）
         */
        void onIntermediateResult(String text);

        /**
         * 最终结果
         */
        void onRecognitionResult(String text);

        /**
         * 错误
         */
        void onError(String error);
    }

    /**
     * 语音合成回调
     */
    public interface VoiceSynthesisCallback {
        void onSpeakStart();
        void onSpeakPaused();
        void onSpeakResumed();
        void onSpeakComplete();
        void onError(String error);
    }
}
