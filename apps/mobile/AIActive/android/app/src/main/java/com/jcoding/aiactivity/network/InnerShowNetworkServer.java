package com.jcoding.aiactivity.network;

import android.content.Context;
import android.util.Log;

import com.jcoding.aiactivity.entity.InnerShowModule;
import com.jcoding.aiactivity.entity.ProgramItem;
import com.jcoding.aiactivity.manager.BackgroundMediaManager;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.ProgramPlayerManager;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 内场秀网络服务器
 *
 * 运行在内场秀设备上，接受控制器的连接和控制命令
 *
 * 功能：
 * 1. 监听指定端口，等待控制器连接
 * 2. 验证控制器密码
 * 3. 接收播放控制命令（播放、暂停、停止、跳转）
 * 4. 接收媒体管理命令（上传、启用、禁用）
 * 5. 向控制器推送状态更新
 * 6. 管理多个控制器连接
 */
public class InnerShowNetworkServer {

    private static final String TAG = "InnerShowNetworkServer";
    private static InnerShowNetworkServer instance;

    private Context context;
    private ConfigManager configManager;
    private ProgramPlayerManager playerManager;
    private BackgroundMediaManager mediaManager;
    private BinaryFileReceiver fileReceiver;

    // 服务器配置
    private int serverPort = 8888;  // 默认端口
    private boolean isRunning = false;
    private ServerSocket serverSocket;

    // 线程池
    private ExecutorService threadPool;
    private static final int MAX_THREADS = 10;  // 最多支持10个控制器连接

    // 客户端连接
    private Map<String, ClientHandler> clients = new HashMap<>();  // clientId -> handler

    // 回调接口
    private ServerCallback callback;

    private InnerShowNetworkServer(Context context) {
        this.context = context.getApplicationContext();
        this.configManager = ConfigManager.getInstance(context);
        this.playerManager = ProgramPlayerManager.getInstance(context);
        this.mediaManager = BackgroundMediaManager.getInstance(context);
        this.fileReceiver = new BinaryFileReceiver();
        this.threadPool = Executors.newFixedThreadPool(MAX_THREADS);

        // 从配置加载端口
        loadServerConfig();
    }

    public static synchronized InnerShowNetworkServer getInstance(Context context) {
        if (instance == null) {
            instance = new InnerShowNetworkServer(context);
        }
        return instance;
    }

    /**
     * 加载服务器配置
     */
    private void loadServerConfig() {
        this.serverPort = configManager.getInnerShowServerPort(8888);
        Log.i(TAG, "服务器配置加载完成，端口: " + serverPort);
    }

    /**
     * 启动服务器
     */
    public boolean startServer() {
        if (isRunning) {
            Log.w(TAG, "服务器已在运行");
            return true;
        }

        try {
            serverSocket = new ServerSocket(serverPort);
            isRunning = true;

            Log.i(TAG, "服务器已启动，监听端口: " + serverPort);

            if (callback != null) {
                callback.onServerStarted(serverPort);
            }

            // 启动监听线程
            new Thread(new Runnable() {
                @Override
                public void run() {
                    while (isRunning) {
                        try {
                            Socket clientSocket = serverSocket.accept();
                            Log.i(TAG, "新客户端连接: " + clientSocket.getInetAddress());

                            // 在线程池中处理客户端
                            threadPool.execute(new ClientHandler(clientSocket));

                        } catch (IOException e) {
                            if (isRunning) {
                                Log.e(TAG, "接受客户端连接失败", e);
                            }
                        }
                    }
                }
            }).start();

            return true;

        } catch (IOException e) {
            Log.e(TAG, "启动服务器失败", e);
            if (callback != null) {
                callback.onError("启动服务器失败: " + e.getMessage());
            }
            return false;
        }
    }

