package com.jcoding.aiactivity.ui;

import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.InputType;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.DeviceAuthManager;
import com.jcoding.aiactivity.manager.VoiceCommandManager;

/**
 * 语音设置对话框
 * 通过语音命令打开和调整设置
 *
 * 使用流程：
 * 1. 显示识别到的设置命令
 * 2. 要求输入管理员口令
 * 3. 验证通过后显示设置界面
 * 4. 应用设置更改
 */
public class VoiceSettingDialog extends Dialog {

    private static final String TAG = "VoiceSettingDialog";

    private Context context;
    private VoiceCommandManager.VoiceCommand command;
    private OnSettingAppliedListener listener;

    // 管理器
    private ConfigManager configManager;
    private DeviceAuthManager authManager;

    // UI组件
    private TextView tvCommandDescription;
    private TextView tvCommandDetails;
    private EditText etPassword;
    private Button btnVerify;
    private Button btnCancel;
    private TextView tvError;
    private ProgressBar progressBar;

    // 设置界面组件
    private LinearLayout layoutSettings;
    private TextView tvSettingsTitle;
    private View settingsContent;

    // 认证状态
    private boolean isAuthenticated = false;

    public VoiceSettingDialog(Context context, VoiceCommandManager.VoiceCommand command) {
        super(context, R.style.Theme_AppCompat_Light_Dialog);
        this.context = context;
        this.command = command;
        this.configManager = ConfigManager.getInstance(context);
        this.authManager = DeviceAuthManager.getInstance(context);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.dialog_voice_setting);
        setCanceledOnTouchOutside(false);

        // 初始化认证管理器
        authManager.initializeDefaultPassword();

