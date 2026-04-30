package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import android.util.Log;

import java.net.InetAddress;

/**
 * 内场秀网络配置管理器
 * 管理内场秀设备的网络连接配置
 */
public class InnerShowNetworkConfigManager {

    private static final String TAG = "InnerShowNetworkConfig";
    private static final String PREF_NAME = "inner_show_network";

    // 配置键
    private static final String KEY_MODE = "network_mode";
    private static final String KEY_SERVER_URL = "server_url";
    private static final String KEY_SERVER_IP = "server_ip";
    private static final String KEY_SERVER_PORT = "server_port";
    private static final String KEY_AUTO_DISCOVER = "auto_discover";
    private static final String KEY_IS_SERVER = "is_server";
    private static final String KEY_WS_PORT = "ws_port";

    // 服务名称（用于设备发现）
    private static final String SERVICE_NAME = "InnerShowServer";
    private static final String SERVICE_TYPE = "_http._tcp.";

    private static InnerShowNetworkConfigManager instance;
    private Context context;
    private SharedPreferences prefs;

    // 网络模式
    public enum NetworkMode {
        LAN("lan", "局域网模式", "所有设备连接同一局域网"),
        SERVER("server", "主服务器模式", "内场秀设备作为主服务器");

        private final String code;
        private final String name;
        private final String description;

        NetworkMode(String code, String name, String description) {
            this.code = code;
            this.name = name;
            this.description = description;
        }

        public String getCode() {
            return code;
        }

        public String getName() {
            return name;
        }

        public String getDescription() {
            return description;
        }

        public static NetworkMode fromCode(String code) {
            for (NetworkMode mode : values()) {
                if (mode.code.equals(code)) {
                    return mode;
                }
            }
            return LAN;
        }
    }

