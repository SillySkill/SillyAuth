package com.jcoding.aiactivity.network;

import android.content.Context;
import android.util.Log;

import com.jcoding.aiactivity.security.OperationLogger;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 文件传输管理器
 *
 * 功能：
 * 1. 分块传输大文件
 * 2. 进度跟踪和回调
 * 3. 断点续传
 * 4. MD5校验
 * 5. 并发传输管理
 */
public class FileTransferManager {

    private static final String TAG = "FileTransferManager";
    private static final int DEFAULT_CHUNK_SIZE = 64 * 1024; // 64KB chunks
    private static final int MAX_CONCURRENT_TRANSFERS = 3;

    private static FileTransferManager instance;
    private Context context;

    // 活跃的传输会话
    private Map<String, FileTransferSession> activeTransfers;
    // 传输监听器
    private Map<String, TransferListener> transferListeners;

    /**
     * 传输监听器接口
     */
    public interface TransferListener {
        void onProgress(String transferId, int progress, long bytesTransferred, long totalBytes);
        void onCompleted(String transferId, File file);
        void onError(String transferId, String error);
    }

    private FileTransferManager(Context context) {
        this.context = context.getApplicationContext();
        this.activeTransfers = new ConcurrentHashMap<>();
        this.transferListeners = new ConcurrentHashMap<>();
    }

    public static synchronized FileTransferManager getInstance(Context context) {
        if (instance == null) {
            instance = new FileTransferManager(context);
        }
        return instance;
    }

    /**
     * 开始上传文件
     *
     * @param filePath 文件路径
     * @param listener 传输监听器
     * @return 传输ID
     */
    public String uploadFile(String filePath, TransferListener listener) {
        File file = new File(filePath);
        if (!file.exists()) {
            if (listener != null) {
                listener.onError(null, "文件不存在");
            }
            return null;
        }

        String transferId = generateTransferId("upload", file.getName());

        FileTransferSession session = new FileTransferSession(
            transferId,
            file.getName(),
            file.getAbsolutePath(),
            file.length(),
            FileTransferSession.TYPE_UPLOAD
        );

        activeTransfers.put(transferId, session);
        if (listener != null) {
            transferListeners.put(transferId, listener);
        }

        // 启动传输线程
        new Thread(() -> performUpload(session)).start();

        return transferId;
    }

    /**
     * 开始下载文件
     *
     * @param remotePath 远程文件路径
     * @param localPath 本地保存路径
     * @param fileSize 文件大小（用于进度计算）
     * @param listener 传输监听器
     * @return 传输ID
     */
    public String downloadFile(String remotePath, String localPath, long fileSize,
                              TransferListener listener) {
        String transferId = generateTransferId("download", new File(remotePath).getName());

        FileTransferSession session = new FileTransferSession(
            transferId,
            new File(remotePath).getName(),
            localPath,
            fileSize,
            FileTransferSession.TYPE_DOWNLOAD
        );

        activeTransfers.put(transferId, session);
        if (listener != null) {
            transferListeners.put(transferId, listener);
        }

        // 启动传输线程
        new Thread(() -> performDownload(session, remotePath)).start();

        return transferId;
    }

    /**
     * 取消传输
     */
    public boolean cancelTransfer(String transferId) {
        FileTransferSession session = activeTransfers.get(transferId);
        if (session != null) {
            session.cancel();
            activeTransfers.remove(transferId);
            transferListeners.remove(transferId);
            return true;
        }
        return false;
    }

    /**
     * 暂停传输（支持断点续传）
     */
    public boolean pauseTransfer(String transferId) {
        FileTransferSession session = activeTransfers.get(transferId);
        if (session != null) {
            session.pause();
            return true;
        }
        return false;
    }

    /**
     * 恢复传输
     */
    public boolean resumeTransfer(String transferId) {
        FileTransferSession session = activeTransfers.get(transferId);
        if (session != null && session.isPaused()) {
            session.resume();
            if (session.getType() == FileTransferSession.TYPE_UPLOAD) {
                new Thread(() -> performUpload(session)).start();
            } else {
                new Thread(() -> performDownload(session, null)).start();
            }
            return true;
        }
        return false;
    }

