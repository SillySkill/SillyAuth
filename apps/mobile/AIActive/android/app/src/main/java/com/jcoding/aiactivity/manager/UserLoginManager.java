package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.text.TextUtils;

import com.jcoding.aiactivity.utils.PreferenceUtils;

/**
 * 用户登录管理器
 * 管理用户登录状态和信息
 */
public class UserLoginManager {

    private static final String PREF_USER_LOGIN = "user_login";
    private static final String KEY_LOGGED_IN = "logged_in";
    private static final String KEY_USER_ID = "user_id";
    private static final String KEY_USER_NAME = "user_name";
    private static final String KEY_USER_PHONE = "user_phone";
    private static final String KEY_USER_EMAIL = "user_email";
    private static final String KEY_LOGIN_TIME = "login_time";
    private static final String KEY_QR_CODE = "qr_code";  // 扫码登录的二维码

    private static UserLoginManager instance;
    private Context context;

    private UserLoginManager(Context context) {
        this.context = context.getApplicationContext();
    }

    public static synchronized UserLoginManager getInstance(Context context) {
        if (instance == null) {
            instance = new UserLoginManager(context);
        }
        return instance;
    }

    /**
     * 用户信息实体
     */
    public static class UserInfo {
        public String userId;
        public String userName;
        public String userPhone;
        public String userEmail;
        public long loginTime;
        public String qrCode;  // 扫码登录的二维码内容

        public UserInfo() {
            this.loginTime = System.currentTimeMillis();
        }
    }

    /**
     * 用户登录
     */
    public void login(UserInfo userInfo) {
        PreferenceUtils.putBoolean(context, KEY_LOGGED_IN, true);
        PreferenceUtils.putString(context, KEY_USER_ID, userInfo.userId);
        PreferenceUtils.putString(context, KEY_USER_NAME, userInfo.userName);
        PreferenceUtils.putString(context, KEY_USER_PHONE, userInfo.userPhone);
        PreferenceUtils.putString(context, KEY_USER_EMAIL, userInfo.userEmail);
        PreferenceUtils.putLong(context, KEY_LOGIN_TIME, userInfo.loginTime);
        PreferenceUtils.putString(context, KEY_QR_CODE, userInfo.qrCode);
    }

    /**
     * 用户登出
     */
    public void logout() {
        PreferenceUtils.putBoolean(context, KEY_LOGGED_IN, false);
        PreferenceUtils.putString(context, KEY_USER_ID, "");
        PreferenceUtils.putString(context, KEY_USER_NAME, "");
        PreferenceUtils.putString(context, KEY_USER_PHONE, "");
        PreferenceUtils.putString(context, KEY_USER_EMAIL, "");
        PreferenceUtils.putLong(context, KEY_LOGIN_TIME, 0);
        PreferenceUtils.putString(context, KEY_QR_CODE, "");
    }

    /**
     * 是否已登录
     */
    public boolean isLoggedIn() {
        return PreferenceUtils.getBoolean(context, KEY_LOGGED_IN, false);
    }

    /**
     * 获取当前登录用户信息
     */
    public UserInfo getCurrentUser() {
        if (!isLoggedIn()) {
            return null;
        }

        UserInfo userInfo = new UserInfo();
        userInfo.userId = PreferenceUtils.getString(context, KEY_USER_ID, "");
        userInfo.userName = PreferenceUtils.getString(context, KEY_USER_NAME, "");
        userInfo.userPhone = PreferenceUtils.getString(context, KEY_USER_PHONE, "");
        userInfo.userEmail = PreferenceUtils.getString(context, KEY_USER_EMAIL, "");
        userInfo.loginTime = PreferenceUtils.getLong(context, KEY_LOGIN_TIME, 0);
        userInfo.qrCode = PreferenceUtils.getString(context, KEY_QR_CODE, "");

        return userInfo;
    }

    /**
     * 获取用户ID
     */
    public String getUserId() {
        UserInfo user = getCurrentUser();
        return user != null ? user.userId : "";
    }

    /**
     * 获取用户名
     */
    public String getUserName() {
        UserInfo user = getCurrentUser();
        return user != null ? user.userName : "";
    }

    /**
     * 获取用户手机号
     */
    public String getUserPhone() {
        UserInfo user = getCurrentUser();
        return user != null ? user.userPhone : "";
    }

    /**
     * 通过二维码登录（扫码后调用）
     */
    public void loginByQrCode(String qrCode, String userId, String userName) {
        UserInfo userInfo = new UserInfo();
        userInfo.qrCode = qrCode;
        userInfo.userId = userId;
        userInfo.userName = userName;
        login(userInfo);
    }

    /**
     * 获取登录二维码
     */
    public String getQrCode() {
        return PreferenceUtils.getString(context, KEY_QR_CODE, "");
    }

    /**
     * 检查是否是指定二维码登录
     */
    public boolean isQrCodeLogin(String qrCode) {
        String savedQrCode = getQrCode();
        return !TextUtils.isEmpty(savedQrCode) && savedQrCode.equals(qrCode);
    }
}
