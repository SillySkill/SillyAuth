package com.jcoding.aiactivity.entity;

/**
 * AI生成任务实体
 */
public class GenerationTask {

    private String taskId;           // 任务ID
    private String styleId;          // 风格ID
    private String imageUrl;         // 用户照片URL
    private int status;              // 状态：0=待处理，1=处理中，2=完成，3=失败
    private String resultUrl;        // 生成结果URL
    private long createdAt;          // 创建时间
    private long completedAt;        // 完成时间
    private String errorMessage;     // 错误信息

    public GenerationTask() {
    }

    public GenerationTask(String taskId, String styleId, String imageUrl) {
        this.taskId = taskId;
        this.styleId = styleId;
        this.imageUrl = imageUrl;
        this.status = 0;
        this.createdAt = System.currentTimeMillis();
    }

    // Getters and Setters
    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getStyleId() {
        return styleId;
    }

    public void setStyleId(String styleId) {
        this.styleId = styleId;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getResultUrl() {
        return resultUrl;
    }

    public void setResultUrl(String resultUrl) {
        this.resultUrl = resultUrl;
    }

    public long getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(long createdAt) {
        this.createdAt = createdAt;
    }

    public long getCompletedAt() {
        return completedAt;
    }

    public void setCompletedAt(long completedAt) {
        this.completedAt = completedAt;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    /**
     * 判断是否完成
     */
    public boolean isCompleted() {
        return status == 2;
    }

    /**
     * 判断是否失败
     */
    public boolean isFailed() {
        return status == 3;
    }

    /**
     * 判断是否处理中
     */
    public boolean isProcessing() {
        return status == 1;
    }
}
