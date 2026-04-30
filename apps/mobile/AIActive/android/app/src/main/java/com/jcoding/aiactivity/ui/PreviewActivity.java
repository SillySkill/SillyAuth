package com.jcoding.aiactivity.ui;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageCaptureException;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.LifecycleOwner;

import com.google.common.util.concurrent.ListenableFuture;
import com.bumptech.glide.Glide;
import com.bumptech.glide.load.DataSource;
import com.bumptech.glide.load.engine.GlideException;
import com.bumptech.glide.request.RequestListener;
import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.CameraDeviceManager;
import com.jcoding.aiactivity.utils.Constants;
import com.jcoding.aiactivity.utils.PhotoUploadHelper;
import com.jcoding.aiactivity.utils.VoiceCaptureHelper;
import com.jcoding.aiactivity.widget.PersonGuidanceView;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ExecutionException;

/**
 * 拍照预览页
 * 使用CameraX实现实时预览和拍照
 * 强制将采集的图片转成竖屏模式
 */
public class PreviewActivity extends BaseActivity {

    private static final int REQUEST_CODE_PERMISSIONS = 1001;
    private static final int REQUEST_CODE_UPLOAD = 1002;  // 上传照片请求码

    /**
     * 获取所需权限列表（根据SDK版本动态调整）
     * Android 10+不需要存储权限即可保存到应用私有目录
     */
    private String[] getRequiredPermissions() {
        if (android.os.Build.VERSION.SDK_INT <= android.os.Build.VERSION_CODES.P) {
            return new String[]{
                    Manifest.permission.CAMERA,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE,
                    Manifest.permission.RECORD_AUDIO
            };
        } else {
            return new String[]{
                    Manifest.permission.CAMERA,
                    Manifest.permission.RECORD_AUDIO
            };
        }
    }

    // 上传配置
    private static final String UPLOAD_URL = "https://www.jcoding.chat/upload/api";

    private androidx.camera.view.PreviewView previewView;
    private ImageView ivCaptured;
    private ImageView ivReferOverlay;
    private Button btnCapture;
    private Button btnRetake;
    private Button btnConfirm;
    private Button btnBack;
    private TextView tvOfflineMode;
    private TextView tvCountdown;  // 倒计时显示
    private LinearLayout layoutConfirmButtons;  // 确认按钮容器

    private ProcessCameraProvider cameraProvider;
    private ImageCapture imageCapture;
    private Bitmap capturedBitmap;
    private String photoFilePath;

    private String styleId;
    private int mode;
    private String capturedImageUrl;  // 上传或拍摄的图片URL

    // 上传助手
    private PhotoUploadHelper photoUploadHelper;
    // 语音识别助手
    private VoiceCaptureHelper voiceCaptureHelper;

