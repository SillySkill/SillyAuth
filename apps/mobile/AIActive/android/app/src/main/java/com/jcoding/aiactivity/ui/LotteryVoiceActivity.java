package com.jcoding.aiactivity.ui;

import android.Manifest;
import android.animation.ValueAnimator;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.VoiceManager;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

/**
 * 语音版抽奖执行页
 * 支持语音命令触发抽奖
 */
public class LotteryVoiceActivity extends BaseActivity {

    private TextView tvProgramName;
    private TextView tvRollingText;
    private TextView tvWinnerList;
    private Button btnStart;
    private Button btnStop;
    private Button btnBack;
    private TextView tvOfflineMode;

    // 语音控件
    private ImageButton btnVoiceTrigger;
    private TextView tvVoiceStatus;

    private String programId;
    private String programName;
    private String fileName;

    private boolean isRolling = false;
    private List<String> candidates;
    private List<String> winners;
    private Random random;
    private ValueAnimator rollAnimator;

    private VoiceManager voiceManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lottery_voice);

        // 获取参数
        programId = getIntent().getStringExtra("program_id");
        programName = getIntent().getStringExtra("program_name");
        fileName = getIntent().getStringExtra("file_name");

        random = new Random();
        winners = new ArrayList<>();
        voiceManager = VoiceManager.getInstance(this);

        initViews();
        loadCandidates();
    }

    private void initViews() {
        tvProgramName = findViewById(R.id.tv_program_name);
        tvRollingText = findViewById(R.id.tv_rolling_text);
        tvWinnerList = findViewById(R.id.tv_winner_list);
        btnStart = findViewById(R.id.btn_start);
        btnStop = findViewById(R.id.btn_stop);
        btnBack = findViewById(R.id.btn_back);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        // 语音控件
        btnVoiceTrigger = findViewById(R.id.btn_voice_trigger);
        tvVoiceStatus = findViewById(R.id.tv_voice_status);

        tvProgramName.setText(programName);

        btnStart.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startLottery();
            }
        });

        btnStop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopLottery();
            }
        });

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnStop.setEnabled(false);

        // 语音触发按钮
        btnVoiceTrigger.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startVoiceRecognition();
            }
        });
    }

    /**
     * 启动语音识别
     */
    private void startVoiceRecognition() {
        requestPermissions(new String[]{
                Manifest.permission.RECORD_AUDIO
        }, new PermissionResultListener() {
            @Override
            public void onGranted() {
                tvVoiceStatus.setText("正在听...");
                tvVoiceStatus.setVisibility(View.VISIBLE);
                btnVoiceTrigger.setEnabled(false);

                voiceManager.startVoiceRecognition(new VoiceManager.VoiceRecognitionCallback() {
                    @Override
                    public void onIntermediateResult(String text) {
                        tvVoiceStatus.setText("听到: " + text);
                    }

                    @Override
                    public void onRecognitionResult(String text) {
                        tvVoiceStatus.setText("识别: " + text);
                        processVoiceCommand(text);
                    }

                    @Override
                    public void onError(String error) {
                        tvVoiceStatus.setText("识别失败: " + error);
                        btnVoiceTrigger.setEnabled(true);
                    }
                });
            }

            @Override
            public void onDenied() {
                showToast("需要录音权限才能使用语音控制");
            }
        });
    }

    /**
     * 处理语音命令
     */
    private void processVoiceCommand(String text) {
        if (text == null || text.isEmpty()) {
            btnVoiceTrigger.setEnabled(true);
            return;
        }

        text = text.toLowerCase().replace(" ", "");

        // 开始抽奖命令
        if (text.contains("开始") || text.contains("启动") || text.contains("抽奖")
                || text.contains("start")) {
            if (!isRolling) {
                startLottery();
            }
        }
        // 停止抽奖命令
        else if (text.contains("停止") || text.contains("停") || text.contains("stop")
                || text.contains("结束")) {
            if (isRolling) {
                stopLottery();
            }
        }
        // 抽奖命令（简化版）
        else if (text.contains("抽")) {
            if (!isRolling) {
                startLottery();
            }
        }

        btnVoiceTrigger.setEnabled(true);
    }

    /**
     * 加载候选人列表
     */
    private void loadCandidates() {
        // TODO: 从配置或API加载候选人列表
        candidates = new ArrayList<>();
        // 示例数据
        for (int i = 1; i <= 50; i++) {
            candidates.add("参与者" + i);
        }
        Collections.shuffle(candidates);
    }

    /**
     * 开始抽奖
     */
    private void startLottery() {
        if (candidates.isEmpty()) {
            showToast("没有候选人");
            return;
        }

        isRolling = true;
        btnStart.setEnabled(false);
        btnVoiceTrigger.setEnabled(false);
        btnStop.setEnabled(true);

        // 语音播报"开始抽奖"
        voiceManager.speakText("开始抽奖", new VoiceManager.VoiceSynthesisCallback() {
            @Override
            public void onSpeakStart() {}

            @Override
            public void onSpeakPaused() {}

            @Override
            public void onSpeakResumed() {}

            @Override
            public void onSpeakComplete() {
                // 播报完成后开始滚动
                startRolling();
            }

            @Override
            public void onError(String error) {
                // 即使语音失败，也继续抽奖
                startRolling();
            }
        });
    }

    /**
     * 开始滚动动画
     */
    private void startRolling() {
        rollAnimator = ValueAnimator.ofInt(0, candidates.size() - 1);
        rollAnimator.setDuration(100);
        rollAnimator.setRepeatCount(ValueAnimator.INFINITE);
        rollAnimator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
            @Override
            public void onAnimationUpdate(ValueAnimator animation) {
                int index = random.nextInt(candidates.size());
                tvRollingText.setText(candidates.get(index));
            }
        });
        rollAnimator.start();
    }

    /**
     * 停止抽奖
     */
    private void stopLottery() {
        if (!isRolling) {
            return;
        }

        isRolling = false;

        if (rollAnimator != null) {
            rollAnimator.cancel();
        }

        // 随机选择中奖者
        int winnerIndex = random.nextInt(candidates.size());
        String winner = candidates.get(winnerIndex);
        winners.add(winner);

        // 显示中奖者
        tvRollingText.setText(winner);
        updateWinnerList();

        // 从候选人中移除
        candidates.remove(winnerIndex);

        // 恢复按钮状态
        btnStart.setEnabled(true);
        btnVoiceTrigger.setEnabled(true);
        btnStop.setEnabled(false);

        // 语音播报中奖结果
        String announcement = "恭喜" + winner + "中奖！";
        voiceManager.speakText(announcement, new VoiceManager.VoiceSynthesisCallback() {
            @Override
            public void onSpeakStart() {}

            @Override
            public void onSpeakPaused() {}

            @Override
            public void onSpeakResumed() {}

            @Override
            public void onSpeakComplete() {}

            @Override
            public void onError(String error) {}
        });

        showToast("恭喜 " + winner + " 中奖！");

        // TODO: 推送中奖信息
    }

    /**
     * 更新中奖列表
     */
    private void updateWinnerList() {
        StringBuilder sb = new StringBuilder();
        sb.append("中奖名单：\n");
        for (int i = 0; i < winners.size(); i++) {
            sb.append(i + 1).append(". ").append(winners.get(i)).append("\n");
        }
        tvWinnerList.setText(sb.toString());
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (rollAnimator != null) {
            rollAnimator.cancel();
        }
        if (voiceManager != null) {
            voiceManager.stopVoiceRecognition();
            voiceManager.stopSpeaking();
        }
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
