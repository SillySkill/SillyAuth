package com.tencent.cloud.sdktts;

import com.tencent.cloud.libqcloudtts.TtsMode;

public class SettingDialogConfig {

    public SettingDialogConfig() {

    }

    public TtsMode ttsmode = TtsMode.ONLINE;

    public int connectTimeout = 15 * 1000;

    public int readTimeout = 30 * 1000;

    public int CheckNetworkIntervalTime = 5 * 60 * 1000;

    public int voiceType = 1001;

    public float speed = 0f;

    public Float volume = 0f;

    public int primaryLanguage = 1;

    //offline
    public String offlineVoiceType = "";

    public float offlineVolume = 1.0f;

    public float offlineSpeed = 1.0f;

}
