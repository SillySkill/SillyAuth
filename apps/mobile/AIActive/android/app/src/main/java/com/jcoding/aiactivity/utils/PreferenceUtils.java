package com.jcoding.aiactivity.utils;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * SharedPreferences工具类
 */
public class PreferenceUtils {

    private static SharedPreferences getPreferences(Context context) {
        return context.getSharedPreferences(Constants.PREF_NAME, Context.MODE_PRIVATE);
    }

    /**
     * 保存字符串
     */
    public static void putString(Context context, String key, String value) {
        getPreferences(context).edit().putString(key, value).apply();
    }

    /**
     * 获取字符串
     */
    public static String getString(Context context, String key, String defaultValue) {
        return getPreferences(context).getString(key, defaultValue);
    }

    /**
     * 保存整数
     */
    public static void putInt(Context context, String key, int value) {
        getPreferences(context).edit().putInt(key, value).apply();
    }

    /**
     * 获取整数
     */
    public static int getInt(Context context, String key, int defaultValue) {
        return getPreferences(context).getInt(key, defaultValue);
    }

    /**
     * 保存长整数
     */
    public static void putLong(Context context, String key, long value) {
        getPreferences(context).edit().putLong(key, value).apply();
    }

    /**
     * 获取长整数
     */
    public static long getLong(Context context, String key, long defaultValue) {
        return getPreferences(context).getLong(key, defaultValue);
    }

    /**
     * 保存布尔值
     */
    public static void putBoolean(Context context, String key, boolean value) {
        getPreferences(context).edit().putBoolean(key, value).apply();
    }

    /**
     * 获取布尔值
     */
    public static boolean getBoolean(Context context, String key, boolean defaultValue) {
        return getPreferences(context).getBoolean(key, defaultValue);
    }

    /**
     * 获取布尔值（支持null，返回Boolean对象）
     */
    public static Boolean getBooleanObject(Context context, String key, Boolean defaultValue) {
        if (!getPreferences(context).contains(key)) {
            return defaultValue;
        }
        return getPreferences(context).getBoolean(key, defaultValue != null ? defaultValue : false);
    }

    /**
     * 删除指定key
     */
    public static void remove(Context context, String key) {
        getPreferences(context).edit().remove(key).apply();
    }

    /**
     * 清空所有数据
     */
    public static void clear(Context context) {
        getPreferences(context).edit().clear().apply();
    }

    /**
     * 保存浮点数
     */
    public static void putFloat(Context context, String key, float value) {
        getPreferences(context).edit().putFloat(key, value).apply();
    }

    /**
     * 获取浮点数
     */
    public static float getFloat(Context context, String key, float defaultValue) {
        return getPreferences(context).getFloat(key, defaultValue);
    }

    /**
     * 获取整数（返回Integer对象，支持null）
     */
    public static Integer getInt(Context context, String key, Integer defaultValue) {
        SharedPreferences prefs = getPreferences(context);
        if (!prefs.contains(key)) {
            return defaultValue;
        }
        return prefs.getInt(key, defaultValue != null ? defaultValue : 0);
    }

    /**
     * 获取浮点数（返回Float对象，支持null）
     */
    public static Float getFloat(Context context, String key, Float defaultValue) {
        SharedPreferences prefs = getPreferences(context);
        if (!prefs.contains(key)) {
            return defaultValue;
        }
        return prefs.getFloat(key, defaultValue != null ? defaultValue : 0f);
    }
}
