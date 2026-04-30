package com.jcoding.aiactivity.ui;

import android.Manifest;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.LotteryPrize;
import com.jcoding.aiactivity.entity.LotteryWinner;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.LotteryAudioManager;
import com.jcoding.aiactivity.opengl.CardTextureGenerator;
import com.jcoding.aiactivity.opengl.SphereGLRenderer;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.Random;

/**
 * 3D球体抽奖Activity
 * 使用OpenGL ES渲染3D球体，卡片排列在球体表面
 */
public class Lottery3DActivity extends BaseActivity {

    private static final String TAG = "Lottery3DActivity";
    private static final int REQUEST_WRITE_STORAGE = 300;
    private static final int REQUEST_SETTINGS = 301;

    // OpenGL渲染器
    private SphereGLRenderer glRenderer;
    private android.opengl.GLSurfaceView glSurfaceView;

    // 纹理生成器
    private CardTextureGenerator textureGenerator;

    // UI组件
    private TextView tvTitle;
    private TextView tvCurrentPrize;
    private TextView tvProgress;
    private TextView tvWinnerName;
    private TextView tvPrizeName;
    private Button btnStart;
    private Button btnStop;
    private Button btnCloseResult;
    private LinearLayout llResultContainer;

    // 抽奖数据
    private List<String> participants = new ArrayList<>();
    private List<LotteryPrize> prizes = new ArrayList<>();
    private List<LotteryWinner> winners = new ArrayList<>();
    private int currentPrizeIndex = 0;

    // 抽奖状态
    private boolean isDrawing = false;
    private Handler drawHandler = new Handler(Looper.getMainLooper());
    private Runnable drawRunnable;
    private int currentWinnerIndex = -1;

    // 音频管理器
    private LotteryAudioManager audioManager;

