package com.jcoding.aiactivity.utils;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.os.Build;
import android.util.Log;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.Enumeration;

/**
 * 网络状态工具类
 */
public class NetworkUtils {

    private static final String TAG = "NetworkUtils";

    /**
     * 检查网络是否可用
     */
    public static boolean isOnline(Context context) {
        ConnectivityManager connectivityManager =
                (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);

        if (connectivityManager == null) {
            return false;
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Network network = connectivityManager.getActiveNetwork();
            if (network == null) {
                return false;
            }

            NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(network);
            return capabilities != null
                    && (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
                    || capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)
                    || capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET));
        } else {
            NetworkInfo networkInfo = connectivityManager.getActiveNetworkInfo();
            return networkInfo != null && networkInfo.isConnected();
        }
    }

    /**
     * 获取网络类型
     */
    public static NetworkType getNetworkType(Context context) {
        ConnectivityManager connectivityManager =
                (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);

        if (connectivityManager == null) {
            return NetworkType.NONE;
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Network network = connectivityManager.getActiveNetwork();
            if (network == null) {
                return NetworkType.NONE;
            }

            NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(network);
            if (capabilities == null) {
                return NetworkType.NONE;
            }

            if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) {
                return NetworkType.WIFI;
            } else if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)) {
                return NetworkType.CELLULAR;
            } else if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)) {
                return NetworkType.ETHERNET;
            }
            return NetworkType.OTHER;
        } else {
            NetworkInfo networkInfo = connectivityManager.getActiveNetworkInfo();
            if (networkInfo == null || !networkInfo.isConnected()) {
                return NetworkType.NONE;
            }

            switch (networkInfo.getType()) {
                case ConnectivityManager.TYPE_WIFI:
                    return NetworkType.WIFI;
                case ConnectivityManager.TYPE_MOBILE:
                    return NetworkType.CELLULAR;
                case ConnectivityManager.TYPE_ETHERNET:
                    return NetworkType.ETHERNET;
                default:
                    return NetworkType.OTHER;
            }
        }
    }

    /**
     * 网络类型枚举
     */
    public enum NetworkType {
        NONE,       // 无网络
        WIFI,       // WiFi
        CELLULAR,   // 移动网络
        ETHERNET,   // 以太网
        OTHER       // 其他
    }

    /**
     * 获取本机IP地址（局域网IP）
     * @return IP地址，获取失败返回空字符串
     */
    public static String getLocalIpAddress() {
        try {
            // 遍历所有网络接口
            Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();

            while (interfaces.hasMoreElements()) {
                NetworkInterface networkInterface = interfaces.nextElement();

                // 跳过回环接口和未启用的接口
                if (networkInterface.isLoopback() || !networkInterface.isUp()) {
                    continue;
                }

                // 获取IP地址
                Enumeration<InetAddress> addresses = networkInterface.getInetAddresses();

                while (addresses.hasMoreElements()) {
                    InetAddress address = addresses.nextElement();

                    // 跳过回环地址和IPv6地址
                    if (!address.isLoopbackAddress() && address.getHostAddress().indexOf(':') == -1) {
                        String ip = address.getHostAddress();
                        Log.d(TAG, "本机IP: " + ip);
                        return ip;
                    }
                }
            }
        } catch (SocketException e) {
            Log.e(TAG, "获取本机IP失败", e);
        }

        Log.w(TAG, "未找到有效的局域网IP，使用默认值");
        return "192.168.1.100";
    }

    /**
     * 获取WiFi的IP地址
     * @return WiFi IP地址，获取失败返回空字符串
     */
    public static String getWifiIpAddress(Context context) {
        try {
            ConnectivityManager connectivityManager =
                    (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);

            if (connectivityManager != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                Network network = connectivityManager.getActiveNetwork();
                if (network != null) {
                    // 对于WiFi网络，使用通用方法获取IP
                    return getLocalIpAddress();
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "获取WiFi IP失败", e);
        }

        return getLocalIpAddress();
    }

    /**
     * 将原始OSS URL转换为自定义域名URL（用于显示和下载）
     * 与convertToProxyUrlDomain功能相同，为兼容保留
     *
     * @param url 原始OSS URL或oss://格式URL
     * @return 自定义域名URL (https://file.jcoding.chat/...)
     */
    public static String convertToProxyUrl(String url) {
        return convertToProxyUrlDomain(url);
    }

    /**
     * 将原始OSS URL转换为自定义域名URL（用于显示和下载）
     * 直接使用自定义域名访问，不再通过服务器代理
     *
     * @param url 原始OSS URL或oss://格式URL
     * @return 自定义域名URL (https://file.jcoding.chat/...)
     */
    public static String convertToProxyUrlDomain(String url) {
        if (url == null || url.isEmpty()) {
            return url;
        }

        try {
            String path = null;

            // 情况1：处理 oss://bucket/path 格式
            if (url.startsWith("oss://")) {
                // 提取路径部分: oss://jc-st/application/... -> application/...
                String remaining = url.substring(6); // 去掉 "oss://"
                int slashIndex = remaining.indexOf('/');
                if (slashIndex > 0 && slashIndex < remaining.length() - 1) {
                    path = remaining.substring(slashIndex + 1);
                    Log.d(TAG, "oss://格式URL，提取路径: " + path);
                }
            }
            // 情况2：处理标准OSS URL格式 (https://jc-st.oss-cn-shanghai.aliyuncs.com/...)
            else if (url.contains("jc-st.oss-cn-shanghai.aliyuncs.com/")) {
                path = url.substring(url.indexOf("jc-st.oss-cn-shanghai.aliyuncs.com/") + "jc-st.oss-cn-shanghai.aliyuncs.com/".length());
                Log.d(TAG, "OSS URL，提取路径: " + path);
            }
            // 情况3：处理北京节点
            else if (url.contains("jc-st.oss-cn-beijing.aliyuncs.com/")) {
                path = url.substring(url.indexOf("jc-st.oss-cn-beijing.aliyuncs.com/") + "jc-st.oss-cn-beijing.aliyuncs.com/".length());
                Log.d(TAG, "北京OSS URL，提取路径: " + path);
            }
            // 情况4：处理热点节点
            else if (url.contains("jc-hot.oss-cn-shanghai.aliyuncs.com/")) {
                path = url.substring(url.indexOf("jc-hot.oss-cn-shanghai.aliyuncs.com/") + "jc-hot.oss-cn-shanghai.aliyuncs.com/".length());
                Log.d(TAG, "热点OSS URL，提取路径: " + path);
            }
            // 情况5：已经是自定义域名URL格式，直接返回
            else if (url.contains("file.jcoding.chat/")) {
                Log.d(TAG, "URL已经是自定义域名格式: " + url);
                return url;
            }
            // 情况6：旧代理URL格式，需要转换
            else if (url.contains("www.jcoding.chat/api/file/")) {
                path = url.substring(url.indexOf("www.jcoding.chat/api/file/") + "www.jcoding.chat/api/file/".length());
                Log.d(TAG, "旧代理URL，提取路径: " + path);
            }

            // 如果提取到了路径，构建自定义域名URL
            if (path != null && !path.isEmpty()) {
                String customUrl = "https://file.jcoding.chat/" + path;
                Log.d(TAG, "转换为自定义域名URL: " + url + " -> " + customUrl);
                return customUrl;
            }

            // 其他情况，直接返回原URL
            Log.d(TAG, "URL格式无法识别，直接返回: " + url);
            return url;

        } catch (Exception e) {
            Log.e(TAG, "转换URL失败: " + url, e);
            return url;
        }
    }

    /**
     * 将自定义域名URL转换回原始OSS URL
     * 用于火山引擎API调用，API无法访问自定义域名URL
     *
     * @param url 自定义域名URL或原始URL
     * @return 原始OSS URL
     */
    public static String convertProxyToOriginalUrl(String url) {
        if (url == null || url.isEmpty()) {
            return url;
        }

        try {
            // 情况1：自定义域名URL格式（直接使用 file.jcoding.chat）
            if (url.contains("file.jcoding.chat/")) {
                // 提取路径部分
                String path = url.substring(url.indexOf("file.jcoding.chat/") + "file.jcoding.chat/".length());
                // 构建原始OSS URL（使用上海节点）
                String originalUrl = "https://jc-st.oss-cn-shanghai.aliyuncs.com/" + path;
                Log.d(TAG, "自定义域名URL转原始OSS: " + url + " -> " + originalUrl);
                return originalUrl;
            }

            // 情况2：旧代理URL格式（带/api/file/路径）
            if (url.contains("www.jcoding.chat/api/file/")) {
                // 提取路径部分
                String path = url.substring(url.indexOf("www.jcoding.chat/api/file/") + "www.jcoding.chat/api/file/".length());
                // 构建原始OSS URL（使用上海节点）
                String originalUrl = "https://jc-st.oss-cn-shanghai.aliyuncs.com/" + path;
                Log.d(TAG, "旧代理URL转原始OSS: " + url + " -> " + originalUrl);
                return originalUrl;
            }

            // 情况3：简化格式（不带/api/file/路径，如 www.jcoding.chat/application/...）
            if (url.contains("www.jcoding.chat/application/")) {
                // 提取路径部分
                String path = url.substring(url.indexOf("www.jcoding.chat/") + "www.jcoding.chat/".length());
                // 构建原始OSS URL
                String originalUrl = "https://jc-st.oss-cn-shanghai.aliyuncs.com/" + path;
                Log.d(TAG, "域名URL转原始OSS: " + url + " -> " + originalUrl);
                return originalUrl;
            }

            // 如果已经是OSS URL，直接返回
            for (String endpoint : new String[]{"jc-st.oss-cn-shanghai.aliyuncs.com", "jc-st.oss-cn-beijing.aliyuncs.com", "jc-hot.oss-cn-shanghai.aliyuncs.com"}) {
                if (url.contains(endpoint)) {
                    Log.d(TAG, "URL已经是原始OSS格式: " + url);
                    return url;
                }
            }

            // 其他情况，直接返回
            Log.d(TAG, "URL格式无法识别，直接返回: " + url);
            return url;

        } catch (Exception e) {
            Log.e(TAG, "转换URL失败: " + url, e);
            return url;
        }
    }

    /**
     * 获取自定义域名访问所需的Host header
     * @return Host header值
     */
    public static String getProxyHost() {
        return "file.jcoding.chat";
    }

    /**
     * 通过服务器API将自定义域名URL转换为直接OSS URL
     * 用于火山引擎API调用（API无法访问自定义域名URL）
     *
     * @param proxyUrl 自定义域名URL (https://file.jcoding.chat/...)
     * @return 直接OSS URL，失败返回原URL
     */
    public static String convertToDirectUrlViaServer(String proxyUrl) {
        if (proxyUrl == null || proxyUrl.isEmpty()) {
            return proxyUrl;
        }

        // 如果不是自定义域名URL，直接返回
        if (!proxyUrl.contains("file.jcoding.chat/")) {
            Log.d(TAG, "非自定义域名URL，无需转换: " + proxyUrl);
            return convertProxyToOriginalUrl(proxyUrl);
        }

        // 使用本地转换方法（无需服务器调用）
        // 因为自定义域名URL格式固定：https://file.jcoding.chat/application/...
        // 转换为：https://jc-st.oss-cn-shanghai.aliyuncs.com/application/...
        String directUrl = convertProxyToOriginalUrl(proxyUrl);
        Log.d(TAG, "本地转换 自定义域名->直接: " + proxyUrl + " -> " + directUrl);
        return directUrl;
    }
}
