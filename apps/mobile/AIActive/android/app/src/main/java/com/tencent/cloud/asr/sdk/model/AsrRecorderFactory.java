package com.tencent.cloud.asr.sdk.model;

import android.content.Context;

/**
 * ASR录音器工厂存根类
 */
public class AsrRecorderFactory {
    public static final int RECORDER_TYPE_RECORD = 0;

    // 录音器类型枚举
    public static class RecorderType {
        public static final int RECORDER_TYPE_RECORD = 0;
    }

    private Context context;

    // 无参构造函数（兼容旧代码）
    public AsrRecorderFactory() {
    }

    public AsrRecorderFactory(Context context) {
        this.context = context;
    }

    public AsrRecorder createRecorder(int recorderType) {
        return new AsrRecorder();
    }
}
