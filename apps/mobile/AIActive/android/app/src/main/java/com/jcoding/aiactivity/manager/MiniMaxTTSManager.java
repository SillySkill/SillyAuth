package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.media.MediaPlayer;
import android.text.TextUtils;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.jcoding.aiactivity.network.MiniMaxApiService;
import com.jcoding.aiactivity.network.MiniMaxAsyncResponse;
import com.jcoding.aiactivity.network.MiniMaxAsyncResult;
import com.jcoding.aiactivity.network.MiniMaxFileInfo;
import com.jcoding.aiactivity.network.MiniMaxSyncResponse;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * MiniMax TTS语音合成管理器
 * 支持同步语音合成，直接获取音频数据并播放
 */
public class MiniMaxTTSManager {

    private static final String TAG = "MiniMaxTTSManager";
    private static final String BASE_URL = "https://api.minimaxi.com/";

    private static MiniMaxTTSManager instance;
    private Context context;
    private MiniMaxApiService apiService;
    private boolean isInit = false;
    private List<SynthesisListener> listeners = new ArrayList<>();

    // 配置参数
    private String apiKey = "";
    private String groupId = "";
    private String voiceId = "audiobook_male_1"; // 默认发音人（使用官方示例的音色）
    private int speed = 1;    // 默认语速（整数，范围通常0.5-2.0）
    private int volume = 10;  // 默认音量（整数，范围0-10）

    // 音频播放
    private MediaPlayer mediaPlayer;
    private boolean isPlaying = false;

    private MiniMaxTTSManager(Context context) {
        this.context = context.getApplicationContext();
        initRetrofit();
    }

    public static synchronized MiniMaxTTSManager getInstance(Context context) {
        if (instance == null) {
            instance = new MiniMaxTTSManager(context);
        }
        return instance;
    }

    /**
     * 初始化Retrofit客户端
     */
    private void initRetrofit() {
        try {
            OkHttpClient okHttpClient = new OkHttpClient.Builder()
                    .connectTimeout(30, TimeUnit.SECONDS)
                    .readTimeout(30, TimeUnit.SECONDS)
                    .writeTimeout(30, TimeUnit.SECONDS)
                    .build();

            Retrofit retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .client(okHttpClient)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();

            apiService = retrofit.create(MiniMaxApiService.class);

            Log.i(TAG, "Retrofit initialized successfully");
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize Retrofit", e);
        }
    }

    /**
     * 设置配置参数
     */
    public void setConfig(String apiKey, String groupId) {
        this.apiKey = apiKey;
        this.groupId = groupId;

        if (!TextUtils.isEmpty(apiKey) && !TextUtils.isEmpty(groupId)) {
            isInit = true;
            Log.i(TAG, "MiniMax TTS config set successfully, groupId=" + groupId);
        }
    }

    /**
     * 应用配置参数
     */
    public void applyConfig(String voiceId, float speed, float volume) {
        this.voiceId = voiceId;
        // MiniMax API requires integer parameters
        this.speed = Math.round(speed);
        this.volume = Math.round(volume);
        Log.i(TAG, "TTS parameters updated: voiceId=" + voiceId + ", speed=" + this.speed + ", volume=" + this.volume);
    }

