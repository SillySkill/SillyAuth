package com.jcoding.aiactivity.ui;

import android.Manifest;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.DigitalHumanManager;
import com.jcoding.aiactivity.manager.GlobalDigitalHumanManager;
import com.jcoding.aiactivity.manager.NetworkMonitor;
import com.jcoding.aiactivity.utils.NetworkUtils;
import com.jcoding.aiactivity.utils.ScreenUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * Activity基类
 */
public abstract class BaseActivity extends AppCompatActivity {

    protected ConfigManager configManager;
    protected NetworkMonitor networkMonitor;

    // 权限请求结果监听器
    protected PermissionResultListener permissionListener;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        configManager = ConfigManager.getInstance(this);
        initNetworkMonitor();
    }

    /**
     * 初始化网络监控
     */
    private void initNetworkMonitor() {
        networkMonitor = NetworkMonitor.getInstance(this);
        networkMonitor.addListener(new NetworkMonitor.NetworkStateListener() {
            @Override
            public void onNetworkAvailable(boolean isOnline, NetworkUtils.NetworkType type) {
                onNetworkChanged(isOnline, type);
            }

            @Override
            public void onNetworkLost() {
                onNetworkChanged(false, NetworkUtils.NetworkType.NONE);
            }
        });
    }

    /**
     * 网络状态变化回调（子类可重写）
     */
    protected void onNetworkChanged(boolean isOnline, NetworkUtils.NetworkType type) {
        if (!isOnline) {
            showOfflineNotice();
        } else {
            hideOfflineNotice();
        }
    }

    /**
     * 显示离线提示
     */
    protected void showOfflineNotice() {
        // 子类可重写实现自定义UI
        Toast.makeText(this, "当前处于离线模式", Toast.LENGTH_SHORT).show();
    }

    /**
     * 隐藏离线提示
     */
    protected void hideOfflineNotice() {
        // 子类可重写实现自定义UI
    }

    /**
     * 显示Toast提示
     */
    protected void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }

    /**
     * 显示Toast提示（长时间）
     */
    protected void showToastLong(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }

    /**
     * 请求权限
     */
    protected void requestPermissions(String[] permissions, PermissionResultListener listener) {
        this.permissionListener = listener;

        List<String> deniedPermissions = new ArrayList<>();
        for (String permission : permissions) {
            if (ActivityCompat.checkSelfPermission(this, permission)
                    != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                deniedPermissions.add(permission);
            }
        }

        if (deniedPermissions.isEmpty()) {
            if (listener != null) {
                listener.onGranted();
            }
        } else {
            ActivityCompat.requestPermissions(this,
                    deniedPermissions.toArray(new String[0]),
                    1001);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == 1001 && permissionListener != null) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }

            if (allGranted) {
                permissionListener.onGranted();
            } else {
                permissionListener.onDenied();
            }
        }
    }

    /**
     * 获取屏幕宽度（dp）
     */
    protected int getScreenWidthDp() {
        return ScreenUtils.getScreenWidthDp(this);
    }

    /**
     * 判断是否是大屏设备
     */
    protected boolean isLargeScreen() {
        ScreenUtils.ScreenType type = ScreenUtils.getScreenType(this);
        return type == ScreenUtils.ScreenType.TABLET_LARGE
                || type == ScreenUtils.ScreenType.LARGE_SCREEN;
    }

    /**
     * 判断是否是横屏
     */
    protected boolean isLandscape() {
        return ScreenUtils.isLandscape(this);
    }

    /**
     * 权限请求结果监听器
     */
    public interface PermissionResultListener {
        void onGranted();
        void onDenied();
    }

    /**
     * 应用数字人显示配置到容器
     *
     * @param container 数字人容器
     * @param imageView 数字人ImageView
     * @param position 位置: "top", "middle", "bottom", "bottom_right"
     */
    protected void applyDigitalHumanConfig(View container, ImageView imageView, String position) {
        if (container == null || imageView == null) {
            return;
        }

        // 应用位置
        FrameLayout.LayoutParams params;
        if (container.getLayoutParams() instanceof FrameLayout.LayoutParams) {
            params = (FrameLayout.LayoutParams) container.getLayoutParams();
        } else {
            params = new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT
            );
        }

        switch (position) {
            case "top":
                params.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL;
                break;
            case "middle":
                params.gravity = Gravity.CENTER;
                break;
            case "bottom":
                params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
                break;
            case "bottom_right":
            default:
                params.gravity = Gravity.BOTTOM | Gravity.END;
                break;
        }

        // 应用大小
        int sizeDp = configManager.getDigitalHumanSize();
        float scale = getResources().getDisplayMetrics().density;
        int sizePx = (int) (sizeDp * scale);
        params.height = sizePx;
        params.width = (int) (sizePx * 0.8f); // 宽高比4:5

        container.setLayoutParams(params);

        // 应用缩放模式
        String scaleType = configManager.getDigitalHumanScaleType();
        switch (scaleType) {
            case "fit_center":
                imageView.setScaleType(ImageView.ScaleType.FIT_CENTER);
                break;
            case "center_crop":
                imageView.setScaleType(ImageView.ScaleType.CENTER_CROP);
                break;
            case "center":
            default:
                imageView.setScaleType(ImageView.ScaleType.CENTER);
                break;
        }
    }

    @Override
    protected void onResume() {
        super.onResume();

        // 显示全局数字人（如果在模块页面且已配置）
        showGlobalDigitalHuman();
    }

    @Override
    protected void onPause() {
        super.onPause();

        // 页面不可见时，可以隐藏全局数字人（可选）
        // hideGlobalDigitalHuman();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (networkMonitor != null) {
            networkMonitor.removeListener(networkStateListener);
        }
    }

    /**
     * 显示全局数字人
     */
    private void showGlobalDigitalHuman() {
        try {
            // 检查是否启用数字人
            boolean isEnabled = configManager.isDigitalHumanEnabled();
            Log.d("BaseActivity", "数字人启用状态: " + isEnabled);

            if (!isEnabled) {
                return;
            }

            // 获取默认数字人ID
            String digitalHumanId = configManager.getDefaultDigitalHumanId();
            Log.d("BaseActivity", "默认数字人ID: " + digitalHumanId);

            if (digitalHumanId == null || digitalHumanId.isEmpty()) {
                // 如果没有设置，自动设置为默认ID
                digitalHumanId = "JC2026012100001";
                configManager.setDefaultDigitalHumanId(digitalHumanId);
                Log.d("BaseActivity", "自动设置默认数字人ID: " + digitalHumanId);
            }

            // 显示全局数字人
            GlobalDigitalHumanManager.getInstance(this).show(this, digitalHumanId);

        } catch (Exception e) {
            Log.e("BaseActivity", "显示全局数字人失败", e);
        }
    }

    /**
     * 隐藏全局数字人
     */
    private void hideGlobalDigitalHuman() {
        GlobalDigitalHumanManager.getInstance(this).hide(this);
    }

    /**
     * 获取全局数字人管理器
     */
    protected GlobalDigitalHumanManager getGlobalDigitalHumanManager() {
        return GlobalDigitalHumanManager.getInstance(this);
    }

    private NetworkMonitor.NetworkStateListener networkStateListener =
            new NetworkMonitor.NetworkStateListener() {
        @Override
        public void onNetworkAvailable(boolean isOnline, NetworkUtils.NetworkType type) {
            onNetworkChanged(isOnline, type);
        }

        @Override
        public void onNetworkLost() {
            onNetworkChanged(false, NetworkUtils.NetworkType.NONE);
        }
    };
}
