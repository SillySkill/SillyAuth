package com.jcoding.aiactivity.utils;

import android.content.Context;
import android.util.Log;

/**
 * 语音拍照助手（简化版 - 预留接口）
 * 注意：当前版本暂未集成ASR SDK，待后续实现
 */
public class VoiceCaptureHelper {

    private static final String TAG = "VoiceCaptureHelper";
    private boolean isListening = false;
    private Context context;

    public VoiceCaptureHelper(Context context) {
        this.context = context.getApplicationContext();
    }

    /**
     * 开始监听语音指令
     * 注意：当前版本暂未实现，预留接口
     */
    public void startListening(VoiceCaptureCallback callback) {
        Log.w(TAG, "语音识别功能暂未实现，待后续集成ASR SDK");
        isListening = true;
        // TODO: 待实现
        // 1. 集成腾讯ASR SDK
        // 2. 初始化录音和识别引擎
        // 3. 监听"拍照"关键词
    }

    /**
     * 停止监听
     */
    public void stopListening() {
        isListening = false;
        Log.d(TAG, "语音监听已停止");
    }

    /**
     * 语音识别回调接口
     */
    public interface VoiceCaptureCallback {
        void onCaptureCommand(String recognizedText);
        void onError(String error);
    }
}
