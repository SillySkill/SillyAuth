package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.engine.GlideException;
import com.bumptech.glide.request.RequestListener;
import com.bumptech.glide.request.target.Target;
import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.StyleConfig;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.DigitalHumanManager;
import com.jcoding.aiactivity.manager.InnerShowDataManager;
import com.jcoding.aiactivity.manager.InnerShowNetworkClient;
import com.jcoding.aiactivity.manager.InnerShowNetworkConfigManager;
import com.jcoding.aiactivity.utils.Constants;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 结果展示页
 * 展示AI生成的最终结果，支持保存和分享
 */
public class ResultActivity extends BaseActivity {

    private ImageView ivResult;
    private ImageView ivOriginal;
    private TextView tvStyleName;
    private TextView tvGenerationTime;
    private Button btnBack;
    private Button btnClose;  // 关闭按钮
    private Button btnRegenerate;
    private Button btnSignature;
    private Button btnCheckIn;
    private Button btnPushInner;
    private TextView tvOfflineMode;

    // 数字人相关
    private FrameLayout digitalHumanContainer;
    private ImageView ivDigitalHuman;
    private DigitalHumanManager digitalHumanManager;

    private String styleId;
    private String styleName;
    private String originalPhotoPath;
    private String resultImageUrl;
    private Bitmap resultBitmap;
    private String resultId; // 生成结果ID
    private String userSignature; // 用户签名
    private boolean isCheckedIn = false; // 是否已签到

