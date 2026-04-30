package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.media.AudioManager;
import android.os.Environment;
import android.text.TextUtils;
import android.util.Log;

import com.tencent.cloud.asr.sdk.AsrRecognizer;
import com.tencent.cloud.asr.sdk.model.AsrAudioInfo;
import com.tencent.cloud.asr.sdk.model.AsrConfig;
import com.tencent.cloud.asr.sdk.model.AsrDetectResult;
import com.tencent.cloud.asr.sdk.model.AsrInitParam;
import com.tencent.cloud.asr.sdk.model.AsrRecorder;
import com.tencent.cloud.asr.sdk.model.AsrRecorderFactory;
import com.tencent.cloud.asr.sdk.model.AsrUserConfig;

import java.io.File;

/**
 * 腾讯ASR语音识别管理器
 */
public class SpeechRecognizerManager {

    private static final String TAG = "SpeechRecognizerManager";

    private static SpeechRecognizerManager instance;
    private Context context;
    private AsrRecognizer asrRecognizer;
    private AsrRecorder asrRecorder;
    private boolean isListening = false;
    private RecognitionListener listener;

    // 配置参数（需要从配置文件读取）
    private String appId = "";
    private String secretId = "";
    private String secretKey = "";

    // ASR参数
    private String engineModelType = "16k_zh";  // 默认：16k中文
    private boolean filterDirty = false;         // 默认：不过滤脏话
    private boolean filterModal = true;          // 默认：过滤语气词
    private boolean convertNumMode = true;       // 默认：数字转阿拉伯数字

    private SpeechRecognizerManager(Context context) {
        this.context = context.getApplicationContext();
        initRecognizer();
    }

    public static synchronized SpeechRecognizerManager getInstance(Context context) {
        if (instance == null) {
            instance = new SpeechRecognizerManager(context);
        }
        return instance;
    }

    /**
     * 初始化识别器
     */
    private void initRecognizer() {
        try {
            // 创建识别器
            asrRecognizer = new AsrRecognizer(context, new AsrRecognizer.IAsrListener() {
                @Override
                public void onAsrDetectResult(AsrDetectResult result) {
                    if (listener != null) {
                        if (result != null && !TextUtils.isEmpty(result.text)) {
                            listener.onResult(result.text, result.isFinal());
                        }
                    }
                }

                @Override
                public void onAsrInitSuccess() {
                    Log.i(TAG, "ASR recognizer initialized successfully");
                }

                @Override
                public void onAsrInitFailure(int errorCode, String errorMsg) {
                    Log.e(TAG, "ASR Init Failed: " + errorCode + ", " + errorMsg);
                    if (listener != null) {
                        listener.onError(errorCode, errorMsg);
                    }
                }
            });

            // 创建录音器
            AsrRecorderFactory recorderFactory = new AsrRecorderFactory();
            asrRecorder = recorderFactory.createRecorder(
                    AsrRecorderFactory.RecorderType.RECORDER_TYPE_RECORD);
            asrRecorder.setAudioSource(android.media.MediaRecorder.AudioSource.MIC);

            Log.i(TAG, "ASR recognizer initialized");
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize ASR", e);
        }
    }

    /**
     * 设置配置参数
     */
    public void setConfig(String appId, String secretId, String secretKey) {
        this.appId = appId;
        this.secretId = secretId;
        this.secretKey = secretKey;
    }

    /**
     * 应用ASR参数配置
     */
    public void applyConfig(String engineModelType, boolean filterDirty,
                          boolean filterModal, boolean convertNumMode) {
        this.engineModelType = engineModelType;
        this.filterDirty = filterDirty;
        this.filterModal = filterModal;
        this.convertNumMode = convertNumMode;

        // 更新识别器配置
        updateUserConfig();
    }

    /**
     * 更新用户配置
     */
    private void updateUserConfig() {
        AsrInitParam initParam = new AsrInitParam();
        initParam.appId = appId;  // 直接使用String
        initParam.secretId = secretId;
        initParam.secretKey = secretKey;

        // 设置识别参数（使用配置值）
        AsrUserConfig userConfig = new AsrUserConfig();

        // 根据engineModelType设置引擎类型
        if ("16k_zh".equals(engineModelType)) {
            userConfig.engineModelType = AsrUserConfig.ENGINE_MODEL_TYPE_16K_ZH;
        } else if ("8k_zh".equals(engineModelType)) {
            userConfig.engineModelType = AsrUserConfig.ENGINE_MODEL_TYPE_8K_ZH;
        } else if ("16k_en".equals(engineModelType)) {
            userConfig.engineModelType = AsrUserConfig.ENGINE_MODEL_TYPE_16K_EN;
        } else {
            userConfig.engineModelType = AsrUserConfig.ENGINE_MODEL_TYPE_16K_ZH;
        }

        userConfig.setFilterDirty(filterDirty ? 1 : 0);   // 过滤脏话
        userConfig.setFilterModal(filterModal ? 1 : 0);   // 过滤语气词
        userConfig.setConvert_num_mode(convertNumMode ? 1 : 0); // 数字转换

        asrRecognizer.init(initParam, userConfig);
    }

    /**
     * 开始识别
     */
    public boolean startListening(RecognitionListener listener) {
        if (isListening) {
            Log.w(TAG, "Already listening");
            return false;
        }

        this.listener = listener;

        try {
            // 检查权限
            if (!hasRecordPermission()) {
                if (listener != null) {
                    listener.onError(-1, "没有录音权限");
                }
                return false;
            }

            // 开始识别
            asrRecognizer.start();
            isListening = true;

            Log.i(TAG, "Started listening");
            return true;
        } catch (Exception e) {
            Log.e(TAG, "Failed to start listening", e);
            if (listener != null) {
                listener.onError(-2, "启动失败: " + e.getMessage());
            }
            return false;
        }
    }

    /**
     * 停止识别
     */
    public void stopListening() {
        if (!isListening) {
            return;
        }

        try {
            asrRecognizer.stop();
            isListening = false;
            Log.i(TAG, "Stopped listening");
        } catch (Exception e) {
            Log.e(TAG, "Failed to stop listening", e);
        }
    }

    /**
     * 取消识别
     */
    public void cancel() {
        try {
            asrRecognizer.cancel();
            isListening = false;
            Log.i(TAG, "Cancelled recognition");
        } catch (Exception e) {
            Log.e(TAG, "Failed to cancel", e);
        }
    }

    /**
     * 释放资源
     */
    public void release() {
        try {
            if (asrRecognizer != null) {
                asrRecognizer.stop();
                asrRecognizer = null;
            }
            if (asrRecorder != null) {
                asrRecorder.stop();
                asrRecorder = null;
            }
            isListening = false;
            Log.i(TAG, "Released resources");
        } catch (Exception e) {
            Log.e(TAG, "Failed to release", e);
        }
    }

    /**
     * 检查录音权限
     */
    private boolean hasRecordPermission() {
        AudioManager audioManager = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
        return audioManager != null;
    }

    /**
     * 是否正在识别
     */
    public boolean isListening() {
        return isListening;
    }

    /**
     * 识别结果监听器
     */
    public interface RecognitionListener {
        /**
         * 识别结果回调
         * @param result 识别文本
         * @param isFinal 是否最终结果
         */
        void onResult(String result, boolean isFinal);

        /**
         * 错误回调
         * @param errorCode 错误码
         * @param errorMsg 错误信息
         */
        void onError(int errorCode, String errorMsg);
    }
}
