package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.MediaPlayer;
import android.util.Log;

import java.io.IOException;

/**
 * 抽奖音频管理器
 * 管理背景音乐和音效的播放
 */
public class LotteryAudioManager {

    private static final String TAG = "LotteryAudioManager";
    private static LotteryAudioManager instance;

    private Context context;
    private MediaPlayer backgroundMusicPlayer;
    private MediaPlayer soundEffectPlayer;

    // 音频状态
    private boolean bgMusicEnabled = false;
    private boolean soundEffectsEnabled = false;
    private float volume = 0.7f;

    // 音频文件路径
    private String bgMusicPath = "lottery/audio/background.mp3";
    private String startSoundPath = "lottery/audio/start.wav";
    private String drawingSoundPath = "lottery/audio/drawing.mp3";
    private String winnerSoundPath = "lottery/audio/winner.mp3";
    private String clickSoundPath = "lottery/audio/click.wav";

    private LotteryAudioManager(Context context) {
        this.context = context.getApplicationContext();
    }

    public static LotteryAudioManager getInstance(Context context) {
        if (instance == null) {
            synchronized (LotteryAudioManager.class) {
                if (instance == null) {
                    instance = new LotteryAudioManager(context);
                }
            }
        }
        return instance;
    }

    /**
     * 设置配置
     */
    public void setConfig(boolean bgMusicEnabled, boolean soundEffectsEnabled, float volume) {
        this.bgMusicEnabled = bgMusicEnabled;
        this.soundEffectsEnabled = soundEffectsEnabled;
        this.volume = volume;

        // 更新当前播放器的音量
        if (backgroundMusicPlayer != null) {
            backgroundMusicPlayer.setVolume(volume, volume);
        }
        if (soundEffectPlayer != null) {
            soundEffectPlayer.setVolume(volume, volume);
        }
    }

