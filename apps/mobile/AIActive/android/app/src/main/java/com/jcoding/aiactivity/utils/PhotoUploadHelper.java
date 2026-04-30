package com.jcoding.aiactivity.utils;

import android.content.Context;
import android.util.Log;

import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * 照片上传助手
 * 负责将拍摄的照片上传到配置的服务器
 */
public class PhotoUploadHelper {

    private static final String TAG = "PhotoUploadHelper";
    private static final String UPLOAD_SOURCE = "camera"; // 来源：相机拍照

    private Context context;
    private String uploadUrl;
    private OkHttpClient httpClient;

    public PhotoUploadHelper(Context context, String uploadUrl) {
        this.context = context.getApplicationContext();
        this.uploadUrl = uploadUrl;

        // 配置HTTP客户端
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(60, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();
    }

    /**
     * 上传照片
     *
     * @param photoFilePath 照片文件路径
     * @param callback      上传回调
     */
    public void uploadPhoto(String photoFilePath, UploadCallback callback) {
        File photoFile = new File(photoFilePath);

        if (!photoFile.exists()) {
            callback.onError("照片文件不存在");
            return;
        }

        // 创建请求体
        RequestBody fileBody = RequestBody.create(
                MediaType.parse("image/jpeg"),
                photoFile
        );

        // 创建multipart body
        MultipartBody.Part body = MultipartBody.Part.createFormData(
                "file",
                photoFile.getName(),
                fileBody
        );

        // 添加source参数
        RequestBody sourceBody = RequestBody.create(
                MediaType.parse("text/plain"),
                UPLOAD_SOURCE
        );

        // 执行上传
        uploadMultipart(body, sourceBody, callback);
    }

    /**
     * 执行multipart上传
     */
    private void uploadMultipart(MultipartBody.Part filePart,
                                 RequestBody sourcePart,
                                 UploadCallback callback) {
        try {
            okhttp3.Request request = new okhttp3.Request.Builder()
                    .url(uploadUrl)
                    .post(new MultipartBody.Builder()
                            .setType(MultipartBody.FORM)
                            .addPart(filePart)
                            .addFormDataPart("source", UPLOAD_SOURCE)
                            .build())
                    .build();

            httpClient.newCall(request).enqueue(new okhttp3.Callback() {
                @Override
                public void onFailure(okhttp3.Call call, IOException e) {
                    Log.e(TAG, "上传失败", e);
                    callback.onError("上传失败: " + e.getMessage());
                }

                @Override
                public void onResponse(okhttp3.Call call, okhttp3.Response response) throws IOException {
                    try {
                        if (response.isSuccessful()) {
                            String responseData = response.body() != null ? response.body().string() : "";
                            Log.d(TAG, "上传成功: " + responseData);
                            callback.onSuccess(responseData);
                        } else {
                            String errorBody = response.body() != null ? response.body().string() : "未知错误";
                            Log.e(TAG, "上传失败: " + response.code() + " - " + errorBody);
                            callback.onError("上传失败: " + errorBody);
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "处理响应失败", e);
                        callback.onError("处理响应失败: " + e.getMessage());
                    } finally {
                        response.close();
                    }
                }
            });

        } catch (Exception e) {
            Log.e(TAG, "创建上传请求失败", e);
            callback.onError("创建上传请求失败: " + e.getMessage());
        }
    }

    /**
     * 上传回调接口
     */
    public interface UploadCallback {
        void onSuccess(String response);
        void onError(String error);
    }
}
