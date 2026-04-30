package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.Candidate;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.DigitalHumanManager;
import com.jcoding.aiactivity.manager.LotteryConfigManager;
import com.jcoding.aiactivity.utils.NetworkUtils;
import com.jcoding.aiactivity.view.FireworksView;
import com.jcoding.aiactivity.view.GiftBoxView;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * 礼花抽奖Activity
 *
 * 功能说明：
 * 1. 点击"开始抽奖"，触发礼花散开动画
 * 2. 礼花停止后，从礼物盒中弹出奖品
 * 3. 显示奖品名称和商家信息
 * 4. 支持完全离线运行
 */
public class FireworksLotteryActivity extends BaseActivity {

    private static final String TAG = "FireworksLotteryActivity";

    // 视图组件
    private TextView tvProgramName;
    private TextView tvRemainingCount;
    private TextView tvReadyText;
    private TextView tvOfflineMode;
    private TextView tvTestModeIndicator;
    private Button btnStartCenter;
    private Button btnReset;
    private Button btnBack;
    private Button btnToggleTestMode;
    private Button btnCancelTest;
    private FireworksView fireworksView;
    private GiftBoxView giftBoxView;

    // 数字人相关
    private com.jcoding.aiactivity.widget.DigitalHumanView digitalHumanView;
    private DigitalHumanManager digitalHumanManager;

    // 数据
    private List<Candidate> candidateList;
    private Candidate currentWinner;
    private Random random;

    // 配置管理器
    private ConfigManager configManager;
    private LotteryConfigManager lotteryManager;

    // 动画状态
    private boolean isAnimating = false;

