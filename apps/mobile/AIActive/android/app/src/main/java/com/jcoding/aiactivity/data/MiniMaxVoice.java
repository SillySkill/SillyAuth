package com.jcoding.aiactivity.data;

/**
 * MiniMax语音合成音色数据类
 * 用于表示可用的TTS发音人
 */
public class MiniMaxVoice {
    private String voiceId;      // API使用的voice_id
    private String displayName;  // 显示名称
    private String language;     // 语言分类
    private String category;     // 细分分类（如"男声"、"女声"等）
    private boolean isCartoon;   // 是否为卡通/动漫风格

    public MiniMaxVoice(String voiceId, String displayName, String language, String category) {
        this(voiceId, displayName, language, category, false);
    }

    public MiniMaxVoice(String voiceId, String displayName, String language, String category, boolean isCartoon) {
        this.voiceId = voiceId;
        this.displayName = displayName;
        this.language = language;
        this.category = category;
        this.isCartoon = isCartoon;
    }

    public String getVoiceId() {
        return voiceId;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getLanguage() {
        return language;
    }

    public String getCategory() {
        return category;
    }

    public boolean isCartoon() {
        return isCartoon;
    }

    public void setCartoon(boolean cartoon) {
        isCartoon = cartoon;
    }

    @Override
    public String toString() {
        return displayName;
    }
}
