package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;

import com.jcoding.aiactivity.entity.InnerShowModule;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 媒体资源管理器
 *
 * 统一管理内场秀设备的所有媒体资源
 *
 * 功能：
 * 1. 媒体资源索引管理
 * 2. 启用/禁用状态管理
 * 3. 媒体文件存储和访问
 * 4. 媒体上传处理
 * 5. 媒体同步状态
 */
public class MediaResourceManager {

    private static final String TAG = "MediaResourceManager";
    private static MediaResourceManager instance;

    private Context context;
    private ConfigManager configManager;

    // 媒体文件夹
    private File mediaRootDir;
    private File backgroundDir;
    private File musicDir;
    private File stickerDir;
    private File videoDir;

    // 媒体索引
    private Map<String, MediaItem> mediaIndex;  // mediaId -> MediaItem
    private Map<InnerShowModule, List<String>> moduleMediaMap;  // module -> mediaId list

    // 同步状态
    private long lastSyncTime = 0;

    private MediaResourceManager(Context context) {
        this.context = context.getApplicationContext();
        this.configManager = ConfigManager.getInstance(context);
        this.mediaIndex = new HashMap<>();
        this.moduleMediaMap = new HashMap<>();

        // 初始化目录
        initializeDirectories();

        // 加载索引
        loadMediaIndex();
    }

    public static synchronized MediaResourceManager getInstance(Context context) {
        if (instance == null) {
            instance = new MediaResourceManager(context);
        }
        return instance;
    }

    /**
     * 初始化媒体目录
     */
    private void initializeDirectories() {
        // 在内部存储创建媒体文件夹
        File internalDir = context.getFilesDir();
        mediaRootDir = new File(internalDir, "media_resources");

        if (!mediaRootDir.exists()) {
            mediaRootDir.mkdirs();
        }

        // 创建子目录
        backgroundDir = new File(mediaRootDir, "background");
        musicDir = new File(mediaRootDir, "music");
        stickerDir = new File(mediaRootDir, "sticker");
        videoDir = new File(mediaRootDir, "video");

        backgroundDir.mkdirs();
        musicDir.mkdirs();
        stickerDir.mkdirs();
        videoDir.mkdirs();

        Log.i(TAG, "媒体目录初始化完成: " + mediaRootDir.getAbsolutePath());
    }

    /**
     * 加载媒体索引
     */
    private void loadMediaIndex() {
        try {
            File indexFile = new File(mediaRootDir, "media_index.json");

            if (!indexFile.exists()) {
                Log.i(TAG, "媒体索引文件不存在，创建默认索引");
                createDefaultIndex();
                return;
            }

            FileInputStream fis = new FileInputStream(indexFile);
            byte[] data = new byte[(int) indexFile.length()];
            fis.read(data);
            fis.close();

            String json = new String(data, "UTF-8");
            JSONObject root = new JSONObject(json);

            // 解析同步时间
            lastSyncTime = root.optLong("last_sync_time", 0);

            // 解析媒体项
            JSONArray itemsArray = root.optJSONArray("items");
            if (itemsArray != null) {
                for (int i = 0; i < itemsArray.length(); i++) {
                    JSONObject itemObj = itemsArray.getJSONObject(i);
                    MediaItem item = MediaItem.fromJson(itemObj);

                    mediaIndex.put(item.id, item);

                    // 添加到模块映射
                    for (InnerShowModule module : item.modules) {
                        if (!moduleMediaMap.containsKey(module)) {
                            moduleMediaMap.put(module, new ArrayList<String>());
                        }
                        moduleMediaMap.get(module).add(item.id);
                    }
                }
            }

            Log.i(TAG, "媒体索引加载完成，共 " + mediaIndex.size() + " 个媒体项");

        } catch (Exception e) {
            Log.e(TAG, "加载媒体索引失败", e);
            createDefaultIndex();
        }
    }

    /**
     * 创建默认索引
     */
    private void createDefaultIndex() {
        // 添加assets中的默认资源
        addDefaultAssets();

        saveMediaIndex();
    }

