package com.jcoding.aiactivity.ui;

import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.QuizConfigManager;
import com.jcoding.aiactivity.manager.QuizPrizeConfigManager;
import com.jcoding.aiactivity.manager.UserLoginManager;
import com.jcoding.aiactivity.manager.VoiceManager;

import java.util.ArrayList;
import java.util.List;

/**
 * 知识问答设置页
 */
public class QuizSettingsActivity extends BaseActivity {

    private Spinner spinQuestionOrder;
    private Spinner spinColorTheme;
    private TextView tvQuestionOrderDescription;
    private Switch switchVoiceEnabled;
    private Switch switchAutoSubmit;
    private android.widget.EditText etRoundQty;
    private android.widget.EditText etRoundChoice;
    private android.widget.EditText etRoundJudgement;
    private android.widget.EditText etPrizeThreshold;
    private android.widget.EditText etQuizTitle;
    private Switch switchPrizeEnabled;
    private Switch switchRequireLogin;
    private Switch switchPushToInner;
    private TextView tvSubmitModeDescription;
    private Button btnSaveSettings;
    private Button btnResetSettings;
    private Button btnBack;

    // 色彩预览视图
    private View viewColorPrimary;
    private View viewColorDark;
    private View viewColorBg;
    private TextView tvColorThemeName;

