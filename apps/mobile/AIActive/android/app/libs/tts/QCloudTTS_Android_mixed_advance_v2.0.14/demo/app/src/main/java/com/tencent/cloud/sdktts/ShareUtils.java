package com.tencent.cloud.sdktts;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import com.tencent.cloud.libqcloudtts.utils.AAILogger;

import java.lang.reflect.Field;

public class ShareUtils {
    private static final String TAG = ShareUtils.class.getSimpleName();
    public static <T> T unmarshal(Context context, T value) {
        try {
            Class<T> cls = (Class<T>) value.getClass();
            if (cls.isAnnotationPresent(ShareKey.class)) {
                ShareKey ann = cls.getAnnotation(ShareKey.class);
                SharedPreferences shared = context.getSharedPreferences(ann.key(), 0);
                for (Field field : cls.getFields()) {
                    if (field.isAnnotationPresent(ShareKey.class)) {
                        ShareKey tmp = field.getAnnotation(ShareKey.class);
                        if (field.getType() == String.class) {
                            field.set(value, shared.getString(tmp.key(), (String) field.get(value)));
                        } else if (field.getType() == int.class) {
                            field.setInt(value, shared.getInt(tmp.key(), field.getInt(value)));
                        } else if (field.getType() == boolean.class) {
                            field.setBoolean(value, shared.getBoolean(tmp.key(), field.getBoolean(value)));
                        }
                    }
                }
            }
        }catch (Exception e) {
            AAILogger.e(TAG, "unmarshal Exception:" + Log.getStackTraceString(e));
        }
        return value;
    }

    public static <T> void marshal(Context context, T value) {
        try {
            Class<T> cls = (Class<T>) value.getClass();
            if (cls.isAnnotationPresent(ShareKey.class)) {
                ShareKey ann = cls.getAnnotation(ShareKey.class);
                SharedPreferences shared = context.getSharedPreferences(ann.key(), 0);
                SharedPreferences.Editor editor = shared.edit();
                for (Field field : cls.getFields()) {
                    if (field.isAnnotationPresent(ShareKey.class)) {
                        ShareKey tmp = field.getAnnotation(ShareKey.class);
                        if (field.getType() == String.class) {
                            editor.putString(tmp.key(), (String)field.get(value));
                        } else if (field.getType() == int.class) {
                            editor.putInt(tmp.key(), field.getInt(value));
                        } else if (field.getType() == boolean.class) {
                            editor.putBoolean(tmp.key(), field.getBoolean(value));
                        }
                    }
                }
                editor.apply();
            }
        }catch (Exception e) {
            AAILogger.e(TAG, "marshal Exception:" + Log.getStackTraceString(e));
        }
    }
}
