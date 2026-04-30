package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.util.Log;

import java.util.Locale;

/**
 * 系统TTS管理器 - 用于测试
 */
public class SystemTTSManager {
    private static final String TAG = "SystemTTSManager";
    private static SystemTTSManager instance;

    private Context context;
    private TextToSpeech tts;
    private boolean isInitialized = false;
    private SpeechCallback callback;

    public interface SpeechCallback {
        void onStart();
        void onComplete();
        void onError(String error);
    }

    private SystemTTSManager(Context context) {
        this.context = context.getApplicationContext();
        initTTS();
    }

    public static synchronized SystemTTSManager getInstance(Context context) {
        if (instance == null) {
            instance = new SystemTTSManager(context);
        }
        return instance;
    }

    private void initTTS() {
        try {
            tts = new TextToSpeech(context, new TextToSpeech.OnInitListener() {
                @Override
                public void onInit(int status) {
                    if (status == TextToSpeech.SUCCESS) {
                        int result = tts.setLanguage(Locale.CHINESE);
                        if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                            Log.e(TAG, "Chinese not supported");
                            isInitialized = false;
                        } else {
                            isInitialized = true;
                            Log.i(TAG, "System TTS initialized successfully");
                        }
                    } else {
                        Log.e(TAG, "TTS initialization failed");
                        isInitialized = false;
                    }
                }
            });
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize TTS", e);
        }
    }

    public void speak(String text, SpeechCallback callback) {
        this.callback = callback;

        if (!isInitialized) {
            if (callback != null) {
                callback.onError("TTS未初始化");
            }
            return;
        }

        if (tts == null) {
            if (callback != null) {
                callback.onError("TTS对象为空");
            }
            return;
        }

        try {
            tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
                @Override
                public void onStart(String utteranceId) {
                    Log.i(TAG, "TTS start: " + text);
                    if (callback != null) {
                        callback.onStart();
                    }
                }

                @Override
                public void onDone(String utteranceId) {
                    Log.i(TAG, "TTS done: " + text);
                    if (callback != null) {
                        callback.onComplete();
                    }
                }

                @Override
                public void onError(String utteranceId) {
                    Log.e(TAG, "TTS error: " + utteranceId);
                    if (callback != null) {
                        callback.onError("播放失败");
                    }
                }
            });

            // 设置音频流类型为MUSIC
            tts.setSpeechRate(1.0f);
            tts.setPitch(1.0f);

            int result = tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "tts_utterance");
            if (result == TextToSpeech.ERROR) {
                if (callback != null) {
                    callback.onError("播放失败");
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to speak", e);
            if (callback != null) {
                callback.onError("播放异常: " + e.getMessage());
            }
        }
    }

    public void stop() {
        if (tts != null) {
            tts.stop();
        }
    }

    public void shutdown() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
        }
    }

    public boolean isInitialized() {
        return isInitialized && tts != null;
    }
}
