package com.jcoding.aiactivity.network;

import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.POST;
import retrofit2.http.Query;

/**
 * MiniMax API服务接口
 * 文档: https://platform.minimaxi.com/docs/api-reference/speech-t2a-async-create
 */
public interface MiniMaxApiService {

    /**
     * 异步语音合成API (v2)
     * POST https://api.minimaxi.com/v1/t2a_async_v2
     * 创建异步语音合成任务，返回task_id和file_id
     */
    @POST("v1/t2a_async_v2")
    Call<MiniMaxAsyncResponse> textToSpeechAsync(
            @Header("Authorization") String authorization,
            @Body RequestBody body
    );

    /**
     * 查询语音生成任务状态
     * GET https://api.minimaxi.com/v1/query/t2a_async_v2?task_id={task_id}
     */
    @GET("v1/query/t2a_async_v2")
    Call<MiniMaxAsyncResult> queryTaskStatus(
            @Header("Authorization") String authorization,
            @Query("task_id") String taskId
    );

    /**
     * 文件内容检索 - 获取文件下载URL
     * GET https://api.minimaxi.com/v1/files/retrieve_content?file_id={file_id}
     * 根据MiniMax官方文档，这是正确的文件下载端点
     */
    @GET("v1/files/retrieve_content")
    Call<MiniMaxFileInfo> getFileInfo(
            @Header("Authorization") String authorization,
            @Query("file_id") String fileId
    );

    /**
     * 同步语音合成API
     * POST https://api.minimaxi.com/v1/t2a_v2
     * 直接返回hex编码的音频数据，无需轮询
     */
    @POST("v1/t2a_v2")
    Call<MiniMaxSyncResponse> textToSpeechSync(
            @Header("Authorization") String authorization,
            @Body RequestBody body
    );

}
