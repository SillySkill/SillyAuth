package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.jcoding.aiactivity.manager.InnerShowDataManager.GenerationResult;
import com.jcoding.aiactivity.manager.InnerShowDataManager.LotteryWinner;
import com.jcoding.aiactivity.manager.InnerShowDataManager.QuizWinner;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;

/**
 * 内场秀网络客户端
 * 用于其他设备连接到内场秀服务器
 */
public class InnerShowNetworkClient {

    private static final String TAG = "InnerShowNetworkClient";
    private static final MediaType JSON_TYPE = MediaType.parse("application/json; charset=utf-8");

    private static InnerShowNetworkClient instance;
    private Context context;
    private InnerShowNetworkConfigManager configManager;
    private Gson gson;

    private OkHttpClient httpClient;
    private WebSocket webSocket;
    private ExecutorService executor;
    private Handler mainHandler;

    private boolean isWebSocketConnected = false;

    private InnerShowNetworkClient(Context context) {
        this.context = context.getApplicationContext();
        this.configManager = InnerShowNetworkConfigManager.getInstance(context);
        this.gson = new Gson();
        this.executor = Executors.newFixedThreadPool(2);
        this.mainHandler = new Handler(Looper.getMainLooper());

        OkHttpClient.Builder builder = new OkHttpClient.Builder();
        httpClient = builder.build();
    }

    public static synchronized InnerShowNetworkClient getInstance(Context context) {
        if (instance == null) {
            instance = new InnerShowNetworkClient(context);
        }
        return instance;
    }

    // ==================== HTTP API调用 ====================

    /**
     * 推送生成结果到内场秀
     */
    public void pushGenerationResult(GenerationResult result, NetworkCallback callback) {
        String url = getServerUrl() + "/api/generations";
        String json = gson.toJson(result);

        postAsync(url, json, callback);
    }

    /**
     * 推送中奖记录到内场秀
     */
    public void pushLotteryWinner(LotteryWinner winner, NetworkCallback callback) {
        String url = getServerUrl() + "/api/lottery-winners";
        String json = gson.toJson(winner);

        postAsync(url, json, callback);
    }

    /**
     * 推送答题中奖记录到内场秀
     */
    public void pushQuizWinner(QuizWinner winner, NetworkCallback callback) {
        String url = getServerUrl() + "/api/quiz-winners";
        String json = gson.toJson(winner);

        postAsync(url, json, callback);
    }

    /**
     * 设置当前显示内容
     */
    public void setCurrentDisplay(String displayId, NetworkCallback callback) {
        String url = getServerUrl() + "/api/current-display";

        JsonObject json = new JsonObject();
        json.addProperty("display_id", displayId);

        postAsync(url, gson.toJson(json), callback);
    }

    /**
     * 获取所有数据
     */
    public void getAllData(NetworkCallback callback) {
        String url = getServerUrl() + "/api/data";
        getAsync(url, callback);
    }

    /**
     * 测试服务器连接
     */
    public void testConnection(NetworkCallback callback) {
        String url = getServerUrl() + "/health";
        getAsync(url, callback);
    }

    // ==================== WebSocket ====================

