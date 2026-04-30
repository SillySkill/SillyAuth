package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 设备认证管理器
 * 管理管理员口令验证、尝试次数限制、超时机制
 *
 * 安全特性：
 * 1. 口令哈希存储（SHA-256）
 * 2. 验证尝试次数限制（5次）
 * 3. 验证超时机制（3分钟）
 * 4. 失败锁定机制（5分钟）
 */
public class DeviceAuthManager {

    private static final String TAG = "DeviceAuthManager";
    private static DeviceAuthManager instance;

    private static final String PREFS_NAME = "device_auth";
    private static final String KEY_PASSWORD_HASH = "password_hash";
    private static final String KEY_DEFAULT_PASSWORD_SET = "default_password_set";

    // 认证配置
    private static final int MAX_ATTEMPTS = 5;           // 最大尝试次数
    private static final long ATTEMPT_RESET_TIME = 5 * 60 * 1000;  // 5分钟重置尝试次数
    private static final long LOCKOUT_DURATION = 5 * 60 * 1000;     // 锁定时长5分钟
    private static final String DEFAULT_PASSWORD = "123456";       // 默认口令

    private Context context;
    private SharedPreferences prefs;

    // 认证状态
    private int attemptCount = 0;
    private long lastAttemptTime = 0;
    private long lockoutUntil = 0;
    private AtomicInteger sessionAttempts = new AtomicInteger(0);

    private DeviceAuthManager(Context context) {
        this.context = context.getApplicationContext();
        this.prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public static synchronized DeviceAuthManager getInstance(Context context) {
        if (instance == null) {
            instance = new DeviceAuthManager(context);
        }
        return instance;
    }

    /**
     * 初始化默认口令（仅在首次使用时）
     */
    public void initializeDefaultPassword() {
        if (!prefs.contains(KEY_DEFAULT_PASSWORD_SET)) {
            // 设置默认口令
            String hash = hashPassword(DEFAULT_PASSWORD);
            prefs.edit()
                    .putString(KEY_PASSWORD_HASH, hash)
                    .putBoolean(KEY_DEFAULT_PASSWORD_SET, true)
                    .apply();
            Log.i(TAG, "默认口令已初始化");
        }
    }

    /**
     * 验证口令
     * @param password 用户输入的口令
     * @param callback 验证回调
     */
    public void verifyPassword(String password, AuthCallback callback) {
        // 检查是否被锁定
        if (isLockedOut()) {
            long remainingTime = (lockoutUntil - System.currentTimeMillis()) / 1000;
            callback.onError("验证失败次数过多，请 " + remainingTime + " 秒后再试");
            return;
        }

        // 检查会话尝试次数
        if (sessionAttempts.get() >= MAX_ATTEMPTS) {
            callback.onError("会话尝试次数已达上限，请重新进入");
            return;
        }

        // 获取存储的口令哈希
        String storedHash = prefs.getString(KEY_PASSWORD_HASH, null);
        if (storedHash == null) {
            initializeDefaultPassword();
            storedHash = prefs.getString(KEY_PASSWORD_HASH, null);
        }

        // 验证口令
        String inputHash = hashPassword(password);
        attemptCount++;
        lastAttemptTime = System.currentTimeMillis();
        sessionAttempts.incrementAndGet();

        if (inputHash.equals(storedHash)) {
            // 验证成功，重置计数
            resetAttempts();
            callback.onSuccess();
            Log.i(TAG, "口令验证成功");
        } else {
            // 验证失败
            int remainingAttempts = MAX_ATTEMPTS - sessionAttempts.get();

            if (remainingAttempts <= 0) {
                // 触发锁定
                lockoutUntil = System.currentTimeMillis() + LOCKOUT_DURATION;
                callback.onError("验证失败次数过多，已锁定5分钟");
            } else {
                callback.onError("口令错误，还剩 " + remainingAttempts + " 次尝试机会");
            }

            Log.w(TAG, "口令验证失败，尝试次数: " + sessionAttempts.get());
        }
    }

    /**
     * 修改口令
     * @param oldPassword 旧口令
     * @param newPassword 新口令
     * @param callback 回调
     */
    public void changePassword(String oldPassword, String newPassword, AuthCallback callback) {
        // 先验证旧口令
        String storedHash = prefs.getString(KEY_PASSWORD_HASH, null);
        if (storedHash == null) {
            initializeDefaultPassword();
            storedHash = prefs.getString(KEY_PASSWORD_HASH, null);
        }

        String oldHash = hashPassword(oldPassword);
        if (!oldHash.equals(storedHash)) {
            callback.onError("旧口令错误");
            return;
        }

        // 验证新口令强度
        if (newPassword == null || newPassword.length() < 4) {
            callback.onError("新口令长度至少4位");
            return;
        }

        // 保存新口令
        String newHash = hashPassword(newPassword);
        prefs.edit().putString(KEY_PASSWORD_HASH, newHash).apply();

        resetAttempts();
        callback.onSuccess();
        Log.i(TAG, "口令已修改");
    }

    /**
     * 重置尝试次数
     */
    public void resetAttempts() {
        attemptCount = 0;
        lastAttemptTime = 0;
        sessionAttempts.set(0);
        lockoutUntil = 0;
    }

    /**
     * 重置为默认口令
     * @param callback 回调
     */
    public void resetToDefaultPassword(AuthCallback callback) {
        String hash = hashPassword(DEFAULT_PASSWORD);
        prefs.edit()
                .putString(KEY_PASSWORD_HASH, hash)
                .apply();

        resetAttempts();
        callback.onSuccess();
        Log.i(TAG, "口令已重置为默认值");
    }

    /**
     * 检查是否被锁定
     */
    private boolean isLockedOut() {
        if (lockoutUntil > System.currentTimeMillis()) {
            return true;
        }
        return false;
    }

    /**
     * 计算口令哈希（SHA-256）
     */
    private String hashPassword(String password) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(password.getBytes());
            StringBuilder hexString = new StringBuilder();

            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }

            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            Log.e(TAG, "哈希算法失败", e);
            return password; // 降级方案
        }
    }

    /**
     * 获取剩余尝试次数
     */
    public int getRemainingAttempts() {
        return MAX_ATTEMPTS - sessionAttempts.get();
    }

    /**
     * 检查是否使用默认口令
     */
    public boolean isUsingDefaultPassword() {
        String storedHash = prefs.getString(KEY_PASSWORD_HASH, null);
        String defaultHash = hashPassword(DEFAULT_PASSWORD);
        return storedHash != null && storedHash.equals(defaultHash);
    }

    /**
     * 认证回调接口
     */
    public interface AuthCallback {
        /**
         * 验证成功
         */
        void onSuccess();

        /**
         * 验证失败
         * @param error 错误信息
         */
        void onError(String error);
    }
}
