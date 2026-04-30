package com.jcoding.aiactivity.ui;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.SpeechRecognizerManager;
import com.jcoding.aiactivity.manager.SpeechSynthesizerManager;

import java.util.Locale;

/**
 * 语音功能测试Activity
 * 模仿微信聊天界面，测试TTS和ASR功能
 */
public class VoiceTestActivity extends BaseActivity {

    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 200;

    private ScrollView scrollViewChat;
    private LinearLayout chatContainer;
    private EditText etTextInput;
    private ImageButton btnSend;
    private ImageButton btnVoiceInput;
    private TextView tvStatus;

    private SpeechSynthesizerManager ttsManager;
    private SpeechRecognizerManager asrManager;

    private boolean isListening = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_voice_test);

        ttsManager = SpeechSynthesizerManager.getInstance(this);
        asrManager = SpeechRecognizerManager.getInstance(this);

        initViews();
        checkPermissions();
        setupListeners();

        // 添加欢迎消息
        addSystemMessage("欢迎使用语音测试！\n\n点击麦克风按钮开始语音识别\n输入文字后点击发送可测试TTS语音合成\n\n识别结果和合成文字都会以气泡形式显示");
    }

    private void initViews() {
        scrollViewChat = findViewById(R.id.scroll_view_chat);
        chatContainer = findViewById(R.id.chat_container);
        etTextInput = findViewById(R.id.et_text_input);
        btnSend = findViewById(R.id.btn_send);
        btnVoiceInput = findViewById(R.id.btn_voice_input);
        tvStatus = findViewById(R.id.tv_status);

        findViewById(R.id.btn_back).setOnClickListener(v -> finish());
    }

    private void setupListeners() {
        // 发送按钮
        btnSend.setOnClickListener(v -> {
            String text = etTextInput.getText().toString().trim();
            if (!text.isEmpty()) {
                addUserMessage(text);
                etTextInput.setText("");

                // 使用TTS播报
                speakText(text);
            }
        });

        // 语音输入按钮
        btnVoiceInput.setOnClickListener(v -> {
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        });
    }

    private void checkPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.RECORD_AUDIO},
                    REQUEST_RECORD_AUDIO_PERMISSION);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_RECORD_AUDIO_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                showToast("录音权限已授予");
            } else {
                showToast("需要录音权限才能使用语音识别");
            }
        }
    }

    /**
     * 开始语音识别
     */
    private void startListening() {
        if (!checkTTSAndASRConfigured()) {
            return;
        }

        isListening = true;
        btnVoiceInput.setImageResource(android.R.drawable.ic_delete);
        tvStatus.setText("正在聆听...");
        tvStatus.setTextColor(getResources().getColor(R.color.colorAccent));

        asrManager.startListening(new SpeechRecognizerManager.RecognitionListener() {
            @Override
            public void onResult(String result, boolean isFinal) {
                if (isFinal) {
                    stopListening();
                    addUserMessage(result);

                    // 使用TTS复述
                    addSystemMessage("正在复述...");
                    speakText(result);
                } else {
                    // 实时结果
                    tvStatus.setText("识别中: " + result);
                }
            }

            @Override
            public void onError(int errorCode, String errorMsg) {
                stopListening();
                addSystemMessage("识别失败: " + errorMsg);
            }
        });
    }

    /**
     * 停止语音识别
     */
    private void stopListening() {
        isListening = false;
        btnVoiceInput.setImageResource(R.drawable.ic_mic);
        tvStatus.setText("点击麦克风开始语音输入");
        tvStatus.setTextColor(getResources().getColor(R.color.text_secondary));
        asrManager.stopListening();
    }

    /**
     * 使用TTS播报文字
     */
    private void speakText(String text) {
        if (!checkTTSAndASRConfigured()) {
            return;
        }

        ttsManager.speak(text, new SpeechSynthesizerManager.SynthesisListener() {
            @Override
            public void onSpeakStart() {
                // 添加气泡显示正在播报
                addSystemMessage("🔊 正在播报: " + text);
            }

            @Override
            public void onSpeakComplete() {
                // 播报完成
            }

            @Override
            public void onError(int errorCode, String errorMsg) {
                addSystemMessage("❌ 语音合成失败: " + errorMsg);
            }
        });
    }

    /**
     * 检查TTS和ASR是否已配置
     */
    private boolean checkTTSAndASRConfigured() {
        // TODO: 从ConfigManager检查配置
        // 现在暂时返回true，实际使用时需要检查
        return true;
    }

    /**
     * 添加用户消息气泡（右侧，绿色）
     */
    private void addUserMessage(String text) {
        View bubbleView = createMessageBubble(text, true);
        chatContainer.post(() -> {
            chatContainer.addView(bubbleView);
            scrollToBottom();
        });
    }

    /**
     * 添加系统消息气泡（左侧，白色）
     */
    private void addSystemMessage(String text) {
        View bubbleView = createMessageBubble(text, false);
        chatContainer.post(() -> {
            chatContainer.addView(bubbleView);
            scrollToBottom();
        });
    }

    /**
     * 创建消息气泡
     * @param text 消息文字
     * @param isUser 是否为用户消息
     * @return 消息视图
     */
    private View createMessageBubble(String text, boolean isUser) {
        // 创建外部容器
        LinearLayout container = new LinearLayout(this);
        container.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
        ));
        container.setOrientation(LinearLayout.HORIZONTAL);
        container.setPadding(0, 8, 0, 8);

        if (isUser) {
            container.setGravity(Gravity.END);
        } else {
            container.setGravity(Gravity.START);
        }

        // 创建气泡
        TextView bubble = new TextView(this);
        bubble.setText(text);
        bubble.setTextSize(16f);
        bubble.setPadding(24, 16, 24, 16);

        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
        );

        if (isUser) {
            // 用户消息：右侧绿色气泡
            bubble.setBackgroundColor(0xFF95EC69); // 微信绿
            bubble.setTextColor(0xFF000000);
            params.setMargins(60, 0, 16, 0);
        } else {
            // 系统消息：左侧白色气泡
            bubble.setBackgroundColor(0xFFFFFFFF);
            bubble.setTextColor(0xFF000000);
            params.setMargins(16, 0, 60, 0);
        }

        bubble.setLayoutParams(params);

        container.addView(bubble);
        return container;
    }

    /**
     * 滚动到底部
     */
    private void scrollToBottom() {
        scrollViewChat.post(() -> {
            scrollViewChat.fullScroll(View.FOCUS_DOWN);
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (isListening) {
            stopListening();
        }
        ttsManager.stop();
    }
}
