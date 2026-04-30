package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.text.TextUtils;
import android.util.Log;

import com.tencent.cloud.libqcloudtts.TtsController;
import com.tencent.cloud.libqcloudtts.TtsError;
import com.tencent.cloud.libqcloudtts.TtsMode;
import com.tencent.cloud.libqcloudtts.TtsResultListener;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * 腾讯TTS语音合成管理器
 * 实现音频数据流的接收和播放
 */
public class SpeechSynthesizerManager {

    private static final String TAG = "SpeechSynthesizerManager";
    private static SpeechSynthesizerManager instance;

    private Context context;
    private TtsController ttsController;
    private boolean isInit = false;
    private List<SynthesisListener> listeners = new ArrayList<>();

    // 配置参数
    private String appId = "";
    private String secretId = "";
    private String secretKey = "";

    // TTS参数
    private int voiceType = 1001;  // 默认发音人：智瑜
    private float speed = 1.0f;    // 默认语速
    private float pitch = 1.0f;    // 默认音调
    private float volume = 5.0f;   // 默认音量 (0-10)

    // 音频播放
    private AudioTrack audioTrack;
    private AtomicBoolean isPlaying = new AtomicBoolean(false);
    private LinkedBlockingQueue<byte[]> audioQueue = new LinkedBlockingQueue<>(10);
    private Thread playThread;
    private final Object playLock = new Object();

    private SpeechSynthesizerManager(Context context) {
        this.context = context.getApplicationContext();
        initTTS();
    }

    public static synchronized SpeechSynthesizerManager getInstance(Context context) {
        if (instance == null) {
            instance = new SpeechSynthesizerManager(context);
        }
        return instance;
    }

    /**
     * 初始化TTS
     */
    private void initTTS() {
        try {
            // 获取TTS控制器实例
            ttsController = TtsController.getInstance();

            // 初始化TTS控制器 - 使用在线模式
            // 注意：需要有效的腾讯云AppID/SecretId/SecretKey才能正常工作
            ttsController.init(context, TtsMode.ONLINE, new TtsResultListener() {
                @Override
                public void onSynthesizeData(byte[] data, String sessionId, String type, int seq) {
                    // 单声道音频数据
                    if (data != null && data.length > 0) {
                        Log.d(TAG, "收到音频数据: " + data.length + " bytes, seq=" + seq);
                        putAudioData(data);
                    }
                }

                @Override
                public void onSynthesizeData(byte[] data, String sessionId, String type, int seq, String text) {
                    // 带文本的音频数据
                    if (data != null && data.length > 0) {
                        Log.d(TAG, "收到音频数据: " + data.length + " bytes, text=" + text);
                        putAudioData(data);
                    }
                }

                @Override
                public void onSynthesizeData(byte[] data, String sessionId, String type, int seq, String text, String phoneme) {
                    // 带文本和音素的音频数据
                    if (data != null && data.length > 0) {
                        Log.d(TAG, "收到音频数据: " + data.length + " bytes");
                        putAudioData(data);
                    }
                }

                @Override
                public void onError(TtsError error, String sessionId, String type) {
                    Log.e(TAG, "TTS错误: " + error.getMessage() + ", code=" + error.getCode());
                    notifyError(error.getCode(), error.getMessage());
                    finishPlayback();
                }

                @Override
                public void onOfflineAuthInfo(com.tencent.cloud.libqcloudtts.engine.offlineModule.auth.QCloudOfflineAuthInfo authInfo) {
                    // 离线认证信息（不需要处理）
                }

                @Override
                public void onChunk(ByteBuffer byteBuffer) {
                    // 分片数据（不需要处理）
                }
            });

            Log.i(TAG, "TTS initialized successfully");
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize TTS", e);
        }
    }