        initViews();
        setupListeners();
        displayCommand();
    }

    private void initViews() {
        // 命令显示区域
        tvCommandDescription = findViewById(R.id.tv_command_description);
        tvCommandDetails = findViewById(R.id.tv_command_details);

        // 认证区域
        etPassword = findViewById(R.id.et_password);
        btnVerify = findViewById(R.id.btn_verify);
        btnCancel = findViewById(R.id.btn_cancel);
        tvError = findViewById(R.id.tv_error);
        progressBar = findViewById(R.id.progress_bar);

        // 设置区域
        layoutSettings = findViewById(R.id.layout_settings);
        tvSettingsTitle = findViewById(R.id.tv_settings_title);
        settingsContent = findViewById(R.id.settings_content);

        // 初始隐藏设置区域
        layoutSettings.setVisibility(View.GONE);
        progressBar.setVisibility(View.GONE);
    }

    private void setupListeners() {
        btnVerify.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String password = etPassword.getText().toString();
                if (password.isEmpty()) {
                    showError("请输入管理员口令");
                    return;
                }

                verifyPassword(password);
            }
        });

        btnCancel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    /**
     * 显示识别到的命令
     */
    private void displayCommand() {
        tvCommandDescription.setText("识别到设置命令：");
        tvCommandDetails.setText(command.description);
        tvCommandDetails.setTextSize(18);
        tvCommandDetails.setTextColor(Color.parseColor("#1976D2"));
    }

    /**
     * 验证口令
     */
    private void verifyPassword(String password) {
        tvError.setVisibility(View.GONE);
        progressBar.setVisibility(View.VISIBLE);
        btnVerify.setEnabled(false);

        authManager.verifyPassword(password, new DeviceAuthManager.AuthCallback() {
            @Override
            public void onSuccess() {
                new Handler(Looper.getMainLooper()).post(new Runnable() {
                    @Override
                    public void run() {
                        progressBar.setVisibility(View.GONE);
                        btnVerify.setEnabled(true);
                        isAuthenticated = true;
                        showSettings();
                    }
                });
            }

            @Override
            public void onError(final String error) {
                new Handler(Looper.getMainLooper()).post(new Runnable() {
                    @Override
                    public void run() {
                        progressBar.setVisibility(View.GONE);
                        btnVerify.setEnabled(true);
                        showError(error);
                        etPassword.setText("");
                        etPassword.requestFocus();
                    }
                });
            }
        });
    }

    /**
     * 显示设置界面
     */
    private void showSettings() {
        // 隐藏认证区域
        etPassword.setVisibility(View.GONE);
        btnVerify.setVisibility(View.GONE);
        btnCancel.setText("关闭");

        // 显示设置区域
        layoutSettings.setVisibility(View.VISIBLE);
        tvSettingsTitle.setText("请调整设置：");

        // 根据命令类型创建设置界面
        settingsContent = createSettingsUI(command);
        layoutSettings.addView(settingsContent, 1);
    }

    /**
     * 创建设置UI
     */
    private View createSettingsUI(VoiceCommandManager.VoiceCommand command) {
        LinearLayout layout = new LinearLayout(context);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(32, 16, 32, 16);

        switch (command.module) {
            case "digital_human":
                createDigitalHumanSettings(layout, command);
                break;
            case "voice":
                createVoiceSettings(layout, command);
                break;
            default:
                createGeneralSettings(layout, command);
                break;
        }

        return layout;
    }

    /**
     * 创建数字人设置UI
     */
    private void createDigitalHumanSettings(LinearLayout layout, VoiceCommandManager.VoiceCommand command) {
        if ("position".equals(command.paramType)) {
            createPositionSelector(layout, command);
        } else if ("size".equals(command.paramType)) {
            createSizeSeekBar(layout, command);
        } else if ("enabled".equals(command.paramType)) {
            createEnabledSwitch(layout, command);
        } else {
            createGeneralSettings(layout, command);
        }
    }

    /**
     * 创建位置选择器
     */
    private void createPositionSelector(LinearLayout layout, VoiceCommandManager.VoiceCommand command) {
        TextView tvLabel = new TextView(context);
        tvLabel.setText("数字人显示位置");
        tvLabel.setTextSize(16);
        tvLabel.setPadding(0, 0, 0, 16);
        layout.addView(tvLabel);

        String[] positions = {"左上角", "右上角", "左下角", "右下角"};
        String[] positionValues = {"left_top", "right_top", "left_bottom", "right_bottom"};

        for (int i = 0; i < positions.length; i++) {
            Button btn = new Button(context);
            btn.setText(positions[i]);
            btn.setTag(positionValues[i]);
            btn.setOnClickListener(new PositionClickListener(positionValues[i]));
            layout.addView(btn);
        }
    }

    /**
     * 创建大小滑块
     */
    private void createSizeSeekBar(LinearLayout layout, VoiceCommandManager.VoiceCommand command) {
        TextView tvLabel = new TextView(context);
        tvLabel.setText("数字人显示大小");
        tvLabel.setTextSize(16);
        tvLabel.setPadding(0, 0, 0, 16);
        layout.addView(tvLabel);

        TextView tvValue = new TextView(context);
        int currentSize = configManager.getDigitalHumanSize();
        tvValue.setText("当前大小: " + currentSize + "dp");
        tvValue.setTextSize(14);
        tvValue.setPadding(0, 0, 0, 16);
        layout.addView(tvValue);

        SeekBar seekBar = new SeekBar(context);
        seekBar.setMax(300); // 100-400
        seekBar.setProgress(currentSize - 100);
        seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                int size = progress + 100;
                tvValue.setText("当前大小: " + size + "dp");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                int size = seekBar.getProgress() + 100;
                configManager.setDigitalHumanSize(size);
                Toast.makeText(context, "数字人大小已设置为 " + size + "dp", Toast.LENGTH_SHORT).show();
                notifySettingApplied();
            }
        });
        layout.addView(seekBar);
    }

    /**
     * 创建开关
     */
    private void createEnabledSwitch(LinearLayout layout, VoiceCommandManager.VoiceCommand command) {
        TextView tvLabel = new TextView(context);
        tvLabel.setText("启用数字人");
        tvLabel.setTextSize(16);
        tvLabel.setPadding(0, 0, 0, 16);
        layout.addView(tvLabel);

        Switch switchEnabled = new Switch(context);
        switchEnabled.setChecked(configManager.isDigitalHumanEnabled());
        switchEnabled.setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                configManager.setDigitalHumanEnabled(isChecked);
                Toast.makeText(context, isChecked ? "数字人已启用" : "数字人已禁用", Toast.LENGTH_SHORT).show();
                notifySettingApplied();
            }
        });
        layout.addView(switchEnabled);
    }

    /**
     * 创建语音设置UI
     */
    private void createVoiceSettings(LinearLayout layout, VoiceCommandManager.VoiceCommand command) {
        TextView tvInfo = new TextView(context);
        tvInfo.setText("语音设置调整功能");
        tvInfo.setTextSize(16);
        tvInfo.setPadding(16, 16, 16, 16);
        layout.addView(tvInfo);

        Button btnOpenSettings = new Button(context);
        btnOpenSettings.setText("打开语音设置页面");
        btnOpenSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
                context.startActivity(new Intent(context, VoiceSettingsActivity.class));
            }
        });
        layout.addView(btnOpenSettings);
    }

    /**
     * 创建通用设置UI
     */
    private void createGeneralSettings(LinearLayout layout, VoiceCommandManager.VoiceCommand command) {
        TextView tvInfo = new TextView(context);
        tvInfo.setText("正在打开设置页面...");
        tvInfo.setTextSize(16);
        tvInfo.setPadding(16, 16, 16, 16);
        layout.addView(tvInfo);

        // 延迟打开设置页面
        layout.postDelayed(new Runnable() {
            @Override
            public void run() {
                dismiss();
                context.startActivity(new Intent(context, SettingActivity.class));
            }
        }, 1500);
    }

    /**
     * 显示错误
     */
    private void showError(String error) {
        tvError.setText(error);
        tvError.setVisibility(View.VISIBLE);
    }

    /**
     * 通知设置已应用
     */
    private void notifySettingApplied() {
        if (listener != null) {
            listener.onSettingApplied(command);
        }
    }

    /**
     * 位置点击监听器
     */
    private class PositionClickListener implements View.OnClickListener {
        private String position;

        public PositionClickListener(String position) {
            this.position = position;
        }

        @Override
        public void onClick(View v) {
            configManager.setDigitalHumanPosition(position);

            String positionName = "";
            switch (position) {
                case "left_top": positionName = "左上角"; break;
                case "right_top": positionName = "右上角"; break;
                case "left_bottom": positionName = "左下角"; break;
                case "right_bottom": positionName = "右下角"; break;
            }

            Toast.makeText(context, "数字人位置已设置为 " + positionName, Toast.LENGTH_SHORT).show();
            notifySettingApplied();
            dismiss();
        }
    }

    /**
     * 设置已应用监听器
     */
    public interface OnSettingAppliedListener {
        void onSettingApplied(VoiceCommandManager.VoiceCommand command);
    }

    public void setOnSettingAppliedListener(OnSettingAppliedListener listener) {
        this.listener = listener;
    }
}
