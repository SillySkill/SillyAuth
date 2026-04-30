package com.jcoding.aiactivity.network;

import com.jcoding.aiactivity.entity.GenerationTask;
import com.jcoding.aiactivity.entity.StyleConfig;

import java.io.File;
import java.util.Map;

import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Query;
import retrofit2.http.QueryMap;
import retrofit2.http.Url;

/**
 * API服务接口
 */
public interface ApiService {

    /**
     * 获取配置版本信息
     */
    @GET("api/config/version")
    Call<ConfigVersionResponse> getConfigVersion();

    /**
     * 下载配置文件
     */
    @GET
    Call<ResponseBody> downloadConfigFile(@Url String fileUrl);

    /**
     * 上报更新结果
     */
    @POST("api/config/report")
    Call<BasicResponse> reportUpdateResult(@Body Map<String, Object> report);

    /**
     * 上传文件（通过代理）
     */
    @Multipart
    @POST
    Call<UploadResponse> uploadFile(
            @Url String url,
            @Part MultipartBody.Part file,
            @Part RequestBody source
    );

    /**
     * 创建AI生成任务
     */
    @POST("api/generate")
    Call<GenerateResponse> createGeneration(@Body GenerateRequest request);

    /**
     * 查询生成状态
     */
    @GET("api/generation/status/{taskId}")
    Call<GenerationStatusResponse> getGenerationStatus(@Query("taskId") String taskId);

    /**
     * 验证邀请码
     */
    @POST("api/invite/verify")
    Call<InviteVerifyResponse> verifyInviteCode(@Body Map<String, String> request);

    /**
     * 生成邀请码
     */
    @POST("api/invite/generate")
    Call<GenerateInviteCodesResponse> generateInviteCodes(@Body Map<String, Object> request);

    /**
     * 获取邀请码列表
     */
    @GET("api/invite/list")
    Call<InviteCodeListResponse> getInviteCodeList(@QueryMap Map<String, String> params);

    /**
     * 删除邀请码
     */
    @POST("api/invite/delete")
    Call<BasicResponse> deleteInviteCodes(@Body Map<String, Object> request);

    /**
     * 导出邀请码
     */
    @POST("api/invite/export")
    Call<ResponseBody> exportInviteCodes(@Body Map<String, String> request);

    /**
     * 创建支付订单
     */
    @POST("api/payment/create")
    Call<PaymentResponse> createPayment(@Body Map<String, Object> request);

    /**
     * 查询支付订单
     */
    @GET("api/payment/query")
    Call<PaymentQueryResponse> queryPayment(@Query("order_id") String orderId);

    /**
     * 员工登录
     */
    @POST("api/employee/login")
    Call<LoginResponse> employeeLogin(@Body Map<String, String> request);

    /**
     * 提交答题记录
     */
    @POST("api/quiz/submit")
    Call<BasicResponse> submitQuizRecord(@Body Map<String, Object> request);

    /**
     * 获取抽奖结果
     */
    @POST("api/lottery/draw")
    Call<LotteryResponse> drawLottery(@Body Map<String, Object> request);

    /**
     * 更新生成任务状态（用于手机端轮询）
     */
    @POST("/application/upload/task/update")
    Call<BasicResponse> updateGenerationTask(@Body Map<String, Object> request);

    /**
     * 查询生成任务状态（用于手机端轮询）
     */
    @GET
    Call<GenerationTaskListResponse> queryGenerationTasks(@Url String url);

    // ========== 响应模型 ==========

    class BasicResponse {
        public int code;
        public String message;
    }

    class ConfigVersionResponse extends BasicResponse {
        public Data data;

        public static class Data {
            public String version;
            public int version_code;
            public String released_at;
            public boolean force_update;
            public String min_compatible_version;
            public String release_notes;
            public File[] files;
        }

        public static class File {
            public String path;
            public long size;
            public String md5;
            public String url;
            public boolean compressed;
            public boolean essential;
        }
    }

    class UploadResponse {
        public int code;
        public String message;
        public String data;  // 文件URL
    }

    static class GenerateRequest {
        public String style_id;
        public String image_url;
        public String prompt;
        public String[] reference_images;
        public String mask_image;  // 遮罩图片URL
    }

    class GenerateResponse extends BasicResponse {
        public Data data;

        public static class Data {
            public String task_id;
            public String status;
            public int estimated_time;
        }
    }

    class GenerationStatusResponse extends BasicResponse {
        public GenerationTask data;
    }

    class InviteVerifyResponse extends BasicResponse {
        public Data data;

        public static class Data {
            public boolean valid;
            public String user_name;
            public int remaining_times;
        }
    }

    class PaymentResponse extends BasicResponse {
        public Data data;

        public static class Data {
            public String order_id;
            public String payment_url;
            public String qr_code_url;
        }
    }

    class LoginResponse extends BasicResponse {
        public Data data;

        public static class Data {
            public String user_id;
            public String user_name;
            public String token;
        }
    }

    class LotteryResponse extends BasicResponse {
        public Data data;

        public static class Data {
            public String[] winners;
            public String[] prizes;
        }
    }

    class PaymentQueryResponse extends BasicResponse {
        public PaymentOrderData data;

        public static class PaymentOrderData {
            public String order_id;
            public String style_id;
            public double amount;
            public String payment_method;
            public int payment_status;
            public String payment_status_text;
            public String transaction_id;
            public String qr_code_url;
            public String payment_url;
            public String user_name;
            public String user_phone;
            public String paid_at;
            public String created_at;
        }
    }

    class GenerateInviteCodesResponse extends BasicResponse {
        public GenerateData data;

        public static class GenerateData {
            public String batchName;
            public int quantity;
            public String[] codes;
        }
    }

    class InviteCodeListResponse extends BasicResponse {
        public InviteCodeListData data;

        public static class InviteCodeListData {
            public int total;
            public int page;
            public int page_size;
            public InviteCodeData[] list;
        }
    }

    class InviteCodeData {
        public int id;
        public String code;
        public String batchName;
        public int maxUsage;
        public int usedCount;
        public int status;
        public String validFrom;
        public String validUntil;
        public String createdBy;
        public String createdAt;
    }

    class GenerationTaskListResponse extends BasicResponse {
        public GenerationTask[] data;
    }
}
