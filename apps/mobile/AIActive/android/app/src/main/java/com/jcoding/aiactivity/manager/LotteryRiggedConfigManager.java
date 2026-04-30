package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.content.SharedPreferences;
import android.text.TextUtils;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.jcoding.aiactivity.entity.Candidate;
import com.jcoding.aiactivity.utils.PreferenceUtils;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 抽奖配置管理器
 * 管理内定模式配置和抽奖模式设置
 */
public class LotteryRiggedConfigManager {

    private static final String PREF_LOTTERY_CONFIG = "lottery_rigged_config";
    private static final String KEY_MODE = "lottery_mode";  // rigged=内定, random=随机
    private static final String KEY_RIGGED_CONFIG = "rigged_config";  // 内定配置JSON
    private static final String KEY_PRIZE_LIST = "prize_list";  // 奖品列表JSON

    /**
     * 抽奖模式
     */
    public enum LotteryMode {
        RANDOM("random", "随机模式（彩旗）", true),
        RIGGED("rigged", "内定模式（灰度）", false);

        private String code;
        private String displayName;
        private boolean isFair;

        LotteryMode(String code, String displayName, boolean isFair) {
            this.code = code;
            this.displayName = displayName;
            this.isFair = isFair;
        }

        public String getCode() {
            return code;
        }

        public String getDisplayName() {
            return displayName;
        }

        public boolean isFair() {
            return isFair;
        }

        public static LotteryMode fromCode(String code) {
            for (LotteryMode mode : values()) {
                if (mode.code.equals(code)) {
                    return mode;
                }
            }
            return RANDOM;  // 默认随机模式
        }
    }

    /**
     * 标的对象类型（决定滚动显示什么）
     */
    public enum TargetType {
        PERSON("person", "标的对象：人", "滚动显示候选人信息，抽出中奖人"),
        PRIZE("prize", "标的对象：奖品", "滚动显示奖品信息，抽出中奖奖品");

        private String code;
        private String displayName;
        private String description;

        TargetType(String code, String displayName, String description) {
            this.code = code;
            this.displayName = displayName;
            this.description = description;
        }

        public String getCode() {
            return code;
        }

        public String getDisplayName() {
            return displayName;
        }

        public String getDescription() {
            return description;
        }

        public static TargetType fromCode(String code) {
            for (TargetType type : values()) {
                if (type.code.equals(code)) {
                    return type;
                }
            }
            return PERSON;  // 默认标的对象是人
        }
    }

    /**
     * 奖品项
     */
    public static class PrizeItem {
        public String id;
        public String name;        // 奖品名称
        public String description; // 奖品描述
        public int quantity;       // 数量
        public String imageUrl;    // 奖品图片URL（可选）

        public PrizeItem() {
            this.id = "prize_" + System.currentTimeMillis();
            this.quantity = 1;
        }

        public PrizeItem(String name, String description) {
            this();
            this.name = name;
            this.description = description;
        }

        public PrizeItem(String name, String description, int quantity) {
            this(name, description);
            this.quantity = quantity;
        }
    }

    /**
     * 内定配置项
     */
    public static class RiggedConfigItem {
        public String id;
        public int round;           // 轮次
        public TargetType targetType; // 标的对象类型
        public String prizeName;    // 奖品名称
        public String candidateId;   // 内定候选人ID（标的对象是人时需要）
        public String candidateName; // 内定候选人姓名（标的对象是人时需要）
        public String prizeId;      // 内定奖品ID（标的对象是奖品时需要）

        public RiggedConfigItem() {
            this.id = "rigged_" + System.currentTimeMillis();
            this.targetType = TargetType.PERSON;  // 默认标的对象是人
        }

        public RiggedConfigItem(int round, TargetType targetType, String prizeName,
                                String candidateId, String candidateName, String prizeId) {
            this();
            this.round = round;
            this.targetType = targetType;
            this.prizeName = prizeName;
            this.candidateId = candidateId;
            this.candidateName = candidateName;
            this.prizeId = prizeId;
        }

        /**
         * 标的对象是人
         */
        public boolean isTargetPerson() {
            return targetType == TargetType.PERSON;
        }

        /**
         * 标的对象是奖品
         */
        public boolean isTargetPrize() {
            return targetType == TargetType.PRIZE;
        }
    }

    private static LotteryRiggedConfigManager instance;
    private Context context;
    private Gson gson;

    private LotteryRiggedConfigManager(Context context) {
        this.context = context.getApplicationContext();
        this.gson = new Gson();
    }

    public static synchronized LotteryRiggedConfigManager getInstance(Context context) {
        if (instance == null) {
            instance = new LotteryRiggedConfigManager(context);
        }
        return instance;
    }

    /**
     * 获取当前抽奖模式
     */
    public LotteryMode getLotteryMode() {
        String modeCode = PreferenceUtils.getString(context, KEY_MODE, LotteryMode.RANDOM.getCode());
        return LotteryMode.fromCode(modeCode);
    }

    /**
     * 设置抽奖模式
     */
    public void setLotteryMode(LotteryMode mode) {
        PreferenceUtils.putString(context, KEY_MODE, mode.getCode());
    }

