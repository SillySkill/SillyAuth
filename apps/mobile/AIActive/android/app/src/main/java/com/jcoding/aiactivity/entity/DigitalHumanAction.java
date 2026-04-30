package com.jcoding.aiactivity.entity;

import java.util.HashMap;
import java.util.Map;

/**
 * 数字人动作类型
 *
 * 定义所有可用的数字人动作及其触发关键词
 */
public enum DigitalHumanAction {

    /**
     * 张开手
     * 场景：欢迎、开场
     */
    OPEN_HAND("open_hand", "张开手", "1.gif",
            "欢迎", "欢迎各位", "欢迎大家", "开场", "活动开始"),

    /**
     * 打招呼
     * 场景：问候、认识
     */
    SAY_HELLO("say_hello", "打招呼", "2.gif",
            "你好", "大家好", "各位来宾", "朋友们", "问候"),

    /**
     * 鼓掌
     * 场景：祝贺、感谢、欢迎
     */
    APPLAUD("applaud", "鼓掌", "3.gif",
            "祝贺", "恭喜", "感谢", "谢谢", "鼓掌", "热烈欢迎"),

    /**
     * 敬礼
     * 场景：致敬、开场、结束
     */
    SALUTE("salute", "敬礼", "4.gif",
            "致敬", "敬礼", "致意", "感谢"),

    /**
     * 自我介绍
     * 场景：开场介绍
     */
    INTRODUCE("introduce", "自我介绍", "5.gif",
            "介绍", "自我介绍", "我是", "我是方小松"),

    /**
     * 祝贺
     * 场景：恭喜、庆祝
     */
    CONGRATULATE("congratulate", "祝贺", "8.gif",
            "祝贺", "恭喜", "庆祝", "祝贺大家", "恭喜获奖"),

    /**
     * 左手指引
     * 场景：引导、指示
     */
    LEFT_POINT("left_point", "左手指引", "9.gif",
            "请看", "请看这边", "请注意", "左边", "左侧"),

    /**
     * 默认动作
     * 场景：待机
     */
    DEFAULT("default", "默认", "10.gif",
            "默认");

    private final String id;
    private final String name;
    private final String gifFile;
    private final String[] keywords;

    private static final Map<String, DigitalHumanAction> KEYWORD_MAP = new HashMap<>();

    static {
        // 构建关键词到动作的映射
        for (DigitalHumanAction action : values()) {
            for (String keyword : action.keywords) {
                KEYWORD_MAP.put(keyword, action);
            }
        }
    }

    DigitalHumanAction(String id, String name, String gifFile, String... keywords) {
        this.id = id;
        this.name = name;
        this.gifFile = gifFile;
        this.keywords = keywords;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getGifFile() {
        return gifFile;
    }

    /**
     * 根据关键词匹配动作
     *
     * @param text 文本内容
     * @return 匹配的动作，如果没有匹配返回DEFAULT
     */
    public static DigitalHumanAction matchAction(String text) {
        if (text == null || text.isEmpty()) {
            return DEFAULT;
        }

        // 查找包含关键词的动作
        for (Map.Entry<String, DigitalHumanAction> entry : KEYWORD_MAP.entrySet()) {
            if (text.contains(entry.getKey())) {
                return entry.getValue();
            }
        }

        return DEFAULT;
    }

    /**
     * 获取动作的资源路径
     */
    public String getAssetPath() {
        return "aibeing/" + gifFile;
    }
}
