package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.text.TextUtils;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.jcoding.aiactivity.utils.PreferenceUtils;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;

/**
 * 内场秀数据管理器
 * 负责管理AI百变秀生成的图片、签名、签到信息，同步到内场秀展示
 */
public class InnerShowDataManager {

    private static final String PREF_INNER_SHOW = "inner_show_data";
    private static final String KEY_GENERATION_LIST = "generation_list";
    private static final String KEY_CHECKIN_LIST = "checkin_list";
    private static final String KEY_CURRENT_IMAGE = "current_image";
    private static final String KEY_LOTTERY_CANDIDATES = "lottery_candidates";
    private static final String KEY_LOTTERY_WINNERS = "lottery_winners";
    private static final String KEY_QUIZ_WINNERS = "quiz_winners";

    private static InnerShowDataManager instance;
    private Context context;
    private Gson gson;

    private InnerShowDataManager(Context context) {
        this.context = context.getApplicationContext();
        this.gson = new Gson();
    }

    public static synchronized InnerShowDataManager getInstance(Context context) {
        if (instance == null) {
            instance = new InnerShowDataManager(context);
        }
        return instance;
    }

    // ========== AI生成结果管理 ==========

    /**
     * AI生成结果实体
     */
    public static class GenerationResult {
        public String id;
        public String styleId;
        public String styleName;
        public String originalImagePath;
        public String resultImagePath;
        public String resultImageUrl;
        public String userName;
        public String signature;
        public long timestamp;
        public boolean pushedToInner;

        public GenerationResult() {
            this.id = "gen_" + System.currentTimeMillis();
            this.timestamp = System.currentTimeMillis();
            this.pushedToInner = false;
        }
    }

    /**
     * 添加AI生成结果
     */
    public void addGenerationResult(GenerationResult result) {
        List<GenerationResult> list = getGenerationResults();
        list.add(0, result); // 添加到列表头部
        saveGenerationResults(list);

        // 设置为当前显示图片
        setCurrentDisplayImage(result.id);
    }

    /**
     * 获取所有AI生成结果
     */
    public List<GenerationResult> getGenerationResults() {
        String json = PreferenceUtils.getString(context, KEY_GENERATION_LIST, "[]");
        Type listType = new TypeToken<List<GenerationResult>>() {}.getType();
        List<GenerationResult> list = gson.fromJson(json, listType);
        if (list == null) {
            list = new ArrayList<>();
        }
        return list;
    }

    /**
     * 保存AI生成结果列表
     */
    private void saveGenerationResults(List<GenerationResult> list) {
        String json = gson.toJson(list);
        PreferenceUtils.putString(context, KEY_GENERATION_LIST, json);
    }

    /**
     * 根据ID获取生成结果
     */
    public GenerationResult getGenerationResult(String id) {
        List<GenerationResult> list = getGenerationResults();
        for (GenerationResult result : list) {
            if (result.id.equals(id)) {
                return result;
            }
        }
        return null;
    }

