package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.ImageView;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.RadioGroup;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.network.ApiService;
import com.jcoding.aiactivity.network.RetrofitClient;
import com.jcoding.aiactivity.utils.Constants;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.util.HashMap;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * 身份验证页
 * 支持邀请码、支付、员工三种模式
 */
public class LoginCheckActivity extends BaseActivity {

    private EditText etInviteCode;
    private RadioGroup rgMode;
    private Button btnVerify;
    private Button btnPayment;
    private ProgressBar progressBar;
    private TextView tvOfflineMode;
    private ImageButton btnBack;

    private String styleId;
    private int currentMode = Constants.MODE_INVITE_CODE;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login_check);

        styleId = getIntent().getStringExtra(Constants.EXTRA_STYLE_ID);

        // 检查是否指定了自动模式
        String autoMode = getIntent().getStringExtra("auto_mode");
        if (autoMode != null) {
            // 如果指定了自动模式，直接跳过验证页面
            handleAutoMode(autoMode);
            return;
        }

        initViews();
        setupListeners();
    }

    /**
     * 处理自动模式（无需用户选择，直接进入下一步）
     */
    private void handleAutoMode(String mode) {
        switch (mode) {
            case "employee":
                // 员工模式：直接跳转到照片选择页
                navigateToPhotoSelection();
                break;
            case "invite_code":
            case "payment":
                // 邀请码和支付模式仍需验证，但可以自动选择对应模式并进入
                initViews();
                setupListeners();

                // 自动设置模式
                if ("invite_code".equals(mode)) {
                    rgMode.check(R.id.rb_invite_code);
                } else if ("payment".equals(mode)) {
                    rgMode.check(R.id.rb_payment);
                }
                break;
        }
    }

    /**
     * 跳转到照片选择页
     */
    private void navigateToPhotoSelection() {
        Intent intent = new Intent(this, PhotoSelectionActivity.class);
        intent.putExtra(Constants.EXTRA_STYLE_ID, styleId);
        intent.putExtra("verified", true);
        intent.putExtra("mode", Constants.MODE_EMPLOYEE);
        startActivity(intent);
        finish();
    }

    private void initViews() {
        etInviteCode = findViewById(R.id.et_invite_code);
        rgMode = findViewById(R.id.rg_mode);
        btnVerify = findViewById(R.id.btn_verify);
        btnPayment = findViewById(R.id.btn_payment);
        progressBar = findViewById(R.id.progress_bar);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);
        btnBack = findViewById(R.id.btn_back);

        // 根据配置显示/隐藏参与模式
        android.widget.RadioButton rbInviteCode = findViewById(R.id.rb_invite_code);
        android.widget.RadioButton rbPayment = findViewById(R.id.rb_payment);
        android.widget.RadioButton rbEmployee = findViewById(R.id.rb_employee);

        boolean inviteCodeEnabled = configManager.isInviteCodeModeEnabled();
        boolean paymentEnabled = configManager.isPaymentModeEnabled();
        boolean employeeEnabled = configManager.isEmployeeModeEnabled();

        // 显示/隐藏模式选项
        if (!inviteCodeEnabled) {
            rbInviteCode.setVisibility(View.GONE);
        }
        if (!paymentEnabled) {
            rbPayment.setVisibility(View.GONE);
        }
        if (!employeeEnabled) {
            rbEmployee.setVisibility(View.GONE);
        }

        // 检查是否有可用模式
        if (!inviteCodeEnabled && !paymentEnabled && !employeeEnabled) {
            // 所有模式都禁用，显示提示并返回
            showToast("管理员未开放任何参与模式");
            finish();
            return;
        }

        // 如果只有一个模式启用，自动选择
        int enabledCount = (inviteCodeEnabled ? 1 : 0) +
                          (paymentEnabled ? 1 : 0) +
                          (employeeEnabled ? 1 : 0);

        if (enabledCount == 1) {
            if (inviteCodeEnabled) {
                rbInviteCode.setChecked(true);
            } else if (paymentEnabled) {
                rbPayment.setChecked(true);
            } else if (employeeEnabled) {
                rbEmployee.setChecked(true);
            }
        } else {
            // 多个模式可用，默认选择第一个可用模式
            if (inviteCodeEnabled) {
                rbInviteCode.setChecked(true);
            } else if (paymentEnabled) {
                rbPayment.setChecked(true);
            } else if (employeeEnabled) {
                rbEmployee.setChecked(true);
            }
        }

        rgMode.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(RadioGroup group, int checkedId) {
                if (checkedId == R.id.rb_invite_code) {
                    currentMode = Constants.MODE_INVITE_CODE;
                    etInviteCode.setHint("请输入邀请码");
                    btnPayment.setVisibility(View.GONE);
                    btnVerify.setVisibility(View.VISIBLE);
                } else if (checkedId == R.id.rb_payment) {
                    currentMode = Constants.MODE_PAYMENT;
                    etInviteCode.setHint("扫码后输入验证码");
                    btnPayment.setVisibility(View.VISIBLE);
                    btnVerify.setVisibility(View.GONE);
                } else if (checkedId == R.id.rb_employee) {
                    currentMode = Constants.MODE_EMPLOYEE;
                    etInviteCode.setHint("员工无需验证");
                    btnPayment.setVisibility(View.GONE);
                    btnVerify.setVisibility(View.VISIBLE);
                }
            }
        });
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnVerify.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                handleVerify();
            }
        });

        btnPayment.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                handlePayment();
            }
        });
    }

    /**
     * 处理验证
     */
    private void handleVerify() {
        String inviteCode = etInviteCode.getText().toString().trim();

        if (currentMode == Constants.MODE_EMPLOYEE) {
            // 员工模式直接通过
            navigateToPhotoSelection();
            return;
        }

        if (TextUtils.isEmpty(inviteCode)) {
            showToast("请输入邀请码");
            return;
        }

        // 离线模式下，简单验证
        if (!NetworkUtils.isOnline(this)) {
            showToast("离线模式：验证通过");
            navigateToPhotoSelection();
            return;
        }

        // 在线验证
        showLoading(true);
        Map<String, String> params = new HashMap<>();
        params.put("invite_code", inviteCode);
        params.put("style_id", styleId);

        RetrofitClient.getInstance().getApiService()
                .verifyInviteCode(params)
                .enqueue(new Callback<ApiService.InviteVerifyResponse>() {
                    @Override
                    public void onResponse(Call<ApiService.InviteVerifyResponse> call,
                                         Response<ApiService.InviteVerifyResponse> response) {
                        showLoading(false);
                        if (response.isSuccessful() && response.body() != null) {
                            ApiService.InviteVerifyResponse verifyResponse = response.body();
                            if (verifyResponse.code == 200 && verifyResponse.data != null
                                    && verifyResponse.data.valid) {
                                navigateToPhotoSelection();
                            } else {
                                showToast("邀请码无效");
                            }
                        } else {
                            showToast("验证失败");
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiService.InviteVerifyResponse> call, Throwable t) {
                        showLoading(false);
                        showToast("验证失败：" + t.getMessage());
                    }
                });
    }

    /**
     * 处理支付
     */
    private void handlePayment() {
        String payCode = etInviteCode.getText().toString().trim();

        // 如果输入了验证码（支付后），直接验证
        if (!TextUtils.isEmpty(payCode)) {
            verifyPaymentAndNavigate(payCode);
            return;
        }

        // 创建支付订单
        if (!NetworkUtils.isOnline(this)) {
            showToast("离线模式：支付功能需要网络连接");
            return;
        }

        showLoading(true);
        Map<String, Object> params = new HashMap<>();
        params.put("style_id", styleId);
        params.put("payment_method", "wechat");  // 默认微信支付
        params.put("amount", 9.9);  // 默认金额，可从配置读取
        params.put("device_id", android.provider.Settings.Secure.getString(
                getContentResolver(), android.provider.Settings.Secure.ANDROID_ID));

        RetrofitClient.getInstance().getApiService()
                .createPayment(params)
                .enqueue(new Callback<ApiService.PaymentResponse>() {
                    @Override
                    public void onResponse(Call<ApiService.PaymentResponse> call,
                                         Response<ApiService.PaymentResponse> response) {
                        showLoading(false);
                        if (response.isSuccessful() && response.body() != null) {
                            ApiService.PaymentResponse paymentResponse = response.body();
                            if (paymentResponse.code == 200 && paymentResponse.data != null) {
                                // 显示支付二维码对话框
                                showPaymentQRCodeDialog(paymentResponse.data);
                            } else {
                                showToast("创建支付订单失败：" + paymentResponse.message);
                            }
                        } else {
                            showToast("创建支付订单失败");
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiService.PaymentResponse> call, Throwable t) {
                        showLoading(false);
                        showToast("创建支付订单失败：" + t.getMessage());
                    }
                });
    }

    /**
     * 显示支付二维码对话框
     */
    private void showPaymentQRCodeDialog(ApiService.PaymentResponse.Data paymentData) {
        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
        builder.setTitle("扫码支付");

        // 创建对话框布局
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_payment_qr, null);
        ImageView ivQRCode = dialogView.findViewById(R.id.iv_qr_code);
        TextView tvAmount = dialogView.findViewById(R.id.tv_amount);
        TextView tvOrderId = dialogView.findViewById(R.id.tv_order_id);
        Button btnConfirm = dialogView.findViewById(R.id.btn_confirm);
        Button btnRefresh = dialogView.findViewById(R.id.btn_refresh);

        tvAmount.setText(String.format("￥%.2f", 9.9));
        tvOrderId.setText("订单号：" + paymentData.order_id);

        // 使用二维码生成库加载二维码（这里简化处理）
        // 实际应用应使用 ZXing 或 GsonQRCode 库生成二维码
        if (paymentData.qr_code_url != null) {
            // 使用 Glide 或其他图片加载库加载二维码图片
            // 这里简化处理
            android.util.Log.d("Payment", "QR Code URL: " + paymentData.qr_code_url);
            showToast("请扫码支付，完成后点击\"确认支付\"");
        }

        builder.setView(dialogView);

        android.app.AlertDialog dialog = builder.create();
        dialog.show();

        // 确认支付按钮
        btnConfirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 验证支付状态
                verifyPaymentStatus(paymentData.order_id, dialog);
            }
        });

        // 刷新状态按钮
        btnRefresh.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                verifyPaymentStatus(paymentData.order_id, dialog);
            }
        });

        // 自动轮询支付状态
        startPaymentStatusPolling(paymentData.order_id, dialog);
    }

    /**
     * 验证支付状态
     */
    private void verifyPaymentStatus(String orderId, android.app.AlertDialog dialog) {
        if (!NetworkUtils.isOnline(this)) {
            showToast("网络不可用");
            return;
        }

        RetrofitClient.getInstance().getApiService()
                .queryPayment(orderId)
                .enqueue(new Callback<ApiService.PaymentQueryResponse>() {
                    @Override
                    public void onResponse(Call<ApiService.PaymentQueryResponse> call,
                                         Response<ApiService.PaymentQueryResponse> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            ApiService.PaymentQueryResponse queryResponse = response.body();
                            if (queryResponse.code == 200 && queryResponse.data != null) {
                                if (queryResponse.data.payment_status == 1) {
                                    // 支付成功
                                    if (dialog != null && dialog.isShowing()) {
                                        dialog.dismiss();
                                    }
                                    showToast("支付成功！");
                                    navigateToPhotoSelection();
                                } else {
                                    showToast("支付状态：" + queryResponse.data.payment_status_text);
                                }
                            }
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiService.PaymentQueryResponse> call, Throwable t) {
                        showToast("查询支付状态失败：" + t.getMessage());
                    }
                });
    }

    /**
     * 开始轮询支付状态
     */
    private void startPaymentStatusPolling(String orderId, android.app.AlertDialog dialog) {
        Handler handler = new Handler(Looper.getMainLooper());
        final Runnable[] pollingRunnableHolder = new Runnable[1];
        final int[] pollingCount = {0};
        final int MAX_POLLING = 30;  // 最多轮询30次（5分钟）

        pollingRunnableHolder[0] = new Runnable() {
            @Override
            public void run() {
                if (pollingCount[0] >= MAX_POLLING || (dialog != null && !dialog.isShowing())) {
                    return;
                }

                pollingCount[0]++;

                RetrofitClient.getInstance().getApiService()
                        .queryPayment(orderId)
                        .enqueue(new Callback<ApiService.PaymentQueryResponse>() {
                            @Override
                            public void onResponse(Call<ApiService.PaymentQueryResponse> call,
                                                 Response<ApiService.PaymentQueryResponse> response) {
                                if (response.isSuccessful() && response.body() != null) {
                                    ApiService.PaymentQueryResponse queryResponse = response.body();
                                    if (queryResponse.code == 200 && queryResponse.data != null
                                            && queryResponse.data.payment_status == 1) {
                                        // 支付成功
                                        if (dialog != null && dialog.isShowing()) {
                                            dialog.dismiss();
                                        }
                                        showToast("支付成功！");
                                        navigateToPhotoSelection();
                                        return;
                                    }
                                }
                                // 继续轮询
                                handler.postDelayed(pollingRunnableHolder[0], 10000);  // 10秒后再次查询
                            }

                            @Override
                            public void onFailure(Call<ApiService.PaymentQueryResponse> call, Throwable t) {
                                // 继续轮询
                                handler.postDelayed(pollingRunnableHolder[0], 10000);
                            }
                        });
            }
        };

        handler.postDelayed(pollingRunnableHolder[0], 10000);  // 10秒后开始查询
    }

    /**
     * 验证支付验证码并导航（简化版本）
     */
    private void verifyPaymentAndNavigate(String code) {
        // 这里可以实现支付后输入验证码的逻辑
        // 暂时简化为直接通过
        navigateToPhotoSelection();
    }

    private void showLoading(boolean show) {
        progressBar.setVisibility(show ? View.VISIBLE : View.GONE);
        btnVerify.setEnabled(!show);
        btnPayment.setEnabled(!show);
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
