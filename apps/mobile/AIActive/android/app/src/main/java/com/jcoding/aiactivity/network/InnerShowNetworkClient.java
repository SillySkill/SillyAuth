package com.jcoding.aiactivity.network;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.jcoding.aiactivity.entity.InnerShowModule;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 内场秀网络客户端
 *
 * 运行在控制器设备上，连接到内场秀设备并发送控制命令
 *
 * 功能：
 * 1. 连接到内场秀服务器
 * 2. 服务器密码认证
 * 3. 发送播放控制命令
 * 4. 发送媒体管理命令
 * 5. 接收服务器状态推送
 * 6. 自动重连机制
 */
public class InnerShowNetworkClient {

    private static final String TAG = "InnerShowNetworkClient";
    private static InnerShowNetworkClient instance;

    private Context context;

    // 连接配置
    private String serverHost;
    private int serverPort = 8888;
    private String serverPassword;
    private Socket socket;
    private BufferedReader in;
    private PrintWriter out;

    // 连接状态
    private boolean isConnected = false;
    private boolean isAuthenticated = false;
    private boolean shouldReconnect = false;

    // 线程
    private ExecutorService executorService;
    private Handler mainHandler;

    // 重连
    private static final int RECONNECT_INTERVAL = 5000;  // 5秒
    private static final int MAX_RECONNECT_ATTEMPTS = 10;
    private int reconnectAttempts = 0;

    // 回调
    private ClientCallback callback;

    private InnerShowNetworkClient(Context context) {
        this.context = context.getApplicationContext();
        this.executorService = Executors.newSingleThreadExecutor();
        this.mainHandler = new Handler(Looper.getMainLooper());
    }

    public static synchronized InnerShowNetworkClient getInstance(Context context) {
        if (instance == null) {
            instance = new InnerShowNetworkClient(context);
        }
        return instance;
    }

