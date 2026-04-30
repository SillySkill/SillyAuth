package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.content.SharedPreferences;
import android.text.TextUtils;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.reflect.TypeToken;
import com.jcoding.aiactivity.entity.Candidate;
import com.jcoding.aiactivity.utils.PreferenceUtils;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * 抽奖配置管理器
 * 负责加载候选人配置和抽奖程序配置
 */
public class LotteryConfigManager {

    private static final String CANDIDATES_FILE = "lottery/candidates.json";
    private static final String PREF_WINNERS = "lottery_winners";
    private static final String PREF_CURRENT_WINNER_COUNT = "current_winner_count";

    // 文件存储路径
    private static final String WINNERS_FILE = "lottery/records/winners.json";
    private static final String REMAINING_CANDIDATES_FILE = "lottery/records/remaining_candidates.json";
    private static final String RECORDS_DIR = "lottery/records";

    private static LotteryConfigManager instance;
    private Context context;
    private Gson gson;
    private List<Candidate> allCandidates;
    private List<Candidate> availableCandidates;
    private List<WinnerRecord> winnerRecords;

    private LotteryConfigManager(Context context) {
        this.context = context.getApplicationContext();
        this.gson = new Gson();
        this.allCandidates = new ArrayList<>();
        this.availableCandidates = new ArrayList<>();
        this.winnerRecords = new ArrayList<>();
        loadConfig();
    }

    public static synchronized LotteryConfigManager getInstance(Context context) {
        if (instance == null) {
            instance = new LotteryConfigManager(context);
        }
        return instance;
    }

    /**
     * 加载配置
     */
    private void loadConfig() {
        loadCandidatesFromFile();
        loadWinnerRecords();
    }

    /**
     * 从文件加载候选人（强制从prizeDate.json）
     */
    private void loadCandidatesFromFile() {
        android.util.Log.i("LotteryConfigManager", "强制从prizeDate.json加载候选人数据...");

        try {
            // 使用PrizeDateJsonParser解析prizeDate.json文件
            List<Candidate> prizeDateCandidates = com.jcoding.aiactivity.utils.PrizeDateJsonParser.parse(context);

            if (prizeDateCandidates != null && !prizeDateCandidates.isEmpty()) {
                allCandidates.clear();
                allCandidates.addAll(prizeDateCandidates);

                availableCandidates.clear();
                availableCandidates.addAll(prizeDateCandidates);

                Collections.shuffle(availableCandidates);
                android.util.Log.i("LotteryConfigManager", "成功从prizeDate.json加载 " + prizeDateCandidates.size() + " 个候选人");

                // 打印摘要
                String summary = com.jcoding.aiactivity.utils.PrizeDateJsonParser.getSummary(context);
                android.util.Log.i("LotteryConfigManager", "数据摘要:\n" + summary);
                return;
            }

        } catch (Exception e) {
            android.util.Log.e("LotteryConfigManager", "从prizeDate.json加载失败: " + e.getMessage(), e);
        }

        // prizeDate.json加载失败，降级到candidates.json
        android.util.Log.w("LotteryConfigManager", "prizeDate.json加载失败，降级到candidates.json...");
        try {
            String configStr = readAssetFile(CANDIDATES_FILE);
            if (!TextUtils.isEmpty(configStr)) {
                JsonObject jsonObject = gson.fromJson(configStr, JsonObject.class);
                if (jsonObject != null && jsonObject.has("candidates")) {
                    JsonArray candidatesArray = jsonObject.getAsJsonArray("candidates");
                    Type listType = new TypeToken<List<Candidate>>() {}.getType();
                    List<Candidate> candidatesJson = gson.fromJson(candidatesArray, listType);

                    allCandidates.clear();
                    allCandidates.addAll(candidatesJson);

                    availableCandidates.clear();
                    availableCandidates.addAll(candidatesJson);

                    Collections.shuffle(availableCandidates);
                    android.util.Log.i("LotteryConfigManager", "成功从candidates.json加载 " + candidatesJson.size() + " 个候选人");
                    return;
                }
            }

        } catch (Exception e) {
            android.util.Log.e("LotteryConfigManager", "从candidates.json加载也失败", e);
        }

        // 如果都失败，使用默认数据
        android.util.Log.w("LotteryConfigManager", "所有加载方式失败，使用默认候选人数据");
        loadDefaultCandidates();
    }

