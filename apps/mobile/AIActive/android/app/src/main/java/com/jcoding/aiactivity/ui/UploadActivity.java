package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.utils.Constants;

import java.io.File;

/**
 * 上传页面
 * 从相册选择照片上传
 */
public class UploadActivity extends BaseActivity {

    private static final int REQUEST_CODE_PICK_PHOTO = 1001;

    private ImageView ivPhoto;
    private Button btnSelect;
    private Button btnConfirm;
    private Button btnBack;
    private TextView tvOfflineMode;

    private String styleId;
    private int mode;
    private String selectedPhotoPath;
    private Uri selectedPhotoUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_upload);

        // 获取参数
        styleId = getIntent().getStringExtra(Constants.EXTRA_STYLE_ID);
        mode = getIntent().getIntExtra(Constants.EXTRA_MODE, Constants.MODE_INVITE_CODE);

        initViews();
        setupListeners();
    }

    private void initViews() {
        ivPhoto = findViewById(R.id.iv_photo);
        btnSelect = findViewById(R.id.btn_select);
        btnConfirm = findViewById(R.id.btn_confirm);
        btnBack = findViewById(R.id.btn_back);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        btnConfirm.setEnabled(false);
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnSelect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openGallery();
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
     * 打开相册
     */
    private void openGallery() {
        Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        intent.setType("image/*");
        startActivityForResult(intent, REQUEST_CODE_PICK_PHOTO);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_CODE_PICK_PHOTO && resultCode == RESULT_OK && data != null) {
            selectedPhotoUri = data.getData();
            selectedPhotoPath = getRealPathFromUri(selectedPhotoUri);

            // 显示选中的照片
            try {
                ivPhoto.setImageURI(selectedPhotoUri);
                btnConfirm.setEnabled(true);
            } catch (Exception e) {
                showToast("加载照片失败");
            }
        }
    }

    /**
     * 从Uri获取真实路径
     */
    private String getRealPathFromUri(Uri uri) {
        String[] projection = {MediaStore.Images.Media.DATA};
        Cursor cursor = getContentResolver().query(uri, projection, null, null, null);
        if (cursor != null && cursor.moveToFirst()) {
            int columnIndex = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
            String path = cursor.getString(columnIndex);
            cursor.close();
            return path;
        }
        return null;
    }

    /**
     * 确认照片
     */
    private void confirmPhoto() {
        if (selectedPhotoPath == null) {
            showToast("请先选择照片");
            return;
        }

        Intent intent = new Intent(this, GenerationActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra(Constants.EXTRA_MODE, mode);
        intent.putExtra("photo_path", selectedPhotoPath);
        startActivity(intent);
    }
}