    /**
     * 播放背景音乐
     */
    public void playBackgroundMusic() {
        if (!bgMusicEnabled) {
            Log.d(TAG, "背景音乐已禁用");
            return;
        }

        try {
            if (backgroundMusicPlayer == null) {
                backgroundMusicPlayer = new MediaPlayer();
            }

            if (backgroundMusicPlayer.isPlaying()) {
                Log.d(TAG, "背景音乐已在播放");
                return;
            }

            // 尝试从assets加载
            try {
                String assetPath = bgMusicPath;
                // 检查文件是否存在
                String[] files = context.getAssets().list("lottery/audio");

                // 尝试多个可能的背景音乐文件
                if (files != null) {
                    for (String file : files) {
                        if (file.contains("worldcup") || file.contains("background") || file.contains("bg")) {
                            assetPath = "lottery/audio/" + file;
                            break;
                        }
                    }
                }

                AssetFileDescriptor afd = context.getAssets().openFd(assetPath);
                backgroundMusicPlayer.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
                afd.close();

                backgroundMusicPlayer.setLooping(true);
                backgroundMusicPlayer.setVolume(volume, volume);
                backgroundMusicPlayer.prepare();
                backgroundMusicPlayer.start();

                Log.d(TAG, "背景音乐开始播放: " + assetPath);
            } catch (IOException e) {
                Log.e(TAG, "加载背景音乐失败，尝试默认路径: " + e.getMessage());
                // 尝试使用默认的世界杯音乐
                try {
                    AssetFileDescriptor afd = context.getAssets().openFd("lottery/circle/src/assets/audio/worldcup.mp3");
                    backgroundMusicPlayer.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
                    afd.close();

                    backgroundMusicPlayer.setLooping(true);
                    backgroundMusicPlayer.setVolume(volume, volume);
                    backgroundMusicPlayer.prepare();
                    backgroundMusicPlayer.start();

                    Log.d(TAG, "使用默认背景音乐");
                } catch (IOException e2) {
                    Log.e(TAG, "加载默认背景音乐也失败: " + e2.getMessage());
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "播放背景音乐异常: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 停止背景音乐
     */
    public void stopBackgroundMusic() {
        if (backgroundMusicPlayer != null && backgroundMusicPlayer.isPlaying()) {
            backgroundMusicPlayer.pause();
            backgroundMusicPlayer.seekTo(0);
            Log.d(TAG, "背景音乐已停止");
        }
    }

    /**
     * 暂停背景音乐
     */
    public void pauseBackgroundMusic() {
        if (backgroundMusicPlayer != null && backgroundMusicPlayer.isPlaying()) {
            backgroundMusicPlayer.pause();
            Log.d(TAG, "背景音乐已暂停");
        }
    }

    /**
     * 恢复背景音乐
     */
    public void resumeBackgroundMusic() {
        if (bgMusicEnabled && backgroundMusicPlayer != null && !backgroundMusicPlayer.isPlaying()) {
            backgroundMusicPlayer.start();
            Log.d(TAG, "背景音乐已恢复");
        }
    }

    /**
     * 播放开始音效
     */
    public void playStartSound() {
        if (!soundEffectsEnabled) return;
        playSound(startSoundPath);
    }

    /**
     * 播放抽奖滚动音效（循环）
     */
    public void playDrawingSound() {
        if (!soundEffectsEnabled) return;
        playSound(drawingSoundPath, true);
    }

    /**
     * 停止抽奖滚动音效
     */
    public void stopDrawingSound() {
        if (soundEffectPlayer != null && soundEffectPlayer.isPlaying()) {
            soundEffectPlayer.stop();
            soundEffectPlayer.reset();
            Log.d(TAG, "抽奖音效已停止");
        }
    }

    /**
     * 播放中奖音效
     */
    public void playWinnerSound() {
        if (!soundEffectsEnabled) return;

        // 先停止滚动音效
        stopDrawingSound();

        // 播放中奖音效
        try {
            if (soundEffectPlayer == null) {
                soundEffectPlayer = new MediaPlayer();
            }

            if (soundEffectPlayer.isPlaying()) {
                soundEffectPlayer.stop();
            }

            soundEffectPlayer.reset();

            // 尝试加载end.mp3
            try {
                AssetFileDescriptor afd = context.getAssets().openFd("lottery/circle/src/assets/audio/end.mp3");
                soundEffectPlayer.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
                afd.close();

                soundEffectPlayer.setVolume(volume, volume);
                soundEffectPlayer.prepare();
                soundEffectPlayer.start();

                soundEffectPlayer.setOnCompletionListener(mp -> Log.d(TAG, "中奖音效播放完成"));

                Log.d(TAG, "中奖音效开始播放");
            } catch (IOException e) {
                Log.e(TAG, "加载中奖音效失败: " + e.getMessage());
            }
        } catch (Exception e) {
            Log.e(TAG, "播放中奖音效异常: " + e.getMessage());
        }
    }

    /**
     * 播放点击音效
     */
    public void playClickSound() {
        if (!soundEffectsEnabled) return;
        playSound(clickSoundPath);
    }

    /**
     * 播放指定音效
     */
    private void playSound(String soundPath) {
        playSound(soundPath, false);
    }

    /**
     * 播放指定音效
     * @param soundPath 音效路径
     * @param looping 是否循环播放
     */
    private void playSound(String soundPath, boolean looping) {
        try {
            if (soundEffectPlayer == null) {
                soundEffectPlayer = new MediaPlayer();
            }

            if (soundEffectPlayer.isPlaying()) {
                soundEffectPlayer.stop();
            }

            soundEffectPlayer.reset();

            // 尝试从assets加载
            try {
                AssetFileDescriptor afd = context.getAssets().openFd(soundPath);
                soundEffectPlayer.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
                afd.close();

                soundEffectPlayer.setLooping(looping);
                soundEffectPlayer.setVolume(volume, volume);
                soundEffectPlayer.prepare();
                soundEffectPlayer.start();

                Log.d(TAG, "音效播放: " + soundPath + (looping ? " (循环)" : ""));
            } catch (IOException e) {
                Log.e(TAG, "加载音效失败: " + soundPath + ", " + e.getMessage());

                // 尝试使用备用路径
                try {
                    String backupPath = "lottery/circle/src/assets/audio/" + soundPath.substring(soundPath.lastIndexOf("/") + 1);
                    AssetFileDescriptor afd = context.getAssets().openFd(backupPath);
                    soundEffectPlayer.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
                    afd.close();

                    soundEffectPlayer.setLooping(looping);
                    soundEffectPlayer.setVolume(volume, volume);
                    soundEffectPlayer.prepare();
                    soundEffectPlayer.start();

                    Log.d(TAG, "使用备用路径: " + backupPath);
                } catch (IOException e2) {
                    Log.e(TAG, "备用路径也失败: " + e2.getMessage());
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "播放音效异常: " + e.getMessage());
        }
    }

    /**
     * 释放资源
     */
    public void release() {
        if (backgroundMusicPlayer != null) {
            backgroundMusicPlayer.release();
            backgroundMusicPlayer = null;
        }

        if (soundEffectPlayer != null) {
            soundEffectPlayer.release();
            soundEffectPlayer = null;
        }

        Log.d(TAG, "音频资源已释放");
    }

    /**
     * 检查背景音乐是否正在播放
     */
    public boolean isBackgroundMusicPlaying() {
        return backgroundMusicPlayer != null && backgroundMusicPlayer.isPlaying();
    }

    /**
     * 获取当前音量
     */
    public float getVolume() {
        return volume;
    }

    /**
     * 获取背景音乐启用状态
     */
    public boolean isBgMusicEnabled() {
        return bgMusicEnabled;
    }

    /**
     * 获取音效启用状态
     */
    public boolean isSoundEffectsEnabled() {
        return soundEffectsEnabled;
    }
}
