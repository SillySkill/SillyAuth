package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.cardview.widget.CardView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.QuizConfigManager;
import com.jcoding.aiactivity.manager.VoiceManager;
import com.jcoding.aiactivity.utils.NetworkUtils;
import android.widget.TextView;

/**
 * 知识问答首页
 * 显示题库选择和开始答题按钮
 */
public class QuizHomeActivity extends BaseActivity {

    private static final String TAG = "QuizHomeActivity";

    private Button btnStartQuiz;
    private Button btnBack;
    private Button btnToggleDigitalHumanLock; // 数字人锁定/解锁控制按钮
    private TextView tvQuizTitle;

    // 题库卡片（只有一个）
    private CardView cardCategory1;

    // 选中标记
    private ImageView ivCheck1;
    private ImageView ivBackground;

    private String selectedQuestionBankId = null; // 选中的题库ID
    private QuizConfigManager configManager;
    private VoiceManager voiceManager;

    // 数字人相关
    private com.jcoding.aiactivity.widget.DigitalHumanView digitalHumanView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Log.d(TAG, "========== onCreate 开始 ==========");
        setContentView(R.layout.activity_quiz_home);

        configManager = QuizConfigManager.getInstance(this);
        voiceManager = VoiceManager.getInstance(this);
        initViews();
        initDigitalHuman();
        setupListeners();