    /**
     * 执行上传
     */
    private void performUpload(FileTransferSession session) {
        FileInputStream fis = null;
        BufferedInputStream bis = null;

        try {
            File file = new File(session.getLocalPath());
            fis = new FileInputStream(file);
            bis = new BufferedInputStream(fis);

            byte[] buffer = new byte[DEFAULT_CHUNK_SIZE];
            long totalBytesRead = session.getBytesTransferred();
            int bytesRead;

            // 如果是从断点恢复，跳过已传输的字节
            if (totalBytesRead > 0) {
                bis.skip(totalBytesRead);
            }

            while ((bytesRead = bis.read(buffer)) != -1 && !session.isCancelled()) {
                while (session.isPaused()) {
                    Thread.sleep(100);
                }

                // TODO: 实际发送到服务器
                // 这里需要根据实际的通信协议实现
                // 示例：networkClient.sendFileChunk(session.getTransferId(), buffer, bytesRead);

                totalBytesRead += bytesRead;
                session.setBytesTransferred(totalBytesRead);

                // 更新进度
                int progress = (int) ((totalBytesRead * 100) / session.getTotalBytes());
                notifyProgress(session.getTransferId(), progress, totalBytesRead, session.getTotalBytes());
            }

            if (session.isCancelled()) {
                notifyError(session.getTransferId(), "传输已取消");
                return;
            }

            // 计算MD5
            String md5 = calculateMD5(file);
            session.setMd5(md5);

            // TODO: 发送完成信号和MD5到服务器
            // networkClient.sendFileComplete(session.getTransferId(), md5);

            session.setStatus(FileTransferSession.STATUS_COMPLETED);
            notifyCompleted(session.getTransferId(), file);

            // 记录日志
            OperationLogger.getInstance(context).log(
                "system",
                OperationLogger.ACTION_MEDIA_UPLOAD,
                "文件上传完成: " + session.getFileName() + " (" + formatFileSize(session.getTotalBytes()) + ")",
                OperationLogger.LEVEL_INFO
            );

        } catch (Exception e) {
            Log.e(TAG, "上传失败", e);
            session.setStatus(FileTransferSession.STATUS_FAILED);
            notifyError(session.getTransferId(), "上传失败: " + e.getMessage());

            OperationLogger.getInstance(context).log(
                "system",
                OperationLogger.ACTION_MEDIA_UPLOAD,
                "文件上传失败: " + session.getFileName() + " - " + e.getMessage(),
                OperationLogger.LEVEL_ERROR
            );
        } finally {
            try {
                if (bis != null) bis.close();
                if (fis != null) fis.close();
            } catch (IOException e) {
                Log.e(TAG, "关闭流失败", e);
            }

            if (!session.isPaused()) {
                activeTransfers.remove(session.getTransferId());
                transferListeners.remove(session.getTransferId());
            }
        }
    }