    /**
     * 连接到服务器
     */
    public void connect(String host, int port, String password) {
        this.serverHost = host;
        this.serverPort = port;
        this.serverPassword = password;

        disconnect();  // 先断开现有连接

        executorService.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    Log.i(TAG, "正在连接服务器: " + serverHost + ":" + serverPort);

                    socket = new Socket(serverHost, serverPort);
                    in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    out = new PrintWriter(socket.getOutputStream(), true);

                    isConnected = true;
                    reconnectAttempts = 0;

                    Log.i(TAG, "已连接到服务器");

                    mainHandler.post(new Runnable() {
                        @Override
                        public void run() {
                            if (callback != null) {
                                callback.onConnected();
                            }
                        }
                    });

                    // 立即进行认证
                    authenticate();

                    // 启动接收线程
                    startReceiving();

                } catch (IOException e) {
                    Log.e(TAG, "连接服务器失败", e);
                    isConnected = false;
                    isAuthenticated = false;

                    mainHandler.post(new Runnable() {
                        @Override
                        public void run() {
                            if (callback != null) {
                                callback.onError("连接失败: " + e.getMessage());
                            }
                        }
                    });

                    // 尝试重连
                    if (shouldReconnect) {
                        scheduleReconnect();
                    }
                }
            }
        });
    }

    /**
     * 认证
     */
    private void authenticate() {
        if (!isConnected) {
            return;
        }

        try {
            StringBuilder sb = new StringBuilder();
            sb.append("COMMAND:auth\n");
            sb.append("password:").append(serverPassword).append("\n");

            sendCommand(sb.toString());

            Log.i(TAG, "已发送认证请求");

        } catch (Exception e) {
            Log.e(TAG, "认证失败", e);
        }
    }

    /**
     * 启动接收线程
     */
    private void startReceiving() {
        executorService.execute(new Runnable() {
            @Override
            public void run() {
                String line;
                try {
                    while (isConnected && (line = in.readLine()) != null) {
                        Log.d(TAG, "收到消息: " + line);
                        handleMessage(line);
                    }
                } catch (IOException e) {
                    if (isConnected) {
                        Log.e(TAG, "接收消息失败", e);
                        mainHandler.post(new Runnable() {
                            @Override
                            public void run() {
                                if (callback != null) {
                                    callback.onError("接收失败: " + e.getMessage());
                                }
                            }
                        });
                    }
                } finally {
                    if (isConnected) {
                        disconnect();
                        if (shouldReconnect) {
                            scheduleReconnect();
                        }
                    }
                }
            }
        });
    }

    /**
     * 处理收到的消息
     */
    private void handleMessage(String message) {
        if (message.startsWith("OK:")) {
            // 成功响应
            String msg = message.substring(3);
            Log.i(TAG, "操作成功: " + msg);

            if (msg.contains("认证成功")) {
                isAuthenticated = true;
                mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        if (callback != null) {
                            callback.onAuthenticated();
                        }
                    }
                });
            }

            mainHandler.post(new Runnable() {
                @Override
                public void run() {
                    if (callback != null) {
                        callback.onSuccess(msg);
                    }
                }
            });

        } else if (message.startsWith("ERROR:")) {
            // 错误响应
            String error = message.substring(6);
            Log.e(TAG, "操作失败: " + error);

            if (error.contains("密码错误")) {
                isAuthenticated = false;
                disconnect();

                mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        if (callback != null) {
                            callback.onAuthFailed(error);
                        }
                    }
                });

                // 不重连（密码错误）
                shouldReconnect = false;

            } else {
                mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        if (callback != null) {
                            callback.onError(error);
                        }
                    }
                });
            }

        } else if (message.startsWith("COMMAND:")) {
            // 服务器推送的命令
            String command = message.substring(8).trim();

            if (command.equals("status")) {
                handleStatusUpdate(message);
            } else if (command.equals("media_status")) {
                handleMediaStatusUpdate(message);
            }
        }
    }

    /**
     * 处理状态更新
     */
    private void handleStatusUpdate(String message) {
        try {
            boolean isPlaying = Boolean.parseBoolean(extractField(message, "isPlaying"));
            boolean isPaused = Boolean.parseBoolean(extractField(message, "isPaused"));
            int currentIndex = Integer.parseInt(extractField(message, "currentIndex"));
            int currentProgress = Integer.parseInt(extractField(message, "currentProgress"));
            int totalProgress = Integer.parseInt(extractField(message, "totalProgress"));
            String currentProgram = extractField(message, "currentProgram");

            final PlaybackStatus status = new PlaybackStatus(isPlaying, isPaused, currentIndex,
                    currentProgress, totalProgress, currentProgram);

            mainHandler.post(new Runnable() {
                @Override
                public void run() {
                    if (callback != null) {
                        callback.onPlaybackStatusChanged(status);
                    }
                }
            });

        } catch (Exception e) {
            Log.e(TAG, "解析状态更新失败", e);
        }
    }

    /**
     * 处理媒体状态更新
     */
    private void handleMediaStatusUpdate(String message) {
        try {
            String moduleId = extractField(message, "module");
            InnerShowModule module = InnerShowModule.fromId(moduleId);
            String background = extractField(message, "background");
            String music = extractField(message, "music");
            String sticker = extractField(message, "sticker");

            final MediaStatus status = new MediaStatus(module, background, music, sticker);

            mainHandler.post(new Runnable() {
                @Override
                public void run() {
                    if (callback != null) {
                        callback.onMediaStatusChanged(status);
                    }
                }
            });

        } catch (Exception e) {
            Log.e(TAG, "解析媒体状态失败", e);
        }
    }

    /**
     * 提取字段
     */
    private String extractField(String message, String key) {
        String[] lines = message.split("\n");
        for (String line : lines) {
            if (line.startsWith(key + ":")) {
                return line.substring(key.length() + 1);
            }
        }
        return "";
    }

    /**
     * 发送命令
     */
    private void sendCommand(String command) {
        if (!isConnected || out == null) {
            Log.w(TAG, "未连接到服务器，无法发送命令");
            return;
        }

        out.print(command);
        out.flush();

        Log.d(TAG, "发送命令: " + command.trim());
    }

    /**
     * 安排重连
     */
    private void scheduleReconnect() {
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            Log.w(TAG, "已达到最大重连次数");
            shouldReconnect = false;

            mainHandler.post(new Runnable() {
                @Override
                public void run() {
                    if (callback != null) {
                        callback.onError("连接失败，已达到最大重连次数");
                    }
                }
            });

            return;
        }

        reconnectAttempts++;

        Log.i(TAG, "将在 " + RECONNECT_INTERVAL / 1000 + " 秒后重连 (尝试 " + reconnectAttempts + "/" + MAX_RECONNECT_ATTEMPTS + ")");

        mainHandler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (shouldReconnect) {
                    connect(serverHost, serverPort, serverPassword);
                }
            }
        }, RECONNECT_INTERVAL);
    }

    /**
     * 断开连接
     */
    public void disconnect() {
        isConnected = false;
        isAuthenticated = false;

        try {
            if (in != null) in.close();
            if (out != null) out.close();
            if (socket != null && !socket.isClosed()) socket.close();

            Log.i(TAG, "已断开连接");

            mainHandler.post(new Runnable() {
                @Override
                public void run() {
                    if (callback != null) {
                        callback.onDisconnected();
                    }
                }
            });

        } catch (IOException e) {
            Log.e(TAG, "断开连接失败", e);
        }
    }

    /**
     * 启用自动重连
     */
    public void enableAutoReconnect() {
        this.shouldReconnect = true;
    }

    /**
     * 禁用自动重连
     */
    public void disableAutoReconnect() {
        this.shouldReconnect = false;
    }

    // ==================== 控制命令 ====================

    /**
     * 播放
     */
    public void play() {
        sendCommand("COMMAND:play\n");
    }

    /**
     * 暂停
     */
    public void pause() {
        sendCommand("COMMAND:pause\n");
    }

    /**
     * 恢复
     */
    public void resume() {
        sendCommand("COMMAND:resume\n");
    }

    /**
     * 停止
     */
    public void stop() {
        sendCommand("COMMAND:stop\n");
    }

    /**
     * 跳转
     */
    public void jumpTo(int index) {
        sendCommand("COMMAND:jump\nindex:" + index + "\n");
    }

    /**
     * 启用媒体
     */
    public void enableMedia(InnerShowModule module, String type, String path) {
        StringBuilder sb = new StringBuilder();
        sb.append("COMMAND:media_enable\n");
        sb.append("module:").append(module.getId()).append("\n");
        sb.append("type:").append(type).append("\n");
        sb.append("path:").append(path).append("\n");

        sendCommand(sb.toString());
    }

    /**
     * 禁用媒体
     */
    public void disableMedia(InnerShowModule module, String type) {
        StringBuilder sb = new StringBuilder();
        sb.append("COMMAND:media_disable\n");
        sb.append("module:").append(module.getId()).append("\n");
        sb.append("type:").append(type).append("\n");

        sendCommand(sb.toString());
    }

    /**
     * 请求状态
     */
    public void requestStatus() {
        sendCommand("COMMAND:status_request\n");
    }

    // ==================== Getters ====================

    public boolean isConnected() {
        return isConnected;
    }

    public boolean isAuthenticated() {
        return isAuthenticated;
    }

    // ==================== 回调接口 ====================

    public void setClientCallback(ClientCallback callback) {
        this.callback = callback;
    }

    /**
     * 客户端回调接口
     */
    public interface ClientCallback {
        /**
         * 已连接到服务器
         */
        void onConnected();

        /**
         * 认证成功
         */
        void onAuthenticated();

        /**
         * 认证失败
         */
        void onAuthFailed(String error);

        /**
         * 已断开连接
         */
        void onDisconnected();

        /**
         * 操作成功
         */
        void onSuccess(String message);

        /**
         * 播放状态变更
         */
        void onPlaybackStatusChanged(PlaybackStatus status);

        /**
         * 媒体状态变更
         */
        void onMediaStatusChanged(MediaStatus status);

        /**
         * 发生错误
         */
        void onError(String error);
    }

    /**
     * 播放状态
     */
    public static class PlaybackStatus {
        public boolean isPlaying;
        public boolean isPaused;
        public int currentIndex;
        public int currentProgress;
        public int totalProgress;
        public String currentProgram;

        public PlaybackStatus(boolean isPlaying, boolean isPaused, int currentIndex,
                             int currentProgress, int totalProgress, String currentProgram) {
            this.isPlaying = isPlaying;
            this.isPaused = isPaused;
            this.currentIndex = currentIndex;
            this.currentProgress = currentProgress;
            this.totalProgress = totalProgress;
            this.currentProgram = currentProgram;
        }
    }

    /**
     * 媒体状态
     */
    public static class MediaStatus {
        public InnerShowModule module;
        public String background;
        public String music;
        public String sticker;

        public MediaStatus(InnerShowModule module, String background, String music, String sticker) {
            this.module = module;
            this.background = background;
            this.music = music;
            this.sticker = sticker;
        }
    }
}