    /**
     * 连接WebSocket
     */
    public void connectWebSocket(WebSocketMessageListener listener) {
        if (isWebSocketConnected) {
            Log.d(TAG, "WebSocket已连接");
            return;
        }

        String wsUrl = getWebSocketUrl();

        Request request = new Request.Builder()
                .url(wsUrl)
                .build();

        webSocket = httpClient.newWebSocket(request, new WebSocketListener() {
            @Override
            public void onOpen(WebSocket webSocket, Response response) {
                Log.i(TAG, "WebSocket连接成功");
                isWebSocketConnected = true;

                if (listener != null) {
                    mainHandler.post(() -> listener.onConnected());
                }
            }

            @Override
            public void onMessage(WebSocket webSocket, String text) {
                Log.d(TAG, "收到WebSocket消息: " + text);

                if (listener != null) {
                    mainHandler.post(() -> listener.onMessage(text));
                }
            }

            @Override
            public void onClosing(WebSocket webSocket, int code, String reason) {
                Log.d(TAG, "WebSocket正在关闭: " + reason);
                isWebSocketConnected = false;
            }

            @Override
            public void onClosed(WebSocket webSocket, int code, String reason) {
                Log.i(TAG, "WebSocket已关闭: " + reason);
                isWebSocketConnected = false;

                if (listener != null) {
                    mainHandler.post(() -> listener.onDisconnected());
                }
            }

            @Override
            public void onFailure(WebSocket webSocket, Throwable t, Response response) {
                Log.e(TAG, "WebSocket连接失败", t);
                isWebSocketConnected = false;

                if (listener != null) {
                    mainHandler.post(() -> listener.onError(t.getMessage()));
                }
            }
        });
    }

    /**
     * 断开WebSocket连接
     */
    public void disconnectWebSocket() {
        if (webSocket != null) {
            webSocket.close(1000, "客户端主动断开");
            webSocket = null;
        }
        isWebSocketConnected = false;
    }

    /**
     * 检查WebSocket是否已连接
     */
    public boolean isWebSocketConnected() {
        return isWebSocketConnected;
    }

    // ==================== 私有方法 ====================

    /**
     * 获取服务器URL
     */
    private String getServerUrl() {
        String serverUrl = configManager.getServerUrl();
        if (serverUrl == null || serverUrl.isEmpty()) {
            // 使用默认IP
            serverUrl = "http://192.168.1.100:8080";
        }
        return serverUrl;
    }

    /**
     * 获取WebSocket URL
     */
    private String getWebSocketUrl() {
        String serverUrl = getServerUrl();
        // 将http://替换为ws://
        return serverUrl.replace("http://", "ws://").replace(":8080", ":8081");
    }

    /**
     * 异步GET请求
     */
    private void getAsync(String url, NetworkCallback callback) {
        executor.execute(() -> {
            try {
                Request request = new Request.Builder()
                        .url(url)
                        .build();

                Response response = httpClient.newCall(request).execute();

                if (response.isSuccessful() && response.body() != null) {
                    String result = response.body().string();
                    notifySuccess(callback, result);
                } else {
                    notifyError(callback, "HTTP " + response.code());
                }

            } catch (Exception e) {
                Log.e(TAG, "GET请求失败", e);
                notifyError(callback, e.getMessage());
            }
        });
    }

    /**
     * 异步POST请求
     */
    private void postAsync(String url, String json, NetworkCallback callback) {
        executor.execute(() -> {
            try {
                RequestBody body = RequestBody.create(json, JSON_TYPE);
                Request request = new Request.Builder()
                        .url(url)
                        .post(body)
                        .build();

                Response response = httpClient.newCall(request).execute();

                if (response.isSuccessful() && response.body() != null) {
                    String result = response.body().string();
                    notifySuccess(callback, result);
                } else {
                    notifyError(callback, "HTTP " + response.code());
                }

            } catch (Exception e) {
                Log.e(TAG, "POST请求失败", e);
                notifyError(callback, e.getMessage());
            }
        });
    }

    /**
     * 通知成功
     */
    private void notifySuccess(NetworkCallback callback, String result) {
        if (callback != null) {
            mainHandler.post(() -> callback.onSuccess(result));
        }
    }

    /**
     * 通知错误
     */
    private void notifyError(NetworkCallback callback, String error) {
        if (callback != null) {
            mainHandler.post(() -> callback.onError(error));
        }
    }

    // ==================== 回调接口 ====================

    /**
     * 网络请求回调
     */
    public interface NetworkCallback {
        void onSuccess(String result);
        void onError(String error);
    }

    /**
     * WebSocket消息监听器
     */
    public interface WebSocketMessageListener {
        void onConnected();
        void onMessage(String message);
        void onDisconnected();
        void onError(String error);
    }
}
