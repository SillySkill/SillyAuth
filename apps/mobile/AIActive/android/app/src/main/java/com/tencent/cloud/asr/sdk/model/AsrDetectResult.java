package com.tencent.cloud.asr.sdk.model;

/**
 * ASR检测结果存根类
 */
public class AsrDetectResult {
    public String text;  // 公开字段，直接访问
    private int voiceTextType;
    private boolean isFinal;

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public int getVoiceTextType() {
        return voiceTextType;
    }

    public void setVoiceTextType(int voiceTextType) {
        this.voiceTextType = voiceTextType;
    }

    public boolean isFinal() {
        return isFinal;
    }

    public void setFinal(boolean isFinal) {
        this.isFinal = isFinal;
    }
}