        Log.d(TAG, "========== onCreate 完成 ==========");
    }

    private void initViews() {
        Log.d(TAG, "initViews: 开始初始化视图");

        // 设置背景图片
        ivBackground = findViewById(R.id.iv_background);
        loadBackgroundImage();

        // 动态设置标题
        tvQuizTitle = findViewById(R.id.tv_quiz_title);
        if (tvQuizTitle != null && configManager != null) {
            String title = configManager.getQuizTitle();
            tvQuizTitle.setText(title);
            Log.d(TAG, "设置标题为: " + title);
        }

        btnStartQuiz = findViewById(R.id.btn_start_quiz);
        btnBack = findViewById(R.id.btn_back);
        btnToggleDigitalHumanLock = findViewById(R.id.btn_toggle_digital_human_lock);

        cardCategory1 = findViewById(R.id.card_category_1);

        ivCheck1 = findViewById(R.id.iv_check_1);

        Log.d(TAG, "initViews: btnStartQuiz = " + (btnStartQuiz != null ? "找到" : "未找到"));
        Log.d(TAG, "initViews: btnBack = " + (btnBack != null ? "找到" : "未找到"));
        Log.d(TAG, "initViews: btnToggleDigitalHumanLock = " + (btnToggleDigitalHumanLock != null ? "找到" : "未找到"));
        Log.d(TAG, "initViews: cardCategory1 = " + (cardCategory1 != null ? "找到" : "未找到"));

        if (btnStartQuiz == null) {
            Log.e(TAG, "btnStartQuiz 为 null！无法设置点击监听");
            Toast.makeText(this, "按钮初始化失败", Toast.LENGTH_SHORT).show();
        }

        // 默认选中第一个题库
        if (cardCategory1 != null) {
            selectQuestionBank(1);
        }
    }

    private void setupListeners() {
        Log.d(TAG, "setupListeners: 开始设置监听器");

        // 返回按钮
        if (btnBack != null) {
            btnBack.setOnClickListener(v -> {
                Log.d(TAG, "btnBack 被点击");
                finish();
            });
        }

        // 题库卡片点击监听
        if (cardCategory1 != null) {
            cardCategory1.setOnClickListener(v -> selectQuestionBank(1));
        }

        // 开始答题按钮
        if (btnStartQuiz != null) {
            btnStartQuiz.setOnClickListener(v -> {
                Log.d(TAG, "btnStartQuiz 被点击，选中题库ID: " + selectedQuestionBankId);
                if (selectedQuestionBankId == null) {
                    Toast.makeText(this, "请先选择题库", Toast.LENGTH_SHORT).show();
                    return;
                }
                Toast.makeText(this, "开始答题...", Toast.LENGTH_SHORT).show();
                startQuiz();
            });
            Log.d(TAG, "setupListeners: btnStartQuiz 点击监听已设置");
        } else {
            Log.e(TAG, "setupListeners: btnStartQuiz 为 null，跳过设置监听器");
        }

        // 数字人锁定/解锁按钮
        Log.d(TAG, "setupListeners: btnToggleDigitalHumanLock = " + (btnToggleDigitalHumanLock != null ? "找到" : "未找到"));
        if (btnToggleDigitalHumanLock != null) {
            btnToggleDigitalHumanLock.setOnClickListener(v -> {
                Log.d(TAG, "========== 控制按钮被点击 ==========");
                toggleDigitalHumanLock();
            });
            Log.d(TAG, "setupListeners: 控制按钮监听器已设置");
        } else {
            Log.e(TAG, "setupListeners: btnToggleDigitalHumanLock 为 null，跳过设置监听器");
        }
    }

    private void startQuiz() {
        Log.d(TAG, "startQuiz: 准备跳转到 QuizActivity");
        try {
            Intent intent = new Intent(this, QuizActivity.class);
            intent.putExtra("question_bank_id", selectedQuestionBankId);
            startActivity(intent);
            Log.d(TAG, "startQuiz: startActivity 已调用");
        } catch (Exception e) {
            Log.e(TAG, "startQuiz: 跳转失败", e);
            Toast.makeText(this, "启动失败: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * 选择题库
     */
    private void selectQuestionBank(int categoryIndex) {
        Log.d(TAG, "选择题库: " + categoryIndex);

        // 隐藏所有选中标记
        hideAllCheckMarks();

        // 设置选中的题库ID
        if (categoryIndex == 1) {
            selectedQuestionBankId = "jcq101";
            if (ivCheck1 != null) {
                ivCheck1.setVisibility(View.VISIBLE);
            }
            highlightCard(cardCategory1);
        }

        Log.d(TAG, "已选择题库ID: " + selectedQuestionBankId);
    }

    /**
     * 隐藏所有选中标记
     */
    private void hideAllCheckMarks() {
        if (ivCheck1 != null) {
            ivCheck1.setVisibility(View.GONE);
        }
    }

    /**
     * 高亮选中的卡片
     */
    private void highlightCard(CardView selectedCard) {
        if (selectedCard == null) return;

        // 重置所有卡片样式
        if (cardCategory1 != null) {
            cardCategory1.setCardBackgroundColor(android.graphics.Color.WHITE);
        }

        // 设置选中卡片的背景色为淡粉色
        selectedCard.setCardBackgroundColor(android.graphics.Color.parseColor("#FFF0F5"));
    }

    @Override
    protected void onNetworkChanged(boolean isOnline, NetworkUtils.NetworkType type) {
        // 网络状态变化，暂时不处理
        Log.d(TAG, "onNetworkChanged: isOnline=" + isOnline);
    }

    /**
     * 从 assets 加载背景图片
     */
    private void loadBackgroundImage() {
        if (ivBackground == null) {
            return;
        }

        try {
            // 从 assets 加载图片
            java.io.InputStream inputStream = getAssets().open("image/question_bk.png");
            android.graphics.Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(inputStream);
            inputStream.close();

            if (bitmap != null) {
                ivBackground.setImageBitmap(bitmap);
                Log.d(TAG, "背景图片加载成功");
            } else {
                Log.e(TAG, "背景图片解码失败");
            }
        } catch (java.io.IOException e) {
            Log.e(TAG, "加载背景图片失败: " + e.getMessage());
        }
    }

    /**
     * 初始化数字人
     */
    private void initDigitalHuman() {
        try {
            digitalHumanView = findViewById(R.id.digital_human_view);
            if (digitalHumanView != null) {
                // 设置模块ID为quiz，以便使用quiz的配置（3倍默认缩放，无限放大）
                digitalHumanView.setModuleId("quiz");

                // 加载数字人（使用实际的项目ID）
                digitalHumanView.loadDigitalHuman("JC2026012100001");
                digitalHumanView.setVisibility(View.VISIBLE);
                Log.d(TAG, "数字人初始化成功");

                // 延迟设置锁定状态，确保在restoreDigitalHumanState之后
                digitalHumanView.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        // 设置为锁定状态（默认禁用拖拽）
                        digitalHumanView.setDragAndScaleEnabled(false);

                        // 设置初始elevation为锁定状态（数字人在ScrollView之下）
                        android.widget.ScrollView scrollView = findViewById(R.id.scrollView);
                        if (scrollView != null) {
                            digitalHumanView.setElevation(1);
                            scrollView.setElevation(4);
                            Log.d(TAG, "数字人初始状态: 锁定，elevation=1dp, ScrollView=4dp");
                        }
                    }
                }, 200); // 延迟200ms，确保restoreDigitalHumanState已完成

                // 页面加载完成后播报欢迎语音
                digitalHumanView.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        speakWelcomeMessage();
                    }
                }, 1000); // 延迟1秒播报
            } else {
                Log.e(TAG, "数字人视图未找到");
            }
        } catch (Exception e) {
            Log.e(TAG, "初始化数字人失败", e);
        }
    }

    /**
     * 切换数字人锁定/解锁状态
     */
    private void toggleDigitalHumanLock() {
        if (digitalHumanView == null) {
            Log.w(TAG, "digitalHumanView为null，无法切换锁定状态");
            return;
        }

        boolean currentState = digitalHumanView.isDragAndScaleEnabled();
        boolean newState = !currentState;

        Log.d(TAG, "切换数字人锁定状态: " + (currentState ? "解锁→锁定" : "锁定→解锁"));

        // 先设置拖拽/缩放状态（这会禁用/启用触摸事件）
        digitalHumanView.setDragAndScaleEnabled(newState);

        // 动态调整elevation（在主线程中执行，避免触发布局重绘）
        android.widget.ScrollView scrollView = findViewById(R.id.scrollView);
        if (scrollView != null && digitalHumanView != null) {
            if (newState) {
                // 解锁状态：数字人在ScrollView之上，可以拖拽
                Log.d(TAG, "设置解锁状态：数字人elevation=5, ScrollView=2");

                // 先调整ScrollView
                scrollView.setElevation(2);
                // 再调整数字人
                digitalHumanView.setElevation(5);

                btnToggleDigitalHumanLock.setText("🔓");
                Toast.makeText(this, "数字人已解锁\n可拖拽调整位置和大小", Toast.LENGTH_SHORT).show();
            } else {
                // 锁定状态：ScrollView在数字人之上，不影响功能点击
                Log.d(TAG, "设置锁定状态：数字人elevation=1, ScrollView=4");

                // 先调整数字人
                digitalHumanView.setElevation(1);
                // 再调整ScrollView
                scrollView.setElevation(4);

                btnToggleDigitalHumanLock.setText("🔒");
                Toast.makeText(this, "数字人已锁定\n位置已固定", Toast.LENGTH_SHORT).show();
            }

            Log.d(TAG, "数字人当前位置: X=" + digitalHumanView.getX() + ", Y=" + digitalHumanView.getY());
            Log.d(TAG, "数字人当前缩放: " + digitalHumanView.getScaleX());
        } else {
            Log.e(TAG, "scrollView或digitalHumanView为null");
        }
    }

    /**
     * 播报欢迎消息
     */
    private void speakWelcomeMessage() {
        if (voiceManager == null) {
            return;
        }

        try {
            // 获取配置的题目数量
            int roundQty = configManager.getRoundQty();
            String message = "请选择题目类别，回答对" + roundQty + "题有奖哦";

            // 使用TTS播报，数字人开始说话动画
            if (digitalHumanView != null) {
                digitalHumanView.startTalking();
            }

            voiceManager.speakText(message, new VoiceManager.VoiceSynthesisCallback() {
                @Override
                public void onSpeakStart() {
                    Log.d(TAG, "TTS播报开始");
                }

                @Override
                public void onSpeakPaused() {
                    // 暂停时不处理
                }

                @Override
                public void onSpeakResumed() {
                    // 恢复时不处理
                }

                @Override
                public void onSpeakComplete() {
                    Log.d(TAG, "TTS播报完成");
                    // 停止数字人说话动画
                    if (digitalHumanView != null) {
                        digitalHumanView.stopTalking();
                    }
                }

                @Override
                public void onError(String error) {
                    Log.e(TAG, "TTS播报错误: " + error);
                    // 停止数字人说话动画
                    if (digitalHumanView != null) {
                        digitalHumanView.stopTalking();
                    }
                }
            });
        } catch (Exception e) {
            Log.e(TAG, "播报欢迎消息失败", e);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // 停止数字人播报
        if (digitalHumanView != null) {
            digitalHumanView.stopTalking();
        }
    }
}
