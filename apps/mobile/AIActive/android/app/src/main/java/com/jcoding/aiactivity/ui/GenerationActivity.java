package com.jcoding.aiactivity.ui;

import android.app.Dialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.DataSource;
import com.bumptech.glide.load.engine.GlideException;
import com.bumptech.glide.request.RequestListener;
import com.jcoding.aiactivity.R;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import com.jcoding.aiactivity.entity.GenerationTask;
import com.jcoding.aiactivity.entity.StyleConfig;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.FileUploadManager;
import com.jcoding.aiactivity.manager.VoiceManager;
import com.jcoding.aiactivity.manager.DigitalHumanManager;
import com.jcoding.aiactivity.manager.SpeechRecognizerManager;
import com.jcoding.aiactivity.network.ApiService;
import com.jcoding.aiactivity.network.RetrofitClient;
import com.jcoding.aiactivity.utils.Constants;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * AI生成页
 * 上传照片并调用AI生成接口
 */
public class GenerationActivity extends BaseActivity {

    private ImageView ivOriginal;
    private ImageView ivResult;
    private ImageView ivLoadingSpinner;
    private ImageView ivDigitalHuman;
    private FrameLayout digitalHumanContainer;
    private TextView tvStatus;
    private TextView tvProgressPercentage;
    private TextView tvEta;
    private ProgressBar progressBar;
    private ProgressBar progressBarHorizontal;
    private Button btnBack;
    private Button btnVoiceInput;
    private TextView tvOfflineMode;

    private String styleId;
    private String photoFilePath;
    private String maskImagePath;  // 遮罩图片路径（assets路径）
    private String uploadedImageUrl;
    private String uploadedMaskUrl;  // 上传后的遮罩图片URL
    private String resultImageUrl;
    private String currentTaskId;
    private String sessionId;  // 会话ID，用于关联生成结果

    private Handler handler = new Handler(Looper.getMainLooper());
    private Runnable pollingRunnable;
    private Runnable progressUpdateRunnable;
    private Runnable spinnerAnimationRunnable;
    private Runnable chitchatRunnable; // 等待期间的聊天任务

    // 进度跟踪
    private int currentProgress = 0;
    private long generationStartTime;
    private int estimatedTime = 30; // 预计时间（秒）

    // 照片拖拽相关
    private android.graphics.Matrix photoMatrix;
    private float lastTouchX, lastTouchY;
    private boolean isDraggingEnabled = true; // 是否启用拖拽功能

    private VoiceManager voiceManager;
    private DigitalHumanManager digitalHumanManager;
    private SpeechRecognizerManager speechRecognizerManager;

    // 语音识别状态
    private boolean isVoiceInputEnabled = false;

    // 全屏结果对话框
    private Dialog fullscreenDialog;
    private Handler qrcodeTimeoutHandler = new Handler(Looper.getMainLooper());
    private Runnable qrcodeTimeoutRunnable;
    private Handler autoCloseHandler = new Handler(Looper.getMainLooper());
    private Runnable autoCloseRunnable;

    // 图片视图（需要保存为成员变量以支持拖拽）
    private ImageView ivUploadedPhoto;
    private ImageView ivMaskOverlay;

