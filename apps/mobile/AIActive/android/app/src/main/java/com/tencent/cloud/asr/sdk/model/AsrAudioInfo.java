package com.tencent.cloud.asr.sdk.model;

/**
 * ASR音频信息存根类
 */
public class AsrAudioInfo {
    private int sampleRate;
    private int channels;
    private int bitsPerSample;

    public int getSampleRate() {
        return sampleRate;
    }

    public void setSampleRate(int sampleRate) {
        this.sampleRate = sampleRate;
    }

    public int getChannels() {
        return channels;
    }

    public void setChannels(int channels) {
        this.channels = channels;
    }
}
