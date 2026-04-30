package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.jcoding.aiactivity.R;

/**
 * 系统设置页
 */
public class SettingActivity extends BaseActivity {

    private Button btnGeneralSettings;
    private Button btnAiShowSettings;
    private Button btnQuizSettings;
    private Button btnLotterySettings;
    private Button btnInnerSettings;
    private Button btnDigitalHumanSettings;
    private Button btnVoiceSettings;
    private Button btnBack;
    private TextView tvUserName;
    private TextView tvVersion;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_setting);

        initViews();
        setupListeners();
    }

    private void initViews() {
        btnGeneralSettings = findViewById(R.id.btn_general_settings);
        btnAiShowSettings = findViewById(R.id.btn_ai_show_settings);
        btnQuizSettings = findViewById(R.id.btn_quiz_settings);
        btnLotterySettings = findViewById(R.id.btn_lottery_settings);
        btnInnerSettings = findViewById(R.id.btn_inner_settings);
        btnDigitalHumanSettings = findViewById(R.id.btn_digital_human_settings);
        btnVoiceSettings = findViewById(R.id.btn_voice_settings);
        btnBack = findViewById(R.id.btn_back);
        tvUserName = findViewById(R.id.tv_user_name);
        tvVersion = findViewById(R.id.tv_version);

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    private void setupListeners() {
        btnGeneralSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开通用设置
                Intent intent = new Intent(SettingActivity.this, GeneralSettingsActivity.class);
                startActivity(intent);
            }
        });

        btnAiShowSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开AI百变秀设置
                Intent intent = new Intent(SettingActivity.this, AiShowSettingsActivity.class);
                startActivity(intent);
            }
        });

        btnQuizSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开知识问答设置
                Intent intent = new Intent(SettingActivity.this, QuizSettingsActivity.class);
                startActivity(intent);
            }
        });

        btnLotterySettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开抽奖设置
                Intent intent = new Intent(SettingActivity.this, LotterySettingsActivity.class);
                startActivity(intent);
            }
        });

        btnInnerSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开内场秀网络设置
                Intent intent = new Intent(SettingActivity.this, InnerShowNetworkSettingsActivity.class);
                startActivity(intent);
            }
        });

        btnDigitalHumanSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开数字人设置
                Intent intent = new Intent(SettingActivity.this, DigitalHumanSettingsActivity.class);
                startActivity(intent);
            }
        });

        btnVoiceSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 打开语音设置
                Intent intent = new Intent(SettingActivity.this, VoiceSettingsActivity.class);
                startActivity(intent);
            }
        });
    }
}
