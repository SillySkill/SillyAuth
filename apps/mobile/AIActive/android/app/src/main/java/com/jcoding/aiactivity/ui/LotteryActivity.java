package com.jcoding.aiactivity.ui;

import android.animation.ValueAnimator;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.Candidate;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.DigitalHumanManager;
import com.jcoding.aiactivity.manager.DigitalHumanGestureHelper;
import com.jcoding.aiactivity.manager.InnerShowDataManager;
import com.jcoding.aiactivity.manager.LotteryConfigManager;
import com.jcoding.aiactivity.manager.LotteryRiggedConfigManager;
import com.jcoding.aiactivity.manager.InnerShowNetworkClient;
import com.jcoding.aiactivity.manager.InnerShowNetworkConfigManager;
import com.jcoding.aiactivity.manager.VoiceManager;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * 抽奖执行页
 * 支持完全离线运行
 * 支持两种标的对象类型：
 * 1. 标的对象：人 - 滚动显示候选人姓名，抽出中奖人
 * 2. 标的对象：奖品 - 滚动显示奖品名称，抽出中奖奖品
 */
public class LotteryActivity extends BaseActivity {

    private TextView tvProgramName;
    private TextView tvRollingText;
    private TextView tvWinnerList;
    private TextView tvRemainingCount;
    private TextView tvTargetType;  // 标的对象类型显示
    private ImageView ivBackground;  // 背景图片
    private Button btnStart;
    private Button btnStop;
    private Button btnReset;
    private Button btnBack;
    private Button btnVoiceControl;
    private Button btnReturnPool;  // 回退奖池按钮
    private TextView tvOfflineMode;

    private String programId;
    private String programName;
    private String fileName;

    private boolean isRolling = false;
    private ValueAnimator rollAnimator;
    private List<String> displayList;  // 用于滚动显示的列表（人或奖品）

    private LotteryConfigManager lotteryManager;
    private LotteryRiggedConfigManager riggedConfigManager;
    private InnerShowDataManager innerShowDataManager;
    private InnerShowNetworkClient networkClient;
    private InnerShowNetworkConfigManager networkConfigManager;
    private int currentPrizeRound = 1;  // 当前抽奖轮次

    private TextView tvModeIndicator;  // 模式指示器

    // 数字人相关
    private FrameLayout digitalHumanContainer;
    private ImageView ivDigitalHuman;
    private DigitalHumanManager digitalHumanManager;
    private DigitalHumanGestureHelper gestureHelper;