    // ========== 奖品列表管理 ==========

    /**
     * 获取奖品列表
     */
    public List<PrizeItem> getPrizeList() {
        String json = PreferenceUtils.getString(context, KEY_PRIZE_LIST, "[]");
        Type listType = new TypeToken<List<PrizeItem>>() {}.getType();
        List<PrizeItem> list = gson.fromJson(json, listType);
        if (list == null) {
            list = new ArrayList<>();
        }
        return list;
    }

    /**
     * 保存奖品列表
     */
    private void savePrizeList(List<PrizeItem> list) {
        String json = gson.toJson(list);
        PreferenceUtils.putString(context, KEY_PRIZE_LIST, json);
    }

    /**
     * 添加奖品
     */
    public void addPrize(PrizeItem prize) {
        List<PrizeItem> list = getPrizeList();
        list.add(prize);
        savePrizeList(list);
    }

    /**
     * 根据ID获取奖品
     */
    public PrizeItem getPrizeById(String prizeId) {
        List<PrizeItem> list = getPrizeList();
        for (PrizeItem prize : list) {
            if (prize.id.equals(prizeId)) {
                return prize;
            }
        }
        return null;
    }

    /**
     * 删除奖品
     */
    public void removePrize(String prizeId) {
        List<PrizeItem> list = getPrizeList();
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).id.equals(prizeId)) {
                list.remove(i);
                savePrizeList(list);
                return;
            }
        }
    }

    /**
     * 清空奖品列表
     */
    public void clearPrizeList() {
        savePrizeList(new ArrayList<PrizeItem>());
    }

    // ========== 内定配置管理 ==========

    /**
     * 获取内定配置列表
     */
    public List<RiggedConfigItem> getRiggedConfig() {
        String json = PreferenceUtils.getString(context, KEY_RIGGED_CONFIG, "[]");
        Type listType = new TypeToken<List<RiggedConfigItem>>() {}.getType();
        List<RiggedConfigItem> list = gson.fromJson(json, listType);
        if (list == null) {
            list = new ArrayList<>();
        }
        return list;
    }

    /**
     * 保存内定配置列表
     */
    public void saveRiggedConfig(List<RiggedConfigItem> config) {
        String json = gson.toJson(config);
        PreferenceUtils.putString(context, KEY_RIGGED_CONFIG, json);
    }

    /**
     * 添加内定配置
     */
    public void addRiggedConfig(RiggedConfigItem item) {
        List<RiggedConfigItem> list = getRiggedConfig();
        list.add(item);
        saveRiggedConfig(list);
    }

    /**
     * 更新内定配置
     */
    public void updateRiggedConfig(RiggedConfigItem item) {
        List<RiggedConfigItem> list = getRiggedConfig();
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).id.equals(item.id)) {
                list.set(i, item);
                saveRiggedConfig(list);
                return;
            }
        }
    }

    /**
     * 删除内定配置
     */
    public void removeRiggedConfig(String itemId) {
        List<RiggedConfigItem> list = getRiggedConfig();
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).id.equals(itemId)) {
                list.remove(i);
                saveRiggedConfig(list);
                return;
            }
        }
    }

    /**
     * 清空内定配置
     */
    public void clearRiggedConfig() {
        saveRiggedConfig(new ArrayList<RiggedConfigItem>());
    }

    /**
     * 根据轮次获取内定配置
     */
    public RiggedConfigItem getRiggedConfigByRound(int round) {
        List<RiggedConfigItem> list = getRiggedConfig();
        for (RiggedConfigItem item : list) {
            if (item.round == round) {
                return item;
            }
        }
        return null;
    }

    /**
     * 检查某轮次是否已内定
     */
    public boolean isRoundRigged(int round) {
        return getRiggedConfigByRound(round) != null;
    }

    /**
     * 获取已内定的轮次列表
     */
    public List<Integer> getRiggedRounds() {
        List<Integer> rounds = new ArrayList<>();
        List<RiggedConfigItem> list = getRiggedConfig();
        for (RiggedConfigItem item : list) {
            if (!rounds.contains(item.round)) {
                rounds.add(item.round);
            }
        }
        return rounds;
    }

    /**
     * 获取内定统计信息
     */
    public String getRiggedSummary() {
        List<RiggedConfigItem> list = getRiggedConfig();
        if (list.isEmpty()) {
            return "暂无内定配置";
        }

        Map<Integer, Integer> roundCount = new HashMap<>();
        for (RiggedConfigItem item : list) {
            roundCount.put(item.round, roundCount.getOrDefault(item.round, 0) + 1);
        }

        StringBuilder sb = new StringBuilder();
        sb.append("已内定 ").append(list.size()).append(" 项，涉及 ").append(roundCount.size()).append(" 轮：\n");
        for (Map.Entry<Integer, Integer> entry : roundCount.entrySet()) {
            sb.append("第").append(entry.getKey()).append("轮：").append(entry.getValue()).append("项\n");
        }

        return sb.toString().trim();
    }
}
