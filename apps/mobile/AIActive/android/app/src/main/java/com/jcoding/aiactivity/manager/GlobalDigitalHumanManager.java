package com.jcoding.aiactivity.manager;

import android.app.Activity;
import android.content.Context;
import android.graphics.PixelFormat;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.FrameLayout;

import com.jcoding.aiactivity.widget.DigitalHumanView;

/**
 * 全局数字人管理器
 * 在所有模块页面显示数字人
 */
public class GlobalDigitalHumanManager {

    private static final String TAG = "GlobalDigitalHumanManager";

    private static GlobalDigitalHumanManager instance;

    private Context context;
    private WindowManager windowManager;
    private DigitalHumanView digitalHumanView;

    // 布局参数
    private WindowManager.LayoutParams layoutParams;

    // 数字人ID
    private String currentDigitalHumanId;

    // 是否已显示
    private boolean isShown = false;

    private GlobalDigitalHumanManager(Context context) {
        this.context = context.getApplicationContext();
        this.windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
    }

    public static synchronized GlobalDigitalHumanManager getInstance(Context context) {
        if (instance == null) {
            instance = new GlobalDigitalHumanManager(context);
        }
        return instance;
    }

    /**
     * 显示数字人
     */
    public void show(Activity activity, String digitalHumanId) {
        if (isShown && digitalHumanId.equals(currentDigitalHumanId)) {
            Log.d(TAG, "数字人已显示，无需重复添加");
            return;
        }

        // 如果已经显示，先移除
        if (isShown) {
            hide(activity);
        }

        // 使用Handler延迟添加，确保窗口完全初始化
        new Handler(Looper.getMainLooper()).post(new Runnable() {
            @Override
            public void run() {
                try {
                    // 使用Activity上下文创建数字人视图
                    digitalHumanView = new DigitalHumanView(activity);
                    digitalHumanView.loadDigitalHuman(digitalHumanId);

                    // 设置初始大小（屏幕宽度的30%）
                    int screenWidth = activity.getResources().getDisplayMetrics().widthPixels;
                    int size = (int) (screenWidth * 0.3);

                    // 创建布局参数
                    FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                            size,
                            size
                    );

                    // 设置初始位置（左下角）
                    // 使用setX和setY来定位
                    digitalHumanView.post(() -> {
                        int screenHeight = activity.getResources().getDisplayMetrics().heightPixels;
                        float margin = activity.getResources().getDisplayMetrics().density * 16; // 16dp margin
                        float targetX = margin; // 左边距16dp
                        float targetY = screenHeight - size - margin; // 底部距离16dp
                        digitalHumanView.setX(targetX);
                        digitalHumanView.setY(targetY);
                        Log.d(TAG, "数字人位置: X=" + targetX + ", Y=" + targetY);
                    });

                    // 添加到Activity的DecorView
                    ViewGroup decorView = (ViewGroup) activity.getWindow().getDecorView();
                    decorView.addView(digitalHumanView, params);

                    currentDigitalHumanId = digitalHumanId;
                    isShown = true;

                    Log.d(TAG, "数字人已显示: " + digitalHumanId);

                } catch (Exception e) {
                    Log.e(TAG, "显示数字人失败", e);
                }
            }
        });
    }

    /**
     * 隐藏数字人
     */
    public void hide(Activity activity) {
        if (!isShown || digitalHumanView == null) {
            return;
        }

        try {
            // 从DecorView移除
            ViewGroup decorView = (ViewGroup) activity.getWindow().getDecorView();
            decorView.removeView(digitalHumanView);
            digitalHumanView = null;
            isShown = false;
            Log.d(TAG, "数字人已隐藏");
        } catch (Exception e) {
            Log.e(TAG, "隐藏数字人失败", e);
        }
    }

    /**
     * 开始说话
     */
    public void startTalking() {
        if (digitalHumanView != null) {
            digitalHumanView.post(new Runnable() {
                @Override
                public void run() {
                    digitalHumanView.startTalking();
                }
            });
        }
    }

    /**
     * 停止说话
     */
    public void stopTalking() {
        if (digitalHumanView != null) {
            digitalHumanView.post(new Runnable() {
                @Override
                public void run() {
                    digitalHumanView.stopTalking();
                }
            });
        }
    }

    /**
     * 获取屏幕高度
     */
    private int getScreenHeight(Context context) {
        return context.getResources().getDisplayMetrics().heightPixels;
    }

    /**
     * 检查是否已显示
     */
    public boolean isShown() {
        return isShown;
    }
}
