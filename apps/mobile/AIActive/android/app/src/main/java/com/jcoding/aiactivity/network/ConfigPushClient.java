package com.jcoding.aiactivity.network;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.jcoding.aiactivity.manager.ConfigSyncManager;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import okio.ByteString;

/**
 * 配置推送 WebSocket 客户端
 * 连接到服务器，接收配置推送通知，支持断线重连和消息确认
 */
public class ConfigPushClient {

    private static final String TAG = "ConfigPushClient";

    // WebSocket 配置
    private static final String WS_SCHEME = "wss://";
    private static final String WS_PATH = "/ws";
    private static final int CONNECT_TIMEOUT = 10;
    private static final int READ_TIMEOUT = 60;
    private static final int HEARTBEAT_INTERVAL = 30; // 心跳间隔（秒）
    private static final int RECONNECT_DELAY = 5; // 重连延迟（秒）
    private static final int MAX_RECONNECT_ATTEMPTS = 10;

    // 消息类型
    private static final String MSG_CONNECTED = "connected";
    private static final String MSG_CONFIG_UPDATE = "config_update";
    private static final String MSG_HEARTBEAT_ACK = "heartbeat_ack";
    private static final String MSG_ERROR = "error";

    private static ConfigPushClient instance;

    private final Context context;
    private final String deviceId;
    private final String serverUrl;
    private final Handler mainHandler;

    private OkHttpClient httpClient;
    private WebSocket webSocket;
    private WebSocketListener wsListener;

    // 连接状态
    private volatile boolean isConnected = false;
    private volatile boolean shouldReconnect = true;
    private int reconnectAttempts = 0;
    private String currentSid;

    // 心跳
    private final Handler heartbeatHandler;
    private final Runnable heartbeatRunnable;

    // 配置更新回调
    private ConfigUpdateCallback configUpdateCallback;

    /**
     * 获取单例实例
     */
    public static synchronized ConfigPushClient getInstance(Context context) {
        if (instance == null) {
            instance = new ConfigPushClient(context.getApplicationContext());
        }
        return instance;
    }

