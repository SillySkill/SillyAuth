package com.jcoding.aiactivity.entity;

/**
 * 内场秀子模块类型
 *
 * 系统分为3个子模块，每个模块有独立的功能和配置
 */
public enum InnerShowModule {

    /**
     * AI暖场秀
     * 功能：活动开始前的暖场展示
     * 特点：接收广播推送、背景循环、音乐播放
     */
    WARMUP("warmup", "AI暖场秀", "活动前暖场"),

    /**
     * AI主持秀
     * 功能：根据节目表进行数字人主持
     * 特点：Excel导入、智能播报、动作匹配
     */
    HOSTING("hosting", "AI主持秀", "节目主持"),

    /**
     * AI茶歇秀
     * 功能：茶歇时间的休闲展示
     * 特点：轻松氛围、互动游戏、照片轮播
     */
    TEA_BREAK("tea_break", "AI茶歇秀", "茶歇休闲");

    private final String id;
    private final String name;
    private final String description;

    InnerShowModule(String id, String name, String description) {
        this.id = id;
        this.name = name;
        this.description = description;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    /**
     * 从ID获取模块
     */
    public static InnerShowModule fromId(String id) {
        for (InnerShowModule module : values()) {
            if (module.id.equals(id)) {
                return module;
            }
        }
        return WARMUP; // 默认返回暖场秀
    }

    /**
     * 获取显示名称
     */
    @Override
    public String toString() {
        return name;
    }
}
