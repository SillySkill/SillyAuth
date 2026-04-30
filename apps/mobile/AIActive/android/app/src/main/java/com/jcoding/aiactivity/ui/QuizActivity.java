package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.Manifest;
import android.graphics.Color;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.Question;
import com.jcoding.aiactivity.entity.QuestionBank;
import com.jcoding.aiactivity.manager.QuizConfigManager;
import com.jcoding.aiactivity.manager.QuizPrizeConfigManager;
import com.jcoding.aiactivity.manager.VoiceManager;
import com.jcoding.aiactivity.manager.VoiceCommandManager;
import com.jcoding.aiactivity.manager.DigitalHumanManager;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

/**
 * 知识问答页
 * 支持选择题和判断题
 * 新增功能：
 * - 出题顺序控制（混合/先选择题/先判断题）
 * - TTS语音播报题目
 * - ASR语音识别答案
 * - 触摸选项自动打断TTS
 * - 自动提交/手动提交模式
 * - 数字人展示和播报
 */
public class QuizActivity extends BaseActivity {

    private TextView tvQuestionNumber;
    private TextView tvQuestion;
    private TextView tvQuizTitle;  // 题库标题
    private View layoutQuestionContainer;  // 题目容器
    private TextView tvVoiceStatus;
    private Button btnOptionA;
    private Button btnOptionB;
    private Button btnOptionC;
    private Button btnOptionD;
    private Button btnNext;
    private Button btnSubmit;
    private Button btnVoiceInput;
    private ProgressBar progressBar;
    private Button btnBack;
    private Button btnToggleDigitalHumanLock;
    private TextView tvOfflineMode;

    // 数字人相关 - 使用视频组件
    private com.jcoding.aiactivity.widget.DigitalHumanView digitalHumanView;

    private QuestionBank questionBank;
    private List<Question> questionList;
    private String questionBankId;  // 题库ID
    private int currentQuestionIndex = 0;
    private int correctCount = 0;
    private int[] userAnswers;
    private boolean hasShownCongratulations = false; // 标记是否已显示恭喜弹窗
    private Random random;

    private QuizConfigManager configManager;
    private QuizPrizeConfigManager prizeConfigManager;
    private VoiceManager voiceManager;
    private VoiceCommandManager voiceCommandManager;
    private DigitalHumanManager digitalHumanManager;
    private boolean isSpeakingQuestion = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // 添加显著的日志标记
        android.util.Log.e("QuizActivity_DEBUG", "================== QuizActivity onCreate STARTED ==================");
        System.out.println("================== QuizActivity onCreate STARTED ==================");

        super.onCreate(savedInstanceState);

        // 获取传递过来的题库ID
        Intent intent = getIntent();
        if (intent != null) {
            questionBankId = intent.getStringExtra("question_bank_id");
            android.util.Log.d("QuizActivity", "Received question_bank_id: " + questionBankId);
        }
        setContentView(R.layout.activity_quiz);

        android.util.Log.e("QuizActivity_DEBUG", "================== QuizActivity setContentView COMPLETED ==================");
        System.out.println("================== QuizActivity setContentView COMPLETED ==================");

        // 加载背景图片
        loadBackgroundImage();

        random = new Random();
        configManager = QuizConfigManager.getInstance(this);
        prizeConfigManager = QuizPrizeConfigManager.getInstance(this);
        voiceManager = VoiceManager.getInstance(this);
        voiceCommandManager = VoiceCommandManager.getInstance(this);