    /**
     * 添加默认assets资源
     */
    private void addDefaultAssets() {
        // 默认背景
        addMediaItem("bg_warmup_default", "暖场背景", "background",
                "assets://video/background/warmup_bg.jpg",
                new InnerShowModule[]{InnerShowModule.WARMUP}, true);

        addMediaItem("bg_hosting_default", "主持背景", "background",
                "assets://video/background/hosting_bg.jpg",
                new InnerShowModule[]{InnerShowModule.HOSTING}, true);

        addMediaItem("bg_teabreak_default", "茶歇背景", "background",
                "assets://video/background/teabreak_bg.jpg",
                new InnerShowModule[]{InnerShowModule.TEA_BREAK}, true);

        // 默认音乐
        addMediaItem("music_warmup_default", "暖场音乐", "music",
                "assets://video/music/warmup.mp3",
                new InnerShowModule[]{InnerShowModule.WARMUP}, true);

        addMediaItem("music_hosting_default", "主持音乐", "music",
                "assets://video/music/hosting.mp3",
                new InnerShowModule[]{InnerShowModule.HOSTING}, true);

        addMediaItem("music_teabreak_default", "茶歇音乐", "music",
                "assets://video/music/teabreak.mp3",
                new InnerShowModule[]{InnerShowModule.TEA_BREAK}, true);

        // 默认贴纸
        addMediaItem("sticker_confetti", "彩带", "sticker",
                "assets://sticker/confetti.png",
                new InnerShowModule[]{InnerShowModule.WARMUP, InnerShowModule.HOSTING, InnerShowModule.TEA_BREAK}, true);

        addMediaItem("sticker_star", "星星", "sticker",
                "assets://sticker/star.png",
                new InnerShowModule[]{InnerShowModule.WARMUP, InnerShowModule.HOSTING, InnerShowModule.TEA_BREAK}, true);

        addMediaItem("sticker_heart", "爱心", "sticker",
                "assets://sticker/heart.png",
                new InnerShowModule[]{InnerShowModule.WARMUP, InnerShowModule.HOSTING, InnerShowModule.TEA_BREAK}, true);

        addMediaItem("sticker_fireworks", "烟花", "sticker",
                "assets://sticker/fireworks.png",
                new InnerShowModule[]{InnerShowModule.WARMUP, InnerShowModule.HOSTING, InnerShowModule.TEA_BREAK}, true);
    }

    /**
     * 保存媒体索引
     */
    private void saveMediaIndex() {
        try {
            File indexFile = new File(mediaRootDir, "media_index.json");

            JSONObject root = new JSONObject();
            root.put("last_sync_time", System.currentTimeMillis());
            root.put("version", "1.0");

            JSONArray itemsArray = new JSONArray();
            for (MediaItem item : mediaIndex.values()) {
                itemsArray.put(item.toJson());
            }
            root.put("items", itemsArray);

            String json = root.toString(2);

            FileOutputStream fos = new FileOutputStream(indexFile);
            fos.write(json.getBytes("UTF-8"));
            fos.close();

            Log.i(TAG, "媒体索引已保存");

        } catch (Exception e) {
            Log.e(TAG, "保存媒体索引失败", e);
        }
    }

    /**
     * 添加媒体项
     */
    public boolean addMediaItem(String id, String name, String type, String path,
                                InnerShowModule[] modules, boolean enabled) {
        MediaItem item = new MediaItem();
        item.id = id;
        item.name = name;
        item.type = type;
        item.path = path;
        item.enabled = enabled;
        item.addTime = System.currentTimeMillis();

        for (InnerShowModule module : modules) {
            item.modules.add(module);
        }

        mediaIndex.put(id, item);

        // 更新模块映射
        for (InnerShowModule module : modules) {
            if (!moduleMediaMap.containsKey(module)) {
                moduleMediaMap.put(module, new ArrayList<String>());
            }
            if (!moduleMediaMap.get(module).contains(id)) {
                moduleMediaMap.get(module).add(id);
            }
        }

        saveMediaIndex();

        Log.i(TAG, "媒体项已添加: " + name);

        return true;
    }

    /**
     * 删除媒体项
     */
    public boolean removeMediaItem(String id) {
        MediaItem item = mediaIndex.get(id);
        if (item == null) {
            return false;
        }

        // 从模块映射中移除
        for (InnerShowModule module : item.modules) {
            List<String> list = moduleMediaMap.get(module);
            if (list != null) {
                list.remove(id);
            }
        }

        // 从索引中移除
        mediaIndex.remove(id);

        saveMediaIndex();

        Log.i(TAG, "媒体项已删除: " + item.name);

        return true;
    }

    /**
     * 启用媒体
     */
    public boolean enableMedia(String id) {
        MediaItem item = mediaIndex.get(id);
        if (item == null) {
            return false;
        }

        item.enabled = true;
        saveMediaIndex();

        Log.i(TAG, "媒体已启用: " + item.name);

        return true;
    }

    /**
     * 禁用媒体
     */
    public boolean disableMedia(String id) {
        MediaItem item = mediaIndex.get(id);
        if (item == null) {
            return false;
        }

        item.enabled = false;
        saveMediaIndex();

        Log.i(TAG, "媒体已禁用: " + item.name);

        return true;
    }

    /**
     * 获取模块的媒体列表
     */
    public List<MediaItem> getModuleMedia(InnerShowModule module, String type) {
        List<MediaItem> result = new ArrayList<>();

        List<String> mediaIds = moduleMediaMap.get(module);
        if (mediaIds == null) {
            return result;
        }

        for (String id : mediaIds) {
            MediaItem item = mediaIndex.get(id);
            if (item != null && item.enabled) {
                if (type == null || type.equals(item.type)) {
                    result.add(item);
                }
            }
        }

        return result;
    }

    /**
     * 获取媒体项
     */
    public MediaItem getMediaItem(String id) {
        return mediaIndex.get(id);
    }

