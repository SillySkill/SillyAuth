package com.jcoding.aiactivity.ui;

import android.Manifest;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.utils.Constants;

/**
 * 照片选择页
 * 选择照片来源：现场拍摄 或 手机上传
 */
public class PhotoSelectionActivity extends BaseActivity {

    private Button btnCamera;
    private Button btnUpload;
    private Button btnBack;
    private TextView tvTitle;
    private TextView tvOfflineMode;

    private String styleId;
    private int mode;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_photo_selection);

        // 获取参数
        styleId = getIntent().getStringExtra(Constants.EXTRA_STYLE_ID);
        mode = getIntent().getIntExtra(Constants.EXTRA_MODE, Constants.MODE_INVITE_CODE);

        initViews();
        setupListeners();
    }

    private void initViews() {
        btnCamera = findViewById(R.id.btn_camera);
        btnUpload = findViewById(R.id.btn_upload);
        btnBack = findViewById(R.id.btn_back);
        tvTitle = findViewById(R.id.tv_title);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        // 现场拍摄
        btnCamera.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                requestPermissionsAndOpenCamera();
            }
        });

        // 手机上传
        btnUpload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openUpload();
            }
        });
    }

    /**
     * 获取所需权限列表（根据SDK版本动态调整）
     * Android 10+不需要存储权限即可保存到应用私有目录
     */
    private String[] getRequiredPermissions() {
        if (android.os.Build.VERSION.SDK_INT <= android.os.Build.VERSION_CODES.P) {
            return new String[]{
                    Manifest.permission.CAMERA,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE,
                    Manifest.permission.READ_EXTERNAL_STORAGE
            };
        } else {
            return new String[]{
                    Manifest.permission.CAMERA
            };
        }
    }

    /**
     * 请求相机权限并打开拍照
     */
    private void requestPermissionsAndOpenCamera() {
        String[] permissions = getRequiredPermissions();

        requestPermissions(permissions, new PermissionResultListener() {
            @Override
            public void onGranted() {
                openCamera();
            }

            @Override
            public void onDenied() {
                showToast("需要相机权限才能拍照");
            }
        });
    }

    /**
     * 打开相机拍照
     */
    private void openCamera() {
        // 签名提醒
        if (configManager.isSignatureReminderEnabled()) {
            showToast("提示：生成完成后可以在结果页添加您的签名");
        }
        Intent intent = new Intent(this, PreviewActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra(Constants.EXTRA_MODE, mode);
        startActivity(intent);
    }

    /**
     * 打开上传页面
     */
    private void openUpload() {
        // 签名提醒
        if (configManager.isSignatureReminderEnabled()) {
            showToast("提示：生成完成后可以在结果页添加您的签名");
        }
        Intent intent = new Intent(this, UploadActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra(Constants.EXTRA_MODE, mode);
        startActivity(intent);
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