    /**
     * 设置配置参数
     */
    public void setConfig(String appId, String secretId, String secretKey) {
        this.appId = appId;
        this.secretId = secretId;
        this.secretKey = secretKey;

        try {
            // 尝试将appId转换为Long类型
            long appIdLong;
            try {
                appIdLong = Long.parseLong(appId);
            } catch (NumberFormatException e) {
                // 如果appId是十六进制或其他非数字格式，使用0作为默认值
                Log.w(TAG, "appId is not a valid number: " + appId + ", using 0 as default");
                appIdLong = 0L;
            }

            // 配置在线模式参数
            ttsController.setAppId(appIdLong);
            ttsController.setSecretId(secretId);
            ttsController.setSecretKey(secretKey);
            ttsController.setToken(null); // 不使用STS临时证书

            // 设置TTS参数
            ttsController.setOnlineVoiceType(this.voiceType);
            ttsController.setOnlineVoiceSpeed(this.speed);
            ttsController.setOnlineVoiceVolume(this.volume / 10.0f);

            isInit = true;
            Log.i(TAG, "TTS config set successfully (online mode), appId=" + appIdLong);
        } catch (Exception e) {
            Log.e(TAG, "Failed to set config", e);
        }
    }

    /**
     * 应用配置参数（从ConfigManager读取）
     */
    public void applyConfig(int voiceType, float speed, float pitch, float volume) {
        // 保存参数供后续使用
        this.voiceType = voiceType;
        this.speed = speed;
        this.pitch = pitch;
        this.volume = volume;

        if (ttsController != null && isInit) {
            try {
                ttsController.setOnlineVoiceType(voiceType);
                ttsController.setOnlineVoiceSpeed(speed);
                ttsController.setOnlineVoiceVolume(volume / 10.0f);
                Log.i(TAG, "TTS parameters updated: voiceType=" + voiceType + ", speed=" + speed);
            } catch (Exception e) {
                Log.e(TAG, "Failed to apply config", e);
            }
        }
    }

    /**
     * 获取当前发音人
     */
    public int getVoiceType() {
        return voiceType;
    }

    /**
     * 设置发音人
     */
    public void setVoiceType(int voiceType) {
        this.voiceType = voiceType;
        if (ttsController != null) {
            ttsController.setOnlineVoiceType(voiceType);
        }
    }

