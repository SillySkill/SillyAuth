package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.Switch;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.StyleConfig;
import com.jcoding.aiactivity.manager.CameraDeviceManager;
import com.jcoding.aiactivity.manager.ConfigManager;

import java.util.ArrayList;
import java.util.List;

/**
 * AI百变秀设置页
 * 配置AI百变秀模块的各种参数和行为
 */
public class AiShowSettingsActivity extends BaseActivity {

    // 基础设置
    private Switch swAiShowEnabled;
    private Spinner spinnerDefaultStyle;
    private Button btnStyleManagement;  // 风格管理按钮

    // 参与模式
    private Switch swInviteCodeMode;
    private Button btnInviteCodeManage;  // 邀请码管理按钮
    private Switch swPaymentMode;
    private Switch swEmployeeMode;

    // 语音与交互
    private Switch swVoiceGuidance;
    private Switch swDigitalHuman;
    private Switch swVoiceCommand;

    // 高级设置
    private Switch swAutoPushInner;
    private Switch swShowGenerationTime;
    private Switch swSignatureReminder;
    private Spinner spinnerGenerationQuality;  // 生成质量

    // 拍照倒计时
    private android.widget.SeekBar seekbarCountdown;
    private android.widget.TextView tvCountdownValue;

    // 结果展示时间
    private android.widget.SeekBar seekbarResultDisplayTime;
    private android.widget.TextView tvResultDisplayTimeValue;

    // 摄像头设备选择
    private Spinner spinnerCameraDevice;
    private LinearLayout layoutWifiCameraConfig;
    private EditText etWifiRtspUrl;
    private Button btnAddWifiCamera;

    private Button btnSave;
    private Button btnReset;
    private Button btnBack;

    private ConfigManager configManager;
    private CameraDeviceManager cameraDeviceManager;

    // 风格列表
    private List<String> styleNameList;
    private List<String> styleIdList;
    private ArrayAdapter<String> styleAdapter;

