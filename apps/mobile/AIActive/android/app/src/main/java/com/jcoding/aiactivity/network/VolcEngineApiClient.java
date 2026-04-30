package com.jcoding.aiactivity.network;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Base64;
import android.util.Log;

import com.jcoding.aiactivity.manager.ConfigManager;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.Headers;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * 火山引擎大模型API客户端
 * 直接调用火山引擎大模型API，无需后端服务器
 */
public class VolcEngineApiClient {

    private static final String TAG = "VolcEngineApiClient";

    // API端点 - 图片生成API
    private static final String API_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/images/generations";

    // 认证信息 - 需要配置实际的API Key
    private String apiKey;
    private String modelId;
    private Context context;

    private OkHttpClient httpClient;

    public VolcEngineApiClient(String apiKey, Context context) {
        this.apiKey = apiKey;
        this.context = context.getApplicationContext();

        // 从配置中获取模型ID
        this.modelId = ConfigManager.getInstance(this.context).getLlmModelId();
        Log.d(TAG, "使用模型ID: " + modelId);

        // 配置HTTP客户端
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(60, TimeUnit.SECONDS)
                .writeTimeout(120, TimeUnit.SECONDS)
                .readTimeout(120, TimeUnit.SECONDS)
                .build();
    }

    /**
     * 生成AI图片
     *
     * @param imageFilePath 用户照片文件路径或URL
     * @param maskImagePath 遮罩图片文件路径或URL（可为null）
     * @param prompt 提示词
     * @param quality 生成质量（720p/1080p/2k/4k）
     * @param callback 回调接口
     */
    public void generateImage(String imageFilePath, String maskImagePath, String prompt,
                             String quality, final GenerationCallback callback) {

        // 在后台线程执行
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String imageUrl = null;  // 图片URL（如果是URL）
                    String imageBase64 = null;  // 图片base64（如果是本地文件）
                    String maskImageUrl = null; // 遮罩URL（如果是URL）

                    // 判断是URL还是本地文件路径
                    Log.d(TAG, "========== 图片类型判断 ==========");
                    Log.d(TAG, "imageFilePath: " + imageFilePath);
                    Log.d(TAG, "maskImagePath: " + maskImagePath);

                    boolean isImageUrl = imageFilePath != null &&
                            (imageFilePath.startsWith("http://") || imageFilePath.startsWith("https://"));

                    Log.d(TAG, "isImageUrl: " + isImageUrl);

                    if (isImageUrl) {
                        // 使用URL
                        imageUrl = imageFilePath;
                        Log.d(TAG, ">>> 使用图片URL: " + imageUrl);
                    } else {
                        // 本地文件，编码为base64
                        Log.d(TAG, ">>> 使用本地文件，开始编码为base64");
                        imageBase64 = encodeImageToBase64(imageFilePath);
                        if (imageBase64 == null) {
                            callback.onError("图片编码失败");
                            return;
                        }
                        Log.d(TAG, ">>> 使用图片base64，长度: " + imageBase64.length());
                    }

                    // 检查mask是URL还是本地路径
                    if (maskImagePath != null) {
                        if (maskImagePath.startsWith("http://") || maskImagePath.startsWith("https://")) {
                            maskImageUrl = maskImagePath;
                            Log.d(TAG, ">>> 使用遮罩URL: " + maskImageUrl);
                        } else {
                            // mask是assets路径，需要上传获取URL
                            Log.d(TAG, ">>> 遮罩是assets路径，需要上传获取URL: " + maskImagePath);
                            // 这里暂时跳过，因为上传mask的逻辑在GenerationActivity中处理
                            // 如果需要，可以在这里添加上传逻辑
                        }
                    }

                    // 2. 构造API请求
                    JSONObject requestBody = buildGenerationRequest(imageUrl, imageBase64, maskImageUrl, prompt, null, null, quality);

                    // 3. 发送API请求
                    String response = sendApiRequest(requestBody);

                    // 4. 解析响应
                    String resultUrl = parseResponse(response);

                    if (resultUrl != null) {
                        callback.onSuccess(resultUrl);
                    } else {
                        callback.onError("解析响应失败");
                    }

                } catch (Exception e) {
                    Log.e(TAG, "生成图片失败", e);
                    callback.onError("生成失败: " + e.getMessage());
                }
            }
        }).start();
    }

    /**
     * 将图片文件编码为base64
     * 支持本地文件路径和HTTP(S) URL
     */
    private String encodeImageToBase64(String imagePath) {
        try {
            Bitmap bitmap;

            // 判断是URL还是本地文件路径
            if (imagePath.startsWith("http://") || imagePath.startsWith("https://")) {
                Log.d(TAG, "检测到URL，开始下载图片: " + imagePath);
                // 从URL下载图片
                bitmap = downloadImage(imagePath);
                if (bitmap == null) {
                    Log.e(TAG, "从URL下载图片失败: " + imagePath);
                    return null;
                }
            } else {
                // 从本地文件读取
                File imageFile = new File(imagePath);
                if (!imageFile.exists()) {
                    Log.e(TAG, "图片文件不存在: " + imagePath);
                    return null;
                }
                Log.d(TAG, "从本地文件读取图片: " + imagePath);

                // 优化：压缩图片以减少大小
                BitmapFactory.Options options = new BitmapFactory.Options();
                options.inSampleSize = 2; // 压缩到1/2大小
                bitmap = BitmapFactory.decodeFile(imagePath, options);

                if (bitmap == null) {
                    Log.e(TAG, "图片解码失败: " + imagePath);
                    return null;
                }
            }

            // 转换为JPEG格式的字节数组
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG, 85, outputStream); // 85%质量

            // 转换为base64
            byte[] imageBytes = outputStream.toByteArray();
            String base64 = Base64.encodeToString(imageBytes, Base64.NO_WRAP);

            // 释放bitmap
            bitmap.recycle();

            Log.d(TAG, "图片编码成功: " + imagePath + ", 大小: " + imageBytes.length + " bytes");
            return base64;

        } catch (Exception e) {
            Log.e(TAG, "图片编码异常: " + imagePath, e);
            return null;
        }
    }

    /**
     * 从URL下载图片
     * @return 下载的Bitmap，失败返回null
     */
    public Bitmap downloadImage(String urlString) {
        // 尝试多次下载，增加成功率
        final int MAX_RETRIES = 3;

        for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            try {
                Log.d(TAG, "开始下载图片 (尝试 " + attempt + "/" + MAX_RETRIES + "): " + urlString);

                // 创建不验证SSL证书的OkHttpClient（用于HTTPS URL）
                // 增加超时时间到90秒，应对网络慢的情况
                OkHttpClient client = new OkHttpClient.Builder()
                        .connectTimeout(90, TimeUnit.SECONDS)
                        .readTimeout(90, TimeUnit.SECONDS)
                        .writeTimeout(90, TimeUnit.SECONDS)
                        .build();

                Request.Builder requestBuilder = new Request.Builder()
                        .url(urlString);

                // 如果是IP地址访问代理URL，添加Host header
                if (urlString.contains("47.96.133.238/api/file/")) {
                    requestBuilder.addHeader("Host", "www.jcoding.chat");
                    Log.d(TAG, "添加Host header: www.jcoding.chat");
                }

                Request request = requestBuilder.build();

                Response response = client.newCall(request).execute();
                if (!response.isSuccessful() || response.body() == null) {
                    Log.e(TAG, "下载图片失败 (尝试 " + attempt + "/" + MAX_RETRIES + ")，响应码: " + response.code());
                    if (attempt < MAX_RETRIES) {
                        continue;  // 重试
                    }
                    return null;
                }

                byte[] imageBytes = response.body().bytes();
                Bitmap bitmap = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.length);

                if (bitmap != null) {
                    Log.d(TAG, "图片下载成功，尺寸: " + bitmap.getWidth() + "x" + bitmap.getHeight());
                    return bitmap;
                } else {
                    Log.e(TAG, "图片解码失败 (尝试 " + attempt + "/" + MAX_RETRIES + ")");
                    if (attempt < MAX_RETRIES) {
                        continue;  // 重试
                    }
                }

            } catch (Exception e) {
                // 输出更详细的错误信息
                String exceptionType = e.getClass().getSimpleName();
                String exceptionMessage = e.getMessage();
                Log.e(TAG, "下载图片异常 (尝试 " + attempt + "/" + MAX_RETRIES + "): " + urlString);
                Log.e(TAG, "异常类型: " + exceptionType);
                Log.e(TAG, "异常消息: " + exceptionMessage);

                if (attempt < MAX_RETRIES) {
                    Log.d(TAG, "等待2秒后重试...");
                    try {
                        Thread.sleep(2000);  // 等待2秒后重试
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        return null;
                    }
                } else {
                    Log.e(TAG, "所有下载尝试均失败");
                }
            }
        }

        return null;
    }

    /**
     * 构建生成请求的JSON
     * 支持单图片和多图片数组格式
     */
    private JSONObject buildGenerationRequest(String imageUrl, String imageBase64, String maskImageUrl,
                                             String prompt, String maskImage, String[] referenceImages,
                                             String quality)
            throws JSONException {

        JSONObject requestBody = new JSONObject();

        // 添加详细日志
        Log.d(TAG, "========== buildGenerationRequest ==========");
        Log.d(TAG, "imageUrl: " + (imageUrl != null ? imageUrl : "null"));
        Log.d(TAG, "imageBase64: " + (imageBase64 != null ? ("length=" + imageBase64.length()) : "null"));
        Log.d(TAG, "maskImageUrl: " + maskImageUrl);
        Log.d(TAG, "maskImage (config): " + maskImage);
        Log.d(TAG, "referenceImages: " + (referenceImages != null ? java.util.Arrays.toString(referenceImages) : "null"));
        Log.d(TAG, "prompt: " + prompt);
        Log.d(TAG, "=======================================");

        // 模型名称 - 使用doubao-seedream-4-5-251128
        requestBody.put("model", "doubao-seedream-4-5-251128");
        Log.d(TAG, "使用模型: doubao-seedream-4-5-251128");

        // 判断是否需要使用数组格式
        boolean useArrayFormat = (maskImageUrl != null && !maskImageUrl.isEmpty()) ||
                (referenceImages != null && referenceImages.length > 0);

        if (useArrayFormat) {
            // 使用数组格式：[maskImage, uploadedImage, referenceImages...]
            org.json.JSONArray imageArray = new org.json.JSONArray();

            // 1. 添加maskImage URL
            if (maskImageUrl != null && !maskImageUrl.isEmpty()) {
                imageArray.put(maskImageUrl);
                Log.d(TAG, "添加maskImage到数组: " + maskImageUrl);
            }

            // 2. 添加用户上传的图片URL
            if (imageUrl != null && !imageUrl.isEmpty()) {
                imageArray.put(imageUrl);
                Log.d(TAG, "添加上传图片URL到数组: " + imageUrl);
            }

            // 3. 添加reference_images
            if (referenceImages != null) {
                for (String ref : referenceImages) {
                    if (ref != null && !ref.isEmpty()) {
                        imageArray.put(ref);
                        Log.d(TAG, "添加reference_image到数组: " + ref);
                    }
                }
            }

            requestBody.put("image", imageArray);
            Log.d(TAG, "使用图片数组格式，数组长度: " + imageArray.length());

        } else {
            // 使用单图片格式
            if (imageUrl != null && !imageUrl.isEmpty()) {
                requestBody.put("image_url", imageUrl);
                Log.d(TAG, "使用图片URL: " + imageUrl);
            } else if (imageBase64 != null) {
                requestBody.put("image", imageBase64);
                Log.d(TAG, "使用图片base64，长度: " + imageBase64.length());
            } else {
                Log.e(TAG, "警告: imageUrl和imageBase64都为null");
            }
        }

        // Prompt提示词
        requestBody.put("prompt", prompt);
        Log.d(TAG, "Prompt: " + prompt);

        // 其他参数
        requestBody.put("sequential_image_generation", "disabled");
        requestBody.put("response_format", "url");
        // doubao-seedream-4-5-251128 支持的尺寸: WIDTHxHEIGHT, 1k, 2k, 4k
        String size = "4k";  // 默认使用 4k 质量
        if (quality != null && !quality.isEmpty()) {
            // 如果配置了质量，转换为API支持的格式
            switch (quality.toLowerCase()) {
                case "720p": size = "1024x1024"; break;  // 720p -> 1024x1024
                case "1080p": size = "2k"; break;         // 1080p -> 2k
                case "2k": size = "2k"; break;
                case "4k": size = "4k"; break;            // 4k -> 4k
                default: size = "4k"; break;
            }
        }
        requestBody.put("size", size);
        Log.d(TAG, "生成尺寸: " + size);
        requestBody.put("stream", false);
        requestBody.put("watermark", false);

        Log.d(TAG, "API请求体: " + requestBody.toString());
        return requestBody;
    }

    /**
     * 发送API请求
     */
    private String sendApiRequest(JSONObject requestBody) throws IOException {
        // 构建请求体
        MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        RequestBody body = RequestBody.create(requestBody.toString(), JSON);

        // 构建请求头
        Headers headers = new Headers.Builder()
                .add("Authorization", "Bearer " + apiKey)
                .add("Content-Type", "application/json")
                .build();

        // 构建请求
        Request request = new Request.Builder()
                .url(API_ENDPOINT)
                .headers(headers)
                .post(body)
                .build();

        // 发送请求
        Response response = httpClient.newCall(request).execute();

        // 获取响应体
        String responseBody = response.body() != null ? response.body().string() : "";

        if (!response.isSuccessful()) {
            Log.e(TAG, "API请求失败: " + response.code() + " - " + responseBody);
            throw new IOException("API请求失败: " + response.code());
        }

        Log.d(TAG, "API响应: " + responseBody);
        return responseBody;
    }

    /**
     * 解析API响应
     */
    private String parseResponse(String responseBody) {
        try {
            Log.d(TAG, "API响应: " + responseBody);
            JSONObject jsonResponse = new JSONObject(responseBody);

            // 检查错误
            if (jsonResponse.has("error")) {
                JSONObject error = jsonResponse.getJSONObject("error");
                String message = error.optString("message", "未知错误");
                Log.e(TAG, "API返回错误: " + message);
                return null;
            }

            // 获取生成的图片URL - 图片生成API返回格式
            // 响应格式: {"data": [{"url": "https://..."}]}
            JSONArray data = jsonResponse.optJSONArray("data");
            if (data != null && data.length() > 0) {
                JSONObject firstImage = data.getJSONObject(0);
                String url = firstImage.optString("url");
                if (url != null && !url.isEmpty()) {
                    Log.d(TAG, "成功提取图片URL: " + url);
                    return url;
                }
            }

            Log.e(TAG, "无法从响应中提取图片URL");
            return null;

        } catch (JSONException e) {
            Log.e(TAG, "解析响应失败", e);
            return null;
        }
    }

    /**
     * 生成AI图片 - 支持多图片数组格式
     * 当有maskImage或reference_images时使用此方法
     *
     * @param imageFilePath 用户照片文件路径或URL
     * @param maskImageUrl 遮罩图片URL（可为null）
     * @param prompt 提示词
     * @param maskImage 配置中的maskImage路径（可为null）
     * @param referenceImages 配置中的reference_images数组（可为null）
     * @param quality 生成质量（720p/1080p/2k/4k）
     * @param callback 回调接口
     */
    public void generateImageWithArray(String imageFilePath, String maskImageUrl, String prompt,
                                        String maskImage, String[] referenceImages,
                                        String quality, final GenerationCallback callback) {

        // 在后台线程执行
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String imageUrl = null;  // 图片URL（如果是URL）
                    String imageBase64 = null;  // 图片base64（如果是本地文件）

                    // 判断是URL还是本地文件路径
                    Log.d(TAG, "========== 图片类型判断（数组格式） ==========");
                    Log.d(TAG, "imageFilePath: " + imageFilePath);
                    Log.d(TAG, "maskImageUrl: " + maskImageUrl);
                    Log.d(TAG, "maskImage (config): " + maskImage);
                    Log.d(TAG, "referenceImages: " + (referenceImages != null ? java.util.Arrays.toString(referenceImages) : "null"));

                    boolean isImageUrl = imageFilePath != null &&
                            (imageFilePath.startsWith("http://") || imageFilePath.startsWith("https://"));

                    Log.d(TAG, "isImageUrl: " + isImageUrl);

                    if (isImageUrl) {
                        // 使用URL
                        imageUrl = imageFilePath;
                        Log.d(TAG, ">>> 使用图片URL: " + imageUrl);
                    } else {
                        // 本地文件，编码为base64
                        Log.d(TAG, ">>> 使用本地文件，开始编码为base64");
                        imageBase64 = encodeImageToBase64(imageFilePath);
                        if (imageBase64 == null) {
                            callback.onError("图片编码失败");
                            return;
                        }
                        Log.d(TAG, ">>> 使用图片base64，长度: " + imageBase64.length());
                    }

                    // 2. 构造API请求（使用新格式）
                    JSONObject requestBody = buildGenerationRequest(imageUrl, imageBase64, maskImageUrl, prompt, maskImage, referenceImages, quality);

                    // 3. 发送API请求
                    String response = sendApiRequest(requestBody);

                    // 4. 解析响应
                    String resultUrl = parseResponse(response);

                    if (resultUrl != null) {
                        callback.onSuccess(resultUrl);
                    } else {
                        callback.onError("解析响应失败");
                    }

                } catch (Exception e) {
                    Log.e(TAG, "生成图片失败", e);
                    callback.onError("生成失败: " + e.getMessage());
                }
            }
        }).start();
    }

    /**
     * 生成回调接口
     */
    public interface GenerationCallback {
        void onSuccess(String imageUrl);
        void onError(String error);
    }
}
