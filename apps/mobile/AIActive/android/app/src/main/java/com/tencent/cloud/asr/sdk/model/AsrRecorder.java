package com.tencent.cloud.asr.sdk.model;

/**
 * ASR录音器存根类
 */
public class AsrRecorder {
    public interface AsrRecorderListener {
        void onAsrRecorderData(byte[] data);
    }

    public void start() {
        // 存根实现
    }

    public void stop() {
        // 存根实现
    }

    public void release() {
        // 存根实现
    }

    /**
     * 设置音频源
     */
    public void setAudioSource(int audioSource) {
        // 存根实现 - 设置音频源（如MediaRecorder.AudioSource.MIC）
    }

    /**
     * 设置采样率
     */
    public void setSampleRate(int sampleRate) {
        // 存根实现
    }

    /**
     * 设置音频格式
     */
    public void setAudioFormat(int audioFormat) {
        // 存根实现 - 如AudioFormat.ENCODING_PCM_16BIT
    }

    /**
     * 设置通道配置
     */
    public void setChannelConfig(int channelConfig) {
        // 存根实现 - 如AudioFormat.CHANNEL_IN_MONO
    }
}
