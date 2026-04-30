package com.jcoding.aiactivity.ui;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.InnerShowModule;
import com.jcoding.aiactivity.manager.BackgroundMediaManager;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.DigitalHumanManager;
import com.jcoding.aiactivity.manager.InnerShowDataManager;
import com.jcoding.aiactivity.manager.InnerShowNetworkServerManager;
import com.jcoding.aiactivity.manager.InnerShowNetworkConfigManager;
import com.jcoding.aiactivity.manager.InnerShowNetworkClient;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.File;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
    * 内场秀页
 * 固定横屏显示，展示AI生成结果、签到信息、数字人播报
 */
public class InnerActivity extends BaseActivity {

        private static final long AUTO_ROTATE_INTERVAL = 5000; // 5秒自动切换

    private ImageView ivBackground;
    private ImageView ivContent;
    private TextView tvSignature;
    private TextView tvInfo;
    private Button btnBack;
    private Button btnPrev;
    private Button btnNext;
    private Button btnToggleAuto;

    private InnerShowDataManager dataManager;
    private InnerShowNetworkServerManager serverManager;
    private InnerShowNetworkConfigManager networkConfigManager;
    private InnerShowNetworkClient networkClient;
    private BackgroundMediaManager backgroundMediaManager;
    private ExecutorService executorService = Executors.newSingleThreadExecutor();
    private Handler handler = new Handler(Looper.getMainLooper());

        // 当前活动的模块（默认暖场秀模式）
    private InnerShowModule currentModule = InnerShowModule.WARMUP;

    private List<InnerShowDataManager.GenerationResult> resultList;
    private List<InnerShowDataManager.CheckInRecord> checkInList;
    private List<InnerShowDataManager.LotteryWinner> winnerList;
    private int currentPosition = 0;
    private boolean autoRotate = false;
    private Runnable autoRotateRunnable;

        // 显示模式：1=AI生成结果，2=抽奖中奖信息
    private int displayMode = 0;
    private static final int MODE_GENERATION = 0;
    private static final int MODE_LOTTERY = 1;

        // 数字人相关
    private FrameLayout digitalHumanContainer;
    private ImageView ivDigitalHuman;
    private DigitalHumanManager digitalHumanManager;

        // 广播接收器注册状态
    private boolean isReceiverRegistered = false;

    private BroadcastReceiver updateReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
                // 检查当前模块是否接受广播
            ConfigManager configManager = ConfigManager.getInstance(InnerActivity.this);
            if (!configManager.getInnerShowAcceptBroadcast(currentModule.getId())) {
                    Log.d("InnerActivity", "当前模块不接受广播: " + currentModule.getName());
                return;
            }

            String action = intent.getStringExtra("action");
            if ("new_image".equals(action)) {
                    // 有新图片推送过来
                refreshData();
                switchToGenerationMode();
            } else if ("new_lottery_winner".equals(action)) {
                    // 有新的中奖信息
                refreshData();
                switchToLotteryMode();
                // 显示中奖提示
                String winnerName = intent.getStringExtra("winner_name");
                showWinnerToast(winnerName);
            } else if ("new_quiz_winner".equals(action)) {
                    // 有新的答题中奖信息
                refreshData();
                switchToQuizMode();
                // 显示中奖提示
                String winnerName = intent.getStringExtra("winner_name");
                showWinnerToast(winnerName);
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_inner);