    /**
     * 加载默认候选人（备用数据）
     */
    private void loadDefaultCandidates() {
        allCandidates.clear();
        for (int i = 1; i <= 50; i++) {
            Candidate candidate = new Candidate();
            candidate.setId("c" + String.format("%03d", i));
            candidate.setName("参与者" + i);
            candidate.setPhone("138****" + String.format("%04d", i));
            candidate.setDepartment("部门" + (i % 5 + 1));
            allCandidates.add(candidate);
        }

        availableCandidates.clear();
        availableCandidates.addAll(allCandidates);
        Collections.shuffle(availableCandidates);
    }

    /**
     * 加载中奖记录
     */
    private void loadWinnerRecords() {
        String recordsJson = PreferenceUtils.getString(context, PREF_WINNERS, "");
        if (!TextUtils.isEmpty(recordsJson)) {
            Type listType = new TypeToken<List<WinnerRecord>>() {}.getType();
            winnerRecords = gson.fromJson(recordsJson, listType);
        }
    }

    /**
     * 保存中奖记录
     */
    private void saveWinnerRecords() {
        String recordsJson = gson.toJson(winnerRecords);
        PreferenceUtils.putString(context, PREF_WINNERS, recordsJson);
    }

    /**
     * 获取所有候选人
     */
    public List<Candidate> getAllCandidates() {
        return new ArrayList<>(allCandidates);
    }

    /**
     * 获取可用候选人（未中奖的）
     */
    public List<Candidate> getAvailableCandidates() {
        return new ArrayList<>(availableCandidates);
    }

    /**
     * 抽取中奖者
     */
    public Candidate drawWinner() {
        if (availableCandidates.isEmpty()) {
            return null;
        }

        int index = (int) (Math.random() * availableCandidates.size());
        Candidate winner = availableCandidates.get(index);

        // 从可用列表中移除
        availableCandidates.remove(index);

        // 记录中奖信息
        WinnerRecord record = new WinnerRecord();
        record.setCandidateId(winner.getId());
        record.setCandidateName(winner.getName());
        record.setDrawTime(System.currentTimeMillis());
        winnerRecords.add(record);

        saveWinnerRecords();

        return winner;
    }

    /**
     * 添加中奖记录
     */
    public void addWinnerRecord(Candidate winner, String prizeName) {
        WinnerRecord record = new WinnerRecord();
        record.setCandidateId(winner.getId());
        record.setCandidateName(winner.getName());
        record.setPrizeName(prizeName);
        record.setDrawTime(System.currentTimeMillis());
        winnerRecords.add(record);

        saveWinnerRecords();
    }

    /**
     * 获取中奖记录列表
     */
    public List<WinnerRecord> getWinnerRecords() {
        return new ArrayList<>(winnerRecords);
    }

    /**
     * 清空中奖记录
     */
    public void clearWinnerRecords() {
        winnerRecords.clear();
        PreferenceUtils.putString(context, PREF_WINNERS, "");

        // 重置可用候选人
        availableCandidates.clear();
        availableCandidates.addAll(allCandidates);
        Collections.shuffle(availableCandidates);
    }

    /**
     * 获取中奖人数
     */
    public int getWinnerCount() {
        return winnerRecords.size();
    }

    /**
     * 重置抽奖（清空记录，重新开始）
     */
    public void resetLottery() {
        clearWinnerRecords();
    }

    /**
     * 回退奖池（移除最后一条中奖记录）
     * @return 如果成功移除返回true，否则返回false
     */
    public boolean returnToPool() {
        if (winnerRecords.isEmpty()) {
            return false;
        }

        // 移除最后一条记录
        WinnerRecord lastRecord = winnerRecords.remove(winnerRecords.size() - 1);

        // 将候选人重新添加回可用列表
        if (lastRecord.getCandidateId() != null) {
            for (Candidate candidate : allCandidates) {
                if (candidate.getId().equals(lastRecord.getCandidateId())) {
                    // 检查是否已经在可用列表中
                    boolean alreadyAvailable = false;
                    for (Candidate c : availableCandidates) {
                        if (c.getId().equals(candidate.getId())) {
                            alreadyAvailable = true;
                            break;
                        }
                    }

                    // 如果不在可用列表中，则添加回去
                    if (!alreadyAvailable) {
                        availableCandidates.add(candidate);
                        Collections.shuffle(availableCandidates);
                    }
                    break;
                }
            }
        }

        // 保存到SharedPreferences
        saveWinnerRecords();

        return true;
    }