    // 摄像头列表
    private List<CameraDeviceManager.CameraInfo> cameraList;
    private List<String> cameraNameList;
    private ArrayAdapter<String> cameraAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ai_show_settings);

        configManager = ConfigManager.getInstance(this);
        cameraDeviceManager = CameraDeviceManager.getInstance(this);

        initViews();
        loadStyleList();
        loadCameraList();
        loadSettings();
        setupListeners();
    }

    /**
     * 初始化视图
     */
    private void initViews() {
        // 基础设置
        swAiShowEnabled = findViewById(R.id.sw_ai_show_enabled);
        spinnerDefaultStyle = findViewById(R.id.spinner_default_style);
        btnStyleManagement = findViewById(R.id.btn_style_management);

        // 参与模式
        swInviteCodeMode = findViewById(R.id.sw_invite_code_mode);
        btnInviteCodeManage = findViewById(R.id.btn_invite_code_manage);
        swPaymentMode = findViewById(R.id.sw_payment_mode);
        swEmployeeMode = findViewById(R.id.sw_employee_mode);

        // 语音与交互
        swVoiceGuidance = findViewById(R.id.sw_voice_guidance);
        swDigitalHuman = findViewById(R.id.sw_digital_human);
        swVoiceCommand = findViewById(R.id.sw_voice_command);

        // 高级设置
        swAutoPushInner = findViewById(R.id.sw_auto_push_inner);
        swShowGenerationTime = findViewById(R.id.sw_show_generation_time);
        swSignatureReminder = findViewById(R.id.sw_signature_reminder);
        spinnerGenerationQuality = findViewById(R.id.spinner_generation_quality);

        // 初始化生成质量选项
        ArrayAdapter<CharSequence> qualityAdapter = ArrayAdapter.createFromResource(this,
                R.array.generation_quality_entries,
                android.R.layout.simple_spinner_item);
        qualityAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerGenerationQuality.setAdapter(qualityAdapter);

        // 拍照倒计时
        seekbarCountdown = findViewById(R.id.seekbar_countdown);
        tvCountdownValue = findViewById(R.id.tv_countdown_value);

        // 结果展示时间
        seekbarResultDisplayTime = findViewById(R.id.seekbar_result_display_time);
        tvResultDisplayTimeValue = findViewById(R.id.tv_result_display_time_value);

        // 摄像头设备选择
        spinnerCameraDevice = findViewById(R.id.spinner_camera_device);
        layoutWifiCameraConfig = findViewById(R.id.layout_wifi_camera_config);
        etWifiRtspUrl = findViewById(R.id.et_wifi_rtsp_url);
        btnAddWifiCamera = findViewById(R.id.btn_add_wifi_camera);

        // 按钮
        btnSave = findViewById(R.id.btn_save);
        btnReset = findViewById(R.id.btn_reset);
        btnBack = findViewById(R.id.btn_back);

        // 初始化风格列表
        styleNameList = new ArrayList<>();
        styleIdList = new ArrayList<>();
        styleAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, styleNameList);
        styleAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerDefaultStyle.setAdapter(styleAdapter);

        // 初始化摄像头列表
        cameraList = new ArrayList<>();
        cameraNameList = new ArrayList<>();
        cameraAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, cameraNameList);
        cameraAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerCameraDevice.setAdapter(cameraAdapter);
    }

    /**
     * 加载风格列表
     */
    private void loadStyleList() {
        styleNameList.clear();
        styleIdList.clear();

        // 添加"未选择"选项
        styleNameList.add("未选择");
        styleIdList.add("");

        // 加载所有风格
        List<StyleConfig> styles = configManager.getStyleConfigs();
        for (StyleConfig style : styles) {
            styleNameList.add(style.getName());
            styleIdList.add(style.getStyleId());
        }

        styleAdapter.notifyDataSetChanged();
    }

    /**
     * 加载摄像头列表
     */
    private void loadCameraList() {
        cameraList.clear();
        cameraNameList.clear();

        // 检测所有可用的摄像头
        cameraDeviceManager.detectCameras();
        List<CameraDeviceManager.CameraInfo> cameras = cameraDeviceManager.getAvailableCameras();

        for (CameraDeviceManager.CameraInfo camera : cameras) {
            cameraList.add(camera);
            cameraNameList.add(camera.getCameraName() + " (" + camera.getType().getDisplayName() + ")");
        }

        cameraAdapter.notifyDataSetChanged();
    }

    /**
     * 加载当前设置
     */
    private void loadSettings() {
        // 基础设置
        swAiShowEnabled.setChecked(configManager.isAiShowEnabled());

        String defaultStyleId = configManager.getAiShowDefaultStyle();
        if (defaultStyleId != null && styleIdList.contains(defaultStyleId)) {
            int position = styleIdList.indexOf(defaultStyleId);
            spinnerDefaultStyle.setSelection(position);
        }

        // 参与模式
        swInviteCodeMode.setChecked(configManager.isInviteCodeModeEnabled());
        swPaymentMode.setChecked(configManager.isPaymentModeEnabled());
        swEmployeeMode.setChecked(configManager.isEmployeeModeEnabled());

        // 语音与交互
        swVoiceGuidance.setChecked(configManager.isVoiceGuidanceEnabled());
        swDigitalHuman.setChecked(configManager.isDigitalHumanEnabled());
        swVoiceCommand.setChecked(configManager.isVoiceCommandEnabled());

        // 高级设置
        swAutoPushInner.setChecked(configManager.isAutoPushInnerEnabled());
        swShowGenerationTime.setChecked(configManager.isShowGenerationTimeEnabled());
        swSignatureReminder.setChecked(configManager.isSignatureReminderEnabled());

        // 生成质量（默认4K）
        String quality = configManager.getGenerationQuality();
        if (quality == null) {
            quality = "4k";  // 默认4K
        }
        String[] qualityValues = getResources().getStringArray(R.array.generation_quality_values);
        for (int i = 0; i < qualityValues.length; i++) {
            if (qualityValues[i].equals(quality)) {
                spinnerGenerationQuality.setSelection(i);
                break;
            }
        }

        // 拍照倒计时
        int countdownSeconds = configManager.getPhotoCountdownSeconds();
        seekbarCountdown.setProgress(countdownSeconds);
        updateCountdownLabel(countdownSeconds);

        // 结果展示时间
        int resultDisplayTime = configManager.getAutoCloseTime();
        seekbarResultDisplayTime.setProgress(resultDisplayTime);
        updateResultDisplayTimeLabel(resultDisplayTime);

        // 摄像头设备选择
        CameraDeviceManager.CameraInfo selectedCamera = cameraDeviceManager.getSelectedCamera();
        if (selectedCamera != null && !cameraList.isEmpty()) {
            for (int i = 0; i < cameraList.size(); i++) {
                if (cameraList.get(i).getCameraId().equals(selectedCamera.getCameraId())) {
                    spinnerCameraDevice.setSelection(i);
                    break;
                }
            }
        }

        // 如果有WiFi摄像头的RTSP地址，显示在输入框中
        String wifiRtspUrl = cameraDeviceManager.getWifiCameraRtspUrl();
        if (!TextUtils.isEmpty(wifiRtspUrl)) {
            etWifiRtspUrl.setText(wifiRtspUrl);
        }

        // 更新模式开关状态
        updateModeSwitchesState();
    }

    /**
     * 设置监听器
     */
    private void setupListeners() {
        // AI百变秀总开关
        swAiShowEnabled.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                updateModeSwitchesState();
                if (!isChecked) {
                    showToast("关闭后AI百变秀入口将隐藏");
                }
            }
        });

        // 保存按钮
        btnSave.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveSettings();
            }
        });

        // 重置按钮
        btnReset.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resetToDefault();
            }
        });

        // 返回按钮
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        // 邀请码管理按钮
        btnInviteCodeManage.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开邀请码管理页面
                Intent intent = new Intent(AiShowSettingsActivity.this, InviteCodeManagementActivity.class);
                startActivity(intent);
            }
        });

        // 风格管理按钮
        btnStyleManagement.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开风格管理页面
                Intent intent = new Intent(AiShowSettingsActivity.this, StyleManagementActivity.class);
                startActivity(intent);
            }
        });

        // 拍照倒计时SeekBar监听
        seekbarCountdown.setOnSeekBarChangeListener(new android.widget.SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(android.widget.SeekBar seekBar, int progress, boolean fromUser) {
                updateCountdownLabel(progress);
            }

            @Override
            public void onStartTrackingTouch(android.widget.SeekBar seekBar) {
            }

            @Override
            public void onStopTrackingTouch(android.widget.SeekBar seekBar) {
            }
        });

        // 结果展示时间SeekBar监听
        seekbarResultDisplayTime.setOnSeekBarChangeListener(new android.widget.SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(android.widget.SeekBar seekBar, int progress, boolean fromUser) {
                updateResultDisplayTimeLabel(progress);
            }

            @Override
            public void onStartTrackingTouch(android.widget.SeekBar seekBar) {
            }

            @Override
            public void onStopTrackingTouch(android.widget.SeekBar seekBar) {
            }
        });

        // 摄像头设备选择监听
        spinnerCameraDevice.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) {
                if (position >= 0 && position < cameraList.size()) {
                    CameraDeviceManager.CameraInfo selectedCamera = cameraList.get(position);
                    // 如果选择了WiFi摄像头，显示配置区域
                    if (selectedCamera.getType() == CameraDeviceManager.CameraType.WIFI) {
                        layoutWifiCameraConfig.setVisibility(View.VISIBLE);
                        if (!TextUtils.isEmpty(selectedCamera.getRtspUrl())) {
                            etWifiRtspUrl.setText(selectedCamera.getRtspUrl());
                        }
                    } else {
                        layoutWifiCameraConfig.setVisibility(View.GONE);
                    }
                }
            }

            @Override
            public void onNothingSelected(android.widget.AdapterView<?> parent) {
            }
        });

        // 添加WiFi摄像头按钮监听
        btnAddWifiCamera.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String rtspUrl = etWifiRtspUrl.getText().toString().trim();
                if (TextUtils.isEmpty(rtspUrl)) {
                    showToast("请输入RTSP地址");
                    return;
                }

                // 简单验证RTSP地址格式
                if (!rtspUrl.toLowerCase().startsWith("rtsp://")) {
                    showToast("请输入正确的RTSP地址（以rtsp://开头）");
                    return;
                }

                // 保存WiFi摄像头配置并重新加载列表
                cameraDeviceManager.setWifiCameraRtspUrl(rtspUrl);
                loadCameraList();

                // 选中新添加的WiFi摄像头
                for (int i = 0; i < cameraList.size(); i++) {
                    if (cameraList.get(i).getType() == CameraDeviceManager.CameraType.WIFI) {
                        spinnerCameraDevice.setSelection(i);
                        break;
                    }
                }

                showToast("WiFi摄像头已添加");
            }
        });
    }

    /**
     * 更新倒计时标签
     */
    private void updateCountdownLabel(int seconds) {
        tvCountdownValue.setText(String.valueOf(seconds) + "秒");
    }

    /**
     * 更新结果展示时间标签
     */
    private void updateResultDisplayTimeLabel(int seconds) {
        if (seconds == 0) {
            tvResultDisplayTimeValue.setText("手动关闭");
        } else {
            tvResultDisplayTimeValue.setText(String.valueOf(seconds) + "秒");
        }
    }

    /**
     * 更新模式开关状态
     */
    private void updateModeSwitchesState() {
        boolean enabled = swAiShowEnabled.isChecked();
        swInviteCodeMode.setEnabled(enabled);
        swPaymentMode.setEnabled(enabled);
        swEmployeeMode.setEnabled(enabled);
        spinnerDefaultStyle.setEnabled(enabled);
    }

    /**
     * 保存设置
     */
    private void saveSettings() {
        // 基础设置
        configManager.setAiShowEnabled(swAiShowEnabled.isChecked());

        int selectedPosition = spinnerDefaultStyle.getSelectedItemPosition();
        if (selectedPosition > 0 && selectedPosition < styleIdList.size()) {
            String defaultStyleId = styleIdList.get(selectedPosition);
            configManager.setAiShowDefaultStyle(defaultStyleId);
        }

        // 参与模式
        configManager.setInviteCodeModeEnabled(swInviteCodeMode.isChecked());
        configManager.setPaymentModeModeEnabled(swPaymentMode.isChecked());
        configManager.setEmployeeModeEnabled(swEmployeeMode.isChecked());

        // 语音与交互
        configManager.setVoiceGuidanceEnabled(swVoiceGuidance.isChecked());
        configManager.setDigitalHumanEnabled(swDigitalHuman.isChecked());
        configManager.setVoiceCommandEnabled(swVoiceCommand.isChecked());

        // 高级设置
        configManager.setAutoPushInnerEnabled(swAutoPushInner.isChecked());
        configManager.setShowGenerationTimeEnabled(swShowGenerationTime.isChecked());
        configManager.setSignatureReminderEnabled(swSignatureReminder.isChecked());

        // 生成质量
        String[] qualityValues = getResources().getStringArray(R.array.generation_quality_values);
        int qualityPosition = spinnerGenerationQuality.getSelectedItemPosition();
        if (qualityPosition >= 0 && qualityPosition < qualityValues.length) {
            configManager.setGenerationQuality(qualityValues[qualityPosition]);
        }

        // 拍照倒计时
        configManager.setPhotoCountdownSeconds(seekbarCountdown.getProgress());

        // 结果展示时间
        configManager.setAutoCloseTime(seekbarResultDisplayTime.getProgress());

        // 摄像头设备选择
        int selectedCameraPosition = spinnerCameraDevice.getSelectedItemPosition();
        if (selectedCameraPosition >= 0 && selectedCameraPosition < cameraList.size()) {
            CameraDeviceManager.CameraInfo selectedCamera = cameraList.get(selectedCameraPosition);
            cameraDeviceManager.setSelectedCamera(selectedCamera);
        }

        showToast("设置已保存");
        finish();
    }

    /**
     * 恢复默认设置
     */
    private void resetToDefault() {
        // 基础设置
        swAiShowEnabled.setChecked(true);
        spinnerDefaultStyle.setSelection(0);

        // 参与模式
        swInviteCodeMode.setChecked(true);
        swPaymentMode.setChecked(true);
        swEmployeeMode.setChecked(true);

        // 语音与交互
        swVoiceGuidance.setChecked(true);
        swDigitalHuman.setChecked(true);
        swVoiceCommand.setChecked(true);

        // 高级设置
        swAutoPushInner.setChecked(false);
        swShowGenerationTime.setChecked(true);
        swSignatureReminder.setChecked(true);

        // 生成质量（默认4K）
        String[] qualityValues = getResources().getStringArray(R.array.generation_quality_values);
        for (int i = 0; i < qualityValues.length; i++) {
            if ("4k".equals(qualityValues[i])) {
                spinnerGenerationQuality.setSelection(i);
                break;
            }
        }

        // 拍照倒计时
        seekbarCountdown.setProgress(20);
        updateCountdownLabel(20);

        showToast("已恢复默认设置");
    }
}
