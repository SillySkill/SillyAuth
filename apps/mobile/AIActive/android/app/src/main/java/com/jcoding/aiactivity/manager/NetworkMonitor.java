package com.jcoding.aiactivity.manager;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;

import com.jcoding.aiactivity.utils.NetworkUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * 网络状态监控器
 */
public class NetworkMonitor {

    private static NetworkMonitor instance;
    private Context context;
    private List<NetworkStateListener> listeners = new ArrayList<>();
    private boolean isRegistered = false;

    private NetworkMonitor(Context context) {
        this.context = context.getApplicationContext();
    }

    public static synchronized NetworkMonitor getInstance(Context context) {
        if (instance == null) {
            instance = new NetworkMonitor(context);
        }
        return instance;
    }

    /**
     * 添加监听器
     */
    public void addListener(NetworkStateListener listener) {
        if (!listeners.contains(listener)) {
            listeners.add(listener);
        }

        if (!isRegistered) {
            registerReceiver();
            isRegistered = true;
        }
    }

    /**
     * 移除监听器
     */
    public void removeListener(NetworkStateListener listener) {
        listeners.remove(listener);

        if (listeners.isEmpty() && isRegistered) {
            unregisterReceiver();
            isRegistered = false;
        }
    }

    /**
     * 注册广播接收器
     */
    private void registerReceiver() {
        IntentFilter filter = new IntentFilter();
        filter.addAction(ConnectivityManager.CONNECTIVITY_ACTION);
        context.registerReceiver(networkReceiver, filter);
    }

    /**
     * 注销广播接收器
     */
    private void unregisterReceiver() {
        try {
            context.unregisterReceiver(networkReceiver);
        } catch (IllegalArgumentException e) {
            // Receiver not registered
        }
    }

    /**
     * 网络状态广播接收器
     */
    private BroadcastReceiver networkReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (ConnectivityManager.CONNECTIVITY_ACTION.equals(intent.getAction())) {
                checkNetworkState();
            }
        }
    };

    /**
     * 检查网络状态
     */
    private void checkNetworkState() {
        boolean isOnline = NetworkUtils.isOnline(context);
        NetworkUtils.NetworkType type = NetworkUtils.getNetworkType(context);

        for (NetworkStateListener listener : listeners) {
            if (isOnline) {
                listener.onNetworkAvailable(isOnline, type);
            } else {
                listener.onNetworkLost();
            }
        }
    }

    /**
     * 网络状态监听器接口
     */
    public interface NetworkStateListener {
        /**
         * 网络可用
         */
        void onNetworkAvailable(boolean isOnline, NetworkUtils.NetworkType type);

        /**
         * 网络断开
         */
        void onNetworkLost();
    }
}