    /**
     * 执行下载
     */
    private void performDownload(FileTransferSession session, String remotePath) {
        FileOutputStream fos = null;
        BufferedOutputStream bos = null;

        try {
            File file = new File(session.getLocalPath());
            File parentDir = file.getParentFile();
            if (parentDir != null && !parentDir.exists()) {
                parentDir.mkdirs();
            }

            fos = new FileOutputStream(file, session.getBytesTransferred() > 0); // 支持断点续传
            bos = new BufferedOutputStream(fos);

            // TODO: 实际从服务器下载
            // 这里需要根据实际的通信协议实现
            // 示例：networkClient.receiveFileChunk(session.getTransferId(), buffer);

            // 模拟下载过程
            byte[] buffer = new byte[DEFAULT_CHUNK_SIZE];
            long totalBytesRead = session.getBytesTransferred();
            long remainingBytes = session.getTotalBytes() - totalBytesRead;

            while (remainingBytes > 0 && !session.isCancelled()) {
                while (session.isPaused()) {
                    Thread.sleep(100);
                }

                int bytesToRead = (int) Math.min(buffer.length, remainingBytes);
                // TODO: 从服务器读取数据
                // int bytesRead = networkClient.readFileChunk(remotePath, totalBytesRead, buffer, 0, bytesToRead);

                // 模拟读取数据
                int bytesRead = bytesToRead; // 实际应该从服务器读取

                bos.write(buffer, 0, bytesRead);

                totalBytesRead += bytesRead;
                session.setBytesTransferred(totalBytesRead);
                remainingBytes = session.getTotalBytes() - totalBytesRead;

                // 更新进度
                int progress = (int) ((totalBytesRead * 100) / session.getTotalBytes());
                notifyProgress(session.getTransferId(), progress, totalBytesRead, session.getTotalBytes());
            }

            if (session.isCancelled()) {
                notifyError(session.getTransferId(), "传输已取消");
                file.delete();
                return;
            }

            // 验证MD5
            String expectedMd5 = session.getMd5();
            if (expectedMd5 != null && !expectedMd5.isEmpty()) {
                String actualMd5 = calculateMD5(file);
                if (!expectedMd5.equals(actualMd5)) {
                    session.setStatus(FileTransferSession.STATUS_FAILED);
                    notifyError(session.getTransferId(), "MD5校验失败");
                    file.delete();
                    return;
                }
            }

            session.setStatus(FileTransferSession.STATUS_COMPLETED);
            notifyCompleted(session.getTransferId(), file);

            OperationLogger.getInstance(context).log(
                "system",
                OperationLogger.ACTION_MEDIA_UPLOAD,
                "文件下载完成: " + session.getFileName() + " (" + formatFileSize(session.getTotalBytes()) + ")",
                OperationLogger.LEVEL_INFO
            );

        } catch (Exception e) {
            Log.e(TAG, "下载失败", e);
            session.setStatus(FileTransferSession.STATUS_FAILED);
            notifyError(session.getTransferId(), "下载失败: " + e.getMessage());

            OperationLogger.getInstance(context).log(
                "system",
                OperationLogger.ACTION_MEDIA_UPLOAD,
                "文件下载失败: " + session.getFileName() + " - " + e.getMessage(),
                OperationLogger.LEVEL_ERROR
            );
        } finally {
            try {
                if (bos != null) bos.close();
                if (fos != null) fos.close();
            } catch (IOException e) {
                Log.e(TAG, "关闭流失败", e);
            }

            if (!session.isPaused()) {
                activeTransfers.remove(session.getTransferId());
                transferListeners.remove(session.getTransferId());
            }
        }
    }

    /**
     * 计算文件的MD5哈希值
     */
    private String calculateMD5(File file) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            FileInputStream fis = new FileInputStream(file);
            byte[] buffer = new byte[8192];
            int bytesRead;

            while ((bytesRead = fis.read(buffer)) != -1) {
                md.update(buffer, 0, bytesRead);
            }

            fis.close();

            byte[] digest = md.digest();
            BigInteger bigInt = new BigInteger(1, digest);
            return bigInt.toString(16);
        } catch (NoSuchAlgorithmException | IOException e) {
            Log.e(TAG, "计算MD5失败", e);
            return "";
        }
    }

    /**
     * 生成传输ID
     */
    private String generateTransferId(String type, String fileName) {
        return type + "_" + System.currentTimeMillis() + "_" + fileName.hashCode();
    }

    /**
     * 格式化文件大小
     */
    private String formatFileSize(long bytes) {
        if (bytes < 1024) {
            return bytes + " B";
        } else if (bytes < 1024 * 1024) {
            return String.format("%.1f KB", bytes / 1024.0);
        } else if (bytes < 1024 * 1024 * 1024) {
            return String.format("%.1f MB", bytes / (1024.0 * 1024));
        } else {
            return String.format("%.1f GB", bytes / (1024.0 * 1024 * 1024));
        }
    }

    /**
     * 通知进度更新
     */
    private void notifyProgress(String transferId, int progress, long bytesTransferred, long totalBytes) {
        TransferListener listener = transferListeners.get(transferId);
        if (listener != null) {
            listener.onProgress(transferId, progress, bytesTransferred, totalBytes);
        }
    }

    /**
     * 通知传输完成
     */
    private void notifyCompleted(String transferId, File file) {
        TransferListener listener = transferListeners.get(transferId);
        if (listener != null) {
            listener.onCompleted(transferId, file);
        }
    }

    /**
     * 通知传输错误
     */
    private void notifyError(String transferId, String error) {
        TransferListener listener = transferListeners.get(transferId);
        if (listener != null) {
            listener.onError(transferId, error);
        }
    }

    /**
     * 获取传输会话信息
     */
    public FileTransferSession getTransferSession(String transferId) {
        return activeTransfers.get(transferId);
    }

    /**
     * 获取所有活跃的传输
     */
    public Map<String, FileTransferSession> getActiveTransfers() {
        return new HashMap<>(activeTransfers);
    }
}