    // 语音控制
    private VoiceManager voiceManager;
    private boolean isVoiceControlEnabled = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lottery);

        // 获取参数
        programId = getIntent().getStringExtra("program_id");
        programName = getIntent().getStringExtra("program_name");
        fileName = getIntent().getStringExtra("file_name");

        lotteryManager = LotteryConfigManager.getInstance(this);
        riggedConfigManager = LotteryRiggedConfigManager.getInstance(this);
        innerShowDataManager = InnerShowDataManager.getInstance(this);
        networkClient = InnerShowNetworkClient.getInstance(this);
        networkConfigManager = InnerShowNetworkConfigManager.getInstance(this);
        voiceManager = VoiceManager.getInstance(this);
        displayList = new ArrayList<>();

        initViews();
        initDigitalHuman();
        loadDisplayList();
    }

    private void initViews() {
        tvProgramName = findViewById(R.id.tv_program_name);
        tvRollingText = findViewById(R.id.tv_rolling_text);
        tvWinnerList = findViewById(R.id.tv_winner_list);
        tvRemainingCount = findViewById(R.id.tv_remaining_count);
        tvTargetType = findViewById(R.id.tv_target_type);
        tvModeIndicator = findViewById(R.id.tv_mode_indicator);
        ivBackground = findViewById(R.id.iv_background);
        btnStart = findViewById(R.id.btn_start);

        // 加载背景图片
        ConfigManager configManager = ConfigManager.getInstance(this);
        Bitmap backgroundBitmap = configManager.loadImageFromAssets("image/question_bk.png");
        if (backgroundBitmap != null) {
            ivBackground.setImageBitmap(backgroundBitmap);
        }
        btnStop = findViewById(R.id.btn_stop);
        btnReset = findViewById(R.id.btn_reset);
        btnBack = findViewById(R.id.btn_back);
        btnVoiceControl = findViewById(R.id.btn_voice_control);
        btnReturnPool = findViewById(R.id.btn_return_pool);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        tvProgramName.setText(programName);
        updateModeIndicator();
        updateTargetTypeIndicator();

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

        btnReset.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resetLottery();
            }
        });

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnVoiceControl.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleVoiceControl();
            }
        });

        btnReturnPool.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                returnToPool();
            }
        });

        btnStop.setEnabled(false);
    }

    /**
     * 切换语音控制
     */
    private void toggleVoiceControl() {
        if (!isVoiceControlEnabled) {
            // 启用语音控制
            isVoiceControlEnabled = true;
            btnVoiceControl.setText("🎤 停止语音");
            showToast("语音控制已启用，请说\"开始抽奖\"或\"停止抽奖\"");
            startVoiceRecognition();
        } else {
            // 禁用语音控制
            isVoiceControlEnabled = false;
            btnVoiceControl.setText("🎤 语音控制");
            voiceManager.stopVoiceRecognition();
            showToast("语音控制已关闭");
        }
    }

    /**
     * 开始语音识别
     */
    private void startVoiceRecognition() {
        requestPermissions(new String[]{
                android.Manifest.permission.RECORD_AUDIO
        }, new BaseActivity.PermissionResultListener() {
            @Override
            public void onGranted() {
                voiceManager.startVoiceRecognition(new VoiceManager.VoiceRecognitionCallback() {
                    @Override
                    public void onIntermediateResult(String text) {
                        // 可以显示实时识别结果
                    }

                    @Override
                    public void onRecognitionResult(String text) {
                        // 识别完成，分析语音命令
                        analyzeVoiceCommand(text);
                        // 继续监听
                        if (isVoiceControlEnabled) {
                            startVoiceRecognition();
                        }
                    }

                    @Override
                    public void onError(String error) {
                        showToast("语音识别失败: " + error);
                        // 出错后重试
                        if (isVoiceControlEnabled) {
                            startVoiceRecognition();
                        }
                    }
                });
            }

            @Override
            public void onDenied() {
                showToast("需要录音权限才能使用语音控制");
                isVoiceControlEnabled = false;
                btnVoiceControl.setText("🎤 语音控制");
            }
        });
    }

    /**
     * 分析语音命令
     */
    private void analyzeVoiceCommand(String text) {
        if (text == null || text.isEmpty()) {
            return;
        }

        String command = text.toLowerCase().replace(" ", "").replace("，", "").replace("。", "");

        // 开始抽奖命令
        if (command.contains("开始") && command.contains("抽奖")) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (!isRolling) {
                        startLottery();
                        showToast("语音命令：开始抽奖");
                    }
                }
            });
        }
        // 停止抽奖命令
        else if (command.contains("停止") && command.contains("抽奖")) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (isRolling) {
                        stopLottery();
                        showToast("语音命令：停止抽奖");
                    }
                }
            });
        }
    }

    /**
     * 获取当前轮次的标的对象类型
     */
    private LotteryRiggedConfigManager.TargetType getCurrentTargetType() {
        LotteryRiggedConfigManager.RiggedConfigItem riggedConfig =
                riggedConfigManager.getRiggedConfigByRound(currentPrizeRound);

        if (riggedConfig != null && riggedConfigManager.getLotteryMode() == LotteryRiggedConfigManager.LotteryMode.RIGGED) {
            return riggedConfig.targetType;
        }

        // 随机模式默认标的对象是人
        return LotteryRiggedConfigManager.TargetType.PERSON;
    }

    /**
     * 更新标的对象类型指示器
     */
    private void updateTargetTypeIndicator() {
        LotteryRiggedConfigManager.TargetType targetType = getCurrentTargetType();

        if (targetType == LotteryRiggedConfigManager.TargetType.PERSON) {
            tvTargetType.setText("👤 标的对象：人");
        } else {
            tvTargetType.setText("🎁 标的对象：奖品");
        }
        tvTargetType.setVisibility(View.VISIBLE);
    }

    /**
     * 加载显示列表（根据标的对象类型）
     */
    private void loadDisplayList() {
        LotteryRiggedConfigManager.TargetType targetType = getCurrentTargetType();
        displayList.clear();

        if (targetType == LotteryRiggedConfigManager.TargetType.PERSON) {
            // 标的对象是人：加载候选人列表
            List<Candidate> candidates = lotteryManager.getAvailableCandidates();
            if (candidates.isEmpty()) {
                showToast("没有候选人，请先重置抽奖");
                return;
            }

            for (Candidate candidate : candidates) {
                displayList.add(candidate.getName());
            }

            updateRemainingCount();
        } else {
            // 标的对象是奖品：加载奖品列表
            List<LotteryRiggedConfigManager.PrizeItem> prizes = riggedConfigManager.getPrizeList();
            if (prizes.isEmpty()) {
                showToast("没有奖品，请先在设置中添加奖品");
                tvRemainingCount.setText("奖品: 0");
                return;
            }

            for (LotteryRiggedConfigManager.PrizeItem prize : prizes) {
                displayList.add(prize.name);
            }

            tvRemainingCount.setText("奖品: " + prizes.size());
        }
    }

    /**
     * 更新模式指示器$
     */
    private void updateModeIndicator() {
        LotteryRiggedConfigManager.LotteryMode mode = riggedConfigManager.getLotteryMode();
        if (mode == LotteryRiggedConfigManager.LotteryMode.RIGGED) {
            // 内定模式 - 灰度显示
            tvModeIndicator.setText("⚙️ 内定模式");
            tvModeIndicator.setBackgroundColor(getResources().getColor(R.color.mode_rigged));
            tvModeIndicator.setTextColor(getResources().getColor(android.R.color.white));
        } else {
            // 随机模式 - 彩旗显示
            tvModeIndicator.setText("🎲 随机模式");
            tvModeIndicator.setBackgroundColor(getResources().getColor(R.color.mode_random));
            tvModeIndicator.setTextColor(getResources().getColor(android.R.color.white));
        }
        tvModeIndicator.setVisibility(View.VISIBLE);
    }

    /**
     * 初始化数字人
     */
    private void initDigitalHuman() {
        digitalHumanContainer = findViewById(R.id.digital_human_container);
        ivDigitalHuman = findViewById(R.id.iv_digital_human);

        ConfigManager globalConfigManager = ConfigManager.getInstance(this);

        if (globalConfigManager.isDigitalHumanEnabledForModule("lottery")) {
            digitalHumanManager = DigitalHumanManager.getInstance(this);
            digitalHumanContainer.setVisibility(View.VISIBLE);

            // 应用配置的数字人位置
            String position = globalConfigManager.getDigitalHumanPosition();
            RelativeLayout.LayoutParams params =
                (RelativeLayout.LayoutParams) digitalHumanContainer.getLayoutParams();

            // 清除所有对齐规则
            params.removeRule(RelativeLayout.ALIGN_PARENT_TOP);
            params.removeRule(RelativeLayout.ALIGN_PARENT_BOTTOM);
            params.removeRule(RelativeLayout.ALIGN_PARENT_START);
            params.removeRule(RelativeLayout.ALIGN_PARENT_END);

            // 根据配置设置位置
            switch (position) {
                case "left_top":
                    params.addRule(RelativeLayout.ALIGN_PARENT_TOP, RelativeLayout.TRUE);
                    params.addRule(RelativeLayout.ALIGN_PARENT_START, RelativeLayout.TRUE);
                    break;
                case "right_top":
                    params.addRule(RelativeLayout.ALIGN_PARENT_TOP, RelativeLayout.TRUE);
                    params.addRule(RelativeLayout.ALIGN_PARENT_END, RelativeLayout.TRUE);
                    break;
                case "left_bottom":
                    params.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM, RelativeLayout.TRUE);
                    params.addRule(RelativeLayout.ALIGN_PARENT_START, RelativeLayout.TRUE);
                    break;
                case "right_bottom":
                default:
                    params.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM, RelativeLayout.TRUE);
                    params.addRule(RelativeLayout.ALIGN_PARENT_END, RelativeLayout.TRUE);
                    break;
            }
            digitalHumanContainer.setLayoutParams(params);
            // 显示默认数字人动画（使用Glide加载GIF）
            updateDigitalHumanImage(digitalHumanManager.getDefaultGif());

            // 设置手势支持
            setupDigitalHumanGestures();

            // 欢迎动作
            digitalHumanManager.welcome(new DigitalHumanManager.DigitalHumanCallback() {
                @Override
                public void onSpeakStart(String gifPath) {
                    updateDigitalHumanImage(gifPath);
                }

                @Override
                public void onComplete() {
                    String defaultGif = digitalHumanManager.getDefaultGif();
                    updateDigitalHumanImage(defaultGif);
                }

                @Override
                public void onError(String error) {
                    Log.e("LotteryActivity", "Digital human error: " + error);
                }
            });
        } else {
            digitalHumanContainer.setVisibility(View.GONE);
        }
    }

    /**
     * 设置数字人手势支持
     */
    private void setupDigitalHumanGestures() {
        // 创建手势辅助类
        gestureHelper = new DigitalHumanGestureHelper(digitalHumanContainer, ivDigitalHuman, this);

        // 设置缩放范围
        gestureHelper.setScaleRange(0.5f, 3.0f);

        // 设置手势回调
        gestureHelper.setGestureCallback(new DigitalHumanGestureHelper.GestureCallback() {
            @Override
            public void onDragStart() {
                Log.d("LotteryActivity", "Digital human drag started");
            }

            @Override
            public void onDragEnd() {
                Log.d("LotteryActivity", "Digital human drag ended");
            }

            @Override
            public void onScaleChanged(float scale) {
                Log.d("LotteryActivity", "Digital human scale changed: " + scale);
            }

            @Override
            public void onDoubleClick() {
                Log.d("LotteryActivity", "Digital human double clicked");
                showToast("双击切换大小");
            }
        });

        Log.d("LotteryActivity", "Digital human gestures enabled");
    }

    /**
     * 更新数字人图片（使用Glide加载GIF动画）
     */
    private void updateDigitalHumanImage(String gifPath) {
        if (digitalHumanContainer == null || digitalHumanContainer.getVisibility() != View.VISIBLE) {
            return;
        }

        if (ivDigitalHuman == null) {
            return;
        }

        ConfigManager globalConfigManager = ConfigManager.getInstance(this);

        // 获取配置的大小（dp值），转换为px
        int sizeDp = globalConfigManager.getDigitalHumanSize();
        final int sizePx = (int) (sizeDp * getResources().getDisplayMetrics().density);

        // 设置ImageView尺寸
        FrameLayout.LayoutParams params = (FrameLayout.LayoutParams) ivDigitalHuman.getLayoutParams();
        params.width = sizePx;
        params.height = sizePx;
        ivDigitalHuman.setLayoutParams(params);

        // 获取缩放类型
        String scaleType = globalConfigManager.getDigitalHumanScaleType();
        final ImageView.ScaleType finalScaleType;
        if ("center_crop".equals(scaleType)) {
            finalScaleType = ImageView.ScaleType.CENTER_CROP;
        } else if ("center".equals(scaleType)) {
            finalScaleType = ImageView.ScaleType.CENTER;
        } else {
            finalScaleType = ImageView.ScaleType.FIT_CENTER;
        }
        ivDigitalHuman.setScaleType(finalScaleType);

        // 使用Glide加载GIF动画
        try {
            // 检查路径是否已经包含aibeing/前缀
            String assetPath = gifPath.startsWith("aibeing/") ? gifPath : "aibeing/" + gifPath;
            // 先将GIF从assets复制到缓存文件
            String outputFileName = "temp_" + (gifPath.replace("/", "_"));
            java.io.File gifFile = copyAssetToFile(assetPath, outputFileName);

            if (gifFile != null && gifFile.exists()) {
                com.bumptech.glide.Glide.with(this)
                        .asGif()
                        .load(gifFile)
                        .override(sizePx, sizePx)
                        .placeholder(android.graphics.Color.TRANSPARENT)
                        .error(android.graphics.Color.TRANSPARENT)
                        .into(new com.bumptech.glide.request.target.CustomTarget<com.bumptech.glide.load.resource.gif.GifDrawable>() {
                            @Override
                            public void onResourceReady(com.bumptech.glide.load.resource.gif.GifDrawable resource, com.bumptech.glide.request.transition.Transition<? super com.bumptech.glide.load.resource.gif.GifDrawable> transition) {
                                ivDigitalHuman.setImageDrawable(resource);
                                String scaleType = globalConfigManager.getDigitalHumanScaleType();
                                if ("center_crop".equals(scaleType)) {
                                    ivDigitalHuman.setScaleType(ImageView.ScaleType.CENTER_CROP);
                                } else if ("center".equals(scaleType)) {
                                    ivDigitalHuman.setScaleType(ImageView.ScaleType.CENTER);
                                } else {
                                    ivDigitalHuman.setScaleType(ImageView.ScaleType.FIT_CENTER);
                                }
                                resource.start();
                            }

                            @Override
                            public void onLoadCleared(android.graphics.drawable.Drawable placeholder) {
                            }
                        });
            } else {
                Log.e("LotteryActivity", "GIF file not found: " + assetPath);
            }
        } catch (Exception e) {
            Log.e("LotteryActivity", "Failed to load GIF: " + gifPath, e);
        }
    }

    /**
     * 更新剩余人数显示
     */
    private void updateRemainingCount() {
        int remaining = lotteryManager.getAvailableCandidates().size();
        int total = lotteryManager.getAllCandidates().size();
        tvRemainingCount.setText(String.format("剩余 %d/%d", remaining, total));
    }

    /**
     * 开始抽奖
     */
    private void startLottery() {
        // 重新加载显示列表
        loadDisplayList();

        if (displayList.isEmpty()) {
            LotteryRiggedConfigManager.TargetType targetType = getCurrentTargetType();
            if (targetType == LotteryRiggedConfigManager.TargetType.PERSON) {
                showToast("所有候选人均已中奖，请重置抽奖");
            } else {
                showToast("没有奖品，请先在设置中添加奖品");
            }
            return;
        }

        isRolling = true;
        btnStart.setEnabled(false);
        btnStop.setEnabled(true);
        btnReset.setEnabled(false);

        // 开始滚动动画
        rollAnimator = ValueAnimator.ofInt(0, displayList.size() - 1);
        rollAnimator.setDuration(100);
        rollAnimator.setRepeatCount(ValueAnimator.INFINITE);
        rollAnimator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
            @Override
            public void onAnimationUpdate(ValueAnimator animation) {
                int index = (int) animation.getAnimatedValue();
                if (index < displayList.size()) {
                    tvRollingText.setText(displayList.get(index));
                }
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

        // 获取标的对象类型
        LotteryRiggedConfigManager.TargetType targetType = getCurrentTargetType();

        // 检查当前轮次是否内定
        String resultText = "";  // 结果显示文本
        String prizeName = "奖品";  // 奖品名称
        Candidate winner = null;  // 中奖者
        LotteryRiggedConfigManager.PrizeItem prize = null;  // 中奖奖品

        LotteryRiggedConfigManager.RiggedConfigItem riggedConfig =
                riggedConfigManager.getRiggedConfigByRound(currentPrizeRound);

        if (riggedConfig != null && riggedConfigManager.getLotteryMode() == LotteryRiggedConfigManager.LotteryMode.RIGGED) {
            // 内定模式
            prizeName = riggedConfig.prizeName;

            if (targetType == LotteryRiggedConfigManager.TargetType.PERSON) {
                // 标的对象是人：滚动显示候选人，结果是中奖者
                List<Candidate> allCandidates = lotteryManager.getAllCandidates();
                for (Candidate candidate : allCandidates) {
                    if (candidate.getId().equals(riggedConfig.candidateId)) {
                        winner = candidate;
                        break;
                    }
                }

                if (winner != null) {
                    // 从prizeDate.json加载的数据：name=店铺名，department=礼品
                    String shopName = winner.getName();
                    String gift = winner.getDepartment();
                    resultText = shopName + "\n\n" + gift + "\n\n恭喜中奖！";
                    showToast("恭喜你中了 " + shopName + " 的 " + gift + "！");
                }
            } else {
                // 标的对象是奖品：滚动显示奖品，结果是中奖奖品
                if (riggedConfig.prizeId != null) {
                    resultText = prize.name + "\n\n恭喜中奖！" + (prize.description != null ? "\n\n" + prize.description : "");
                    showToast("恭喜中奖！" + prize.name);
                } else if (riggedConfig.prizeName != null) {
                    resultText = riggedConfig.prizeName + "\n\n恭喜中奖！";
                    showToast("恭喜中奖！" + riggedConfig.prizeName);
                }

                if (prize != null) {
                    resultText = prize.name + "\n\n恭喜中奖！" + (prize.description != null ? "\n\n" + prize.description : "");
                    showToast("恭喜中奖！" + prize.name);
                } else if (riggedConfig.prizeName != null) {
                    resultText = riggedConfig.prizeName + "\n\n恭喜中奖！";
                    showToast("恭喜中奖！" + riggedConfig.prizeName);
                }

                // 奖品模式下也需要一个中奖人（随机抽取）
                winner = lotteryManager.drawWinner();
            }
        } else {
            // 随机模式
            if (targetType == LotteryRiggedConfigManager.TargetType.PERSON) {
                winner = lotteryManager.drawWinner();
                if (winner != null) {
                    // 从prizeDate.json加载的数据：name=店铺名，department=礼品
                    String shopName = winner.getName();
                    String gift = winner.getDepartment();
                    String winnerName = shopName;

                    resultText = shopName + "\n\n" + gift + "\n\n恭喜中奖！";
                    showToast("恭喜你中了 " + shopName + " 的 " + gift + "！");
                }
            } else {
                // 标的对象是奖品：随机抽取奖品
                List<LotteryRiggedConfigManager.PrizeItem> prizes = riggedConfigManager.getPrizeList();
                if (!prizes.isEmpty()) {
                    int randomIndex = (int) (Math.random() * prizes.size());
                    prize = prizes.get(randomIndex);
                    resultText = prize.name + "\n\n恭喜中奖！" + (prize.description != null ? "\n\n" + prize.description : "");
                    showToast("恭喜中奖！" + prize.name);

                    // 同时也需要一个中奖人（随机抽取）
                    winner = lotteryManager.drawWinner();
                }
            }
        }

        // 检查抽奖是否成功
        if (targetType == LotteryRiggedConfigManager.TargetType.PERSON && winner == null) {
            showToast("抽奖失败，没有可用候选人");
            btnStart.setEnabled(true);
            btnStop.setEnabled(false);
            btnReset.setEnabled(true);
            return;
        }

        if (targetType == LotteryRiggedConfigManager.TargetType.PRIZE && prize == null && winner == null) {
            showToast("抽奖失败，没有可用奖品或候选人");
            btnStart.setEnabled(true);
            btnStop.setEnabled(false);
        // 检查抽奖是否成功
            return;
        }

        // 显示结果
        tvRollingText.setText(resultText);

        // 数字人祝贺（检查模块语音配置）
        if (digitalHumanManager != null && winner != null && digitalHumanManager.isEnabled() && isVoiceEnabledForModule()) {
            digitalHumanManager.congratulate(
                winner.getName(),
                prizeName != null ? prizeName : "奖品",
                new DigitalHumanManager.DigitalHumanCallback() {
                    @Override
                    public void onSpeakStart(String gifPath) {
                        updateDigitalHumanImage(gifPath);
                    }

                    @Override
                    public void onComplete() {
                        String defaultGif = digitalHumanManager.getDefaultGif();
                        updateDigitalHumanImage(defaultGif);
                    }

                    @Override
                    public void onError(String error) {
                        Log.e("LotteryActivity", "Digital human congratulate error: " + error);
                    }
                }
            );
        }

        // 恢复按钮状态

        // 记录中奖信息（如果有中奖人）
        if (winner != null) {
            lotteryManager.addWinnerRecord(winner, prizeName);
            pushToInnerShow(winner, prizeName);
        }

        // 更新显示列表
        if (targetType == LotteryRiggedConfigManager.TargetType.PERSON && winner != null) {
            displayList.remove(winner.getName());
        }

        updateWinnerList();
        loadDisplayList();  // 刷新显示列表

        // 恢复按钮状态
        btnStart.setEnabled(true);
        btnStop.setEnabled(false);

        // 离线提示
        if (!NetworkUtils.isOnline(this)) {
            if (winner != null) {
                String shopName = winner.getName();
                String gift = winner.getDepartment();
                showToast("恭喜你中了 " + shopName + " 的 " + gift + "！（离线模式，已保存到本地）");
            }
        }
    }

    /**
     * 重置抽奖
     */
    private void resetLottery() {
        new android.app.AlertDialog.Builder(this)
                .setTitle("重置抽奖")
                .setMessage("确定要清空中奖记录并重新开始抽奖吗？")
                .setPositiveButton("确定", (dialog, which) -> {
                    lotteryManager.resetLottery();
                    loadDisplayList();
                    tvRollingText.setText("准备抽奖");
                    tvWinnerList.setText("中奖名单：\n");
                    showToast("抽奖已重置");
                })
                .setNegativeButton("取消", null)
                .show();
    }

    /**
     * 回退奖池（移除最后一条中奖记录）
     */
    private void returnToPool() {
        if (lotteryManager.getWinnerCount() == 0) {
            showToast("没有可回退的中奖记录");
            return;
        }

        LotteryConfigManager.WinnerRecord lastRecord = lotteryManager.getWinnerRecords()
                .get(lotteryManager.getWinnerCount() - 1);

        String message = "确定要回退最后一条中奖记录吗？\n\n";
        message += "中奖人：" + lastRecord.getCandidateName();
        if (lastRecord.getPrizeName() != null) {
            message += "\n奖品：" + lastRecord.getPrizeName();
        }

        new android.app.AlertDialog.Builder(this)
                .setTitle("回退奖池")
                .setMessage(message)
                .setPositiveButton("确定", (dialog, which) -> {
                    boolean success = lotteryManager.returnToPool();
                    if (success) {
                        loadDisplayList();
                        updateWinnerList();
                        updateRemainingCount();
                        tvRollingText.setText("准备抽奖");
                        showToast("已回退到奖池");
                    } else {
                        showToast("回退失败");
                    }
                })
                .setNegativeButton("取消", null)
                .show();
    }

    /**
     * 更新中奖名单
     */
    private void updateWinnerList() {
        List<LotteryConfigManager.WinnerRecord> records = lotteryManager.getWinnerRecords();
        StringBuilder sb = new StringBuilder();
        sb.append("中奖名单：\n");
        for (int i = 0; i < records.size(); i++) {
            LotteryConfigManager.WinnerRecord record = records.get(i);
            sb.append(i + 1).append(". ").append(record.getCandidateName());
            if (record.getPrizeName() != null) {
                sb.append(" - ").append(record.getPrizeName());
            }
            sb.append("\n");
        }
        tvWinnerList.setText(sb.toString());
    }

    /**
     * 推送中奖信息到内场秀
     */
    private void pushToInnerShow(Candidate winner, String prizeName) {
        // 创建中奖记录
        InnerShowDataManager.LotteryWinner lotteryWinner = new InnerShowDataManager.LotteryWinner();
        lotteryWinner.winnerName = winner.getName();
        lotteryWinner.winnerPhone = winner.getPhone();
        lotteryWinner.winnerDepartment = winner.getDepartment();
        lotteryWinner.prizeName = prizeName;
        lotteryWinner.lotteryProgram = programName;
        lotteryWinner.prizeRound = currentPrizeRound;

        // 保存到内场秀数据管理器
        innerShowDataManager.addLotteryWinner(lotteryWinner);

        // 检查是否是主服务器模式
        if (networkConfigManager.isServerMode()) {
            // 主服务器模式：本设备就是内场秀设备，直接发送本地广播
            Intent broadcast = new Intent("com.jcoding.aiactivity.INNER_SHOW_UPDATE");
            broadcast.putExtra("action", "new_lottery_winner");
            broadcast.putExtra("winner_id", lotteryWinner.id);
            broadcast.putExtra("winner_name", winner.getName());
            sendBroadcast(broadcast);
        } else {
            // 客户端模式：通过网络推送到内场秀设备
            networkClient.pushLotteryWinner(lotteryWinner, new InnerShowNetworkClient.NetworkCallback() {
                @Override
                public void onSuccess(String result) {
                    // 网络推送成功
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            // 静默成功，不显示Toast
                        }
                    });
                }

                @Override
                public void onError(String error) {
                    // 网络推送失败，已保存到本地
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            android.util.Log.e("LotteryActivity", "推送失败 " + error);
                        }
                    });
                }
            });

            // 同时发送本地广播（同一设备的情况）
            Intent broadcast = new Intent("com.jcoding.aiactivity.INNER_SHOW_UPDATE");
            broadcast.putExtra("action", "new_lottery_winner");
            broadcast.putExtra("winner_id", lotteryWinner.id);
            broadcast.putExtra("winner_name", winner.getName());
            sendBroadcast(broadcast);
        }
    }

    /**
     * 检查lottery模块的语音是否启用
     */
    private boolean isVoiceEnabledForModule() {
        // 检查lottery模块的语音播报是否启用
        return configManager.isDigitalHumanEnabledForModule("lottery");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (rollAnimator != null) {
            rollAnimator.cancel();
        }
        // 释放手势辅助类资源
        if (gestureHelper != null) {
            gestureHelper.release();
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

    /**
     * 将assets中的文件复制到缓存目录
     */
    private java.io.File copyAssetToFile(String assetPath, String outputFileName) {
        java.io.InputStream is = null;
        java.io.OutputStream os = null;
        try {
            java.io.File outputFile = new java.io.File(getCacheDir(), outputFileName);
            if (outputFile.exists()) {
                return outputFile;
            }
            is = getAssets().open(assetPath);
            os = new java.io.FileOutputStream(outputFile);
            byte[] buffer = new byte[8192];
            int len;
            while ((len = is.read(buffer)) != -1) {
                os.write(buffer, 0, len);
            }
            os.flush();
            return outputFile;
        } catch (java.io.IOException e) {
            e.printStackTrace();
            return null;
        } finally {
            try {
                if (is != null) is.close();
                if (os != null) os.close();
            } catch (java.io.IOException e) {
                e.printStackTrace();
            }
        }
    }
}

