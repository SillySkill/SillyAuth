package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.webkit.MimeTypeMap;

import com.jcoding.aiactivity.network.ApiService;
import com.jcoding.aiactivity.network.RetrofitClient;
import com.jcoding.aiactivity.utils.Constants;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * 文件上传管理器
 */
public class FileUploadManager {

    private static FileUploadManager instance;
    private Context context;

    private FileUploadManager(Context context) {
        this.context = context.getApplicationContext();
    }

    public static synchronized FileUploadManager getInstance(Context context) {
        if (instance == null) {
            instance = new FileUploadManager(context);
        }
        return instance;
    }

    /**
     * 上传文件接口
     */
    public interface UploadCallback {
        void onSuccess(String fileUrl);
        void onError(String error);
    }

    /**
     * 上传文件
     *
     * @param file    要上传的文件
     * @param source  来源：camera=相机，file=文件
     * @param callback 回调
     */
    public void uploadFile(File file, String source, UploadCallback callback) {
        // 调用新方法，默认module为style
        uploadGeneratedFile(file, "style", source, null, null, false, callback);
    }

    /**
     * 上传生成的文件（支持完整参数）
     *
     * @param file          要上传的文件
     * @param module        模块名：style/gen/quiz等
     * @param source        来源标识
     * @param sessionId     会话ID（可选）
     * @param parentFileId  父文件ID（可选）
     * @param isGenerated   是否为生成的文件
     * @param callback      回调
     */
    public void uploadGeneratedFile(File file, String module, String source,
                                    String sessionId, String parentFileId,
                                    boolean isGenerated, UploadCallback callback) {
        // 获取当前存储策略
        ConfigManager configManager = ConfigManager.getInstance(context);
        String storageStrategy = configManager.getStorageStrategy();

        android.util.Log.d("FileUploadManager", "当前存储策略: " + storageStrategy);

        if (ConfigManager.StorageStrategy.TOS.equals(storageStrategy)) {
            // 使用TOS直接上传
            uploadToTos(file, module, callback);
        } else {
            // 使用后端代理上传到OSS
            uploadViaProxy(file, module, source, sessionId, parentFileId, isGenerated, callback);
        }
    }

    /**
     * 直接上传到TOS
     */
    private void uploadToTos(File file, String module, UploadCallback callback) {
        try {
            // 生成object key
            String timestamp = String.valueOf(System.currentTimeMillis());
            String extension = file.getName().substring(file.getName().lastIndexOf('.'));
            String objectKey = "application/com.jcoding.aiactivity/" + module + "/" + timestamp + "_" + file.getName();

            android.util.Log.d("FileUploadManager", "上传到TOS: " + objectKey);

            TosUploadManager.getInstance(context).uploadFile(file, objectKey,
                new TosUploadManager.UploadCallback() {
                    @Override
                    public void onSuccess(String fileUrl) {
                        android.util.Log.d("FileUploadManager", "TOS上传成功: " + fileUrl);
                        callback.onSuccess(fileUrl);
                    }

                    @Override
                    public void onError(String error) {
                        android.util.Log.e("FileUploadManager", "TOS上传失败: " + error);
                        callback.onError(error);
                    }
                }
            );
        } catch (Exception e) {
            android.util.Log.e("FileUploadManager", "TOS上传异常", e);
            callback.onError("上传失败: " + e.getMessage());
        }
    }

    /**
     * 通过后端代理上传到OSS
     */
    private void uploadViaProxy(File file, String module, String source,
                                String sessionId, String parentFileId,
                                boolean isGenerated, UploadCallback callback) {
        new Thread(() -> {
            try {
                android.util.Log.d("FileUploadManager", "通过后端代理上传到OSS");

                // 使用OkHttp直接上传，支持完整参数
                okhttp3.OkHttpClient client = new okhttp3.OkHttpClient.Builder()
                        .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                        .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                        .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                        .build();

                // 构建multipart请求体
                okhttp3.MultipartBody.Builder builder = new okhttp3.MultipartBody.Builder()
                        .setType(okhttp3.MultipartBody.FORM);

                // 添加文件
                RequestBody requestFile = RequestBody.create(
                        okhttp3.MediaType.parse(getMimeType(file)),
                        file
                );
                builder.addFormDataPart("file", file.getName(), requestFile);

                // 添加module参数
                builder.addFormDataPart("module", module);

                // 添加source参数
                builder.addFormDataPart("source", source);

                // 添加可选参数
                if (sessionId != null && !sessionId.isEmpty()) {
                    builder.addFormDataPart("session_id", sessionId);
                }

                if (parentFileId != null && !parentFileId.isEmpty()) {
                    builder.addFormDataPart("parent_file_id", parentFileId);
                }

                if (isGenerated) {
                    builder.addFormDataPart("is_generated", "true");
                }

                okhttp3.RequestBody requestBody = builder.build();

                // 构建请求
                okhttp3.Request request = new okhttp3.Request.Builder()
                        .url(Constants.UPLOAD_PROXY_URL)
                        .post(requestBody)
                        .build();

                // 执行请求
                okhttp3.Response response = client.newCall(request).execute();

                if (response.isSuccessful() && response.body() != null) {
                    String responseBody = response.body().string();
                    org.json.JSONObject jsonResponse = new org.json.JSONObject(responseBody);

                    int code = jsonResponse.optInt("code", -1);
                    if (code == 200 && jsonResponse.has("data")) {
                        String fileUrl = jsonResponse.optJSONObject("data").optString("url", "");
                        if (!fileUrl.isEmpty()) {
                            callback.onSuccess(fileUrl);
                        } else {
                            callback.onError("上传成功但未返回URL");
                        }
                    } else {
                        String message = jsonResponse.optString("message", "上传失败");
                        callback.onError("上传失败：" + message);
                    }
                } else {
                    callback.onError("上传失败：HTTP " + response.code());
                }

            } catch (Exception e) {
                android.util.Log.e("FileUploadManager", "上传异常", e);
                callback.onError("上传失败：" + e.getMessage());
            }
        }).start();
    }