    // 倒计时相关
    private int countdownSeconds;  // 倒计时秒数（从配置读取）
    private android.os.CountDownTimer countDownTimer;  // 倒计时定时器

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_preview);

        // 获取参数
        styleId = getIntent().getStringExtra(Constants.EXTRA_STYLE_ID);
        mode = getIntent().getIntExtra(Constants.EXTRA_MODE, Constants.MODE_INVITE_CODE);

        // 读取拍照倒计时配置
        countdownSeconds = configManager.getPhotoCountdownSeconds();

        // 初始化上传助手
        photoUploadHelper = new PhotoUploadHelper(this, UPLOAD_URL);

        // 初始化语音识别助手
        voiceCaptureHelper = new VoiceCaptureHelper(this);

        initViews();
        checkPermissionsAndStartCamera();
    }

    private void initViews() {
        previewView = findViewById(R.id.preview_view);
        ivCaptured = findViewById(R.id.iv_captured);
        ivReferOverlay = findViewById(R.id.iv_refer_overlay);
        btnCapture = findViewById(R.id.btn_capture);
        btnRetake = findViewById(R.id.btn_retake);
        btnConfirm = findViewById(R.id.btn_confirm);
        btnBack = findViewById(R.id.btn_back);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);
        tvCountdown = findViewById(R.id.tv_countdown);  // 初始化倒计时TextView
        layoutConfirmButtons = findViewById(R.id.layout_confirm_buttons);  // 初始化确认按钮容器

        // 加载并显示前遮盖图（拍照前就显示）
        loadStyleBackground();

        setupListeners();
        startVoiceCapture();
    }

    /**
     * 启动语音拍照功能
     */
    private void startVoiceCapture() {
        // 检查录音权限
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED) {
            voiceCaptureHelper.startListening(new VoiceCaptureHelper.VoiceCaptureCallback() {
                @Override
                public void onCaptureCommand(String recognizedText) {
                    Log.d("PreviewActivity", "语音指令: " + recognizedText);
                    runOnUiThread(() -> {
                        showToast("语音指令: " + recognizedText);
                        // 延迟500ms后拍照，给用户反馈时间
                        btnCapture.postDelayed(() -> takePhoto(), 500);
                    });
                }

                @Override
                public void onError(String error) {
                    Log.e("PreviewActivity", "语音识别错误: " + error);
                }
            });
            Log.d("PreviewActivity", "语音拍照已启动");
        } else {
            Log.w("PreviewActivity", "未授予录音权限，语音拍照功能不可用");
        }
    }

    /**
     * 从style/background目录随机加载一张图片作为叠加层
     */
    /**
     * 根据选择的风格加载并显示前遮盖图
     * 前遮盖图在拍照前和拍照后都显示
     */
    private void loadStyleBackground() {
        try {
            // 获取风格配置
            com.jcoding.aiactivity.entity.StyleConfig styleConfig = configManager.getStyleConfig(styleId);

            if (styleConfig == null) {
                android.util.Log.w("PreviewActivity", "未找到风格配置: " + styleId);
                ivReferOverlay.setVisibility(View.GONE);
                return;
            }

            // 获取前遮盖图路径（使用maskImage）
            String backgroundPath = styleConfig.getMaskImage();
            if (backgroundPath == null || backgroundPath.isEmpty()) {
                android.util.Log.w("PreviewActivity", "风格未配置前遮盖图");
                ivReferOverlay.setVisibility(View.GONE);
                return;
            }

            // 构建完整路径
            String fullPath = "style/" + backgroundPath;
            android.util.Log.d("PreviewActivity", "加载前遮盖图: " + fullPath);

            // 使用ConfigManager加载图片
            Bitmap bitmap = configManager.loadImageFromAssets(fullPath);

            if (bitmap != null) {
                ivReferOverlay.setScaleType(ImageView.ScaleType.FIT_CENTER);
                ivReferOverlay.setAdjustViewBounds(true);
                ivReferOverlay.setAlpha(0.6f); // 60%透明度
                ivReferOverlay.setImageBitmap(bitmap);
                // 立即显示前遮盖图
                ivReferOverlay.setVisibility(View.VISIBLE);
                android.util.Log.d("PreviewActivity", "前遮盖图已显示: " + backgroundPath);
            } else {
                android.util.Log.w("PreviewActivity", "前遮盖图加载失败: " + fullPath);
                ivReferOverlay.setVisibility(View.GONE);
            }

        } catch (Exception e) {
            android.util.Log.e("PreviewActivity", "加载前遮盖图异常", e);
            ivReferOverlay.setVisibility(View.GONE);
        }
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnCapture.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showCaptureOptionsDialog();
            }
        });

        btnRetake.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                retakePhoto();
            }
        });

        btnConfirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                confirmPhoto();
            }
        });
    }

    /**
     * 检查权限并启动相机
     */
    private void checkPermissionsAndStartCamera() {
        if (allPermissionsGranted()) {
            startCamera();
        } else {
            ActivityCompat.requestPermissions(this, getRequiredPermissions(), REQUEST_CODE_PERMISSIONS);
        }
    }

    /**
     * 检查是否所有权限都已授予
     */
    private boolean allPermissionsGranted() {
        for (String permission : getRequiredPermissions()) {
            if (ContextCompat.checkSelfPermission(this, permission)
                    != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        return true;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                          @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            // 直接检查本次权限请求结果
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }

            if (allGranted) {
                startCamera();
            } else {
                showToast("需要相机权限才能使用此功能");
                finish();
            }
        }
    }

    /**
     * 启动相机
     */
    private void startCamera() {
        // 检查是否选择了WiFi摄像头
        CameraDeviceManager cameraDeviceManager = CameraDeviceManager.getInstance(this);
        if (cameraDeviceManager.isRtspCamera()) {
            showToast("WiFi摄像头暂不支持实时预览，请使用其他摄像头");
            // TODO: 后续可以添加RTSP流的播放支持
            return;
        }

        ListenableFuture<ProcessCameraProvider> cameraProviderFuture =
                ProcessCameraProvider.getInstance(this);

        cameraProviderFuture.addListener(new Runnable() {
            @Override
            public void run() {
                try {
                    cameraProvider = cameraProviderFuture.get();

                    // 预览
                    Preview preview = new Preview.Builder().build();
                    preview.setSurfaceProvider(previewView.getSurfaceProvider());

                    // 图片捕获
                    imageCapture = new ImageCapture.Builder()
                            .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                            .build();

                    // 使用CameraDeviceManager获取选择的摄像头
                    CameraSelector cameraSelector = cameraDeviceManager.getCameraSelector();
                    if (cameraSelector == null) {
                        cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;
                        Log.w("PreviewActivity", "无法获取CameraSelector，使用默认后置摄像头");
                    }

                    // 绑定到生命周期
                    cameraProvider.unbindAll();
                    cameraProvider.bindToLifecycle(
                            (LifecycleOwner) PreviewActivity.this,
                            cameraSelector,
                            preview,
                            imageCapture
                    );

                    // 显示当前使用的摄像头信息
                    CameraDeviceManager.CameraInfo selectedCamera = cameraDeviceManager.getSelectedCamera();
                    if (selectedCamera != null) {
                        Log.d("PreviewActivity", "使用摄像头: " + selectedCamera.getCameraName());
                    }
                } catch (ExecutionException | InterruptedException e) {
                    e.printStackTrace();
                    showToast("相机启动失败");
                }
            }
        }, ContextCompat.getMainExecutor(this));
    }

    /**
     * 拍照
     */
    private void takePhoto() {
        if (imageCapture == null) {
            return;
        }

        // 创建文件
        File photoFile = createPhotoFile();
        photoFilePath = photoFile.getAbsolutePath();

        ImageCapture.OutputFileOptions outputOptions =
                new ImageCapture.OutputFileOptions.Builder(photoFile).build();

        // 拍照并保存
        imageCapture.takePicture(
                outputOptions,
                ContextCompat.getMainExecutor(this),
                new ImageCapture.OnImageSavedCallback() {
                    @Override
                    public void onImageSaved(@NonNull ImageCapture.OutputFileResults output) {
                        // 加载并处理照片，保持宽高比适配屏幕
                        capturedBitmap = loadAndRotateToPortrait(photoFilePath);

                        if (capturedBitmap != null) {
                            // 保存处理后的图片
                            saveBitmapToFile(capturedBitmap, photoFilePath);

                            // 显示照片，使用fitCenter保持宽高比
                            ivCaptured.setScaleType(ImageView.ScaleType.FIT_CENTER);
                            ivCaptured.setAdjustViewBounds(true);
                            ivCaptured.setImageBitmap(capturedBitmap);
                            ivCaptured.setVisibility(View.VISIBLE);
                            previewView.setVisibility(View.GONE);

                            // 前遮盖图保持显示（已经在拍照前显示）
                            // 照片在前遮盖图下面

                            // 停止语音监听（拍照后不需要语音控制）
                            voiceCaptureHelper.stopListening();

                            // 切换按钮 - 显示居中的确认按钮容器
                            btnCapture.setVisibility(View.GONE);
                            layoutConfirmButtons.setVisibility(View.VISIBLE);

                            Log.d("PreviewActivity", "照片已处理并显示，保持宽高比");
                        } else {
                            showToast("照片处理失败");
                        }
                    }

                    @Override
                    public void onError(@NonNull ImageCaptureException exception) {
                        showToast("拍照失败：" + exception.getMessage());
                    }
                }
        );
    }

    /**
     * 加载图片并保持正确的宽高比，适配大屏幕显示
     * 横屏照片会进行中心裁剪，高度撑满，保持宽高比
     * @param filePath 图片文件路径
     * @return 处理后的Bitmap
     */
    private Bitmap loadAndRotateToPortrait(String filePath) {
        try {
            // 获取屏幕宽度
            int screenWidth = getResources().getDisplayMetrics().widthPixels;
            int screenHeight = getResources().getDisplayMetrics().heightPixels;

            // 获取图片的EXIF旋转信息
            ExifInterface exif = new ExifInterface(filePath);
            int rotation = exif.getAttributeInt(ExifInterface.TAG_ORIENTATION,
                    ExifInterface.ORIENTATION_NORMAL);

            // 加载原始图片
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inJustDecodeBounds = true;
            BitmapFactory.decodeFile(filePath, options);

            Log.d("PreviewActivity", "屏幕尺寸: " + screenWidth + "x" + screenHeight);
            Log.d("PreviewActivity", "原始图片尺寸: " + options.outWidth + "x" + options.outHeight);

            // 计算采样率，基于屏幕宽度，避免内存溢出
            int scale = 1;
            if (options.outWidth > screenWidth * 2) {
                scale = (int) Math.ceil(options.outWidth / (float) (screenWidth * 2));
            }

            options.inJustDecodeBounds = false;
            options.inSampleSize = scale;

            Bitmap bitmap = BitmapFactory.decodeFile(filePath, options);

            if (bitmap == null) {
                Log.e("PreviewActivity", "无法加载图片: " + filePath);
                return null;
            }

            // 读取EXIF旋转角度
            int rotationDegrees = 0;
            switch (rotation) {
                case ExifInterface.ORIENTATION_ROTATE_90:
                    rotationDegrees = 90;
                    break;
                case ExifInterface.ORIENTATION_ROTATE_180:
                    rotationDegrees = 180;
                    break;
                case ExifInterface.ORIENTATION_ROTATE_270:
                    rotationDegrees = 270;
                    break;
                default:
                    rotationDegrees = 0;
                    break;
            }

            Log.d("PreviewActivity", "加载后图片: " + bitmap.getWidth() + "x" + bitmap.getHeight()
                    + ", EXIF旋转: " + rotationDegrees + "度");

            // 应用EXIF旋转
            if (rotationDegrees != 0) {
                Matrix matrix = new Matrix();
                matrix.postRotate(rotationDegrees);
                Bitmap rotatedBitmap = Bitmap.createBitmap(bitmap, 0, 0,
                        bitmap.getWidth(), bitmap.getHeight(), matrix, true);

                if (rotatedBitmap != bitmap) {
                    bitmap.recycle();
                }
                bitmap = rotatedBitmap;

                Log.d("PreviewActivity", "应用EXIF旋转后: " + bitmap.getWidth() + "x" + bitmap.getHeight());
            }

            // 检查是否为横屏照片（宽>高）
            boolean isLandscape = bitmap.getWidth() > bitmap.getHeight();

            if (isLandscape) {
                Log.d("PreviewActivity", "检测到横屏照片，进行中心裁剪");

                // 横屏照片：中心裁剪，使高度撑满屏幕高度，保持宽高比
                int bitmapWidth = bitmap.getWidth();
                int bitmapHeight = bitmap.getHeight();

                // 计算目标高度（屏幕高度）
                int targetHeight = screenHeight;
                // 根据宽高比计算目标宽度
                int targetWidth = (int) (bitmapWidth * ((float) targetHeight / bitmapHeight));

                Log.d("PreviewActivity", "横屏照片缩放: 从" + bitmapWidth + "x" + bitmapHeight +
                      "到" + targetWidth + "x" + targetHeight);

                // 先缩放到目标尺寸
                Bitmap scaledBitmap = Bitmap.createScaledBitmap(bitmap, targetWidth, targetHeight, true);
                if (scaledBitmap != bitmap) {
                    bitmap.recycle();
                }
                bitmap = scaledBitmap;

                // 如果缩放后宽度超过屏幕宽度，进行中心裁剪
                if (bitmap.getWidth() > screenWidth) {
                    int cropX = (bitmap.getWidth() - screenWidth) / 2;
                    Bitmap croppedBitmap = Bitmap.createBitmap(bitmap, cropX, 0, screenWidth, screenHeight);
                    if (croppedBitmap != bitmap) {
                        bitmap.recycle();
                    }
                    bitmap = croppedBitmap;

                    Log.d("PreviewActivity", "中心裁剪后: " + bitmap.getWidth() + "x" + bitmap.getHeight());
                }
            } else {
                // 竖屏照片：正常处理
                Log.d("PreviewActivity", "竖屏照片，正常适配");

                // 调整图片尺寸，使其宽度适配屏幕宽度，保持宽高比
                int finalWidth = screenWidth;
                int finalHeight = (int) (bitmap.getHeight() * ((float) screenWidth / bitmap.getWidth()));

                // 如果调整后的高度超过屏幕高度，则以高度为准
                if (finalHeight > screenHeight) {
                    finalHeight = screenHeight;
                    finalWidth = (int) (bitmap.getWidth() * ((float) screenHeight / bitmap.getHeight()));
                }

                // 只有当尺寸差异较大时才缩放，避免质量损失
                if (Math.abs(finalWidth - bitmap.getWidth()) > 10 || Math.abs(finalHeight - bitmap.getHeight()) > 10) {
                    Bitmap scaledBitmap = Bitmap.createScaledBitmap(bitmap, finalWidth, finalHeight, true);
                    if (scaledBitmap != bitmap) {
                        bitmap.recycle();
                    }
                    bitmap = scaledBitmap;

                    Log.d("PreviewActivity", "缩放到屏幕适配: " + bitmap.getWidth() + "x" + bitmap.getHeight());
                }
            }

            return bitmap;

        } catch (IOException e) {
            Log.e("PreviewActivity", "读取EXIF信息失败", e);
            // 如果读取EXIF失败，直接加载图片
            Bitmap bitmap = BitmapFactory.decodeFile(filePath);
            if (bitmap != null && bitmap.getWidth() > bitmap.getHeight()) {
                // 横屏照片，进行中心裁剪
                int screenWidth = getResources().getDisplayMetrics().widthPixels;
                int screenHeight = getResources().getDisplayMetrics().heightPixels;

                int bitmapWidth = bitmap.getWidth();
                int bitmapHeight = bitmap.getHeight();

                int targetHeight = screenHeight;
                int targetWidth = (int) (bitmapWidth * ((float) targetHeight / bitmapHeight));

                Bitmap scaledBitmap = Bitmap.createScaledBitmap(bitmap, targetWidth, targetHeight, true);
                if (scaledBitmap != bitmap) {
                    bitmap.recycle();
                }
                bitmap = scaledBitmap;

                if (bitmap.getWidth() > screenWidth) {
                    int cropX = (bitmap.getWidth() - screenWidth) / 2;
                    Bitmap croppedBitmap = Bitmap.createBitmap(bitmap, cropX, 0, screenWidth, screenHeight);
                    if (croppedBitmap != bitmap) {
                        bitmap.recycle();
                    }
                    bitmap = croppedBitmap;
                }
                return bitmap;
            }
            return bitmap;
        }
    }

    /**
     * 将Bitmap保存到文件
     * @param bitmap 要保存的Bitmap
     * @param filePath 文件路径
     */
    private void saveBitmapToFile(Bitmap bitmap, String filePath) {
        try {
            File file = new File(filePath);
            FileOutputStream fos = new FileOutputStream(file);
            bitmap.compress(Bitmap.CompressFormat.JPEG, 95, fos);
            fos.flush();
            fos.close();

            // 清除EXIF旋转信息，因为我们已经应用了旋转
            ExifInterface exif = new ExifInterface(filePath);
            exif.setAttribute(ExifInterface.TAG_ORIENTATION,
                    String.valueOf(ExifInterface.ORIENTATION_NORMAL));
            exif.saveAttributes();

            Log.d("PreviewActivity", "图片已保存到文件: " + filePath);
        } catch (IOException e) {
            Log.e("PreviewActivity", "保存图片失败", e);
        }
    }

    /**
     * 创建照片文件
     */
    private File createPhotoFile() {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        String fileName = "AI_" + timeStamp + ".jpg";

        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        return new File(storageDir, fileName);
    }

    /**
     * 重拍
     */
    private void retakePhoto() {
        capturedBitmap = null;
        photoFilePath = null;

        ivCaptured.setVisibility(View.GONE);
        previewView.setVisibility(View.VISIBLE);

        // 重新显示引导图
        ivReferOverlay.setVisibility(View.VISIBLE);

        // 重新启动语音监听
        startVoiceCapture();

        // 切换按钮 - 隐藏确认按钮容器，显示拍照按钮
        layoutConfirmButtons.setVisibility(View.GONE);
        btnCapture.setVisibility(View.VISIBLE);

        // 隐藏倒计时显示
        tvCountdown.setVisibility(View.GONE);
    }

    /**
     * 确认照片
     * 传递照片路径和遮罩图片路径给生成页
     */
    private void confirmPhoto() {
        // 检查是否有照片（本机拍摄或上传）
        boolean hasLocalPhoto = photoFilePath != null;
        boolean hasUploadedPhoto = capturedImageUrl != null;

        if (!hasLocalPhoto && !hasUploadedPhoto) {
            showToast("请先拍照或上传照片");
            return;
        }

        Intent intent = new Intent(this, GenerationActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra(Constants.EXTRA_MODE, mode);

        // 优先使用上传的图片URL，否则使用本地路径
        if (hasUploadedPhoto) {
            intent.putExtra(Constants.EXTRA_IMAGE_URL, capturedImageUrl);
            Log.d("PreviewActivity", "使用上传的图片URL: " + capturedImageUrl);
        } else if (hasLocalPhoto) {
            intent.putExtra("photo_path", photoFilePath);
            Log.d("PreviewActivity", "使用本地照片路径: " + photoFilePath);
        }

        // 获取风格配置，传递遮罩图片路径（用于AI生成时的遮罩层）
        com.jcoding.aiactivity.entity.StyleConfig styleConfig = configManager.getStyleConfig(styleId);
        if (styleConfig != null && styleConfig.getMaskImage() != null) {
            intent.putExtra("mask_image_path", styleConfig.getMaskImage());
            android.util.Log.d("PreviewActivity", "传递遮罩图片给AI生成: " + styleConfig.getMaskImage());
        }

        startActivity(intent);
    }

    /**
     * 上传照片到服务器
     */
    private void uploadPhotoToServer(String filePath) {
        Log.d("PreviewActivity", "开始上传照片: " + filePath);

        photoUploadHelper.uploadPhoto(filePath, new PhotoUploadHelper.UploadCallback() {
            @Override
            public void onSuccess(String response) {
                Log.d("PreviewActivity", "照片上传成功: " + response);
                runOnUiThread(() -> {
                    showToast("照片上传成功");
                });
            }

            @Override
            public void onError(String error) {
                Log.e("PreviewActivity", "照片上传失败: " + error);
                runOnUiThread(() -> {
                    showToast("照片上传失败: " + error);
                });
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();

        // 停止轮询上传
        stopPollingUpload();

        // 取消倒计时
        if (countDownTimer != null) {
            countDownTimer.cancel();
        }
        if (cameraProvider != null) {
            cameraProvider.unbindAll();
        }
        // 停止语音监听
        if (voiceCaptureHelper != null) {
            voiceCaptureHelper.stopListening();
        }

        // 清理Handler
        if (uploadPollingHandler != null) {
            uploadPollingHandler.removeCallbacksAndMessages(null);
        }
    }

    /**
     * 显示拍照选项对话框
     * 根据用户设置自动选择拍照方式
     */
    private void showCaptureOptionsDialog() {
        // 读取用户设置的拍照方式
        int photoSourceMode = com.jcoding.aiactivity.utils.PreferenceUtils.getInt(
                this, Constants.PREF_PHOTO_SOURCE_MODE, Constants.PHOTO_SOURCE_UPLOAD);

        if (photoSourceMode == Constants.PHOTO_SOURCE_CAMERA) {
            // 设置为本机摄像头，直接开始倒计时
            startCountdown();
        } else if (photoSourceMode == Constants.PHOTO_SOURCE_UPLOAD) {
            // 设置为扫码上传，打开二维码页面
            openWebUpload();
        } else {
            // 未设置，显示选择对话框
            new androidx.appcompat.app.AlertDialog.Builder(this)
                    .setTitle("选择操作")
                    .setItems(new String[]{"📷 拍照", "📱 上传照片"}, (dialog, which) -> {
                        if (which == 0) {
                            // 选择拍照
                            startCountdown();
                        } else {
                            // 选择上传照片，跳转到二维码上传页面
                            openWebUpload();
                        }
                    })
                    .setNegativeButton("取消", null)
                    .show();
        }
    }

    /**
     * 显示二维码上传对话框
     */
    private void openWebUpload() {
        showQRCodeUploadDialog();
    }

    /**
     * 显示二维码上传对话框（半透明）
     */
    private void showQRCodeUploadDialog() {
        // 创建半透明对话框
        androidx.appcompat.app.AlertDialog.Builder builder = new androidx.appcompat.app.AlertDialog.Builder(this);

        // 创建自定义布局
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_qrcode_upload, null);

        ImageView ivQRCode = dialogView.findViewById(R.id.iv_qrcode);
        TextView tvHint = dialogView.findViewById(R.id.tv_hint);
        TextView tvStatus = dialogView.findViewById(R.id.tv_status);
        Button btnClose = dialogView.findViewById(R.id.btn_close);

        // 先在主线程生成session_id，避免竞态条件
        currentSessionId = "session_" + System.currentTimeMillis() + "_" + new java.util.Random().nextInt(10000);
        Log.d("PreviewActivity", "生成会话ID: " + currentSessionId);

        // 生成二维码
        generateQRCode(ivQRCode, tvHint);

        // 创建对话框
        androidx.appcompat.app.AlertDialog dialog = builder.setView(dialogView).create();

        // 设置对话框样式 - 半透明背景
        dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        dialog.getWindow().setDimAmount(0.5f); // 设置背景透明度为50%

        // 关闭按钮
        btnClose.setOnClickListener(v -> {
            stopPollingUpload();
            dialog.dismiss();
        });

        dialog.show();

        // 开始轮询检查上传
        startPollingUpload(tvStatus, dialog);
    }

    /**
     * 生成二维码
     */
    private void generateQRCode(ImageView imageView, TextView hintView) {
        new Thread(() -> {
            try {
                com.google.zxing.qrcode.QRCodeWriter qrCodeWriter = new com.google.zxing.qrcode.QRCodeWriter();
                Map<com.google.zxing.EncodeHintType, Object> hints = new HashMap<>();
                hints.put(com.google.zxing.EncodeHintType.CHARACTER_SET, "UTF-8");
                hints.put(com.google.zxing.EncodeHintType.MARGIN, 1);

                // currentSessionId 已在主线程中生成，避免竞态条件

                // 使用统一的/upload路径，并添加session_id参数
                String uploadUrl = "https://www.jcoding.chat/upload?session_id=" + currentSessionId;
                if (styleId != null && !styleId.isEmpty()) {
                    uploadUrl += "&style_id=" + styleId;
                }

                Log.d("PreviewActivity", "生成二维码，URL: " + uploadUrl);

                com.google.zxing.common.BitMatrix bitMatrix = qrCodeWriter.encode(uploadUrl,
                    com.google.zxing.BarcodeFormat.QR_CODE, 512, 512, hints);

                int width = bitMatrix.getWidth();
                int height = bitMatrix.getHeight();
                Bitmap bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565);

                for (int x = 0; x < width; x++) {
                    for (int y = 0; y < height; y++) {
                        bitmap.setPixel(x, y, bitMatrix.get(x, y) ? 0xFF000000 : 0xFFFFFFFF);
                    }
                }

                runOnUiThread(() -> {
                    imageView.setImageBitmap(bitmap);
                    hintView.setText("请使用手机扫描二维码\\n在手机浏览器中上传照片");
                });

            } catch (Exception e) {
                Log.e("PreviewActivity", "生成二维码失败", e);
                runOnUiThread(() -> {
                    hintView.setText("二维码生成失败，请稍后重试");
                });
            }
        }).start();
    }

    // 上传轮询相关
    private Handler uploadPollingHandler = new Handler(Looper.getMainLooper());
    private Runnable uploadPollingRunnable;
    private boolean isPollingUpload = false;
    private long uploadCheckStartTime;
    private String lastProcessedFileId = null; // 追踪已处理的文件ID，避免重复处理
    private String currentSessionId = null; // 当前会话ID，用于关联上传和轮询

    /**
     * 开始轮询检查上传
     */
    private void startPollingUpload(TextView statusView, androidx.appcompat.app.AlertDialog dialog) {
        isPollingUpload = true;
        uploadCheckStartTime = System.currentTimeMillis();
        lastProcessedFileId = null; // 重置已处理的文件ID

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
                // 使用统一的/application/upload/query路径，并通过session_id过滤
                String queryUrl = "https://www.jcoding.chat/application/upload/query?session_id=" + currentSessionId + "&limit=1";
                Log.d("PreviewActivity", "查询URL: " + queryUrl);

                // 创建信任所有证书的OkHttpClient（用于IP访问）
                okhttp3.OkHttpClient client = createUnsafeOkHttpClient();

                okhttp3.Request request = new okhttp3.Request.Builder()
                        .url(queryUrl)
                        .addHeader("Host", "www.jcoding.chat")
                        .build();

                okhttp3.Response response = client.newCall(request).execute();

                Log.d("PreviewActivity", "响应码: " + response.code() + ", 成功: " + response.isSuccessful());

                if (response.isSuccessful() && response.body() != null) {
                    String jsonStr = response.body().string();
                    Log.d("PreviewActivity", "响应内容: " + jsonStr);

                    org.json.JSONObject jsonResponse = new org.json.JSONObject(jsonStr);

                    if (jsonResponse.optInt("code") == 200) {
                        org.json.JSONArray uploads = jsonResponse.optJSONArray("data");
                        Log.d("PreviewActivity", "上传记录数量: " + (uploads != null ? uploads.length() : 0));

                        if (uploads != null && uploads.length() > 0) {
                            org.json.JSONObject latestUpload = uploads.optJSONObject(0);
                            if (latestUpload != null) {
                                String fileId = latestUpload.optString("file_id");
                                String imageUrl = latestUpload.optString("oss_url");
                                String filename = latestUpload.optString("filename");
                                long uploadTime = latestUpload.optLong("upload_time", 0);
                                String sessionId = latestUpload.optString("session_id");

                                Log.d("PreviewActivity", "获取到图片 - file_id: " + fileId + ", upload_time: " + uploadTime + ", sessionId: " + sessionId + ", URL: " + imageUrl);

                                // 检查是否在开始轮询之后上传
                                if (uploadTime > uploadCheckStartTime && !imageUrl.isEmpty()) {
                                    // 检查session_id是否匹配（参考PhotoStyleActivity）
                                    if (sessionId != null && !sessionId.isEmpty() && !sessionId.equals(currentSessionId)) {
                                        Log.d("PreviewActivity", "session_id不匹配 - 当前: " + currentSessionId + ", 上传: " + sessionId);
                                        runOnUiThread(() -> {
                                            stopPollingUpload();
                                            dialog.dismiss();
                                            showToast("已有人扫码上传，请排队等待下一次机会");
                                        });
                                        return;
                                    }

                                    // 检查是否已经处理过这个上传（避免重复处理）
                                    if (!fileId.equals(lastProcessedFileId)) {
                                        Log.d("PreviewActivity", "检测到新上传，开始处理");
                                        // 标记为已处理
                                        lastProcessedFileId = fileId;

                                        // 上传成功 - 在主线程处理
                                        runOnUiThread(() -> {
                                            handleUploadSuccess(imageUrl, filename, dialog);
                                        });
                                        return;
                                    } else {
                                        Log.d("PreviewActivity", "此上传已处理过，跳过");
                                    }
                                }
                            }
                        }
                    } else {
                        Log.e("PreviewActivity", "响应code不是200: " + jsonResponse.optInt("code"));
                    }
                } else {
                    Log.e("PreviewActivity", "响应失败或body为空");
                }
            } catch (final Exception e) {
                Log.e("PreviewActivity", "检查上传状态失败: " + e.getClass().getName() + ": " + e.getMessage(), e);
                e.printStackTrace();

                String errorMsg = e.getMessage();
                if (errorMsg != null && errorMsg.contains("Trust")) {
                    errorMsg = "SSL证书验证失败";
                } else if (errorMsg != null && errorMsg.contains("timeout")) {
                    errorMsg = "网络超时";
                } else if (errorMsg != null && errorMsg.contains("UnknownHost")) {
                    errorMsg = "无法连接服务器";
                } else {
                    errorMsg = "检查失败，请稍后重试";
                }

                final String finalErrorMsg = errorMsg;
                runOnUiThread(() -> {
                    if (statusView != null) {
                        statusView.setText(finalErrorMsg);
                    }
                });
            }
        }).start();
    }

    /**
     * 处理上传成功
     * 参考PhotoStyleActivity的实现：在对话框中显示图片后延迟跳转到生成页面
     */
    private void handleUploadSuccess(String imageUrl, String filename, androidx.appcompat.app.AlertDialog dialog) {
        Log.d("PreviewActivity", "处理上传成功，图片URL: " + imageUrl);

        // 停止轮询
        isPollingUpload = false;
        if (uploadPollingHandler != null && uploadPollingRunnable != null) {
            uploadPollingHandler.removeCallbacks(uploadPollingRunnable);
        }

        // 将OSS URL转换为代理URL（用于显示）
        String proxyUrl = com.jcoding.aiactivity.utils.NetworkUtils.convertToProxyUrl(imageUrl);
        Log.d("PreviewActivity", "代理URL: " + proxyUrl);

        // 保存图片URL供后续使用
        capturedImageUrl = imageUrl;
        photoFilePath = imageUrl;

        // 在对话框中显示图片，延迟后跳转到生成页面（参考PhotoStyleActivity的showImageInDialogAndDelay）
        showImageInDialogAndNavigate(proxyUrl, imageUrl, dialog);
    }

    /**
     * 在对话框中显示图片，延迟后关闭对话框并跳转到生成页面
     * 参考PhotoStyleActivity的实现
     */
    private void showImageInDialogAndNavigate(String proxyUrl, String imageUrl,
                                              androidx.appcompat.app.AlertDialog dialog) {
        Log.d("PreviewActivity", "在对话框中显示图片: " + proxyUrl);

        try {
            // 获取对话框中的ImageView
            android.widget.ImageView ivQRCode = dialog.findViewById(R.id.iv_qrcode);
            android.widget.TextView tvHint = dialog.findViewById(R.id.tv_hint);
            android.widget.TextView tvStatus = dialog.findViewById(R.id.tv_status);

            if (ivQRCode != null && tvHint != null) {
                // 隐藏QR码，显示上传的图片
                ivQRCode.setScaleType(android.widget.ImageView.ScaleType.FIT_CENTER);
                ivQRCode.setAdjustViewBounds(true);

                // 使用Glide加载并显示图片
                com.bumptech.glide.Glide.with(this)
                        .load(proxyUrl)
                        .placeholder(android.R.drawable.ic_menu_gallery)
                        .error(android.R.drawable.ic_menu_report_image)
                        .fitCenter()
                        .listener(new com.bumptech.glide.request.RequestListener<android.graphics.drawable.Drawable>() {
                            @Override
                            public boolean onLoadFailed(@androidx.annotation.Nullable com.bumptech.glide.load.engine.GlideException e, Object model,
                                                       com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target, boolean isFirstResource) {
                                Log.e("PreviewActivity", "图片加载失败", e);
                                runOnUiThread(() -> {
                                    if (tvHint != null) {
                                        tvHint.setText("图片加载失败");
                                    }
                                    // 即使加载失败也继续跳转
                                    delayedNavigateToGeneration(imageUrl, dialog);
                                });
                                return false;
                            }

                            @Override
                            public boolean onResourceReady(android.graphics.drawable.Drawable resource, Object model,
                                                           com.bumptech.glide.request.target.Target<android.graphics.drawable.Drawable> target,
                                                           DataSource dataSource, boolean isFirstResource) {
                                Log.d("PreviewActivity", "图片加载成功");
                                runOnUiThread(() -> {
                                    if (tvHint != null) {
                                        tvHint.setText("照片已接收");
                                        tvHint.setTextSize(18);
                                    }
                                    if (tvStatus != null) {
                                        tvStatus.setText("正在准备生成...");
                                    }
                                });
                                return false;
                            }
                        })
                        .into(ivQRCode);

                // 更新提示文字
                if (tvHint != null) {
                    tvHint.setText("正在加载照片...");
                }

                // 延迟3秒后关闭对话框并跳转到生成页面
                delayedNavigateToGeneration(imageUrl, dialog);

            } else {
                // 如果找不到ImageView，直接跳转
                Log.w("PreviewActivity", "对话框ImageView为空，直接跳转到生成页面");
                navigateToGenerationAfterUpload(imageUrl, dialog);
            }
        } catch (Exception e) {
            Log.e("PreviewActivity", "显示图片异常", e);
            // 异常情况直接跳转
            navigateToGenerationAfterUpload(imageUrl, dialog);
        }
    }

    /**
     * 延迟跳转到生成页面
     */
    private void delayedNavigateToGeneration(String imageUrl, androidx.appcompat.app.AlertDialog dialog) {
        new Handler(Looper.getMainLooper()).postDelayed(new Runnable() {
            @Override
            public void run() {
                navigateToGenerationAfterUpload(imageUrl, dialog);
            }
        }, 3000); // 延迟3秒
    }

    /**
     * 跳转到生成页面（上传成功后）
     */
    private void navigateToGenerationAfterUpload(String imageUrl, androidx.appcompat.app.AlertDialog dialog) {
        Log.d("PreviewActivity", "跳转到生成页面，图片URL: " + imageUrl);

        // 关闭对话框
        if (dialog != null && dialog.isShowing()) {
            try {
                dialog.dismiss();
            } catch (Exception e) {
                Log.e("PreviewActivity", "关闭对话框失败", e);
            }
        }

        // 跳转到生成页面
        Intent intent = new Intent(this, GenerationActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra(Constants.EXTRA_MODE, mode);
        intent.putExtra(Constants.EXTRA_IMAGE_URL, imageUrl);

        // 获取风格配置，传递遮罩图片路径
        com.jcoding.aiactivity.entity.StyleConfig styleConfig = configManager.getStyleConfig(styleId);
        if (styleConfig != null && styleConfig.getMaskImage() != null) {
            intent.putExtra("mask_image_path", styleConfig.getMaskImage());
            Log.d("PreviewActivity", "传递遮罩图片给AI生成: " + styleConfig.getMaskImage());
        }

        // 传递session_id用于生成结果关联
        if (currentSessionId != null && !currentSessionId.isEmpty()) {
            intent.putExtra("session_id", currentSessionId);
            Log.d("PreviewActivity", "传递session_id: " + currentSessionId);
        }

        startActivity(intent);
    }

    /**
     * 显示已拍摄的图片界面
     */
    private void showCapturedImage() {
        // 隐藏相机预览和拍照按钮
        if (previewView != null) {
            previewView.setVisibility(View.GONE);
        }
        if (btnCapture != null) {
            btnCapture.setVisibility(View.GONE);
        }

        // 显示拍摄的照片和确认按钮
        if (ivCaptured != null) {
            ivCaptured.setVisibility(View.VISIBLE);
        }
        if (layoutConfirmButtons != null) {
            layoutConfirmButtons.setVisibility(View.VISIBLE);
        }

        // 遮罩层始终显示
        if (ivReferOverlay != null) {
            ivReferOverlay.setVisibility(View.VISIBLE);
        }

        Toast.makeText(this, "照片上传成功！点击确认继续", Toast.LENGTH_SHORT).show();
    }

    /**
     * 创建信任所有证书的OkHttpClient（用于通过IP地址访问HTTPS）
     * 注意：仅用于测试环境，生产环境应使用正确的SSL证书
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
     * 上传成功回调（已弃用，使用handleUploadSuccess代替）
     */
    private void onUploadSuccess(String imageUrl, String filename, androidx.appcompat.app.AlertDialog dialog) {
        handleUploadSuccess(imageUrl, filename, dialog);
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
     * 打开Web上传页面
     */

    /**
     * 启动倒计时
     */
    private void startCountdown() {
        // 隐藏拍照按钮
        btnCapture.setVisibility(View.GONE);

        // 显示倒计时
        tvCountdown.setVisibility(View.VISIBLE);
        tvCountdown.setText(String.valueOf(countdownSeconds));

        // 创建倒计时定时器
        countDownTimer = new android.os.CountDownTimer(
                countdownSeconds * 1000,  // 总时长（毫秒）
                1000  // 间隔（毫秒）
        ) {
            @Override
            public void onTick(long millisUntilFinished) {
                int secondsLeft = (int) (millisUntilFinished / 1000);
                tvCountdown.setText(String.valueOf(secondsLeft));
                Log.d("PreviewActivity", "倒计时: " + secondsLeft + "秒");
            }

            @Override
            public void onFinish() {
                // 倒计时结束，隐藏倒计时显示
                tvCountdown.setVisibility(View.GONE);
                Log.d("PreviewActivity", "倒计时结束，开始拍照");

                // 自动拍照
                takePhoto();
            }
        }.start();

        Log.d("PreviewActivity", "开始倒计时: " + countdownSeconds + "秒");
    }

    /**
     * 处理Activity返回结果
     * 处理WebUploadActivity上传成功后的回调
     */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_CODE_UPLOAD && resultCode == RESULT_OK && data != null) {
            // 处理上传成功
            boolean uploadSuccess = data.getBooleanExtra("upload_success", false);
            if (uploadSuccess) {
                String imageUrl = data.getStringExtra("image_url");
                String filename = data.getStringExtra("filename");
                String fileId = data.getStringExtra("file_id");
                long timestamp = data.getLongExtra("timestamp", 0);

                Log.d("PreviewActivity", "上传成功: " + imageUrl);

                // 显示成功提示
                Toast.makeText(this, "照片上传成功", Toast.LENGTH_SHORT).show();

                // 跳转到生成页面
                if (imageUrl != null && !imageUrl.isEmpty()) {
                    proceedToGeneration(imageUrl);
                }
            }
        }
    }

    /**
     * 继续到生成页面
     * @param imageUrl 图片URL
     */
    private void proceedToGeneration(String imageUrl) {
        Intent intent = new Intent(this, GenerationActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra(Constants.EXTRA_IMAGE_URL, imageUrl);
        intent.putExtra(Constants.EXTRA_MODE, mode);
        startActivity(intent);
        finish();
    }
}
