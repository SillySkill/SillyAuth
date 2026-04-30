package com.jcoding.aiactivity.network;

import com.google.gson.annotations.SerializedName;

/**
 * MiniMax语音合成任务状态查询结果
 * API: GET /v1/query/t2a_async_v2?task_id={task_id}
 * 返回: task_id, file_id, status, process_status等
 */
public class MiniMaxAsyncResult {

    @SerializedName("task_id")
    private String taskId;

    @SerializedName("file_id")
    private String fileId;

    @SerializedName("task_status")
    private String taskStatus;  // Queueing, Processing, Success, Fail, Timeout

    @SerializedName("process_status")
    private String processStatus;

    @SerializedName("status")
    private String status;

    @SerializedName("created_time")
    private long createdTime;

    @SerializedName("base_resp")
    private BaseResp baseResp;

    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getFileId() {
        return fileId;
    }

    public void setFileId(String fileId) {
        this.fileId = fileId;
    }

    public String getTaskStatus() {
        return taskStatus;
    }

    public void setTaskStatus(String taskStatus) {
        this.taskStatus = taskStatus;
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
        return "Success".equalsIgnoreCase(taskStatus) ||
               "Success".equalsIgnoreCase(processStatus);
    }

    public boolean isProcessing() {
        return "Queueing".equalsIgnoreCase(taskStatus) ||
               "Processing".equalsIgnoreCase(taskStatus) ||
               "Queueing".equalsIgnoreCase(processStatus) ||
               "Processing".equalsIgnoreCase(processStatus);
    }

    public boolean isFailed() {
        return "Fail".equalsIgnoreCase(taskStatus) ||
               "Timeout".equalsIgnoreCase(taskStatus) ||
               "Fail".equalsIgnoreCase(status);
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
