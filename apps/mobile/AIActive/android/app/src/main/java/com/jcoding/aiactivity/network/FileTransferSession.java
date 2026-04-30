package com.jcoding.aiactivity.network;

/**
 * 文件传输会话
 *
 * 记录单个文件传输的所有信息，包括：
 * - 传输ID
 * - 文件信息（名称、路径、大小）
 * - 传输类型（上传/下载）
 * - 当前进度
 * - 状态
 * - MD5校验和
 */
public class FileTransferSession {

    // 传输类型
    public static final int TYPE_UPLOAD = 1;
    public static final int TYPE_DOWNLOAD = 2;

    // 传输状态
    public static final int STATUS_PENDING = 0;
    public static final int STATUS_IN_PROGRESS = 1;
    public static final int STATUS_PAUSED = 2;
    public static final int STATUS_COMPLETED = 3;
    public static final int STATUS_FAILED = 4;
    public static final int STATUS_CANCELLED = 5;

    private String transferId;
    private String fileName;
    private String localPath;
    private long totalBytes;
    private long bytesTransferred;
    private int type;
    private int status;
    private String md5;
    private long startTime;
    private long endTime;
    private String errorMessage;
    private volatile boolean paused;
    private volatile boolean cancelled;

    /**
     * 构造函数
     *
     * @param transferId 传输ID
     * @param fileName 文件名
     * @param localPath 本地路径
     * @param totalBytes 文件总大小（字节）
     * @param type 传输类型（TYPE_UPLOAD 或 TYPE_DOWNLOAD）
     */
    public FileTransferSession(String transferId, String fileName, String localPath,
                              long totalBytes, int type) {
        this.transferId = transferId;
        this.fileName = fileName;
        this.localPath = localPath;
        this.totalBytes = totalBytes;
        this.type = type;
        this.status = STATUS_PENDING;
        this.bytesTransferred = 0;
        this.startTime = System.currentTimeMillis();
        this.paused = false;
        this.cancelled = false;
    }

    // Getters and Setters

    public String getTransferId() {
        return transferId;
    }

    public void setTransferId(String transferId) {
        this.transferId = transferId;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getLocalPath() {
        return localPath;
    }

    public void setLocalPath(String localPath) {
        this.localPath = localPath;
    }

    public long getTotalBytes() {
        return totalBytes;
    }

    public void setTotalBytes(long totalBytes) {
        this.totalBytes = totalBytes;
    }

    public long getBytesTransferred() {
        return bytesTransferred;
    }

    public void setBytesTransferred(long bytesTransferred) {
        this.bytesTransferred = bytesTransferred;
    }

    public int getType() {
        return type;
    }

    public void setType(int type) {
        this.type = type;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
        if (status == STATUS_COMPLETED || status == STATUS_FAILED || status == STATUS_CANCELLED) {
            this.endTime = System.currentTimeMillis();
        }
    }

    public String getMd5() {
        return md5;
    }

    public void setMd5(String md5) {
        this.md5 = md5;
    }

    public long getStartTime() {
        return startTime;
    }

    public void setStartTime(long startTime) {
        this.startTime = startTime;
    }

    public long getEndTime() {
        return endTime;
    }

    public void setEndTime(long endTime) {
        this.endTime = endTime;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public boolean isPaused() {
        return paused;
    }

    public boolean isCancelled() {
        return cancelled;
    }

    /**
     * 暂停传输
     */
    public void pause() {
        this.paused = true;
        this.status = STATUS_PAUSED;
    }

    /**
     * 恢复传输
     */
    public void resume() {
        this.paused = false;
        this.status = STATUS_IN_PROGRESS;
    }

    /**
     * 取消传输
     */
    public void cancel() {
        this.cancelled = true;
        this.status = STATUS_CANCELLED;
    }

    /**
     * 获取传输进度百分比
     */
    public int getProgress() {
        if (totalBytes == 0) {
            return 0;
        }
        return (int) ((bytesTransferred * 100) / totalBytes);
    }

    /**
     * 获取剩余字节数
     */
    public long getRemainingBytes() {
        return totalBytes - bytesTransferred;
    }

    /**
     * 获取传输速度（字节/秒）
     * 注意：返回当前瞬时速度
     */
    public double getSpeedBytesPerSecond() {
        long elapsedTime = System.currentTimeMillis() - startTime;
        if (elapsedTime <= 0) {
            return 0;
        }
        return (bytesTransferred * 1000.0) / elapsedTime;
    }

    /**
     * 获取预计剩余时间（毫秒）
     */
    public long getEstimatedTimeRemaining() {
        long remainingBytes = getRemainingBytes();
        double speed = getSpeedBytesPerSecond();
        if (speed <= 0) {
            return -1; // 无法估算
        }
        return (long) ((remainingBytes * 1000) / speed);
    }

    /**
     * 获取传输类型的字符串表示
     */
    public String getTypeName() {
        return type == TYPE_UPLOAD ? "上传" : "下载";
    }

    /**
     * 获取状态的字符串表示
     */
    public String getStatusName() {
        switch (status) {
            case STATUS_PENDING:
                return "等待中";
            case STATUS_IN_PROGRESS:
                return "传输中";
            case STATUS_PAUSED:
                return "已暂停";
            case STATUS_COMPLETED:
                return "已完成";
            case STATUS_FAILED:
                return "失败";
            case STATUS_CANCELLED:
                return "已取消";
            default:
                return "未知";
        }
    }

    @Override
    public String toString() {
        return "FileTransferSession{" +
                "transferId='" + transferId + '\'' +
                ", fileName='" + fileName + '\'' +
                ", type=" + getTypeName() +
                ", status=" + getStatusName() +
                ", progress=" + getProgress() + "%" +
                ", bytesTransferred=" + bytesTransferred +
                ", totalBytes=" + totalBytes +
                '}';
    }
}