    /**
     * 更新生成结果
     */
    public void updateGenerationResult(GenerationResult updated) {
        List<GenerationResult> list = getGenerationResults();
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).id.equals(updated.id)) {
                list.set(i, updated);
                saveGenerationResults(list);
                return;
            }
        }
    }

    /**
     * 标记为已推送到内场秀
     */
    public void markAsPushedToInner(String resultId) {
        GenerationResult result = getGenerationResult(resultId);
        if (result != null) {
            result.pushedToInner = true;
            updateGenerationResult(result);
        }
    }

    /**
     * 设置当前显示的图片
     */
    public void setCurrentDisplayImage(String resultId) {
        PreferenceUtils.putString(context, KEY_CURRENT_IMAGE, resultId);
    }

    /**
     * 获取当前显示的图片
     */
    public GenerationResult getCurrentDisplayImage() {
        String currentId = PreferenceUtils.getString(context, KEY_CURRENT_IMAGE, "");
        if (!TextUtils.isEmpty(currentId)) {
            return getGenerationResult(currentId);
        }

        // 如果没有设置，返回最新的
        List<GenerationResult> list = getGenerationResults();
        if (!list.isEmpty()) {
            return list.get(0);
        }
        return null;
    }

    // ========== 签到管理 ==========

    /**
     * 签到记录实体
     */
    public static class CheckInRecord {
        public String id;
        public String userName;
        public String userPhone;
        public String department;
        public String signature;
        public long timestamp;
        public String photoPath; // 可选：签到照片

        public CheckInRecord() {
            this.id = "checkin_" + System.currentTimeMillis();
            this.timestamp = System.currentTimeMillis();
        }
    }

    /**
     * 添加签到记录
     */
    public void addCheckInRecord(CheckInRecord record) {
        List<CheckInRecord> list = getCheckInRecords();
        list.add(0, record);
        saveCheckInRecords(list);
    }

    /**
     * 获取所有签到记录
     */
    public List<CheckInRecord> getCheckInRecords() {
        String json = PreferenceUtils.getString(context, KEY_CHECKIN_LIST, "[]");
        Type listType = new TypeToken<List<CheckInRecord>>() {}.getType();
        List<CheckInRecord> list = gson.fromJson(json, listType);
        if (list == null) {
            list = new ArrayList<>();
        }
        return list;
    }

    /**
     * 保存签到记录列表
     */
    private void saveCheckInRecords(List<CheckInRecord> list) {
        String json = gson.toJson(list);
        PreferenceUtils.putString(context, KEY_CHECKIN_LIST, json);
    }

    /**
     * 清空签到记录
     */
    public void clearCheckInRecords() {
        PreferenceUtils.putString(context, KEY_CHECKIN_LIST, "[]");
    }

    /**
     * 获取签到人数
     */
    public int getCheckInCount() {
        return getCheckInRecords().size();
    }

    // ========== 待抽奖候选人管理 ==========

    /**
     * 添加待抽奖候选人（从签到或外部导入）
     */
    public void addLotteryCandidate(CheckInRecord record) {
        // 候选人直接复用签到记录结构
        // 可以额外标记为已抽奖
    }

    // ========== 图片文件管理 ==========

    /**
     * 保存图片到本地
     */
    public String saveImageToLocal(Bitmap bitmap, String fileName) {
        try {
            File imagesDir = new File(context.getFilesDir(), "inner_show_images");
            if (!imagesDir.exists()) {
                imagesDir.mkdirs();
            }

            File file = new File(imagesDir, fileName);
            FileOutputStream fos = new FileOutputStream(file);
            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, fos);
            fos.flush();
            fos.close();

            return file.getAbsolutePath();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 从本地加载图片
     */
    public Bitmap loadImageFromLocal(String filePath) {
        if (TextUtils.isEmpty(filePath)) {
            return null;
        }

        try {
            File file = new File(filePath);
            if (file.exists()) {
                return BitmapFactory.decodeStream(new FileInputStream(file));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    // ========== 数据清理 ==========

    /**
     * 清除所有数据
     */
    public void clearAllData() {
        PreferenceUtils.putString(context, KEY_GENERATION_LIST, "[]");
        PreferenceUtils.putString(context, KEY_CHECKIN_LIST, "[]");
        PreferenceUtils.putString(context, KEY_CURRENT_IMAGE, "");
    }

    /**
     * 清除过期的生成结果（保留最近N条）
     */
    public void clearOldGenerationResults(int keepCount) {
        List<GenerationResult> list = getGenerationResults();
        if (list.size() > keepCount) {
            List<GenerationResult> keepList = new ArrayList<>(list.subList(0, keepCount));
            saveGenerationResults(keepList);
        }
    }

    // ========== 抽奖中奖记录管理 ==========

    /**
     * 抽奖中奖记录实体
     */
    public static class LotteryWinner {
        public String id;             // 唯一ID
        public String winnerName;     // 中奖者姓名
        public String winnerPhone;    // 中奖者手机号
        public String winnerDepartment; // 中奖者部门
        public String prizeName;      // 奖品名称
        public String lotteryProgram; // 抽奖程序名称
        public long winTime;          // 中奖时间
        public int prizeRound;        // 第几轮抽奖
        public boolean displayed;     // 是否已在内场秀显示

        public LotteryWinner() {
            this.id = "lottery_winner_" + System.currentTimeMillis();
            this.winTime = System.currentTimeMillis();
            this.displayed = false;
        }
    }

    /**
     * 添加抽奖中奖记录
     */
    public void addLotteryWinner(LotteryWinner winner) {
        List<LotteryWinner> list = getLotteryWinners();
        list.add(0, winner);
        saveLotteryWinners(list);
    }

    /**
     * 获取所有抽奖中奖记录
     */
    public List<LotteryWinner> getLotteryWinners() {
        String json = PreferenceUtils.getString(context, KEY_LOTTERY_WINNERS, "[]");
        Type listType = new TypeToken<List<LotteryWinner>>() {}.getType();
        List<LotteryWinner> list = gson.fromJson(json, listType);
        if (list == null) {
            list = new ArrayList<>();
        }
        return list;
    }

    /**
     * 保存抽奖中奖记录列表
     */
    private void saveLotteryWinners(List<LotteryWinner> list) {
        String json = gson.toJson(list);
        PreferenceUtils.putString(context, KEY_LOTTERY_WINNERS, json);
    }

    /**
     * 获取最新中奖者
     */
    public LotteryWinner getLatestWinner() {
        List<LotteryWinner> list = getLotteryWinners();
        if (!list.isEmpty()) {
            return list.get(0);
        }
        return null;
    }

    /**
     * 标记为已显示
     */
    public void markWinnerAsDisplayed(String winnerId) {
        List<LotteryWinner> list = getLotteryWinners();
        for (LotteryWinner winner : list) {
            if (winner.id.equals(winnerId)) {
                winner.displayed = true;
                saveLotteryWinners(list);
                return;
            }
        }
    }

    /**
     * 获取中奖人数
     */
    public int getLotteryWinnerCount() {
        return getLotteryWinners().size();
    }

    /**
     * 清空抽奖中奖记录
     */
    public void clearLotteryWinners() {
        PreferenceUtils.putString(context, KEY_LOTTERY_WINNERS, "[]");
    }

    // ========== 答题中奖记录管理 ==========

    /**
     * 答题中奖记录实体
     */
    public static class QuizWinner {
        public String id;             // 唯一ID
        public String userName;       // 答题者姓名
        public String userPhone;      // 答题者手机号
        public String userId;         // 答题者ID（登录用户）
        public String prizeName;      // 奖品名称
        public String prizeLevel;     // 奖品等级
        public String prizeDescription; // 奖品描述
        public String prizeImageUrl;  // 奖品图片URL
        public int totalQuestions;    // 总题数
        public int correctCount;      // 答对题数
        public long winTime;          // 中奖时间
        public boolean displayed;     // 是否已在内场秀显示

        public QuizWinner() {
            this.id = "quiz_winner_" + System.currentTimeMillis();
            this.winTime = System.currentTimeMillis();
            this.displayed = false;
        }
    }

    /**
     * 添加答题中奖记录
     */
    public void addQuizWinner(QuizWinner winner) {
        List<QuizWinner> list = getQuizWinners();
        list.add(0, winner);
        saveQuizWinners(list);
    }

    /**
     * 获取所有答题中奖记录
     */
    public List<QuizWinner> getQuizWinners() {
        String json = PreferenceUtils.getString(context, KEY_QUIZ_WINNERS, "[]");
        Type listType = new TypeToken<List<QuizWinner>>() {}.getType();
        List<QuizWinner> list = gson.fromJson(json, listType);
        if (list == null) {
            list = new ArrayList<>();
        }
        return list;
    }

    /**
     * 保存答题中奖记录列表
     */
    private void saveQuizWinners(List<QuizWinner> list) {
        String json = gson.toJson(list);
        PreferenceUtils.putString(context, KEY_QUIZ_WINNERS, json);
    }

    /**
     * 获取最新答题中奖者
     */
    public QuizWinner getLatestQuizWinner() {
        List<QuizWinner> list = getQuizWinners();
        if (!list.isEmpty()) {
            return list.get(0);
        }
        return null;
    }

    /**
     * 标记答题中奖者为已显示
     */
    public void markQuizWinnerAsDisplayed(String winnerId) {
        List<QuizWinner> list = getQuizWinners();
        for (QuizWinner winner : list) {
            if (winner.id.equals(winnerId)) {
                winner.displayed = true;
                saveQuizWinners(list);
                return;
            }
        }
    }

    /**
     * 获取答题中奖人数
     */
    public int getQuizWinnerCount() {
        return getQuizWinners().size();
    }

    /**
     * 清空答题中奖记录
     */
    public void clearQuizWinners() {
        PreferenceUtils.putString(context, KEY_QUIZ_WINNERS, "[]");
    }

    /**
     * 获取当前显示的图片ID
     */
    public String getCurrentDisplayImageId() {
        return PreferenceUtils.getString(context, KEY_CURRENT_IMAGE, "");
    }
}