    private QuizConfigManager configManager;
    private QuizPrizeConfigManager prizeConfigManager;
    private VoiceManager voiceManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_quiz_settings);

        configManager = QuizConfigManager.getInstance(this);
        prizeConfigManager = QuizPrizeConfigManager.getInstance(this);
        voiceManager = VoiceManager.getInstance(this);

        initViews();
        loadSettings();
        setupListeners();
    }

    private void initViews() {
        spinQuestionOrder = findViewById(R.id.spin_question_order);
        spinColorTheme = findViewById(R.id.spin_color_theme);
        tvQuestionOrderDescription = findViewById(R.id.tv_question_order_description);
        switchVoiceEnabled = findViewById(R.id.switch_voice_enabled);
        switchAutoSubmit = findViewById(R.id.switch_auto_submit);
        etRoundQty = findViewById(R.id.et_round_qty);
        etRoundChoice = findViewById(R.id.et_round_choice);
        etRoundJudgement = findViewById(R.id.et_round_judgement);
        etPrizeThreshold = findViewById(R.id.et_prize_threshold);
        etQuizTitle = findViewById(R.id.et_quiz_title);
        switchPrizeEnabled = findViewById(R.id.switch_prize_enabled);
        switchRequireLogin = findViewById(R.id.switch_require_login);
        switchPushToInner = findViewById(R.id.switch_push_to_inner);
        tvSubmitModeDescription = findViewById(R.id.tv_submit_mode_description);
        btnSaveSettings = findViewById(R.id.btn_save_settings);
        btnResetSettings = findViewById(R.id.btn_reset_settings);
        btnBack = findViewById(R.id.btn_back);

        // 色彩预览视图
        viewColorPrimary = findViewById(R.id.view_color_primary);
        viewColorDark = findViewById(R.id.view_color_dark);
        viewColorBg = findViewById(R.id.view_color_bg);
        tvColorThemeName = findViewById(R.id.tv_color_theme_name);

        // 准备出题顺序选项
        List<String> orderOptions = new ArrayList<>();
        for (QuizConfigManager.QuestionOrder order : QuizConfigManager.QuestionOrder.values()) {
            orderOptions.add(order.getDisplayName() + " - " + order.getDescription());
        }

        ArrayAdapter<String> orderAdapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_spinner_item,
                orderOptions
        );
        orderAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinQuestionOrder.setAdapter(orderAdapter);

        // 准备色彩风格选项
        List<String> colorOptions = new ArrayList<>();
        for (QuizConfigManager.ColorTheme theme : QuizConfigManager.ColorTheme.values()) {
            colorOptions.add(theme.getDisplayName());
        }

        ArrayAdapter<String> colorAdapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_spinner_item,
                colorOptions
        );
        colorAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinColorTheme.setAdapter(colorAdapter);

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    private void loadSettings() {
        // 加载出题顺序
        QuizConfigManager.QuestionOrder currentOrder = configManager.getQuestionOrder();
        for (int i = 0; i < QuizConfigManager.QuestionOrder.values().length; i++) {
            if (QuizConfigManager.QuestionOrder.values()[i] == currentOrder) {
                spinQuestionOrder.setSelection(i);
                break;
            }
        }
        updateOrderDescription(currentOrder);

        // 加载语音开关
        switchVoiceEnabled.setChecked(configManager.isVoiceEnabled());

        // 检查语音功能是否可用（腾讯云或MiniMax任一即可）
        if (!voiceManager.isInitialized()) {
            switchVoiceEnabled.setEnabled(false);
            findViewById(R.id.layout_voice_hint).setVisibility(View.VISIBLE);
        }

        // 加载自动提交开关
        switchAutoSubmit.setChecked(configManager.isAutoSubmit());
        updateSubmitModeDescription(configManager.isAutoSubmit());

        // 加载轮次配置
        etRoundQty.setText(String.valueOf(configManager.getRoundQty()));
        etRoundChoice.setText(String.valueOf(configManager.getRoundChoice()));
        etRoundJudgement.setText(String.valueOf(configManager.getRoundJudgement()));

        // 加载标题设置
        etQuizTitle.setText(configManager.getQuizTitle());

        // 加载色彩风格
        QuizConfigManager.ColorTheme currentTheme = configManager.getColorTheme();
        for (int i = 0; i < QuizConfigManager.ColorTheme.values().length; i++) {
            if (QuizConfigManager.ColorTheme.values()[i] == currentTheme) {
                spinColorTheme.setSelection(i);
                break;
            }
        }
        updateColorPreview(currentTheme);

        // 加载奖品设置
        switchPrizeEnabled.setChecked(prizeConfigManager.isPrizeEnabled());
        switchRequireLogin.setChecked(prizeConfigManager.isRequireLogin());
        switchPushToInner.setChecked(prizeConfigManager.isPushToInner());

        // 加载奖品门槛
        int prizeThreshold = prizeConfigManager.getPrizeThreshold();
        if (prizeThreshold > 0) {
            etPrizeThreshold.setText(String.valueOf(prizeThreshold));
        } else {
            // 如果没有设置，使用默认值10
            etPrizeThreshold.setText("10");
        }
    }

    private void setupListeners() {
        // 出题顺序选择监听
        spinQuestionOrder.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                QuizConfigManager.QuestionOrder selectedOrder = QuizConfigManager.QuestionOrder.values()[position];
                configManager.setQuestionOrder(selectedOrder);
                updateOrderDescription(selectedOrder);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        // 色彩风格选择监听
        spinColorTheme.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                QuizConfigManager.ColorTheme selectedTheme = QuizConfigManager.ColorTheme.values()[position];
                configManager.setColorTheme(selectedTheme);
                updateColorPreview(selectedTheme);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        // 语音开关监听
        switchVoiceEnabled.setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                configManager.setVoiceEnabled(isChecked);
                if (isChecked && !voiceManager.isInitialized()) {
                    showToast("语音功能未初始化，请先在语音设置中配置MiniMax或腾讯云密钥");
                    switchVoiceEnabled.setChecked(false);
                }
            }
        });

        // 自动提交开关监听
        switchAutoSubmit.setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                configManager.setAutoSubmit(isChecked);
                updateSubmitModeDescription(isChecked);
            }
        });

        // 奖品功能开关监听
        switchPrizeEnabled.setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                prizeConfigManager.setPrizeEnabled(isChecked);
            }
        });

        // 需要登录开关监听
        switchRequireLogin.setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                prizeConfigManager.setRequireLogin(isChecked);
                if (isChecked && !UserLoginManager.getInstance(QuizSettingsActivity.this).isLoggedIn()) {
                    showToast("提示：用户需要先登录才能参与奖品活动");
                }
            }
        });

        // 推送到内场设备开关监听
        switchPushToInner.setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                prizeConfigManager.setPushToInner(isChecked);
                if (isChecked) {
                    showToast("中奖信息将推送到内场设备");
                }
            }
        });

        // 保存设置按钮监听
        btnSaveSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveAllSettings();
            }
        });

        // 重置设置按钮监听
        btnResetSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                configManager.resetToDefault();
                loadSettings();
                showToast("已重置为默认设置");
            }
        });
    }

    private void updateOrderDescription(QuizConfigManager.QuestionOrder order) {
        tvQuestionOrderDescription.setText(order.getDescription());
    }

    private void updateSubmitModeDescription(boolean autoSubmit) {
        if (autoSubmit) {
            tvSubmitModeDescription.setText("选择答案后自动进入下一题");
        } else {
            tvSubmitModeDescription.setText("选择答案后需点击\'提交\'按钮确认");
        }
    }

    /**
     * 更新色彩预览
     */
    private void updateColorPreview(QuizConfigManager.ColorTheme theme) {
        if (viewColorPrimary != null) {
            viewColorPrimary.setBackgroundColor(theme.getPrimaryColor());
        }
        if (viewColorDark != null) {
            viewColorDark.setBackgroundColor(theme.getDarkColor());
        }
        if (viewColorBg != null) {
            viewColorBg.setBackgroundColor(theme.getBackgroundColor());
        }
        if (tvColorThemeName != null) {
            tvColorThemeName.setText(theme.getDisplayName());
        }
    }

    /**
     * 保存所有设置
     */
    private void saveAllSettings() {
        // 保存轮次配置
        try {
            String qtyStr = etRoundQty.getText().toString();
            String choiceStr = etRoundChoice.getText().toString();
            String judgementStr = etRoundJudgement.getText().toString();
            String thresholdStr = etPrizeThreshold.getText().toString();

            if (qtyStr.isEmpty() || choiceStr.isEmpty() || judgementStr.isEmpty() || thresholdStr.isEmpty()) {
                showToast("请填写完整的配置");
                return;
            }

            int qty = Integer.parseInt(qtyStr);
            int choice = Integer.parseInt(choiceStr);
            int judgement = Integer.parseInt(judgementStr);
            int threshold = Integer.parseInt(thresholdStr);

            // 验证输入
            if (qty < 1 || qty > 100) {
                showToast("题目总数必须在1-100之间");
                return;
            }
            if (choice < 0 || judgement < 0) {
                showToast("选择题和判断题数量不能为负数");
                return;
            }
            if (threshold < 1 || threshold > qty) {
                showToast("奖品门槛必须在1-" + qty + "之间");
                return;
            }

            configManager.setRoundQty(qty);
            configManager.setRoundChoice(choice);
            configManager.setRoundJudgement(judgement);

            // 保存奖品门槛
            prizeConfigManager.setPrizeThreshold(threshold);

            // 保存标题设置
            String title = etQuizTitle.getText().toString();
            if (!title.isEmpty()) {
                configManager.setQuizTitle(title);
            }

            showToast("设置已保存");
        } catch (NumberFormatException e) {
            showToast("输入格式错误，请输入有效的数字");
        }
    }
}