    /**
     * 合成并播放
     * @param text 要合成的文本
     * @param listener 监听器
     */
    public boolean speak(String text, SynthesisListener listener) {
        if (!isInit) {
            if (listener != null) {
                listener.onError(-1, "TTS未初始化");
            }
            return false;
        }

        if (TextUtils.isEmpty(text)) {
            if (listener != null) {
                listener.onError(-2, "文本为空");
            }
            return false;
        }

        // 添加监听器
        if (listener != null) {
            listeners.add(listener);
        }

        try {
            // 开始播放
            startPlayback();
            notifySpeakStart();

            // 开始合成
            TtsError error = ttsController.synthesize(text);
            if (error == null || error.getCode() == 0) {
                Log.i(TAG, "Started speaking: " + text);
                return true;
            } else {
                notifyError(error.getCode(), error.getMessage());
                return false;
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to speak", e);
            notifyError(-3, "播放异常: " + e.getMessage());
            return false;
        }
    }

    /**
     * 放入音频数据
     */
    private void putAudioData(byte[] data) {
        try {
            audioQueue.put(data);
            synchronized (playLock) {
                playLock.notifyAll();
            }
        } catch (InterruptedException e) {
            Log.e(TAG, "Failed to put audio data", e);
        }
    }

    /**
     * 开始播放
     */
    private void startPlayback() {
        if (isPlaying.get()) {
            return;
        }

        isPlaying.set(true);
        audioQueue.clear();

        playThread = new Thread(new Runnable() {
            @Override
            public void run() {
                playAudio();
            }
        }, "TTS-PlayThread");
        playThread.start();
    }

    /**
     * 播放音频数据
     */
    private void playAudio() {
        try {
            // 配置AudioTrack
            int sampleRate = 16000;
            int channelConfig = AudioFormat.CHANNEL_OUT_MONO;
            int audioFormat = AudioFormat.ENCODING_PCM_16BIT;
            int bufferSize = AudioTrack.getMinBufferSize(sampleRate, channelConfig, audioFormat);

            audioTrack = new AudioTrack.Builder()
                    .setAudioAttributes(new AudioAttributes.Builder()
                            .setUsage(AudioAttributes.USAGE_MEDIA)
                            .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                            .build())
                    .setAudioFormat(new AudioFormat.Builder()
                            .setEncoding(audioFormat)
                            .setSampleRate(sampleRate)
                            .setChannelMask(channelConfig)
                            .build())
                    .setBufferSizeInBytes(bufferSize)
                    .setTransferMode(AudioTrack.MODE_STREAM)
                    .build();

            audioTrack.play();

            Log.i(TAG, "AudioTrack started, bufferSize=" + bufferSize);

            while (isPlaying.get()) {
                byte[] data = audioQueue.poll();
                if (data == null) {
                    synchronized (playLock) {
                        try {
                            playLock.wait(100);
                        } catch (InterruptedException e) {
                            break;
                        }
                    }
                    continue;
                }

                int written = audioTrack.write(data, 0, data.length);
                Log.d(TAG, "Wrote audio data: " + written + " bytes");
            }

            // 等待音频缓冲播放完成
            if (audioTrack != null) {
                audioTrack.stop();
                Log.i(TAG, "AudioTrack stopped");
            }

        } catch (Exception e) {
            Log.e(TAG, "Audio playback error", e);
            notifyError(-4, "播放错误: " + e.getMessage());
        } finally {
            releaseAudioTrack();
            notifySpeakComplete();
        }
    }

    /**
     * 结束播放
     */
    private void finishPlayback() {
        isPlaying.set(false);
        synchronized (playLock) {
            playLock.notifyAll();
        }

        // 放入结束标记
        try {
            audioQueue.put(new byte[0]);
        } catch (InterruptedException e) {
            Log.e(TAG, "Failed to finish playback", e);
        }
    }

    /**
     * 释放AudioTrack
     */
    private void releaseAudioTrack() {
        if (audioTrack != null) {
            try {
                audioTrack.release();
            } catch (Exception e) {
                Log.e(TAG, "Failed to release AudioTrack", e);
            }
            audioTrack = null;
        }
    }

    /**
     * 暂停播放
     */
    public void pause() {
        if (audioTrack != null && audioTrack.getPlayState() == AudioTrack.PLAYSTATE_PLAYING) {
            audioTrack.pause();
            Log.i(TAG, "Audio paused");
        }
    }

    /**
     * 恢复播放
     */
    public void resume() {
        if (audioTrack != null && audioTrack.getPlayState() == AudioTrack.PLAYSTATE_PAUSED) {
            audioTrack.play();
            Log.i(TAG, "Audio resumed");
        }
    }

    /**
     * 停止播放
     */
    public void stop() {
        isPlaying.set(false);
        audioQueue.clear();

        if (ttsController != null) {
            ttsController.cancel();
        }

        synchronized (playLock) {
            playLock.notifyAll();
        }

        if (audioTrack != null) {
            audioTrack.pause();
            audioTrack.flush();
        }

        Log.i(TAG, "Stopped");
    }

    /**
     * 释放资源
     */
    public void release() {
        stop();
        releaseAudioTrack();

        if (ttsController != null) {
            TtsController.release();
            ttsController = null;
        }
        isInit = false;
    }

    /**
     * 检查是否正在播放
     */
    public boolean isSpeaking() {
        return isPlaying.get() && !audioQueue.isEmpty();
    }

    /**
     * 检查是否已初始化
     */
    public boolean isInitialized() {
        return isInit && ttsController != null;
    }

    // 通知方法
    private void notifySpeakStart() {
        for (SynthesisListener listener : listeners) {
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
        for (SynthesisListener listener : listeners) {
            if (listener != null) {
                try {
                    listener.onSpeakComplete();
                } catch (Exception e) {
                    Log.e(TAG, "Listener error", e);
                }
            }
        }
        listeners.clear();
    }

    private void notifyError(int code, String message) {
        for (SynthesisListener listener : listeners) {
            if (listener != null) {
                try {
                    listener.onError(code, message);
                } catch (Exception e) {
                    Log.e(TAG, "Listener error", e);
                }
            }
        }
        listeners.clear();
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
