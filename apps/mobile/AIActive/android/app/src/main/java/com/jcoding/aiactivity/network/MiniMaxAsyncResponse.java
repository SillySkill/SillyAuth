package com.jcoding.aiactivity.network;

import com.google.gson.annotations.SerializedName;

/**
 * MiniMax异步语音合成响应
 * API: POST /v1/t2a_async_v2
 * 返回: task_id, file_id, task_token, usage_characters
 */
public class MiniMaxAsyncResponse {

    @SerializedName("task_id")
    private String taskId;

    @SerializedName("task_token")
    private String taskToken;

    @SerializedName("file_id")
    private String fileId;

    @SerializedName("usage_characters")
    private int usageCharacters;

    @SerializedName("base_resp")
    private BaseResp baseResp;

    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getTaskToken() {
        return taskToken;
    }

    public void setTaskToken(String taskToken) {
        this.taskToken = taskToken;
    }

    public String getFileId() {
        return fileId;
    }

    public void setFileId(String fileId) {
        this.fileId = fileId;
    }

    public int getUsageCharacters() {
        return usageCharacters;
    }

    public void setUsageCharacters(int usageCharacters) {
        this.usageCharacters = usageCharacters;
    }

    public BaseResp getBaseResp() {
        return baseResp;
    }

    public void setBaseResp(BaseResp baseResp) {
        this.baseResp = baseResp;
    }

    /**
     * 基础响应
     */
    public static class BaseResp {
        @SerializedName("status_code")
        private int statusCode;

        @SerializedName("status_msg")
        private String statusMsg;

        public int getStatusCode() {
            return statusCode;
        }

        public void setStatusCode(int statusCode) {
            this.statusCode = statusCode;
        }

        public String getStatusMsg() {
            return statusMsg;
        }

        public void setStatusMsg(String statusMsg) {
            this.statusMsg = statusMsg;
        }
    }
}