    /**
     * 读取assets文件
     */
    private String readAssetFile(String filePath) {
        try {
            InputStream is = context.getAssets().open(filePath);
            int size = is.available();
            byte[] buffer = new byte[size];
            is.read(buffer);
            is.close();
            return new String(buffer, StandardCharsets.UTF_8);
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 中奖记录实体
     */
    public static class WinnerRecord {
        private String candidateId;
        private String candidateName;
        private String prizeName;
        private long drawTime;

        public String getCandidateId() {
            return candidateId;
        }

        public void setCandidateId(String candidateId) {
            this.candidateId = candidateId;
        }

        public String getCandidateName() {
            return candidateName;
        }

        public void setCandidateName(String candidateName) {
            this.candidateName = candidateName;
        }

        public String getPrizeName() {
            return prizeName;
        }

        public void setPrizeName(String prizeName) {
            this.prizeName = prizeName;
        }

        public long getDrawTime() {
            return drawTime;
        }

        public void setDrawTime(long drawTime) {
            this.drawTime = drawTime;
        }
    }

    // ==================== 文件存储功能 ====================

    /**
     * 导出中奖记录到文件
     * @return 是否成功
     */
    public boolean exportWinnersToFile() {
        try {
            // 创建records目录
            File recordsDir = new File(context.getFilesDir(), RECORDS_DIR);
            if (!recordsDir.exists()) {
                recordsDir.mkdirs();
            }

            File winnersFile = new File(recordsDir, "winners.json");

            // 构建JSON对象
            com.google.gson.JsonObject root = new com.google.gson.JsonObject();
            com.google.gson.JsonArray winnersArray = new com.google.gson.JsonArray();

            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());

            for (WinnerRecord record : winnerRecords) {
                com.google.gson.JsonObject recordObj = new com.google.gson.JsonObject();
                recordObj.addProperty("candidate_id", record.getCandidateId());
                recordObj.addProperty("candidate_name", record.getCandidateName());
                if (record.getPrizeName() != null) {
                    recordObj.addProperty("prize_name", record.getPrizeName());
                }

                // 格式化时间
                String timeStr = sdf.format(new Date(record.getDrawTime()));
                recordObj.addProperty("winner_time", timeStr);

                winnersArray.add(recordObj);
            }

            root.add("winners", winnersArray);
            root.addProperty("last_updated", sdf.format(new Date()));
            root.addProperty("version", "1.0");

            // 写入文件
            String jsonStr = gson.toJson(root);
            FileOutputStream fos = new FileOutputStream(winnersFile);
            fos.write(jsonStr.getBytes(StandardCharsets.UTF_8));
            fos.close();

            android.util.Log.i("LotteryConfigManager", "中奖记录已导出到文件: " + winnersFile.getAbsolutePath());
            return true;

        } catch (Exception e) {
            android.util.Log.e("LotteryConfigManager", "导出中奖记录失败", e);
            return false;
        }
    }

    /**
     * 导出剩余候选人到文件
     * @return 是否成功
     */
    public boolean exportRemainingCandidatesToFile() {
        try {
            // 创建records目录
            File recordsDir = new File(context.getFilesDir(), RECORDS_DIR);
            if (!recordsDir.exists()) {
                recordsDir.mkdirs();
            }

            File remainingFile = new File(recordsDir, "remaining_candidates.json");

            // 构建JSON对象
            com.google.gson.JsonObject root = new com.google.gson.JsonObject();
            com.google.gson.JsonArray idsArray = new com.google.gson.JsonArray();

            for (Candidate candidate : availableCandidates) {
                idsArray.add(candidate.getId());
            }

            root.add("remaining_candidate_ids", idsArray);
            root.addProperty("total_count", availableCandidates.size());

            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
            root.addProperty("last_updated", sdf.format(new Date()));
            root.addProperty("auto_reset", false);

            // 写入文件
            String jsonStr = gson.toJson(root);
            FileOutputStream fos = new FileOutputStream(remainingFile);
            fos.write(jsonStr.getBytes(StandardCharsets.UTF_8));
            fos.close();

            android.util.Log.i("LotteryConfigManager", "剩余候选人已导出到文件: " + remainingFile.getAbsolutePath());
            return true;

        } catch (Exception e) {
            android.util.Log.e("LotteryConfigManager", "导出剩余候选人失败", e);
            return false;
        }
    }

    /**
     * 从文件导入中奖记录
     * @param filePath 文件路径
     * @return 是否成功
     */
    public boolean importWinnersFromFile(String filePath) {
        try {
            File file = new File(filePath);
            if (!file.exists()) {
                android.util.Log.e("LotteryConfigManager", "文件不存在: " + filePath);
                return false;
            }

            // 读取文件
            java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.FileReader(file));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            reader.close();

            // 解析JSON
            com.google.gson.JsonObject root = gson.fromJson(sb.toString(), com.google.gson.JsonObject.class);
            com.google.gson.JsonArray winnersArray = root.getAsJsonArray("winners");

            winnerRecords.clear();
            for (int i = 0; i < winnersArray.size(); i++) {
                com.google.gson.JsonObject recordObj = winnersArray.get(i).getAsJsonObject();
                WinnerRecord record = new WinnerRecord();
                record.setCandidateId(recordObj.get("candidate_id").getAsString());
                record.setCandidateName(recordObj.get("candidate_name").getAsString());

                if (recordObj.has("prize_name") && !recordObj.get("prize_name").isJsonNull()) {
                    record.setPrizeName(recordObj.get("prize_name").getAsString());
                }

                if (recordObj.has("winner_time")) {
                    String timeStr = recordObj.get("winner_time").getAsString();
                    SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                    try {
                        Date date = sdf.parse(timeStr);
                        record.setDrawTime(date.getTime());
                    } catch (Exception e) {
                        record.setDrawTime(System.currentTimeMillis());
                    }
                }

                winnerRecords.add(record);
            }

            android.util.Log.i("LotteryConfigManager", "成功导入 " + winnerRecords.size() + " 条中奖记录");
            return true;

        } catch (Exception e) {
            android.util.Log.e("LotteryConfigManager", "导入中奖记录失败", e);
            return false;
        }
    }

