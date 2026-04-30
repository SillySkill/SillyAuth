package com.jcoding.aiactivity.network;

import com.google.gson.annotations.SerializedName;

/**
 * MiniMax文件信息响应
 * API: GET /v1/files/retrieve?file_id={file_id}
 * 返回: file_id, download_url, process_status等
 */
public class MiniMaxFileInfo {

    @SerializedName("file_id")
    private String fileId;

    @SerializedName("download_url")
    private String downloadUrl;

    @SerializedName("process_status")
    private String processStatus;  // Queueing, Processing, Success, Fail

    @SerializedName("status")
    private String status;

    @SerializedName("file_type")
    private String fileType;

    @SerializedName("created_time")
    private long createdTime;

    @SerializedName("base_resp")
    private BaseResp baseResp;

    public String getFileId() {
        return fileId;
    }

    public void setFileId(String fileId) {
        this.fileId = fileId;
    }

    public String getDownloadUrl() {
        return downloadUrl;
    }

    public void setDownloadUrl(String downloadUrl) {
        this.downloadUrl = downloadUrl;
    }

    public String getProcessStatus() {
        return processStatus;
    }

    public void setProcessStatus(String processStatus) {
        this.processStatus = processStatus;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getFileType() {
        return fileType;
    }

    public void setFileType(String fileType) {
        this.fileType = fileType;
    }

    public long getCreatedTime() {
        return createdTime;
    }

    public void setCreatedTime(long createdTime) {
        this.createdTime = createdTime;
    }

    public BaseResp getBaseResp() {
        return baseResp;
    }

    public void setBaseResp(BaseResp baseResp) {
        this.baseResp = baseResp;
    }

    public boolean isSuccess() {
        return "Success".equalsIgnoreCase(processStatus) ||
               "success".equalsIgnoreCase(status);
    }

    public boolean isProcessing() {
        return "Queueing".equalsIgnoreCase(processStatus) ||
               "Processing".equalsIgnoreCase(processStatus);
    }

    public boolean isFailed() {
        return "Fail".equalsIgnoreCase(processStatus) ||
               "fail".equalsIgnoreCase(status);
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