    /**
     * 上传媒体文件
     */
    public boolean uploadMedia(String sourcePath, String name, String type,
                               InnerShowModule[] modules) {
        try {
            // 生成唯一ID
            String id = "media_" + System.currentTimeMillis();

            // 确定目标目录
            File targetDir = null;
            switch (type) {
                case "background":
                    targetDir = backgroundDir;
                    break;
                case "music":
                    targetDir = musicDir;
                    break;
                case "sticker":
                    targetDir = stickerDir;
                    break;
                case "video":
                    targetDir = videoDir;
                    break;
            }

            if (targetDir == null) {
                Log.e(TAG, "无效的媒体类型: " + type);
                return false;
            }

            // 复制文件
            File sourceFile = new File(sourcePath);
            File targetFile = new File(targetDir, id + getFileExtension(sourcePath));

            if (!copyFile(sourceFile, targetFile)) {
                return false;
            }

            // 添加到索引
            String relativePath = targetFile.getAbsolutePath().replace(mediaRootDir.getAbsolutePath(), "");
            addMediaItem(id, name, type, relativePath, modules, true);

            Log.i(TAG, "媒体上传成功: " + name);

            return true;

        } catch (Exception e) {
            Log.e(TAG, "上传媒体失败", e);
            return false;
        }
    }

    /**
     * 复制文件
     */
    private boolean copyFile(File source, File target) {
        try {
            FileInputStream fis = new FileInputStream(source);
            FileOutputStream fos = new FileOutputStream(target);

            byte[] buffer = new byte[1024];
            int length;
            while ((length = fis.read(buffer)) > 0) {
                fos.write(buffer, 0, length);
            }

            fis.close();
            fos.close();

            return true;

        } catch (Exception e) {
            Log.e(TAG, "复制文件失败", e);
            return false;
        }
    }

    /**
     * 获取文件扩展名
     */
    private String getFileExtension(String path) {
        int dotIndex = path.lastIndexOf('.');
        if (dotIndex > 0) {
            return path.substring(dotIndex);
        }
        return "";
    }

    /**
     * 加载媒体图片
     */
    public Bitmap loadMediaImage(String id) {
        MediaItem item = mediaIndex.get(id);
        if (item == null) {
            return null;
        }

        if (item.path.startsWith("assets://")) {
            // 从assets加载
            String assetPath = item.path.substring(9);
            return configManager.loadImageFromAssets(assetPath);
        } else {
            // 从文件加载
            String fullPath = mediaRootDir.getAbsolutePath() + item.path;
            return BitmapFactory.decodeFile(fullPath);
        }
    }

    /**
     * 获取媒体文件路径
     */
    public String getMediaFilePath(String id) {
        MediaItem item = mediaIndex.get(id);
        if (item == null) {
            return null;
        }

        if (item.path.startsWith("assets://")) {
            return item.path;
        } else {
            return mediaRootDir.getAbsolutePath() + item.path;
        }
    }

    // ==================== 数据类 ====================

    /**
     * 媒体项
     */
    public static class MediaItem {
        public String id;                          // 唯一ID
        public String name;                        // 名称
        public String type;                        // 类型: background/music/sticker/video
        public String path;                        // 路径
        public boolean enabled;                    // 是否启用
        public long addTime;                       // 添加时间
        public List<InnerShowModule> modules = new ArrayList<>();  // 适用模块
        public transient InnerShowModule module;   // 主模块（用于快捷访问）

        /**
         * 获取第一个适用模块（用于快捷访问）
         */
        public InnerShowModule getModule() {
            if (module != null) {
                return module;
            }
            return modules.isEmpty() ? null : modules.get(0);
        }

        /**
         * 从JSON解析
         */
        public static MediaItem fromJson(JSONObject obj) {
            MediaItem item = new MediaItem();

            try {
                item.id = obj.getString("id");
                item.name = obj.getString("name");
                item.type = obj.getString("type");
                item.path = obj.getString("path");
                item.enabled = obj.getBoolean("enabled");
                item.addTime = obj.optLong("add_time", System.currentTimeMillis());

                JSONArray modulesArray = obj.optJSONArray("modules");
                if (modulesArray != null) {
                    for (int i = 0; i < modulesArray.length(); i++) {
                        String moduleId = modulesArray.getString(i);
                        InnerShowModule module = InnerShowModule.fromId(moduleId);
                        if (module != null) {
                            item.modules.add(module);
                        }
                    }
                }

            } catch (Exception e) {
                Log.e("MediaItem", "解析JSON失败", e);
            }

            return item;
        }

        /**
         * 转换为JSON
         */
        public JSONObject toJson() {
            JSONObject obj = new JSONObject();

            try {
                obj.put("id", id);
                obj.put("name", name);
                obj.put("type", type);
                obj.put("path", path);
                obj.put("enabled", enabled);
                obj.put("add_time", addTime);

                JSONArray modulesArray = new JSONArray();
                for (InnerShowModule module : modules) {
                    modulesArray.put(module.getId());
                }
                obj.put("modules", modulesArray);

            } catch (Exception e) {
                Log.e("MediaItem", "转换为JSON失败", e);
            }

            return obj;
        }
    }
}
