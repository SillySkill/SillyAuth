package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.utils.Constants;

import java.io.File;
import java.io.FileOutputStream;

/**
 * 签名输入页
 * 支持手写签名和文字签名
 */
public class SignatureActivity extends BaseActivity {

    private static final int SIGNATURE_MODE_HANDWRITE = 1;
    private static final int SIGNATURE_MODE_TEXT = 2;

    private SignatureView signatureView;
    private EditText etTextSignature;
    private ImageView ivPreview;
    private Button btnClear;
    private Button btnConfirm;
    private Button btnBack;
    private Button btnToggleMode;

    private int currentMode = SIGNATURE_MODE_HANDWRITE;
    private String signatureText;
    private Bitmap signatureBitmap;

    private String resultId;
    private String resultImageUrl;
    private String styleName;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signature);

        // 获取参数
        resultId = getIntent().getStringExtra("result_id");
        resultImageUrl = getIntent().getStringExtra("result_image_url");
        styleName = getIntent().getStringExtra("style_name");

        initViews();
        setupListeners();
    }

    private void initViews() {
        signatureView = findViewById(R.id.signature_view);
        etTextSignature = findViewById(R.id.et_text_signature);
        ivPreview = findViewById(R.id.iv_preview);
        btnClear = findViewById(R.id.btn_clear);
        btnConfirm = findViewById(R.id.btn_confirm);
        btnBack = findViewById(R.id.btn_back);
        btnToggleMode = findViewById(R.id.btn_toggle_mode);

        // 默认显示手写签名板
        updateModeView();
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnToggleMode.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleMode();
            }
        });

        btnClear.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                clearSignature();
            }
        });

        btnConfirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                confirmSignature();
            }
        });
    }

    /**
     * 切换签名模式
     */
    private void toggleMode() {
        if (currentMode == SIGNATURE_MODE_HANDWRITE) {
            currentMode = SIGNATURE_MODE_TEXT;
        } else {
            currentMode = SIGNATURE_MODE_HANDWRITE;
        }
        updateModeView();
    }

    /**
     * 更新模式视图
     */
    private void updateModeView() {
        if (currentMode == SIGNATURE_MODE_HANDWRITE) {
            signatureView.setVisibility(View.VISIBLE);
            etTextSignature.setVisibility(View.GONE);
            btnToggleMode.setText("切换到文字签名");
        } else {
            signatureView.setVisibility(View.GONE);
            etTextSignature.setVisibility(View.VISIBLE);
            btnToggleMode.setText("切换到手写签名");
        }
    }

    /**
     * 清除签名
     */
    private void clearSignature() {
        if (currentMode == SIGNATURE_MODE_HANDWRITE) {
            signatureView.clear();
        } else {
            etTextSignature.setText("");
        }
    }

    /**
     * 确认签名
     */
    private void confirmSignature() {
        if (currentMode == SIGNATURE_MODE_HANDWRITE) {
            signatureBitmap = signatureView.getSignatureBitmap();
            if (signatureBitmap == null || signatureView.isEmpty()) {
                Toast.makeText(this, "请先签名", Toast.LENGTH_SHORT).show();
                return;
            }

            // 保存签名图片
            String signaturePath = saveSignatureImage(signatureBitmap);

            // 返回结果
            Intent result = new Intent();
            result.putExtra("signature_type", "image");
            result.putExtra("signature_path", signaturePath);
            setResult(RESULT_OK, result);
            finish();

        } else {
            signatureText = etTextSignature.getText().toString().trim();
            if (signatureText.isEmpty()) {
                Toast.makeText(this, "请输入签名文字", Toast.LENGTH_SHORT).show();
                return;
            }

            // 返回结果
            Intent result = new Intent();
            result.putExtra("signature_type", "text");
            result.putExtra("signature_text", signatureText);
            setResult(RESULT_OK, result);
            finish();
        }
    }

    /**
     * 保存签名为图片
     */
    private String saveSignatureImage(Bitmap bitmap) {
        try {
            File signatureDir = new File(getFilesDir(), "signatures");
            if (!signatureDir.exists()) {
                signatureDir.mkdirs();
            }

            String fileName = "signature_" + System.currentTimeMillis() + ".png";
            File file = new File(signatureDir, fileName);
            FileOutputStream fos = new FileOutputStream(file);
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, fos);
            fos.flush();
            fos.close();

            return file.getAbsolutePath();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 签名视图
     */
    public static class SignatureView extends View {
        private Bitmap signatureBitmap;
        private Canvas signatureCanvas;
        private boolean isEmpty = true;

        public SignatureView(android.content.Context context) {
            super(context);
            init();
        }

        public SignatureView(android.content.Context context, android.util.AttributeSet attrs) {
            super(context, attrs);
            init();
        }

        private void init() {
            // 设置背景
            setBackgroundColor(Color.WHITE);
        }

        @Override
        protected void onSizeChanged(int w, int h, int oldw, int oldh) {
            super.onSizeChanged(w, h, oldw, oldh);

            if (signatureBitmap == null) {
                signatureBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
                signatureCanvas = new Canvas(signatureBitmap);
                signatureCanvas.drawColor(Color.WHITE);
            }
        }

        @Override
        protected void onDraw(android.graphics.Canvas canvas) {
            super.onDraw(canvas);

            if (signatureBitmap != null) {
                canvas.drawBitmap(signatureBitmap, 0, 0, null);
            }
        }

        @Override
        public boolean onTouchEvent(android.view.MotionEvent event) {
            float x = event.getX();
            float y = event.getY();

            switch (event.getAction()) {
                case android.view.MotionEvent.ACTION_DOWN:
                    isEmpty = false;
                    // 绘制点
                    if (signatureCanvas != null) {
                        signatureCanvas.drawCircle(x, y, 5, new android.graphics.Paint());
                    }
                    invalidate();
                    return true;

                case android.view.MotionEvent.ACTION_MOVE:
                    isEmpty = false;
                    // 绘制线（简化实现）
                    if (signatureCanvas != null) {
                        android.graphics.Paint paint = new android.graphics.Paint();
                        paint.setColor(Color.BLACK);
                        paint.setStrokeWidth(8);
                        paint.setStyle(android.graphics.Paint.Style.STROKE);
                        paint.setAntiAlias(true);
                        signatureCanvas.drawPoint(x, y, paint);
                    }
                    invalidate();
                    return true;
            }

            return super.onTouchEvent(event);
        }

        public void clear() {
            if (signatureCanvas != null) {
                signatureCanvas.drawColor(Color.WHITE);
                isEmpty = true;
                invalidate();
            }
        }

        public Bitmap getSignatureBitmap() {
            return signatureBitmap;
        }

        public boolean isEmpty() {
            return isEmpty;
        }
    }
}