    private ExecutorService executorService = Executors.newSingleThreadExecutor();
    private InnerShowDataManager innerShowDataManager;
    private InnerShowNetworkClient networkClient;
    private InnerShowNetworkConfigManager networkConfigManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);

        // 获取参数
        styleId = getIntent().getStringExtra(Constants.EXTRA_STYLE_ID);
        originalPhotoPath = getIntent().getStringExtra("original_photo_path");
        resultImageUrl = getIntent().getStringExtra("result_image_url");
        String generationTime = getIntent().getStringExtra("generation_time");

        // 生成唯一ID
        resultId = "result_" + System.currentTimeMillis();

        // 初始化内场秀数据管理器
        innerShowDataManager = InnerShowDataManager.getInstance(this);
        networkClient = InnerShowNetworkClient.getInstance(this);
        networkConfigManager = InnerShowNetworkConfigManager.getInstance(this);

        // 保存生成结果到内场秀数据管理器
        saveGenerationResult();

        initViews();
        initDigitalHuman();
        loadStyleInfo();
        loadOriginalPhoto();
        loadResultImage();

        // 根据配置决定是否显示生成时间
        if (configManager.isShowGenerationTimeEnabled()) {
            if (generationTime != null) {
                tvGenerationTime.setText("生成时间：" + generationTime);
                tvGenerationTime.setVisibility(View.VISIBLE);
            } else {
                // 如果没有传入时间，显示当前时间
                String currentTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
                        .format(new Date());
                tvGenerationTime.setText("生成时间：" + currentTime);
                tvGenerationTime.setVisibility(View.VISIBLE);
            }
        } else {
            tvGenerationTime.setVisibility(View.GONE);
        }
    }

    private void initViews() {
        ivResult = findViewById(R.id.iv_result);
        ivOriginal = findViewById(R.id.iv_original);
        tvStyleName = findViewById(R.id.tv_style_name);
        tvGenerationTime = findViewById(R.id.tv_generation_time);
        btnBack = findViewById(R.id.btn_back);
        btnClose = findViewById(R.id.btn_close);  // 初始化关闭按钮
        btnRegenerate = findViewById(R.id.btn_regenerate);
        btnSignature = findViewById(R.id.btn_signature);
        btnCheckIn = findViewById(R.id.btn_checkin);
        btnPushInner = findViewById(R.id.btn_push_inner);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        // 数字人相关
        digitalHumanContainer = findViewById(R.id.digital_human_container);
        ivDigitalHuman = findViewById(R.id.iv_digital_human);

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        // 关闭按钮 - 返回百变秀首页
        btnClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 启动百变秀首页，并清除其上的所有Activity
                Intent intent = new Intent(ResultActivity.this, PhotoStyleActivity.class);
                intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
                startActivity(intent);
                // finish()会在系统启动PhotoStyleActivity后自动调用
            }
        });

        btnRegenerate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                regenerate();
            }
        });

        // 添加签名
        btnSignature.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openSignatureActivity();
            }
        });

        // 签到
        btnCheckIn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                performCheckIn();
            }
        });

        // 推送到内场秀
        btnPushInner.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                pushToInnerShow();
            }
        });
    }

    /**
     * 加载风格信息
     */
    private void loadStyleInfo() {
        StyleConfig styleConfig = configManager.getStyleConfig(styleId);
        if (styleConfig != null) {
            styleName = styleConfig.getName();
            tvStyleName.setText("风格：" + styleName);
        }
    }

    /**
     * 初始化数字人
     */
    private void initDigitalHuman() {
        digitalHumanContainer = findViewById(R.id.digital_human_container);
        ivDigitalHuman = findViewById(R.id.iv_digital_human);

        if (!configManager.isDigitalHumanEnabledForModule("ai_show")) {
            digitalHumanContainer.setVisibility(View.GONE);
            return;
        }

        digitalHumanManager = DigitalHumanManager.getInstance(this);
        digitalHumanContainer.setVisibility(View.VISIBLE);

        // 应用配置的数字人位置
        String position = configManager.getDigitalHumanPosition();
        android.widget.RelativeLayout.LayoutParams params =
            (android.widget.RelativeLayout.LayoutParams) digitalHumanContainer.getLayoutParams();

        // 清除所有对齐规则
        params.removeRule(android.widget.RelativeLayout.ALIGN_PARENT_TOP);
        params.removeRule(android.widget.RelativeLayout.ALIGN_PARENT_BOTTOM);
        params.removeRule(android.widget.RelativeLayout.ALIGN_PARENT_START);
        params.removeRule(android.widget.RelativeLayout.ALIGN_PARENT_END);

        // 根据配置设置位置
        switch (position) {
            case "left_top":
                params.addRule(android.widget.RelativeLayout.ALIGN_PARENT_TOP, android.widget.RelativeLayout.TRUE);
                params.addRule(android.widget.RelativeLayout.ALIGN_PARENT_START, android.widget.RelativeLayout.TRUE);
                break;
            case "right_top":
                params.addRule(android.widget.RelativeLayout.ALIGN_PARENT_TOP, android.widget.RelativeLayout.TRUE);
                params.addRule(android.widget.RelativeLayout.ALIGN_PARENT_END, android.widget.RelativeLayout.TRUE);
                break;
            case "left_bottom":
                params.addRule(android.widget.RelativeLayout.ALIGN_PARENT_BOTTOM, android.widget.RelativeLayout.TRUE);
                params.addRule(android.widget.RelativeLayout.ALIGN_PARENT_START, android.widget.RelativeLayout.TRUE);
                break;
            case "right_bottom":
            default:
                params.addRule(android.widget.RelativeLayout.ALIGN_PARENT_BOTTOM, android.widget.RelativeLayout.TRUE);
                params.addRule(android.widget.RelativeLayout.ALIGN_PARENT_END, android.widget.RelativeLayout.TRUE);
                break;
        }
        digitalHumanContainer.setLayoutParams(params);

        // 显示默认数字人动画（使用Glide加载GIF）
        updateDigitalHumanImage(digitalHumanManager.getDefaultGif());

        // 数字人祝贺
        digitalHumanManager.congratulate(
            "恭喜您，您的" + styleName + "作品生成成功！您可以保存或分享这张美照",
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
                    android.util.Log.e("ResultActivity", "Digital human error: " + error);
                }
            }
        );
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
        FrameLayout.LayoutParams imageParams = (FrameLayout.LayoutParams) ivDigitalHuman.getLayoutParams();
        imageParams.width = sizePx;
        imageParams.height = sizePx;
        ivDigitalHuman.setLayoutParams(imageParams);

        // 获取缩放类型
        String scaleType = configManager.getDigitalHumanScaleType();
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
                                String scaleType = configManager.getDigitalHumanScaleType();
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
                android.util.Log.e("ResultActivity", "GIF file not found: " + assetPath);
            }
        } catch (Exception e) {
            android.util.Log.e("ResultActivity", "Failed to load GIF: " + gifPath, e);
        }
    }

    /**
     * 加载原始照片
     */
    private void loadOriginalPhoto() {
        if (originalPhotoPath != null) {
            Bitmap bitmap = BitmapFactory.decodeFile(originalPhotoPath);
            if (bitmap != null) {
                ivOriginal.setImageBitmap(bitmap);
            }
        }
    }

    /**
     * 加载结果图片
     */
    private void loadResultImage() {
        if (resultImageUrl != null) {
            // 从网络下载
            if (resultImageUrl.startsWith("http")) {
                downloadImageFromNetwork(resultImageUrl);
            } else {
                // 从本地加载
                resultBitmap = BitmapFactory.decodeFile(resultImageUrl);
                if (resultBitmap != null) {
                    ivResult.setImageBitmap(resultBitmap);
                } else {
                    showToast("图片加载失败");
                }
            }
        } else {
            // 如果没有图片URL，显示占位符
            ivResult.setBackgroundColor(android.graphics.Color.parseColor("#333333"));
        }
    }

    /**
     * 从网络下载图片（使用Glide，避免黑屏）
     */
    private void downloadImageFromNetwork(String imageUrl) {
        // 使用Glide加载，自动处理缓存和占位符
        Glide.with(this)
                .load(imageUrl)
                .placeholder(Color.parseColor("#333333"))  // 深灰色占位符，避免黑屏
                .listener(new RequestListener<Drawable>() {
                    @Override
                    public boolean onLoadFailed(@Nullable GlideException e, Object model, Target<Drawable> target, boolean isFirstResource) {
                        android.util.Log.e("ResultActivity", "图片加载失败", e);
                        return false;
                    }

                    @Override
                    public boolean onResourceReady(Drawable resource, Object model, Target<Drawable> target, com.bumptech.glide.load.DataSource dataSource, boolean isFirstResource) {
                        // 图片加载成功，转换为Bitmap保存
                        if (resource instanceof android.graphics.drawable.BitmapDrawable) {
                            resultBitmap = ((android.graphics.drawable.BitmapDrawable) resource).getBitmap();
                        }
                        return false;
                    }
                })
                .into(ivResult);
    }

    /**
     * 保存图片到相册
     */
    private void downloadImage() {
        if (resultBitmap == null) {
            showToast("图片尚未加载完成");
            return;
        }

        executorService.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    // 保存到应用私有目录
                    File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
                    String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
                    String fileName = "AI_Result_" + timeStamp + ".jpg";
                    File file = new File(storageDir, fileName);

                    FileOutputStream fos = new FileOutputStream(file);
                    resultBitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
                    fos.flush();
                    fos.close();

                    // 通知系统扫描
                    Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
                    mediaScanIntent.setData(Uri.fromFile(file));
                    sendBroadcast(mediaScanIntent);

                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(ResultActivity.this,
                                    "图片已保存：" + file.getAbsolutePath(),
                                    Toast.LENGTH_LONG).show();
                        }
                    });
                } catch (IOException e) {
                    e.printStackTrace();
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            showToast("保存失败：" + e.getMessage());
                        }
                    });
                }
            }
        });
    }

    /**
     * 分享图片
     */
    private void shareImage() {
        if (resultBitmap == null) {
            showToast("图片尚未加载完成");
            return;
        }

        executorService.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    // 保存到缓存
                    File cacheDir = getExternalCacheDir();
                    File file = new File(cacheDir, "ai_result_share.jpg");
                    FileOutputStream fos = new FileOutputStream(file);
                    resultBitmap.compress(Bitmap.CompressFormat.JPEG, 90, fos);
                    fos.flush();
                    fos.close();

                    Uri uri = Uri.fromFile(file);

                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Intent shareIntent = new Intent(Intent.ACTION_SEND);
                            shareIntent.setType("image/jpeg");
                            shareIntent.putExtra(Intent.EXTRA_STREAM, uri);
                            shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                            startActivity(Intent.createChooser(shareIntent, "分享到"));
                        }
                    });
                } catch (IOException e) {
                    e.printStackTrace();
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            showToast("分享失败：" + e.getMessage());
                        }
                    });
                }
            }
        });
    }

    /**
     * 重新生成
     */
    private void regenerate() {
        if (originalPhotoPath == null) {
            showToast("无法重新生成：原始照片丢失");
            return;
        }

        Intent intent = new Intent(this, GenerationActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra("photo_path", originalPhotoPath);
        startActivity(intent);
        finish();
    }

    /**
     * 保存生成结果到内场秀数据管理器
     */
    private void saveGenerationResult() {
        InnerShowDataManager.GenerationResult result = new InnerShowDataManager.GenerationResult();
        result.id = resultId;
        result.styleId = styleId;
        result.styleName = styleName;
        result.originalImagePath = originalPhotoPath;
        result.resultImageUrl = resultImageUrl;
        result.signature = userSignature;

        innerShowDataManager.addGenerationResult(result);
    }

    /**
     * 打开签名页面
     */
    private static final int REQUEST_CODE_SIGNATURE = 1001;

    private void openSignatureActivity() {
        Intent intent = new Intent(this, SignatureActivity.class);
        intent.putExtra("result_id", resultId);
        intent.putExtra("result_image_url", resultImageUrl);
        intent.putExtra("style_name", styleName);
        startActivityForResult(intent, REQUEST_CODE_SIGNATURE);
    }

    /**
     * 执行签到
     */
    private void performCheckIn() {
        if (isCheckedIn) {
            showToast("您已经签到过了");
            return;
        }

        InnerShowDataManager.CheckInRecord record = new InnerShowDataManager.CheckInRecord();
        record.userName = "用户"; // 可以从登录信息获取
        record.signature = userSignature != null ? userSignature : "";

        innerShowDataManager.addCheckInRecord(record);
        isCheckedIn = true;

        showToast("签到成功！已加入到内场秀名单");
        btnCheckIn.setEnabled(false);
        btnCheckIn.setText("✓ 已签到");
    }

    /**
     * 推送到内场秀
     */
    private void pushToInnerShow() {
        // 更新生成结果
        InnerShowDataManager.GenerationResult result = innerShowDataManager.getGenerationResult(resultId);
        if (result != null) {
            result.signature = userSignature;
            innerShowDataManager.updateGenerationResult(result);

            // 标记为已推送
            innerShowDataManager.markAsPushedToInner(resultId);

            // 检查是否是主服务器模式
            if (networkConfigManager.isServerMode()) {
                // 主服务器模式：本设备就是内场秀设备，直接发送本地广播
                Intent broadcast = new Intent("com.jcoding.aiactivity.INNER_SHOW_UPDATE");
                broadcast.putExtra("action", "new_image");
                broadcast.putExtra("result_id", resultId);
                sendBroadcast(broadcast);
                showToast("已推送到内场秀大屏！");
            } else {
                // 客户端模式：通过网络推送到内场秀设备
                networkClient.pushGenerationResult(result, new InnerShowNetworkClient.NetworkCallback() {
                    @Override
                    public void onSuccess(String resultResponse) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                showToast("已推送到内场秀大屏！");
                            }
                        });
                    }

                    @Override
                    public void onError(String error) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                showToast("推送失败: " + error + "，已保存到本地");
                            }
                        });
                    }
                });

                // 同时发送本地广播（同一设备的情况）
                Intent broadcast = new Intent("com.jcoding.aiactivity.INNER_SHOW_UPDATE");
                broadcast.putExtra("action", "new_image");
                broadcast.putExtra("result_id", resultId);
                sendBroadcast(broadcast);
            }

            // 设置为当前显示图片
            innerShowDataManager.setCurrentDisplayImage(resultId);
        }

        // 打开内场秀页面
        Intent intent = new Intent(this, InnerActivity.class);
        startActivity(intent);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_CODE_SIGNATURE && resultCode == RESULT_OK && data != null) {
            String signatureType = data.getStringExtra("signature_type");

            if ("image".equals(signatureType)) {
                String signaturePath = data.getStringExtra("signature_path");
                userSignature = "[签名图片] " + signaturePath;
                showToast("签名已保存");
            } else if ("text".equals(signatureType)) {
                String signatureText = data.getStringExtra("signature_text");
                userSignature = signatureText;
                showToast("签名已保存：" + signatureText);
            }

            // 更新生成结果
            InnerShowDataManager.GenerationResult result = innerShowDataManager.getGenerationResult(resultId);
            if (result != null) {
                result.signature = userSignature;
                innerShowDataManager.updateGenerationResult(result);
            }

            btnSignature.setText("✓ 已签名");
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
    protected void onDestroy() {
        super.onDestroy();
        if (executorService != null) {
            executorService.shutdown();
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
}