        try {
            dataManager = InnerShowDataManager.getInstance(this);
            serverManager = InnerShowNetworkServerManager.getInstance(this);
            networkConfigManager = InnerShowNetworkConfigManager.getInstance(this);
            networkClient = InnerShowNetworkClient.getInstance(this);
            backgroundMediaManager = BackgroundMediaManager.getInstance(this);

            initViews();
            initDigitalHuman();
            setupListeners();

            // 应用当前模块配置
            applyModuleConfig(currentModule);

            // 启动网络服务器（如果是主服务器模式）
            startNetworkServerIfNeeded();

            loadData();
            registerReceiver();
            startAutoRotate();
        } catch (Exception e) {
                Log.e("InnerActivity", "初始化失败: " + e.getMessage(), e);
                showToast("初始化失败: " + e.getMessage());
            finish();
        }
    }

    private void initViews() {
        ivBackground = findViewById(R.id.iv_background);
        ivContent = findViewById(R.id.iv_content);
        tvSignature = findViewById(R.id.tv_signature);
        tvInfo = findViewById(R.id.tv_info);
        btnBack = findViewById(R.id.btn_back);
        btnPrev = findViewById(R.id.btn_prev);
        btnNext = findViewById(R.id.btn_next);
        btnToggleAuto = findViewById(R.id.btn_toggle_auto);
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnPrev.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showPrevious();
            }
        });

        btnNext.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showNext();
            }
        });

        btnToggleAuto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleAutoRotate();
            }
        });
    }

    /**
     * 初始化数字人
     */
    private void initDigitalHuman() {
        try {
            digitalHumanContainer = findViewById(R.id.digital_human_container);
            ivDigitalHuman = findViewById(R.id.iv_digital_human);

            if (digitalHumanContainer == null || ivDigitalHuman == null) {
                Log.e("InnerActivity", "数字人视图初始化失败");
                return;
            }

            ConfigManager globalConfigManager = ConfigManager.getInstance(this);

            if (globalConfigManager != null && globalConfigManager.isDigitalHumanEnabledForModule("inner")) {
                digitalHumanManager = DigitalHumanManager.getInstance(this);
                if (digitalHumanManager == null) {
                    Log.e("InnerActivity", "DigitalHumanManager初始化失败");
                    digitalHumanContainer.setVisibility(View.GONE);
                    return;
                }
                digitalHumanContainer.setVisibility(View.VISIBLE);

                // 应用配置的数字人位置
                String position = globalConfigManager.getDigitalHumanPosition();
                if (position == null) position = "bottom_right";

                FrameLayout.LayoutParams params =
                    (FrameLayout.LayoutParams) digitalHumanContainer.getLayoutParams();

                if (params == null) {
                    params = new FrameLayout.LayoutParams(
                        FrameLayout.LayoutParams.WRAP_CONTENT,
                        FrameLayout.LayoutParams.WRAP_CONTENT
                    );
                }

                // 根据配置设置位置（使用正确的值）
                switch (position) {
                    case "top":
                        params.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL;
                        break;
                    case "middle":
                        params.gravity = Gravity.CENTER;
                        break;
                    case "bottom":
                        params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
                        break;
                    case "bottom_right":
                    default:
                        params.gravity = Gravity.BOTTOM | Gravity.END;
                        break;
                }

                // 应用配置的数字人大小
                int sizeDp = globalConfigManager.getDigitalHumanSize();
                float scale = getResources().getDisplayMetrics().density;
                int sizePx = (int) (sizeDp * scale);
                params.height = sizePx;
                    params.width = (int) (sizePx * 0.8f); // 宽高比4:5

                // 应用缩放模式
                String scaleType = globalConfigManager.getDigitalHumanScaleType();
                if (scaleType == null) scaleType = "center";

                switch (scaleType) {
                    case "fit_center":
                        ivDigitalHuman.setScaleType(ImageView.ScaleType.FIT_CENTER);
                        break;
                    case "center_crop":
                        ivDigitalHuman.setScaleType(ImageView.ScaleType.CENTER_CROP);
                        break;
                    case "center":
                    default:
                        ivDigitalHuman.setScaleType(ImageView.ScaleType.CENTER);
                        break;
                }

                digitalHumanContainer.setLayoutParams(params);

                    Log.i("InnerActivity", "数字人位置: " + position + ", 大小: " + sizeDp + "dp, 缩放: " + scaleType);

                    // 显示默认GIF（使用updateDigitalHumanImage方法）
                try {
                    String defaultGif = digitalHumanManager.getDefaultGif();
                    if (defaultGif != null) {
                        updateDigitalHumanImage(defaultGif);
                    }
                } catch (Exception e) {
                    Log.e("InnerActivity", "加载默认GIF失败: " + e.getMessage());
                }

                // 欢迎动作
                digitalHumanManager.welcome(new DigitalHumanManager.DigitalHumanCallback() {
                    @Override
                    public void onSpeakStart(String gifPath) {
                        updateDigitalHumanImage(gifPath);
                    }

                    @Override
                    public void onComplete() {
                        try {
                            String defaultGif = digitalHumanManager.getDefaultGif();
                            updateDigitalHumanImage(defaultGif);
                        } catch (Exception e) {
                            Log.e("InnerActivity", "恢复默认GIF失败: " + e.getMessage());
                        }
                    }

                    @Override
                    public void onError(String error) {
                        Log.e("InnerActivity", "Digital human error: " + error);
                    }
                });
            } else {
                digitalHumanContainer.setVisibility(View.GONE);
                Log.i("InnerActivity", "数字人未启用");
            }
        } catch (Exception e) {
            Log.e("InnerActivity", "初始化数字人失败: " + e.getMessage(), e);
            if (digitalHumanContainer != null) {
                digitalHumanContainer.setVisibility(View.GONE);
            }
        }
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
                Log.e("InnerActivity", "GIF file not found: " + assetPath);
            }
        } catch (Exception e) {
            Log.e("InnerActivity", "Failed to load GIF: " + gifPath, e);
        }
    }

    /**
     * 加载数据
     */
    private void loadData() {
        executorService.execute(new Runnable() {
            @Override
            public void run() {
                resultList = dataManager.getGenerationResults();
                checkInList = dataManager.getCheckInRecords();
                winnerList = dataManager.getLotteryWinners();

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        if (displayMode == MODE_GENERATION) {
                            if (!resultList.isEmpty()) {
                                    // 显示当前应该显示的图片
                                InnerShowDataManager.GenerationResult current = dataManager.getCurrentDisplayImage();
                                if (current != null) {
                                    currentPosition = findPosition(current.id);
                                    displayResult(current);
                                } else {
                                    displayResult(resultList.get(0));
                                }
                            } else {
                                showEmptyState();
                            }
                        } else if (displayMode == MODE_LOTTERY) {
                            if (!winnerList.isEmpty()) {
                                currentPosition = 0;
                                displayWinner(winnerList.get(0));
                            } else {
                                showEmptyState();
                            }
                        }

                        updateInfo();
                    }
                });
            }
        });
    }

    /**
     * 刷新数据
     */
    private void refreshData() {
        loadData();
    }

    /**
     * 查找位置
     */
    private int findPosition(String id) {
        for (int i = 0; i < resultList.size(); i++) {
            if (resultList.get(i).id.equals(id)) {
                return i;
            }
        }
        return 0;
    }

    /**
     * 显示生成结果
     */
    private void displayResult(InnerShowDataManager.GenerationResult result) {
        executorService.execute(new Runnable() {
            @Override
            public void run() {
                // 加载图片
                Bitmap resultBitmap = null;
                Bitmap originalBitmap = null;

                    // 尝试从本地文件加载
                if (result.resultImagePath != null) {
                    resultBitmap = dataManager.loadImageFromLocal(result.resultImagePath);
                }
                if (result.originalImagePath != null) {
                    originalBitmap = dataManager.loadImageFromLocal(result.originalImagePath);
                }

                    // 合成图片（原图+签名）
                Bitmap finalBitmap = compositeImage(originalBitmap, result);

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        if (finalBitmap != null) {
                            ivContent.setImageBitmap(finalBitmap);

                            // 显示签名
                            if (result.signature != null && !result.signature.isEmpty()) {
                                tvSignature.setText(result.signature);
                                tvSignature.setVisibility(View.VISIBLE);
                            } else {
                                tvSignature.setVisibility(View.GONE);
                            }
                        }
                    }
                });
            }
        });
    }

    /**
         * 合成图片和签名
     */
    private Bitmap compositeImage(Bitmap original, InnerShowDataManager.GenerationResult result) {
        try {
            // 如果有结果图URL，可以在这里下载
            // 简化实现：使用原图+文字签名

            if (original == null) {
                return null;
            }

            // 创建副本
            Bitmap composite = original.copy(Bitmap.Config.ARGB_8888, true);
            Canvas canvas = new Canvas(composite);

            // 添加签名文字
            if (result.signature != null && !result.signature.isEmpty() &&
                    !result.signature.startsWith("[签名图片]")) {
                Paint paint = new Paint();
                paint.setColor(Color.WHITE);
                paint.setTextSize(60);
                paint.setTypeface(Typeface.DEFAULT_BOLD);
                paint.setShadowLayer(10, 0, 0, Color.BLACK);

                    // 在底部居中显示签名
                String text = result.signature;
                float textWidth = paint.measureText(text);
                float x = (composite.getWidth() - textWidth) / 2;
                float y = composite.getHeight() - 100;

                canvas.drawText(text, x, y, paint);
            }

            // 添加风格名称
            Paint stylePaint = new Paint();
            stylePaint.setColor(Color.WHITE);
            stylePaint.setTextSize(50);
            stylePaint.setTypeface(Typeface.DEFAULT_BOLD);
            stylePaint.setShadowLayer(10, 0, 0, Color.BLACK);

            if (result.styleName != null) {
                canvas.drawText(result.styleName, 50, 100, stylePaint);
            }

            return composite;
        } catch (Exception e) {
            e.printStackTrace();
            return original;
        }
    }

    /**
         * 显示空状态
     */
    private void showEmptyState() {
        tvInfo.setText("暂无内容，请先生成AI百变秀图片");
        tvInfo.setVisibility(View.VISIBLE);
        ivContent.setImageDrawable(null);
        tvSignature.setVisibility(View.GONE);
    }

    /**
     * 更新信息显示
     */
    private void updateInfo() {
        StringBuilder sb = new StringBuilder();
        sb.append("AI生成: ").append(resultList != null ? resultList.size() : 0).append("个");
        sb.append("  |  ");
        sb.append("签到: ").append(checkInList != null ? checkInList.size() : 0).append("个");
        sb.append("  |  ");
        sb.append("中奖: ").append(winnerList != null ? winnerList.size() : 0).append("个");
        sb.append("  |  ");

        if (displayMode == MODE_GENERATION) {
            sb.append("当前: ").append(currentPosition + 1).append("/").append(resultList != null ? resultList.size() : 0);
        } else {
            sb.append("中奖名单: ").append(currentPosition + 1).append("/").append(winnerList != null ? winnerList.size() : 0);
        }

        tvInfo.setText(sb.toString());
        tvInfo.setVisibility(View.VISIBLE);
    }

    /**
     * 显示上一张
     */
    private void showPrevious() {
        if (displayMode == MODE_GENERATION) {
            if (resultList == null || resultList.isEmpty()) {
                return;
            }
            currentPosition--;
            if (currentPosition < 0) {
                currentPosition = resultList.size() - 1;
            }
            displayResult(resultList.get(currentPosition));
        } else if (displayMode == MODE_LOTTERY) {
            if (winnerList == null || winnerList.isEmpty()) {
                return;
            }
            currentPosition--;
            if (currentPosition < 0) {
                currentPosition = winnerList.size() - 1;
            }
            displayWinner(winnerList.get(currentPosition));
        }
        updateInfo();
    }

    /**
         * 显示下一张
     */
    private void showNext() {
        if (displayMode == MODE_GENERATION) {
            if (resultList == null || resultList.isEmpty()) {
                return;
            }
            currentPosition++;
            if (currentPosition >= resultList.size()) {
                currentPosition = 0;
            }
            displayResult(resultList.get(currentPosition));
        } else if (displayMode == MODE_LOTTERY) {
            if (winnerList == null || winnerList.isEmpty()) {
                return;
            }
            currentPosition++;
            if (currentPosition >= winnerList.size()) {
                currentPosition = 0;
            }
            displayWinner(winnerList.get(currentPosition));
        }
        updateInfo();
    }

    /**
     * 切换自动播放
     */
    private void toggleAutoRotate() {
        autoRotate = !autoRotate;
        btnToggleAuto.setText(autoRotate ? "暂停轮播" : "开始轮播");

        if (autoRotate) {
            startAutoRotate();
        } else {
            stopAutoRotate();
        }
    }

    /**
     * 开始自动轮播
     */
    private void startAutoRotate() {
        if (autoRotateRunnable != null) {
            handler.removeCallbacks(autoRotateRunnable);
        }

        autoRotateRunnable = new Runnable() {
            @Override
            public void run() {
                if (autoRotate) {
                    showNext();
                    handler.postDelayed(this, AUTO_ROTATE_INTERVAL);
                }
            }
        };

        handler.postDelayed(autoRotateRunnable, AUTO_ROTATE_INTERVAL);
    }

    /**
     * 停止自动轮播
     */
    private void stopAutoRotate() {
        if (autoRotateRunnable != null) {
            handler.removeCallbacks(autoRotateRunnable);
        }
    }

    /**
         * 注册广播接收器
     */
    private void registerReceiver() {
        if (!isReceiverRegistered) {
            try {
                IntentFilter filter = new IntentFilter("com.jcoding.aiactivity.INNER_SHOW_UPDATE");
                    // Android 14+ 需要指定RECEIVER_NOT_EXPORTED 标志
                registerReceiver(updateReceiver, filter, Context.RECEIVER_NOT_EXPORTED);
                isReceiverRegistered = true;
                Log.i("InnerActivity", "广播接收器已注册");
            } catch (Exception e) {
                    Log.e("InnerActivity", "注册广播接收器失败: " + e.getMessage(), e);
            }
        }
    }

    /**
     * 显示中奖信息
     */
    private void displayWinner(InnerShowDataManager.LotteryWinner winner) {
        if (winner == null) {
            return;
        }

            // 隐藏图片，显示文字信息
        ivContent.setImageDrawable(null);

        // 构建中奖信息
        StringBuilder sb = new StringBuilder();
        sb.append("🎉 恭喜中奖 🎉\n\n");
        sb.append("中奖者：").append(winner.winnerName).append("\n");
        if (winner.winnerDepartment != null && !winner.winnerDepartment.isEmpty()) {
            sb.append("部门：").append(winner.winnerDepartment).append("\n");
        }
        sb.append("奖品：").append(winner.prizeName).append("\n");
        if (winner.lotteryProgram != null) {
            sb.append("抽奖程序：").append(winner.lotteryProgram).append("\n");
        }
        sb.append("第").append(winner.prizeRound).append("轮");

        tvSignature.setText(sb.toString());
        tvSignature.setVisibility(View.VISIBLE);
        tvSignature.setTextSize(40);

        // 标记为已显示
        dataManager.markWinnerAsDisplayed(winner.id);
    }

    /**
     * 切换到抽奖模式
     */
    private void switchToLotteryMode() {
        displayMode = MODE_LOTTERY;
        currentPosition = 0;

        // 停止自动轮播
        if (autoRotate) {
            autoRotate = false;
            stopAutoRotate();
        }

            // 显示最新中奖信息
        if (winnerList != null && !winnerList.isEmpty()) {
            InnerShowDataManager.LotteryWinner winner = winnerList.get(0);
            displayWinner(winner);
            updateInfo();

            // 数字人播报（检查语音配置）
            if (digitalHumanManager != null && isVoiceEnabledForCurrentModule()) {
                String announcement = "恭喜" + winner.winnerName + "获得" + winner.prizeName;
                digitalHumanManager.announceWinner(winner.winnerName, winner.prizeName, new DigitalHumanManager.DigitalHumanCallback() {
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
                        Log.e("InnerActivity", "Digital human error: " + error);
                    }
                });
            }
        }
    }

    /**
         * 切换到生成模式
     */
    private void switchToGenerationMode() {
        displayMode = MODE_GENERATION;
        currentPosition = 0;

        // 显示生成结果
        if (resultList != null && !resultList.isEmpty()) {
            InnerShowDataManager.GenerationResult current = dataManager.getCurrentDisplayImage();
            if (current != null) {
                currentPosition = findPosition(current.id);
                displayResult(current);
            } else {
                displayResult(resultList.get(0));
            }
            updateInfo();

            // 数字人播报（检查语音配置）
            if (digitalHumanManager != null && isVoiceEnabledForCurrentModule()) {
                digitalHumanManager.speak("新的AI百变秀作品已生成", new DigitalHumanManager.DigitalHumanCallback() {
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
                        Log.e("InnerActivity", "Digital human error: " + error);
                    }
                });
            }
        }
    }

    /**
         * 切换到答题中奖模式
     */
    private void switchToQuizMode() {
            displayMode = MODE_LOTTERY; // 复用抽奖模式的显示
        currentPosition = 0;

        // 停止自动轮播
        if (autoRotate) {
            autoRotate = false;
            stopAutoRotate();
        }

            // 显示最新答题中奖信息
        List<InnerShowDataManager.QuizWinner> quizWinners = dataManager.getQuizWinners();
        if (quizWinners != null && !quizWinners.isEmpty()) {
            // 转换为LotteryWinner显示格式
            InnerShowDataManager.QuizWinner quizWinner = quizWinners.get(0);
            displayQuizWinner(quizWinner);
            updateInfo();

            // 数字人播报（检查语音配置）
            if (digitalHumanManager != null && isVoiceEnabledForCurrentModule()) {
                String announcement = "恭喜" + quizWinner.userName + "在知识问答中获得" +
                        (quizWinner.prizeName != null ? quizWinner.prizeName : "奖品") +
                        "，答对了" + quizWinner.correctCount + "道题";
                digitalHumanManager.speak(announcement, new DigitalHumanManager.DigitalHumanCallback() {
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
                        Log.e("InnerActivity", "Digital human error: " + error);
                    }
                });
            }
        }
    }

    /**
         * 显示答题中奖信息
     */
    private void displayQuizWinner(InnerShowDataManager.QuizWinner winner) {
        if (ivContent == null) return;

        // 创建中奖信息图片
        int width = 1920;
        int height = 1080;
        Bitmap bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);
        canvas.drawColor(Color.WHITE);

        Paint paint = new Paint();
        paint.setAntiAlias(true);

        // 绘制背景
        Paint bgPaint = new Paint();
        bgPaint.setColor(Color.parseColor("#4CAF50"));
        canvas.drawRect(0, 0, width, height, bgPaint);

        // 绘制文字
        paint.setColor(Color.WHITE);
        paint.setTextAlign(Paint.Align.CENTER);
        paint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));

        // 标题
        paint.setTextSize(120);
        canvas.drawText("🎉 答题中奖 🎉", width / 2, 300, paint);

        // 奖品等级
        paint.setTextSize(100);
        if (winner.prizeLevel != null) {
            canvas.drawText(winner.prizeLevel, width / 2, 500, paint);
        }

        // 奖品名称
        paint.setTextSize(80);
        if (winner.prizeName != null) {
            canvas.drawText(winner.prizeName, width / 2, 700, paint);
        }

        // 用户名和分数
        paint.setTextSize(60);
        String info = "恭喜 " + winner.userName + " 答对 " + winner.correctCount + " 题！";
        canvas.drawText(info, width / 2, 900, paint);

        ivContent.setImageBitmap(bitmap);
        tvSignature.setText("");
        tvInfo.setText("答题中奖 - " + (winner.prizeName != null ? winner.prizeName : "奖品"));
    }

        // ==================== 网络服务器相关方法 ==================

    /**
         * 如果是主服务器模式，启动网络服务器
     */
    private void startNetworkServerIfNeeded() {
        try {
            if (networkConfigManager == null) {
                Log.w("InnerActivity", "networkConfigManager为null，跳过服务器启动");
                return;
            }

            if (networkConfigManager.isServerMode()) {
                int httpPort = networkConfigManager.getServerPort();
                int wsPort = networkConfigManager.getWsPort();

                if (serverManager == null) {
                    Log.e("InnerActivity", "serverManager为null，无法启动服务器");
                    return;
                }

                boolean success = serverManager.startServer(httpPort, wsPort);

                if (success) {
                    android.util.Log.i("InnerActivity", "内场秀服务器已启动");
                    android.widget.Toast.makeText(this, "服务器已启动: " + serverManager.getServerUrl(),
                            android.widget.Toast.LENGTH_SHORT).show();
                } else {
                        android.widget.Toast.makeText(this, "服务器启动失败",
                            android.widget.Toast.LENGTH_SHORT).show();
                }
            }
        } catch (Exception e) {
                Log.e("InnerActivity", "启动网络服务器失败: " + e.getMessage(), e);
        }
    }

    /**
     * 连接到内场秀服务器（客户端模式）
     */
    private void connectToInnerShowServer() {
        if (!networkConfigManager.isServerMode()) {
            networkClient.connectWebSocket(new InnerShowNetworkClient.WebSocketMessageListener() {
                @Override
                public void onConnected() {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            android.widget.Toast.makeText(InnerActivity.this,
                                        "已连接到内场秀服务器", android.widget.Toast.LENGTH_SHORT).show();
                        }
                    });
                }

                @Override
                public void onMessage(String message) {
                    // 处理WebSocket消息
                    handleWebSocketMessage(message);
                }

                @Override
                public void onDisconnected() {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            android.widget.Toast.makeText(InnerActivity.this,
                                    "与服务器断开连接", android.widget.Toast.LENGTH_SHORT).show();
                        }
                    });
                }

                @Override
                public void onError(String error) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            android.util.Log.e("InnerActivity", "WebSocket错误: " + error);
                        }
                    });
                }
            });
        }
    }

    /**
     * 处理WebSocket消息
     */
    private void handleWebSocketMessage(String message) {
        try {
            JsonObject json = JsonParser.parseString(message).getAsJsonObject();
            String type = json.get("type").getAsString();

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if ("refresh".equals(type)) {
                        refreshData();
                    } else if ("new_image".equals(type)) {
                        refreshData();
                        switchToGenerationMode();
                    } else if ("new_lottery_winner".equals(type)) {
                        refreshData();
                        switchToLotteryMode();
                    } else if ("new_quiz_winner".equals(type)) {
                        refreshData();
                        switchToQuizMode();
                    }
                }
            });
        } catch (Exception e) {
            android.util.Log.e("InnerActivity", "处理WebSocket消息失败", e);
        }
    }

    /**
     * 显示中奖提示
     */
    private void showWinnerToast(String winnerName) {
            // 可以显示一个Toast提示或特殊效果
        android.widget.Toast.makeText(this,
                    "🎉 恭喜 " + winnerName + " 中奖！",
                android.widget.Toast.LENGTH_LONG).show();
    }

    @Override
    protected void showOfflineNotice() {
            // 内场秀不显示离线提示
    }

    @Override
    protected void hideOfflineNotice() {
            // 内场秀不显示离线提示
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopAutoRotate();

            // 安全注销广播接收器
        if (isReceiverRegistered) {
            try {
                unregisterReceiver(updateReceiver);
                isReceiverRegistered = false;
                Log.i("InnerActivity", "广播接收器已注销");
            } catch (Exception e) {
                    Log.e("InnerActivity", "注销广播接收器失败: " + e.getMessage());
            }
        }

        stopBackgroundMusic();

        // 断开WebSocket连接
        if (networkClient != null) {
            try {
                networkClient.disconnectWebSocket();
            } catch (Exception e) {
                Log.e("InnerActivity", "断开WebSocket失败: " + e.getMessage());
            }
        }

            // 如果是主服务器模式，停止服务器
        if (networkConfigManager != null && networkConfigManager.isServerMode()) {
            try {
                if (serverManager != null) {
                    serverManager.stopServer();
                }
            } catch (Exception e) {
                    Log.e("InnerActivity", "停止服务器失败: " + e.getMessage());
            }
        }

        if (executorService != null) {
            executorService.shutdown();
        }
    }

    // ==================== 模块配置相关方法 ====================

    /**
         * 切换到指定模式
     */
    public void switchToModule(InnerShowModule module) {
        if (this.currentModule != module) {
                // 停止当前模块的背景音乐
            stopBackgroundMusic();

            this.currentModule = module;
            applyModuleConfig(module);
            Log.i("InnerActivity", "已切换到模块: " + module.getName());
        }
    }

    /**
     * 应用模块配置
     */
    private void applyModuleConfig(InnerShowModule module) {
        try {
            ConfigManager configManager = ConfigManager.getInstance(this);
            if (configManager == null || module == null) {
                    Log.w("InnerActivity", "ConfigManager或module为null，跳过配置应用");
                return;
            }

            // 1. 应用背景图片/视频
            applyBackgroundMedia(module);

                // 2. 应用背景音乐（如果未静音）
            boolean broadcastMuted = configManager.getInnerShowBroadcastMuted(module.getId());
            if (!broadcastMuted) {
                playBackgroundMusic(module);
            } else {
                    Log.i("InnerActivity", "模块 " + module.getName() + " 广播已静音，不播放背景音");
            }

            // 3. 应用语音配置（在数字人播报时会检查）
            boolean voiceEnabled = configManager.getInnerShowVoiceEnabled(module.getId());
            Log.i("InnerActivity", "模块 " + module.getName() + " 语音: " + (voiceEnabled ? "启用" : "禁用"));
        } catch (Exception e) {
            Log.e("InnerActivity", "应用模块配置失败: " + e.getMessage(), e);
        }
    }

    /**
     * 应用背景媒体
     */
    private void applyBackgroundMedia(InnerShowModule module) {
        try {
            if (backgroundMediaManager == null || module == null) {
                Log.w("InnerActivity", "backgroundMediaManager或module为null，跳过背景媒体应用");
                return;
            }

            // 尝试加载背景视频
            String videoPath = backgroundMediaManager.getBackgroundVideo(module);
            if (videoPath != null && !videoPath.isEmpty()) {
                // TODO: 播放背景视频
                Log.i("InnerActivity", "播放背景视频: " + videoPath);
            } else {
                // 加载背景图片
                String imagePath = backgroundMediaManager.getBackgroundImage(module);
                if (imagePath != null && !imagePath.isEmpty()) {
                    Bitmap bitmap = backgroundMediaManager.loadBackgroundBitmap(module);
                    if (bitmap != null && ivBackground != null) {
                        ivBackground.setImageBitmap(bitmap);
                            Log.i("InnerActivity", "已加载背景图片: " + imagePath);
                    }
                }
            }
        } catch (Exception e) {
            Log.e("InnerActivity", "应用背景媒体失败: " + e.getMessage(), e);
        }
    }

    /**
     * 播放背景音乐
     */
    private void playBackgroundMusic(InnerShowModule module) {
        if (backgroundMediaManager != null) {
            backgroundMediaManager.playBackgroundMusic(module);
        }
    }

    /**
     * 停止背景音乐
     */
    private void stopBackgroundMusic() {
        if (backgroundMediaManager != null) {
            backgroundMediaManager.stopBackgroundMusic();
        }
    }

    /**
         * 检查当前模块是否启用语音
     */
    private boolean isVoiceEnabledForCurrentModule() {
        ConfigManager configManager = ConfigManager.getInstance(this);
        return configManager.getInnerShowVoiceEnabled(currentModule.getId());
    }

    /**
         * 检查当前模块广播是否静音
     */
    private boolean isBroadcastMutedForCurrentModule() {
        ConfigManager configManager = ConfigManager.getInstance(this);
        return configManager.getInnerShowBroadcastMuted(currentModule.getId());
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

