package com.jcoding.aiactivity.network;

import android.util.Log;

import java.io.BufferedOutputStream;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;

/**
 * 二进制文件接收器
 *
 * 处理大文件接收：
 * 1. 分块接收
 * 2. 进度跟踪
 * 3. MD5校验
 * 4. 断点续传
 */
public class BinaryFileReceiver {

    private static final String TAG = "BinaryFileReceiver";
    private static final int BUFFER_SIZE = 64 * 1024; // 64KB

    /**
     * 文件传输会话
     */
    public static class TransferSession {
        public String transferId;
        public String fileName;
        public String filePath;
        public long fileSize;
        public long bytesReceived;
        public String md5;
        public boolean completed;
        public File outputFile;

        public int getProgress() {
            if (fileSize == 0) return 0;
            return (int) ((bytesReceived * 100) / fileSize);
        }
    }

    // 活跃的传输会话
    private Map<String, TransferSession> activeTransfers = new HashMap<>();

    /**
     * 开始文件传输
     *
     * @param transferId 传输ID
     * @param fileName 文件名
     * @param fileSize 文件大小
     * @param saveDir 保存目录
     * @return 会话对象
     */
    public TransferSession startTransfer(String transferId, String fileName, long fileSize, File saveDir) {
        TransferSession session = new TransferSession();
        session.transferId = transferId;
        session.fileName = fileName;
        session.fileSize = fileSize;
        session.bytesReceived = 0;
        session.completed = false;

        // 创建输出文件
        if (!saveDir.exists()) {
            saveDir.mkdirs();
        }
        session.outputFile = new File(saveDir, fileName);
        session.filePath = session.outputFile.getAbsolutePath();

        activeTransfers.put(transferId, session);
        Log.i(TAG, "开始文件传输: " + fileName + " (" + formatFileSize(fileSize) + ")");

        return session;
    }

    /**
     * 接收文件数据块
     *
     * @param transferId 传输ID
     * @param data 数据
     * @param offset 偏移量
     * @param length 长度
     * @return 接收的字节数
     */
    public int receiveChunk(String transferId, byte[] data, int offset, int length) {
        TransferSession session = activeTransfers.get(transferId);
        if (session == null || session.completed) {
            Log.w(TAG, "无效的传输会话: " + transferId);
            return 0;
        }

        try {
            // 以追加模式写入文件
            FileOutputStream fos = new FileOutputStream(session.outputFile, true);
            BufferedOutputStream bos = new BufferedOutputStream(fos);

            bos.write(data, offset, length);
            bos.flush();
            bos.close();

            session.bytesReceived += length;

            int progress = session.getProgress();
            Log.d(TAG, "接收进度: " + transferId + " - " + progress + "%");

            return length;

        } catch (IOException e) {
            Log.e(TAG, "写入文件块失败", e);
            return 0;
        }
    }

    /**
     * 完成传输并验证
     *
     * @param transferId 传输ID
     * @param expectedMd5 期望的MD5
     * @return 是否成功
     */
    public boolean completeTransfer(String transferId, String expectedMd5) {
        TransferSession session = activeTransfers.get(transferId);
        if (session == null) {
            Log.w(TAG, "无效的传输会话: " + transferId);
            return false;
        }

        try {
            // 验证文件大小
            if (session.outputFile.length() != session.fileSize) {
                Log.e(TAG, "文件大小不匹配: 期望 " + session.fileSize + ", 实际 " + session.outputFile.length());
                return false;
            }

            // 如果提供了MD5，进行验证
            if (expectedMd5 != null && !expectedMd5.isEmpty()) {
                String actualMd5 = calculateMD5(session.outputFile);
                if (!expectedMd5.equals(actualMd5)) {
                    Log.e(TAG, "MD5不匹配: 期望 " + expectedMd5 + ", 实际 " + actualMd5);
                    session.outputFile.delete();
                    return false;
                }
            }

            session.completed = true;
            session.md5 = expectedMd5;

            Log.i(TAG, "文件传输完成: " + session.fileName + " -> " + session.filePath);

            return true;

        } catch (Exception e) {
            Log.e(TAG, "完成传输失败", e);
            return false;
        } finally {
            activeTransfers.remove(transferId);
        }
    }

    /**
     * 取消传输
     */
    public void cancelTransfer(String transferId) {
        TransferSession session = activeTransfers.remove(transferId);
        if (session != null) {
            if (session.outputFile != null && session.outputFile.exists()) {
                session.outputFile.delete();
            }
            Log.i(TAG, "传输已取消: " + transferId);
        }
    }

    /**
     * 获取传输会话
     */
    public TransferSession getSession(String transferId) {
        return activeTransfers.get(transferId);
    }

    /**
     * 计算文件MD5
     */
    private String calculateMD5(File file) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            java.io.FileInputStream fis = new java.io.FileInputStream(file);
            byte[] buffer = new byte[8192];
            int bytesRead;

            while ((bytesRead = fis.read(buffer)) != -1) {
                md.update(buffer, 0, bytesRead);
            }

            fis.close();

            byte[] digest = md.digest();
            java.math.BigInteger bigInt = new java.math.BigInteger(1, digest);
            return bigInt.toString(16);
        } catch (Exception e) {
            Log.e(TAG, "计算MD5失败", e);
            return "";
        }
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
     * 从输入流读取文件数据
     *
     * @param inputStream 输入流
     * @param session 传输会话
     * @param listener 进度监听器
     * @return 是否成功
     */
    public boolean receiveFile(InputStream inputStream, TransferSession session,
                                 FileTransferProgressListener listener) {
        try {
            DataInputStream dis = new DataInputStream(inputStream);
            FileOutputStream fos = new FileOutputStream(session.outputFile);
            BufferedOutputStream bos = new BufferedOutputStream(fos);

            byte[] buffer = new byte[BUFFER_SIZE];
            long totalReceived = 0;
            int bytesRead;

            while ((bytesRead = dis.read(buffer)) != -1 && totalReceived < session.fileSize) {
                bos.write(buffer, 0, bytesRead);
                totalReceived += bytesRead;
                session.bytesReceived = totalReceived;

                // 通知进度
                if (listener != null) {
                    int progress = session.getProgress();
                    listener.onProgress(progress, totalReceived, session.fileSize);
                }

                Log.d(TAG, "接收: " + session.getProgress() + "%");
            }

            bos.flush();
            bos.close();

            // 验证完整性
            if (session.outputFile.length() != session.fileSize) {
                Log.e(TAG, "文件大小不匹配");
                return false;
            }

            session.completed = true;
            Log.i(TAG, "文件接收完成: " + session.fileName);

            return true;

        } catch (IOException e) {
            Log.e(TAG, "接收文件失败", e);
            return false;
        }
    }

    /**
     * 进度监听器
     */
    public interface FileTransferProgressListener {
        void onProgress(int progress, long bytesReceived, long totalBytes);
    }
}
