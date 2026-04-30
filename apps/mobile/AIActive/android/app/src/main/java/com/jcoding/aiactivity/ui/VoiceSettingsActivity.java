package com.jcoding.aiactivity.ui;

import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.data.MiniMaxVoice;
import com.jcoding.aiactivity.data.MiniMaxVoiceProvider;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.VoiceManager;

import java.util.ArrayList;
import java.util.List;

/**
 * 语音设置页
 * 配置TTS语音合成和ASR语音识别参数
 */
public class VoiceSettingsActivity extends BaseActivity {

    private static final String TAG = "VoiceSettingsActivity";

    // TTS引擎类型
    private static final int TTS_ENGINE_TENCENT = 0;
    private static final int TTS_ENGINE_MINIMAX = 1;

    private ConfigManager configManager;
    private VoiceManager voiceManager;

    // TTS引擎选择
    private Spinner spinnerTTSEngine;
    private LinearLayout layoutTencentTTSParams;
    private LinearLayout layoutMiniMaxTTSParams;

    // 腾讯TTS配置
    private Spinner spinnerTTSVoiceType;
    private SeekBar seekBarTTSPitch;
    private TextView tvTTSPitchValue;

    // MiniMax TTS配置
    private EditText etMiniMaxApiKey;
    private EditText etMiniMaxGroupId;
    private Spinner spinnerMiniMaxLanguage;
    private Spinner spinnerMiniMaxVoice;
    private LinearLayout layoutMiniMaxVoiceSelection;

    // 通用TTS配置
    private SeekBar seekBarTTSSpeed;
    private TextView tvTTSSpeedValue;
    private SeekBar seekBarTTSVolume;
    private TextView tvTTSVolumeValue;

    // ASR配置
    private Spinner spinnerASREngineModel;
    private Switch swASRFilterDirty;
    private Switch swASRFilterModal;
    private Switch swASRConvertNumMode;

    private Button btnSave;
    private Button btnTestTTS;
    private ImageButton btnBack;