    private InnerShowNetworkConfigManager(Context context) {
        this.context = context.getApplicationContext();
        this.prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public static synchronized InnerShowNetworkConfigManager getInstance(Context context) {
        if (instance == null) {
            instance = new InnerShowNetworkConfigManager(context);
        }
        return instance;
    }

    // ==================== 网络模式 ====================

    /**
     * 设置网络模式
     */
    public void setNetworkMode(NetworkMode mode) {
        prefs.edit().putString(KEY_MODE, mode.getCode()).apply();
        Log.i(TAG, "网络模式已设置为: " + mode.getName());
    }

    /**
     * 获取网络模式
     */
    public NetworkMode getNetworkMode() {
        String code = prefs.getString(KEY_MODE, NetworkMode.LAN.getCode());
        return NetworkMode.fromCode(code);
    }

    /**
     * 是否为主服务器模式
     */
    public boolean isServerMode() {
        return prefs.getBoolean(KEY_IS_SERVER, false);
    }

    /**
     * 设置为主服务器模式
     */
    public void setServerMode(boolean isServer) {
        prefs.edit().putBoolean(KEY_IS_SERVER, isServer).apply();
        Log.i(TAG, "主服务器模式: " + isServer);
    }

    // ==================== 服务器配置 ====================

    /**
     * 设置服务器URL
     */
    public void setServerUrl(String url) {
        prefs.edit().putString(KEY_SERVER_URL, url).apply();
        Log.i(TAG, "服务器URL已设置: " + url);
    }

    /**
     * 获取服务器URL
     */
    public String getServerUrl() {
        String url = prefs.getString(KEY_SERVER_URL, "");

        // 如果URL为空，使用IP和端口构建
        if (url.isEmpty()) {
            String ip = getServerIp();
            int port = getServerPort();
            if (!ip.isEmpty()) {
                url = "http://" + ip + ":" + port;
            }
        }

        return url;
    }

    /**
     * 设置服务器IP
     */
    public void setServerIp(String ip) {
        prefs.edit().putString(KEY_SERVER_IP, ip).apply();
        // 清除URL缓存，强制使用新IP重建
        prefs.edit().remove(KEY_SERVER_URL).apply();
        Log.i(TAG, "服务器IP已设置: " + ip);
    }

    /**
     * 获取服务器IP
     */
    public String getServerIp() {
        return prefs.getString(KEY_SERVER_IP, "192.168.1.100");
    }

    /**
     * 设置服务器端口
     */
    public void setServerPort(int port) {
        prefs.edit().putInt(KEY_SERVER_PORT, port).apply();
        prefs.edit().remove(KEY_SERVER_URL).apply();
        Log.i(TAG, "服务器端口已设置: " + port);
    }

    /**
     * 获取服务器端口
     */
    public int getServerPort() {
        return prefs.getInt(KEY_SERVER_PORT, 8080);
    }

    /**
     * 设置WebSocket端口
     */
    public void setWsPort(int port) {
        prefs.edit().putInt(KEY_WS_PORT, port).apply();
    }

    /**
     * 获取WebSocket端口
     */
    public int getWsPort() {
        return prefs.getInt(KEY_WS_PORT, 8081);
    }

    // ==================== 自动发现 ====================

    /**
     * 是否启用自动发现
     */
    public boolean isAutoDiscoverEnabled() {
        return prefs.getBoolean(KEY_AUTO_DISCOVER, true);
    }

    /**
     * 设置自动发现
     */
    public void setAutoDiscover(boolean enabled) {
        prefs.edit().putBoolean(KEY_AUTO_DISCOVER, enabled).apply();
        Log.i(TAG, "自动发现: " + (enabled ? "启用" : "禁用"));
    }

    // ==================== 设备发现 ====================

    /**
     * 注册网络服务（主服务器模式）
     */
    public void registerService(NsdManager nsdManager, int port, ServiceRegistrationCallback callback) {
        NsdServiceInfo serviceInfo = new NsdServiceInfo();
        serviceInfo.setServiceName(SERVICE_NAME);
        serviceInfo.setServiceType(SERVICE_TYPE);
        serviceInfo.setPort(port);

        try {
            nsdManager.registerService(
                serviceInfo,
                NsdManager.PROTOCOL_DNS_SD,
                new NsdManager.RegistrationListener() {
                    @Override
                    public void onRegistrationFailed(NsdServiceInfo serviceInfo, int errorCode) {
                        Log.e(TAG, "服务注册失败: " + errorCode);
                        if (callback != null) {
                            callback.onRegistrationFailed(errorCode);
                        }
                    }

                    @Override
                    public void onUnregistrationFailed(NsdServiceInfo serviceInfo, int errorCode) {
                        Log.e(TAG, "服务注销失败: " + errorCode);
                    }

                    @Override
                    public void onServiceRegistered(NsdServiceInfo serviceInfo) {
                        Log.i(TAG, "服务注册成功: " + serviceInfo.getServiceName());
                        if (callback != null) {
                            callback.onServiceRegistered(serviceInfo);
                        }
                    }

                    @Override
                    public void onServiceUnregistered(NsdServiceInfo serviceInfo) {
                        Log.i(TAG, "服务已注销");
                    }
                }
            );
        } catch (Exception e) {
            Log.e(TAG, "注册服务异常", e);
            if (callback != null) {
                callback.onRegistrationFailed(-1);
            }
        }
    }

    /**
     * 注销网络服务
     */
    public void unregisterService(NsdManager nsdManager, NsdManager.RegistrationListener listener) {
        try {
            nsdManager.unregisterService(listener);
            Log.i(TAG, "服务已注销");
        } catch (Exception e) {
            Log.e(TAG, "注销服务异常", e);
        }
    }

    /**
     * 发现网络服务（客户端模式）
     */
    public void discoverServices(NsdManager nsdManager, ServiceDiscoveryCallback callback) {
        try {
            nsdManager.discoverServices(SERVICE_TYPE, NsdManager.PROTOCOL_DNS_SD,
                new NsdManager.DiscoveryListener() {
                    @Override
                    public void onStartDiscoveryFailed(String serviceType, int errorCode) {
                        Log.e(TAG, "开始发现服务失败: " + errorCode);
                        if (callback != null) {
                            callback.onDiscoveryFailed(errorCode);
                        }
                    }

                    @Override
                    public void onStopDiscoveryFailed(String serviceType, int errorCode) {
                        Log.e(TAG, "停止发现服务失败: " + errorCode);
                    }

                    @Override
                    public void onDiscoveryStarted(String serviceType) {
                        Log.i(TAG, "开始发现服务: " + serviceType);
                        if (callback != null) {
                            callback.onDiscoveryStarted();
                        }
                    }

                    @Override
                    public void onDiscoveryStopped(String serviceType) {
                        Log.i(TAG, "停止发现服务");
                        if (callback != null) {
                            callback.onDiscoveryStopped();
                        }
                    }

                    @Override
                    public void onServiceFound(NsdServiceInfo serviceInfo) {
                        Log.i(TAG, "发现服务: " + serviceInfo.getServiceName());

                        // 只处理内场秀服务
                        if (serviceInfo.getServiceName().contains(SERVICE_NAME)) {
                            if (callback != null) {
                                callback.onServiceFound(serviceInfo);
                            }

                            // 解析服务地址
                            nsdManager.resolveService(serviceInfo, new NsdManager.ResolveListener() {
                                @Override
                                public void onResolveFailed(NsdServiceInfo serviceInfo, int errorCode) {
                                    Log.e(TAG, "解析服务失败: " + errorCode);
                                }

                                @Override
                                public void onServiceResolved(NsdServiceInfo serviceInfo) {
                                    Log.i(TAG, "服务已解析");
                                    if (callback != null) {
                                        callback.onServiceResolved(serviceInfo);
                                    }
                                }
                            });
                        }
                    }

                    @Override
                    public void onServiceLost(NsdServiceInfo serviceInfo) {
                        Log.i(TAG, "服务丢失: " + serviceInfo.getServiceName());
                        if (callback != null) {
                            callback.onServiceLost(serviceInfo);
                        }
                    }
                }
            );
        } catch (Exception e) {
            Log.e(TAG, "发现服务异常", e);
            if (callback != null) {
                callback.onDiscoveryFailed(-1);
            }
        }
    }

    /**
     * 停止发现服务
     */
    public void stopDiscovery(NsdManager nsdManager, NsdManager.DiscoveryListener listener) {
        try {
            nsdManager.stopServiceDiscovery(listener);
            Log.i(TAG, "停止发现服务");
        } catch (Exception e) {
            Log.e(TAG, "停止发现服务异常", e);
        }
    }

    // ==================== 重置配置 ====================

    /**
     * 重置为默认配置
     */
    public void resetToDefault() {
        prefs.edit().clear().apply();
        Log.i(TAG, "配置已重置为默认");
    }

    /**
     * 获取配置摘要
     */
    public String getConfigSummary() {
        NetworkMode mode = getNetworkMode();
        String ip = getServerIp();
        int port = getServerPort();

        StringBuilder sb = new StringBuilder();
        sb.append("网络模式: ").append(mode.getName()).append("\n");
        sb.append("服务器: ").append(ip).append(":").append(port).append("\n");
        sb.append("自动发现: ").append(isAutoDiscoverEnabled() ? "启用" : "禁用");

        return sb.toString();
    }

    // ==================== 回调接口 ====================

    /**
     * 服务注册回调
     */
    public interface ServiceRegistrationCallback {
        void onServiceRegistered(NsdServiceInfo serviceInfo);
        void onRegistrationFailed(int errorCode);
    }

    /**
     * 服务发现回调
     */
    public interface ServiceDiscoveryCallback {
        void onDiscoveryStarted();
        void onServiceFound(NsdServiceInfo serviceInfo);
        void onServiceResolved(NsdServiceInfo serviceInfo);
        void onServiceLost(NsdServiceInfo serviceInfo);
        void onDiscoveryStopped();
        void onDiscoveryFailed(int errorCode);
    }
}
