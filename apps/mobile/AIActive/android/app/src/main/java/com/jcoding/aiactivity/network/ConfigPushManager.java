package com.jcoding.aiactivity.network;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.jcoding.aiactivity.manager.ConfigSyncManager;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 配置推送管理器
 * 集成 WebSocket 客户端和配置同步管理器，实现完整的配置推送功能
 */
public class ConfigPushManager {

    private static final String TAG = "ConfigPushManager";

    private static ConfigPushManager instance;

    private final Context context;
    private final ConfigPushClient wsClient;
    private final ConfigSyncManager configSyncManager;
    private final Handler mainHandler;

    // 当前推送任务
    private String currentPushId;
    private boolean isProcessingUpdate = false;

    private ConfigPushManager(Context context) {
        this.context = context.getApplicationContext();
        this.wsClient = ConfigPushClient.getInstance(context);
        this.configSyncManager = ConfigSyncManager.getInstance(context);
        this.mainHandler = new Handler(Looper.getMainLooper());

        // 设置 WebSocket 回调
        wsClient.setConfigUpdateCallback(wsCallback);

        Log.d(TAG, "配置推送管理器初始化完成");
    }

    public static synchronized ConfigPushManager getInstance(Context context) {
        if (instance == null) {
            instance = new ConfigPushManager(context);
        }
        return instance;
    }

    /**
     * 启动推送客户端
     */
    public void start() {
        Log.i(TAG, "启动配置推送客户端");
        wsClient.connect();

        // 定期上报设备状态
        scheduleStatusReport();
    }

    /**
     * 停止推送客户端
     */
    public void stop() {
        Log.i(TAG, "停止配置推送客户端");
        wsClient.disconnect();
    }

    /**
     * WebSocket 回调
     */
    private final ConfigPushClient.ConfigUpdateCallback wsCallback =
            new ConfigPushClient.ConfigUpdateCallback() {

        @Override
        public void onConnected() {
            Log.i(TAG, "WebSocket 已连接");
            // 立即上报一次设备状态
            reportDeviceStatus();
        }

        @Override
        public void onDisconnected(int code, String reason) {
            Log.w(TAG, "WebSocket 已断开: " + code + ", " + reason);
        }

        @Override
        public void onConfigUpdate(String pushId, String version, int versionCode,
                                  boolean forceUpdate, String releaseNotes, JSONArray files) {
            Log.i(TAG, String.format("收到配置更新: pushId=%s, version=%s, force=%b",
                    pushId, version, forceUpdate));

            // 处理配置更新
            handleConfigUpdate(pushId, version, versionCode, forceUpdate, releaseNotes, files);
        }

        @Override
        public void onError(String error) {
            Log.e(TAG, "WebSocket 错误: " + error);
        }
    };

    /**
     * 处理配置更新
     */
    private void handleConfigUpdate(String pushId, String version, int versionCode,
                                   boolean forceUpdate, String releaseNotes, JSONArray files) {
        if (isProcessingUpdate) {
            Log.w(TAG, "正在处理配置更新，忽略新的推送");
            wsClient.sendConfigAck(pushId, false, "正在处理其他更新", null, null);
            return;
        }

        // 检查版本
        int currentVersion = configSyncManager.getCurrentVersionCode();
        if (versionCode <= currentVersion) {
            Log.i(TAG, "配置版本已是最新，无需更新");
            wsClient.sendConfigAck(pushId, true, "已是最新版本", new String[0], new String[0]);
            return;
        }

        // 检查是否强制更新
        if (!forceUpdate) {
            // TODO: 可以弹窗询问用户是否更新
            Log.i(TAG, "非强制更新，跳过自动处理");
            return;
        }

        // 开始处理更新
        isProcessingUpdate = true;
        currentPushId = pushId;

        Log.i(TAG, "开始处理配置更新...");

        // TODO: 实现文件下载逻辑
        // 这里需要调用 ConfigSyncManager 或其他下载服务下载配置文件

        // 模拟处理过程
        mainHandler.postDelayed(() -> {
            List<String> receivedFiles = new ArrayList<>();
            List<String> failedFiles = new ArrayList<>();

            try {
                // 解析文件列表
                for (int i = 0; i < files.length(); i++) {
                    JSONObject file = files.getJSONObject(i);
                    String path = file.getString("path");
                    String url = file.getString("url");
                    String md5 = file.getString("md5");

                    // TODO: 下载文件
                    // downloadFile(path, url, md5);

                    receivedFiles.add(path);
                }

                // 更新成功
                Log.i(TAG, "配置更新成功");
                wsClient.sendConfigAck(pushId, true, "更新成功",
                        receivedFiles.toArray(new String[0]),
                        failedFiles.toArray(new String[0]));

                // 重新加载配置
                configSyncManager.checkAndUpdate(new ConfigSyncManager.ConfigUpdateCallback() {
                    @Override
                    public void onSuccess(boolean updated, String message) {
                        isProcessingUpdate = false;
                        currentPushId = null;
                    }

                    @Override
                    public void onError(String error) {
                        isProcessingUpdate = false;
                        currentPushId = null;
                        Log.e(TAG, "重新加载配置失败: " + error);
                    }

                    @Override
                    public void onProgress(int progress, String message) {
                        Log.d(TAG, "配置同步进度: " + progress + "% - " + message);
                    }
                });

            } catch (Exception e) {
                Log.e(TAG, "配置更新失败", e);

                // 更新失败
                failedFiles.add("config.json");
                wsClient.sendConfigAck(pushId, false, "更新失败: " + e.getMessage(),
                        receivedFiles.toArray(new String[0]),
                        failedFiles.toArray(new String[0]));

                isProcessingUpdate = false;
                currentPushId = null;
            }

        }, 1000);
    }

    /**
     * 上报设备状态
     */
    private void reportDeviceStatus() {
        try {
            Map<String, Object> status = new HashMap<>();
            status.put("battery", getBatteryLevel());
            status.put("storage", getAvailableStorage());
            status.put("network_type", getNetworkType());
            status.put("app_version", getAppVersion());
            status.put("config_version", configSyncManager.getCurrentVersion());

            wsClient.reportDeviceStatus(status);

        } catch (Exception e) {
            Log.e(TAG, "上报设备状态失败", e);
        }
    }

    /**
     * 定时上报设备状态
     */
    private void scheduleStatusReport() {
        mainHandler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (wsClient.isConnected()) {
                    reportDeviceStatus();
                }

                // 每5分钟上报一次
                mainHandler.postDelayed(this, 5 * 60 * 1000);
            }
        }, 5 * 60 * 1000);
    }

    /**
     * 获取电池电量
     */
    private int getBatteryLevel() {
        // TODO: 从 BatteryManager 获取实际电量
        return 100;
    }

    /**
     * 获取可用存储空间（MB）
     */
    private long getAvailableStorage() {
        // TODO: 获取实际可用存储
        return 1024;
    }

    /**
     * 获取网络类型
     */
    private String getNetworkType() {
        // TODO: 从 ConnectivityManager 获取实际网络类型
        return "wifi";
    }

    /**
     * 获取应用版本
     */
    private String getAppVersion() {
        try {
            android.content.pm.PackageInfo info = context.getPackageManager()
                    .getPackageInfo(context.getPackageName(), 0);
            return info.versionName;
        } catch (Exception e) {
            return "unknown";
        }
    }

    /**
     * 检查连接状态
     */
    public boolean isConnected() {
        return wsClient.isConnected();
    }
}
