package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.MediaPlayer;
import android.util.Log;

import com.jcoding.aiactivity.entity.InnerShowModule;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * 背景媒体管理器
 *
 * 管理内场秀的：
 * 1. 背景图片/视频
 * 2. 背景音乐
 * 3. 装饰贴纸
 */
public class BackgroundMediaManager {

    private static final String TAG = "BackgroundMediaManager";
    private static BackgroundMediaManager instance;

    private Context context;
    private ConfigManager configManager;

    // 背景资源
    private Map<InnerShowModule, String> backgroundImages;  // 模块 -> 背景图片路径
    private Map<InnerShowModule, String> backgroundVideos;  // 模块 -> 背景视频路径
    private Map<InnerShowModule, String> backgroundMusic;    // 模块 -> 背景音乐路径

    // 贴纸资源
    private Map<String, Sticker> stickers;  // 贴纸ID -> 贴纸对象
    private Map<InnerShowModule, String> activeStickers;  // 模块 -> 当前贴纸ID

    // 媒体播放器
    private MediaPlayer musicPlayer;
    private boolean isMusicPlaying = false;
    private float musicVolume = 0.7f;

    private BackgroundMediaManager(Context context) {
        this.context = context.getApplicationContext();
        this.configManager = ConfigManager.getInstance(context);

        this.backgroundImages = new HashMap<>();
        this.backgroundVideos = new HashMap<>();
        this.backgroundMusic = new HashMap<>();
        this.stickers = new HashMap<>();
        this.activeStickers = new HashMap<>();

        // 初始化默认资源
        initializeDefaults();
    }

    public static synchronized BackgroundMediaManager getInstance(Context context) {
        if (instance == null) {
            instance = new BackgroundMediaManager(context);
        }
        return instance;
    }

    /**
     * 初始化默认资源
     */
    private void initializeDefaults() {
        // 默认背景（从assets加载）
        backgroundImages.put(InnerShowModule.WARMUP, "video/background/warmup_bg.jpg");
        backgroundImages.put(InnerShowModule.HOSTING, "video/background/hosting_bg.jpg");
        backgroundImages.put(InnerShowModule.TEA_BREAK, "video/background/teabreak_bg.jpg");

        // 默认音乐
        backgroundMusic.put(InnerShowModule.WARMUP, "video/music/warmup.mp3");
        backgroundMusic.put(InnerShowModule.HOSTING, "video/music/hosting.mp3");
        backgroundMusic.put(InnerShowModule.TEA_BREAK, "video/music/teabreak.mp3");

        // 默认贴纸
        loadDefaultStickers();
    }

    /**
     * 加载默认贴纸
     */
    private void loadDefaultStickers() {
        // 创建默认贴纸
        stickers.put("confetti", new Sticker("confetti", "彩带", "sticker/confetti.png", 100, 100));
        stickers.put("star", new Sticker("star", "星星", "sticker/star.png", 80, 80));
        stickers.put("heart", new Sticker("heart", "爱心", "sticker/heart.png", 60, 60));
        stickers.put("fireworks", new Sticker("fireworks", "烟花", "sticker/fireworks.png", 150, 150));
    }

    // ==================== 背景管理 ====================

    /**
     * 设置背景图片
     */
    public void setBackgroundImage(InnerShowModule module, String imagePath) {
        backgroundImages.put(module, imagePath);
        configManager.setInnerShowBackground(module.getId(), imagePath);
        Log.i(TAG, "背景图片已设置: " + module.getName() + " -> " + imagePath);
    }

    /**
     * 获取背景图片
     */
    public String getBackgroundImage(InnerShowModule module) {
        String path = backgroundImages.get(module);
        if (path == null) {
            // 从配置读取
            path = configManager.getInnerShowBackground(module.getId());
            if (path != null) {
                backgroundImages.put(module, path);
            }
        }
        return path;
    }

    /**
     * 设置背景视频
     */
    public void setBackgroundVideo(InnerShowModule module, String videoPath) {
        backgroundVideos.put(module, videoPath);
        configManager.setInnerShowBackgroundVideo(module.getId(), videoPath);
        Log.i(TAG, "背景视频已设置: " + module.getName() + " -> " + videoPath);
    }

    /**
     * 获取背景视频
     */
    public String getBackgroundVideo(InnerShowModule module) {
        String path = backgroundVideos.get(module);
        if (path == null) {
            path = configManager.getInnerShowBackgroundVideo(module.getId());
            if (path != null) {
                backgroundVideos.put(module, path);
            }
        }
        return path;
    }

    /**
     * 加载背景图片为Bitmap
     */
    public Bitmap loadBackgroundBitmap(InnerShowModule module) {
        String path = getBackgroundImage(module);
        if (path != null) {
            if (path.startsWith("assets/")) {
                // 从assets加载
                String assetPath = path.substring(7); // 移除 "assets/" 前缀
                return configManager.loadImageFromAssets(assetPath);
            } else {
                // 从文件加载
                return BitmapFactory.decodeFile(path);
            }
        }
        return null;
    }

    // ==================== 音乐管理 ====================

