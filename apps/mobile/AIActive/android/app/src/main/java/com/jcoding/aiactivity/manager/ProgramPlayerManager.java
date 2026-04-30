package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.graphics.Bitmap;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.jcoding.aiactivity.entity.DigitalHumanAction;
import com.jcoding.aiactivity.entity.InnerShowModule;
import com.jcoding.aiactivity.entity.ProgramItem;
import com.jcoding.aiactivity.manager.DigitalHumanManager.DigitalHumanCallback;

import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

/**
 * 节目播放管理器
 *
 * 功能：
 * 1. 加载节目表
 * 2. 控制播放流程（播放、暂停、停止、跳转）
 * 3. 数字人动作和语音同步
 * 4. 进度管理和时间控制
 * 5. 播放状态回调
 */
public class ProgramPlayerManager {

    private static final String TAG = "ProgramPlayerManager";
    private static ProgramPlayerManager instance;

    private Context context;
    private DigitalHumanManager digitalHumanManager;
    private VoiceManager voiceManager;

    // 节目数据
    private List<ProgramItem> programs;
    private int currentIndex = -1;

    // 播放状态
    private boolean isPlaying = false;
    private boolean isPaused = false;
    private long startTime = 0;
    private long pausedTime = 0;

    // 进度
    private int currentProgress = 0;  // 当前节目进度（秒）
    private int totalProgress = 0;     // 总进度

    // 定时器
    private Timer progressTimer;
    private Handler mainHandler;

    // 回调
    private PlaybackListener listener;

    private ProgramPlayerManager(Context context) {
        this.context = context.getApplicationContext();
        this.digitalHumanManager = DigitalHumanManager.getInstance(context);
        this.voiceManager = VoiceManager.getInstance(context);
        this.mainHandler = new Handler(Looper.getMainLooper());
        this.programs = new ArrayList<>();
    }

    public static synchronized ProgramPlayerManager getInstance(Context context) {
        if (instance == null) {
            instance = new ProgramPlayerManager(context);
        }
        return instance;
    }

    /**
     * 加载节目表
     */
    public void loadPrograms(List<ProgramItem> programList) {
        this.programs = programList != null ? programList : new ArrayList<ProgramItem>();
        this.currentIndex = -1;
        this.currentProgress = 0;

        // 计算总时长（假设每个节目30秒）
        this.totalProgress = this.programs.size() * 30;

        Log.i(TAG, "加载节目表，共 " + this.programs.size() + " 个节目，总时长 " + totalProgress + " 秒");

        if (listener != null) {
            listener.onProgramsLoaded(this.programs.size());
        }
    }

    /**
     * 开始播放
     */
    public void play() {
        if (programs == null || programs.isEmpty()) {
            Log.w(TAG, "没有可播放的节目");
            if (listener != null) {
                listener.onError("节目表为空");
            }
            return;
        }

        if (isPlaying && !isPaused) {
            Log.w(TAG, "已在播放中");
            return;
        }

        if (isPaused) {
            // 从暂停恢复
            resume();
            return;
        }

        // 开始播放
        isPlaying = true;
        isPaused = false;
        currentIndex = 0;
        startTime = System.currentTimeMillis();

        Log.i(TAG, "开始播放，共 " + programs.size() + " 个节目");

        // 播放第一个节目
        playProgram(0);

        // 启动进度计时器
        startProgressTimer();

        if (listener != null) {
            listener.onPlayStarted();
        }
    }

    /**
     * 暂停播放
     */
    public void pause() {
        if (!isPlaying || isPaused) {
            return;
        }

        isPaused = true;
        pausedTime = System.currentTimeMillis();

        // 停止数字人和语音
        digitalHumanManager.stop();
        voiceManager.stopSpeaking();

        // 停止进度计时
        stopProgressTimer();

        Log.i(TAG, "播放已暂停");

        if (listener != null) {
            listener.onPaused();
        }
    }

    /**
     * 恢复播放
     */
    public void resume() {
        if (!isPlaying || !isPaused) {
            return;
        }

        isPaused = false;

        // 调整开始时间（减去暂停时长）
        long pausedDuration = System.currentTimeMillis() - pausedTime;
        startTime += pausedDuration;

        // 恢复播放当前节目
        if (currentIndex >= 0 && currentIndex < programs.size()) {
            playProgram(currentIndex, false); // false = 不重置进度
        }

        // 恢复进度计时
        startProgressTimer();

        Log.i(TAG, "播放已恢复");

        if (listener != null) {
            listener.onResumed();
        }
    }

    /**
     * 停止播放
     */
    public void stop() {
        isPlaying = false;
        isPaused = false;
        currentIndex = -1;
        currentProgress = 0;

        // 停止数字人和语音
        digitalHumanManager.stop();
        voiceManager.stopSpeaking();

        // 停止进度计时
        stopProgressTimer();

        Log.i(TAG, "播放已停止");

        if (listener != null) {
            listener.onStopped();
        }
    }

    /**
     * 跳转到指定节目
     */
    public void jumpTo(int index) {
        if (index < 0 || index >= programs.size()) {
            Log.w(TAG, "无效的节目索引: " + index);
            return;
        }

        currentIndex = index;
        currentProgress = index * 30;

        // 播放指定节目
        if (isPlaying) {
            playProgram(index, true);
        }

        Log.i(TAG, "跳转到第 " + (index + 1) + " 个节目");

        if (listener != null) {
            listener.onJumpedTo(index);
        }
    }

    /**
     * 下一个节目
     */
    public void next() {
        if (currentIndex < programs.size() - 1) {
            jumpTo(currentIndex + 1);
        } else {
            Log.i(TAG, "已是最后一个节目");
        }
    }