    // 试抽模式
    private boolean isTestMode = false;
    private Candidate lastTestWinner;  // 上次试抽的中奖者，用于作废时恢复

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fireworks_lottery);

        // 初始化
        configManager = ConfigManager.getInstance(this);
        lotteryManager = LotteryConfigManager.getInstance(this);
        random = new Random();
        candidateList = new ArrayList<>();

        // 初始化视图
        initViews();

        // 初始化数字人
        initDigitalHuman();

        // 加载候选人数据
        loadCandidates();

        // 更新剩余数量显示
        updateRemainingCount();

        // 加载背景图片
        loadBackgroundImage();
    }

    /**
     * 加载背景图片
     */
    private void loadBackgroundImage() {
        try {
            android.graphics.Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(
                    getAssets().open("image/question_bk.png"));
            android.graphics.drawable.BitmapDrawable drawable = new android.graphics.drawable.BitmapDrawable(
                    getResources(), bitmap);

            // 设置到背景ImageView
            android.widget.ImageView ivBackground = findViewById(R.id.iv_background);
            if (ivBackground != null) {
                ivBackground.setImageDrawable(drawable);
            }
        } catch (java.io.IOException e) {
            Log.e(TAG, "Failed to load background image", e);
            // 背景图片加载失败，使用默认背景
        }
    }

    private void initViews() {
        tvProgramName = findViewById(R.id.tv_program_name);
        tvRemainingCount = findViewById(R.id.tv_remaining_count);
        tvReadyText = findViewById(R.id.tv_ready_text);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);
        tvTestModeIndicator = findViewById(R.id.tv_test_mode_indicator);
        btnStartCenter = findViewById(R.id.btn_start_center);
        btnReset = findViewById(R.id.btn_reset);
        btnBack = findViewById(R.id.btn_back);
        btnToggleTestMode = findViewById(R.id.btn_toggle_test_mode);
        btnCancelTest = findViewById(R.id.btn_cancel_test);
        fireworksView = findViewById(R.id.fireworks_view);
        giftBoxView = findViewById(R.id.gift_box_view);

        // 设置程序名称
        tvProgramName.setText("礼花抽奖");

        // 中央开始抽奖按钮
        btnStartCenter.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startLottery();
            }
        });

        // 重置抽奖按钮
        btnReset.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resetLottery();
            }
        });

        // 返回按钮
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        // 试抽模式切换按钮
        btnToggleTestMode.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleTestMode();
            }
        });

        // 作废按钮
        btnCancelTest.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                cancelTestDraw();
            }
        });

        // 礼花动画结束监听
        fireworksView.setOnFireworksEndListener(new FireworksView.OnFireworksEndListener() {
            @Override
            public void onFireworksEnd() {
                // 礼花动画结束，显示奖品
                showPrize();
            }
        });

        // 礼物盒动画完成监听
        giftBoxView.setOnGiftBoxAnimationListener(new GiftBoxView.OnGiftBoxAnimationListener() {
            @Override
            public void onAnimationComplete() {
                // 动画完成，恢复按钮状态
                isAnimating = false;
                btnStartCenter.setEnabled(true);
                btnReset.setEnabled(true);
            }
        });
    }

    /**
     * 初始化数字人
     */
    private void initDigitalHuman() {
        digitalHumanView = findViewById(R.id.digital_human_view);

        // 强制启用数字人
        digitalHumanManager = DigitalHumanManager.getInstance(this);
        digitalHumanView.setVisibility(View.VISIBLE);

        // 加载默认数字人
        String digitalHumanId = "JC2026012100001"; // 默认数字人ID
        digitalHumanView.loadDigitalHuman(digitalHumanId);

        // 欢迎动作
        digitalHumanManager.welcome(new DigitalHumanManager.DigitalHumanCallback() {
            @Override
            public void onSpeakStart(String gifPath) {
                // DigitalHumanView 会自动处理
                if (digitalHumanView != null) {
                    digitalHumanView.startTalking();
                }
            }

            @Override
            public void onComplete() {
                // 完成后自动切换回闭嘴状态
                if (digitalHumanView != null) {
                    digitalHumanView.stopTalking();
                }
            }

            @Override
            public void onError(String error) {
                Log.e(TAG, "Digital human error: " + error);
            }
        });
    }

    /**
     * 加载候选人数据
     * 从 LotteryConfigManager 获取候选人列表
     */
    private void loadCandidates() {
        try {
            // 从 LotteryConfigManager 获取可用候选人
            candidateList = lotteryManager.getAvailableCandidates();

            if (candidateList.isEmpty()) {
                Log.w(TAG, "没有可用候选人，所有候选人都已中奖");
                Toast.makeText(this, "所有候选人都已中奖，请重置抽奖", Toast.LENGTH_LONG).show();
            } else {
                Log.i(TAG, "成功加载 " + candidateList.size() + " 个候选人");
            }
        } catch (Exception e) {
            Log.e(TAG, "加载候选人数据失败", e);
            Toast.makeText(this, "加载候选人数据失败: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    /**
     * 更新剩余数量显示
     */
    private void updateRemainingCount() {
        int availableCount = lotteryManager.getAvailableCandidates().size();
        int totalCount = lotteryManager.getAllCandidates().size();
        tvRemainingCount.setText(String.format("剩余候选人：%d/%d", availableCount, totalCount));
    }

    /**
     * 开始抽奖
     */
    private void startLottery() {
        if (isAnimating) {
            return;
        }

        // 重新加载候选人列表
        loadCandidates();

        if (candidateList.isEmpty()) {
            Toast.makeText(this, "所有候选人都已中奖，请重置抽奖", Toast.LENGTH_SHORT).show();
            return;
        }

        // 随机选择一个中奖者
        currentWinner = candidateList.get(random.nextInt(candidateList.size()));

        // 开始动画
        isAnimating = true;
        btnStartCenter.setEnabled(false);
        btnStartCenter.setVisibility(View.GONE);
        btnReset.setEnabled(false);
        btnCancelTest.setVisibility(View.GONE); // 开始新抽奖时隐藏作废按钮

        // 隐藏准备文字
        tvReadyText.setVisibility(View.GONE);

        // 重置视图状态
        giftBoxView.reset();

        // 开始礼花动画
        fireworksView.startFireworks();

        Log.i(TAG, "开始抽奖，选中中奖者: " + currentWinner.getName());
    }

    /**
     * 显示中奖者（礼花动画结束后调用）
     */
    private void showPrize() {
        if (currentWinner == null) {
            isAnimating = false;
            btnStartCenter.setEnabled(true);
            btnStartCenter.setVisibility(View.VISIBLE);
            btnReset.setEnabled(true);
            tvReadyText.setVisibility(View.VISIBLE);
            return;
        }

        // 停止礼花动画
        fireworksView.stopFireworks();

        // 记录中奖者
        lotteryManager.addWinnerRecord(currentWinner, null);

        // 试抽模式：记录试抽结果
        if (isTestMode) {
            lastTestWinner = currentWinner;
            // 显示作废按钮
            btnCancelTest.setVisibility(View.VISIBLE);
            Toast.makeText(this, "试抽结果：" + currentWinner.getName() + "\n可点击作废按钮重新填入奖池", Toast.LENGTH_LONG).show();
        } else {
            // 正式抽奖：自动保存到文件
            boolean exportSuccess = lotteryManager.exportAllRecords();
            if (exportSuccess) {
                Log.i(TAG, "抽奖记录已自动保存到文件");
            }
        }

        // 更新剩余数量
        updateRemainingCount();

        // 显示礼物盒动画（显示中奖者）
        giftBoxView.setWinnerAndAnimate(currentWinner);

        // 检查是否还有可用候选人，如果有则显示中央按钮
        if (lotteryManager.getAvailableCandidates().size() > 0) {
            btnStartCenter.setEnabled(true);
            btnStartCenter.setVisibility(View.VISIBLE);
        }
        btnReset.setEnabled(true);

        // 数字人祝贺（检查lottery模块是否启用数字人）
        if (digitalHumanManager != null && digitalHumanManager.isEnabledForModule("lottery")) {
            // 构建祝贺消息（包含中奖者姓名和部门）
            String message = "恭喜你中奖了！" + currentWinner.getName();
            if (currentWinner.getDepartment() != null && !currentWinner.getDepartment().isEmpty()) {
                message += "，" + currentWinner.getDepartment();
            }

            digitalHumanManager.congratulate(
                message,
                new DigitalHumanManager.DigitalHumanCallback() {
                    @Override
                    public void onSpeakStart(String gifPath) {
                        // DigitalHumanView 会自动处理说话动画
                        if (digitalHumanView != null) {
                            digitalHumanView.startTalking();
                        }
                    }

                    @Override
                    public void onComplete() {
                        // 完成后自动切换回闭嘴状态
                        if (digitalHumanView != null) {
                            digitalHumanView.stopTalking();
                        }
                    }

                    @Override
                    public void onError(String error) {
                        Log.e(TAG, "Digital human congratulate error: " + error);
                    }
                }
            );
        }

        // 离线提示
        if (!NetworkUtils.isOnline(this)) {
            Toast.makeText(this, "恭喜 " + currentWinner.getName() + " 中奖！（离线模式）", Toast.LENGTH_SHORT).show();
        }

        Log.i(TAG, "中奖: " + currentWinner.getName() + " - " + currentWinner.getDepartment());
    }

    /**
     * 重置抽奖
     */
    private void resetLottery() {
        new android.app.AlertDialog.Builder(this)
                .setTitle("重置抽奖")
                .setMessage("确定要清空中奖记录并重新开始抽奖吗？")
                .setPositiveButton("确定", (dialog, which) -> {
                    // 重置抽奖数据
                    lotteryManager.resetLottery();

                    // 重新加载候选人数据
                    loadCandidates();
                    updateRemainingCount();

                    // 重置视图状态
                    fireworksView.stopFireworks();
                    giftBoxView.reset();
                    tvReadyText.setVisibility(View.GONE);

                    // 显示中央按钮
                    btnStartCenter.setEnabled(true);
                    btnStartCenter.setVisibility(View.VISIBLE);

                    // 隐藏作废按钮
                    btnCancelTest.setVisibility(View.GONE);

                    // 清空试抽记录
                    lastTestWinner = null;

                    Toast.makeText(this, "抽奖已重置", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("取消", null)
                .show();
    }

    /**
     * 切换试抽模式
     */
    private void toggleTestMode() {
        isTestMode = !isTestMode;

        if (isTestMode) {
            // 开启试抽模式
            btnToggleTestMode.setText("🔴 关闭试抽模式");
            tvTestModeIndicator.setVisibility(View.VISIBLE);
            Toast.makeText(this, "试抽模式已开启，抽中的结果可作废", Toast.LENGTH_SHORT).show();
            Log.i(TAG, "试抽模式已开启");
        } else {
            // 关闭试抽模式
            btnToggleTestMode.setText("🧪 开启试抽模式");
            tvTestModeIndicator.setVisibility(View.GONE);
            btnCancelTest.setVisibility(View.GONE);
            Toast.makeText(this, "试抽模式已关闭", Toast.LENGTH_SHORT).show();
            Log.i(TAG, "试抽模式已关闭");
        }
    }

    /**
     * 作废试抽结果
     * 将候选人重新填回奖池，并移除中奖记录
     */
    private void cancelTestDraw() {
        if (lastTestWinner == null) {
            Toast.makeText(this, "没有可作废的试抽结果", Toast.LENGTH_SHORT).show();
            return;
        }

        new android.app.AlertDialog.Builder(this)
                .setTitle("作废试抽结果")
                .setMessage("确定要作废试抽结果吗？\n中奖者：" + lastTestWinner.getName() + "\n\n作废后将重新填入奖池。")
                .setPositiveButton("确定", (dialog, which) -> {
                    // 恢复候选人到奖池
                    boolean restored = lotteryManager.restoreCandidate(lastTestWinner);

                    if (restored) {
                        // 移除中奖记录
                        lotteryManager.removeLastWinnerRecord();

                        // 更新显示
                        updateRemainingCount();

                        // 重置视图
                        giftBoxView.reset();
                        tvReadyText.setVisibility(View.GONE);

                        // 显示中央按钮
                        btnStartCenter.setEnabled(true);
                        btnStartCenter.setVisibility(View.VISIBLE);

                        // 隐藏作废按钮
                        btnCancelTest.setVisibility(View.GONE);

                        // 清空上次试抽记录
                        lastTestWinner = null;

                        Toast.makeText(this, "已作废，候选人已重新填入奖池", Toast.LENGTH_SHORT).show();
                        Log.i(TAG, "试抽结果已作废: " + lastTestWinner.getName());
                    } else {
                        Toast.makeText(this, "作废失败：候选人已在奖池中", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("取消", null)
                .show();
    }

    @Override
    protected void showOfflineNotice() {
        if (tvOfflineMode != null) {
            tvOfflineMode.setVisibility(View.VISIBLE);
        }
    }

    @Override
    protected void hideOfflineNotice() {
        if (tvOfflineMode != null) {
            tvOfflineMode.setVisibility(View.GONE);
        }
    }

}