    /**
     * 设置背景音乐
     */
    public void setBackgroundMusic(InnerShowModule module, String musicPath) {
        backgroundMusic.put(module, musicPath);
        configManager.setInnerShowBackgroundMusic(module.getId(), musicPath);
        Log.i(TAG, "背景音乐已设置: " + module.getName() + " -> " + musicPath);
    }

    /**
     * 获取背景音乐
     */
    public String getBackgroundMusic(InnerShowModule module) {
        String path = backgroundMusic.get(module);
        if (path == null) {
            path = configManager.getInnerShowBackgroundMusic(module.getId());
            if (path != null) {
                backgroundMusic.put(module, path);
            }
        }
        return path;
    }

    /**
     * 播放背景音乐
     */
    public void playBackgroundMusic(InnerShowModule module) {
        String musicPath = getBackgroundMusic(module);
        if (musicPath == null || musicPath.isEmpty()) {
            Log.w(TAG, "没有设置背景音乐: " + module.getName());
            return;
        }

        try {
            // 停止当前播放
            stopBackgroundMusic();

            // 创建新的播放器
            musicPlayer = new MediaPlayer();

            if (musicPath.startsWith("assets/")) {
                // 从assets加载
                String assetPath = musicPath.substring(7);
                android.content.res.AssetFileDescriptor afd = context.getAssets().openFd(assetPath);
                musicPlayer.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
                afd.close();
            } else {
                // 从文件加载
                musicPlayer.setDataSource(musicPath);
            }

            musicPlayer.prepare();
            musicPlayer.setVolume(musicVolume, musicVolume);
            musicPlayer.setLooping(true); // 循环播放
            musicPlayer.start();

            isMusicPlaying = true;
            Log.i(TAG, "背景音乐开始播放: " + musicPath);

        } catch (IOException e) {
            Log.e(TAG, "播放背景音乐失败: " + musicPath, e);
        }
    }

    /**
     * 停止背景音乐
     */
    public void stopBackgroundMusic() {
        if (musicPlayer != null && musicPlayer.isPlaying()) {
            musicPlayer.stop();
            musicPlayer.release();
            musicPlayer = null;
            isMusicPlaying = false;
            Log.i(TAG, "背景音乐已停止");
        }
    }

    /**
     * 暂停背景音乐
     */
    public void pauseBackgroundMusic() {
        if (musicPlayer != null && musicPlayer.isPlaying()) {
            musicPlayer.pause();
            isMusicPlaying = false;
            Log.i(TAG, "背景音乐已暂停");
        }
    }

    /**
     * 恢复背景音乐
     */
    public void resumeBackgroundMusic() {
        if (musicPlayer != null && !musicPlayer.isPlaying()) {
            musicPlayer.start();
            isMusicPlaying = true;
            Log.i(TAG, "背景音乐已恢复");
        }
    }

    /**
     * 设置音乐音量
     */
    public void setMusicVolume(float volume) {
        this.musicVolume = volume;
        if (musicPlayer != null) {
            musicPlayer.setVolume(volume, volume);
        }
    }

    /**
     * 获取音乐音量
     */
    public float getMusicVolume() {
        return musicVolume;
    }

    /**
     * 检查音乐是否在播放
     */
    public boolean isMusicPlaying() {
        return isMusicPlaying && musicPlayer != null && musicPlayer.isPlaying();
    }

    // ==================== 贴纸管理 ====================

    /**
     * 添加贴纸
     */
    public void addSticker(String id, String name, String imagePath, int width, int height) {
        Sticker sticker = new Sticker(id, name, imagePath, width, height);
        stickers.put(id, sticker);
        Log.i(TAG, "贴纸已添加: " + name);
    }

    /**
     * 为模块添加贴纸
     */
    public void setSticker(InnerShowModule module, String stickerId) {
        activeStickers.put(module, stickerId);
        configManager.setInnerShowSticker(module.getId(), stickerId);
        Log.i(TAG, "贴纸已设置: " + module.getName() + " -> " + stickerId);
    }

    /**
     * 获取模块的贴纸
     */
    public Sticker getSticker(InnerShowModule module) {
        String stickerId = activeStickers.get(module);
        if (stickerId == null) {
            stickerId = configManager.getInnerShowSticker(module.getId());
            if (stickerId != null) {
                activeStickers.put(module, stickerId);
            }
        }

        if (stickerId != null) {
            return stickers.get(stickerId);
        }
        return null;
    }

    /**
     * 移除模块的贴纸
     */
    public void removeSticker(InnerShowModule module) {
        activeStickers.remove(module);
        configManager.setInnerShowSticker(module.getId(), null);
        Log.i(TAG, "贴纸已移除: " + module.getName());
    }

    /**
     * 获取所有贴纸
     */
    public Map<String, Sticker> getAllStickers() {
        return new HashMap<>(stickers);
    }

    /**
     * 贴纸数据类
     */
    public static class Sticker {
        public String id;
        public String name;
        public String imagePath;
        public int width;
        public int height;

        public Sticker(String id, String name, String imagePath, int width, int height) {
            this.id = id;
            this.name = name;
            this.imagePath = imagePath;
            this.width = width;
            this.height = height;
        }

        public String getId() { return id; }
        public String getName() { return name; }
        public String getImagePath() { return imagePath; }
        public int getWidth() { return width; }
        public int getHeight() { return height; }
    }
}
