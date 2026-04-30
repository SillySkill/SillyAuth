package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.util.Base64;
import android.util.Log;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

/**
 * 火山引擎TOS上传管理器
 * 使用火山引擎TOS API进行文件上传
 */
public class TosUploadManager {

    private static final String TAG = "TosUploadManager";
    private static TosUploadManager instance;
    private Context context;

    // TOS配置
    private String accessKeyId;
    private String secretAccessKey;
    private String region;
    private String endpoint;
    private String bucket;
    private String customDomain;

    private TosUploadManager(Context context) {
        this.context = context.getApplicationContext();
        loadConfig();
    }

    public static synchronized TosUploadManager getInstance(Context context) {
        if (instance == null) {
            instance = new TosUploadManager(context);
        }
        return instance;
    }

    /**
     * 加载TOS配置（每次上传时重新获取，确保使用最新配置）
     */
    private void loadConfig() {
        com.google.gson.JsonObject config = ConfigManager.getInstance(context).getTosConfig();
        this.accessKeyId = config.get("access_key_id").getAsString();
        this.secretAccessKey = config.get("secret_access_key").getAsString();
        this.region = config.get("region").getAsString();
        this.endpoint = config.get("endpoint").getAsString();
        this.bucket = config.get("bucket").getAsString();
        this.customDomain = config.get("custom_domain").getAsString();

        Log.d(TAG, "TOS配置加载完成: bucket=" + bucket + ", endpoint=" + endpoint + ", domain=" + customDomain);
    }

    /**
     * 上传文件到TOS
     * @param file 要上传的文件
     * @param objectKey OSS对象键（路径）
     * @param callback 上传回调
     */
    public void uploadFile(File file, String objectKey, final UploadCallback callback) {
        new Thread(() -> {
            try {
                Log.d(TAG, "开始上传文件到TOS: " + file.getName() + " -> " + objectKey);

                // 读取文件内容
                FileInputStream fis = new FileInputStream(file);
                byte[] fileData = new byte[(int) file.length()];
                fis.read(fileData);
                fis.close();

                // 使用自定义域名上传（更简单，不需要签名）
                String urlString = customDomain + "/" + objectKey;
                Log.d(TAG, "上传URL: " + urlString);
                URL url = new URL(urlString);

                // 创建HTTP连接
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("PUT");
                conn.setDoOutput(true);
                conn.setConnectTimeout(60000);
                conn.setReadTimeout(300000);

                // 设置请求头
                String contentType = getContentType(file.getName());
                conn.setRequestProperty("Content-Type", contentType);

                // 发送文件数据
                OutputStream os = conn.getOutputStream();
                os.write(fileData);
                os.flush();
                os.close();

                // 获取响应
                int responseCode = conn.getResponseCode();
                Log.d(TAG, "TOS上传响应码: " + responseCode);

                if (responseCode == 200) {
                    // 上传成功，使用自定义域名URL
                    String fileUrl = customDomain + "/" + objectKey;
                    Log.d(TAG, "TOS上传成功: " + fileUrl);
                    callback.onSuccess(fileUrl);
                } else {
                    // 读取错误信息
                    BufferedReader errorReader = new BufferedReader(new InputStreamReader(conn.getErrorStream()));
                    StringBuilder error = new StringBuilder();
                    String line;
                    while ((line = errorReader.readLine()) != null) {
                        error.append(line);
                    }
                    Log.e(TAG, "TOS上传失败: " + responseCode + ", " + error.toString());
                    callback.onError("上传失败: HTTP " + responseCode);
                }

                conn.disconnect();

            } catch (Exception e) {
                Log.e(TAG, "TOS上传异常", e);
                callback.onError("上传异常: " + e.getMessage());
            }
        }).start();
    }

    /**
     * 生成TOS API授权头
     */
    private String generateAuthorization(String method, String objectKey, String contentType, String date, byte[] data) {
        try {
            // 计算Content-MD5
            String contentMd5 = calculateMD5(data);

            // 构建待签名字符串
            StringBuilder stringToSign = new StringBuilder();
            stringToSign.append(method).append("\n");
            stringToSign.append(contentMd5).append("\n");
            stringToSign.append(contentType).append("\n");
            stringToSign.append(date).append("\n");
            stringToSign.append("/").append(bucket).append("/").append(objectKey);

            Log.d(TAG, "待签名字符串: " + stringToSign.toString());

            // 使用HMAC-SHA1签名
            String signature = hmacSha1(stringToSign.toString(), decodeBase64(secretAccessKey));

            // 构建Authorization头
            return "TOS " + accessKeyId + ":" + signature;

        } catch (Exception e) {
            Log.e(TAG, "生成授权头失败", e);
            throw new RuntimeException("生成授权头失败", e);
        }
    }

    /**
     * 计算MD5
     */
    private String calculateMD5(byte[] data) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] hash = md.digest(data);
        return Base64.encodeToString(hash, Base64.NO_WRAP);
    }

    /**
     * HMAC-SHA1签名
     */
    private String hmacSha1(String data, byte[] key) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA1");
        SecretKeySpec secretKeySpec = new SecretKeySpec(key, "HmacSHA1");
        mac.init(secretKeySpec);
        byte[] signature = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));
        return Base64.encodeToString(signature, Base64.NO_WRAP);
    }

    /**
     * 解码Base64
     */
    private byte[] decodeBase64(String encoded) {
        return Base64.decode(encoded, Base64.NO_WRAP);
    }

    /**
     * 获取GMT格式日期
     */
    private String getGMTDate() {
        SimpleDateFormat sdf = new SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss z", Locale.US);
        sdf.setTimeZone(TimeZone.getTimeZone("GMT"));
        return sdf.format(new Date());
    }

    /**
     * 根据文件名获取Content-Type
     */
    private String getContentType(String fileName) {
        String extension = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase();
        switch (extension) {
            case "jpg":
            case "jpeg":
                return "image/jpeg";
            case "png":
                return "image/png";
            case "gif":
                return "image/gif";
            case "webp":
                return "image/webp";
            default:
                return "application/octet-stream";
        }
    }

    /**
     * 上传回调接口
     */
    public interface UploadCallback {
        void onSuccess(String fileUrl);
        void onError(String error);
    }
}