    private ConfigPushClient(Context context) {
        this.context = context;
        this.deviceId = getDeviceId();
        this.serverUrl = buildServerUrl();
        this.mainHandler = new Handler(Looper.getMainLooper());
        this.heartbeatHandler = new Handler(Looper.getMainLooper());

        // 配置 HTTP 客户端
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(CONNECT_TIMEOUT, TimeUnit.SECONDS)
                .readTimeout(READ_TIMEOUT, TimeUnit.SECONDS)
                .writeTimeout(CONNECT_TIMEOUT, TimeUnit.SECONDS)
                .pingInterval(30, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build();

        // 心跳任务
        this.heartbeatRunnable = new Runnable() {
            @Override
            public void run() {
                if (isConnected) {
                    sendHeartbeat();
                    heartbeatHandler.postDelayed(this, HEARTBEAT_INTERVAL * 1000);
                }
            }
        };

        // 创建 WebSocket 监听器
        createWebSocketListener();

        Log.d(TAG, "配置推送客户端初始化完成");
    }

    /**
     * 连接到服务器
     */
    public void connect() {
        if (isConnected) {
            Log.w(TAG, "已经连接，无需重复连接");
            return;
        }

        shouldReconnect = true;
        reconnectAttempts = 0;

        Log.i(TAG, "开始连接到服务器: " + serverUrl);

        // 构建请求 URL（包含认证参数）
        String url = buildWebSocketUrl();

        Request request = new Request.Builder()
                .url(url)
                .build();

        // 发起连接
        webSocket = httpClient.newWebSocket(request, wsListener);
    }

    /**
     * 断开连接
     */
    public void disconnect() {
        shouldReconnect = false;
        isConnected = false;

        // 停止心跳
        heartbeatHandler.removeCallbacks(heartbeatRunnable);

        if (webSocket != null) {
            webSocket.close(1000, "客户端主动断开");
            webSocket = null;
        }

        Log.i(TAG, "已断开连接");
    }

    /**
     * 设置配置更新回调
     */
    public void setConfigUpdateCallback(ConfigUpdateCallback callback) {
        this.configUpdateCallback = callback;
    }

    /**
     * 创建 WebSocket 监听器
     */
    private void createWebSocketListener() {
        wsListener = new WebSocketListener() {
            @Override
            public void onOpen(WebSocket webSocket, Response response) {
                Log.i(TAG, "WebSocket 连接已建立");
                isConnected = true;
                reconnectAttempts = 0;

                // 启动心跳
                heartbeatHandler.post(heartbeatRunnable);

                // 通知连接成功
                notifyConnected();
            }

            @Override
            public void onMessage(WebSocket webSocket, String text) {
                Log.d(TAG, "收到消息: " + text);
                handleMessage(text);
            }

            @Override
            public void onMessage(WebSocket webSocket, ByteString bytes) {
                Log.d(TAG, "收到二进制消息: " + bytes.hex());
            }

            @Override
            public void onClosing(WebSocket webSocket, int code, String reason) {
                Log.w(TAG, "WebSocket 正在关闭: " + code + ", " + reason);
            }

            @Override
            public void onClosed(WebSocket webSocket, int code, String reason) {
                Log.i(TAG, "WebSocket 已关闭: " + code + ", " + reason);
                isConnected = false;

                // 停止心跳
                heartbeatHandler.removeCallbacks(heartbeatRunnable);

                // 通知断开连接
                notifyDisconnected(code, reason);

                // 尝试重连
                if (shouldReconnect) {
                    scheduleReconnect();
                }
            }

            @Override
            public void onFailure(WebSocket webSocket, Throwable t, Response response) {
                Log.e(TAG, "WebSocket 连接失败", t);
                isConnected = false;

                // 停止心跳
                heartbeatHandler.removeCallbacks(heartbeatRunnable);

                // 通知连接失败
                notifyError(t.getMessage());

                // 尝试重连
                if (shouldReconnect) {
                    scheduleReconnect();
                }
            }
        };
    }

    /**
     * 处理收到的消息
     */
    private void handleMessage(String message) {
        try {
            JSONObject json = new JSONObject(message);
            String type = json.keys().next();

            if (type.equals(MSG_CONNECTED)) {
                handleConnected(json.getJSONObject(type));
            } else if (type.equals(MSG_CONFIG_UPDATE)) {
                handleConfigUpdate(json.getJSONObject(type));
            } else if (type.equals(MSG_HEARTBEAT_ACK)) {
                handleHeartbeatAck(json.getJSONObject(type));
            } else if (type.equals(MSG_ERROR)) {
                handleError(json.getJSONObject(type));
            } else {
                Log.w(TAG, "未知消息类型: " + type);
            }

        } catch (JSONException e) {
            Log.e(TAG, "解析消息失败", e);
        }
    }

    /**
     * 处理连接确认
     */
    private void handleConnected(JSONObject data) throws JSONException {
        currentSid = data.getString("sid");
        String serverTime = data.optString("server_time");

        Log.i(TAG, "连接确认: sid=" + currentSid + ", serverTime=" + serverTime);

        notifyConnected();
    }

    /**
     * 处理配置更新
     */
    private void handleConfigUpdate(JSONObject data) throws JSONException {
        String pushId = data.getString("push_id");
        String version = data.getString("version");
        int versionCode = data.getInt("version_code");
        boolean forceUpdate = data.optBoolean("force_update", false);
        String releaseNotes = data.optString("release_notes", "");
        JSONArray filesArray = data.getJSONArray("files");

        Log.i(TAG, String.format("收到配置推送: pushId=%s, version=%s (%d), force=%b",
                pushId, version, versionCode, forceUpdate));

        // 通知回调
        if (configUpdateCallback != null) {
            mainHandler.post(() -> {
                configUpdateCallback.onConfigUpdate(pushId, version, versionCode,
                        forceUpdate, releaseNotes, filesArray);
            });
        }
    }

    /**
     * 处理心跳确认
     */
    private void handleHeartbeatAck(JSONObject data) throws JSONException {
        String serverTime = data.getString("server_time");
        Log.d(TAG, "心跳确认: serverTime=" + serverTime);
    }

    /**
     * 处理错误消息
     */
    private void handleError(JSONObject data) throws JSONException {
        int code = data.getInt("code");
        String message = data.getString("message");

        Log.e(TAG, "服务器错误: " + code + ", " + message);

        notifyError("服务器错误: " + message);
    }

    /**
     * 发送心跳
     */
    private void sendHeartbeat() {
        try {
            JSONObject data = new JSONObject();
            data.put("client_time", System.currentTimeMillis());

            JSONObject message = new JSONObject();
            message.put("heartbeat", data);

            if (webSocket != null) {
                webSocket.send(message.toString());
                Log.d(TAG, "心跳已发送");
            }

        } catch (JSONException e) {
            Log.e(TAG, "构造心跳消息失败", e);
        }
    }

    /**
     * 发送配置确认
     */
    public void sendConfigAck(String pushId, boolean success, String message,
                              String[] receivedFiles, String[] failedFiles) {
        if (!isConnected) {
            Log.w(TAG, "未连接，无法发送确认");
            return;
        }

        try {
            JSONObject data = new JSONObject();
            data.put("push_id", pushId);
            data.put("status", success ? "success" : "failed");
            data.put("message", message);

            if (receivedFiles != null) {
                data.put("received_files", new JSONArray(receivedFiles));
            }

            if (failedFiles != null) {
                data.put("failed_files", new JSONArray(failedFiles));
            }

            JSONObject json = new JSONObject();
            json.put("config_ack", data);

            if (webSocket != null) {
                webSocket.send(json.toString());
                Log.i(TAG, "配置确认已发送: pushId=" + pushId + ", status=" + (success ? "success" : "failed"));
            }

        } catch (JSONException e) {
            Log.e(TAG, "构造确认消息失败", e);
        }
    }

    /**
     * 上报设备状态
     */
    public void reportDeviceStatus(Map<String, Object> status) {
        if (!isConnected) {
            Log.w(TAG, "未连接，无法上报状态");
            return;
        }

        try {
            JSONObject data = new JSONObject();
            for (Map.Entry<String, Object> entry : status.entrySet()) {
                data.put(entry.getKey(), entry.getValue());
            }

            JSONObject json = new JSONObject();
            json.put("device_status", data);

            if (webSocket != null) {
                webSocket.send(json.toString());
                Log.d(TAG, "设备状态已上报");
            }

        } catch (JSONException e) {
            Log.e(TAG, "构造状态消息失败", e);
        }
    }

    /**
     * 安排重连
     */
    private void scheduleReconnect() {
        if (!shouldReconnect || reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            Log.e(TAG, "达到最大重连次数，停止重连");
            return;
        }

        reconnectAttempts++;
        int delay = RECONNECT_DELAY * reconnectAttempts;

        Log.i(TAG, String.format("将在 %d 秒后进行第 %d 次重连", delay, reconnectAttempts));

        mainHandler.postDelayed(() -> {
            if (shouldReconnect) {
                Log.i(TAG, "开始重连...");
                connect();
            }
        }, delay * 1000);
    }

    /**
     * 通知连接成功
     */
    private void notifyConnected() {
        if (configUpdateCallback != null) {
            mainHandler.post(() -> configUpdateCallback.onConnected());
        }
    }

    /**
     * 通知断开连接
     */
    private void notifyDisconnected(int code, String reason) {
        if (configUpdateCallback != null) {
            mainHandler.post(() -> configUpdateCallback.onDisconnected(code, reason));
        }
    }

    /**
     * 通知错误
     */
    private void notifyError(String error) {
        if (configUpdateCallback != null) {
            mainHandler.post(() -> configUpdateCallback.onError(error));
        }
    }

    /**
     * 构建服务器 URL
     */
    private String buildServerUrl() {
        // 从配置或 API 服务获取服务器地址
        // 这里简化为硬编码，实际应该从配置文件读取
        return "api.jcoding.tech";
    }

    /**
     * 构建 WebSocket URL
     */
    private String buildWebSocketUrl() {
        // 获取 token（这里简化处理，实际应该从认证管理器获取）
        String token = getAuthToken();

        return String.format("%s%s%s?device_id=%s&token=%s",
                WS_SCHEME, serverUrl, WS_PATH, deviceId, token);
    }

    /**
     * 获取设备 ID
     */
    private String getDeviceId() {
        return android.provider.Settings.Secure.getString(
                context.getContentResolver(),
                android.provider.Settings.Secure.ANDROID_ID
        );
    }

    /**
     * 获取认证 Token
     */
    private String getAuthToken() {
        // TODO: 从 UserLoginManager 或其他认证管理器获取 token
        // 这里返回一个临时 token
        return "temp_token_" + deviceId;
    }

    /**
     * 检查连接状态
     */
    public boolean isConnected() {
        return isConnected && webSocket != null;
    }

    // ========== 回调接口 ==========

    /**
     * 配置更新回调接口
     */
    public interface ConfigUpdateCallback {
        /**
         * 连接成功
         */
        void onConnected();

        /**
         * 断开连接
         */
        void onDisconnected(int code, String reason);

        /**
         * 收到配置更新
         */
        void onConfigUpdate(String pushId, String version, int versionCode,
                           boolean forceUpdate, String releaseNotes, JSONArray files);

        /**
         * 发生错误
         */
        void onError(String error);
    }
}
