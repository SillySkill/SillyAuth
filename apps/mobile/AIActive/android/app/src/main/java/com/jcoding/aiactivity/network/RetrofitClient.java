package com.jcoding.aiactivity.network;

import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * Retrofit客户端
 * 后端服务URL格式：https://域名/application/包名/服务path
 */
public class RetrofitClient {

    // 主API服务基础URL：https://www.jcoding.chat/application/com.jcoding.aiactivity/
    private static final String BASE_URL = "https://www.jcoding.chat/application/com.jcoding.aiactivity/";

    // 上传服务基础URL（必须以/结尾）：https://www.jcoding.chat/application/
    private static final String UPLOAD_URL = "https://www.jcoding.chat/application/";

    private static RetrofitClient instance;
    private ApiService apiService;
    private ApiService uploadService;

    private RetrofitClient() {
        // 创建OkHttpClient
        OkHttpClient.Builder okHttpBuilder = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS);

        // 注释掉日志拦截器（需要添加依赖）
        // HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
        // loggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BODY);
        // okHttpBuilder.addInterceptor(loggingInterceptor);

        OkHttpClient okHttpClient = okHttpBuilder.build();

        // 创建Retrofit实例（API服务）
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        apiService = retrofit.create(ApiService.class);

        // 创建Retrofit实例（上传服务）
        Retrofit uploadRetrofit = new Retrofit.Builder()
                .baseUrl(UPLOAD_URL)
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        uploadService = uploadRetrofit.create(ApiService.class);
    }

    public static synchronized RetrofitClient getInstance() {
        if (instance == null) {
            instance = new RetrofitClient();
        }
        return instance;
    }

    public ApiService getApiService() {
        return apiService;
    }

    public ApiService getUploadService() {
        return uploadService;
    }
}