    /**
     * 停止服务器
     */
    public void stopServer() {
        if (!isRunning) {
            return;
        }

        isRunning = false;

        // 断开所有客户端
        for (ClientHandler handler : clients.values()) {
            handler.disconnect();
        }
        clients.clear();

        // 关闭服务器socket
        if (serverSocket != null && !serverSocket.isClosed()) {
            try {
                serverSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "关闭服务器socket失败", e);
            }
        }

        // 关闭线程池
        if (threadPool != null && !threadPool.isShutdown()) {
            threadPool.shutdown();
        }

        Log.i(TAG, "服务器已停止");

        if (callback != null) {
            callback.onServerStopped();
        }
    }

    /**
     * 广播消息到所有连接的控制器
     */
    public void broadcast(String message) {
        for (ClientHandler handler : clients.values()) {
            handler.sendMessage(message);
        }
    }

    /**
     * 推送播放状态到所有控制器
     */
    public void pushPlaybackStatus() {
        StringBuilder sb = new StringBuilder();
        sb.append("COMMAND:status\n");
        sb.append("isPlaying:").append(playerManager.isPlaying()).append("\n");
        sb.append("isPaused:").append(playerManager.isPaused()).append("\n");
        sb.append("currentIndex:").append(playerManager.getCurrentIndex()).append("\n");
        sb.append("currentProgress:").append(playerManager.getCurrentProgress()).append("\n");
        sb.append("totalProgress:").append(playerManager.getTotalProgress()).append("\n");

        ProgramItem currentProgram = playerManager.getCurrentProgram();
        if (currentProgram != null) {
            sb.append("currentProgram:").append(currentProgram.getContent()).append("\n");
        }

        broadcast(sb.toString());
    }

    /**
     * 推送媒体资源状态到所有控制器
     */
    public void pushMediaStatus(InnerShowModule module) {
        StringBuilder sb = new StringBuilder();
        sb.append("COMMAND:media_status\n");
        sb.append("module:").append(module.getId()).append("\n");
        sb.append("background:").append(mediaManager.getBackgroundImage(module)).append("\n");
        sb.append("music:").append(mediaManager.getBackgroundMusic(module)).append("\n");

        BackgroundMediaManager.Sticker sticker = mediaManager.getSticker(module);
        if (sticker != null) {
            sb.append("sticker:").append(sticker.getId()).append("\n");
        } else {
            sb.append("sticker:\n");
        }

        broadcast(sb.toString());
    }

    /**
     * 客户端处理器
     */
    private class ClientHandler implements Runnable {
        private Socket socket;
        private BufferedReader in;
        private PrintWriter out;
        private String clientId;
        private boolean authenticated = false;

        public ClientHandler(Socket socket) {
            this.socket = socket;
            this.clientId = socket.getInetAddress().toString() + ":" + socket.getPort();
        }

        @Override
        public void run() {
            try {
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                out = new PrintWriter(socket.getOutputStream(), true);

                String line;
                while ((line = in.readLine()) != null) {
                    Log.d(TAG, "收到消息 [" + clientId + "]: " + line);

                    // 处理消息
                    handleMessage(line);
                }

            } catch (IOException e) {
                Log.e(TAG, "客户端连接异常: " + clientId, e);
            } finally {
                disconnect();
            }
        }

        /**
         * 处理收到的消息
         */
        private void handleMessage(String message) {
            try {
                // 解析命令
                if (message.startsWith("COMMAND:")) {
                    String command = message.substring(8).trim();

                    switch (command) {
                        case "auth":
                            // 认证命令
                            handleAuth(message);
                            break;

                        case "play":
                            // 播放命令
                            handlePlay(message);
                            break;

                        case "pause":
                            // 暂停命令
                            handlePause(message);
                            break;

                        case "resume":
                            // 恢复命令
                            handleResume(message);
                            break;

                        case "stop":
                            // 停止命令
                            handleStop(message);
                            break;

                        case "jump":
                            // 跳转命令
                            handleJump(message);
                            break;

                        case "media_upload":
                            // 媒体上传命令
                            handleMediaUpload(message);
                            break;

                        case "media_enable":
                            // 启用媒体命令
                            handleMediaEnable(message);
                            break;

                        case "media_disable":
                            // 禁用媒体命令
                            handleMediaDisable(message);
                            break;

                        case "status_request":
                            // 状态请求
                            handleStatusRequest();
                            break;

                        default:
                            sendMessage("ERROR:未知命令\n");
                            break;
                    }
                }

            } catch (Exception e) {
                Log.e(TAG, "处理消息失败", e);
                sendMessage("ERROR:" + e.getMessage() + "\n");
            }
        }

        /**
         * 处理认证
         */
        private void handleAuth(String message) {
            try {
                String password = extractParameter(message, "password");

                // 验证密码
                String serverPassword = configManager.getInnerShowServerPassword();
                if (serverPassword == null || serverPassword.isEmpty()) {
                    serverPassword = "123456";  // 默认密码
                }

                if (serverPassword.equals(password)) {
                    authenticated = true;
                    clients.put(clientId, this);

                    sendMessage("OK:认证成功\n");
                    Log.i(TAG, "客户端认证成功: " + clientId);

                    if (callback != null) {
                        callback.onClientConnected(clientId);
                    }

                    // 推送当前状态
                    pushPlaybackStatus();

                } else {
                    sendMessage("ERROR:密码错误\n");
                    Log.w(TAG, "客户端认证失败: " + clientId);
                }

            } catch (Exception e) {
                Log.e(TAG, "处理认证失败", e);
                sendMessage("ERROR:认证失败\n");
            }
        }

        /**
         * 处理播放命令
         */
        private void handlePlay(String message) {
            if (!checkAuth()) return;

            playerManager.play();
            sendMessage("OK:播放开始\n");

            if (callback != null) {
                callback.onPlaybackCommand("play", null);
            }
        }

        /**
         * 处理暂停命令
         */
        private void handlePause(String message) {
            if (!checkAuth()) return;

            playerManager.pause();
            sendMessage("OK:已暂停\n");

            if (callback != null) {
                callback.onPlaybackCommand("pause", null);
            }
        }

        /**
         * 处理恢复命令
         */
        private void handleResume(String message) {
            if (!checkAuth()) return;

            playerManager.resume();
            sendMessage("OK:已恢复\n");

            if (callback != null) {
                callback.onPlaybackCommand("resume", null);
            }
        }

        /**
         * 处理停止命令
         */
        private void handleStop(String message) {
            if (!checkAuth()) return;

            playerManager.stop();
            sendMessage("OK:已停止\n");

            if (callback != null) {
                callback.onPlaybackCommand("stop", null);
            }
        }

        /**
         * 处理跳转命令
         */
        private void handleJump(String message) {
            if (!checkAuth()) return;

            try {
                int index = Integer.parseInt(extractParameter(message, "index"));
                playerManager.jumpTo(index);
                sendMessage("OK:已跳转到第" + (index + 1) + "个节目\n");

                if (callback != null) {
                    callback.onPlaybackCommand("jump", index);
                }

            } catch (Exception e) {
                sendMessage("ERROR:跳转失败\n");
            }
        }

        /**
         * 处理媒体上传命令
         * 协议：
         * COMMAND:media_upload
         * module:warmup
         * type:background
         * filename:test.jpg
         * filesize:102400
         * md5:abc123...
         * <binary data>
         */
        private void handleMediaUpload(String message) {
            if (!checkAuth()) return;

            try {
                // 提取参数
                String moduleStr = extractParameter(message, "module");
                String type = extractParameter(message, "type");
                String fileName = extractParameter(message, "filename");
                String fileSizeStr = extractParameter(message, "filesize");
                String md5 = extractParameter(message, "md5");

                if (moduleStr == null || type == null || fileName == null || fileSizeStr == null) {
                    sendMessage("ERROR:缺少必要参数\n");
                    return;
                }

                long fileSize;
                try {
                    fileSize = Long.parseLong(fileSizeStr);
                } catch (NumberFormatException e) {
                    sendMessage("ERROR:文件大小格式错误\n");
                    return;
                }

                // 创建保存目录
                java.io.File saveDir = new java.io.File(context.getExternalFilesDir(null), "media/" + moduleStr);
                String transferId = "upload_" + System.currentTimeMillis();

                // 开始传输会话
                BinaryFileReceiver.TransferSession session =
                    fileReceiver.startTransfer(transferId, fileName, fileSize, saveDir);

                // 告诉客户端准备接收
                sendMessage("OK:READY_TO_RECEIVE\n" +
                           "transfer_id:" + transferId + "\n");

                // 启动二进制接收线程
                new Thread(() -> receiveBinaryFile(session, moduleStr, type, md5)).start();

                Log.i(TAG, "开始接收文件: " + fileName + " (" + fileSize + " bytes)");

            } catch (Exception e) {
                Log.e(TAG, "处理上传命令失败", e);
                sendMessage("ERROR:" + e.getMessage() + "\n");
            }
        }

        /**
         * 接收二进制文件
         */
        private void receiveBinaryFile(BinaryFileReceiver.TransferSession session,
                                       String moduleStr, String type, String expectedMd5) {
            try {
                // 获取socket的输入流
                DataInputStream dis = new DataInputStream(socket.getInputStream());

                // 使用fileReceiver接收文件
                boolean success = fileReceiver.receiveFile(dis, session,
                    new BinaryFileReceiver.FileTransferProgressListener() {
                        @Override
                        public void onProgress(int progress, long bytesReceived, long totalBytes) {
                            // 推送进度到控制器
                            sendMessage("EVENT:progress\n" +
                                       "percent:" + progress + "\n" +
                                       "received:" + bytesReceived + "\n" +
                                       "total:" + totalBytes + "\n");
                        }
                    });

                if (success) {
                    // 验证MD5
                    if (expectedMd5 != null && !expectedMd5.isEmpty()) {
                        if (!fileReceiver.completeTransfer(session.transferId, expectedMd5)) {
                            sendMessage("ERROR:MD5校验失败\n");
                            return;
                        }
                    } else {
                        fileReceiver.completeTransfer(session.transferId, null);
                    }

                    // 应用媒体
                    InnerShowModule module = InnerShowModule.fromId(moduleStr);
                    if (module != null) {
                        applyUploadedMedia(module, type, session.filePath);
                    }

                    sendMessage("OK:文件上传成功\n" +
                               "path:" + session.filePath + "\n");

                    Log.i(TAG, "文件上传成功: " + session.fileName);

                } else {
                    fileReceiver.cancelTransfer(session.transferId);
                    sendMessage("ERROR:文件接收失败\n");
                }

            } catch (IOException e) {
                Log.e(TAG, "接收文件失败", e);
                fileReceiver.cancelTransfer(session.transferId);
                try {
                    sendMessage("ERROR:" + e.getMessage() + "\n");
                } catch (Exception ex) {
                    // 忽略
                }
            }
        }

        /**
         * 应用上传的媒体
         */
        private void applyUploadedMedia(InnerShowModule module, String type, String filePath) {
            switch (type) {
                case "background":
                    mediaManager.setBackgroundImage(module, filePath);
                    break;
                case "video":
                    mediaManager.setBackgroundVideo(module, filePath);
                    break;
                case "music":
                    mediaManager.setBackgroundMusic(module, filePath);
                    break;
                case "sticker":
                    mediaManager.setSticker(module, filePath);
                    break;
            }

            // 通知回调
            if (callback != null) {
                callback.onMediaChanged(module, type, filePath, true);
            }
        }

        /**
         * 处理启用媒体命令
         */
        private void handleMediaEnable(String message) {
            if (!checkAuth()) return;

            try {
                String moduleStr = extractParameter(message, "module");
                String type = extractParameter(message, "type");  // background/music/sticker
                String path = extractParameter(message, "path");

                InnerShowModule module = InnerShowModule.fromId(moduleStr);

                if (module != null) {
                    switch (type) {
                        case "background":
                            mediaManager.setBackgroundImage(module, path);
                            break;
                        case "music":
                            mediaManager.setBackgroundMusic(module, path);
                            break;
                        case "sticker":
                            mediaManager.setSticker(module, path);
                            break;
                    }

                    sendMessage("OK:媒体已启用\n");

                    if (callback != null) {
                        callback.onMediaChanged(module, type, path, true);
                    }

                } else {
                    sendMessage("ERROR:无效的模块\n");
                }

            } catch (Exception e) {
                Log.e(TAG, "启用媒体失败", e);
                sendMessage("ERROR:启用失败\n");
            }
        }

        /**
         * 处理禁用媒体命令
         */
        private void handleMediaDisable(String message) {
            if (!checkAuth()) return;

            try {
                String moduleStr = extractParameter(message, "module");
                String type = extractParameter(message, "type");

                InnerShowModule module = InnerShowModule.fromId(moduleStr);

                if (module != null) {
                    switch (type) {
                        case "sticker":
                            mediaManager.removeSticker(module);
                            break;
                    }

                    sendMessage("OK:媒体已禁用\n");

                    if (callback != null) {
                        callback.onMediaChanged(module, type, null, false);
                    }

                } else {
                    sendMessage("ERROR:无效的模块\n");
                }

            } catch (Exception e) {
                Log.e(TAG, "禁用媒体失败", e);
                sendMessage("ERROR:禁用失败\n");
            }
        }

        /**
         * 处理状态请求
         */
        private void handleStatusRequest() {
            if (!checkAuth()) return;

            pushPlaybackStatus();
            // 推送所有模块的媒体状态
            for (InnerShowModule module : InnerShowModule.values()) {
                pushMediaStatus(module);
            }
        }

        /**
         * 检查认证状态
         */
        private boolean checkAuth() {
            if (!authenticated) {
                sendMessage("ERROR:未认证\n");
                return false;
            }
            return true;
        }

        /**
         * 提取参数
         */
        private String extractParameter(String message, String key) {
            String[] lines = message.split("\n");
            for (String line : lines) {
                if (line.startsWith(key + ":")) {
                    return line.substring(key.length() + 1);
                }
            }
            return "";
        }

        /**
         * 发送消息
         */
        public void sendMessage(String message) {
            if (out != null) {
                out.print(message);
                out.flush();
            }
        }

        /**
         * 断开连接
         */
        public void disconnect() {
            try {
                if (in != null) in.close();
                if (out != null) out.close();
                if (socket != null && !socket.isClosed()) socket.close();

                clients.remove(clientId);

                Log.i(TAG, "客户端断开连接: " + clientId);

                if (callback != null) {
                    callback.onClientDisconnected(clientId);
                }

            } catch (IOException e) {
                Log.e(TAG, "断开连接失败", e);
            }
        }
    }

    // ==================== Getters ====================

    public boolean isRunning() {
        return isRunning;
    }

    public int getServerPort() {
        return serverPort;
    }

    public int getConnectedClientsCount() {
        return clients.size();
    }

    // ==================== 回调接口 ====================

    public void setServerCallback(ServerCallback callback) {
        this.callback = callback;
    }

    /**
     * 服务器回调接口
     */
    public interface ServerCallback {
        /**
         * 服务器已启动
         */
        void onServerStarted(int port);

        /**
         * 服务器已停止
         */
        void onServerStopped();

        /**
         * 客户端已连接
         */
        void onClientConnected(String clientId);

        /**
         * 客户端已断开
         */
        void onClientDisconnected(String clientId);

        /**
         * 播放控制命令
         */
        void onPlaybackCommand(String command, Object parameter);

        /**
         * 媒体变更
         */
        void onMediaChanged(InnerShowModule module, String type, String path, boolean enabled);

        /**
         * 发生错误
         */
        void onError(String error);
    }
}