    /**
     * 获取记录存储目录路径
     * @return 目录路径
     */
    public String getRecordsDirectoryPath() {
        File recordsDir = new File(context.getFilesDir(), RECORDS_DIR);
        if (!recordsDir.exists()) {
            recordsDir.mkdirs();
        }
        return recordsDir.getAbsolutePath();
    }

    /**
     * 自动导出所有记录
     * @return 是否成功
     */
    public boolean exportAllRecords() {
        boolean winnersSuccess = exportWinnersToFile();
        boolean candidatesSuccess = exportRemainingCandidatesToFile();

        android.util.Log.i("LotteryConfigManager", "导出结果 - 中奖记录: " + winnersSuccess + ", 剩余候选人: " + candidatesSuccess);
        return winnersSuccess && candidatesSuccess;
    }

    // ==================== 试抽功能 ====================

    /**
     * 恢复候选人到奖池
     * 用于试抽作废后，将候选人重新添加到可用列表
     * @param candidate 要恢复的候选人
     * @return 是否成功
     */
    public boolean restoreCandidate(Candidate candidate) {
        if (candidate == null) {
            return false;
        }

        // 检查候选人是否已经在可用列表中
        for (Candidate c : availableCandidates) {
            if (c.getId().equals(candidate.getId())) {
                android.util.Log.w("LotteryConfigManager", "候选人已在可用列表中: " + candidate.getName());
                return false;
            }
        }

        // 添加到可用列表
        availableCandidates.add(candidate);
        Collections.shuffle(availableCandidates);

        android.util.Log.i("LotteryConfigManager", "候选人已恢复到奖池: " + candidate.getName());
        return true;
    }

    /**
     * 移除最后一条中奖记录
     * 用于试抽作废后，删除临时中奖记录
     * @return 被移除的记录，如果没有则返回null
     */
    public WinnerRecord removeLastWinnerRecord() {
        if (winnerRecords.isEmpty()) {
            return null;
        }

        WinnerRecord lastRecord = winnerRecords.remove(winnerRecords.size() - 1);
        android.util.Log.i("LotteryConfigManager", "已移除最后一条中奖记录: " + lastRecord.getCandidateName());
        return lastRecord;
    }

    /**
     * 通过ID查找候选人
     * @param candidateId 候选人ID
     * @return 候选人对象，未找到返回null
     */
    public Candidate findCandidateById(String candidateId) {
        for (Candidate candidate : allCandidates) {
            if (candidate.getId().equals(candidateId)) {
                return candidate;
            }
        }
        return null;
    }

    /**
     * 判断候选人是否可用
     * @param candidateId 候选人ID
     * @return 是否可用
     */
    public boolean isCandidateAvailable(String candidateId) {
        for (Candidate candidate : availableCandidates) {
            if (candidate.getId().equals(candidateId)) {
                return true;
            }
        }
        return false;
    }
}