    /**
     * 上一个节目
     */
    public void previous() {
        if (currentIndex > 0) {
            jumpTo(currentIndex - 1);
        } else {
            Log.i(TAG, "已是第一个节目");
        }
    }

    /**
     * 播放指定节目
     */
    private void playProgram(final int index) {
        playProgram(index, true);
    }

    /**
     * 播放指定节目
     *
     * @param index 节目索引
     * @param resetProgress 是否重置进度
     */
    private void playProgram(final int index, boolean resetProgress) {
        if (index < 0 || index >= programs.size()) {
            Log.w(TAG, "无效的节目索引: " + index);
            return;
        }

        final ProgramItem item = programs.get(index);
        currentIndex = index;

        if (resetProgress) {
            currentProgress = index * 30;
        }

        Log.i(TAG, "播放节目 " + (index + 1) + ": " + item.getContent());

        // 1. 执行数字人动作
        DigitalHumanAction action = item.getAction();
        if (action != null) {
            performDigitalHumanAction(action);
        }

        // 2. 语音播报
        speakContent(item.getContent());

        // 3. 通知回调
        if (listener != null) {
            listener.onProgramChanged(index, item);
        }
    }

    /**
     * 执行数字人动作
     */
    private void performDigitalHumanAction(DigitalHumanAction action) {
        digitalHumanManager.performAction(
            action.getId(),
            new DigitalHumanCallback() {
                @Override
                public void onSpeakStart(String gifPath) {
                    Log.d(TAG, "数字人动作开始: " + action.getName());
                    if (listener != null) {
                        listener.onActionStarted(action);
                    }
                }

                @Override
                public void onComplete() {
                    Log.d(TAG, "数字人动作完成: " + action.getName());
                    if (listener != null) {
                        listener.onActionCompleted(action);
                    }
                }

                @Override
                public void onError(String error) {
                    Log.e(TAG, "数字人动作错误: " + error);
                }
            }
        );
    }

    /**
     * 语音播报内容
     */
    private void speakContent(String content) {
        if (voiceManager != null && voiceManager.isInitialized()) {
            voiceManager.speakText(content, new VoiceManager.SynthesisListener() {
                @Override
                public void onSpeakStart() {
                    Log.d(TAG, "语音播报开始: " + content);
                }

                @Override
                public void onSpeakComplete() {
                    Log.d(TAG, "语音播报完成: " + content);
                    // 播报完成后，自动播放下一个节目
                    if (isPlaying && !isPaused) {
                        mainHandler.postDelayed(new Runnable() {
                            @Override
                            public void run() {
                                next();
                            }
                        }, 2000); // 2秒后播放下一个
                    }
                }

                @Override
                public void onSpeakPaused() {}

                @Override
                public void onSpeakResumed() {}

                @Override
                public void onError(String error) {
                    Log.e(TAG, "语音播报错误: " + error);
                }
            });
        }
    }

    /**
     * 启动进度计时器
     */
    private void startProgressTimer() {
        stopProgressTimer();

        progressTimer = new Timer();
        progressTimer.schedule(new TimerTask() {
            @Override
            public void run() {
                if (isPlaying && !isPaused) {
                    currentProgress++;
                    mainHandler.post(new Runnable() {
                        @Override
                        public void run() {
                            if (listener != null) {
                                listener.onProgressChanged(currentProgress, totalProgress);
                            }
                        }
                    });

                    // 检查是否播放完成
                    if (currentProgress >= totalProgress) {
                        stop();
                        mainHandler.post(new Runnable() {
                            @Override
                            public void run() {
                                if (listener != null) {
                                    listener.onPlaybackCompleted();
                                }
                            }
                        });
                    }
                }
            }
        }, 1000, 1000); // 每秒更新一次
    }

    /**
     * 停止进度计时器
     */
    private void stopProgressTimer() {
        if (progressTimer != null) {
            progressTimer.cancel();
            progressTimer = null;
        }
    }

    // ==================== Getters ====================

    public boolean isPlaying() {
        return isPlaying;
    }

    public boolean isPaused() {
        return isPaused;
    }

    public int getCurrentIndex() {
        return currentIndex;
    }

    public ProgramItem getCurrentProgram() {
        if (currentIndex >= 0 && currentIndex < programs.size()) {
            return programs.get(currentIndex);
        }
        return null;
    }

    public List<ProgramItem> getPrograms() {
        return programs;
    }

    public int getCurrentProgress() {
        return currentProgress;
    }

    public int getTotalProgress() {
        return totalProgress;
    }

    // ==================== 回调接口 ====================

    public void setPlaybackListener(PlaybackListener listener) {
        this.listener = listener;
    }

    /**
     * 播放监听接口
     */
    public interface PlaybackListener {
        /**
         * 节目表已加载
         */
        void onProgramsLoaded(int count);

        /**
         * 播放开始
         */
        void onPlayStarted();

        /**
         * 已暂停
         */
        void onPaused();

        /**
         * 已恢复
         */
        void onResumed();

        /**
         * 已停止
         */
        void onStopped();

        /**
         * 已跳转到指定节目
         */
        void onJumpedTo(int index);

        /**
         * 节目已切换
         */
        void onProgramChanged(int index, ProgramItem item);

        /**
         * 动作开始
         */
        void onActionStarted(DigitalHumanAction action);

        /**
         * 动作完成
         */
        void onActionCompleted(DigitalHumanAction action);

        /**
         * 进度更新
         */
        void onProgressChanged(int current, int total);

        /**
         * 播放完成
         */
        void onPlaybackCompleted();

        /**
         * 发生错误
         */
        void onError(String error);
    }
}
