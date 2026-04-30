package com.jcoding.aiactivity.utils;

/**
 * 应用常量定义
 */
public class Constants {

    // 应用信息
    public static final String APP_NAME = "AI活动秀";
    public static final String APP_VERSION = "1.0.0";

    // Intent Extra键
    public static final String EXTRA_STYLE_ID = "style_id";
    public static final String EXTRA_IMAGE_URL = "image_url";
    public static final String EXTRA_USER_NAME = "user_name";
    public static final String EXTRA_MODE = "mode";
    public static final String EXTRA_QUESTION_BANK = "question_bank";
    public static final String EXTRA_LOTTERY_PROGRAM = "lottery_program";

    // 参与模式
    public static final int MODE_CAMERA = 0;       // 直接相机模式（跳过验证）
    public static final int MODE_INVITE_CODE = 1;  // 邀请码模式
    public static final int MODE_PAYMENT = 2;      // 支付模式
    public static final int MODE_EMPLOYEE = 3;     // 员工模式

    // 照片来源
    public static final int PHOTO_SOURCE_CAMERA = 1;  // 现场拍摄
    public static final int PHOTO_SOURCE_UPLOAD = 2;  // 手机上传

    // 文件上传
    // 上传API端点：https://www.sillymd.com/upload/api
    public static final String UPLOAD_PROXY_URL = "https://www.sillymd.com/upload/api";
    public static final String UPLOAD_SOURCE_CAMERA = "camera";
    public static final String UPLOAD_SOURCE_FILE = "file";

    // 后端服务基础URL
    public static final String BACKEND_BASE_URL = "https://www.sillymd.com/application/com.jcoding.aiactivity";

    // 网络请求
    public static final int NETWORK_TIMEOUT = 30; // 秒

    // 存储键
    public static final String PREF_NAME = "ai_activity_prefs";
    public static final String PREF_USER_ID = "user_id";
    public static final String PREF_USER_NAME = "user_name";
    public static final String PREF_IS_LOGGED_IN = "is_logged_in";
    public static final String PREF_CONFIG_VERSION = "config_version";
    public static final String PREF_PHOTO_SOURCE_MODE = "photo_source_mode";  // 拍照方式：1=本机摄像头，2=扫码上传

    // AI生成状态
    public static final int GENERATION_STATUS_PENDING = 0;
    public static final int GENERATION_STATUS_PROCESSING = 1;
    public static final int GENERATION_STATUS_COMPLETED = 2;
    public static final int GENERATION_STATUS_FAILED = 3;

    // 数字人动作
    public static final String AIBEING_ACTION_OPEN_HAND = "open_hand";
    public static final String AIBEING_ACTION_SAY_HELLO = "say_hello";
    public static final String AIBEING_ACTION_APPLAUD = "applaud";
    public static final String AIBEING_ACTION_SALUTE = "salute";
    public static final String AIBEING_ACTION_INTRODUCE = "introduce";
    public static final String AIBEING_ACTION_CONGRATULATE = "congratulate";
    public static final String AIBEING_ACTION_LEFT_POINT = "left_point";

    private Constants() {
        // 防止实例化
    }
}
