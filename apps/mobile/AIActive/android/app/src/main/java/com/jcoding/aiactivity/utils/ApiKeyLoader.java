package com.jcoding.aiactivity.utils;

import android.content.Context;
import android.text.TextUtils;
import android.util.Log;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

/**
 * API密钥加载工具类
 * 从assets目录加载第三方API密钥
 */
public class ApiKeyLoader {

    private static final String TAG = "ApiKeyLoader";

    /**
     * 从assets加载MiniMax API Key
     * @param context 上下文
     * @return API Key，加载失败返回null
     */
    public static String loadMiniMaxApiKey(Context context) {
        return loadApiKeyFromAssets(context, "minimax/api.txt");
    }

    /**
     * 从assets加载MiniMax Group ID
     * @param context 上下文
     * @return Group ID，加载失败返回null
     */
    public static String loadMiniMaxGroupId(Context context) {
        return loadApiKeyFromAssets(context, "minimax/group.txt");
    }

    /**
     * 从assets加载腾讯TTS凭证（JSON格式）
     * @param context 上下文
     * @return 包含所有TTS认证字段的JSONObject，加载失败返回null
     */
    public static TencentTTSCredentials loadTencentTTSCredentials(Context context) {
        try {
            InputStream inputStream = context.getAssets().open("tts/SDK_Key.json");
            BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            reader.close();
            inputStream.close();

            String jsonStr = sb.toString();
            JSONObject jsonObject = new JSONObject(jsonStr);

            // 读取所有必需字段
            String secretId = jsonObject.optString("offline_online_secret_id", "");
            String secretKey = jsonObject.optString("offline_online_secret_key", "");
            String licKey = jsonObject.optString("offline_online_lic_key", "");
            String licPk = jsonObject.optString("offline_online_lic_pk", "");
            String lic = jsonObject.optString("offline_lic", "");
            String licSign = jsonObject.optString("offline_lic_sign", "");
            String licPk2 = jsonObject.optString("offline_lic_pk", "");

            TencentTTSCredentials credentials = new TencentTTSCredentials(
                secretId, secretKey, licKey, licPk, lic, licSign, licPk2);

            Log.i(TAG, "Tencent TTS credentials loaded from SDK_Key.json");
            return credentials;

        } catch (IOException e) {
            Log.e(TAG, "Failed to load Tencent TTS credentials from JSON", e);
            return null;
        } catch (Exception e) {
            Log.e(TAG, "Failed to parse Tencent TTS credentials JSON", e);
            return null;
        }
    }

    /**
     * 腾讯TTS凭证容器类
     */
    public static class TencentTTSCredentials {
        public final String secretId;
        public final String secretKey;
        public final String licKey;
        public final String licPk;
        public final String lic;
        public final String licSign;
        public final String licPk2;

        public TencentTTSCredentials(String secretId, String secretKey, String licKey,
                                   String licPk, String lic, String licSign, String licPk2) {
            this.secretId = secretId;
            this.secretKey = secretKey;
            this.licKey = licKey;
            this.licPk = licPk;
            this.lic = lic;
            this.licSign = licSign;
            this.licPk2 = licPk2;
        }

        public boolean hasOnlineAuthParams() {
            return !TextUtils.isEmpty(secretId) && !TextUtils.isEmpty(secretKey);
        }

        public boolean hasOfflineAuthParams() {
            return !TextUtils.isEmpty(lic) && !TextUtils.isEmpty(licSign);
        }
    }

    /**
     * 从assets加载API密钥文件
     * @param context 上下文
     * @param filePath assets中的文件路径
     * @return API Key，加载失败返回null
     */
    private static String loadApiKeyFromAssets(Context context, String filePath) {
        InputStream inputStream = null;
        BufferedReader reader = null;

        try {
            inputStream = context.getAssets().open(filePath);
            reader = new BufferedReader(new InputStreamReader(inputStream));

            String apiKey = reader.readLine();
            if (!TextUtils.isEmpty(apiKey)) {
                apiKey = apiKey.trim();
                // 隐藏中间部分用于日志输出
                String maskedKey = maskApiKey(apiKey);
                Log.i(TAG, "API key loaded from " + filePath + ": " + maskedKey);
                return apiKey;
            }

            Log.w(TAG, "API key file is empty: " + filePath);
            return null;

        } catch (IOException e) {
            Log.e(TAG, "Failed to load API key from " + filePath, e);
            return null;
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    Log.e(TAG, "Failed to close reader", e);
                }
            }
            if (inputStream != null) {
                try {
                    inputStream.close();
                } catch (IOException e) {
                    Log.e(TAG, "Failed to close input stream", e);
                }
            }
        }
    }

    /**
     * 隐藏API密钥中间部分用于日志输出
     */
    private static String maskApiKey(String apiKey) {
        if (TextUtils.isEmpty(apiKey) || apiKey.length() < 10) {
            return "***";
        }

        int showLength = 8;
        if (apiKey.length() <= 16) {
            showLength = 4;
        }

        return apiKey.substring(0, showLength) + "..." + apiKey.substring(apiKey.length() - 4);
    }
}
