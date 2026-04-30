package com.jcoding.aiactivity.entity;

/**
 * 活动轮播项
 * 支持图片和视频
 */
public class BannerItem {
    public static final int TYPE_IMAGE = 1;
    public static final int TYPE_VIDEO = 2;

    private String assetPath;     // assets路径，如 "banner/1.jpg" 或 "banner/video1.mp4"
    private int type;             // 类型：图片或视频
    private int duration;         // 显示时长（毫秒），仅图片有效，视频以实际时长为准

    public BannerItem(String assetPath, int type, int duration) {
        this.assetPath = assetPath;
        this.type = type;
        this.duration = duration;
    }

    public BannerItem(String assetPath, int type) {
        this(assetPath, type, 3000); // 默认3秒
    }

    public String getAssetPath() {
        return assetPath;
    }

    public void setAssetPath(String assetPath) {
        this.assetPath = assetPath;
    }

    public int getType() {
        return type;
    }

    public void setType(int type) {
        this.type = type;
    }

    public int getDuration() {
        return duration;
    }

    public void setDuration(int duration) {
        this.duration = duration;
    }

    public boolean isImage() {
        return type == TYPE_IMAGE;
    }

    public boolean isVideo() {
        return type == TYPE_VIDEO;
    }
}
