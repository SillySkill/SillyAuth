package com.tencent.cloud.asr.sdk.model;

/**
 * ASR配置存根类
 */
public class AsrConfig {
    private int engineModelType;
    private int audioInfo;
    private String secretId;
    private String secretKey;
    private String appId;

    public int getEngineModelType() {
        return engineModelType;
    }

    public void setEngineModelType(int engineModelType) {
        this.engineModelType = engineModelType;
    }

    public String getSecretId() {
        return secretId;
    }

    public void setSecretId(String secretId) {
        this.secretId = secretId;
    }

    public String getSecretKey() {
        return secretKey;
    }

    public void setSecretKey(String secretKey) {
        this.secretKey = secretKey;
    }

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }
}