    /**
     * 获取文件的MIME类型
     */
    private String getMimeType(File file) {
        String type = null;
        String extension = MimeTypeMap.getFileExtensionFromUrl(file.getAbsolutePath());
        if (extension != null) {
            type = MimeTypeMap.getSingleton().getMimeTypeFromExtension(extension.toLowerCase());
        }
        if (type == null) {
            type = "image/jpeg";  // 默认图片类型
        }
        return type;
    }

    /**
     * 上传生成的图片URL（后端下载并上传到OSS）
     *
     * @param imageUrl 大模型返回的图片URL（如火山引擎URL）
     * @param sessionId 会话ID
     * @param callback 回调
     */
    public void uploadGeneratedImageUrl(String imageUrl, String sessionId, UploadCallback callback) {
        new Thread(() -> {
            try {
                android.util.Log.d("FileUploadManager", "开始上传生成图片URL: " + imageUrl);

                // 使用OkHttp直接调用后端
                okhttp3.OkHttpClient client = new okhttp3.OkHttpClient.Builder()
                        .connectTimeout(300, java.util.concurrent.TimeUnit.SECONDS)
                        .readTimeout(300, java.util.concurrent.TimeUnit.SECONDS)
                        .writeTimeout(300, java.util.concurrent.TimeUnit.SECONDS)
                        .build();

                // 构建multipart请求体
                okhttp3.MultipartBody.Builder builder = new okhttp3.MultipartBody.Builder()
                        .setType(okhttp3.MultipartBody.FORM);

                // 添加参数
                builder.addFormDataPart("url", imageUrl);
                builder.addFormDataPart("module", "gen");
                builder.addFormDataPart("is_generated", "true");

                if (sessionId != null && !sessionId.isEmpty()) {
                    builder.addFormDataPart("session_id", sessionId);
                }

                okhttp3.RequestBody requestBody = builder.build();

                // 构建请求
                okhttp3.Request request = new okhttp3.Request.Builder()
                        .url(Constants.UPLOAD_PROXY_URL.replace("/upload/api", "/upload/url"))
                        .post(requestBody)
                        .build();

                android.util.Log.d("FileUploadManager", "请求URL: " + Constants.UPLOAD_PROXY_URL.replace("/upload/api", "/upload/url"));

                // 执行请求
                okhttp3.Response response = client.newCall(request).execute();

                if (response.isSuccessful() && response.body() != null) {
                    String responseBody = response.body().string();
                    android.util.Log.d("FileUploadManager", "响应: " + responseBody);

                    org.json.JSONObject jsonResponse = new org.json.JSONObject(responseBody);

                    int code = jsonResponse.optInt("code", -1);
                    if (code == 200 && jsonResponse.has("data")) {
                        String fileUrl = jsonResponse.optJSONObject("data").optString("url", "");
                        if (!fileUrl.isEmpty()) {
                            android.util.Log.d("FileUploadManager", "========== URL上传成功 ==========");
                            android.util.Log.d("FileUploadManager", "返回URL: " + fileUrl);
                            callback.onSuccess(fileUrl);
                        } else {
                            callback.onError("上传成功但未返回URL");
                        }
                    } else {
                        String message = jsonResponse.optString("message", "上传失败");
                        callback.onError("上传失败：" + message);
                    }
                } else {
                    String errorBody = response.body() != null ? response.body().string() : "无响应体";
                    android.util.Log.e("FileUploadManager", "上传失败: " + response.code() + ", " + errorBody);
                    callback.onError("上传失败：HTTP " + response.code());
                }

            } catch (Exception e) {
                android.util.Log.e("FileUploadManager", "上传异常", e);
                callback.onError("上传失败：" + e.getMessage());
            }
        }).start();
    }
}
