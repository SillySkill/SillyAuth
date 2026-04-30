package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.network.ApiService;
import com.jcoding.aiactivity.network.RetrofitClient;
import com.jcoding.aiactivity.utils.PreferenceUtils;
import com.jcoding.aiactivity.utils.Constants;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.util.HashMap;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * 登录页
 * 支持游客模式、员工登录
 */
public class LoginActivity extends BaseActivity {

    private EditText etUsername;
    private EditText etPassword;
    private EditText etInviteCode;
    private Button btnLogin;
    private Button btnGuest;
    private ProgressBar progressBar;
    private TextView tvOfflineMode;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        initViews();
        setupListeners();
    }

    private void initViews() {
        etUsername = findViewById(R.id.et_username);
        etPassword = findViewById(R.id.et_password);
        etInviteCode = findViewById(R.id.et_invite_code);
        btnLogin = findViewById(R.id.btn_login);
        btnGuest = findViewById(R.id.btn_guest);
        progressBar = findViewById(R.id.progress_bar);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);
    }

    private void setupListeners() {
        // 员工登录
        btnLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                handleEmployeeLogin();
            }
        });

        // 游客模式
        btnGuest.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                enterAsGuest();
            }
        });
    }

    /**
     * 处理员工登录
     */
    private void handleEmployeeLogin() {
        String username = etUsername.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        if (TextUtils.isEmpty(username)) {
            showToast("请输入用户名");
            return;
        }

        if (TextUtils.isEmpty(password)) {
            showToast("请输入密码");
            return;
        }

        android.util.Log.d("LoginActivity", "handleEmployeeLogin: username=" + username);

        // 测试模式：离线登录（用于开发测试）
        if ("admin".equals(username) && "jcoding2026".equals(password)) {
            android.util.Log.d("LoginActivity", "Using test credentials - offline login");
            saveLoginInfo("admin_001", "管理员");
            showToast("登录成功（测试模式）");
            navigateToMain();
            return;
        }

        // 检查网络状态
        if (!NetworkUtils.isOnline(this)) {
            showToast("员工登录需要网络连接");
            return;
        }

        // 显示加载状态
        showLoading(true);

        try {
            // 调用登录API
            Map<String, String> params = new HashMap<>();
            params.put("username", username);
            params.put("password", password);

            android.util.Log.d("LoginActivity", "Calling API login...");

            RetrofitClient.getInstance().getApiService()
                    .employeeLogin(params)
                    .enqueue(new Callback<ApiService.LoginResponse>() {
                        @Override
                        public void onResponse(Call<ApiService.LoginResponse> call,
                                             Response<ApiService.LoginResponse> response) {
                            showLoading(false);
                            android.util.Log.d("LoginActivity", "API response received: " + response.code());

                            if (response.isSuccessful() && response.body() != null) {
                                ApiService.LoginResponse loginResponse = response.body();
                                if (loginResponse.code == 200 && loginResponse.data != null) {
                                    // 登录成功
                                    saveLoginInfo(
                                            loginResponse.data.user_id,
                                            loginResponse.data.user_name
                                    );
                                    navigateToMain();
                                } else {
                                    showToast("登录失败：" + loginResponse.message);
                                }
                            } else {
                                showToast("登录失败：服务器错误 (code=" + response.code() + ")");
                            }
                        }

                        @Override
                        public void onFailure(Call<ApiService.LoginResponse> call, Throwable t) {
                            showLoading(false);
                            android.util.Log.e("LoginActivity", "API call failed", t);
                            showToast("登录失败：" + t.getMessage());
                        }
                    });
        } catch (Exception e) {
            showLoading(false);
            android.util.Log.e("LoginActivity", "Login exception", e);
            showToast("登录失败：" + e.getMessage());
        }
    }

    /**
     * 游客模式进入
     */
    private void enterAsGuest() {
        // 游客使用默认用户信息
        saveLoginInfo("guest_" + System.currentTimeMillis(), "游客");
        navigateToMain();
    }

    /**
     * 保存登录信息
     */
    private void saveLoginInfo(String userId, String userName) {
        PreferenceUtils.putString(this, Constants.PREF_USER_ID, userId);
        PreferenceUtils.putString(this, Constants.PREF_USER_NAME, userName);
        PreferenceUtils.putBoolean(this, Constants.PREF_IS_LOGGED_IN, true);
    }

    /**
     * 跳转到主页面
     */
    private void navigateToMain() {
        Intent intent = new Intent(this, ModeSelectionActivity.class);
        startActivity(intent);
        finish();
    }

    /**
     * 显示/隐藏加载状态
     */
    private void showLoading(boolean show) {
        if (progressBar != null) {
            progressBar.setVisibility(show ? View.VISIBLE : View.GONE);
        }
        btnLogin.setEnabled(!show);
        btnGuest.setEnabled(!show);
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
