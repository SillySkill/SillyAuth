package com.jcoding.aiactivity.utils;

import android.content.Context;
import android.content.res.Configuration;
import android.util.DisplayMetrics;
import android.util.TypedValue;
import android.view.WindowManager;

/**
 * 屏幕工具类
 */
public class ScreenUtils {

    /**
     * 获取屏幕宽度（像素）
     */
    public static int getScreenWidth(Context context) {
        WindowManager windowManager =
                (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        if (windowManager == null) {
            return 0;
        }

        DisplayMetrics metrics = new DisplayMetrics();
        windowManager.getDefaultDisplay().getMetrics(metrics);
        return metrics.widthPixels;
    }

    /**
     * 获取屏幕高度（像素）
     */
    public static int getScreenHeight(Context context) {
        WindowManager windowManager =
                (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        if (windowManager == null) {
            return 0;
        }

        DisplayMetrics metrics = new DisplayMetrics();
        windowManager.getDefaultDisplay().getMetrics(metrics);
        return metrics.heightPixels;
    }

    /**
     * 获取屏幕宽度（dp）
     */
    public static int getScreenWidthDp(Context context) {
        return pxToDp(context, getScreenWidth(context));
    }

    /**
     * 获取屏幕高度（dp）
     */
    public static int getScreenHeightDp(Context context) {
        return pxToDp(context, getScreenHeight(context));
    }

    /**
     * 判断是否是横屏
     */
    public static boolean isLandscape(Context context) {
        return context.getResources().getConfiguration().orientation
                == Configuration.ORIENTATION_LANDSCAPE;
    }

    /**
     * 判断是否是竖屏
     */
    public static boolean isPortrait(Context context) {
        return context.getResources().getConfiguration().orientation
                == Configuration.ORIENTATION_PORTRAIT;
    }

    /**
     * dp转px
     */
    public static int dpToPx(Context context, float dp) {
        return (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                dp,
                context.getResources().getDisplayMetrics()
        );
    }

    /**
     * px转dp
     */
    public static int pxToDp(Context context, float px) {
        return (int) (px / context.getResources().getDisplayMetrics().density);
    }

    /**
     * sp转px
     */
    public static int spToPx(Context context, float sp) {
        return (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_SP,
                sp,
                context.getResources().getDisplayMetrics()
        );
    }

    /**
     * 获取屏幕类型
     */
    public static ScreenType getScreenType(Context context) {
        int screenWidthDp = getScreenWidthDp(context);

        if (screenWidthDp >= 1024) {
            return ScreenType.LARGE_SCREEN;  // 触摸一体机/大屏
        } else if (screenWidthDp >= 720) {
            return ScreenType.TABLET_LARGE;  // 10寸平板
        } else if (screenWidthDp >= 600) {
            return ScreenType.TABLET_SMALL;  // 7寸平板
        } else {
            return ScreenType.PHONE;         // 手机
        }
    }

    /**
     * 根据屏幕类型获取触摸目标尺寸
     */
    public static int getTouchTargetSize(Context context) {
        ScreenType type = getScreenType(context);
        switch (type) {
            case LARGE_SCREEN:
                return dpToPx(context, 96);
            case TABLET_LARGE:
                return dpToPx(context, 80);
            case TABLET_SMALL:
                return dpToPx(context, 64);
            default:
                return dpToPx(context, 56);
        }
    }

    /**
     * 屏幕类型枚举
     */
    public enum ScreenType {
        PHONE,           // 手机
        TABLET_SMALL,    // 7寸平板
        TABLET_LARGE,    // 10寸平板
        LARGE_SCREEN     // 触摸一体机/大屏
    }
}
