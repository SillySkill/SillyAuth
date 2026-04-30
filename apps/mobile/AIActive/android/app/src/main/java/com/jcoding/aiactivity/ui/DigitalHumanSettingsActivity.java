package com.jcoding.aiactivity.ui;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.ConfigManager;

/**
 * 数字人设置页
 * 配置数字人显示、位置、大小等参数
 */
public class DigitalHumanSettingsActivity extends BaseActivity {

    private ConfigManager configManager;

    // 基础开关
    private Switch swDigitalHumanEnabled;

    // 模块独立开关
    private Switch swAiShowEnabled;
    private Switch swQuizEnabled;
    private Switch swLotteryEnabled;
    private Switch swInnerEnabled;
    private Switch swDigitalHumanLocked;

    // 显示配置
    private SeekBar seekBarPositionX;
    private SeekBar seekBarPositionY;
    private TextView tvPositionXValue;
    private TextView tvPositionYValue;

    private Button btnSave;
    private ImageButton btnBack;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_digital_human_settings);

        configManager = ConfigManager.getInstance(this);

        initViews();
        loadSettings();
        setupListeners();
    }

    private void initViews() {
        // 基础开关
        swDigitalHumanEnabled = findViewById(R.id.sw_digital_human_enabled);

        // 模块独立开关
        swAiShowEnabled = findViewById(R.id.sw_ai_show_enabled);
        swQuizEnabled = findViewById(R.id.sw_quiz_enabled);
        swLotteryEnabled = findViewById(R.id.sw_lottery_enabled);
        swInnerEnabled = findViewById(R.id.sw_inner_enabled);
        swDigitalHumanLocked = findViewById(R.id.sw_digital_human_locked);

        // 显示配置
        seekBarPositionX = findViewById(R.id.seek_bar_position_x);
        seekBarPositionY = findViewById(R.id.seek_bar_position_y);
        tvPositionXValue = findViewById(R.id.tv_position_x_value);
        tvPositionYValue = findViewById(R.id.tv_position_y_value);

        // 按钮
        btnSave = findViewById(R.id.btn_save);
        btnBack = findViewById(R.id.btn_back);

        // 初始化位置滑块
        seekBarPositionX.setProgress(configManager.getDigitalHumanPositionX());
        seekBarPositionY.setProgress(configManager.getDigitalHumanPositionY());
        updatePositionLabels();
    }

    private void loadSettings() {
        // 基础开关
        swDigitalHumanEnabled.setChecked(configManager.isDigitalHumanEnabled());

        // 模块独立开关
        swAiShowEnabled.setChecked(configManager.isDigitalHumanEnabledForModule("ai_show"));
        swQuizEnabled.setChecked(configManager.isDigitalHumanEnabledForModule("quiz"));
        swLotteryEnabled.setChecked(configManager.isDigitalHumanEnabledForModule("lottery"));
        swInnerEnabled.setChecked(configManager.isDigitalHumanEnabledForModule("inner"));

        // 锁定开关
        swDigitalHumanLocked.setChecked(configManager.isDigitalHumanLocked());

        // 显示位置
        seekBarPositionX.setProgress(configManager.getDigitalHumanPositionX());
        seekBarPositionY.setProgress(configManager.getDigitalHumanPositionY());
        updatePositionLabels();
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnSave.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveSettings();
            }
        });

        // 总开关变化时，更新模块开关状态
        swDigitalHumanEnabled.setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                updateModuleSwitchesState();
            }
        });

        // X轴位置滑块变化
        seekBarPositionX.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                updatePositionLabels();
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
            }
        });

        // Y轴位置滑块变化
        seekBarPositionY.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                updatePositionLabels();
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
            }
        });
    }

    /**
     * 更新位置标签
     */
    private void updatePositionLabels() {
        tvPositionXValue.setText(seekBarPositionX.getProgress() + "%");
        tvPositionYValue.setText(seekBarPositionY.getProgress() + "%");
    }

    /**
     * 更新模块开关状态
     */
    private void updateModuleSwitchesState() {
        boolean globalEnabled = swDigitalHumanEnabled.isChecked();

        swAiShowEnabled.setEnabled(globalEnabled);
        swQuizEnabled.setEnabled(globalEnabled);
        swLotteryEnabled.setEnabled(globalEnabled);
        swInnerEnabled.setEnabled(globalEnabled);

        if (!globalEnabled) {
            // 总开关关闭时，所有模块开关也关闭
            swAiShowEnabled.setChecked(false);
            swQuizEnabled.setChecked(false);
            swLotteryEnabled.setChecked(false);
            swInnerEnabled.setChecked(false);
        }
    }

    /**
     * 保存设置
     */
    private void saveSettings() {
        // 保存总开关
        configManager.setDigitalHumanEnabled(swDigitalHumanEnabled.isChecked());

        // 保存模块开关
        configManager.setDigitalHumanEnabledForModule("ai_show", swAiShowEnabled.isChecked());
        configManager.setDigitalHumanEnabledForModule("quiz", swQuizEnabled.isChecked());
        configManager.setDigitalHumanEnabledForModule("lottery", swLotteryEnabled.isChecked());
        configManager.setDigitalHumanEnabledForModule("inner", swInnerEnabled.isChecked());

        // 保存显示位置（XY坐标）
        configManager.setDigitalHumanPositionX(seekBarPositionX.getProgress());
        configManager.setDigitalHumanPositionY(seekBarPositionY.getProgress());

        // 保存锁定状态
        configManager.setDigitalHumanLocked(swDigitalHumanLocked.isChecked());

        showToast("数字人设置已保存");
        finish();
    }

    @Override
    protected void showOfflineNotice() {
        // 设置页不显示离线提示
    }

    @Override
    protected void hideOfflineNotice() {
        // 设置页不显示离线提示
    }
}