        initViews();
        initDigitalHuman();
        loadQuestions();
        setupListeners();
    }

    private void initViews() {
        tvQuestionNumber = findViewById(R.id.tv_question_number);
        tvQuestion = findViewById(R.id.tv_question);
        tvQuizTitle = findViewById(R.id.tv_quiz_title);  // 题库标题
        layoutQuestionContainer = findViewById(R.id.layout_question_container);  // 题目容器
        tvVoiceStatus = findViewById(R.id.tv_voice_status);
        btnOptionA = findViewById(R.id.btn_option_a);
        btnOptionB = findViewById(R.id.btn_option_b);
        btnOptionC = findViewById(R.id.btn_option_c);
        btnOptionD = findViewById(R.id.btn_option_d);
        btnNext = findViewById(R.id.btn_next);
        btnSubmit = findViewById(R.id.btn_submit);
        btnVoiceInput = findViewById(R.id.btn_voice_input);
        progressBar = findViewById(R.id.progress_bar);
        btnBack = findViewById(R.id.btn_back);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnNext.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                nextQuestion();
            }
        });

        btnSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                submitQuiz();
            }
        });

        // 语音输入按钮监听
        btnVoiceInput.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startVoiceRecognition();
            }
        });

        // 初始隐藏下一题和提交按钮
        btnNext.setVisibility(View.GONE);
        btnSubmit.setVisibility(View.GONE);

        // 根据配置显示语音按钮
        if (configManager.isVoiceEnabled() && voiceManager.isInitialized()) {
            btnVoiceInput.setVisibility(View.VISIBLE);
        }

        // 应用色彩风格
        applyColorTheme();
    }

    /**
     * 应用色彩风格到选项按钮和UI元素
     */
    private void applyColorTheme() {
        QuizConfigManager.ColorTheme theme = configManager.getColorTheme();
        int primaryColor = theme.getPrimaryColor();
        int darkColor = theme.getDarkColor();
        int textColor = theme.getTextColor();
        int backgroundColor = theme.getBackgroundColor();
        int overlayColor = theme.getOverlayColor(); // 获取底纹颜色（包含透明度）

        // 1. 设置题目编号为配置的文字颜色
        if (tvQuestionNumber != null) {
            tvQuestionNumber.setTextColor(textColor);
        }

        // 题库标题使用配置的文字颜色
        if (tvQuizTitle != null) {
            tvQuizTitle.setTextColor(textColor);
        }

        // 2. 题目容器：透明背景（去掉底纹）
        if (layoutQuestionContainer != null) {
            layoutQuestionContainer.setBackgroundColor(android.graphics.Color.TRANSPARENT);
        }
        // 题目文字颜色
        if (tvQuestion != null) {
            tvQuestion.setTextColor(textColor);
        }

        // 3. 应用颜色到选项按钮（使用底纹颜色作为背景，无边框）
        Button[] allButtons = {btnOptionA, btnOptionB, btnOptionC, btnOptionD};
        for (Button button : allButtons) {
            if (button != null && button.getVisibility() == android.view.View.VISIBLE) {
                android.graphics.drawable.GradientDrawable drawable = new android.graphics.drawable.GradientDrawable();
                drawable.setColor(overlayColor); // 使用底纹颜色
                drawable.setCornerRadius(28);
                button.setBackground(drawable);
                button.setTextColor(textColor); // 使用配置的文字颜色
            }
        }

        // 4. 应用颜色到操作按钮（使用主题色和配置的文字颜色）
        if (btnNext != null && btnNext.getVisibility() == View.VISIBLE) {
            btnNext.setBackgroundColor(primaryColor);
            btnNext.setTextColor(textColor);
        }
        if (btnSubmit != null && btnSubmit.getVisibility() == View.VISIBLE) {
            btnSubmit.setBackgroundColor(primaryColor);
            btnSubmit.setTextColor(textColor);
        }
        if (btnVoiceInput != null && btnVoiceInput.getVisibility() == View.VISIBLE) {
            btnVoiceInput.setBackgroundColor(primaryColor);
            btnVoiceInput.setTextColor(textColor);
        }

        // 5. 返回按钮使用配置的文字颜色
        if (btnBack != null) {
            btnBack.setTextColor(textColor);
        }

        // 6. 语音状态文字使用配置的文字颜色
        if (tvVoiceStatus != null) {
            tvVoiceStatus.setTextColor(textColor);
        }

        // 7. 进度条使用主题主色
        if (progressBar != null) {
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.LOLLIPOP) {
                progressBar.setProgressTintList(android.content.res.ColorStateList.valueOf(primaryColor));
            }
        }
    }

    /**
     * 初始化数字人
     */
    private void initDigitalHuman() {
        android.util.Log.e("QuizActivity_DEBUG", "================== initDigitalHuman CALLED ==================");
        System.out.println("================== initDigitalHuman CALLED ==================");

        digitalHumanView = findViewById(R.id.digital_human_view);
        android.util.Log.d("QuizActivity", "initDigitalHuman: digitalHumanView = " + digitalHumanView);
        System.out.println("initDigitalHuman: digitalHumanView = " + digitalHumanView);

        // 根据配置决定是否显示数字人
        com.jcoding.aiactivity.manager.ConfigManager globalConfigManager =
            com.jcoding.aiactivity.manager.ConfigManager.getInstance(this);

        boolean isEnabled = globalConfigManager.isDigitalHumanEnabledForModule("quiz");
        android.util.Log.d("QuizActivity", "isDigitalHumanEnabledForModule('quiz') = " + isEnabled);

        // 根据配置决定是否显示数字人
        if (isEnabled) {
            android.util.Log.e("QuizActivity_DEBUG", "================== DigitalHuman ENABLED ==================");
            System.out.println("================== DigitalHuman ENABLED ==================");

            digitalHumanManager = DigitalHumanManager.getInstance(this);
            digitalHumanView.setVisibility(View.VISIBLE);
            android.util.Log.d("QuizActivity", "DigitalHumanView set to VISIBLE (forced)");
            System.out.println("DigitalHumanView set to VISIBLE (forced)");

            // 设置模块ID为quiz，以便使用quiz的配置
            digitalHumanView.setModuleId("quiz");

            // 应用XY坐标位置（使用保存的位置和缩放）
            applyDigitalHumanPosition();

            // 加载数字人视频（使用视频组件而非GIF）
            // 从配置获取数字人ID，默认为项目ID
            String digitalHumanId = "JC2026012100001";  // 与DigitalHumanManager中的projectId一致
            android.util.Log.e("QuizActivity_DEBUG", "================== CALLING loadDigitalHuman: " + digitalHumanId + " ==================");
            System.out.println("================== CALLING loadDigitalHuman: " + digitalHumanId + " ==================");
            digitalHumanView.loadDigitalHuman(digitalHumanId);

            // 初始化控制按钮
            btnToggleDigitalHumanLock = findViewById(R.id.btn_toggle_digital_human_lock);
            if (btnToggleDigitalHumanLock != null) {
                // 设置按钮点击监听
                btnToggleDigitalHumanLock.setOnClickListener(v -> toggleDigitalHumanLock());

                android.util.Log.d("QuizActivity", "控制按钮已初始化");
            }

            // 延迟设置锁定状态，确保在restoreDigitalHumanState之后
            digitalHumanView.postDelayed(new Runnable() {
                @Override
                public void run() {
                    // 设置为锁定状态（默认禁用拖拽）
                    digitalHumanView.setDragAndScaleEnabled(false);

                    // 设置初始elevation为锁定状态（数字人在主布局之下）
                    digitalHumanView.setElevation(1);

                    android.util.Log.d("QuizActivity", "数字人初始状态: 锁定，elevation=1dp");
                }
            }, 200); // 延迟200ms，确保restoreDigitalHumanState已完成

            // 数字人欢迎动作
            digitalHumanManager.welcome(new DigitalHumanManager.DigitalHumanCallback() {
                @Override
                public void onSpeakStart(String gifPath) {
                    // 开始说话，显示说话视频
                    digitalHumanView.startTalking();
                }

                @Override
                public void onComplete() {
                    // 欢迎完成，停止说话，显示闭嘴视频
                    digitalHumanView.stopTalking();
                }

                @Override
                public void onError(String error) {
                    android.util.Log.e("QuizActivity", "Digital human error: " + error);
                }
            });
        } else {
            digitalHumanView.setVisibility(View.GONE);
        }
    }

    /**
     * 应用数字人XY坐标位置
     * 注意：这个方法已被弃用，现在位置和缩放由DigitalHumanView自动从配置恢复
     */
    private void applyDigitalHumanPosition() {
        android.util.Log.e("QuizActivity_DEBUG", "================== applyDigitalHumanPosition CALLED ==================");
        System.out.println("================== applyDigitalHumanPosition CALLED ==================");

        // 位置和缩放现在由DigitalHumanView.loadDigitalHuman()中的restoreDigitalHumanState()自动恢复
        // 不再需要在这里手动设置

        android.util.Log.d("QuizActivity", "Quiz模块数字人位置和缩放将从配置自动恢复");
        android.util.Log.e("QuizActivity_DEBUG", "================== applyDigitalHumanPosition COMPLETED (auto-restore) ==================");
        System.out.println("================== applyDigitalHumanPosition COMPLETED (auto-restore) ==================");
    }

    /**
     * 切换数字人锁定/解锁状态
     */
    private void toggleDigitalHumanLock() {
        if (digitalHumanView == null) {
            android.util.Log.w("QuizActivity", "digitalHumanView为null，无法切换锁定状态");
            return;
        }

        boolean currentState = digitalHumanView.isDragAndScaleEnabled();
        boolean newState = !currentState;

        android.util.Log.d("QuizActivity", "切换数字人锁定状态: " + (currentState ? "解锁→锁定" : "锁定→解锁"));

        // 设置拖拽/缩放状态
        digitalHumanView.setDragAndScaleEnabled(newState);

        // 动态调整elevation
        if (digitalHumanView != null) {
            if (newState) {
                // 解锁状态：数字人可见，可以拖拽
                digitalHumanView.setElevation(5);
                btnToggleDigitalHumanLock.setText("🔓");
                Toast.makeText(this, "数字人已解锁\n可拖拽调整位置和大小", Toast.LENGTH_SHORT).show();
                android.util.Log.d("QuizActivity", "数字人解锁：elevation=5dp");
            } else {
                // 锁定状态：数字人置于后面，不影响功能点击
                digitalHumanView.setElevation(1);
                btnToggleDigitalHumanLock.setText("🔒");
                Toast.makeText(this, "数字人已锁定\n位置已固定", Toast.LENGTH_SHORT).show();
                android.util.Log.d("QuizActivity", "数字人锁定：elevation=1dp");
            }

            android.util.Log.d("QuizActivity", "数字人当前位置: X=" + digitalHumanView.getX() + ", Y=" + digitalHumanView.getY());
        }
    }

    private void setupListeners() {
        // 选项按钮监听
        btnOptionA.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectAnswer(0);
            }
        });

        btnOptionB.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectAnswer(1);
            }
        });

        btnOptionC.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectAnswer(2);
            }
        });

        btnOptionD.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectAnswer(3);
            }
        });
    }

    /**
     * 加载题目（支持出题顺序控制）
     */
    private void loadQuestions() {
        // 重置恭喜弹窗标志
        hasShownCongratulations = false;

        android.util.Log.d("QuizActivity", "loadQuestions: Starting");
        // 获取题库配置
        com.google.gson.JsonObject questionConfig = configManager.getQuestionConfig();
        android.util.Log.d("QuizActivity", "questionConfig: " + (questionConfig != null ? "loaded" : "null"));

        if (questionConfig == null || !questionConfig.has("round")) {
            showToast("题库配置加载失败，使用默认配置");
            loadQuestionsFallback();
            return;
        }

        // 直接加载题库，不显示选择题库弹框
        loadQuestionBankFromConfig(questionConfig);
    }

    /**
     * 显示题库选择对话框 - 使用自定义布局，大字体和带背景色的选项
     */
    private void showQuestionBankSelector(com.google.gson.JsonObject questionConfig, com.google.gson.JsonArray catalogArray) {
        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);

        // 创建自定义布局
        android.view.LayoutInflater inflater = getLayoutInflater();
        android.view.View dialogView = inflater.inflate(com.jcoding.aiactivity.R.layout.dialog_question_bank_selector, null);
        builder.setView(dialogView);

        // 获取题库名称数组
        final String[] bankNames = new String[catalogArray.size()];
        for (int i = 0; i < catalogArray.size(); i++) {
            com.google.gson.JsonObject catalogItem = catalogArray.get(i).getAsJsonObject();
            bankNames[i] = catalogItem.has("catalog_name") ?
                catalogItem.get("catalog_name").getAsString() : "题库" + (i + 1);
        }

        // 获取选项容器
        android.widget.LinearLayout optionsContainer = dialogView.findViewById(com.jcoding.aiactivity.R.id.ll_bank_options);

        // 创建对话框的引用数组，用于在onClick中访问
        final android.app.AlertDialog[] dialogHolder = new android.app.AlertDialog[1];

        // 为每个题库创建一个按钮
        for (int i = 0; i < bankNames.length; i++) {
            final int index = i;
            Button bankButton = new Button(this);
            bankButton.setText(bankNames[i]);
            bankButton.setTextSize(20); // 大字体
            bankButton.setGravity(android.view.Gravity.CENTER);
            bankButton.setPadding(24, 32, 24, 32); // 更大的内边距
            bankButton.setTextColor(0xFF000000); // 黑色文字
            bankButton.setBackground(getResources().getDrawable(com.jcoding.aiactivity.R.drawable.bg_bank_option_selector));

            // 设置点击事件
            bankButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    com.google.gson.JsonObject selectedCatalog = catalogArray.get(index).getAsJsonObject();
                    loadSelectedQuestionBank(selectedCatalog);
                    if (dialogHolder[0] != null) {
                        dialogHolder[0].dismiss();
                    }
                }
            });

            // 添加到容器
            optionsContainer.addView(bankButton);
        }

        // 创建对话框
        dialogHolder[0] = builder.create();
        dialogHolder[0].setCancelable(false);
        dialogHolder[0].show();
    }

    /**
     * 加载选中的题库
     */
    private void loadSelectedQuestionBank(com.google.gson.JsonObject catalogItem) {
        try {
            String file = catalogItem.get("file").getAsString();
            String bankName = catalogItem.has("catalog_name") ? catalogItem.get("catalog_name").getAsString() : "默认题库";
            String bankId = catalogItem.has("qid") ? catalogItem.get("qid").getAsString() : "default";
            int status = catalogItem.has("status") ? catalogItem.get("status").getAsInt() : 1;

            android.util.Log.d("QuizActivity", "Loading selected question file: question/" + file);

            String content = com.jcoding.aiactivity.utils.FileUtils.readAssetFile(this, "question/" + file);

            if (content != null) {
                // 解析题库
                try {
                    com.google.gson.Gson gson = new com.google.gson.Gson();
                    questionBank = gson.fromJson(content, com.jcoding.aiactivity.entity.QuestionBank.class);
                    if (questionBank.getQuestionCount() == 0) {
                        questionBank = QuizConfigManager.getInstance(this).parseLegacyQuestionBank(content, bankId, bankName, file, status);
                    }
                } catch (Exception e) {
                    questionBank = QuizConfigManager.getInstance(this).parseLegacyQuestionBank(content, bankId, bankName, file, status);
                }

                if (questionBank != null && questionBank.getQuestionCount() > 0) {
                    // 加载题目
                    loadQuestionsFromBank();
                } else {
                    showToast("题库加载失败");
                    finish();
                }
            } else {
                showToast("题库文件不存在: " + file);
                finish();
            }
        } catch (Exception e) {
            android.util.Log.e("QuizActivity", "Error loading selected question bank", e);
            showToast("题库加载失败");
            finish();
        }
    }

    /**
     * 从配置加载题库（原有逻辑）
     */
    private void loadQuestionBankFromConfig(com.google.gson.JsonObject questionConfig) {
        // 读取round配置
        com.google.gson.JsonObject roundConfig = questionConfig.getAsJsonObject("round");
        int totalQty = roundConfig.has("qty") ? roundConfig.get("qty").getAsInt() : 10;
        int choiceQty = roundConfig.has("choice") ? roundConfig.get("choice").getAsInt() : 6;
        int judgementQty = roundConfig.has("judgement") ? roundConfig.get("judgement").getAsInt() : 4;

        android.util.Log.d("QuizActivity", "Round config: total=" + totalQty + ", choice=" + choiceQty + ", judgement=" + judgementQty);

        // 根据传递的题库ID获取题库，如果没有传递则使用默认题库
        android.util.Log.d("QuizActivity", "Loading question bank with ID: " + questionBankId);
        if (questionBankId != null && !questionBankId.isEmpty()) {
            questionBank = configManager.getQuestionBankById(questionBankId);
        } else {
            android.util.Log.d("QuizActivity", "No question_bank_id provided, using default");
            questionBank = configManager.getDefaultQuestionBank();
        }

        android.util.Log.d("QuizActivity", "questionBank returned: " + (questionBank != null ? questionBank.getBankName() : "null") + ", questions: " + (questionBank != null ? questionBank.getQuestionCount() : "N/A"));

        if (questionBank == null || questionBank.getQuestionCount() == 0) {
            showToast("题库加载失败");
            android.util.Log.e("QuizActivity", "Question bank is null or empty!");
            finish();
            return;
        }

        loadQuestionsFromBank();
    }

    /**
     * 从已加载的题库中抽取题目
     */
    private void loadQuestionsFromBank() {
        // 从配置管理器读取用户设置的题目数量
        int choiceQty = configManager.getRoundChoice();
        int judgementQty = configManager.getRoundJudgement();

        List<Question> allQuestions = questionBank.getQuestions();
        List<Question> choiceQuestions = new ArrayList<>();
        List<Question> judgementQuestions = new ArrayList<>();

        for (Question q : allQuestions) {
            if (q.isChoice()) {
                choiceQuestions.add(q);
            } else if (q.isJudgement()) {
                judgementQuestions.add(q);
            }
        }

        // 检查题目数量是否足够
        if (choiceQuestions.size() < choiceQty) {
            showToast("选择题数量不足：需要" + choiceQty + "题，实际只有" + choiceQuestions.size() + "题");
            // 自动调整数量为实际可用数量
            choiceQty = choiceQuestions.size();
        }

        if (judgementQuestions.size() < judgementQty) {
            showToast("判断题数量不足：需要" + judgementQty + "题，实际只有" + judgementQuestions.size() + "题");
            // 自动调整数量为实际可用数量
            judgementQty = judgementQuestions.size();
        }

        if (choiceQty == 0 && judgementQty == 0) {
            showToast("题库中没有可用题目");
            finish();
            return;
        }

        // 随机打乱题目
        Collections.shuffle(choiceQuestions);
        Collections.shuffle(judgementQuestions);

        // 按配置数量抽取题目
        questionList = new ArrayList<>();
        if (choiceQty > 0) {
            questionList.addAll(choiceQuestions.subList(0, choiceQty));
        }
        if (judgementQty > 0) {
            questionList.addAll(judgementQuestions.subList(0, judgementQty));
        }

        // 根据出题顺序设置排列题目
        QuizConfigManager.QuestionOrder order = configManager.getQuestionOrder();
        switch (order) {
            case MIXED:
                // 混合随机：再次打乱题目顺序
                Collections.shuffle(questionList);
                break;
            case CHOICE_FIRST:
                // 先选择题：已经按顺序添加了，不需要额外处理
                break;
            case JUDGEMENT_FIRST:
                // 先判断题：重新排序，判断题在前
                List<Question> reorderedList = new ArrayList<>();
                if (judgementQty > 0) {
                    reorderedList.addAll(judgementQuestions.subList(0, judgementQty));
                }
                if (choiceQty > 0) {
                    reorderedList.addAll(choiceQuestions.subList(0, choiceQty));
                }
                questionList = reorderedList;
                break;
        }

        // 初始化用户答案数组
        userAnswers = new int[questionList.size()];
        for (int i = 0; i < userAnswers.length; i++) {
            userAnswers[i] = -1;  // -1表示未作答
        }

        displayQuestion();
    }

    /**
     * 加载题目（降级方案，配置读取失败时使用）
     */
    private void loadQuestionsFallback() {
        // 获取默认题库
        questionBank = configManager.getDefaultQuestionBank();

        if (questionBank == null || questionBank.getQuestionCount() == 0) {
            showToast("题库加载失败");
            finish();
            return;
        }

        // 获取题目列表并打乱顺序
        questionList = new ArrayList<>(questionBank.getQuestions());
        Collections.shuffle(questionList);

        // 限制题目数量（默认10题）
        int maxQuestions = Math.min(questionList.size(), 10);
        questionList = questionList.subList(0, maxQuestions);

        userAnswers = new int[questionList.size()];
        for (int i = 0; i < userAnswers.length; i++) {
            userAnswers[i] = -1;  // -1表示未作答
        }

        displayQuestion();
    }

    /**
     * 显示当前题目
     */
    private void displayQuestion() {
        android.util.Log.d("QuizActivity", "========== displayQuestion START ==========");
        android.util.Log.d("QuizActivity", "currentQuestionIndex: " + currentQuestionIndex);
        android.util.Log.d("QuizActivity", "questionList.size(): " + (questionList != null ? questionList.size() : "null"));

        if (currentQuestionIndex >= questionList.size()) {
            // 所有题目已完成
            showResult();
            return;
        }

        Question question = questionList.get(currentQuestionIndex);
        android.util.Log.d("QuizActivity", "Current question: " + (question != null ? question.getContent() : "null"));

        // 设置题库标题
        if (questionBank != null && tvQuizTitle != null) {
            String bankName = questionBank.getBankName();
            tvQuizTitle.setText("知识答题." + bankName);
            android.util.Log.d("QuizActivity", "Set title to: 知识答题." + bankName);
        }

        // 更新题目编号
        tvQuestionNumber.setText(String.format("第 %d / %d 题",
                currentQuestionIndex + 1, questionList.size()));

        // 显示题目内容
        android.util.Log.d("QuizActivity", "Setting question text: " + (question != null ? question.getContent() : "null"));
        tvQuestion.setText(question.getContent());
        android.util.Log.d("QuizActivity", "Question text set successfully");

        // 显示选项
        android.util.Log.d("QuizActivity", "Question isChoice: " + question.isChoice() + ", isJudgement: " + question.isJudgement());
        if (question.isChoice()) {
            // 选择题 - 根据实际选项数量显示按钮
            String[] options = question.getOptions();
            int optionCount = options != null ? options.length : 0;
            android.util.Log.d("QuizActivity", "Choice question with " + optionCount + " options");

            // 至少显示2个选项按钮（A和B）
            btnOptionA.setText("A. " + (optionCount > 0 ? options[0] : ""));
            btnOptionB.setText("B. " + (optionCount > 1 ? options[1] : ""));
            android.util.Log.d("QuizActivity", "Set option A: " + (optionCount > 0 ? options[0] : "empty"));
            android.util.Log.d("QuizActivity", "Set option B: " + (optionCount > 1 ? options[1] : "empty"));

            // 根据选项数量决定是否显示C和D按钮
            if (optionCount >= 3) {
                btnOptionC.setText("C. " + options[2]);
                btnOptionC.setVisibility(View.VISIBLE);
            } else {
                btnOptionC.setVisibility(View.GONE);
            }

            if (optionCount >= 4) {
                btnOptionD.setText("D. " + options[3]);
                btnOptionD.setVisibility(View.VISIBLE);
            } else {
                btnOptionD.setVisibility(View.GONE);
            }
        } else if (question.isJudgement()) {
            // 判断题
            btnOptionA.setText("正确");
            btnOptionB.setText("错误");
            btnOptionC.setVisibility(View.GONE);
            btnOptionD.setVisibility(View.GONE);
        }

        // 重置选项状态
        resetOptionButtons();

        // 隐藏下一题和提交按钮
        btnNext.setVisibility(View.GONE);
        btnSubmit.setVisibility(View.GONE);

        // 如果已作答，恢复选择
        if (userAnswers[currentQuestionIndex] != -1) {
            highlightSelectedOption(userAnswers[currentQuestionIndex]);
            showNextButton();
        } else {
            // 未作答，语音播报题目和数字人播报
            if (configManager.isVoiceEnabled()) {
                speakQuestion();
            }

            // 数字人播报题目（如果启用）
            if (digitalHumanManager != null && digitalHumanManager.isEnabled() && isVoiceEnabledForModule()) {
                announceQuestionWithDigitalHuman(question);
            }
        }
    }

    /**
     * 数字人播报题目
     */
    private void announceQuestionWithDigitalHuman(Question question) {
        StringBuilder textToSpeak = new StringBuilder(question.getContent());

        // 如果是选择题，播报选项
        if (question.isChoice() && question.getOptions() != null) {
            String[] options = question.getOptions();
            textToSpeak.append("。A选项，").append(options[0]);
            textToSpeak.append("。B选项，").append(options[1]);
            if (options.length > 2) {
                textToSpeak.append("。C选项，").append(options[2]);
            }
            if (options.length > 3) {
                textToSpeak.append("。D选项，").append(options[3]);
            }
        }

        digitalHumanManager.announceQuestion(
            question.getContent(),
            question.isChoice() ? question.getOptions() : null,
            new DigitalHumanManager.DigitalHumanCallback() {
                @Override
                public void onSpeakStart(String gifPath) {
                    // 开始说话，显示说话视频
                    if (digitalHumanView != null) {
                        digitalHumanView.startTalking();
                    }
                }

                @Override
                public void onComplete() {
                    // 播报完成，停止说话，显示闭嘴视频
                    if (digitalHumanView != null) {
                        digitalHumanView.stopTalking();
                    }
                }

                @Override
                public void onError(String error) {
                    android.util.Log.e("QuizActivity", "Digital human announce error: " + error);
                }
            }
        );
    }

    /**
     * 语音播报当前题目
     */
    private void speakQuestion() {
        android.util.Log.i("QuizActivity", "speakQuestion() called");

        boolean voiceEnabled = configManager.isVoiceEnabled();
        boolean voiceManagerInitialized = voiceManager.isInitialized();

        android.util.Log.i("QuizActivity", "Voice enabled: " + voiceEnabled + ", VoiceManager initialized: " + voiceManagerInitialized);

        if (!voiceEnabled || !voiceManagerInitialized) {
            if (!voiceEnabled) {
                android.util.Log.w("QuizActivity", "Voice is disabled in settings");
            }
            if (!voiceManagerInitialized) {
                android.util.Log.w("QuizActivity", "VoiceManager is not initialized");
            }
            return;
        }

        Question question = questionList.get(currentQuestionIndex);
        String textToSpeak = question.getContent();

        // 如果是选择题，播报选项
        if (question.isChoice() && question.getOptions() != null) {
            String[] options = question.getOptions();
            textToSpeak += "。A选项，" + options[0] +
                    "。B选项，" + options[1];
            if (options.length > 2) {
                textToSpeak += "。C选项，" + options[2];
            }
            if (options.length > 3) {
                textToSpeak += "。D选项，" + options[3];
            }
        }

        android.util.Log.i("QuizActivity", "Speaking text: " + textToSpeak);

        isSpeakingQuestion = true;
        showVoiceStatus("正在播报题目...");

        voiceManager.speakText(textToSpeak, new VoiceManager.VoiceSynthesisCallback() {
            @Override
            public void onSpeakStart() {
                android.util.Log.i("QuizActivity", "onSpeakStart() called");
            }

            @Override
            public void onSpeakPaused() {
            }

            @Override
            public void onSpeakResumed() {
            }

            @Override
            public void onSpeakComplete() {
                android.util.Log.i("QuizActivity", "onSpeakComplete() called");
                isSpeakingQuestion = false;
                hideVoiceStatus();
            }

            @Override
            public void onError(String error) {
                android.util.Log.e("QuizActivity", "onError() called: " + error);
                isSpeakingQuestion = false;
                hideVoiceStatus();
                showToast("语音播报失败: " + error);
            }
        });
    }

    /**
     * 显示语音状态
     */
    private void showVoiceStatus(String status) {
        tvVoiceStatus.setText(status);
        tvVoiceStatus.setVisibility(View.VISIBLE);
    }

    /**
     * 隐藏语音状态
     */
    private void hideVoiceStatus() {
        tvVoiceStatus.postDelayed(new Runnable() {
            @Override
            public void run() {
                tvVoiceStatus.setVisibility(View.GONE);
            }
        }, 2000);
    }

    /**
     * 检查quiz模块的语音是否启用
     */
    private boolean isVoiceEnabledForModule() {
        // 检查quiz模块的语音播报是否启用
        // 注意：这里使用"quiz"作为模块ID，需要与ConfigManager中的设置一致
        return configManager.isDigitalHumanEnabledForModule("quiz");
    }

    /**
     * 停止语音播报
     */
    private void stopSpeaking() {
        if (voiceManager.isSpeaking()) {
            voiceManager.stopSpeaking();
            isSpeakingQuestion = false;
            hideVoiceStatus();
        }
    }

    /**
     * 选择答案
     */
    private void selectAnswer(int answerIndex) {
        // 如果正在播报题目，停止播报
        if (isSpeakingQuestion) {
            stopSpeaking();
        }

        // 记录答案
        userAnswers[currentQuestionIndex] = answerIndex;
        highlightSelectedOption(answerIndex);

        // 判断当前答案是否正确
        Question currentQuestion = questionList.get(currentQuestionIndex);
        boolean isCorrect = (answerIndex == currentQuestion.getCorrectAnswer());

        // 显示正确/错误的视觉标记和屏幕提示
        showAnswerFeedback(isCorrect, answerIndex, currentQuestion.getCorrectAnswer());

        // 数字人播报正确/错误
        announceAnswerResult(isCorrect);

        // 如果答对了，实时更新答对题数
        if (isCorrect) {
            // 计算当前的答对题数
            int currentCorrectCount = 0;
            for (int i = 0; i <= currentQuestionIndex; i++) {
                if (userAnswers[i] == questionList.get(i).getCorrectAnswer()) {
                    currentCorrectCount++;
                }
            }

            // 检查是否达到奖励门槛
            checkAndShowPrizeForCorrectCount(currentCorrectCount);
        }

        // 自动提交模式
        if (configManager.isAutoSubmit()) {
            // 延迟1.5秒后自动进入下一题，让用户看到反馈
            new Handler().postDelayed(new Runnable() {
                @Override
                public void run() {
                    // 清除视觉标记
                    clearAnswerFeedback();

                    // 自动进入下一题
                    if (currentQuestionIndex < questionList.size() - 1) {
                        nextQuestion();
                    } else {
                        // 最后一题，直接提交
                        submitQuiz();
                    }
                }
            }, 1500);
        } else {
            // 手动提交模式，显示按钮
            showNextButton();
        }
    }

    /**
     * 显示答案反馈（视觉标记）
     * @param isCorrect 是否回答正确
     * @param selectedAnswer 用户选择的答案
     * @param correctAnswer 正确答案
     */
    private void showAnswerFeedback(boolean isCorrect, int selectedAnswer, int correctAnswer) {
        Button[] optionButtons = {btnOptionA, btnOptionB, btnOptionC, btnOptionD};

        if (isCorrect) {
            // 回答正确：在选中选项上显示勾
            Button selectedButton = optionButtons[selectedAnswer];
            String originalText = selectedButton.getText().toString();
            selectedButton.setText("✓ " + originalText);
            selectedButton.setBackgroundColor(Color.parseColor("#4CAF50")); // 绿色背景

            // 显示屏幕提示
            showToast("✓ 回答正确！");

            android.util.Log.d("QuizActivity", "回答正确，选项" + selectedAnswer);
        } else {
            // 回答错误：在选中选项上显示叉，并在正确答案上显示勾
            Button selectedButton = optionButtons[selectedAnswer];
            Button correctButton = optionButtons[correctAnswer];

            // 在错误答案上显示叉
            String selectedOriginalText = selectedButton.getText().toString();
            selectedButton.setText("✗ " + selectedOriginalText);
            selectedButton.setBackgroundColor(Color.parseColor("#F44336")); // 红色背景

            // 在正确答案上显示勾
            String correctOriginalText = correctButton.getText().toString();
            correctButton.setText("✓ " + correctOriginalText);
            correctButton.setBackgroundColor(Color.parseColor("#4CAF50")); // 绿色背景

            // 显示屏幕提示
            showToast("✗ 回答错误！正确答案: " + (char)('A' + correctAnswer));

            android.util.Log.d("QuizActivity", "回答错误，选项" + selectedAnswer + "，正确答案" + correctAnswer);
        }
    }

    /**
     * 清除答案反馈（恢复原始状态）
     */
    private void clearAnswerFeedback() {
        Button[] optionButtons = {btnOptionA, btnOptionB, btnOptionC, btnOptionD};
        Question currentQuestion = questionList.get(currentQuestionIndex);

        // 恢复选项按钮的文本和背景色
        String[] options = currentQuestion.getOptions();
        QuizConfigManager.ColorTheme theme = configManager.getColorTheme();

        for (int i = 0; i < options.length && i < 4; i++) {
            Button button = optionButtons[i];
            String prefix = (char)('A' + i) + ". ";
            button.setText(prefix + options[i]);
            button.setBackgroundColor(theme.getPrimaryColor());
        }

        android.util.Log.d("QuizActivity", "清除答案反馈");
    }

    /**
     * 数字人播报答案结果
     * @param isCorrect 是否回答正确
     */
    private void announceAnswerResult(boolean isCorrect) {
        if (!configManager.isDigitalHumanEnabledForModule("quiz")) {
            android.util.Log.d("QuizActivity", "数字人未启用，跳过播报");
            return;
        }

        String message = isCorrect ? "回答正确" : "回答错误";
        android.util.Log.d("QuizActivity", "数字人播报: " + message);

        if (digitalHumanView != null && digitalHumanManager != null) {
            // 开始说话动画
            digitalHumanView.startTalking();

            // 数字人播报
            digitalHumanManager.speak(message, new DigitalHumanManager.DigitalHumanCallback() {
                @Override
                public void onSpeakStart(String gifPath) {
                    android.util.Log.d("QuizActivity", "数字人开始播报: " + message);
                }

                @Override
                public void onComplete() {
                    android.util.Log.d("QuizActivity", "数字人播报完成: " + message);
                    // 停止说话动画
                    if (digitalHumanView != null) {
                        digitalHumanView.stopTalking();
                    }
                }

                @Override
                public void onError(String error) {
                    android.util.Log.e("QuizActivity", "数字人播报错误: " + error);
                    // 出错时也要停止说话动画
                    if (digitalHumanView != null) {
                        digitalHumanView.stopTalking();
                    }
                }
            });
        }
    }

    /**
     * 检查答对题数是否达到奖励门槛并显示恭喜
     */
    private void checkAndShowPrizeForCorrectCount(int currentCorrectCount) {
        // 检查是否启用奖品功能
        if (!prizeConfigManager.isPrizeEnabled()) {
            return;
        }

        // 检查是否达到奖励门槛
        int prizeThreshold = prizeConfigManager.getPrizeThreshold();
        if (prizeThreshold <= 0 || currentCorrectCount < prizeThreshold) {
            return;
        }

        // 获取奖品信息
        String prizeImageUrl = prizeConfigManager.getPrizeImageUrl(currentCorrectCount);
        if (prizeImageUrl == null || prizeImageUrl.isEmpty()) {
            return;
        }

        // 只显示一次：检查是否已经显示过恭喜
        if (hasShownCongratulations) {
            return;
        }
        hasShownCongratulations = true;

        // 显示恭喜弹窗（不阻塞答题流程）
        showPrizeCongratulationsDialog(prizeImageUrl, currentCorrectCount);
    }

    /**
     * 高亮选中的选项
     */
    private void highlightSelectedOption(int answerIndex) {
        resetOptionButtons();

        // 获取当前主题配置
        QuizConfigManager.ColorTheme theme = configManager.getColorTheme();
        int primaryColor = theme.getPrimaryColor();

        // 设置选中的选项
        Button selectedButton = null;
        switch (answerIndex) {
            case 0:
                selectedButton = btnOptionA;
                break;
            case 1:
                selectedButton = btnOptionB;
                break;
            case 2:
                selectedButton = btnOptionC;
                break;
            case 3:
                selectedButton = btnOptionD;
                break;
        }

        if (selectedButton != null) {
            selectedButton.setSelected(true);
            // 创建高亮背景：使用主题主色（80%透明度），无边框
            int primaryWithAlpha = (primaryColor & 0x00FFFFFF) | 0xCC000000;
            android.graphics.drawable.GradientDrawable highlightBg = new android.graphics.drawable.GradientDrawable();
            highlightBg.setColor(primaryWithAlpha);
            highlightBg.setCornerRadius(28);
            selectedButton.setBackground(highlightBg);

            // 使用配置的文字颜色和粗体
            int textColor = theme.getTextColor();
            selectedButton.setTextColor(textColor);
            selectedButton.setTypeface(null, android.graphics.Typeface.BOLD);
            selectedButton.setAlpha(1.0f);
        }

        // 其他选项降低透明度，使用配置的文字颜色
        int textColor = theme.getTextColor();
        Button[] allButtons = {btnOptionA, btnOptionB, btnOptionC, btnOptionD};
        for (int i = 0; i < allButtons.length; i++) {
            if (i != answerIndex && allButtons[i].getVisibility() == android.view.View.VISIBLE) {
                allButtons[i].setAlpha(0.5f);
                allButtons[i].setTextColor(textColor); // 使用配置的文字颜色
                allButtons[i].setTypeface(null, android.graphics.Typeface.NORMAL);
                // 保持原有背景，不重置
            }
        }
    }

    /**
     * 重置选项按钮状态
     */
    private void resetOptionButtons() {
        btnOptionA.setSelected(false);
        btnOptionB.setSelected(false);
        btnOptionC.setSelected(false);
        btnOptionD.setSelected(false);

        // 重置所有按钮的视觉状态并重新应用主题
        Button[] allButtons = {btnOptionA, btnOptionB, btnOptionC, btnOptionD};
        for (Button button : allButtons) {
            button.setAlpha(1.0f);
            button.setTypeface(null, android.graphics.Typeface.NORMAL);
        }

        // 重新应用主题色彩
        applyColorTheme();
    }

    /**
     * 显示下一题按钮
     */
    private void showNextButton() {
        android.util.Log.d("QuizActivity_DEBUG", "========== showNextButton CALLED ==========");
        android.util.Log.d("QuizActivity_DEBUG", "当前题目索引: " + currentQuestionIndex);
        android.util.Log.d("QuizActivity_DEBUG", "题目总数: " + questionList.size());
        android.util.Log.d("QuizActivity_DEBUG", "btnNext null? " + (btnNext == null));
        android.util.Log.d("QuizActivity_DEBUG", "btnSubmit null? " + (btnSubmit == null));
        android.util.Log.d("QuizActivity_DEBUG", "自动提交模式? " + configManager.isAutoSubmit());

        if (currentQuestionIndex < questionList.size() - 1) {
            android.util.Log.d("QuizActivity_DEBUG", "显示下一题按钮");
            btnNext.setVisibility(View.VISIBLE);
            android.util.Log.d("QuizActivity_DEBUG", "btnNext visibility after set: " + btnNext.getVisibility());
        } else {
            android.util.Log.d("QuizActivity_DEBUG", "显示提交答案按钮");
            btnSubmit.setVisibility(View.VISIBLE);
            android.util.Log.d("QuizActivity_DEBUG", "btnSubmit visibility after set: " + btnSubmit.getVisibility());
        }
    }

    /**
     * 下一题
     */
    private void nextQuestion() {
        // 清除答案反馈
        clearAnswerFeedback();

        currentQuestionIndex++;
        displayQuestion();
    }

    /**
     * 提交答题
     */
    private void submitQuiz() {
        // 计算得分
        calculateScore();

        // 检查是否达到奖励门槛并显示恭喜弹窗
        if (!checkAndShowPrizeCongratulations()) {
            // 如果没有显示恭喜弹窗，直接显示结果
            showResult();
        }
    }

    /**
     * 检查并显示奖励恭喜弹窗
     * @return true=显示了弹窗，false=未显示
     */
    private boolean checkAndShowPrizeCongratulations() {
        // 检查是否启用奖品功能
        if (!prizeConfigManager.isPrizeEnabled()) {
            return false;
        }

        // 检查是否达到奖励门槛
        int prizeThreshold = prizeConfigManager.getPrizeThreshold();
        if (prizeThreshold <= 0 || correctCount < prizeThreshold) {
            return false;
        }

        // 获取奖品信息
        String prizeImageUrl = prizeConfigManager.getPrizeImageUrl(correctCount);
        if (prizeImageUrl == null || prizeImageUrl.isEmpty()) {
            return false;
        }

        // 显示恭喜弹窗
        showPrizeCongratulationsDialog(prizeImageUrl, correctCount);
        return true;
    }

    /**
     * 显示恭喜中奖弹窗
     */
    private void showPrizeCongratulationsDialog(String prizeImageUrl, final int correctCount) {
        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
        builder.setTitle(""); // 无标题

        // 创建自定义布局
        android.view.LayoutInflater inflater = getLayoutInflater();
        android.view.View dialogView = inflater.inflate(R.layout.dialog_prize_congratulations, null);
        builder.setView(dialogView);

        // 设置奖品图片
        android.widget.ImageView ivPrize = dialogView.findViewById(R.id.iv_prize_image);
        android.widget.TextView tvCongratulations = dialogView.findViewById(R.id.tv_congratulations);
        android.widget.TextView tvCorrectCount = dialogView.findViewById(R.id.tv_correct_count);
        android.widget.Button btnClose = dialogView.findViewById(R.id.btn_close);

        // 设置恭喜文字
        tvCorrectCount.setText("恭喜您答对 " + correctCount + " 题，获得奖品！");

        // 加载奖品图片
        if (prizeImageUrl != null && prizeImageUrl.startsWith("file:///android_asset/")) {
            // 从assets加载图片
            String assetPath = prizeImageUrl.substring("file:///android_asset/".length());
            try {
                android.graphics.Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(getAssets().open(assetPath));
                if (bitmap != null) {
                    ivPrize.setImageBitmap(bitmap);
                } else {
                    ivPrize.setImageResource(android.R.drawable.ic_menu_report_image);
                }
            } catch (Exception e) {
                android.util.Log.e("QuizActivity", "加载assets图片失败: " + e.getMessage());
                ivPrize.setImageResource(android.R.drawable.ic_menu_report_image);
            }
        } else {
            // 使用Glide加载网络图片或其他路径
            com.bumptech.glide.Glide.with(this)
                    .load(prizeImageUrl)
                    .placeholder(android.R.drawable.ic_menu_info_details)
                    .error(android.R.drawable.ic_menu_report_image)
                    .into(ivPrize);
        }

        // 创建并显示对话框
        final android.app.AlertDialog dialog = builder.create();

        // 关闭按钮
        btnClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                // 先计算分数，再显示结果
                calculateScore();
                QuizActivity.this.showResult();
            }
        });

        // 对话框不可取消（必须点击按钮关闭）
        dialog.setCancelable(false);
        dialog.show();
    }

    /**
     * 计算得分
     */
    private void calculateScore() {
        correctCount = 0;

        android.util.Log.d("QuizActivity", "=== calculateScore 开始 ===");
        android.util.Log.d("QuizActivity", "题目总数: " + questionList.size());
        android.util.Log.d("QuizActivity", "userAnswers长度: " + (userAnswers != null ? userAnswers.length : "null"));

        for (int i = 0; i < questionList.size(); i++) {
            Question question = questionList.get(i);
            int userAnswer = userAnswers[i];
            int correctAnswer = question.getCorrectAnswer();

            android.util.Log.d("QuizActivity", "题目" + i + ": userAnswer=" + userAnswer + ", correctAnswer=" + correctAnswer);

            if (userAnswer == correctAnswer) {
                correctCount++;
                android.util.Log.d("QuizActivity", "题目" + i + ": 答对 ✓");
            } else if (userAnswer == -1) {
                android.util.Log.d("QuizActivity", "题目" + i + ": 未作答");
            } else {
                android.util.Log.d("QuizActivity", "题目" + i + ": 答错 ✗");
            }
        }

        android.util.Log.d("QuizActivity", "=== calculateScore 结束, 正确数: " + correctCount + " ===");
    }

    /**
     * 显示结果
     * 检查奖品配置，如果启用奖品功能则进行相应处理
     */
    private void showResult() {
        // 确保分数已计算
        calculateScore();

        // 检查是否启用奖品功能
        boolean prizeEnabled = prizeConfigManager.isPrizeEnabled();

        Intent intent = new Intent(this, QuizResultActivity.class);
        intent.putExtra("total_questions", questionList.size());
        intent.putExtra("correct_count", correctCount);
        intent.putExtra("prize_enabled", prizeEnabled);

        // 如果启用了奖品功能
        if (prizeEnabled) {
            // 检查是否需要登录
            boolean requireLogin = prizeConfigManager.isRequireLogin();
            intent.putExtra("require_login", requireLogin);

            // 检查是否推送到内场秀
            boolean pushToInner = prizeConfigManager.isPushToInner();
            intent.putExtra("push_to_inner", pushToInner);

            // 如果答对的题目数达到获奖标准
            if (correctCount >= prizeConfigManager.getPrizeThreshold()) {
                String prizeImageUrl = prizeConfigManager.getPrizeImageUrl(correctCount);
                if (prizeImageUrl != null && !prizeImageUrl.isEmpty()) {
                    intent.putExtra("prize_image_url", prizeImageUrl);
                    intent.putExtra("won_prize", true);
                }

                // 如果启用推送到内场秀
                if (pushToInner) {
                    pushQuizResultToInner();
                }
            }
        }

        // 使用startActivityForResult以便返回时重新加载题库
        startActivityForResult(intent, 1001);
    }

    /**
     * 从结果页返回后重新初始化题库
     */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, android.content.Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 1001) {
            // 重新加载配置
            configManager = QuizConfigManager.getInstance(this);
            prizeConfigManager = QuizPrizeConfigManager.getInstance(this);

            // 重新加载背景图片
            loadBackgroundImage();

            // 重置状态，重新加载题库选择
            currentQuestionIndex = 0;
            correctCount = 0;
            questionList = null;
            userAnswers = null;
            loadQuestions();

            // 重新应用色彩主题
            applyColorTheme();
        }
    }

    /**
     * 推送答题结果到内场秀
     */
    private void pushQuizResultToInner() {
        try {
            Intent broadcast = new Intent("com.jcoding.aiactivity.QUIZ_RESULT_UPDATE");
            broadcast.putExtra("action", "new_result");
            broadcast.putExtra("total_questions", questionList.size());
            broadcast.putExtra("correct_count", correctCount);
            broadcast.putExtra("timestamp", System.currentTimeMillis());
            sendBroadcast(broadcast);

            android.util.Log.i("QuizActivity", "Quiz result pushed to inner show");
        } catch (Exception e) {
            android.util.Log.e("QuizActivity", "Failed to push quiz result to inner show", e);
        }
    }

    /**
     * 显示语音设置对话框
     */
    private void showVoiceSettingDialog(VoiceCommandManager.VoiceCommand command) {
        VoiceSettingDialog dialog = new VoiceSettingDialog(this, command);
        dialog.setOnSettingAppliedListener(new VoiceSettingDialog.OnSettingAppliedListener() {
            @Override
            public void onSettingApplied(VoiceCommandManager.VoiceCommand command) {
                // 设置已应用，可以在这里添加额外的处理逻辑
                android.util.Log.i("QuizActivity", "设置已应用: " + command.description);
            }
        });
        dialog.show();
    }

    /**
     * 开始语音识别
     */
    private void startVoiceRecognition() {
        // 检查录音权限
        requestPermissions(new String[]{
                Manifest.permission.RECORD_AUDIO
        }, new PermissionResultListener() {
            @Override
            public void onGranted() {
                // 如果正在播报题目，停止播报
                if (isSpeakingQuestion) {
                    stopSpeaking();
                }

                // 开始语音识别
                showVoiceStatus("正在听...");
                btnVoiceInput.setEnabled(false);

                voiceManager.startVoiceRecognition(new VoiceManager.VoiceRecognitionCallback() {
                    @Override
                    public void onIntermediateResult(String text) {
                        // 实时显示识别结果
                        showVoiceStatus("听到: " + text);
                    }

                    @Override
                    public void onRecognitionResult(String text) {
                        // 识别完成
                        showVoiceStatus("识别: " + text);
                        btnVoiceInput.setEnabled(true);

                        // 优先检查是否是语音设置命令
                        VoiceCommandManager.VoiceCommand command = voiceCommandManager.parseCommand(text);
                        if (command != null) {
                            // 识别到设置命令，显示设置对话框
                            showVoiceSettingDialog(command);
                            return;
                        }

                        // 不是设置命令，继续分析答案
                        analyzeVoiceAnswer(text);
                    }

                    @Override
                    public void onError(String error) {
                        showVoiceStatus("识别失败: " + error);
                        btnVoiceInput.setEnabled(true);
                        hideVoiceStatus();
                        showToast("语音识别失败: " + error);
                    }
                });
            }

            @Override
            public void onDenied() {
                showToast("需要录音权限才能使用语音答题");
            }
        });
    }

    /**
     * 分析语音答案
     */
    private void analyzeVoiceAnswer(String text) {
        if (text == null || text.isEmpty()) {
            return;
        }

        Question question = questionList.get(currentQuestionIndex);
        String answer = "";

        // 提取答案关键词
        text = text.toLowerCase().replace(" ", "").replace("，", "").replace("。", "");

        // 判断题
        if (question.isJudgement()) {
            if (text.contains("对") || text.contains("正确") || text.contains("是")
                    || text.contains("true") || text.contains("t")) {
                answer = "对";
            } else if (text.contains("错") || text.contains("错误") || text.contains("不")
                    || text.contains("false") || text.contains("f")) {
                answer = "错";
            }
        }
        // 选择题
        else if (question.isChoice()) {
            if (text.contains("a") || text.contains("1")) {
                answer = "A";
            } else if (text.contains("b") || text.contains("2")) {
                answer = "B";
            } else if (text.contains("c") || text.contains("3")) {
                answer = "C";
            } else if (text.contains("d") || text.contains("4")) {
                answer = "D";
            }
        }

        // 匹配答案
        if (!answer.isEmpty()) {
            int answerIndex = parseAnswerIndex(answer);
            selectAnswer(answerIndex);
        } else {
            showToast("未识别到答案，请重试");
            hideVoiceStatus();
        }
    }

    /**
     * 解析答案索引
     */
    private int parseAnswerIndex(String answer) {
        answer = answer.toUpperCase().trim();
        switch (answer) {
            case "A":
            case "对":
            case "正确":
                return 0;
            case "B":
            case "错":
            case "错误":
                return 1;
            case "C":
                return 2;
            case "D":
                return 3;
            default:
                return 0;
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // 停止语音播报和识别
        if (voiceManager != null) {
            voiceManager.stopSpeaking();
            voiceManager.stopVoiceRecognition();
        }
        // 释放背景图片资源
        recycleBackgroundImage();
    }

    /**
     * 加载背景图片
     */
    private void loadBackgroundImage() {
        try {
            android.graphics.Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(
                    getAssets().open("image/question_bk.png"));
            android.graphics.drawable.BitmapDrawable drawable = new android.graphics.drawable.BitmapDrawable(
                    getResources(), bitmap);

            // 设置到背景ImageView
            android.widget.ImageView ivBackground = findViewById(R.id.iv_background);
            if (ivBackground != null) {
                ivBackground.setImageDrawable(drawable);
            }
        } catch (java.io.IOException e) {
            android.util.Log.e("QuizActivity", "Failed to load background image", e);
            // 背景图片加载失败，使用默认背景
        }
    }

    /**
     * 释放背景图片资源
     */
    private void recycleBackgroundImage() {
        try {
            android.view.View contentView = findViewById(android.R.id.content);
            if (contentView != null) {
                android.graphics.drawable.Drawable background = contentView.getBackground();
                if (background instanceof android.graphics.drawable.BitmapDrawable) {
                    android.graphics.Bitmap bitmap = ((android.graphics.drawable.BitmapDrawable) background).getBitmap();
                    if (bitmap != null && !bitmap.isRecycled()) {
                        bitmap.recycle();
                    }
                }
                contentView.setBackground(null);
            }
        } catch (Exception e) {
            android.util.Log.e("QuizActivity", "Failed to recycle background image", e);
        }
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
