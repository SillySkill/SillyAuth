package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.FrameLayout;

import androidx.recyclerview.widget.RecyclerView;
import androidx.viewpager2.widget.ViewPager2;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.adapter.StyleCarouselAdapter;
import com.jcoding.aiactivity.adapter.BannerPagerAdapter;
import com.jcoding.aiactivity.entity.StyleConfig;
import com.jcoding.aiactivity.entity.BannerItem;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.ConfigSyncManager;
import com.jcoding.aiactivity.manager.DigitalHumanManager;
import com.jcoding.aiactivity.manager.DigitalHumanGestureHelper;
import com.jcoding.aiactivity.manager.VoiceManager;
import com.jcoding.aiactivity.utils.Constants;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;
import java.util.Collections;

/**
 * AI百变秀 - 风格浏览页（全屏轮播模式）
 * 支持自动轮播展示所有风格
 */
public class PhotoStyleActivity extends BaseActivity implements
        com.jcoding.aiactivity.widget.DigitalHumanView.TripleTapListener {

    // 轮播相关
    private ViewPager2 viewPager;
    private StyleCarouselAdapter carouselAdapter;
    private TextView tvStyleName;
    private Button btnStart;
    private Button btnBackToMain;
    private TextView tvOfflineMode;

    // Banner轮播相关
    private ViewPager2 bannerViewPager;
    private BannerPagerAdapter bannerAdapter;
    private Handler bannerHandler = new Handler(Looper.getMainLooper());
    private Runnable bannerRunnable;
    private int bannerInterval = 10000; // Banner轮播间隔10秒（给视频足够时间播放）

    // 数字人显示相关
    private com.jcoding.aiactivity.widget.DigitalHumanView digitalHumanView;
    private Button btnToggleDigitalHumanLock; // 数字人锁定/解锁控制按钮
    private DigitalHumanManager digitalHumanManager;
    private VoiceManager voiceManager; // 语音管理器

    // 数字人三击启动相关
    private int digitalHumanTapCount = 0;
    private static final int REQUIRED_TAPS = 3;
    private static final long TAP_TIMEOUT = 2000; // 2秒内点击有效
    private Handler tapCountHandler = new Handler(Looper.getMainLooper());

    // 图层切换相关
    private View layerSwitchTrigger;
    private int layerSwitchTapCount = 0;
    private static final int LAYER_SWITCH_TAPS = 3;
    private static final long LAYER_SWITCH_TIMEOUT = 2000;
    private Handler layerSwitchHandler = new Handler(Looper.getMainLooper());

    // 图层控制开关状态
    private boolean digitalHumanLayerEnabled = false; // 数字人图层是否在最上面
    private boolean buttonLayerEnabled = true; // 按钮图层是否在最上面

    // 语音引导相关
    private List<String> guidanceMessages; // 引导语列表
    private Handler guidanceHandler = new Handler(Looper.getMainLooper());
    private Runnable guidanceRunnable;
    private int guidanceInterval = 15000; // 引导间隔15秒
    private Random random = new Random();

    private List<StyleConfig> styleList;
    private List<com.jcoding.aiactivity.entity.BannerItem> bannerList;
    private StyleConfig selectedStyle;
    private int currentPosition = 0;
    private boolean autoRotate = false; // 默认自动轮播
    private boolean isPaused = false; // 是否暂停
    private Handler autoRotateHandler = new Handler(Looper.getMainLooper());
    private Runnable autoRotateRunnable;
    private int carouselInterval = 5000; // 默认5秒
    private boolean isAutoScrolling = false; // 标记是否正在自动滚动

    // 二维码上传轮询相关
    private boolean isPollingUpload = false;
    private Handler uploadPollingHandler;
    private Runnable uploadPollingRunnable;
    private long uploadCheckStartTime = 0;
    private String lastProcessedFileId = null;
    private String currentSessionId;  // 当前上传会话ID，用于标识唯一的一次扫码机会

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_photo_style_carousel);

        initViews();

        // 检查远程配置更新（异步，不阻塞UI）
        checkForConfigUpdates();

        loadBanners();
        loadStyles();
        setupListeners();
        startGuidance(); // 启动语音引导
    }

    private void initViews() {
        viewPager = findViewById(R.id.viewpager_styles);
        tvStyleName = findViewById(R.id.tv_style_name);
        btnStart = findViewById(R.id.btn_start);
        btnBackToMain = findViewById(R.id.btn_back_to_main);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        // Banner轮播初始化
        bannerViewPager = findViewById(R.id.viewpager_banner);

        // 加载背景遮罩图片
        loadBackgroundMask();

        // 数字人初始化（使用DigitalHumanView组件）
        digitalHumanView = findViewById(R.id.digital_human_view);
        btnToggleDigitalHumanLock = findViewById(R.id.btn_toggle_digital_human_lock);
        digitalHumanManager = DigitalHumanManager.getInstance(this);
        setupDigitalHuman();

        // 设置数字人三击监听器
        if (digitalHumanView != null) {
            digitalHumanView.setTripleTapListener(this);
        }

        // 隐藏数字人锁定按钮（改用三击启动）
        if (btnToggleDigitalHumanLock != null) {
            btnToggleDigitalHumanLock.setVisibility(View.GONE);
        }

        // 初始化图层切换功能
        layerSwitchTrigger = findViewById(R.id.layer_switch_trigger);
        setupLayerSwitch();

        // 初始化语音管理器
        voiceManager = VoiceManager.getInstance(this);
        initGuidanceMessages();

        // 从配置读取轮播间隔（默认5秒）
        carouselInterval = configManager.getAiShowCarouselInterval();
        if (carouselInterval < 1000) {
            carouselInterval = 5000; // 最小1秒
        }
        android.util.Log.d("PhotoStyleActivity", "风格轮播间隔: " + carouselInterval + "ms");

        styleList = new ArrayList<>();
        bannerList = new ArrayList<>();

        // 设置ViewPager2
        viewPager.registerOnPageChangeCallback(new ViewPager2.OnPageChangeCallback() {
            @Override
            public void onPageSelected(int position) {
                android.util.Log.d("PhotoStyleActivity", "onPageSelected: 页面切换到位置 " + position + ", autoRotate=" + autoRotate + ", isPaused=" + isPaused + ", isAutoScrolling=" + isAutoScrolling);

                currentPosition = position;
                updateStyleName(position);
                android.util.Log.d("PhotoStyleActivity", "切换到风格: " + position);

                // 只在用户手动滑动时重置自动轮播计时器（不是自动滚动时）
                if (autoRotate && !isPaused && !isAutoScrolling) {
                    android.util.Log.d("PhotoStyleActivity", "onPageSelected: 用户手动滑动，重置轮播计时器");
                    stopAutoRotate();
                    startAutoRotate();
                } else if (isAutoScrolling) {
                    android.util.Log.d("PhotoStyleActivity", "onPageSelected: 自动滚动，不重置轮播计时器");
                }
            }
        });

        // 启动自动轮播
        autoRotate = true;
        startAutoRotate();
    }

    private void setupListeners() {
        // 返回主页面按钮
        btnBackToMain.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopGuidance();
                finish();
            }
        });

        // 开始生成按钮 - 长按拖拽功能
        setupDraggableButton(btnStart);

        // 开始生成按钮 - 点击功能
        btnStart.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 停止语音引导
                stopGuidance();

                if (styleList == null || styleList.isEmpty()) {
                    showToast("没有可用的风格");
                    return;
                }
                selectedStyle = styleList.get(currentPosition);
                navigateToVerification();
            }
        });
    }

    /**
     * 设置按钮支持长按拖拽（带边界限制）
     */
    private void setupDraggableButton(final Button button) {
        button.setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View v) {
                showToast("长按成功，可拖拽移动位置");
                return true;
            }
        });

        button.setOnTouchListener(new View.OnTouchListener() {
            private float dX, dY;
            private int lastAction;
            private boolean isDragging = false;
            private long downTime = 0;

            @Override
            public boolean onTouch(View v, MotionEvent event) {
                // Get screen dimensions
                android.view.Display display = getWindowManager().getDefaultDisplay();
                android.graphics.Point size = new android.graphics.Point();
                display.getSize(size);
                int screenWidth = size.x;
                int screenHeight = size.y;

                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        downTime = System.currentTimeMillis();
                        dX = v.getX() - event.getRawX();
                        dY = v.getY() - event.getRawY();
                        lastAction = MotionEvent.ACTION_DOWN;
                        return false; // Let click event continue

                    case MotionEvent.ACTION_MOVE:
                        // Allow dragging after 500ms long press
                        if (System.currentTimeMillis() - downTime > 500) {
                            isDragging = true;

                            // Calculate new position
                            float newX = event.getRawX() + dX;
                            float newY = event.getRawY() + dY;

                            // Get button dimensions
                            float buttonWidth = button.getWidth();
                            float buttonHeight = button.getHeight();

                            // Constrain to screen bounds
                            // Keep at least 50% of button visible
                            newX = Math.max(-buttonWidth * 0.5f, Math.min(newX, screenWidth - buttonWidth * 0.5f));
                            newY = Math.max(-buttonHeight * 0.5f, Math.min(newY, screenHeight - buttonHeight * 0.5f));

                            v.animate()
                                    .x(newX)
                                    .y(newY)
                                    .setDuration(0)
                                    .start();
                            lastAction = MotionEvent.ACTION_MOVE;
                            return true;
                        }
                        return false;

                    case MotionEvent.ACTION_UP:
                        if (isDragging) {
                            isDragging = false;
                            return true; // Consume event to avoid triggering click
                        }
                        if (lastAction == MotionEvent.ACTION_DOWN) {
                            return false; // This is a click, let OnClickListener handle it
                        }
                        return true;

                    default:
                        return false;
                }
            }
        });
    }

    /**
     * 检查远程配置更新
     */
    private void checkForConfigUpdates() {
        ConfigSyncManager syncManager = ConfigSyncManager.getInstance(this);
        syncManager.checkAndUpdate(new ConfigSyncManager.ConfigUpdateCallback() {
            @Override
            public void onSuccess(boolean updated, String message) {
                android.util.Log.i("PhotoStyleActivity", "配置更新检查: " + message);
                if (updated) {
                    // 配置已更新，重新加载风格列表
                    runOnUiThread(() -> {
                        showToast("配置已更新");
                        loadStyles();
                        loadBanners();
                    });
                }
            }

            @Override
            public void onError(String error) {
                android.util.Log.w("PhotoStyleActivity", "配置更新检查失败: " + error);
                // 不显示错误提示，静默失败
            }

            @Override
            public void onProgress(int progress, String message) {
                android.util.Log.d("PhotoStyleActivity", "配置更新进度: " + progress + "% - " + message);
            }
        });
    }

    /**
     * 切换暂停/继续轮播
     */
    private void togglePause() {
        isPaused = !isPaused;
        if (isPaused) {
            stopAutoRotate();
            showToast("已暂停");
        } else {
            startAutoRotate();
            showToast("继续轮播");
        }
    }

    /**
     * 加载风格列表
     */
    private void loadStyles() {
        android.util.Log.d("PhotoStyleActivity", "loadStyles: Starting to load styles");
        styleList.clear();
        styleList.addAll(configManager.getStyleConfigs());
        android.util.Log.d("PhotoStyleActivity", "loadStyles: Loaded " + styleList.size() + " styles");

        if (!styleList.isEmpty()) {
            // 设置适配器
            carouselAdapter = new StyleCarouselAdapter(this, styleList,
                new StyleCarouselAdapter.OnItemClickListener() {
                    @Override
                    public void onItemClick(StyleConfig style, int position) {
                        viewPager.setCurrentItem(position, true);
                    }
                });
            viewPager.setAdapter(carouselAdapter);

            // 默认选中第一个
            selectedStyle = styleList.get(0);
            updateStyleName(0);

            android.util.Log.d("PhotoStyleActivity", "loadStyles: Setup completed successfully");
        } else {
            android.util.Log.e("PhotoStyleActivity", "loadStyles: No styles found!");
            showToast("未找到可用的风格配置，请检查style/style.json文件");
        }
    }

    /**
     * 更新风格名称显示
     */
    private void updateStyleName(int position) {
        if (styleList != null && position < styleList.size()) {
            StyleConfig style = styleList.get(position);
            tvStyleName.setText(style.getName());
        }
    }

    /**
     * 开始自动轮播
     */
    private void startAutoRotate() {
        android.util.Log.d("PhotoStyleActivity", "startAutoRotate: 开始轮播，当前位置=" + currentPosition + ", 间隔=" + carouselInterval + "ms");

        if (autoRotateRunnable != null) {
            autoRotateHandler.removeCallbacks(autoRotateRunnable);
            android.util.Log.d("PhotoStyleActivity", "startAutoRotate: 移除旧的轮播任务");
        }

        autoRotateRunnable = new Runnable() {
            @Override
            public void run() {
                isAutoScrolling = true; // 标记为自动滚动
                int nextPosition = currentPosition + 1;
                if (nextPosition >= styleList.size()) {
                    nextPosition = 0; // 循环到第一个
                }
                android.util.Log.d("PhotoStyleActivity", "autoRotate: 自动切换到位置 " + nextPosition + " (从位置 " + currentPosition + " 切换)");
                viewPager.setCurrentItem(nextPosition, true);
                isAutoScrolling = false; // 切换完成，清除标记
                autoRotateHandler.postDelayed(this, carouselInterval);
            }
        };

        autoRotateHandler.postDelayed(autoRotateRunnable, carouselInterval);
        android.util.Log.d("PhotoStyleActivity", "startAutoRotate: 已安排轮播任务，" + carouselInterval + "ms后执行");
    }

    /**
     * 停止自动轮播
     */
    private void stopAutoRotate() {
        android.util.Log.d("PhotoStyleActivity", "stopAutoRotate: 停止轮播，当前位置=" + currentPosition);
        if (autoRotateRunnable != null) {
            autoRotateHandler.removeCallbacks(autoRotateRunnable);
            android.util.Log.d("PhotoStyleActivity", "stopAutoRotate: 已移除轮播任务");
        }
    }

    /**
     * 加载Banner素材
     */
    private void loadBanners() {
        android.util.Log.d("PhotoStyleActivity", "loadBanners: Starting to load banners");

        try {
            // 获取banner目录下的所有文件
            String[] files = getAssets().list("banner");

            if (files == null || files.length == 0) {
                android.util.Log.w("PhotoStyleActivity", "No banner files found in assets/banner");
                // 创建默认banner
                createDefaultBanner();
                return;
            }

            // 对文件排序
            java.util.Arrays.sort(files);

            android.util.Log.d("PhotoStyleActivity", "Found " + files.length + " files in banner directory");

            bannerList.clear();
            for (String fileName : files) {
                // 跳过README文件
                if (fileName.equalsIgnoreCase("README.txt") || fileName.equalsIgnoreCase("README.md")) {
                    continue;
                }

                String filePath = "banner/" + fileName;
                android.util.Log.d("PhotoStyleActivity", "Processing file: " + fileName);

                // 根据文件扩展名判断类型
                if (fileName.toLowerCase().endsWith(".jpg") ||
                    fileName.toLowerCase().endsWith(".jpeg") ||
                    fileName.toLowerCase().endsWith(".png")) {
                    // 图片文件
                    bannerList.add(new BannerItem(filePath, BannerItem.TYPE_IMAGE, 5000));
                    android.util.Log.d("PhotoStyleActivity", "Added image banner: " + fileName);

                } else if (fileName.toLowerCase().endsWith(".mp4") ||
                           fileName.toLowerCase().endsWith(".3gp") ||
                           fileName.toLowerCase().endsWith(".webm") ||
                           fileName.toLowerCase().endsWith(".m4v") ||
                           fileName.toLowerCase().endsWith(".mkv") ||
                           fileName.toLowerCase().endsWith(".avi")) {
                    // 视频文件
                    bannerList.add(new BannerItem(filePath, BannerItem.TYPE_VIDEO));
                    android.util.Log.d("PhotoStyleActivity", "Added video banner: " + fileName);
                }
            }

            // 如果没有找到有效的banner文件，创建默认的
            if (bannerList.isEmpty()) {
                android.util.Log.w("PhotoStyleActivity", "No valid banner files found, creating default banner");
                createDefaultBanner();
                return;
            }

            // 设置适配器
            bannerAdapter = new BannerPagerAdapter(this, bannerList);
            bannerViewPager.setAdapter(bannerAdapter);

            // 设置预加载所有页面（确保视频不会因视图回收而停止播放）
            // 设置为banner总数，这样所有banner视图都会保持在内存中
            bannerViewPager.setOffscreenPageLimit(bannerList.size());

            // 设置页面切换回调
            bannerViewPager.registerOnPageChangeCallback(new ViewPager2.OnPageChangeCallback() {
                @Override
                public void onPageSelected(int position) {
                    // 调整页面图层：当前页在最上层
                    RecyclerView recyclerView = (RecyclerView) bannerViewPager.getChildAt(0);
                    if (recyclerView != null) {
                        for (int i = 0; i < bannerList.size(); i++) {
                            RecyclerView.ViewHolder holder = recyclerView.findViewHolderForAdapterPosition(i);
                            if (holder instanceof BannerPagerAdapter.ViewHolder) {
                                BannerPagerAdapter.ViewHolder bannerHolder = (BannerPagerAdapter.ViewHolder) holder;
                                if (bannerHolder.itemView != null) {
                                    if (i == position) {
                                        // 当前页：高elevation
                                        bannerHolder.itemView.setElevation(10);
                                    } else {
                                        // 其他页：低elevation
                                        bannerHolder.itemView.setElevation(0);
                                    }
                                }
                            }
                        }
                    }

                    // 确保切换到的页面的视频正在播放
                    if (bannerAdapter != null && bannerList != null && !bannerList.isEmpty()) {
                        BannerItem item = bannerList.get(position);
                        if (item.isVideo()) {
                            android.util.Log.d("PhotoStyleActivity", "确保position " + position + " 的视频正在播放");
                            // 通过RecyclerView找到对应位置的ViewHolder并启动视频
                            if (recyclerView != null) {
                                RecyclerView.ViewHolder holder = recyclerView.findViewHolderForAdapterPosition(position);
                                if (holder instanceof BannerPagerAdapter.ViewHolder) {
                                    BannerPagerAdapter.ViewHolder bannerHolder = (BannerPagerAdapter.ViewHolder) holder;
                                    if (bannerHolder.videoView != null) {
                                        bannerHolder.videoView.start();
                                        android.util.Log.d("PhotoStyleActivity", "已启动position " + position + " 的视频");
                                    }
                                }
                            }
                        }
                    }
                    // 重置自动轮播计时器
                    stopBannerAutoRotate();
                    startBannerAutoRotate();
                }
            });

            // 启动自动轮播
            startBannerAutoRotate();

            android.util.Log.d("PhotoStyleActivity", "Banner setup completed, total: " + bannerList.size());

        } catch (IOException e) {
            android.util.Log.e("PhotoStyleActivity", "Error listing banner files", e);
            createDefaultBanner();
        }
    }

    /**
     * 创建默认Banner（用于测试）
     */
    private void createDefaultBanner() {
        android.util.Log.d("PhotoStyleActivity", "Creating default banner for testing");

        bannerList.clear();

        // 创建3个默认的图片banner（使用drawable资源）
        // 注意：这里使用特殊标记，在adapter中会显示默认背景
        bannerList.add(new BannerItem("default_1", BannerItem.TYPE_IMAGE, 5000));
        bannerList.add(new BannerItem("default_2", BannerItem.TYPE_IMAGE, 5000));
        bannerList.add(new BannerItem("default_3", BannerItem.TYPE_IMAGE, 5000));

        // 设置适配器
        bannerAdapter = new BannerPagerAdapter(this, bannerList);
        bannerViewPager.setAdapter(bannerAdapter);

        // 设置页面切换回调
        bannerViewPager.registerOnPageChangeCallback(new ViewPager2.OnPageChangeCallback() {
            @Override
            public void onPageSelected(int position) {
                stopBannerAutoRotate();
                startBannerAutoRotate();
            }
        });

        // 启动自动轮播
        startBannerAutoRotate();

        android.util.Log.d("PhotoStyleActivity", "Default banner created, total: " + bannerList.size());
    }

    /**
     * 开始Banner自动轮播
     */
    private void startBannerAutoRotate() {
        android.util.Log.d("PhotoStyleActivity", "startBannerAutoRotate: 启动banner轮播，间隔=" + bannerInterval + "ms");
        if (bannerRunnable != null) {
            bannerHandler.removeCallbacks(bannerRunnable);
        }

        bannerRunnable = new Runnable() {
            @Override
            public void run() {
                if (bannerList == null || bannerList.isEmpty()) {
                    android.util.Log.w("PhotoStyleActivity", "Banner轮播: banner列表为空，停止轮播");
                    return;
                }

                int currentPosition = bannerViewPager.getCurrentItem();
                int nextPosition = currentPosition + 1;
                if (nextPosition >= bannerList.size()) {
                    nextPosition = 0; // 循环到第一个
                }
                android.util.Log.d("PhotoStyleActivity", "Banner轮播: " + currentPosition + " -> " + nextPosition);
                bannerViewPager.setCurrentItem(nextPosition, true);
                // 不在这里postDelayed，而是依赖onPageSelected回调重新调度
            }
        };

        bannerHandler.postDelayed(bannerRunnable, bannerInterval);
    }

    /**
     * 停止Banner自动轮播
     */
    private void stopBannerAutoRotate() {
        if (bannerRunnable != null) {
            bannerHandler.removeCallbacks(bannerRunnable);
        }
    }

    /**
     * 加载背景遮罩图片
     */
    private void loadBackgroundMask() {
        android.widget.ImageView ivBackgroundMask = findViewById(R.id.iv_background_mask);
        if (ivBackgroundMask != null) {
            try {
                // 从assets加载背景图片
                java.io.InputStream inputStream = getAssets().open("style/background/styleBk.png");
                android.graphics.Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(inputStream);
                inputStream.close();

                if (bitmap != null) {
                    ivBackgroundMask.setImageBitmap(bitmap);
                    android.util.Log.d("PhotoStyleActivity", "背景遮罩图片加载成功");
                } else {
                    android.util.Log.e("PhotoStyleActivity", "背景遮罩图片解码失败");
                }
            } catch (java.io.IOException e) {
                android.util.Log.e("PhotoStyleActivity", "加载背景遮罩图片失败: " + e.getMessage());
            }
        }
    }

    /**
     * 设置数字人显示
     */
    private void setupDigitalHuman() {
        try {
            if (digitalHumanView != null) {
                // 检查style模块是否启用数字人
                boolean isDigitalHumanEnabled = com.jcoding.aiactivity.manager.ConfigManager.getInstance(this)
                        .isDigitalHumanEnabledForModule("ai_show");

                android.util.Log.d("PhotoStyleActivity", "style模块数字人启用状态: " + isDigitalHumanEnabled);

                if (!isDigitalHumanEnabled) {
                    // 如果禁用，隐藏数字人
                    digitalHumanView.setVisibility(View.GONE);
                    android.util.Log.d("PhotoStyleActivity", "style模块数字人已禁用，隐藏数字人视图");
                    return;
                }

                // 设置模块ID为aishow，以便使用quiz的配置（3倍默认缩放，无限放大）
                digitalHumanView.setModuleId("aishow");

                // 加载数字人（使用实际的项目ID）
                digitalHumanView.loadDigitalHuman("JC2026012100001");
                digitalHumanView.setVisibility(View.VISIBLE);
                android.util.Log.d("PhotoStyleActivity", "数字人初始化成功");

                // 延迟设置锁定状态，确保在restoreDigitalHumanState之后
                digitalHumanView.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        // 设置为锁定状态（默认禁用拖拽）
                        digitalHumanView.setDragAndScaleEnabled(false);

                        // 设置初始elevation为锁定状态（数字人在其他图层之下）
                        digitalHumanView.setElevation(1);
                        android.util.Log.d("PhotoStyleActivity", "数字人初始状态: 锁定，elevation=1dp");
                    }
                }, 200); // 延迟200ms，确保restoreDigitalHumanState已完成
            } else {
                android.util.Log.e("PhotoStyleActivity", "数字人视图未找到");
            }
        } catch (Exception e) {
            android.util.Log.e("PhotoStyleActivity", "初始化数字人失败", e);
        }
    }

    /**
     * 设置锁定控制按钮
     */
    private void setupLockButton() {
        if (btnToggleDigitalHumanLock == null) {
            return;
        }

        btnToggleDigitalHumanLock.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleDigitalHumanLock();
            }
        });
    }

    /**
     * 切换数字人锁定/解锁状态
     */
    private void toggleDigitalHumanLock() {
        if (digitalHumanView == null) {
            android.util.Log.w("PhotoStyleActivity", "digitalHumanView为null，无法切换锁定状态");
            return;
        }

        boolean currentState = digitalHumanView.isDragAndScaleEnabled();
        boolean newState = !currentState;

        android.util.Log.d("PhotoStyleActivity", "切换数字人锁定状态: " + (currentState ? "解锁→锁定" : "锁定→解锁"));

        // 先设置拖拽/缩放状态（这会禁用/启用触摸事件）
        digitalHumanView.setDragAndScaleEnabled(newState);

        // 动态调整elevation
        if (newState) {
            // 解锁状态：数字人在其他图层之上，可以拖拽
            android.util.Log.d("PhotoStyleActivity", "设置解锁状态：数字人elevation=5");

            digitalHumanView.setElevation(5);

            btnToggleDigitalHumanLock.setText("🔓");
            showToast("数字人已解锁\n可拖拽调整位置和大小");
        } else {
            // 锁定状态：数字人在其他图层之下
            android.util.Log.d("PhotoStyleActivity", "设置锁定状态：数字人elevation=1");

            digitalHumanView.setElevation(1);

            btnToggleDigitalHumanLock.setText("🔒");
            showToast("数字人已锁定\n位置已固定");
        }

        android.util.Log.d("PhotoStyleActivity", "数字人当前位置: X=" + digitalHumanView.getX() + ", Y=" + digitalHumanView.getY());
        android.util.Log.d("PhotoStyleActivity", "数字人当前缩放: " + digitalHumanView.getScaleX());
    }

    /**
     * 跳转到验证页（根据设置选择相机或扫码上传）
     */
    private void navigateToVerification() {
        android.util.Log.d("PhotoStyleActivity", "navigateToVerification: Starting");

        if (selectedStyle == null) {
            android.util.Log.e("PhotoStyleActivity", "navigateToVerification: No style selected");
            showToast("请先选择风格");
            return;
        }

        android.util.Log.d("PhotoStyleActivity", "navigateToVerification: Selected style = " + selectedStyle.getName());

        // 停止轮播，保持当前选定的风格位置
        stopAutoRotate();
        android.util.Log.d("PhotoStyleActivity", "navigateToVerification: 已停止轮播，当前位置=" + currentPosition);

        // 检查拍照方式设置
        int photoSourceMode = com.jcoding.aiactivity.utils.PreferenceUtils.getInt(
                this, Constants.PREF_PHOTO_SOURCE_MODE, Constants.PHOTO_SOURCE_UPLOAD);

        if (photoSourceMode == Constants.PHOTO_SOURCE_UPLOAD) {
            // 扫码上传模式 - 直接显示二维码对话框
            android.util.Log.d("PhotoStyleActivity", "扫码上传模式，显示二维码对话框");
            showQRCodeUploadDialog();
        } else {
            // 本机摄像头模式 - 跳转到预览页面
            android.util.Log.d("PhotoStyleActivity", "本机摄像头模式，跳转到预览页面");
            try {
                Intent intent = new Intent(this, PreviewActivity.class);
                intent.putExtra(Constants.EXTRA_STYLE_ID, selectedStyle.getStyleId());
                intent.putExtra(Constants.EXTRA_MODE, Constants.MODE_CAMERA);
                startActivity(intent);
            } catch (Exception e) {
                android.util.Log.e("PhotoStyleActivity", "navigateToVerification: Error starting activity", e);
                showToast("启动相机失败: " + e.getMessage());
            }
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

    @Override
    protected void onPause() {
        super.onPause();
        // 离开页面时暂停轮播，保持当前选定的风格位置
        android.util.Log.d("PhotoStyleActivity", "onPause: 暂停轮播，当前位置=" + currentPosition);
        stopAutoRotate();
    }

    @Override
    protected void onResume() {
        super.onResume();
        // 返回页面时恢复轮播，从当前位置继续
        android.util.Log.d("PhotoStyleActivity", "onResume: 恢复轮播，当前位置=" + currentPosition);
        if (autoRotate) {
            startAutoRotate();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopPollingUpload(); // 停止轮询上传
        stopAutoRotate();
        stopBannerAutoRotate();
        stopGuidance(); // 停止语音引导
        // bannerAdapter的视频会随着视图销毁自动清理，无需手动停止
    }

    /**
     * 初始化语音引导语列表
     */
    private void initGuidanceMessages() {
        guidanceMessages = Arrays.asList(
            "欢迎来到AI百变秀，点击拍照按钮，开始您的美照之旅吧",
            "选择您喜欢的风格，拍照后生成专属的AI美照",
            "快来试试吧，多种风格任您选择，一键生成精美照片",
            "点击拍照变一下，记录美好瞬间，创造独特回忆",
            "我们为您准备了丰富的风格模板，快来体验吧",
            "AI智能美化，让您瞬间变身，快来拍照试试吧",
            "每一种风格都是一次新的冒险，快来看看吧",
            "不要错过这个展示自我的机会，点击拍照开始创作"
        );
    }

    /**
     * 启动语音引导
     */
    private void startGuidance() {
        if (guidanceRunnable != null) {
            guidanceHandler.removeCallbacks(guidanceRunnable);
        }

        guidanceRunnable = new Runnable() {
            @Override
            public void run() {
                // 随机选择一条引导语
                int index = random.nextInt(guidanceMessages.size());
                String message = guidanceMessages.get(index);

                android.util.Log.d("PhotoStyleActivity", "播放语音引导: " + message);

                // 数字人说话
                if (digitalHumanView != null && digitalHumanManager != null) {
                    // 开始说话动画（显示talk.gif）
                    digitalHumanView.startTalking();

                    digitalHumanManager.speak(message, new DigitalHumanManager.DigitalHumanCallback() {
                        @Override
                        public void onSpeakStart(String gifPath) {
                            android.util.Log.d("PhotoStyleActivity", "数字人开始说话: " + gifPath);
                        }

                        @Override
                        public void onComplete() {
                            android.util.Log.d("PhotoStyleActivity", "语音播报完成");
                            // 语音播报完成，停止说话动画（恢复shutup.gif）
                            if (digitalHumanView != null) {
                                digitalHumanView.stopTalking();
                            }
                        }

                        @Override
                        public void onError(String error) {
                            android.util.Log.e("PhotoStyleActivity", "语音播报错误: " + error);
                            // 出错时也要停止说话动画
                            if (digitalHumanView != null) {
                                digitalHumanView.stopTalking();
                            }
                        }
                    });
                }

                // 继续下一次引导
                guidanceHandler.postDelayed(this, guidanceInterval);
            }
        };

        // 延迟3秒后开始第一次引导
        guidanceHandler.postDelayed(guidanceRunnable, 3000);
        android.util.Log.d("PhotoStyleActivity", "语音引导已启动，间隔: " + guidanceInterval + "ms");
    }

    /**
     * 停止语音引导
     */
    private void stopGuidance() {
        if (guidanceRunnable != null) {
            guidanceHandler.removeCallbacks(guidanceRunnable);
            guidanceRunnable = null;
        }

        // 停止语音播报
        if (voiceManager != null) {
            voiceManager.stopSpeaking();
        }

        android.util.Log.d("PhotoStyleActivity", "语音引导已停止");
    }

    /**
     * 显示二维码上传对话框
     */
    private void showQRCodeUploadDialog() {
        android.util.Log.d("PhotoStyleActivity", "显示二维码上传对话框");

        androidx.appcompat.app.AlertDialog.Builder builder = new androidx.appcompat.app.AlertDialog.Builder(this);
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_qrcode_upload, null);

        ImageView ivQRCode = dialogView.findViewById(R.id.iv_qrcode);
        TextView tvHint = dialogView.findViewById(R.id.tv_hint);
        TextView tvStatus = dialogView.findViewById(R.id.tv_status);
        Button btnClose = dialogView.findViewById(R.id.btn_close);

        // 先在主线程生成sessionId，避免竞态条件
        currentSessionId = java.util.UUID.randomUUID().toString();
        android.util.Log.d("PhotoStyleActivity", "生成session_id: " + currentSessionId);

        // 生成二维码
        generateQRCode(ivQRCode, tvHint);

        androidx.appcompat.app.AlertDialog dialog = builder.setView(dialogView).create();
        dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        dialog.getWindow().setDimAmount(0.5f); // 50%透明度
        dialog.setCanceledOnTouchOutside(false);

        dialog.show();

        // 开始轮询上传状态
        startPollingUpload(tvStatus, dialog);

        // 关闭按钮
        btnClose.setOnClickListener(v -> {
            stopPollingUpload();
            dialog.dismiss();
            // 恢复轮播
            if (autoRotate) {
                android.util.Log.d("PhotoStyleActivity", "二维码对话框关闭，恢复轮播");
                startAutoRotate();
            }
        });
    }

    /**
     * 获取适合当前屏幕的二维码尺寸
     * 根据屏幕尺寸（英寸）动态调整二维码大小
     * @return 二维码边长（像素）
     */
    private int getQRCodeSizeForScreen() {
        android.util.DisplayMetrics metrics = new android.util.DisplayMetrics();
        getWindowManager().getDefaultDisplay().getMetrics(metrics);

        // 计算屏幕对角线（英寸）
        double screenWidthInch = metrics.widthPixels / metrics.xdpi;
        double screenHeightInch = metrics.heightPixels / metrics.ydpi;
        double diagonalInch = Math.sqrt(Math.pow(screenWidthInch, 2) + Math.pow(screenHeightInch, 2));

        android.util.Log.d("PhotoStyleActivity", "屏幕尺寸: " + String.format("%.1f", diagonalInch) + "英寸");
        android.util.Log.d("PhotoStyleActivity", "屏幕分辨率: " + metrics.widthPixels + "x" + metrics.heightPixels);

        // 根据屏幕尺寸确定二维码大小
        int qrSize;
        if (diagonalInch >= 85.0) {
            // 85寸及以上大屏
            qrSize = 250;
            android.util.Log.d("PhotoStyleActivity", "检测到85寸+大屏，二维码大小: " + qrSize);
        } else if (diagonalInch >= 75.0) {
            // 75寸大屏
            qrSize = 280;
            android.util.Log.d("PhotoStyleActivity", "检测到75寸大屏，二维码大小: " + qrSize);
        } else if (diagonalInch >= 65.0) {
            // 65寸大屏
            qrSize = 320;
            android.util.Log.d("PhotoStyleActivity", "检测到65寸大屏，二维码大小: " + qrSize);
        } else if (diagonalInch >= 55.0) {
            // 55寸大屏
            qrSize = 360;
            android.util.Log.d("PhotoStyleActivity", "检测到55寸大屏，二维码大小: " + qrSize);
        } else {
            // 普通屏幕（平板、小屏等）
            qrSize = 400;
            android.util.Log.d("PhotoStyleActivity", "检测到普通屏幕，二维码大小: " + qrSize);
        }

        return qrSize;
    }

    /**
     * 生成二维码
     */
    private void generateQRCode(ImageView imageView, TextView hintTextView) {
        new Thread(() -> {
            try {
                // currentSessionId 已在主线程中生成，避免竞态条件
                long timestamp = System.currentTimeMillis();

                // 获取当前选中的styleId
                String currentStyleId = selectedStyle != null ? selectedStyle.getStyleId() : "";

                // 构建带参数的上传URL（包含style_id）
                String uploadUrl = "https://www.jcoding.chat/upload?session_id=" + currentSessionId
                        + "&timestamp=" + timestamp
                        + "&style_id=" + currentStyleId;
                android.util.Log.d("PhotoStyleActivity", "生成二维码: " + uploadUrl);
                android.util.Log.d("PhotoStyleActivity", "session_id: " + currentSessionId);
                android.util.Log.d("PhotoStyleActivity", "styleId: " + currentStyleId);

                // 获取适合当前屏幕的二维码尺寸
                int qrSize = getQRCodeSizeForScreen();

                // 使用ZXing生成二维码
                com.google.zxing.Writer writer = new com.google.zxing.qrcode.QRCodeWriter();
                String charset = "UTF-8";
                com.google.zxing.common.BitMatrix bitMatrix = writer.encode(uploadUrl,
                        com.google.zxing.BarcodeFormat.QR_CODE, qrSize, qrSize);

                int width = bitMatrix.getWidth();
                int height = bitMatrix.getHeight();
                int[] pixels = new int[width * height];

                for (int y = 0; y < height; y++) {
                    for (int x = 0; x < width; x++) {
                        pixels[y * width + x] = bitMatrix.get(x, y) ?
                                android.graphics.Color.BLACK : android.graphics.Color.WHITE;
                    }
                }

                android.graphics.Bitmap bitmap = android.graphics.Bitmap.createBitmap(width, height, android.graphics.Bitmap.Config.ARGB_8888);
                bitmap.setPixels(pixels, 0, width, 0, 0, width, height);

                // 在主线程设置图片并调整ImageView尺寸
                runOnUiThread(() -> {
                    // 动态调整ImageView尺寸以匹配二维码大小
                    android.view.ViewGroup.LayoutParams params = imageView.getLayoutParams();
                    params.width = qrSize;
                    params.height = qrSize;
                    imageView.setLayoutParams(params);

                    imageView.setImageBitmap(bitmap);
                    hintTextView.setText("请使用手机扫描二维码上传照片");

                    android.util.Log.d("PhotoStyleActivity", "二维码已生成并设置ImageView尺寸: " + qrSize + "x" + qrSize);
                });

            } catch (Exception e) {
                android.util.Log.e("PhotoStyleActivity", "生成二维码失败", e);
                runOnUiThread(() -> {
                    hintTextView.setText("二维码生成失败，请重试");
                });
            }
        }).start();
    }

    /**
     * 开始轮询上传状态
     */
    private void startPollingUpload(TextView statusView, androidx.appcompat.app.AlertDialog dialog) {
        isPollingUpload = true;
        uploadCheckStartTime = System.currentTimeMillis();
        lastProcessedFileId = null;

        uploadPollingHandler = new Handler(Looper.getMainLooper());
        uploadPollingRunnable = new Runnable() {
            @Override
            public void run() {
                if (!isPollingUpload) {
                    return;
                }

                checkUploadStatus(statusView, dialog);
                uploadPollingHandler.postDelayed(this, 3000); // 每3秒检查一次
            }
        };

        uploadPollingHandler.post(uploadPollingRunnable);
    }

    /**
     * 检查上传状态
     */
    private void checkUploadStatus(TextView statusView, androidx.appcompat.app.AlertDialog dialog) {
        new Thread(() -> {
            try {
                // 1. 查询生成结果（gen模块）
                checkGenerationResult(dialog);

                // 2. 查询上传记录（style模块）- 使用session_id过滤
                String queryUrl = "https://www.jcoding.chat/application/upload/query?session_id=" + currentSessionId + "&limit=1";
                android.util.Log.d("PhotoStyleActivity", "查询URL: " + queryUrl);

                okhttp3.OkHttpClient client = createUnsafeOkHttpClient();

                okhttp3.Request request = new okhttp3.Request.Builder()
                        .url(queryUrl)
                        .addHeader("Host", "www.jcoding.chat")
                        .build();

                okhttp3.Response response = client.newCall(request).execute();

                if (response.isSuccessful() && response.body() != null) {
                    String jsonStr = response.body().string();
                    org.json.JSONObject jsonResponse = new org.json.JSONObject(jsonStr);

                    if (jsonResponse.optInt("code") == 200) {
                        org.json.JSONArray uploads = jsonResponse.optJSONArray("data");

                        if (uploads != null && uploads.length() > 0) {
                            org.json.JSONObject latestUpload = uploads.optJSONObject(0);
                            if (latestUpload != null) {
                                String fileId = latestUpload.optString("file_id");
                                String imageUrl = latestUpload.optString("oss_url");
                                String filename = latestUpload.optString("filename");
                                long uploadTime = latestUpload.optLong("upload_time", 0);
                                String sessionId = latestUpload.optString("session_id");

                                android.util.Log.d("PhotoStyleActivity", "获取到图片 - file_id: " + fileId + ", upload_time: " + uploadTime + ", sessionId: " + sessionId);

                                // 检查是否在开始轮询之后上传
                                if (uploadTime > uploadCheckStartTime && !imageUrl.isEmpty()) {
                                    // 检查session_id是否匹配
                                    if (sessionId != null && !sessionId.isEmpty() && !sessionId.equals(currentSessionId)) {
                                        android.util.Log.d("PhotoStyleActivity", "session_id不匹配 - 当前: " + currentSessionId + ", 上传: " + sessionId);
                                        runOnUiThread(() -> {
                                            stopPollingUpload();
                                            dialog.dismiss();
                                            showToast("已有人扫码上传，请排队等待下一次机会");
                                        });
                                        return;
                                    }

                                    if (!fileId.equals(lastProcessedFileId)) {
                                        android.util.Log.d("PhotoStyleActivity", "检测到新上传，开始处理");
                                        lastProcessedFileId = fileId;

                                        runOnUiThread(() -> {
                                            handleUploadSuccess(imageUrl, filename, dialog);
                                        });
                                        return;
                                    }
                                }
                            }
                        }
                    }
                }
            } catch (Exception e) {
                android.util.Log.e("PhotoStyleActivity", "查询上传状态失败", e);
            }
        }).start();
    }

    /**
     * 检查生成结果（gen模块）
     */
    private void checkGenerationResult(androidx.appcompat.app.AlertDialog dialog) {
        try {
            String queryUrl = "https://www.jcoding.chat/application/generation/query";
            if (currentSessionId != null && !currentSessionId.isEmpty()) {
                queryUrl += "?session_id=" + currentSessionId;
            }

            android.util.Log.d("PhotoStyleActivity", "查询生成结果URL: " + queryUrl);

            okhttp3.OkHttpClient client = createUnsafeOkHttpClient();

            okhttp3.Request request = new okhttp3.Request.Builder()
                    .url(queryUrl)
                    .addHeader("Host", "www.jcoding.chat")
                    .build();

            okhttp3.Response response = client.newCall(request).execute();

            if (response.isSuccessful() && response.body() != null) {
                String jsonStr = response.body().string();
                org.json.JSONObject jsonResponse = new org.json.JSONObject(jsonStr);

                int code = jsonResponse.optInt("code", -1);
                android.util.Log.d("PhotoStyleActivity", "生成结果查询响应: code=" + code);

                if (code == 200) {
                    org.json.JSONObject data = jsonResponse.optJSONObject("data");
                    if (data != null) {
                        String resultUrl = data.optString("result_url");
                        String resultSessionId = data.optString("session_id");
                        long uploadTime = data.optLong("upload_time", 0);

                        android.util.Log.d("PhotoStyleActivity", "获取到生成结果: resultUrl=" + resultUrl +
                            ", sessionId=" + resultSessionId + ", uploadTime=" + uploadTime);

                        // 检查是否在开始轮询之后生成
                        if (uploadTime > uploadCheckStartTime && !resultUrl.isEmpty()) {
                            // 检查session_id是否匹配
                            if (resultSessionId != null && !resultSessionId.isEmpty() &&
                                !resultSessionId.equals(currentSessionId)) {
                                android.util.Log.d("PhotoStyleActivity", "生成结果session_id不匹配 - 当前: " +
                                    currentSessionId + ", 生成: " + resultSessionId);
                                return;
                            }

                            // 检查是否已处理过这个结果
                            if (!resultUrl.equals(lastProcessedFileId)) {
                                android.util.Log.d("PhotoStyleActivity", "检测到新生成结果，开始处理");
                                lastProcessedFileId = resultUrl;

                                // 停止轮询
                                stopPollingUpload();

                                        runOnUiThread(() -> {
                                            // 关闭二维码对话框
                                            if (dialog != null && dialog.isShowing()) {
                                                dialog.dismiss();
                                            }

                                            // 跳转到生成结果页面
                                            navigateToGenerationResult(resultUrl);
                                        });
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
            android.util.Log.e("PhotoStyleActivity", "查询生成结果失败", e);
        }
    }

    /**
     * 跳转到生成结果页面
     */
    private void navigateToGenerationResult(String resultUrl) {
        try {
            android.util.Log.d("PhotoStyleActivity", "跳转到生成结果页面: " + resultUrl);

            // 将OSS URL转换为代理URL
            String proxyUrl = com.jcoding.aiactivity.utils.NetworkUtils.convertToProxyUrl(resultUrl);
            android.util.Log.d("PhotoStyleActivity", "代理URL: " + proxyUrl);

            Intent intent = new Intent(this, com.jcoding.aiactivity.ui.ResultActivity.class);
            intent.putExtra(Constants.EXTRA_STYLE_ID, selectedStyle != null ? selectedStyle.getStyleId() : "");
            intent.putExtra("result_image_url", proxyUrl);
            intent.putExtra("original_photo_path", "");
            intent.putExtra("generation_time", new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss",
                java.util.Locale.getDefault()).format(new java.util.Date()));

            startActivity(intent);
        } catch (Exception e) {
            android.util.Log.e("PhotoStyleActivity", "跳转到生成结果页面失败", e);
            showToast("跳转失败: " + e.getMessage());
        }
    }

    /**
     * 处理上传成功
     */
    private void handleUploadSuccess(String imageUrl, String filename, androidx.appcompat.app.AlertDialog dialog) {
        android.util.Log.d("PhotoStyleActivity", "处理上传成功，图片URL: " + imageUrl);

        // 将OSS URL转换为代理URL
        String proxyUrl = com.jcoding.aiactivity.utils.NetworkUtils.convertToProxyUrl(imageUrl);
        android.util.Log.d("PhotoStyleActivity", "代理URL: " + proxyUrl);

        // 停止轮询
        isPollingUpload = false;
        if (uploadPollingHandler != null && uploadPollingRunnable != null) {
            uploadPollingHandler.removeCallbacks(uploadPollingRunnable);
        }

        // 直接在对话框中显示图片，延迟后跳转（不再下载到temp）
        showImageInDialogAndDelay(proxyUrl, imageUrl, dialog);
    }

    /**
     * 下载图片到temp文件夹
     * @param proxyUrl 代理URL（用于下载）
     * @param filename 文件名
     * @param originalUrl 原始URL（用于备份）
     * @param dialog QR码对话框（用于显示图片后关闭）
     */
    private void downloadImageToTemp(String proxyUrl, String filename, String originalUrl,
                                      androidx.appcompat.app.AlertDialog dialog) {
        android.util.Log.d("PhotoStyleActivity", "开始下载图片到temp");
        android.util.Log.d("PhotoStyleActivity", "  代理URL: " + proxyUrl);
        android.util.Log.d("PhotoStyleActivity", "  原始URL: " + originalUrl);

        new Thread(() -> {
            okhttp3.OkHttpClient client = createUnsafeOkHttpClient();
            try {
                // 创建temp文件夹
                java.io.File tempDir = new java.io.File(getCacheDir(), "temp");
                if (!tempDir.exists()) {
                    tempDir.mkdirs();
                }

                // 清理temp文件夹中的旧图片
                cleanupTempFiles(tempDir);

                // 创建目标文件
                String extension = getImageExtension(proxyUrl);
                java.io.File destFile = new java.io.File(tempDir, "uploaded_photo" + extension);

                // 使用OkHttp下载图片（添加Host header）
                okhttp3.Request request = new okhttp3.Request.Builder()
                        .url(proxyUrl)
                        .addHeader("Host", com.jcoding.aiactivity.utils.NetworkUtils.getProxyHost())
                        .build();

                okhttp3.Response response = client.newCall(request).execute();

                if (response.isSuccessful() && response.body() != null) {
                    java.io.InputStream input = response.body().byteStream();
                    java.io.FileOutputStream output = new java.io.FileOutputStream(destFile);

                    byte[] buffer = new byte[8192];
                    int len;
                    long total = 0;
                    while ((len = input.read(buffer)) > 0) {
                        output.write(buffer, 0, len);
                        total += len;
                    }

                    output.flush();
                    output.close();
                    input.close();

                    android.util.Log.d("PhotoStyleActivity", "图片下载成功: " + destFile.getAbsolutePath() + ", 大小: " + total + " bytes");

                    // 在主线程中先显示图片，再延迟跳转
                    runOnUiThread(() -> {
                        // 先在对话框中显示图片满屏
                        showImageInDialogAndDelay(destFile.getAbsolutePath(), originalUrl, dialog);
                    });

                } else {
                    android.util.Log.e("PhotoStyleActivity", "下载失败，响应码: " + response.code());
                    // 下载失败，仍然传递URL，让GenerationActivity处理
                    runOnUiThread(() -> {
                        navigateToGeneration(null, originalUrl);
                    });
                }

            } catch (Exception e) {
                android.util.Log.e("PhotoStyleActivity", "下载图片异常", e);
                // 下载失败，仍然传递URL，让GenerationActivity处理
                runOnUiThread(() -> {
                    navigateToGeneration(null, originalUrl);
                });
            }
        }).start();
    }

    /**
     * 在对话框中显示图片，延迟后关闭对话框并跳转
     */
    private void showImageInDialogAndDelay(String proxyUrl, String imageUrl,
                                           androidx.appcompat.app.AlertDialog dialog) {
        android.util.Log.d("PhotoStyleActivity", "在对话框中显示图片: " + proxyUrl);

        try {
            // 获取对话框中的ImageView
            android.widget.ImageView ivQRCode = dialog.findViewById(R.id.iv_qrcode);
            android.widget.TextView tvHint = dialog.findViewById(R.id.tv_hint);
            android.widget.TextView tvStatus = dialog.findViewById(R.id.tv_status);

            if (ivQRCode != null && tvHint != null) {
                // 隐藏QR码，显示图片
                ivQRCode.setScaleType(android.widget.ImageView.ScaleType.FIT_XY);
                ivQRCode.setAdjustViewBounds(false);

                // 直接从URL加载并显示图片（满屏）
                com.bumptech.glide.Glide.with(this)
                        .load(proxyUrl)
                        .placeholder(android.graphics.Color.TRANSPARENT)
                        .fitCenter()
                        .addListener(new com.bumptech.glide.request.RequestListener<android.graphics.drawable.Drawable>() {
                            @Override
                            public boolean onLoadFailed(@androidx.annotation.Nullable com.bumptech.glide.load.engine.GlideException e, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                                android.util.Log.e("PhotoStyleActivity", "图片加载失败", e);
                                runOnUiThread(() -> {
                                    tvHint.setText("图片加载失败");
                                });
                                return false;
                            }

                            @Override
                            public boolean onResourceReady(android.graphics.drawable.Drawable resource, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                                android.util.Log.d("PhotoStyleActivity", "图片加载成功");
                                runOnUiThread(() -> {
                                    tvHint.setText("照片已接收");
                                    tvHint.setTextSize(18);
                                });
                                return false;
                            }
                        })
                        .into(ivQRCode);

                // 更新提示文字
                tvHint.setText("正在加载照片...");

                if (tvStatus != null) {
                    tvStatus.setText("正在准备生成...");
                }

                // 延迟3秒后关闭对话框并跳转
                new android.os.Handler().postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        // 关闭对话框
                        if (dialog != null && dialog.isShowing()) {
                            try {
                                dialog.dismiss();
                            } catch (Exception e) {
                                android.util.Log.e("PhotoStyleActivity", "关闭对话框失败", e);
                            }
                        }

                        // 跳转到生成页面（传递null表示使用URL）
                        navigateToGeneration(null, imageUrl);
                    }
                }, 3000); // 延迟3秒

            } else {
                // 如果找不到ImageView，直接跳转
                navigateToGeneration(null, imageUrl);
            }
        } catch (Exception e) {
            android.util.Log.e("PhotoStyleActivity", "显示图片异常", e);
            // 异常情况直接跳转
            navigateToGeneration(null, imageUrl);
        }
    }

    /**
     * 清理temp文件夹中的旧图片
     */
    private void cleanupTempFiles(java.io.File tempDir) {
        try {
            java.io.File[] files = tempDir.listFiles();
            if (files != null) {
                for (java.io.File file : files) {
                    if (file.isFile() && file.getName().startsWith("uploaded_photo")) {
                        boolean deleted = file.delete();
                        android.util.Log.d("PhotoStyleActivity", "删除旧文件: " + file.getName() + ", 成功: " + deleted);
                    }
                }
            }
        } catch (Exception e) {
            android.util.Log.e("PhotoStyleActivity", "清理temp文件失败", e);
        }
    }

    /**
     * 获取图片扩展名
     */
    private String getImageExtension(String url) {
        if (url.contains(".jpg") || url.contains(".jpeg")) {
            return ".jpg";
        } else if (url.contains(".png")) {
            return ".png";
        } else if (url.contains(".webp")) {
            return ".webp";
        } else {
            return ".jpg"; // 默认
        }
    }

    /**
     * 跳转到生成页面
     */
    private void navigateToGeneration(String localPath, String imageUrl) {
        android.util.Log.d("PhotoStyleActivity", "跳转到GenerationActivity");
        android.util.Log.d("PhotoStyleActivity", "本地路径: " + localPath);
        android.util.Log.d("PhotoStyleActivity", "图片URL: " + imageUrl);
        android.util.Log.d("PhotoStyleActivity", "currentPosition: " + currentPosition);

        // 确保selectedStyle正确
        if (selectedStyle == null && styleList != null && !styleList.isEmpty() && currentPosition < styleList.size()) {
            selectedStyle = styleList.get(currentPosition);
            android.util.Log.d("PhotoStyleActivity", "从styleList重新获取selectedStyle: " +
                (selectedStyle != null ? selectedStyle.getName() : "null"));
        }

        android.util.Log.d("PhotoStyleActivity", "selectedStyle: " + (selectedStyle != null ? selectedStyle.getName() : "null"));
        android.util.Log.d("PhotoStyleActivity", "currentSessionId: " + currentSessionId);

        if (selectedStyle != null) {
            android.util.Log.d("PhotoStyleActivity", "selectedStyle.getMaskImage(): " + selectedStyle.getMaskImage());
        }

        try {
            Intent intent = new Intent(this, com.jcoding.aiactivity.ui.GenerationActivity.class);
            intent.putExtra(Constants.EXTRA_STYLE_ID, selectedStyle != null ? selectedStyle.getStyleId() : "");
            intent.putExtra(Constants.EXTRA_MODE, Constants.MODE_CAMERA);
            if (localPath != null) {
                intent.putExtra("photo_path", localPath); // 传递本地文件路径
            }
            intent.putExtra(Constants.EXTRA_IMAGE_URL, imageUrl); // 传递图片URL作为备份

            // 传递遮罩图片路径
            if (selectedStyle != null && selectedStyle.getMaskImage() != null && !selectedStyle.getMaskImage().isEmpty()) {
                intent.putExtra("mask_image_path", selectedStyle.getMaskImage());
                android.util.Log.d("PhotoStyleActivity", "传递遮罩图片路径: " + selectedStyle.getMaskImage());
            } else {
                android.util.Log.w("PhotoStyleActivity", "没有遮罩图片配置或selectedStyle为null");
            }

            // 传递session_id用于生成结果关联
            if (currentSessionId != null && !currentSessionId.isEmpty()) {
                intent.putExtra("session_id", currentSessionId);
                android.util.Log.d("PhotoStyleActivity", "传递session_id: " + currentSessionId);
            }

            startActivity(intent);
        } catch (Exception e) {
            android.util.Log.e("PhotoStyleActivity", "跳转到生成页面失败", e);
            showToast("跳转失败: " + e.getMessage());
        }
    }

    /**
     * 停止轮询上传
     */
    private void stopPollingUpload() {
        isPollingUpload = false;
        if (uploadPollingHandler != null && uploadPollingRunnable != null) {
            uploadPollingHandler.removeCallbacks(uploadPollingRunnable);
        }
    }

    /**
     * 创建信任所有证书的OkHttpClient
     */
    private okhttp3.OkHttpClient createUnsafeOkHttpClient() {
        try {
            javax.net.ssl.TrustManager[] trustAllCerts = new javax.net.ssl.TrustManager[]{
                new javax.net.ssl.X509TrustManager() {
                    @Override
                    public void checkClientTrusted(java.security.cert.X509Certificate[] chain, String authType) {
                    }

                    @Override
                    public void checkServerTrusted(java.security.cert.X509Certificate[] chain, String authType) {
                    }

                    @Override
                    public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                        return new java.security.cert.X509Certificate[]{};
                    }
                }
            };

            javax.net.ssl.SSLContext sslContext = javax.net.ssl.SSLContext.getInstance("SSL");
            sslContext.init(null, trustAllCerts, new java.security.SecureRandom());

            javax.net.ssl.SSLSocketFactory sslSocketFactory = sslContext.getSocketFactory();

            return new okhttp3.OkHttpClient.Builder()
                    .sslSocketFactory(sslSocketFactory, (javax.net.ssl.X509TrustManager) trustAllCerts[0])
                    .hostnameVerifier((hostname, session) -> true)
                    .protocols(java.util.Collections.singletonList(okhttp3.Protocol.HTTP_1_1))
                    .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                    .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                    .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                    .build();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * 数字人三击回调
     */
    @Override
    public void onDigitalHumanTap() {
        digitalHumanTapCount++;

        android.util.Log.d("PhotoStyleActivity", "数字人点击计数: " + digitalHumanTapCount);

        // 取消之前的超时任务
        tapCountHandler.removeCallbacks(tapTimeoutRunnable);

        if (digitalHumanTapCount >= REQUIRED_TAPS) {
            // 达到3次，切换锁定状态
            android.util.Log.d("PhotoStyleActivity", "达到3次点击，切换数字人锁定状态");
            digitalHumanTapCount = 0;
            toggleDigitalHumanLock();
        } else {
            // 重新设置超时
            tapCountHandler.postDelayed(tapTimeoutRunnable, TAP_TIMEOUT);
        }
    }

    private Runnable tapTimeoutRunnable = new Runnable() {
        @Override
        public void run() {
            digitalHumanTapCount = 0;
            android.util.Log.d("PhotoStyleActivity", "点击超时，重置计数器");
        }
    };

    /**
     * 设置图层切换功能
     */
    private void setupLayerSwitch() {
        layerSwitchTrigger = findViewById(R.id.layer_switch_trigger);

        if (layerSwitchTrigger != null) {
            layerSwitchTrigger.setOnTouchListener(new View.OnTouchListener() {
                @Override
                public boolean onTouch(View v, MotionEvent event) {
                    if (event.getAction() == MotionEvent.ACTION_UP) {
                        handleLayerSwitchTap();
                        return true;
                    }
                    return false;
                }
            });
        }
    }

    /**
     * 处理图层切换区域的点击
     */
    private void handleLayerSwitchTap() {
        layerSwitchTapCount++;

        android.util.Log.d("PhotoStyleActivity", "图层切换点击计数: " + layerSwitchTapCount);

        // 取消之前的超时任务
        layerSwitchHandler.removeCallbacks(layerSwitchTimeoutRunnable);

        if (layerSwitchTapCount >= LAYER_SWITCH_TAPS) {
            // 达到3次，显示图层切换对话框
            android.util.Log.d("PhotoStyleActivity", "达到3次点击，显示图层切换对话框");
            layerSwitchTapCount = 0;
            showLayerSwitchDialog();
        } else {
            // 重新设置超时
            layerSwitchHandler.postDelayed(layerSwitchTimeoutRunnable, LAYER_SWITCH_TIMEOUT);
        }
    }

    private Runnable layerSwitchTimeoutRunnable = new Runnable() {
        @Override
        public void run() {
            layerSwitchTapCount = 0;
            android.util.Log.d("PhotoStyleActivity", "图层切换点击超时，重置计数器");
        }
    };

    /**
     * 显示图层切换对话框
     */
    private void showLayerSwitchDialog() {
        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
        builder.setTitle("图层控制");
        builder.setMessage("选择要操作的图层：");

        // 创建开关选项
        String[] items = {"数字人图层", "按钮图层"};
        boolean[] checkedItems = {digitalHumanLayerEnabled, buttonLayerEnabled};

        builder.setMultiChoiceItems(items, checkedItems, new android.content.DialogInterface.OnMultiChoiceClickListener() {
            @Override
            public void onClick(android.content.DialogInterface dialog, int which, boolean isChecked) {
                if (which == 0) {
                    digitalHumanLayerEnabled = isChecked;
                    android.util.Log.d("PhotoStyleActivity", "数字人图层: " + (isChecked ? "启用" : "禁用"));
                } else if (which == 1) {
                    buttonLayerEnabled = isChecked;
                    android.util.Log.d("PhotoStyleActivity", "按钮图层: " + (isChecked ? "启用" : "禁用"));
                }
            }
        });

        builder.setPositiveButton("确定", new android.content.DialogInterface.OnClickListener() {
            @Override
            public void onClick(android.content.DialogInterface dialog, int which) {
                updateLayerElevation();
                showToast("图层设置已更新");
            }
        });

        builder.setNegativeButton("取消", null);
        builder.show();
    }

    /**
     * 更新图层elevation
     */
    private void updateLayerElevation() {
        // 获取GlobalDigitalHumanManager中的数字人视图
        com.jcoding.aiactivity.manager.GlobalDigitalHumanManager globalManager =
                com.jcoding.aiactivity.manager.GlobalDigitalHumanManager.getInstance(this);

        // 设置数字人图层elevation
        if (digitalHumanLayerEnabled) {
            // 数字人在最上面 - 设置最高elevation
            if (digitalHumanView != null) {
                digitalHumanView.setElevation(200);
            }
            android.util.Log.d("PhotoStyleActivity", "数字人图层置顶: elevation=200");
        } else {
            // 数字人在下面
            if (digitalHumanView != null) {
                digitalHumanView.setElevation(1);
            }
            android.util.Log.d("PhotoStyleActivity", "数字人图层下沉: elevation=1");
        }

        // 设置按钮图层elevation
        if (buttonLayerEnabled) {
            // 按钮在最上面
            if (btnStart != null) {
                // 需要获取按钮容器
                View buttonContainer = findViewById(R.id.button_container);
                if (buttonContainer != null) {
                    buttonContainer.setElevation(200);
                }
            }
            android.util.Log.d("PhotoStyleActivity", "按钮图层置顶: elevation=200");
        } else {
            // 按钮在下面
            if (btnStart != null) {
                View buttonContainer = findViewById(R.id.button_container);
                if (buttonContainer != null) {
                    buttonContainer.setElevation(50);
                }
            }
            android.util.Log.d("PhotoStyleActivity", "按钮图层下沉: elevation=50");
        }
    }
}