    // MiniMax语音数据
    private List<String> languages;
    private List<MiniMaxVoice> currentVoices;
    private MiniMaxVoice selectedVoice;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_voice_settings);

        // 调试信息：打印卡通语音数量
        android.util.Log.i("VoiceSettings", "===== VoiceSettings Debug Info =====");
        android.util.Log.i("VoiceSettings", "Total cartoon voices: " + MiniMaxVoiceProvider.getCartoonVoiceCount());
        for (MiniMaxVoice voice : MiniMaxVoiceProvider.getCartoonVoices()) {
            android.util.Log.i("VoiceSettings", "  - " + voice.getDisplayName() + " (" + voice.getVoiceId() + ")");
        }
        android.util.Log.i("VoiceSettings", "======================================");

        configManager = ConfigManager.getInstance(this);
        voiceManager = VoiceManager.getInstance(this);

        initViews();
        loadSettings();
        setupListeners();
    }

    private void initViews() {
        // TTS引擎选择
        spinnerTTSEngine = findViewById(R.id.spinner_tts_engine);
        layoutTencentTTSParams = findViewById(R.id.layout_tencent_tts_params);
        layoutMiniMaxTTSParams = findViewById(R.id.layout_minimax_tts_params);

        // 设置TTS引擎选项
        String[] ttsEngines = {"腾讯云 TTS", "MiniMax TTS"};
        ArrayAdapter<String> engineAdapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_item, ttsEngines);
        engineAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerTTSEngine.setAdapter(engineAdapter);

        // 腾讯TTS配置
        spinnerTTSVoiceType = findViewById(R.id.spinner_tts_voice_type);
        seekBarTTSPitch = findViewById(R.id.seek_bar_tts_pitch);
        tvTTSPitchValue = findViewById(R.id.tv_tts_pitch_value);

        // MiniMax TTS配置
        etMiniMaxApiKey = findViewById(R.id.et_minimax_api_key);
        etMiniMaxGroupId = findViewById(R.id.et_minimax_group_id);
        spinnerMiniMaxLanguage = findViewById(R.id.spinner_minimax_language);
        spinnerMiniMaxVoice = findViewById(R.id.spinner_minimax_voice);
        layoutMiniMaxVoiceSelection = findViewById(R.id.layout_minimax_voice_selection);

        // 设置MiniMax语言选项（添加卡通/动漫分类）
        languages = new ArrayList<>();
        languages.add("🎬 卡通/动漫");  // 特殊分类，放在第一位
        languages.addAll(MiniMaxVoiceProvider.getLanguages());

        android.util.Log.i("VoiceSettings", "Languages list: " + languages.toString());

        ArrayAdapter<String> languageAdapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_item, languages);
        languageAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerMiniMaxLanguage.setAdapter(languageAdapter);

        // 通用TTS配置
        seekBarTTSSpeed = findViewById(R.id.seek_bar_tts_speed);
        tvTTSSpeedValue = findViewById(R.id.tv_tts_speed_value);
        seekBarTTSVolume = findViewById(R.id.seek_bar_tts_volume);
        tvTTSVolumeValue = findViewById(R.id.tv_tts_volume_value);

        // 初始化TTS滑块
        seekBarTTSSpeed.setMax(15); // 0.5-2.0 (x10)
        seekBarTTSPitch.setMax(15); // 0.5-2.0 (x10)
        seekBarTTSVolume.setMax(10); // 0.0-1.0 (x10)

        // ASR配置
        spinnerASREngineModel = findViewById(R.id.spinner_asr_engine_model);
        swASRFilterDirty = findViewById(R.id.sw_asr_filter_dirty);
        swASRFilterModal = findViewById(R.id.sw_asr_filter_modal);
        swASRConvertNumMode = findViewById(R.id.sw_asr_convert_num_mode);

        // 按钮
        btnSave = findViewById(R.id.btn_save);
        btnTestTTS = findViewById(R.id.btn_test_tts);
        btnBack = findViewById(R.id.btn_back);
    }

    private void loadSettings() {
        android.util.Log.i("VoiceSettings", "===== loadSettings() called =====");

        // TTS引擎选择
        String ttsEngine = configManager.getTTSEngine();
        android.util.Log.i("VoiceSettings", "Saved TTS engine: " + ttsEngine);

        int engineIndex = "minimax".equals(ttsEngine) ? TTS_ENGINE_MINIMAX : TTS_ENGINE_TENCENT;
        android.util.Log.i("VoiceSettings", "Calculated engineIndex: " + engineIndex + " (0=Tencent, 1=MiniMax)");

        spinnerTTSEngine.setSelection(engineIndex);
        android.util.Log.i("VoiceSettings", "Set spinner selection to: " + engineIndex);

        updateTTSEngineUI(engineIndex);

        // 初始化语音列表（即使不是MiniMax引擎也要初始化，以备切换使用）
        initMiniMaxVoiceList();

        // 腾讯TTS发音人
        int voiceType = configManager.getTTSVoiceType();
        String[] voiceTypeValues = getResources().getStringArray(R.array.tts_voice_type_values);
        for (int i = 0; i < voiceTypeValues.length; i++) {
            if (Integer.parseInt(voiceTypeValues[i]) == voiceType) {
                spinnerTTSVoiceType.setSelection(i);
                break;
            }
        }

        // 腾讯TTS音调
        float pitch = configManager.getTTSPitch();
        seekBarTTSPitch.setProgress((int) ((pitch - 0.5f) * 10));
        updateTTSPitchLabel();

        // MiniMax配置
        etMiniMaxApiKey.setText(configManager.getMiniMaxApiKey());
        etMiniMaxGroupId.setText(configManager.getMiniMaxGroupId());

        // 通用TTS配置（语速、音量）
        float speed = configManager.getTTSSpeed();
        seekBarTTSSpeed.setProgress((int) ((speed - 0.5f) * 10));
        updateTTSSpeedLabel();

        float volume = configManager.getTTSVolume();
        seekBarTTSVolume.setProgress((int) (volume * 10));
        updateTTSVolumeLabel();

        // ASR引擎类型
        String engineModel = configManager.getASREngineModelType();
        String[] engineModelValues = getResources().getStringArray(R.array.asr_engine_model_values);
        for (int i = 0; i < engineModelValues.length; i++) {
            if (engineModelValues[i].equals(engineModel)) {
                spinnerASREngineModel.setSelection(i);
                break;
            }
        }

        // ASR过滤选项
        swASRFilterDirty.setChecked(configManager.isASRFilterDirty());
        swASRFilterModal.setChecked(configManager.isASRFilterModal());
        swASRConvertNumMode.setChecked(configManager.isASRConvertNumMode());
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

        // 测试TTS按钮
        btnTestTTS.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                testTTS();
            }
        });

        // TTS引擎选择监听
        spinnerTTSEngine.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                android.util.Log.i("VoiceSettings", "===== TTS Engine Spinner onItemSelected =====");
                android.util.Log.i("VoiceSettings", "Selected position: " + position + " (0=Tencent, 1=MiniMax)");
                android.util.Log.i("VoiceSettings", "Selected item: " + parent.getItemAtPosition(position).toString());
                updateTTSEngineUI(position);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        // MiniMax语言选择监听
        spinnerMiniMaxLanguage.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                String language = languages.get(position);
                android.util.Log.i("VoiceSettings", "===== MiniMax Language selected =====");
                android.util.Log.i("VoiceSettings", "Language: " + language);
                updateVoiceList(language);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        // MiniMax发音人选择监听
        spinnerMiniMaxVoice.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                android.util.Log.i("VoiceSettings", "===== MiniMax Voice selected =====");
                android.util.Log.i("VoiceSettings", "Position: " + position);
                if (currentVoices != null && position < currentVoices.size()) {
                    selectedVoice = currentVoices.get(position);
                    android.util.Log.i("VoiceSettings", "Selected voice: " + selectedVoice.getDisplayName());
                } else {
                    android.util.Log.e("VoiceSettings", "Invalid voice selection! currentVoices=" + currentVoices + ", position=" + position);
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        // TTS语速滑块
        seekBarTTSSpeed.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                updateTTSSpeedLabel();
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
            }
        });

        // TTS音调滑块
        seekBarTTSPitch.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                updateTTSPitchLabel();
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
            }
        });

        // TTS音量滑块
        seekBarTTSVolume.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                updateTTSVolumeLabel();
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
     * 初始化MiniMax语音列表
     */
    private void initMiniMaxVoiceList() {
        // 加载MiniMax语音选择
        String miniMaxVoiceId = configManager.getMiniMaxVoiceId();
        android.util.Log.i("VoiceSettings", "Loading saved voice ID: " + miniMaxVoiceId);

        if (TextUtils.isEmpty(miniMaxVoiceId)) {
            miniMaxVoiceId = "Chinese (Mandarin)_Cute_Spirit"; // 默认发音人 - 憨憨萌兽（卡通）
        }
        selectedVoice = MiniMaxVoiceProvider.findVoiceById(miniMaxVoiceId);

        if (selectedVoice != null) {
            android.util.Log.i("VoiceSettings", "Found voice: " + selectedVoice.getDisplayName() +
                    ", language: " + selectedVoice.getLanguage() +
                    ", isCartoon: " + selectedVoice.isCartoon());

            // 如果是卡通声音，选择卡通分类
            if (selectedVoice.isCartoon()) {
                spinnerMiniMaxLanguage.setSelection(0);  // 卡通/动漫在第一位
                updateVoiceList("🎬 卡通/动漫");
            } else {
                // 设置语言
                String lang = selectedVoice.getLanguage();
                int langIndex = languages.indexOf(lang);
                android.util.Log.i("VoiceSettings", "Language: " + lang + ", index: " + langIndex);

                if (langIndex >= 0) {
                    spinnerMiniMaxLanguage.setSelection(langIndex);
                    updateVoiceList(lang);
                } else {
                    // 如果找不到语言，默认使用中文
                    android.util.Log.w("VoiceSettings", "Language not found in list, using default");
                    spinnerMiniMaxLanguage.setSelection(1);  // 中文通常在第二个位置
                    updateVoiceList("中文");
                }
            }

            // 设置发音人
            if (currentVoices != null && currentVoices.contains(selectedVoice)) {
                int voiceIndex = currentVoices.indexOf(selectedVoice);
                if (voiceIndex >= 0) {
                    spinnerMiniMaxVoice.setSelection(voiceIndex);
                }
            }
        } else {
            // 使用默认发音人
            android.util.Log.w("VoiceSettings", "Voice not found, using default");
            selectedVoice = MiniMaxVoiceProvider.getDefaultVoice();
            spinnerMiniMaxLanguage.setSelection(1);  // 中文
            updateVoiceList("中文");
        }
    }

    /**
     * 根据TTS引擎选择更新UI
     */
    private void updateTTSEngineUI(int engineIndex) {
        android.util.Log.i("VoiceSettings", "========== updateTTSEngineUI called ==========");
        android.util.Log.i("VoiceSettings", "engineIndex: " + engineIndex);
        android.util.Log.i("VoiceSettings", "TTS_ENGINE_MINIMAX: " + TTS_ENGINE_MINIMAX);
        android.util.Log.i("VoiceSettings", "isMiniMax: " + (engineIndex == TTS_ENGINE_MINIMAX));

        // 检查views是否为null
        android.util.Log.i("VoiceSettings", "layoutTencentTTSParams is null: " + (layoutTencentTTSParams == null));
        android.util.Log.i("VoiceSettings", "layoutMiniMaxTTSParams is null: " + (layoutMiniMaxTTSParams == null));
        android.util.Log.i("VoiceSettings", "layoutMiniMaxVoiceSelection is null: " + (layoutMiniMaxVoiceSelection == null));

        if (engineIndex == TTS_ENGINE_MINIMAX) {
            android.util.Log.i("VoiceSettings", "SWITCHING TO MINIMAX - Showing MiniMax UI, hiding Tencent");
            // 显示MiniMax参数，隐藏腾讯TTS参数
            layoutTencentTTSParams.setVisibility(View.GONE);
            layoutMiniMaxTTSParams.setVisibility(View.VISIBLE);
            layoutMiniMaxVoiceSelection.setVisibility(View.VISIBLE);

            android.util.Log.i("VoiceSettings", "After setting visibility:");
            android.util.Log.i("VoiceSettings", "  layoutTencentTTSParams visibility: " + layoutTencentTTSParams.getVisibility() + " (GONE=8, VISIBLE=0)");
            android.util.Log.i("VoiceSettings", "  layoutMiniMaxTTSParams visibility: " + layoutMiniMaxTTSParams.getVisibility());
            android.util.Log.i("VoiceSettings", "  layoutMiniMaxVoiceSelection visibility: " + layoutMiniMaxVoiceSelection.getVisibility());
        } else {
            android.util.Log.i("VoiceSettings", "SWITCHING TO TENCENT - Showing Tencent UI, hiding MiniMax");
            // 显示腾讯TTS参数，隐藏MiniMax参数
            layoutTencentTTSParams.setVisibility(View.VISIBLE);
            layoutMiniMaxTTSParams.setVisibility(View.GONE);
            layoutMiniMaxVoiceSelection.setVisibility(View.GONE);

            android.util.Log.i("VoiceSettings", "After setting visibility:");
            android.util.Log.i("VoiceSettings", "  layoutTencentTTSParams visibility: " + layoutTencentTTSParams.getVisibility() + " (VISIBLE=0, GONE=8)");
            android.util.Log.i("VoiceSettings", "  layoutMiniMaxTTSParams visibility: " + layoutMiniMaxTTSParams.getVisibility());
            android.util.Log.i("VoiceSettings", "  layoutMiniMaxVoiceSelection visibility: " + layoutMiniMaxVoiceSelection.getVisibility());
        }
        android.util.Log.i("VoiceSettings", "========================================");
    }

    /**
     * 更新MiniMax语音列表
     */
    private void updateVoiceList(String language) {
        android.util.Log.i("VoiceSettings", "===== updateVoiceList() called =====");
        android.util.Log.i("VoiceSettings", "Language parameter: " + language);

        // 处理卡通/动漫分类
        if (language.equals("🎬 卡通/动漫")) {
            currentVoices = MiniMaxVoiceProvider.getCartoonVoices();
            android.util.Log.i("VoiceSettings", "Loading CARTOON voices");
        } else {
            currentVoices = MiniMaxVoiceProvider.getVoicesByLanguage(language);
            android.util.Log.i("VoiceSettings", "Loading voices for language: " + language);
        }

        // 检查是否获取到了语音列表
        if (currentVoices == null || currentVoices.isEmpty()) {
            android.util.Log.e("VoiceSettings", "No voices found for language: " + language);
            android.util.Log.e("VoiceSettings", "currentVoices is null: " + (currentVoices == null));
            if (currentVoices != null) {
                android.util.Log.e("VoiceSettings", "currentVoices.size(): " + currentVoices.size());
            }
            return;
        }

        android.util.Log.i("VoiceSettings", "Found " + currentVoices.size() + " voices");

        List<String> voiceNames = new ArrayList<>();
        for (MiniMaxVoice voice : currentVoices) {
            String displayName = voice.getDisplayName();
            // 为卡通声音添加特殊标记
            if (voice.isCartoon()) {
                displayName = "🎬 " + displayName;
            }
            voiceNames.add(displayName + " (" + voice.getCategory() + ")");
            android.util.Log.i("VoiceSettings", "  - " + voice.getDisplayName() + " (" + voice.getVoiceId() + ")");
        }

        ArrayAdapter<String> voiceAdapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_item, voiceNames);
        voiceAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerMiniMaxVoice.setAdapter(voiceAdapter);

        android.util.Log.i("VoiceSettings", "Set adapter to spinnerMiniMaxVoice with " + voiceNames.size() + " items");

        // 如果有选中的发音人，尝试保持选中状态
        if (selectedVoice != null && currentVoices.contains(selectedVoice)) {
            int voiceIndex = currentVoices.indexOf(selectedVoice);
            if (voiceIndex >= 0) {
                spinnerMiniMaxVoice.setSelection(voiceIndex);
                android.util.Log.i("VoiceSettings", "Maintained selected voice: " + selectedVoice.getDisplayName());
            }
        } else if (currentVoices.size() > 0) {
            // 默认选择第一个
            selectedVoice = currentVoices.get(0);
            android.util.Log.i("VoiceSettings", "Selected first voice by default: " + selectedVoice.getDisplayName());
        }

        android.util.Log.i("VoiceSettings", "=====================================");
    }

    /**
     * 更新TTS语速标签
     */
    private void updateTTSSpeedLabel() {
        float speed = 0.5f + (seekBarTTSSpeed.getProgress() / 10.0f);
        tvTTSSpeedValue.setText(String.format("%.1f", speed));
    }

    /**
     * 更新TTS音调标签
     */
    private void updateTTSPitchLabel() {
        float pitch = 0.5f + (seekBarTTSPitch.getProgress() / 10.0f);
        tvTTSPitchValue.setText(String.format("%.1f", pitch));
    }

    /**
     * 更新TTS音量标签
     */
    private void updateTTSVolumeLabel() {
        float volume = seekBarTTSVolume.getProgress() / 10.0f;
        tvTTSVolumeValue.setText(String.format("%.1f", volume));
    }

    /**
     * 保存设置
     */
    private void saveSettings() {
        // 保存TTS引擎选择
        int engineIndex = spinnerTTSEngine.getSelectedItemPosition();
        String ttsEngine = (engineIndex == TTS_ENGINE_MINIMAX) ? "minimax" : "tencent";
        configManager.setTTSEngine(ttsEngine);

        // 保存通用TTS配置（语速、音量）
        float speed = 0.5f + (seekBarTTSSpeed.getProgress() / 10.0f);
        configManager.setTTSSpeed(speed);

        float volume = seekBarTTSVolume.getProgress() / 10.0f;
        configManager.setTTSVolume(volume);

        // 根据引擎保存特定配置
        if (engineIndex == TTS_ENGINE_MINIMAX) {
            // 保存MiniMax配置
            String apiKey = etMiniMaxApiKey.getText().toString().trim();
            String groupId = etMiniMaxGroupId.getText().toString().trim();

            if (TextUtils.isEmpty(apiKey) || TextUtils.isEmpty(groupId)) {
                showToast("请填写MiniMax API Key和Group ID");
                return;
            }

            configManager.setMiniMaxApiKey(apiKey);
            configManager.setMiniMaxGroupId(groupId);

            // 保存选中的发音人
            if (selectedVoice != null) {
                configManager.setMiniMaxVoiceId(selectedVoice.getVoiceId());
            } else {
                // 使用默认发音人
                MiniMaxVoice defaultVoice = MiniMaxVoiceProvider.getDefaultVoice();
                configManager.setMiniMaxVoiceId(defaultVoice.getVoiceId());
            }
        } else {
            // 保存腾讯TTS配置
            String voiceTypeStr = getResources().getStringArray(R.array.tts_voice_type_values)
                    [spinnerTTSVoiceType.getSelectedItemPosition()];
            configManager.setTTSVoiceType(Integer.parseInt(voiceTypeStr));

            float pitch = 0.5f + (seekBarTTSPitch.getProgress() / 10.0f);
            configManager.setTTSPitch(pitch);
        }

        // 保存ASR配置
        int asrSpinnerPosition = spinnerASREngineModel.getSelectedItemPosition();
        if (asrSpinnerPosition >= 0) {
            String[] asrEngineModelValues = getResources().getStringArray(R.array.asr_engine_model_values);
            if (asrSpinnerPosition < asrEngineModelValues.length) {
                String engineModel = asrEngineModelValues[asrSpinnerPosition];
                configManager.setASREngineModelType(engineModel);
            }
        }

        configManager.setASRFilterDirty(swASRFilterDirty.isChecked());
        configManager.setASRFilterModal(swASRFilterModal.isChecked());
        configManager.setASRConvertNumMode(swASRConvertNumMode.isChecked());

        showToast("语音设置已保存");
        finish();
    }

    /**
     * 测试TTS语音合成
     */
    private void testTTS() {
        int engineIndex = spinnerTTSEngine.getSelectedItemPosition();
        String testText = "大家好，我来了";

        if (engineIndex == TTS_ENGINE_MINIMAX) {
            // 测试MiniMax TTS
            String apiKey = etMiniMaxApiKey.getText().toString().trim();
            String groupId = etMiniMaxGroupId.getText().toString().trim();

            if (TextUtils.isEmpty(apiKey)) {
                // 尝试从assets加载
                apiKey = configManager.getMiniMaxApiKey();
                if (TextUtils.isEmpty(apiKey)) {
                    showToast("请先配置MiniMax API Key");
                    return;
                }
            }

            if (TextUtils.isEmpty(groupId)) {
                showToast("请先填写MiniMax Group ID");
                return;
            }

            // 临时保存配置用于测试
            String originalApiKey = configManager.getMiniMaxApiKey();
            String originalGroupId = configManager.getMiniMaxGroupId();
            String originalVoiceId = configManager.getMiniMaxVoiceId();

            configManager.setMiniMaxApiKey(apiKey);
            configManager.setMiniMaxGroupId(groupId);

            // 保存选中的发音人
            if (selectedVoice != null) {
                configManager.setMiniMaxVoiceId(selectedVoice.getVoiceId());
            } else {
                // 使用默认发音人
                MiniMaxVoice defaultVoice = MiniMaxVoiceProvider.getDefaultVoice();
                configManager.setMiniMaxVoiceId(defaultVoice.getVoiceId());
            }

            // 重新初始化VoiceManager
            voiceManager.reinitialize();

            showToast("正在测试MiniMax语音合成...");
        } else {
            // 测试腾讯TTS
            showToast("正在测试腾讯云语音合成...");
        }

        // 使用VoiceManager播放测试文本
        voiceManager.speakText(testText, new VoiceManager.VoiceSynthesisCallback() {
            @Override
            public void onSpeakStart() {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        // 播放开始
                    }
                });
            }

            @Override
            public void onSpeakPaused() {
            }

            @Override
            public void onSpeakResumed() {
            }

            @Override
            public void onSpeakComplete() {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        showToast("语音合成测试完成");
                    }
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        showToast("语音合成测试失败: " + error);
                    }
                });
            }
        });
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
