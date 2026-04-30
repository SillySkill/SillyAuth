package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.util.Log;

import com.jcoding.aiactivity.entity.DigitalHumanAction;
import com.jcoding.aiactivity.entity.ProgramItem;

import java.util.HashMap;
import java.util.Map;

/**
 * 动作匹配引擎
 *
 * 智能分析文本内容，匹配合适的数字人动作
 *
 * 匹配策略：
 * 1. 关键词匹配 - 检查预定义关键词
 * 2. 情感分析 - 分析文本情感倾向
 * 3. 场景识别 - 识别特定场景
 * 4. 自定义规则 - 支持用户自定义匹配规则
 */
public class ActionMatcher {

    private static final String TAG = "ActionMatcher";
    private static ActionMatcher instance;

    private Context context;

    // 情感关键词
    private static final Map<String, DigitalHumanAction> EMOTION_KEYWORDS = new HashMap<String, DigitalHumanAction>() {{
        put("恭喜", DigitalHumanAction.CONGRATULATE);
        put("祝贺", DigitalHumanAction.CONGRATULATE);
        put("庆祝", DigitalHumanAction.CONGRATULATE);
        put("获奖", DigitalHumanAction.CONGRATULATE);
        put("感谢", DigitalHumanAction.APPLAUD);
        put("谢谢", DigitalHumanAction.APPLAUD);
        put("欢迎", DigitalHumanAction.OPEN_HAND);
        put("开场", DigitalHumanAction.SAY_HELLO);
        put("介绍", DigitalHumanAction.INTRODUCE);
        put("注意", DigitalHumanAction.LEFT_POINT);
        put("请看", DigitalHumanAction.LEFT_POINT);
    }};

    // 场景模式
    private static final Map<String, DigitalHumanAction> SCENE_ACTIONS = new HashMap<String, DigitalHumanAction>() {{
        put("开场", DigitalHumanAction.SAY_HELLO);
        put("结束", DigitalHumanAction.SALUTE);
        put("颁奖", DigitalHumanAction.CONGRATULATE);
        put("抽奖", DigitalHumanAction.APPLAUD);
        put("游戏", DigitalHumanAction.OPEN_HAND);
        put("互动", DigitalHumanAction.SAY_HELLO);
    }};

    private ActionMatcher(Context context) {
        this.context = context.getApplicationContext();
    }

    public static synchronized ActionMatcher getInstance(Context context) {
        if (instance == null) {
            instance = new ActionMatcher(context);
        }
        return instance;
    }

    /**
     * 智能匹配动作
     *
     * @param item 节目项
     * @return 匹配的动作
     */
    public DigitalHumanAction matchAction(ProgramItem item) {
        if (item == null) {
            return DigitalHumanAction.DEFAULT;
        }

        String content = item.getContent();
        String remark = item.getRemark();

        // 1. 优先匹配备注中的场景
        DigitalHumanAction action = matchByScene(remark);
        if (action != DigitalHumanAction.DEFAULT) {
            Log.i(TAG, "场景匹配: " + remark + " -> " + action.getName());
            return action;
        }

        // 2. 匹配内容中的关键词
        action = matchByKeyword(content);
        if (action != DigitalHumanAction.DEFAULT) {
            Log.i(TAG, "关键词匹配: " + content + " -> " + action.getName());
            return action;
        }

        // 3. 情感分析
        action = matchByEmotion(content);
        if (action != DigitalHumanAction.DEFAULT) {
            Log.i(TAG, "情感匹配: " + content + " -> " + action.getName());
            return action;
        }

        // 4. 使用默认动作
        Log.i(TAG, "使用默认动作: " + content);
        return DigitalHumanAction.DEFAULT;
    }

    /**
     * 批量匹配动作
     *
     * @param items 节目项列表
     */
    public void matchActions(java.util.List<ProgramItem> items) {
        if (items == null || items.isEmpty()) {
            return;
        }

        for (ProgramItem item : items) {
            DigitalHumanAction action = matchAction(item);
            item.setAction(action);
        }

        Log.i(TAG, "批量匹配完成，共 " + items.size() + " 项");
    }

    /**
     * 场景匹配
     */
    private DigitalHumanAction matchByScene(String text) {
        if (text == null || text.isEmpty()) {
            return DigitalHumanAction.DEFAULT;
        }

        for (Map.Entry<String, DigitalHumanAction> entry : SCENE_ACTIONS.entrySet()) {
            if (text.contains(entry.getKey())) {
                return entry.getValue();
            }
        }

        return DigitalHumanAction.DEFAULT;
    }

    /**
     * 关键词匹配
     */
    private DigitalHumanAction matchByKeyword(String text) {
        return DigitalHumanAction.matchAction(text);
    }

    /**
     * 情感分析匹配
     */
    private DigitalHumanAction matchByEmotion(String text) {
        if (text == null || text.isEmpty()) {
            return DigitalHumanAction.DEFAULT;
        }

        // 积极情感
        if (text.contains("快乐") || text.contains("开心") || text.contains("欢乐")) {
            return DigitalHumanAction.APPLAUD;
        }

        // 尊敬情感
        if (text.contains("尊敬") || text.contains("嘉宾") || text.contains("领导")) {
            return DigitalHumanAction.SALUTE;
        }

        // 引导情感
        if (text.contains("现在") || text.contains("接下来") || text.contains("然后")) {
            return DigitalHumanAction.LEFT_POINT;
        }

        return DigitalHumanAction.DEFAULT;
    }

    /**
     * 手动设置动作（支持用户自定义）
     *
     * @param item 节目项
     * @param action 动作
     */
    public void setAction(ProgramItem item, DigitalHumanAction action) {
        if (item != null && action != null) {
            item.setAction(action);
            Log.i(TAG, "手动设置动作: " + item.getContent() + " -> " + action.getName());
        }
    }

    /**
     * 获取动作说明
     */
    public static String getActionDescription(DigitalHumanAction action) {
        if (action == null) {
            return "未设置";
        }

        switch (action) {
            case OPEN_HAND:
                return "张开手 - 适合开场、欢迎";
            case SAY_HELLO:
                return "打招呼 - 适合问候、介绍";
            case APPLAUD:
                return "鼓掌 - 适合祝贺、感谢";
            case SALUTE:
                return "敬礼 - 适合致敬、致谢";
            case INTRODUCE:
                return "自我介绍 - 适合开场";
            case CONGRATULATE:
                return "祝贺 - 适合恭喜、庆祝";
            case LEFT_POINT:
                return "左手指引 - 适合引导关注";
            case DEFAULT:
                return "默认动作";
            default:
                return action.getName();
        }
    }

    /**
     * 验证动作是否适合内容
     *
     * @param content 文本内容
     * @param action 动作
     * @return 是否适合
     */
    public boolean isActionSuitable(String content, DigitalHumanAction action) {
        if (content == null || action == null) {
            return true;
        }

        DigitalHumanAction matched = matchAction(content);
        return matched == action;
    }

    /**
     * 根据文本内容匹配动作（便捷方法）
     *
     * @param content 文本内容
     * @return 匹配的动作
     */
    public DigitalHumanAction matchAction(String content) {
        // 创建临时ProgramItem用于匹配
        ProgramItem tempItem = new ProgramItem();
        tempItem.setContent(content);
        return matchAction(tempItem);
    }
}
