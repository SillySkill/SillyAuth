package com.tencent.cloud.asr.sdk;

import android.content.Context;
import com.tencent.cloud.asr.sdk.model.AsrInitParam;
import com.tencent.cloud.asr.sdk.model.AsrDetectResult;
import com.tencent.cloud.asr.sdk.model.AsrUserConfig;

/**
 * ASR识别器存根类
 * 原SDK类缺失时的临时实现
 */
public class AsrRecognizer {
    public interface IAsrListener {
        void onAsrDetectResult(AsrDetectResult result);
        void onAsrInitSuccess();
        void onAsrInitFailure(int errorCode, String errorMsg);
    }

    public AsrRecognizer(Context context, IAsrListener listener) {
        // 存根实现 - SDK类缺失时使用
    }

    public void init(AsrInitParam initParam) {
        // 存根实现
    }

    public void init(AsrInitParam initParam, AsrUserConfig userConfig) {
        // 存根实现 - 带用户配置的初始化
    }

    public void start() {
        // 存根实现
    }

    public void stop() {
        // 存根实现
    }

    public void cancel() {
        // 存根实现 - 取消识别
    }

    public void release() {
        // 存根实现
    }
}
