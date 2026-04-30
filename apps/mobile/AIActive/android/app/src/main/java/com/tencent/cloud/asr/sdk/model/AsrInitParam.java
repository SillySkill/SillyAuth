package com.tencent.cloud.asr.sdk.model;

/**
 * ASR初始化参数存根类
 */
public class AsrInitParam {
    // 公开字段，直接访问
    public String appId;
    public String projectId;
    public String secretId;
    public String secretKey;

    // Getter和Setter方法
    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getProjectId() {
        return projectId;
    }

    public void setProjectId(String projectId) {
        this.projectId = projectId;
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
}