    // 配置管理器
    private ConfigManager configManager;
    private com.jcoding.aiactivity.manager.LotteryConfigManager lotteryConfigManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lottery_3d);

        android.util.Log.d(TAG, "onCreate: Lottery3DActivity启动");
        Toast.makeText(this, "3D球体抽奖正在加载...", Toast.LENGTH_SHORT).show();

        configManager = ConfigManager.getInstance(this);
        lotteryConfigManager = com.jcoding.aiactivity.manager.LotteryConfigManager.getInstance(this);
        audioManager = LotteryAudioManager.getInstance(this);
        textureGenerator = new CardTextureGenerator(this);

        initViews();
        loadLotteryData();  // 加载统一数据
        setupListeners();
        setupGLSurfaceView();  // 初始化OpenGL并更新卡片
        initAudioSettings();

        android.util.Log.d(TAG, "onCreate: 初始化完成，参与者数量=" + participants.size());
    }

    private void initViews() {
        glSurfaceView = findViewById(R.id.gl_surface_view);
        tvTitle = findViewById(R.id.tv_title);
        tvCurrentPrize = findViewById(R.id.tv_current_prize);
        tvProgress = findViewById(R.id.tv_progress);
        tvWinnerName = findViewById(R.id.tv_winner_name);
        tvPrizeName = findViewById(R.id.tv_prize_name);
        btnStart = findViewById(R.id.btn_start_lottery);
        btnStop = findViewById(R.id.btn_stop_lottery);
        btnCloseResult = findViewById(R.id.btn_close_result);
        llResultContainer = findViewById(R.id.ll_result_container);

        // 返回和设置按钮
        findViewById(R.id.btn_back).setOnClickListener(v -> finish());
        findViewById(R.id.btn_settings).setOnClickListener(v -> showSettings());
    }

    private void setupGLSurfaceView() {
        android.util.Log.d(TAG, "setupGLSurfaceView: 开始初始化OpenGL");

        // 检查GLSurfaceView是否正确获取
        if (glSurfaceView == null) {
            android.util.Log.e(TAG, "setupGLSurfaceView: glSurfaceView为null！");
            return;
        }

        android.util.Log.d(TAG, "setupGLSurfaceView: GLSurfaceView可见性=" + glSurfaceView.getVisibility());
        android.util.Log.d(TAG, "setupGLSurfaceView: GLSurfaceView尺寸=" + glSurfaceView.getWidth() + "x" + glSurfaceView.getHeight());

        // 创建OpenGL渲染器
        glRenderer = new SphereGLRenderer(this);
        glSurfaceView.setEGLContextClientVersion(2);
        glSurfaceView.setRenderer(glRenderer);
        glSurfaceView.setRenderMode(android.opengl.GLSurfaceView.RENDERMODE_CONTINUOUSLY);

        // 确保GLSurfaceView可见
        glSurfaceView.setVisibility(View.VISIBLE);

        android.util.Log.d(TAG, "setupGLSurfaceView: OpenGL渲染器已设置，参与者数量=" + participants.size());

        // 设置卡片到球体
        updateSphereCards();

        android.util.Log.d(TAG, "setupGLSurfaceView: 卡片已更新到球体");
    }

    private void setupListeners() {
        // 开始抽奖
        btnStart.setOnClickListener(v -> startLottery());

        // 停止抽奖
        btnStop.setOnClickListener(v -> stopLottery());

        // 关闭结果
        btnCloseResult.setOnClickListener(v -> {
            llResultContainer.setVisibility(View.GONE);
            glRenderer.startRotation(); // 恢复球体旋转
        });
    }

    /**
     * 加载抽奖数据
     * 使用统一的候选人数据源（LotteryConfigManager）
     */
    private void loadLotteryData() {
        android.util.Log.d(TAG, "loadLotteryData: 开始加载统一数据");

        // 从LotteryConfigManager加载候选人数据
        List<com.jcoding.aiactivity.entity.Candidate> candidates =
            lotteryConfigManager.getAvailableCandidates();

        if (candidates != null && !candidates.isEmpty()) {
            // 使用真实的候选人数据
            for (com.jcoding.aiactivity.entity.Candidate candidate : candidates) {
                participants.add(candidate.getName());
            }
            android.util.Log.d(TAG, "loadLotteryData: 已加载 " + participants.size() + " 个真实候选人");
            Toast.makeText(this, "已加载 " + participants.size() + " 位候选人", Toast.LENGTH_SHORT).show();
        } else {
            // 如果没有候选人数据，使用测试数据
            android.util.Log.w(TAG, "loadLotteryData: 没有候选人数据，使用测试数据");
            addTestData();
        }

        // 加载奖品数据（从配置）
        loadPrizesFromConfig();

        // 注意：不在这里调用updateSphereCards()
        // 因为glRenderer还没初始化，会在setupGLSurfaceView()中调用
    }

    /**
     * 添加测试数据（仅在没有候选人数据时使用）
     */
    private void addTestData() {
        android.util.Log.d(TAG, "addTestData: 开始添加测试数据");

        // 添加测试参与者
        String[] testParticipants = {
            "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
            "郑十一", "王十二", "冯十三", "陈十四", "褚十五", "卫十六", "蒋十七", "沈十八",
            "韩十九", "杨二十"
        };

        for (String name : testParticipants) {
            participants.add(name);
        }

        android.util.Log.d(TAG, "addTestData: 已添加 " + participants.size() + " 个测试参与者");
        Toast.makeText(this, "使用测试数据：" + participants.size() + " 人", Toast.LENGTH_SHORT).show();
    }

    /**
     * 从配置加载奖品数据
     */
    private void loadPrizesFromConfig() {
        // 添加默认奖品（后续可以从配置文件加载）
        prizes.add(new LotteryPrize("一等奖", 1, 0xFFD700));
        prizes.add(new LotteryPrize("二等奖", 3, 0xFFC0C0C0));
        prizes.add(new LotteryPrize("三等奖", 5, 0xFFCD7F32));

        updateCurrentPrizeDisplay();
    }

    /**
     * 更新球体上的卡片
     */
    private void updateSphereCards() {
        android.util.Log.d(TAG, "updateSphereCards: 开始更新卡片，glRenderer=" + (glRenderer != null ? "非空" : "空"));

        if (glRenderer == null) {
            android.util.Log.w(TAG, "updateSphereCards: glRenderer为空，无法更新卡片");
            return;
        }

        glRenderer.clearCards();
        android.util.Log.d(TAG, "updateSphereCards: 已清除旧卡片");

        int cardCount = 0;
        for (String name : participants) {
            Bitmap cardBitmap = textureGenerator.generateCard(name);
            glRenderer.addCard(name, cardBitmap);
            cardCount++;
        }

        android.util.Log.d(TAG, "updateSphereCards: 已添加 " + cardCount + " 张卡片到球体");
    }

    /**
     * 更新当前奖品显示
     */
    private void updateCurrentPrizeDisplay() {
        if (currentPrizeIndex >= prizes.size()) {
            tvCurrentPrize.setText("所有奖项已抽完");
            btnStart.setEnabled(false);
            return;
        }

        LotteryPrize prize = prizes.get(currentPrizeIndex);
        int remaining = prize.getTotalCount() - getPrizeWinnerCount(prize);
        tvCurrentPrize.setText(String.format("当前奖项：%s（剩余 %d/%d）",
            prize.getName(), remaining, prize.getTotalCount()));
    }

    /**
     * 获取奖品已中奖人数
     */
    private int getPrizeWinnerCount(LotteryPrize prize) {
        int count = 0;
        for (LotteryWinner winner : winners) {
            if (winner.getPrizeName().equals(prize.getName())) {
                count++;
            }
        }
        return count;
    }

    /**
     * 开始抽奖
     */
    private void startLottery() {
        if (participants.isEmpty()) {
            showToast("没有参与人员");
            return;
        }

        if (currentPrizeIndex >= prizes.size()) {
            showToast("所有奖项已抽完");
            return;
        }

        LotteryPrize prize = prizes.get(currentPrizeIndex);
        if (getPrizeWinnerCount(prize) >= prize.getTotalCount()) {
            showToast("当前奖项已抽完");
            currentPrizeIndex++;
            updateCurrentPrizeDisplay();
            return;
        }

        isDrawing = true;
        btnStart.setEnabled(false);
        btnStop.setEnabled(true);

        // 停止球体旋转
        glRenderer.stopRotation();

        // 播放开始音效
        audioManager.playStartSound();

        // 开始滚动动画
        startDrawingAnimation();

        // 播放滚动音效
        audioManager.playDrawingSound();

        // 启动背景音乐
        audioManager.playBackgroundMusic();
    }

    /**
     * 开始抽奖动画
     */
    private void startDrawingAnimation() {
        tvProgress.setText("正在抽奖...");
        tvProgress.setTextColor(getResources().getColor(R.color.colorAccent));

        final Random random = new Random();

        drawRunnable = new Runnable() {
            @Override
            public void run() {
                if (!isDrawing) return;

                // 随机选择一个中奖者
                currentWinnerIndex = random.nextInt(participants.size());
                String currentName = participants.get(currentWinnerIndex);
                tvProgress.setText("正在抽奖... 当前：" + currentName);

                // 每100ms更新一次
                drawHandler.postDelayed(this, 100);
            }
        };

        drawHandler.post(drawRunnable);
    }

    /**
     * 停止抽奖
     */
    private void stopLottery() {
        if (!isDrawing) return;

        isDrawing = false;
        drawHandler.removeCallbacks(drawRunnable);

        // 停止滚动音效
        audioManager.stopDrawingSound();

        // 确定中奖者
        if (currentWinnerIndex >= 0 && currentWinnerIndex < participants.size()) {
            String winnerName = participants.get(currentWinnerIndex);
            LotteryPrize prize = prizes.get(currentPrizeIndex);

            // 记录中奖信息
            LotteryWinner winner = new LotteryWinner(winnerName, prize.getName(), new Date());
            winners.add(winner);

            // 从参与者中移除中奖者（一人只能中一次）
            participants.remove(currentWinnerIndex);

            // 显示中奖结果
            showResult(winnerName, prize.getName());

            // 更新球体
            updateSphereCards();

            // 检查当前奖品是否抽完
            if (getPrizeWinnerCount(prize) >= prize.getTotalCount()) {
                currentPrizeIndex++;
                updateCurrentPrizeDisplay();
            }

            // 播放中奖音效
            audioManager.playWinnerSound();

            // 导出结果
            exportResult(winner);
        }

        btnStart.setEnabled(true);
        btnStop.setEnabled(false);
    }

    /**
     * 显示中奖结果
     */
    private void showResult(String winnerName, String prizeName) {
        tvWinnerName.setText(winnerName);
        tvPrizeName.setText(prizeName);
        llResultContainer.setVisibility(View.VISIBLE);
    }

    /**
     * 初始化音频设置
     */
    private void initAudioSettings() {
        // 从SharedPreferences加载音频设置，或使用默认值
        boolean bgMusicEnabled = getSharedPreferences("lottery_3d", MODE_PRIVATE)
                .getBoolean("bg_music_enabled", false);
        boolean soundEffectsEnabled = getSharedPreferences("lottery_3d", MODE_PRIVATE)
                .getBoolean("sound_effects_enabled", true);
        float volume = getSharedPreferences("lottery_3d", MODE_PRIVATE)
                .getFloat("volume", 0.7f);

        audioManager.setConfig(bgMusicEnabled, soundEffectsEnabled, volume);
    }

    /**
     * 导出中奖结果
     */
    private void exportResult(LotteryWinner winner) {
        // 检查存储权限
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                    REQUEST_WRITE_STORAGE);
            return;
        }

        try {
            // 创建导出目录
            File exportDir = new File(Environment.getExternalStorageDirectory(), "LotteryResults");
            if (!exportDir.exists()) {
                exportDir.mkdirs();
            }

            // 创建导出文件
            String timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
            File exportFile = new File(exportDir, "lottery_result_" + timestamp + ".txt");

            // 写入中奖信息
            FileOutputStream fos = new FileOutputStream(exportFile, true);
            String content = String.format("[%s] %s - %s%n",
                    new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(winner.getTime()),
                    winner.getName(),
                    winner.getPrizeName());
            fos.write(content.getBytes("UTF-8"));
            fos.close();

            showToast("结果已导出到: " + exportFile.getAbsolutePath());

        } catch (IOException e) {
            showToast("导出失败: " + e.getMessage());
        }
    }

    /**
     * 显示设置对话框
     */
    private void showSettings() {
        Intent intent = new Intent(this, Lottery3DSettingsActivity.class);
        // Pass current settings
        intent.putStringArrayListExtra("participants", new ArrayList<>(participants));
        intent.putExtra("prizes", (java.io.Serializable) new ArrayList<>(prizes));
        startActivityForResult(intent, REQUEST_SETTINGS);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_WRITE_STORAGE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                showToast("存储权限已授予");
            } else {
                showToast("需要存储权限才能导出结果");
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_SETTINGS && resultCode == RESULT_OK && data != null) {
            // Update participants
            ArrayList<String> newParticipants = data.getStringArrayListExtra("participants");
            if (newParticipants != null) {
                participants.clear();
                participants.addAll(newParticipants);
                updateSphereCards();
            }

            // Update prizes
            try {
                ArrayList<LotteryPrize> newPrizes = (ArrayList<LotteryPrize>) data.getSerializableExtra("prizes");
                if (newPrizes != null) {
                    prizes.clear();
                    prizes.addAll(newPrizes);
                    currentPrizeIndex = 0;
                    updateCurrentPrizeDisplay();
                }
            } catch (Exception e) {
                e.printStackTrace();
            }

            // Reload audio settings
            initAudioSettings();

            showToast("设置已更新");
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (glSurfaceView != null) {
            glSurfaceView.onPause();
        }
        // 暂停背景音乐
        audioManager.pauseBackgroundMusic();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (glSurfaceView != null) {
            glSurfaceView.onResume();
        }
        // 恢复背景音乐
        audioManager.resumeBackgroundMusic();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // 释放音频资源
        audioManager.release();

        if (glRenderer != null) {
            glRenderer.clearCards();
        }

        drawHandler.removeCallbacks(drawRunnable);
    }
}