    // 图片URL（从扫码上传获得）
    private String imageUrl;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_generation_simple);

        // 获取参数
        styleId = getIntent().getStringExtra(Constants.EXTRA_STYLE_ID);
        photoFilePath = getIntent().getStringExtra("photo_path");
        imageUrl = getIntent().getStringExtra(Constants.EXTRA_IMAGE_URL);
        maskImagePath = getIntent().getStringExtra("mask_image_path");
        sessionId = getIntent().getStringExtra("session_id");

        // imageUrl直接使用，不再转换为代理URL

        android.util.Log.d("GenerationActivity", "参数接收 - styleId: " + styleId);
        android.util.Log.d("GenerationActivity", "参数接收 - photoFilePath: " + photoFilePath);
        android.util.Log.d("GenerationActivity", "参数接收 - maskImagePath: " + maskImagePath);
        android.util.Log.d("GenerationActivity", "参数接收 - imageUrl: " + imageUrl);
        android.util.Log.d("GenerationActivity", "maskImagePath: " + maskImagePath);

        // 初始化管理器（根据配置）
        if (configManager.isVoiceGuidanceEnabled()) {
            voiceManager = VoiceManager.getInstance(this);
        }
        if (configManager.isDigitalHumanEnabled()) {
            digitalHumanManager = DigitalHumanManager.getInstance(this);
        }
        if (configManager.isVoiceCommandEnabled()) {
            speechRecognizerManager = SpeechRecognizerManager.getInstance(this);
        }

        initViews();
        initDigitalHuman();
        loadOriginalPhoto();
        // 注意：startGeneration() 会在图片加载完成后调用
    }

    private void initViews() {
        // 新布局的视图
        ivUploadedPhoto = findViewById(R.id.iv_uploaded_photo);
        ivMaskOverlay = findViewById(R.id.iv_mask_overlay);

        // 初始化照片拖拽Matrix
        photoMatrix = new android.graphics.Matrix();
        ivUploadedPhoto.setScaleType(ImageView.ScaleType.MATRIX);
        ivUploadedPhoto.setImageMatrix(photoMatrix);

        // 设置照片拖拽监听器
        setupPhotoDragListener();

        // 保留旧视图但设为null（兼容性）
        ivOriginal = null;
        ivResult = null;

        ivLoadingSpinner = findViewById(R.id.iv_loading_spinner);
        ivDigitalHuman = findViewById(R.id.iv_digital_human);
        digitalHumanContainer = findViewById(R.id.digital_human_container);
        tvStatus = findViewById(R.id.tv_status);
        tvProgressPercentage = findViewById(R.id.tv_progress_percentage);
        tvEta = findViewById(R.id.tv_eta);
        progressBar = findViewById(R.id.progress_bar);
        progressBarHorizontal = null; // 新布局中没有
        btnBack = findViewById(R.id.btn_back);
        btnVoiceInput = null; // 新布局中没有
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        // btnVoiceInput 可能为null（新布局中没有）
        if (btnVoiceInput != null) {
            btnVoiceInput.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startVoiceRecognition();
                }
            });
        }

        // 启用语音输入（等待生成完成后启用）
        enableVoiceInput(false);
    }

    /**
     * 设置照片拖拽监听器
     * 允许用户拖动照片调整位置，以便更好地与遮罩对齐
     */
    private void setupPhotoDragListener() {
        if (ivUploadedPhoto == null || !isDraggingEnabled) {
            return;
        }

        ivUploadedPhoto.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (!isDraggingEnabled) {
                    return false;
                }

                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        // 记录初始触摸位置
                        lastTouchX = event.getX();
                        lastTouchY = event.getY();
                        return true;

                    case MotionEvent.ACTION_MOVE:
                        // 计算移动距离
                        float dx = event.getX() - lastTouchX;
                        float dy = event.getY() - lastTouchY;

                        // 更新Matrix，平移图片
                        photoMatrix.postTranslate(dx, dy);
                        ivUploadedPhoto.setImageMatrix(photoMatrix);

                        // 更新最后触摸位置
                        lastTouchX = event.getX();
                        lastTouchY = event.getY();
                        return true;

                    case MotionEvent.ACTION_UP:
                    case MotionEvent.ACTION_CANCEL:
                        // 触摸结束，无需特殊处理
                        return true;
                }
                return false;
            }
        });

        android.util.Log.d("GenerationActivity", "照片拖拽功能已启用");
    }

    /**
     * 初始化数字人
     * 在等待生成时，数字人显示在画面中间进行互动
     */
    private void initDigitalHuman() {
        if (digitalHumanManager == null) {
            digitalHumanContainer.setVisibility(View.GONE);
            return;
        }

        // 检查AI百变秀模块是否启用数字人
        if (!configManager.isDigitalHumanEnabledForModule("ai_show")) {
            digitalHumanContainer.setVisibility(View.GONE);
            return;
        }

        digitalHumanContainer.setVisibility(View.VISIBLE);

        // 等待时数字人尺寸更大（40%屏幕宽度）
        int screenSize = getResources().getDisplayMetrics().widthPixels;
        final int waitingSizePx = (int) (screenSize * 0.4);

        // 修改ivDigitalHuman的尺寸
        android.view.ViewGroup.LayoutParams imageParams = ivDigitalHuman.getLayoutParams();
        imageParams.width = waitingSizePx;
        imageParams.height = waitingSizePx;
        ivDigitalHuman.setLayoutParams(imageParams);
        ivDigitalHuman.setScaleType(ImageView.ScaleType.FIT_CENTER);

        // 显示默认数字人动画（使用Glide加载GIF）
        updateDigitalHumanImage(digitalHumanManager.getDefaultGif());

        // 欢迎并播报提示
        if (configManager.isVoiceGuidanceEnabled()) {
            digitalHumanManager.speak("正在为您生成AI百变秀作品，请稍候", new DigitalHumanManager.DigitalHumanCallback() {
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
                    android.util.Log.e("GenerationActivity", "Digital human error: " + error);
                }
            });
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

        // 获取配置的大小（dp值），转换为px
        int sizeDp = configManager.getDigitalHumanSize();
        final int sizePx = (int) (sizeDp * getResources().getDisplayMetrics().density);

        // 设置ImageView尺寸
        android.widget.FrameLayout.LayoutParams params = (android.widget.FrameLayout.LayoutParams) ivDigitalHuman.getLayoutParams();
        params.width = sizePx;
        params.height = sizePx;
        ivDigitalHuman.setLayoutParams(params);

        // 获取缩放类型
        String scaleType = configManager.getDigitalHumanScaleType();
        final android.widget.ImageView.ScaleType finalScaleType;
        if ("center_crop".equals(scaleType)) {
            finalScaleType = android.widget.ImageView.ScaleType.CENTER_CROP;
        } else if ("center".equals(scaleType)) {
            finalScaleType = android.widget.ImageView.ScaleType.CENTER;
        } else {
            finalScaleType = android.widget.ImageView.ScaleType.FIT_CENTER;
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
                                String scaleType = configManager.getDigitalHumanScaleType();
                                if ("center_crop".equals(scaleType)) {
                                    ivDigitalHuman.setScaleType(android.widget.ImageView.ScaleType.CENTER_CROP);
                                } else if ("center".equals(scaleType)) {
                                    ivDigitalHuman.setScaleType(android.widget.ImageView.ScaleType.CENTER);
                                } else {
                                    ivDigitalHuman.setScaleType(android.widget.ImageView.ScaleType.FIT_CENTER);
                                }
                                resource.start();
                            }

                            @Override
                            public void onLoadCleared(android.graphics.drawable.Drawable placeholder) {
                            }
                        });
            } else {
                android.util.Log.e("GenerationActivity", "GIF file not found: " + assetPath);
            }
        } catch (Exception e) {
            android.util.Log.e("GenerationActivity", "Failed to load GIF: " + gifPath, e);
        }
    }

    /**
     * 加载上传的照片和遮罩层
     * 优先从本地temp文件加载，如果没有则从URL下载
     */
    private void loadOriginalPhoto() {
        android.util.Log.d("GenerationActivity", "loadOriginalPhoto - 开始加载");
        android.util.Log.d("GenerationActivity", "  photoFilePath: " + photoFilePath);
        android.util.Log.d("GenerationActivity", "  imageUrl: " + imageUrl);
        android.util.Log.d("GenerationActivity", "  maskImagePath: " + maskImagePath);

        // 使用成员变量而不是局部变量
        if (ivUploadedPhoto == null) {
            ivUploadedPhoto = findViewById(R.id.iv_uploaded_photo);
        }
        if (ivMaskOverlay == null) {
            ivMaskOverlay = findViewById(R.id.iv_mask_overlay);
        }

        // 加载遮罩层图片（支持URL和assets路径）
        if (maskImagePath != null && !maskImagePath.isEmpty()) {
            android.util.Log.d("GenerationActivity", "加载遮罩层: " + maskImagePath);
            try {
                // 确保遮罩图层可见且在上层
                if (ivMaskOverlay != null) {
                    ivMaskOverlay.setVisibility(android.view.View.VISIBLE);
                    android.util.Log.d("GenerationActivity", "遮罩ImageView已设置为可见");

                    // 判断是URL还是assets路径
                    if (maskImagePath.startsWith("http://") || maskImagePath.startsWith("https://")) {
                        // 从URL加载遮罩 - 直接使用原URL
                        android.util.Log.d("GenerationActivity", "从URL加载遮罩: " + maskImagePath);
                        Glide.with(this)
                                .load(maskImagePath)
                                .listener(new com.bumptech.glide.request.RequestListener<android.graphics.drawable.Drawable>() {
                                    @Override
                                    public boolean onLoadFailed(@androidx.annotation.Nullable com.bumptech.glide.load.engine.GlideException e, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                                        android.util.Log.e("GenerationActivity", "遮罩URL加载失败", e);
                                        return false;
                                    }

                                    @Override
                                    public boolean onResourceReady(android.graphics.drawable.Drawable resource, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                                        android.util.Log.d("GenerationActivity", "遮罩URL加载成功");
                                        // 设置遮罩不透明度为100%（完全不透明）
                                        ivMaskOverlay.setAlpha(1.0f);
                                        android.util.Log.d("GenerationActivity", "遮罩不透明度设置为100%");
                                        return false;
                                    }
                                })
                                .into(ivMaskOverlay);
                    } else {
                        // 本地路径，优先尝试从缓存或OSS加载
                        android.util.Log.d("GenerationActivity", "本地mask路径: " + maskImagePath);

                        // 1. 先尝试从缓存加载
                        java.io.File cacheDir = new java.io.File(getCacheDir(), "masks");
                        java.io.File cachedMaskFile = new java.io.File(cacheDir, maskImagePath);

                        if (cachedMaskFile.exists()) {
                            // 从缓存加载
                            android.util.Log.d("GenerationActivity", "从缓存加载遮罩: " + cachedMaskFile.getAbsolutePath());
                            Glide.with(this)
                                    .load(cachedMaskFile)
                                    .listener(new com.bumptech.glide.request.RequestListener<android.graphics.drawable.Drawable>() {
                                        @Override
                                        public boolean onLoadFailed(@androidx.annotation.Nullable com.bumptech.glide.load.engine.GlideException e, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                                            android.util.Log.e("GenerationActivity", "缓存遮罩加载失败: " + e.getMessage());
                                            // 从缓存失败，尝试OSS
                                            loadMaskFromOSS(maskImagePath);
                                            return false;
                                        }

                                        @Override
                                        public boolean onResourceReady(android.graphics.drawable.Drawable resource, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                                            android.util.Log.d("GenerationActivity", "缓存遮罩加载成功");
                                            ivMaskOverlay.setAlpha(1.0f);
                                            return false;
                                        }
                                    })
                                    .into(ivMaskOverlay);
                        } else {
                            // 2. 缓存不存在，尝试从OSS加载
                            loadMaskFromOSS(maskImagePath);
                        }
                    }
                }

                android.util.Log.d("GenerationActivity", "遮罩层加载完成");
            } catch (Exception e) {
                android.util.Log.e("GenerationActivity", "加载遮罩层失败", e);
            }
        } else {
            android.util.Log.w("GenerationActivity", "没有遮罩层配置");
            // 隐藏遮罩图层
            if (ivMaskOverlay != null) {
                ivMaskOverlay.setVisibility(android.view.View.GONE);
            }
        }

        // 加载上传的照片
        // 优先级：URL > 本地文件
        if (imageUrl != null && !imageUrl.isEmpty() && (imageUrl.startsWith("http://") || imageUrl.startsWith("https://"))) {
            // 优先从URL加载
            android.util.Log.d("GenerationActivity", "从URL加载图片: " + imageUrl);
            tvStatus.setText(stripHtmlTags("正在加载上传的照片..."));

            // 使用Glide从URL加载图片（直接使用原URL）
            Glide.with(this)
                    .load(imageUrl)
                    .placeholder(android.graphics.Color.TRANSPARENT)
                    .fitCenter()
                    .listener(new com.bumptech.glide.request.RequestListener<android.graphics.drawable.Drawable>() {
                        @Override
                        public boolean onLoadFailed(@androidx.annotation.Nullable com.bumptech.glide.load.engine.GlideException e, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                            android.util.Log.e("GenerationActivity", "图片加载失败", e);
                            runOnUiThread(() -> {
                                tvStatus.setText(stripHtmlTags("图片加载失败"));
                                // 加载失败，仍然尝试开始生成
                                startGeneration();
                            });
                            return false;
                        }

                        @Override
                        public boolean onResourceReady(android.graphics.drawable.Drawable resource, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                            android.util.Log.d("GenerationActivity", "图片加载成功，开始生成");

                            // 图片加载完成后，重置Matrix并让图片居中显示
                            if (ivUploadedPhoto != null && photoMatrix != null) {
                                ivUploadedPhoto.post(new Runnable() {
                                    @Override
                                    public void run() {
                                        // 重置Matrix
                                        photoMatrix.reset();
                                        // 获取ImageView和图片的尺寸
                                        int viewWidth = ivUploadedPhoto.getWidth();
                                        int viewHeight = ivUploadedPhoto.getHeight();
                                        android.graphics.drawable.Drawable drawable = ivUploadedPhoto.getDrawable();
                                        if (drawable != null) {
                                            int drawableWidth = drawable.getIntrinsicWidth();
                                            int drawableHeight = drawable.getIntrinsicHeight();

                                            // 计算缩放比例，让图片适配ImageView
                                            float scale = Math.min(
                                                (float) viewWidth / drawableWidth,
                                                (float) viewHeight / drawableHeight
                                            );

                                            // 计算居中位置
                                            float scaledWidth = drawableWidth * scale;
                                            float scaledHeight = drawableHeight * scale;
                                            float dx = (viewWidth - scaledWidth) / 2f;
                                            float dy = (viewHeight - scaledHeight) / 2f;

                                            // 设置Matrix：缩放并居中
                                            photoMatrix.setScale(scale, scale);
                                            photoMatrix.postTranslate(dx, dy);
                                            ivUploadedPhoto.setImageMatrix(photoMatrix);

                                            android.util.Log.d("GenerationActivity", "照片Matrix已重置并居中: scale=" + scale + ", dx=" + dx + ", dy=" + dy);
                                        }
                                    }
                                });
                            }

                            runOnUiThread(() -> {
                                tvStatus.setText(stripHtmlTags("照片加载成功，开始生成..."));
                                startGeneration();
                            });
                            return false;
                        }
                    })
                    .into(ivUploadedPhoto);

        } else if (photoFilePath != null && !photoFilePath.isEmpty()) {
            // 降级：从本地文件加载（temp文件夹）
            android.util.Log.d("GenerationActivity", "从本地文件加载: " + photoFilePath);
            tvStatus.setText(stripHtmlTags("正在加载上传的照片..."));

            try {
                java.io.File localFile = new java.io.File(photoFilePath);
                if (localFile.exists()) {
                    android.graphics.Bitmap bitmap = android.graphics.BitmapFactory.decodeFile(photoFilePath);
                    if (bitmap != null) {
                        android.util.Log.d("GenerationActivity", "本地图片加载成功，尺寸: " + bitmap.getWidth() + "x" + bitmap.getHeight());
                        ivUploadedPhoto.setImageBitmap(bitmap);
                        tvStatus.setText(stripHtmlTags("照片加载成功，开始生成..."));
                        // 本地图片加载成功，开始生成
                        startGeneration();
                        return;
                    } else {
                        android.util.Log.e("GenerationActivity", "本地图片解码失败");
                        tvStatus.setText(stripHtmlTags("图片加载失败"));
                    }
                } else {
                    android.util.Log.w("GenerationActivity", "本地文件不存在: " + photoFilePath);
                    tvStatus.setText(stripHtmlTags("图片文件不存在"));
                }
            } catch (Exception e) {
                android.util.Log.e("GenerationActivity", "加载本地文件异常", e);
                tvStatus.setText(stripHtmlTags("图片加载异常"));
            }
        } else {
            android.util.Log.w("GenerationActivity", "没有可用的图片");
            tvStatus.setText(stripHtmlTags("没有可用的图片"));
            // 没有图片，直接开始生成（会失败）
            startGeneration();
        }
    }

    /**
     * 从URL加载图片（降级方案）
     */
    private void loadFromUrl(ImageView imageView) {
        android.util.Log.d("GenerationActivity", "从URL加载图片: " + imageUrl);
        tvStatus.setText(stripHtmlTags("正在从网络加载照片..."));

        new Thread(() -> {
            try {
                // 创建API客户端（使用已有的方法）
                String apiKey = getVolcEngineApiKey();
                if (apiKey == null || apiKey.isEmpty()) {
                    runOnUiThread(() -> {
                        tvStatus.setText(stripHtmlTags("加载失败，开始生成..."));
                        // 即使加载失败，也尝试开始生成
                        startGeneration();
                    });
                    return;
                }

                com.jcoding.aiactivity.network.VolcEngineApiClient apiClient =
                        new com.jcoding.aiactivity.network.VolcEngineApiClient(apiKey, this);

                // 使用downloadImage方法下载URL
                android.graphics.Bitmap bitmap = apiClient.downloadImage(imageUrl);

                if (bitmap != null) {
                    android.util.Log.d("GenerationActivity", "图片下载成功，尺寸: " + bitmap.getWidth() + "x" + bitmap.getHeight());
                    final android.graphics.Bitmap finalBitmap = bitmap;
                    runOnUiThread(() -> {
                        imageView.setImageBitmap(finalBitmap);
                        tvStatus.setText(stripHtmlTags("照片加载成功，开始生成..."));
                        // 下载成功，开始生成
                        startGeneration();
                    });
                } else {
                    android.util.Log.e("GenerationActivity", "图片下载失败，bitmap为null");
                    runOnUiThread(() -> {
                        imageView.setImageResource(android.R.drawable.ic_menu_report_image);
                        tvStatus.setText(stripHtmlTags("照片URL已保存，开始生成..."));
                        // 下载失败，但仍尝试生成（使用URL）
                        startGeneration();
                    });
                }

            } catch (Exception e) {
                android.util.Log.e("GenerationActivity", "下载图片异常", e);
                runOnUiThread(() -> {
                    imageView.setImageResource(android.R.drawable.ic_menu_report_image);
                    tvStatus.setText(stripHtmlTags("照片URL已保存，开始生成..."));
                    // 下载失败，但仍尝试生成（使用URL）
                    startGeneration();
                });
            }
        }).start();
    }

    /**
     * 开始AI生成
     * 直接调用大模型API，跳过文件上传步骤
     */
    private void startGeneration() {
        // 检查网络状态
        if (!NetworkUtils.isOnline(this)) {
            tvStatus.setText(stripHtmlTags("AI生成需要网络连接"));
            hideAllProgressIndicators();
            speakStatus("AI生成需要网络连接，请检查网络设置");
            return;
        }

        tvStatus.setText(stripHtmlTags("准备生成图片..."));
        showProgressBar();
        speakStatus("正在准备生成图片，请稍候");

        // 直接调用API，跳过上传步骤
        android.util.Log.d("GenerationActivity", "直接调用大模型API，跳过文件上传");
        updateProgress(5, "准备完成，开始生成...");
        callGenerateAPI();
    }

    /**
     * 上传遮罩图片
     */
    private void uploadMaskImage() {
        updateProgress(10, "正在上传遮罩图片...");
        android.util.Log.d("GenerationActivity", "开始上传遮罩图片: " + maskImagePath);

        // 遮罩图片在assets中，需要先复制到临时文件
        try {
            // 构建完整路径
            String assetPath = "style/" + maskImagePath;
            android.util.Log.d("GenerationActivity", "遮罩图片assets路径: " + assetPath);

            // 复制到缓存文件
            String outputFileName = "mask_" + (maskImagePath.replace("/", "_"));
            java.io.File maskFile = copyAssetToFile(assetPath, outputFileName);

            if (maskFile != null && maskFile.exists()) {
                // 上传遮罩图片
                FileUploadManager.getInstance(this).uploadFile(
                        maskFile,
                        "mask",  // 来源标识为mask
                        new FileUploadManager.UploadCallback() {
                            @Override
                            public void onSuccess(String fileUrl) {
                                uploadedMaskUrl = fileUrl;
                                android.util.Log.d("GenerationActivity", "遮罩图片上传成功: " + fileUrl);
                                updateProgress(15, "遮罩图片上传完成，开始生成...");
                                callGenerateAPI();
                            }

                            @Override
                            public void onError(String error) {
                                android.util.Log.e("GenerationActivity", "遮罩图片上传失败: " + error);
                                // 遮罩图片上传失败，继续生成（不带遮罩）
                                updateProgress(15, "遮罩图片上传失败，继续生成...");
                                callGenerateAPI();
                            }
                        }
                );
            } else {
                android.util.Log.e("GenerationActivity", "遮罩文件不存在: " + assetPath);
                // 遮罩文件不存在，继续生成（不带遮罩）
                updateProgress(15, "遮罩图片不存在，开始生成...");
                callGenerateAPI();
            }
        } catch (Exception e) {
            android.util.Log.e("GenerationActivity", "上传遮罩图片异常", e);
            // 出错后继续生成（不带遮罩）
            updateProgress(15, "遮罩图片处理失败，开始生成...");
            callGenerateAPI();
        }
    }

    /**
     * 调用AI生成API
     * 直接调用火山引擎大模型API
     */
    private void callGenerateAPI() {
        tvStatus.setText(stripHtmlTags("正在生成图片..."));
        showHorizontalProgressBar();
        speakStatus("AI正在生成您的照片，这可能需要几十秒时间，请耐心等待");

        // 记录开始时间
        generationStartTime = System.currentTimeMillis();

        StyleConfig styleConfig = configManager.getStyleConfig(styleId);

        // 获取原始prompt
        String originalPrompt = styleConfig != null ? styleConfig.getPrompt() : "";

        // 构建最终prompt
        String finalPrompt = originalPrompt;
        String maskFilePath = null; // 实际的文件路径（用于API调用）
        String maskImageUrl = null; // mask的URL（如果是URL）

        // 检查是否需要使用数组格式
        boolean needsArrayFormat = false;
        String configBackImage = styleConfig != null ? styleConfig.getBackImage() : null;  // 背景图（KV图，传递给大模型API作为图1）
        String[] configReferenceImages = styleConfig != null ? styleConfig.getReferenceImages() : null;

        // 判断是否需要数组格式：有backImage或referenceImages
        if ((configBackImage != null && !configBackImage.isEmpty()) ||
            (configReferenceImages != null && configReferenceImages.length > 0)) {
            needsArrayFormat = true;
        }

        android.util.Log.d("GenerationActivity", "========== API调用方式判断 ==========");
        android.util.Log.d("GenerationActivity", "configBackImage (KV图): " + configBackImage);
        android.util.Log.d("GenerationActivity", "configReferenceImages: " + java.util.Arrays.toString(configReferenceImages));
        android.util.Log.d("GenerationActivity", "needsArrayFormat: " + needsArrayFormat);
        android.util.Log.d("GenerationActivity", "=====================================");

        // 准备backImage URL（KV图，作为图1传递给大模型）
        if (configBackImage != null && !configBackImage.isEmpty()) {
            if (configBackImage.startsWith("http://") || configBackImage.startsWith("https://")) {
                // 直接使用配置中的URL
                maskImageUrl = configBackImage;
                android.util.Log.d("GenerationActivity", "使用配置中的backImage URL: " + maskImageUrl);
            } else {
                // 本地路径，尝试从OSS下载同名文件
                android.util.Log.d("GenerationActivity", "backImage是本地路径: " + configBackImage);

                // 构建OSS URL：https://file.jcoding.chat/application/com.jcoding.aiactivity/style/{configBackImage}
                String ossMaskUrl = "https://file.jcoding.chat/application/com.jcoding.aiactivity/style/" + configBackImage;
                android.util.Log.d("GenerationActivity", "尝试从OSS下载backImage: " + ossMaskUrl);

                // 尝试从OSS下载并缓存到本地，然后使用本地路径
                downloadAndCacheMaskFromOSS(ossMaskUrl, configBackImage);

                // 使用OSS URL
                maskImageUrl = ossMaskUrl;
                android.util.Log.d("GenerationActivity", "使用OSS backImage URL: " + maskImageUrl);
            }
        }

        // 数字人欢迎
        if (configManager.isDigitalHumanEnabled() && digitalHumanManager != null) {
            digitalHumanManager.performActionAndSpeak(
                    "introduce",
                    "正在为您生成照片，请稍候",
                    new DigitalHumanManager.DigitalHumanCallback() {
                        @Override
                        public void onSpeakStart(String gifPath) {
                            showDigitalHuman(gifPath);
                        }

                        @Override
                        public void onComplete() {
                            // 开始等待陪聊
                            startWaitingChitchat();
                            // 开始进度更新
                            startProgressUpdates();
                        }

                        @Override
                        public void onError(String error) {
                            android.util.Log.e("GenerationActivity", "Digital human error: " + error);
                            // 即使数字人出错，也继续流程
                            startWaitingChitchat();
                            startProgressUpdates();
                        }
                    }
            );
        } else {
            // 如果没有启用数字人，直接开始其他流程
            startWaitingChitchat();
            startProgressUpdates();
        }

        // 直接调用火山引擎大模型API，使用URL或本地文件路径
        // 优先使用URL（扫码上传情况），如果没有URL才使用本地文件
        String imagePathToUse;
        if (imageUrl != null && !imageUrl.isEmpty() && (imageUrl.startsWith("http://") || imageUrl.startsWith("https://"))) {
            // 使用URL（扫码上传情况）
            // 统一处理：所有URL通过NetworkUtils转换为火山引擎可访问的格式
            imagePathToUse = com.jcoding.aiactivity.utils.NetworkUtils.convertToDirectUrlViaServer(imageUrl);
            android.util.Log.d("GenerationActivity", "使用图片URL（已转换）: " + imagePathToUse);
        } else {
            // 使用本地文件路径
            imagePathToUse = photoFilePath;
            android.util.Log.d("GenerationActivity", "使用本地文件: " + imagePathToUse);
        }

        android.util.Log.d("GenerationActivity", "最终prompt: " + finalPrompt);

        // 获取API Key
        String apiKey = getVolcEngineApiKey();
        if (apiKey == null || apiKey.isEmpty()) {
            android.util.Log.e("GenerationActivity", "火山引擎API Key未配置");
            tvStatus.setText(stripHtmlTags("API Key未配置，请联系管理员"));
            hideAllProgressIndicators();
            return;
        }

        android.util.Log.d("GenerationActivity", "API Key已配置，长度: " + apiKey.length());

        // 创建API客户端
        com.jcoding.aiactivity.network.VolcEngineApiClient apiClient =
                new com.jcoding.aiactivity.network.VolcEngineApiClient(apiKey, this);

        android.util.Log.d("GenerationActivity", "开始发送请求到大模型...");

        // 根据配置选择API调用方式
        if (needsArrayFormat) {
            // 使用数组格式
            android.util.Log.d("GenerationActivity", "使用数组格式调用API");
            // 获取配置的生成质量
            String quality = configManager.getGenerationQuality();
            android.util.Log.d("GenerationActivity", "生成质量: " + quality);
            apiClient.generateImageWithArray(imagePathToUse, maskImageUrl, finalPrompt,
                    configBackImage, configReferenceImages, quality,
                    new com.jcoding.aiactivity.network.VolcEngineApiClient.GenerationCallback() {
                        @Override
                        public void onSuccess(String imageUrl) {
                            android.util.Log.d("GenerationActivity", "生成成功: " + imageUrl);
                            // 注意：不要在这里设置resultImageUrl，等上传完成后再设置
                            // resultImageUrl = imageUrl;  // 移除这行，避免在上传前显示火山引擎URL

                            // 在主线程中执行所有UI操作
                            runOnUiThread(() -> {
                                // 下载生成的图片并上传到OSS
                                uploadGeneratedResultToServer(imageUrl);
                            });
                        }

                        @Override
                        public void onError(String error) {
                            android.util.Log.e("GenerationActivity", "生成失败: " + error);

                            // 在主线程中执行UI操作
                            runOnUiThread(() -> {
                                tvStatus.setText(stripHtmlTags("生成失败: " + error));
                                hideAllProgressIndicators();
                                hideDigitalHuman();
                                speakStatus("生成失败，请重试");
                            });
                        }
                    }
            );
        } else {
            // 使用单图片格式
            android.util.Log.d("GenerationActivity", "使用单图片格式调用API");
            callVolcEngineApi(imagePathToUse, maskFilePath, finalPrompt);
        }
    }

    /**
     * 调用火山引擎大模型API
     */
    private void callVolcEngineApi(String imageFilePath, String maskImagePath, String prompt) {
        // 添加详细日志
        android.util.Log.d("GenerationActivity", "========== 开始调用火山引擎API ==========");
        android.util.Log.d("GenerationActivity", "图片路径: " + imageFilePath);
        android.util.Log.d("GenerationActivity", "遮罩路径: " + maskImagePath);
        android.util.Log.d("GenerationActivity", "Prompt内容: " + prompt);

        // 从配置中获取API Key
        String apiKey = getVolcEngineApiKey();
        if (apiKey == null || apiKey.isEmpty()) {
            android.util.Log.e("GenerationActivity", "火山引擎API Key未配置");
            tvStatus.setText(stripHtmlTags("API Key未配置，请联系管理员"));
            hideAllProgressIndicators();
            return;
        }

        android.util.Log.d("GenerationActivity", "API Key已配置，长度: " + apiKey.length());

        // 创建API客户端
        com.jcoding.aiactivity.network.VolcEngineApiClient apiClient =
                new com.jcoding.aiactivity.network.VolcEngineApiClient(apiKey, this);

        android.util.Log.d("GenerationActivity", "开始发送请求到大模型...");

        // 获取配置的生成质量
        String quality = configManager.getGenerationQuality();
        android.util.Log.d("GenerationActivity", "生成质量: " + quality);

        // 调用生成API（URL已经是域名格式）
        apiClient.generateImage(imageFilePath,
                maskImagePath,
                prompt,
                quality,
                new com.jcoding.aiactivity.network.VolcEngineApiClient.GenerationCallback() {
                    @Override
                    public void onSuccess(String imageUrl) {
                        android.util.Log.d("GenerationActivity", "生成成功: " + imageUrl);
                        // 注意：不要在这里设置resultImageUrl，等上传完成后再设置
                        // resultImageUrl = imageUrl;  // 移除这行，避免在上传前显示火山引擎URL

                        // 在主线程中执行所有UI操作
                        runOnUiThread(() -> {
                            // 下载生成的图片并上传到OSS
                            uploadGeneratedResultToServer(imageUrl);
                        });
                    }

                    @Override
                    public void onError(String error) {
                        android.util.Log.e("GenerationActivity", "生成失败: " + error);

                        // 在主线程中执行UI操作
                        runOnUiThread(() -> {
                            tvStatus.setText(stripHtmlTags("生成失败: " + error));
                            hideAllProgressIndicators();
                            hideDigitalHuman();
                            speakStatus("生成失败，请重试");
                        });
                    }
                }
        );
    }

    /**
     * 获取火山引擎API Key
     * 从通用设置中读取LLM API Key
     */
    private String getVolcEngineApiKey() {
        // 从ConfigManager读取LLM API Key（存储在通用设置中）
        String apiKey = configManager.getLlmApiKey();

        if (apiKey != null && !apiKey.isEmpty()) {
            android.util.Log.d("GenerationActivity", "已从配置中读取API Key");
            return apiKey;
        }

        android.util.Log.e("GenerationActivity", "API Key未配置，请在通用设置中输入大模型API_KEY");
        return "";
    }

    /**
     * 开始轮询生成状态
     */
    private void startPolling() {
        pollingRunnable = new Runnable() {
            @Override
            public void run() {
                checkGenerationStatus();
            }
        };
        handler.postDelayed(pollingRunnable, 3000);  // 每3秒检查一次
    }

    /**
     * 检查生成状态
     */
    private void checkGenerationStatus() {
        Map<String, String> params = new HashMap<>();
        params.put("task_id", currentTaskId);

        RetrofitClient.getInstance().getApiService()
                .getGenerationStatus(currentTaskId)
                .enqueue(new Callback<ApiService.GenerationStatusResponse>() {
                    @Override
                    public void onResponse(Call<ApiService.GenerationStatusResponse> call,
                                         Response<ApiService.GenerationStatusResponse> response) {
                        if (response.isSuccessful() && response.body() != null
                                && response.body().code == 200) {
                            GenerationTask task = response.body().data;
                            if (task != null) {
                                if (task.isCompleted()) {
                                    // 生成完成
                                    resultImageUrl = task.getResultUrl();
                                    displayResult();
                                } else if (task.isFailed()) {
                                    // 生成失败
                                    tvStatus.setText(stripHtmlTags("生成失败：" + task.getErrorMessage()));
                                    progressBar.setVisibility(View.GONE);
                                } else {
                                    // 继续轮询
                                    handler.postDelayed(pollingRunnable, 3000);
                                }
                            }
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiService.GenerationStatusResponse> call, Throwable t) {
                        handler.postDelayed(pollingRunnable, 3000);
                    }
                });
    }

    /**
     * 上传生成的结果图片到存储服务
     * 客户端下载火山引擎图片后直接上传文件（更快）
     */
    private void uploadGeneratedResultToServer(String generatedImageUrl) {
        android.util.Log.d("GenerationActivity", "========== 开始上传生成结果 ==========");
        android.util.Log.d("GenerationActivity", "火山引擎URL: " + generatedImageUrl);
        updateProgress(90, "正在保存生成结果...");

        // 使用后台线程下载图片并上传
        new Thread(() -> {
            try {
                // 1. 下载火山引擎图片到本地临时文件
                android.util.Log.d("GenerationActivity", "步骤1：下载火山引擎图片...");
                com.jcoding.aiactivity.network.VolcEngineApiClient apiClient =
                    new com.jcoding.aiactivity.network.VolcEngineApiClient("", this);

                android.graphics.Bitmap bitmap = apiClient.downloadImage(generatedImageUrl);

                if (bitmap == null) {
                    throw new Exception("下载图片失败");
                }

                android.util.Log.d("GenerationActivity", "图片下载成功，尺寸: " + bitmap.getWidth() + "x" + bitmap.getHeight());

                // 2. 保存到临时文件
                android.util.Log.d("GenerationActivity", "步骤2：保存到临时文件...");
                java.io.File tempDir = new java.io.File(getCacheDir(), "temp");
                if (!tempDir.exists()) {
                    tempDir.mkdirs();
                }

                String timestamp = String.valueOf(System.currentTimeMillis());
                java.io.File tempFile = new java.io.File(tempDir, "gen_" + timestamp + ".jpg");

                java.io.FileOutputStream fos = new java.io.FileOutputStream(tempFile);
                bitmap.compress(android.graphics.Bitmap.CompressFormat.JPEG, 95, fos);
                fos.flush();
                fos.close();

                android.util.Log.d("GenerationActivity", "图片已保存到临时文件: " + tempFile.getAbsolutePath() + ", 大小: " + tempFile.length() / 1024 + "KB");

                // 3. 上传文件到存储服务（根据策略自动选择TOS或OSS）
                android.util.Log.d("GenerationActivity", "步骤3：上传文件到存储服务...");

                // 在主线程更新UI
                runOnUiThread(() -> updateProgress(95, "正在上传..."));

                FileUploadManager.getInstance(this).uploadGeneratedFile(
                    tempFile,
                    "gen",
                    "generated",
                    sessionId,
                    null,
                    true,
                    new FileUploadManager.UploadCallback() {
                        @Override
                        public void onSuccess(String fileUrl) {
                            android.util.Log.d("GenerationActivity", "========== 上传成功 ==========");
                            android.util.Log.d("GenerationActivity", "文件URL: " + fileUrl);

                            // 通知手机端轮询机制：更新生成任务状态
                            notifyGenerationTaskComplete(fileUrl);

                            runOnUiThread(() -> {
                                resultImageUrl = fileUrl;
                                android.util.Log.d("GenerationActivity", "设置resultImageUrl为: " + resultImageUrl);

                                updateProgress(100, "生成完成！");

                                handler.postDelayed(new Runnable() {
                                    @Override
                                    public void run() {
                                        android.util.Log.d("GenerationActivity", "即将显示结果，resultImageUrl: " + resultImageUrl);
                                        hideAllProgressIndicators();
                                        displayResult();
                                    }
                                }, 500);
                            });
                        }

                        @Override
                        public void onError(String error) {
                            android.util.Log.e("GenerationActivity", "生成结果上传失败: " + error);

                            runOnUiThread(() -> {
                                tvStatus.setText(stripHtmlTags("生成成功，但保存失败"));
                                hideAllProgressIndicators();
                                android.widget.Toast.makeText(GenerationActivity.this, "图片保存失败: " + error, android.widget.Toast.LENGTH_LONG).show();
                                hideDigitalHuman();
                                speakStatus("生成完成");
                            });
                        }
                    }
                );

            } catch (Exception e) {
                android.util.Log.e("GenerationActivity", "上传生成结果异常", e);

                runOnUiThread(() -> {
                    tvStatus.setText(stripHtmlTags("生成成功，但保存失败"));
                    hideAllProgressIndicators();
                    android.widget.Toast.makeText(GenerationActivity.this, "图片保存失败: " + e.getMessage(), android.widget.Toast.LENGTH_LONG).show();
                    hideDigitalHuman();
                    speakStatus("生成完成");
                });
            }
        }).start();
    }

    /**
     * 通知手机端轮询机制：生成任务已完成
     */
    private void notifyGenerationTaskComplete(String resultUrl) {
        try {
            // 使用sessionId作为taskId，这样手机端可以轮询到对应的任务
            String taskId = sessionId != null ? sessionId : "gen_" + System.currentTimeMillis();

            android.util.Log.d("GenerationActivity", "通知手机端轮询：taskId=" + taskId + ", resultUrl=" + resultUrl);

            // 构建请求体
            java.util.HashMap<String, Object> request = new java.util.HashMap<>();
            request.put("task_id", taskId);
            request.put("status", "completed");
            request.put("progress", 100);
            request.put("result_url", resultUrl);
            request.put("status_text", "生成完成");

            // 调用后端API更新任务状态
            com.jcoding.aiactivity.network.RetrofitClient.getInstance()
                .getApiService()
                .updateGenerationTask(request)
                .enqueue(new retrofit2.Callback<com.jcoding.aiactivity.network.ApiService.BasicResponse>() {
                    @Override
                    public void onResponse(retrofit2.Call<com.jcoding.aiactivity.network.ApiService.BasicResponse> call,
                                           retrofit2.Response<com.jcoding.aiactivity.network.ApiService.BasicResponse> response) {
                        if (response.isSuccessful() && response.body() != null && response.body().code == 200) {
                            android.util.Log.d("GenerationActivity", "任务状态更新成功，手机端将收到通知");
                        } else {
                            android.util.Log.w("GenerationActivity", "任务状态更新失败: " + response.code());
                        }
                    }

                    @Override
                    public void onFailure(retrofit2.Call<com.jcoding.aiactivity.network.ApiService.BasicResponse> call, Throwable t) {
                        android.util.Log.e("GenerationActivity", "任务状态更新请求失败", t);
                        // 不阻塞主流程，即使更新失败也继续
                    }
                });
        } catch (Exception e) {
            android.util.Log.e("GenerationActivity", "通知手机端轮询失败", e);
        }
    }

    /**
     * 显示生成结果 - 满屏显示图片并弹出二维码
     */
    private void displayResult() {
        // 清理temp文件夹中的上传图片
        cleanupTempFiles();

        // 取消所有进度更新和等待任务
        if (handler != null) {
            if (progressUpdateRunnable != null) {
                handler.removeCallbacks(progressUpdateRunnable);
            }
            if (spinnerAnimationRunnable != null) {
                handler.removeCallbacks(spinnerAnimationRunnable);
            }
            if (chitchatRunnable != null) {
                handler.removeCallbacks(chitchatRunnable);
            }
            // 取消所有callback和messages，确保没有遗留任务
            handler.removeCallbacksAndMessages(null);
        }

        updateProgress(100, "生成完成！");

        // 隐藏所有UI元素，只显示全屏对话框
        hideAllUIElements();

        // 播放祝贺语音（使用数字人）
        if (digitalHumanManager != null && configManager.isDigitalHumanEnabledForModule("ai_show")) {
            String currentStyleName = getStyleName(styleId);
            String congratulationMessage = "恭喜您，您的" + currentStyleName + "作品生成成功！请扫描页面右上角的二维码下载图片。温馨提示：如果您使用微信扫码，请在手机浏览器中打开下载链接。";

            // 只播放语音，不显示动画（因为全屏对话框已覆盖）
            digitalHumanManager.speak(congratulationMessage, new DigitalHumanManager.DigitalHumanCallback() {
                @Override
                public void onSpeakStart(String gifPath) {
                    // 不显示数字人动画，保持全屏对话框显示
                }

                @Override
                public void onComplete() {
                    // 不做任何操作
                }

                @Override
                public void onError(String error) {
                    android.util.Log.e("GenerationActivity", "Digital human error: " + error);
                }
            });
        }

        // 启用语音输入（用户可以使用语音命令进行操作）
        if (configManager.isVoiceCommandEnabled()) {
            enableVoiceInput(true);
        }

        // 显示全屏结果对话框
        showFullscreenResult();

        // 自动推送到内场秀
        if (configManager.isAutoPushInnerEnabled()) {
            pushToInnerShow();
            // 显示推送成功提示（只播放语音，不显示动画）
            if (digitalHumanManager != null && configManager.isDigitalHumanEnabledForModule("ai_show")) {
                // 使用新的handler，因为原来的handler已经被清空了
                Handler newHandler = new Handler(Looper.getMainLooper());
                newHandler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        digitalHumanManager.speak("您的作品已推送到内场秀大屏幕",
                            new DigitalHumanManager.DigitalHumanCallback() {
                                @Override
                                public void onSpeakStart(String gifPath) {
                                    // 不显示数字人动画，保持全屏对话框显示
                                }

                                @Override
                                public void onComplete() {
                                    // 不做任何操作
                                }

                                @Override
                                public void onError(String error) {
                                    android.util.Log.e("GenerationActivity", "Digital human error: " + error);
                                }
                            });
                    }
                }, 3000); // 延迟3秒，等祝贺完成
            }
        }
    }

    /**
     * 显示全屏结果和二维码对话框
     */
    private void showFullscreenResult() {
        android.util.Log.d("GenerationActivity", "========== 显示全屏结果 ==========");
        android.util.Log.d("GenerationActivity", "resultImageUrl: " + resultImageUrl);

        // 创建全屏对话框
        fullscreenDialog = new Dialog(this, android.R.style.Theme_Black_NoTitleBar_Fullscreen);
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_fullscreen_result, null);
        fullscreenDialog.setContentView(dialogView);

        // 确保对话框全屏显示
        android.view.Window window = fullscreenDialog.getWindow();
        if (window != null) {
            android.view.WindowManager.LayoutParams params = window.getAttributes();
            params.width = android.view.WindowManager.LayoutParams.MATCH_PARENT;
            params.height = android.view.WindowManager.LayoutParams.MATCH_PARENT;
            window.setAttributes(params);
        }

        ImageView ivFullscreenResult = dialogView.findViewById(R.id.iv_fullscreen_result);
        ImageView ivQrcode = dialogView.findViewById(R.id.iv_qrcode);
        TextView tvQrcodeHint = dialogView.findViewById(R.id.tv_qrcode_hint);
        Button btnClose = dialogView.findViewById(R.id.btn_close_fullscreen);
        View qrcodeContainer = dialogView.findViewById(R.id.qrcode_container);

        // 加载并显示生成的图片
        android.util.Log.d("GenerationActivity", "加载图片URL: " + resultImageUrl);

        // 先显示加载提示，避免黑屏
        tvQrcodeHint.setText("正在加载生成的图片...");
        tvQrcodeHint.setVisibility(View.VISIBLE);

        com.bumptech.glide.Glide.with(this)
                .load(resultImageUrl)
                .placeholder(android.graphics.Color.parseColor("#333333"))  // 深灰色占位符，避免黑屏
                .listener(new com.bumptech.glide.request.RequestListener<android.graphics.drawable.Drawable>() {
                    @Override
                    public boolean onLoadFailed(@androidx.annotation.Nullable com.bumptech.glide.load.engine.GlideException e, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                        android.util.Log.e("GenerationActivity", "结果图片加载失败", e);
                        tvQrcodeHint.setText("图片加载失败，请重试");
                        tvQrcodeHint.setVisibility(View.VISIBLE);
                        return false;
                    }

                    @Override
                    public boolean onResourceReady(android.graphics.drawable.Drawable resource, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                        android.util.Log.d("GenerationActivity", "结果图片加载成功");
                        // 图片加载成功后隐藏提示
                        tvQrcodeHint.setVisibility(View.GONE);
                        return false;
                    }
                })
                .into(ivFullscreenResult);

        // 生成二维码
        try {
            // 转换为代理URL用于二维码（用户扫描后使用代理访问）
            String qrcodeUrl = com.jcoding.aiactivity.utils.NetworkUtils.convertToProxyUrlDomain(resultImageUrl);
            android.util.Log.d("GenerationActivity", "生成二维码，URL: " + qrcodeUrl);
            // 使用ZXing生成二维码
            com.google.zxing.Writer writer = new com.google.zxing.qrcode.QRCodeWriter();
            int width = 140;
            int height = 140;
            com.google.zxing.common.BitMatrix bitMatrix = writer.encode(qrcodeUrl,
                    com.google.zxing.BarcodeFormat.QR_CODE, width, height);

            android.graphics.Bitmap qrcodeBitmap = android.graphics.Bitmap.createBitmap(width, height,
                    android.graphics.Bitmap.Config.RGB_565);

            for (int x = 0; x < width; x++) {
                for (int y = 0; y < height; y++) {
                    qrcodeBitmap.setPixel(x, y, bitMatrix.get(x, y) ?
                            android.graphics.Color.BLACK : android.graphics.Color.WHITE);
                }
            }

            ivQrcode.setImageBitmap(qrcodeBitmap);
            android.util.Log.d("GenerationActivity", "二维码已生成，使用域名URL");
        } catch (Exception e) {
            android.util.Log.e("GenerationActivity", "生成二维码失败: " + e.getMessage(), e);
            tvQrcodeHint.setText("二维码生成失败");
        }

        // 关闭按钮点击事件 - 关闭对话框并返回首页
        btnClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 取消自动关闭定时器
                if (autoCloseRunnable != null) {
                    autoCloseHandler.removeCallbacks(autoCloseRunnable);
                }

                // 关闭对话框
                if (fullscreenDialog != null && fullscreenDialog.isShowing()) {
                    fullscreenDialog.dismiss();
                    fullscreenDialog = null;
                }
                // 返回到百变秀首页
                navigateToPhotoStyleHome();
            }
        });

        // 显示对话框
        fullscreenDialog.show();
        android.util.Log.d("GenerationActivity", "全屏对话框已显示");

        // 启动1分钟自动隐藏定时器
        startQrcodeTimeout(qrcodeContainer, tvQrcodeHint);

        // 启动对话框自动关闭定时器
        startDialogAutoClose();
    }

    /**
     * 启动二维码自动隐藏定时器
     * 根据配置的自动关闭时间来隐藏二维码，与图片显示时间保持一致
     * @param qrcodeContainer 二维码容器
     * @param tvQrcodeHint 提示文本
     */
    private void startQrcodeTimeout(View qrcodeContainer, TextView tvQrcodeHint) {
        // 取消之前的定时器
        if (qrcodeTimeoutRunnable != null) {
            qrcodeTimeoutHandler.removeCallbacks(qrcodeTimeoutRunnable);
        }

        // 获取自动关闭时间配置
        int autoCloseTime = configManager.getAutoCloseTime();

        // 如果设置为0，表示手动关闭，不启动定时器
        if (autoCloseTime == 0) {
            android.util.Log.i("GenerationActivity", "二维码设置为手动关闭模式");
            return;
        }

        // 创建新的定时器
        qrcodeTimeoutRunnable = new Runnable() {
            @Override
            public void run() {
                // 隐藏二维码
                if (qrcodeContainer != null) {
                    qrcodeContainer.setVisibility(View.GONE);
                }
                if (tvQrcodeHint != null) {
                    tvQrcodeHint.setVisibility(View.GONE);
                }
                android.util.Log.i("GenerationActivity", "二维码已自动隐藏");
            }
        };

        // 使用配置的自动关闭时间（与图片显示时间一致）
        qrcodeTimeoutHandler.postDelayed(qrcodeTimeoutRunnable, autoCloseTime * 1000);
        android.util.Log.i("GenerationActivity", "二维码将在 " + autoCloseTime + " 秒后自动隐藏");
    }

    /**
     * 启动对话框自动关闭定时器
     */
    private void startDialogAutoClose() {
        // 取消之前的定时器
        if (autoCloseRunnable != null) {
            autoCloseHandler.removeCallbacks(autoCloseRunnable);
        }

        // 获取自动关闭时间配置
        int autoCloseTime = configManager.getAutoCloseTime();

        // 如果设置为0，表示手动关闭，不启动定时器
        if (autoCloseTime == 0) {
            android.util.Log.i("GenerationActivity", "结果展示时间设置为手动关闭，不自动关闭对话框");
            return;
        }

        android.util.Log.i("GenerationActivity", "对话框将在 " + autoCloseTime + " 秒后自动关闭");

        // 创建新的定时器
        autoCloseRunnable = new Runnable() {
            @Override
            public void run() {
                // 关闭对话框并返回首页
                if (fullscreenDialog != null && fullscreenDialog.isShowing()) {
                    fullscreenDialog.dismiss();
                    fullscreenDialog = null;
                }
                navigateToPhotoStyleHome();
                android.util.Log.i("GenerationActivity", "对话框已自动关闭");
            }
        };

        // 延迟关闭
        autoCloseHandler.postDelayed(autoCloseRunnable, autoCloseTime * 1000);
    }

    /**
     * 推送到内场秀
     */
    private void pushToInnerShow() {
        try {
            com.jcoding.aiactivity.manager.InnerShowDataManager dataManager =
                    com.jcoding.aiactivity.manager.InnerShowDataManager.getInstance(this);

            // 创建生成结果记录
            com.jcoding.aiactivity.manager.InnerShowDataManager.GenerationResult result =
                    new com.jcoding.aiactivity.manager.InnerShowDataManager.GenerationResult();

            result.id = java.util.UUID.randomUUID().toString();
            result.styleId = styleId;
            result.styleName = getStyleName(styleId);
            result.originalImagePath = photoFilePath;
            result.resultImagePath = resultImageUrl;
            result.signature = ""; // 签名暂时为空
            result.timestamp = System.currentTimeMillis();

            // 保存到数据管理器
            dataManager.addGenerationResult(result);

            // 发送广播通知InnerActivity
            Intent broadcast = new Intent("com.jcoding.aiactivity.INNER_SHOW_UPDATE");
            broadcast.putExtra("action", "new_image");
            broadcast.putExtra("result_id", result.id);
            sendBroadcast(broadcast);

            android.util.Log.i("GenerationActivity", "已推送到内场秀: " + result.id);
        } catch (Exception e) {
            android.util.Log.e("GenerationActivity", "推送内场秀失败", e);
        }
    }

    /**
     * 获取风格名称
     */
    private String getStyleName(String styleId) {
        List<StyleConfig> styles = configManager.getStyleConfigs();
        for (StyleConfig style : styles) {
            if (style.getStyleId().equals(styleId)) {
                return style.getName();
            }
        }
        return "未知风格";
    }

    /**
     * 跳转到结果页
     */
    private void navigateToResult() {
        Intent intent = new Intent(this, ResultActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra("original_photo_path", photoFilePath);
        intent.putExtra("result_image_url", resultImageUrl);
        intent.putExtra("generation_time", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",
                Locale.getDefault()).format(new Date()));
        startActivity(intent);

        // 可选：关闭当前Activity，避免返回
        finish();
    }

    /**
     * 语音播报状态
     */
    private void speakStatus(String message) {
        if (configManager.isVoiceGuidanceEnabled() &&
            voiceManager != null && voiceManager.isInitialized()) {
            voiceManager.speakText(message, null);
        }
    }

    /**
     * 等待期间陪聊
     * 数字人在画面中间进行友好的互动聊天
     * 保持固定动画，避免频繁切换导致跳帧
     */
    private void startWaitingChitchat() {
        String[] waitingTips = {
                "AI正在精心创作您的照片，请稍候片刻",
                "我们正在进行细节优化，请耐心等待",
                "马上就要完成了，感谢您的等待",
                "正在进行最后的处理，请稍候",
                "别着急哦，好作品值得等待",
                "AI正在努力为您创作中"
        };

        final int[] tipIndex = {0};

        // 立即开始第一次播报
        speakStatus("AI正在精心创作您的照片，请稍候片刻，我会在画面中间陪您等待");

        // 保存到成员变量，以便取消
        chitchatRunnable = new Runnable() {
            @Override
            public void run() {
                if (tipIndex[0] < waitingTips.length) {
                    // 只播放语音，不切换动画（避免跳帧）
                    speakStatus(waitingTips[tipIndex[0]]);

                    tipIndex[0]++;
                    // 每12秒播报一次（比之前的15秒更频繁）
                    handler.postDelayed(this, 12000);
                }
            }
        };

        // 5秒后开始第二次播报
        handler.postDelayed(chitchatRunnable, 5000);
    }

    /**
     * 下载结果
     * 下载完成后自动隐藏二维码
     */
    private void downloadResult() {
        showToast("正在下载图片...");

        // 使用Glide下载图片到相册
        com.bumptech.glide.Glide.with(this)
                .asBitmap()
                .load(resultImageUrl)
                .into(new com.bumptech.glide.request.target.CustomTarget<android.graphics.Bitmap>() {
                    @Override
                    public void onResourceReady(@NonNull android.graphics.Bitmap bitmap,
                                                @Nullable com.bumptech.glide.request.transition.Transition<? super android.graphics.Bitmap> transition) {
                        // 保存到相册
                        saveBitmapToGallery(bitmap, "AI_Show_" + System.currentTimeMillis());
                        showToast("图片已保存到相册");

                        // 下载完成后隐藏二维码容器
                        if (fullscreenDialog != null && fullscreenDialog.isShowing()) {
                            View dialogView = fullscreenDialog.findViewById(android.R.id.content);
                            if (dialogView != null) {
                                View qrcodeContainer = dialogView.findViewById(R.id.qrcode_container);
                                if (qrcodeContainer != null) {
                                    qrcodeContainer.setVisibility(View.GONE);
                                }
                            }
                        }
                    }

                    @Override
                    public void onLoadCleared(@Nullable android.graphics.drawable.Drawable placeholder) {
                    }

                    @Override
                    public void onLoadFailed(@Nullable android.graphics.drawable.Drawable errorDrawable) {
                        showToast("下载失败，请重试");
                    }
                });
    }

    /**
     * 保存Bitmap到相册
     */
    private void saveBitmapToGallery(android.graphics.Bitmap bitmap, String filename) {
        try {
            // 保存到Pictures目录
            android.content.ContentValues values = new android.content.ContentValues();
            values.put(android.provider.MediaStore.Images.Media.DISPLAY_NAME, filename + ".jpg");
            values.put(android.provider.MediaStore.Images.Media.MIME_TYPE, "image/jpeg");
            values.put(android.provider.MediaStore.Images.Media.RELATIVE_PATH, android.os.Environment.DIRECTORY_PICTURES + "/AIActivity");

            android.net.Uri uri = getContentResolver().insert(android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values);

            if (uri != null) {
                java.io.OutputStream outputStream = getContentResolver().openOutputStream(uri);
                if (outputStream != null) {
                    bitmap.compress(android.graphics.Bitmap.CompressFormat.JPEG, 100, outputStream);
                    outputStream.close();
                }
            }
        } catch (Exception e) {
            android.util.Log.e("GenerationActivity", "保存图片失败: " + e.getMessage(), e);
        }
    }

    /**
     * 分享结果
     */
    private void shareResult() {
        showToast("分享功能开发中");
        // TODO: 实现分享功能
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();

        // 停止语音识别
        if (speechRecognizerManager != null && speechRecognizerManager.isListening()) {
            speechRecognizerManager.stopListening();
        }

        // 取消所有回调
        if (handler != null) {
            if (pollingRunnable != null) {
                handler.removeCallbacks(pollingRunnable);
            }
            if (progressUpdateRunnable != null) {
                handler.removeCallbacks(progressUpdateRunnable);
            }
            if (spinnerAnimationRunnable != null) {
                handler.removeCallbacks(spinnerAnimationRunnable);
            }
        }

        // 取消二维码定时器
        if (qrcodeTimeoutHandler != null && qrcodeTimeoutRunnable != null) {
            qrcodeTimeoutHandler.removeCallbacks(qrcodeTimeoutRunnable);
        }

        // 取消自动关闭定时器
        if (autoCloseHandler != null && autoCloseRunnable != null) {
            autoCloseHandler.removeCallbacks(autoCloseRunnable);
        }

        // 关闭对话框
        if (fullscreenDialog != null && fullscreenDialog.isShowing()) {
            fullscreenDialog.dismiss();
            fullscreenDialog = null;
        }
    }

    // ==================== 进度显示相关方法 ====================

    /**
     * 显示传统进度条
     */
    private void showProgressBar() {
        if (progressBar != null) {
            progressBar.setVisibility(View.VISIBLE);
        }
        if (progressBarHorizontal != null) {
            progressBarHorizontal.setVisibility(View.GONE);
        }
        if (ivLoadingSpinner != null) {
            ivLoadingSpinner.setVisibility(View.GONE);
        }
        if (tvProgressPercentage != null) {
            tvProgressPercentage.setVisibility(View.GONE);
        }
        if (tvEta != null) {
            tvEta.setVisibility(View.GONE);
        }
    }

    /**
     * 显示水平进度条
     */
    private void showHorizontalProgressBar() {
        if (progressBar != null) {
            progressBar.setVisibility(View.GONE);
        }
        if (progressBarHorizontal != null) {
            progressBarHorizontal.setVisibility(View.VISIBLE);
            progressBarHorizontal.setProgress(0);
        }
        if (tvProgressPercentage != null) {
            tvProgressPercentage.setVisibility(View.VISIBLE);
            tvProgressPercentage.setText("0%");
        }
        if (tvEta != null) {
            tvEta.setVisibility(View.VISIBLE);
            tvEta.setText("预计剩余: --");
        }
        if (ivLoadingSpinner != null) {
            ivLoadingSpinner.setVisibility(View.GONE);
        }
    }

    /**
     * 隐藏所有进度指示器
     */
    private void hideAllProgressIndicators() {
        if (progressBar != null) {
            progressBar.setVisibility(View.GONE);
        }
        if (progressBarHorizontal != null) {
            progressBarHorizontal.setVisibility(View.GONE);
        }
        if (ivLoadingSpinner != null) {
            ivLoadingSpinner.setVisibility(View.GONE);
        }
        if (tvProgressPercentage != null) {
            tvProgressPercentage.setVisibility(View.GONE);
        }
        if (tvEta != null) {
            tvEta.setVisibility(View.GONE);
        }
    }

    /**
     * 去除HTML标签，防止显示HTML编码
     * 将HTML标签转换为纯文本或移除
     */
    private String stripHtmlTags(String html) {
        if (html == null || html.isEmpty()) {
            return html;
        }
        // 移除所有HTML标签
        String text = html.replaceAll("<[^>]*>", "");
        // 解码HTML实体（如 &nbsp; &lt; 等）
        text = android.text.Html.fromHtml(text, android.text.Html.FROM_HTML_MODE_LEGACY).toString();
        return text.trim();
    }

    /**
     * 更新进度
     */
    private void updateProgress(int progress, String status) {
        this.currentProgress = progress;

        // 更新进度条
        if (progressBarHorizontal != null) {
            progressBarHorizontal.setProgress(progress);
        }

        // 更新百分比显示
        if (tvProgressPercentage != null) {
            tvProgressPercentage.setText(progress + "%");
        }

        // 更新状态文字 - 去除HTML标签
        if (tvStatus != null && status != null) {
            tvStatus.setText(stripHtmlTags(status));
        }

        // 更新预计剩余时间
        updateEta();
    }

    /**
     * 更新预计剩余时间
     */
    private void updateEta() {
        if (estimatedTime <= 0 || currentProgress <= 0) {
            return;
        }

        long elapsedTime = (System.currentTimeMillis() - generationStartTime) / 1000; // 秒
        if (elapsedTime <= 0) {
            return;
        }

        // 计算预计剩余时间：基于已过时间和进度
        int estimatedTotalSeconds = (int) (elapsedTime * 100 / currentProgress);
        int remainingSeconds = estimatedTotalSeconds - (int) elapsedTime;

        if (remainingSeconds < 0) {
            remainingSeconds = 0;
        }

        // 格式化时间显示
        String etaText;
        if (remainingSeconds >= 60) {
            int minutes = remainingSeconds / 60;
            int seconds = remainingSeconds % 60;
            etaText = String.format("预计剩余: %d分%d秒", minutes, seconds);
        } else {
            etaText = String.format("预计剩余: %d秒", remainingSeconds);
        }

        if (tvEta != null) {
            tvEta.setText(etaText);
        }
    }

    /**
     * 开始进度更新
     */
    private void startProgressUpdates() {
        if (progressUpdateRunnable != null) {
            handler.removeCallbacks(progressUpdateRunnable);
        }

        progressUpdateRunnable = new Runnable() {
            @Override
            public void run() {
                // 模拟进度增长（20% -> 95%）
                if (currentProgress < 95) {
                    // 根据已过时间计算进度
                    long elapsedTime = (System.currentTimeMillis() - generationStartTime) / 1000;
                    int simulatedProgress = 20 + (int) ((elapsedTime * 75) / estimatedTime);
                    if (simulatedProgress > 95) {
                        simulatedProgress = 95;
                    }
                    if (simulatedProgress > currentProgress) {
                        updateProgress(simulatedProgress, null);
                    }

                    // 每秒更新一次
                    handler.postDelayed(this, 1000);
                }
            }
        };

        // 延迟1秒后开始更新
        handler.postDelayed(progressUpdateRunnable, 1000);
    }

    // ==================== 数字人相关方法 ====================

    /**
     * 显示数字人GIF
     */
    private void showDigitalHuman(String gifPath) {
        if (gifPath == null || gifPath.isEmpty()) {
            return;
        }

        if (digitalHumanContainer != null && ivDigitalHuman != null) {
            digitalHumanContainer.setVisibility(View.VISIBLE);

            // 使用Glide加载GIF
            try {
                com.bumptech.glide.Glide.with(this)
                        .load(new java.io.File(gifPath))
                        .into(ivDigitalHuman);
            } catch (Exception e) {
                android.util.Log.e("GenerationActivity", "Failed to load digital human GIF: " + e.getMessage());
            }
        }
    }

    /**
     * 隐藏数字人
     */
    private void hideDigitalHuman() {
        if (digitalHumanContainer != null) {
            digitalHumanContainer.setVisibility(View.GONE);
        }
    }

    // ==================== 语音识别相关方法 ====================

    /**
     * 启用/禁用语音输入
     */
    private void enableVoiceInput(boolean enable) {
        isVoiceInputEnabled = enable;
        if (btnVoiceInput != null) {
            if (enable) {
                btnVoiceInput.setVisibility(View.VISIBLE);
                btnVoiceInput.setEnabled(true);
            } else {
                btnVoiceInput.setVisibility(View.GONE);
                btnVoiceInput.setEnabled(false);
            }
        }
    }

    /**
     * 开始语音识别
     */
    private void startVoiceRecognition() {
        if (!isVoiceInputEnabled) {
            showToast("语音输入不可用");
            return;
        }

        if (speechRecognizerManager.isListening()) {
            speechRecognizerManager.stopListening();
            btnVoiceInput.setText("🎤 语音指令");
            return;
        }

        // 更新按钮状态
        btnVoiceInput.setText("🎤 正在聆听...");
        btnVoiceInput.setEnabled(false);

        // 开始识别
        speechRecognizerManager.startListening(
                new SpeechRecognizerManager.RecognitionListener() {
                    @Override
                    public void onResult(String result, boolean isFinal) {
                        if (isFinal) {
                            // 恢复按钮状态
                            btnVoiceInput.setText("🎤 语音指令");
                            btnVoiceInput.setEnabled(true);

                            // 处理语音命令
                            handleVoiceCommand(result);
                        }
                    }

                    @Override
                    public void onError(int errorCode, String errorMsg) {
                        // 恢复按钮状态
                        btnVoiceInput.setText("🎤 语音指令");
                        btnVoiceInput.setEnabled(true);

                        showToast("语音识别失败: " + errorMsg);
                    }
                }
        );
    }

    /**
     * 处理语音命令
     */
    private void handleVoiceCommand(String command) {
        if (command == null || command.isEmpty()) {
            return;
        }

        android.util.Log.i("GenerationActivity", "Voice command: " + command);

        // 标准化命令文本（去除空格和标点）
        String normalizedCommand = command.trim().toLowerCase()
                .replaceAll("[，。！？、；：\"\"\'\'（）]", "");

        // 处理命令
        if (containsKeyword(normalizedCommand, new String[]{"重新生成", "重试", "再来一次", "重新来"})) {
            // 重新生成
            handleRegenerateCommand();
        } else if (containsKeyword(normalizedCommand, new String[]{"取消", "算了", "不要了", "停止"})) {
            // 取消生成
            handleCancelCommand();
        } else if (containsKeyword(normalizedCommand, new String[]{"查看", "显示", "看看", "预览"})) {
            // 查看结果
            handleViewResultCommand();
        } else if (containsKeyword(normalizedCommand, new String[]{"下载", "保存"})) {
            // 下载结果
            handleDownloadCommand();
        } else if (containsKeyword(normalizedCommand, new String[]{"分享", "发给"})) {
            // 分享结果
            handleShareCommand();
        } else {
            // 未识别的命令
            speakStatus("抱歉，我没有理解您的指令");
            showToast("未识别的指令: " + command);
        }
    }

    /**
     * 检查命令是否包含关键词
     */
    private boolean containsKeyword(String command, String[] keywords) {
        for (String keyword : keywords) {
            if (command.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 处理重新生成命令
     */
    private void handleRegenerateCommand() {
        if (resultImageUrl != null && !resultImageUrl.isEmpty()) {
            // 如果已经有结果，询问是否重新生成
            speakStatus("好的，正在为您重新生成");
            showToast("正在重新生成...");

            // 重置状态
            resultImageUrl = null;
            currentProgress = 0;

            // 重新开始生成
            startGeneration();
        } else if (currentTaskId != null && !currentTaskId.isEmpty()) {
            // 如果正在生成中，取消并重新开始
            speakStatus("好的，正在重新开始");
            showToast("正在重新生成...");

            // 取消当前任务
            if (handler != null && pollingRunnable != null) {
                handler.removeCallbacks(pollingRunnable);
            }

            // 重置状态
            currentTaskId = null;
            currentProgress = 0;

            // 重新开始生成
            startGeneration();
        } else {
            speakStatus("正在为您生成照片");
            startGeneration();
        }
    }

    /**
     * 处理取消命令
     */
    private void handleCancelCommand() {
        speakStatus("好的，已取消生成");

        // 取消所有回调
        if (handler != null) {
            if (pollingRunnable != null) {
                handler.removeCallbacks(pollingRunnable);
            }
            if (progressUpdateRunnable != null) {
                handler.removeCallbacks(progressUpdateRunnable);
            }
        }

        // 停止语音识别
        if (speechRecognizerManager.isListening()) {
            speechRecognizerManager.stopListening();
        }

        // 隐藏所有进度指示器
        hideAllProgressIndicators();
        hideDigitalHuman();

        // 返回
        finish();
    }

    /**
     * 处理查看结果命令
     */
    private void handleViewResultCommand() {
        if (resultImageUrl != null && !resultImageUrl.isEmpty()) {
            speakStatus("正在为您展示结果");
            navigateToResult();
        } else {
            speakStatus("照片还在生成中，请稍候");
            showToast("照片还在生成中...");
        }
    }

    /**
     * 处理下载命令
     */
    private void handleDownloadCommand() {
        if (resultImageUrl != null && !resultImageUrl.isEmpty()) {
            speakStatus("正在保存照片");
            downloadResult();
        } else {
            speakStatus("照片还未生成完成");
            showToast("照片还未生成完成");
        }
    }

    /**
     * 处理分享命令
     */
    private void handleShareCommand() {
        if (resultImageUrl != null && !resultImageUrl.isEmpty()) {
            speakStatus("正在打开分享");
            shareResult();
        } else {
            speakStatus("照片还未生成完成");
            showToast("照片还未生成完成");
        }
    }

    /**
     * 将assets中的文件复制到缓存目录
     */
    private java.io.File copyAssetToFile(String assetPath, String outputFileName) {
        java.io.InputStream is = null;
        java.io.OutputStream os = null;
        try {
            // 创建缓存文件
            java.io.File outputFile = new java.io.File(getCacheDir(), outputFileName);

            // 如果文件已存在，直接返回
            if (outputFile.exists()) {
                return outputFile;
            }

            // 从assets读取
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

    /**
     * 隐藏所有UI元素，只显示全屏对话框
     */
    private void hideAllUIElements() {
        // 方法1：直接隐藏Activity的窗口内容视图
        android.view.Window window = getWindow();
        if (window != null) {
            android.view.View decorView = window.getDecorView();
            if (decorView != null) {
                // 获取内容视图（LinearLayout包含ActionBar和Content）
                android.view.ViewGroup contentView = decorView.findViewById(android.R.id.content);
                if (contentView != null && contentView.getChildCount() > 0) {
                    // 隐藏第一个子视图（ScrollView）
                    android.view.View mainView = contentView.getChildAt(0);
                    mainView.setVisibility(View.GONE);
                }
            }
        }

        android.util.Log.d("GenerationActivity", "已隐藏所有UI元素");
    }

    /**
     * 返回到百变秀主页面（风格选择页）
     * 清除中间的所有Activity（PhotoSelectionActivity等）
     */
    private void navigateToPhotoStyleHome() {
        android.util.Log.d("GenerationActivity", "返回到百变秀主页面");

        // 创建Intent返回到PhotoStyleActivity（百变秀主页面）
        android.content.Intent intent = new android.content.Intent(this, PhotoStyleActivity.class);
        // 使用CLEAR_TOP清除栈中目标Activity之上的所有Activity
        // 使用SINGLE_TOP如果目标Activity已存在则复用
        intent.setFlags(android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP |
                        android.content.Intent.FLAG_ACTIVITY_SINGLE_TOP);

        startActivity(intent);

        // 不调用finishAffinity()，让系统自动管理任务栈
        finish();
    }

    /**
     * 清理temp文件夹中的上传图片
     */
    private void cleanupTempFiles() {
        try {
            java.io.File tempDir = new java.io.File(getCacheDir(), "temp");
            if (tempDir.exists() && tempDir.isDirectory()) {
                java.io.File[] files = tempDir.listFiles();
                if (files != null) {
                    for (java.io.File file : files) {
                        if (file.isFile() && file.getName().startsWith("uploaded_photo")) {
                            boolean deleted = file.delete();
                            android.util.Log.d("GenerationActivity", "清理temp文件: " + file.getName() + ", 成功: " + deleted);
                        }
                    }
                }
            }
        } catch (Exception e) {
            android.util.Log.e("GenerationActivity", "清理temp文件异常", e);
        }
    }

    /**
     * 从OSS下载遮罩图片并缓存到本地
     * @param ossUrl OSS代理URL
     * @param originalFilename 原始文件名（用于缓存）
     */
    private void downloadAndCacheMaskFromOSS(String ossUrl, String originalFilename) {
        new Thread(() -> {
            try {
                android.util.Log.d("GenerationActivity", "开始从OSS下载遮罩: " + ossUrl);

                // 使用OkHttp下载图片
                okhttp3.OkHttpClient client = new okhttp3.OkHttpClient.Builder()
                        .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                        .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                        .build();

                okhttp3.Request request = new okhttp3.Request.Builder()
                        .url(ossUrl)
                        .build();

                okhttp3.Response response = client.newCall(request).execute();

                if (response.isSuccessful() && response.body() != null) {
                    byte[] imageBytes = response.body().bytes();

                    // 缓存到本地文件
                    java.io.File cacheDir = new java.io.File(getCacheDir(), "masks");
                    if (!cacheDir.exists()) {
                        cacheDir.mkdirs();
                    }
                    java.io.File maskFile = new java.io.File(cacheDir, originalFilename);

                    java.io.FileOutputStream fos = new java.io.FileOutputStream(maskFile);
                    fos.write(imageBytes);
                    fos.close();

                    android.util.Log.d("GenerationActivity", "遮罩已缓存到: " + maskFile.getAbsolutePath());
                } else {
                    android.util.Log.e("GenerationActivity", "下载遮罩失败，响应码: " + response.code());
                }
            } catch (Exception e) {
                android.util.Log.e("GenerationActivity", "下载遮罩异常: " + e.getMessage(), e);
            }
        }).start();
    }

    /**
     * 从OSS加载遮罩并显示
     * @param maskFilename 遮罩文件名（如 background/styleBk.png）
     */
    private void loadMaskFromOSS(String maskFilename) {
        // 构建OSS URL
        String ossMaskUrl = "https://file.jcoding.chat/application/com.jcoding.aiactivity/style/" + maskFilename;
        android.util.Log.d("GenerationActivity", "从OSS加载遮罩: " + ossMaskUrl);

        Glide.with(this)
                .load(ossMaskUrl)
                .listener(new com.bumptech.glide.request.RequestListener<android.graphics.drawable.Drawable>() {
                    @Override
                    public boolean onLoadFailed(@androidx.annotation.Nullable com.bumptech.glide.load.engine.GlideException e, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                        android.util.Log.e("GenerationActivity", "OSS遮罩加载失败: " + e.getMessage() + "，尝试从assets加载");
                        // OSS加载失败，fallback到assets
                        loadMaskFromAssets(maskFilename);
                        return false;
                    }

                    @Override
                    public boolean onResourceReady(android.graphics.drawable.Drawable resource, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                        android.util.Log.d("GenerationActivity", "OSS遮罩加载成功");
                        ivMaskOverlay.setAlpha(1.0f);
                        return false;
                    }
                })
                .into(ivMaskOverlay);
    }

    /**
     * 从assets加载遮罩（最后的fallback）
     * @param maskFilename 遮罩文件名
     */
    private void loadMaskFromAssets(String maskFilename) {
        String maskAssetPath = "style/" + maskFilename;
        android.util.Log.d("GenerationActivity", "从assets加载遮罩: " + maskAssetPath);

        Glide.with(this)
                .load("file:///android_asset/" + maskAssetPath)
                .listener(new com.bumptech.glide.request.RequestListener<android.graphics.drawable.Drawable>() {
                    @Override
                    public boolean onLoadFailed(@androidx.annotation.Nullable com.bumptech.glide.load.engine.GlideException e, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                        android.util.Log.e("GenerationActivity", "assets遮罩加载失败，遮罩不可用");
                        return false;
                    }

                    @Override
                    public boolean onResourceReady(android.graphics.drawable.Drawable resource, java.lang.Object model, com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                        android.util.Log.d("GenerationActivity", "assets遮罩加载成功");
                        ivMaskOverlay.setAlpha(1.0f);
                        return false;
                    }
                })
                .into(ivMaskOverlay);
    }
}