    /**
     * 合成并播放文本
     */
    public void speak(final String text, final SynthesisListener listener) {
        Log.i(TAG, "speak() called, text length: " + text.length());
        Log.i(TAG, "isInit: " + isInit);

        if (!isInit) {
            Log.e(TAG, "MiniMax TTS not initialized");
            if (listener != null) {
                listener.onError(-1, "MiniMax TTS未初始化，请先配置API Key和Group ID");
            }
            return;
        }

        if (TextUtils.isEmpty(text)) {
            Log.e(TAG, "Text is empty");
            if (listener != null) {
                listener.onError(-2, "文本为空");
            }
            return;
        }

        // 添加监听器
        if (listener != null) {
            listeners.add(listener);
        }

        Log.i(TAG, "Starting background thread for TTS synthesis (synchronous mode)");

        // 在后台线程执行合成
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Log.i(TAG, "Thread started, calling requestSynthesisSync()");

                    // 同步合成请求，直接返回音频数据
                    byte[] audioData = requestSynthesisSync(text);
                    if (audioData == null) {
                        Log.e(TAG, "requestSynthesisSync() returned null");
                        notifyError(-3, "发起合成请求失败");
                        return;
                    }

                    Log.i(TAG, "Audio data received, size=" + audioData.length + " bytes");

                    // 播放音频
                    playAudioData(audioData);

                } catch (Exception e) {
                    Log.e(TAG, "Failed to speak", e);
                    notifyError(-5, "播放异常: " + e.getMessage());
                }
            }
        }, "MiniMax-TTS").start();
    }

    /**
     * 发起同步语音合成请求 (v2 API)
     * 文档: https://platform.minimaxi.com/docs/api-reference/speech-t2a-http
     * 直接返回hex编码的音频数据，无需轮询
     */
    private byte[] requestSynthesisSync(String text) {
        try {
            // 构建请求体 - 符合MiniMax同步API v2规范
            JsonObject requestBody = new JsonObject();
            requestBody.addProperty("model", "speech-02-turbo");  // 使用turbo系列模型
            requestBody.addProperty("text", text);
            requestBody.addProperty("stream", false);  // 同步模式，非流式
            requestBody.addProperty("subtitle_enable", false);  // 不启用字幕

            // voice_setting对象
            JsonObject voiceSetting = new JsonObject();
            voiceSetting.addProperty("voice_id", voiceId);
            voiceSetting.addProperty("speed", speed);
            voiceSetting.addProperty("vol", volume);
            voiceSetting.addProperty("pitch", 1);
            requestBody.add("voice_setting", voiceSetting);

            // audio_setting对象
            JsonObject audioSetting = new JsonObject();
            audioSetting.addProperty("sample_rate", 32000);
            audioSetting.addProperty("bitrate", 128000);
            audioSetting.addProperty("format", "mp3");
            audioSetting.addProperty("channel", 1);  // 单声道
            requestBody.add("audio_setting", audioSetting);

            String jsonBody = new Gson().toJson(requestBody);
            Log.d(TAG, "Request body: " + jsonBody);

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json; charset=utf-8"),
                    jsonBody
            );

            String authorization = "Bearer " + apiKey;

            Call<MiniMaxSyncResponse> call = apiService.textToSpeechSync(authorization, body);
            Response<MiniMaxSyncResponse> response = call.execute();

            Log.d(TAG, "Response code: " + response.code());

            if (response.isSuccessful() && response.body() != null) {
                MiniMaxSyncResponse syncResponse = response.body();
                Log.d(TAG, "Response body: " + new Gson().toJson(syncResponse));

                if (syncResponse.getBaseResp() != null &&
                        syncResponse.getBaseResp().getStatusCode() == 0) {
                    // 成功，获取hex编码的音频数据
                    String hexAudio = syncResponse.getData().getAudio();
                    if (hexAudio != null && !hexAudio.isEmpty()) {
                        Log.i(TAG, "Audio data received, hex length=" + hexAudio.length());
                        // 将hex字符串转换为字节数组
                        return hexStringToBytes(hexAudio);
                    } else {
                        Log.e(TAG, "Audio data is null or empty");
                    }
                } else {
                    int code = syncResponse.getBaseResp() != null ? syncResponse.getBaseResp().getStatusCode() : -1;
                    String msg = syncResponse.getBaseResp() != null ? syncResponse.getBaseResp().getStatusMsg() : "Unknown error";
                    Log.e(TAG, "Synthesis request failed: " + code + ", " + msg);
                    Log.e(TAG, "Full response: " + new Gson().toJson(syncResponse));
                }
            } else {
                Log.e(TAG, "HTTP error: " + response.code() + ", " + response.message());
                try {
                    if (response.errorBody() != null) {
                        String errorBody = response.errorBody().string();
                        Log.e(TAG, "Error body: " + errorBody);
                    }
                } catch (IOException e) {
                    Log.e(TAG, "Failed to read error body", e);
                }
            }

        } catch (Exception e) {
            Log.e(TAG, "Failed to request synthesis", e);
        }
        return null;
    }

    /**
     * 将hex字符串转换为字节数组
     */
    private byte[] hexStringToBytes(String hexString) {
        int len = hexString.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hexString.charAt(i), 16) << 4)
                    + Character.digit(hexString.charAt(i + 1), 16));
        }
        return data;
    }

    /**
     * 播放音频数据（从字节数组）
     */
    private void playAudioData(final byte[] audioData) {
        try {
            // 保存到临时文件
            File tempFile = new File(context.getCacheDir(), "tts_audio_" + System.currentTimeMillis() + ".mp3");
            FileOutputStream fos = new FileOutputStream(tempFile);
            fos.write(audioData);
            fos.close();

            Log.i(TAG, "Audio data saved to: " + tempFile.getAbsolutePath() + ", size=" + tempFile.length());

            // 使用MediaPlayer播放
            playAudioFile(tempFile);

        } catch (Exception e) {
            Log.e(TAG, "Failed to play audio data", e);
            notifyError(-7, "播放失败: " + e.getMessage());
        }
    }

    // ========== 以下方法保留以兼容，但不再使用 ==========

    /**
     * 发起异步语音合成请求 (v2 API) - 已废弃，请使用requestSynthesisSync
     * 文档: https://platform.minimaxi.com/docs/api-reference/speech-t2a-async-create
     * @deprecated 使用同步API代替
     */
    @Deprecated
    private String requestSynthesis(String text) {
        try {
            // 构建请求体 - 符合MiniMax API v2规范
            // 使用turbo系列模型（更经济实惠）
            JsonObject requestBody = new JsonObject();
            requestBody.addProperty("model", "speech-02-turbo");  // 使用turbo系列模型
            requestBody.addProperty("text", text);
            requestBody.addProperty("group_id", groupId);  // 添加Group ID到请求体
            requestBody.addProperty("language_boost", "auto");

            // voice_setting对象 (注意是单数)
            JsonObject voiceSetting = new JsonObject();
            voiceSetting.addProperty("voice_id", voiceId);
            voiceSetting.addProperty("speed", speed);
            voiceSetting.addProperty("vol", volume);  // 注意是vol不是volume
            voiceSetting.addProperty("pitch", 1);     // MiniMax API requires integer
            requestBody.add("voice_setting", voiceSetting);

            // audio_setting对象 (使用官方示例的参数)
            JsonObject audioSetting = new JsonObject();
            audioSetting.addProperty("audio_sample_rate", 32000);
            audioSetting.addProperty("bitrate", 128000);
            audioSetting.addProperty("format", "mp3");
            audioSetting.addProperty("channel", 2);  // 官方示例使用2通道
            requestBody.add("audio_setting", audioSetting);

            String jsonBody = new Gson().toJson(requestBody);
            Log.d(TAG, "Request body: " + jsonBody);

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json; charset=utf-8"),
                    jsonBody
            );

            String authorization = "Bearer " + apiKey;

            Call<MiniMaxAsyncResponse> call = apiService.textToSpeechAsync(authorization, body);
            Response<MiniMaxAsyncResponse> response = call.execute();

            Log.d(TAG, "Response code: " + response.code());

            if (response.isSuccessful() && response.body() != null) {
                MiniMaxAsyncResponse asyncResponse = response.body();
                Log.d(TAG, "Response body: " + new Gson().toJson(asyncResponse));

                if (asyncResponse.getBaseResp() != null &&
                        asyncResponse.getBaseResp().getStatusCode() == 0) {
                    Log.i(TAG, "Synthesis request created, taskId=" + asyncResponse.getTaskId() +
                            ", fileId=" + asyncResponse.getFileId());
                    // 返回file_id用于后续获取下载链接
                    return asyncResponse.getFileId();
                } else {
                    int code = asyncResponse.getBaseResp() != null ? asyncResponse.getBaseResp().getStatusCode() : -1;
                    String msg = asyncResponse.getBaseResp() != null ? asyncResponse.getBaseResp().getStatusMsg() : "Unknown error";
                    Log.e(TAG, "Synthesis request failed: " + code + ", " + msg);
                    Log.e(TAG, "Full response: " + new Gson().toJson(asyncResponse));
                }
            } else {
                Log.e(TAG, "HTTP error: " + response.code() + ", " + response.message());
                try {
                    if (response.errorBody() != null) {
                        String errorBody = response.errorBody().string();
                        Log.e(TAG, "Error body: " + errorBody);
                    }
                } catch (IOException e) {
                    Log.e(TAG, "Failed to read error body", e);
                }
            }

        } catch (Exception e) {
            Log.e(TAG, "Failed to request synthesis", e);
        }
        return null;
    }

    /**
     * 轮询获取文件下载链接 - 已废弃，使用同步API不需要轮询
     * @deprecated 使用同步API代替
     */
    @Deprecated
    private String pollForResult(final String fileId) {
        final int MAX_RETRIES = 60; // 最多轮询60次（约2分钟）
        final int POLL_INTERVAL_MS = 2000; // 每2秒轮询一次

        String authorization = "Bearer " + apiKey;

        for (int i = 0; i < MAX_RETRIES; i++) {
            try {
                Call<MiniMaxFileInfo> call = apiService.getFileInfo(authorization, fileId);
                Response<MiniMaxFileInfo> response = call.execute();

                if (response.isSuccessful() && response.body() != null) {
                    MiniMaxFileInfo fileInfo = response.body();

                    if (fileInfo.getBaseResp() != null && fileInfo.getBaseResp().getStatusCode() != 0) {
                        Log.e(TAG, "File info error: " + fileInfo.getBaseResp().getStatusMsg());
                        return null;
                    }

                    Log.d(TAG, "Poll file info [" + i + "/" + MAX_RETRIES + "]: process_status=" +
                            fileInfo.getProcessStatus() + ", status=" + fileInfo.getStatus());

                    if (fileInfo.isSuccess()) {
                        String downloadUrl = fileInfo.getDownloadUrl();
                        if (downloadUrl != null && !downloadUrl.isEmpty()) {
                            Log.i(TAG, "File ready, downloadUrl=" + downloadUrl);
                            return downloadUrl;
                        } else {
                            Log.e(TAG, "File is ready but download_url is empty");
                            return null;
                        }
                    } else if (fileInfo.isFailed()) {
                        Log.e(TAG, "File processing failed");
                        return null;
                    }

                    // 继续等待（Queueing或Processing）
                } else {
                    Log.e(TAG, "HTTP error while polling: " + response.code());
                }

                Thread.sleep(POLL_INTERVAL_MS);

            } catch (Exception e) {
                Log.e(TAG, "Failed to poll file info", e);
            }
        }

        Log.e(TAG, "Poll timeout after " + MAX_RETRIES + " retries");
        return null;
    }

    /**
     * 下载音频并播放 - 已废弃，使用同步API不需要下载
     * @deprecated 使用playAudioData代替
     */
    @Deprecated
    private void downloadAndPlay(String audioUrl) {
        try {
            Log.i(TAG, "Downloading audio from: " + audioUrl);

            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(30, TimeUnit.SECONDS)
                    .readTimeout(30, TimeUnit.SECONDS)
                    .build();

            Request request = new Request.Builder()
                    .url(audioUrl)
                    .build();

            okhttp3.Response response = client.newCall(request).execute();
            if (!response.isSuccessful()) {
                notifyError(-6, "下载音频失败: HTTP " + response.code());
                return;
            }

            InputStream inputStream = response.body().byteStream();

            // 保存到临时文件
            File tempFile = new File(context.getCacheDir(), "tts_audio_" + System.currentTimeMillis() + ".mp3");
            FileOutputStream fos = new FileOutputStream(tempFile);

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                fos.write(buffer, 0, bytesRead);
            }
            fos.close();
            inputStream.close();

            Log.i(TAG, "Audio downloaded to: " + tempFile.getAbsolutePath() + ", size=" + tempFile.length());

            // 使用MediaPlayer播放
            playAudioFile(tempFile);

        } catch (Exception e) {
            Log.e(TAG, "Failed to download and play", e);
            notifyError(-7, "播放失败: " + e.getMessage());
        }
    }

    /**
     * 使用MediaPlayer播放音频文件
     */
    private synchronized void playAudioFile(final File audioFile) {
        try {
            // 释放之前的播放器
            if (mediaPlayer != null) {
                mediaPlayer.release();
                mediaPlayer = null;
            }

            mediaPlayer = new MediaPlayer();
            mediaPlayer.setDataSource(audioFile.getAbsolutePath());

            mediaPlayer.setOnPreparedListener(new MediaPlayer.OnPreparedListener() {
                @Override
                public void onPrepared(MediaPlayer mp) {
                    Log.i(TAG, "MediaPlayer prepared, starting playback");
                    isPlaying = true;
                    mp.start();
                    notifySpeakStart();
                }
            });

            mediaPlayer.setOnCompletionListener(new MediaPlayer.OnCompletionListener() {
                @Override
                public void onCompletion(MediaPlayer mp) {
                    Log.i(TAG, "Playback completed");
                    isPlaying = false;
                    notifySpeakComplete();
                    // 清理临时文件
                    audioFile.delete();
                }
            });

            mediaPlayer.setOnErrorListener(new MediaPlayer.OnErrorListener() {
                @Override
                public boolean onError(MediaPlayer mp, int what, int extra) {
                    Log.e(TAG, "MediaPlayer error: what=" + what + ", extra=" + extra);
                    isPlaying = false;
                    notifyError(-8, "MediaPlayer播放错误");
                    // 清理临时文件
                    audioFile.delete();
                    return true;
                }
            });

            mediaPlayer.prepareAsync();

        } catch (Exception e) {
            Log.e(TAG, "Failed to play audio", e);
            isPlaying = false;
            notifyError(-9, "播放失败: " + e.getMessage());
            audioFile.delete();
        }
    }

    /**
     * 停止播放
     */
    public synchronized void stop() {
        isPlaying = false;
        if (mediaPlayer != null) {
            try {
                mediaPlayer.stop();
                mediaPlayer.release();
            } catch (Exception e) {
                Log.e(TAG, "Failed to stop MediaPlayer", e);
            }
            mediaPlayer = null;
        }
        Log.i(TAG, "Stopped");
    }

    /**
     * 释放资源
     */
    public synchronized void release() {
        stop();
        listeners.clear();
        isInit = false;
    }

    /**
     * 检查是否正在播放
     */
    public boolean isSpeaking() {
        return isPlaying;
    }

    /**
     * 检查是否已初始化
     */
    public boolean isInitialized() {
        return isInit;
    }

    // 通知方法
    private void notifySpeakStart() {
        List<SynthesisListener> listenersCopy;
        synchronized (listeners) {
            listenersCopy = new ArrayList<>(listeners);
        }

        for (SynthesisListener listener : listenersCopy) {
            if (listener != null) {
                try {
                    listener.onSpeakStart();
                } catch (Exception e) {
                    Log.e(TAG, "Listener error", e);
                }
            }
        }
    }

    private void notifySpeakComplete() {
        // 使用副本避免并发修改异常
        List<SynthesisListener> listenersCopy;
        synchronized (listeners) {
            listenersCopy = new ArrayList<>(listeners);
            listeners.clear();
        }

        for (SynthesisListener listener : listenersCopy) {
            if (listener != null) {
                try {
                    listener.onSpeakComplete();
                } catch (Exception e) {
                    Log.e(TAG, "Listener error", e);
                }
            }
        }
    }

    private void notifyError(int code, String message) {
        List<SynthesisListener> listenersCopy;
        synchronized (listeners) {
            listenersCopy = new ArrayList<>(listeners);
            listeners.clear();
        }

        for (SynthesisListener listener : listenersCopy) {
            if (listener != null) {
                try {
                    listener.onError(code, message);
                } catch (Exception e) {
                    Log.e(TAG, "Listener error", e);
                }
            }
        }
    }

    /**
     * 合成监听器接口
     */
    public interface SynthesisListener {
        void onSpeakStart();
        void onSpeakComplete();
        void onError(int errorCode, String errorMessage);
    }
}
