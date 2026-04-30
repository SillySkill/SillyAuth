package com.jcoding.aiactivity.ui;

import android.Manifest;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.Question;
import com.jcoding.aiactivity.entity.QuestionBank;
import com.jcoding.aiactivity.manager.VoiceManager;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

/**
 * 语音版知识答题页
 * 支持语音识别答案和语音播报题目
 */
public class QuizVoiceActivity extends BaseActivity {

    private TextView tvQuestionNumber;
    private TextView tvQuestion;
    private Button btnOptionA;
    private Button btnOptionB;
    private Button btnOptionC;
    private Button btnOptionD;
    private Button btnNext;
    private Button btnSubmit;
    private ProgressBar progressBar;
    private Button btnBack;
    private TextView tvOfflineMode;

    // 语音相关控件
    private ImageButton btnVoiceInput;
    private ImageButton btnVoiceOutput;
    private TextView tvVoiceStatus;

    private QuestionBank questionBank;
    private List<Question> questionList;
    private int currentQuestionIndex = 0;
    private int correctCount = 0;
    private int[] userAnswers;
    private Random random;

    private VoiceManager voiceManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_quiz_voice);

        random = new Random();
        voiceManager = VoiceManager.getInstance(this);

        initViews();
        loadQuestions();
        setupListeners();
    }

    private void initViews() {
        tvQuestionNumber = findViewById(R.id.tv_question_number);
        tvQuestion = findViewById(R.id.tv_question);
        btnOptionA = findViewById(R.id.btn_option_a);
        btnOptionB = findViewById(R.id.btn_option_b);
        btnOptionC = findViewById(R.id.btn_option_c);
        btnOptionD = findViewById(R.id.btn_option_d);
        btnNext = findViewById(R.id.btn_next);
        btnSubmit = findViewById(R.id.btn_submit);
        progressBar = findViewById(R.id.progress_bar);
        btnBack = findViewById(R.id.btn_back);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        // 语音控件
        btnVoiceInput = findViewById(R.id.btn_voice_input);
        btnVoiceOutput = findViewById(R.id.btn_voice_output);
        tvVoiceStatus = findViewById(R.id.tv_voice_status);

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

        // 语音输入按钮
        btnVoiceInput.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startVoiceRecognition();
            }
        });

        // 语音播报按钮
        btnVoiceOutput.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                speakCurrentQuestion();
            }
        });

        // 初始隐藏下一题和提交按钮
        btnNext.setVisibility(View.GONE);
        btnSubmit.setVisibility(View.GONE);
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
     * 开始语音识别
     */
    private void startVoiceRecognition() {
        // 检查录音权限
        requestPermissions(new String[]{
                Manifest.permission.RECORD_AUDIO
        }, new PermissionResultListener() {
            @Override
            public void onGranted() {
                // 开始语音识别
                tvVoiceStatus.setText("正在听...");
                tvVoiceStatus.setVisibility(View.VISIBLE);
                btnVoiceInput.setEnabled(false);

                voiceManager.startVoiceRecognition(new VoiceManager.VoiceRecognitionCallback() {
                    @Override
                    public void onIntermediateResult(String text) {
                        // 实时显示识别结果
                        tvVoiceStatus.setText("听到: " + text);
                    }

                    @Override
                    public void onRecognitionResult(String text) {
                        // 识别完成，分析答案
                        tvVoiceStatus.setText("识别: " + text);
                        analyzeVoiceAnswer(text);
                    }

                    @Override
                    public void onError(String error) {
                        tvVoiceStatus.setText("识别失败: " + error);
                        btnVoiceInput.setEnabled(true);
                    }
                });
            }

            @Override
            public void onDenied() {
                showToast("需要录音权限才能使用语音输入");
            }
        });
    }

    /**
     * 分析语音答案
     */
    private void analyzeVoiceAnswer(String text) {
        if (text == null || text.isEmpty()) {
            btnVoiceInput.setEnabled(true);
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
        }

        btnVoiceInput.setEnabled(true);
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

    /**
     * 播报当前题目
     */
    private void speakCurrentQuestion() {
        if (currentQuestionIndex >= questionList.size()) {
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

        btnVoiceOutput.setEnabled(false);
        tvVoiceStatus.setText("正在播报...");
        tvVoiceStatus.setVisibility(View.VISIBLE);

        voiceManager.speakText(textToSpeak, new VoiceManager.VoiceSynthesisCallback() {
            @Override
            public void onSpeakStart() {
            }

            @Override
            public void onSpeakPaused() {
            }

            @Override
            public void onSpeakResumed() {
            }

            @Override
            public void onSpeakComplete() {
                tvVoiceStatus.setText("播报完成");
                tvVoiceStatus.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        tvVoiceStatus.setVisibility(View.GONE);
                    }
                }, 2000);
                btnVoiceOutput.setEnabled(true);
            }

            @Override
            public void onError(String error) {
                tvVoiceStatus.setText("播报失败: " + error);
                btnVoiceOutput.setEnabled(true);
            }
        });
    }

    /**
     * 加载题目
     */
    private void loadQuestions() {
        // 获取题库配置
        com.google.gson.JsonObject questionConfig = configManager.getQuestionConfig();
        if (questionConfig == null || !questionConfig.has("round")) {
            showToast("题库配置加载失败，使用默认配置");
            loadQuestionsFallback();
            return;
        }

        // 读取round配置
        com.google.gson.JsonObject roundConfig = questionConfig.getAsJsonObject("round");
        int totalQty = roundConfig.has("qty") ? roundConfig.get("qty").getAsInt() : 10;
        int choiceQty = roundConfig.has("choice") ? roundConfig.get("choice").getAsInt() : 6;
        int judgementQty = roundConfig.has("judgement") ? roundConfig.get("judgement").getAsInt() : 4;

        // 获取默认题库
        questionBank = configManager.getDefaultQuestionBank();
        if (questionBank == null || questionBank.getQuestionCount() == 0) {
            showToast("题库加载失败");
            finish();
            return;
        }

        // 分类获取题目
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
            choiceQty = choiceQuestions.size();
        }

        if (judgementQuestions.size() < judgementQty) {
            showToast("判断题数量不足：需要" + judgementQty + "题，实际只有" + judgementQuestions.size() + "题");
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

        // 再次打乱题目顺序
        Collections.shuffle(questionList);

        // 初始化用户答案数组
        userAnswers = new int[questionList.size()];
        for (int i = 0; i < userAnswers.length; i++) {
            userAnswers[i] = -1;
        }

        displayQuestion();
    }

    /**
     * 加载题目（降级方案）
     */
    private void loadQuestionsFallback() {
        questionBank = configManager.getDefaultQuestionBank();

        if (questionBank == null || questionBank.getQuestionCount() == 0) {
            showToast("题库加载失败");
            finish();
            return;
        }

        questionList = new ArrayList<>(questionBank.getQuestions());
        Collections.shuffle(questionList);

        int maxQuestions = Math.min(questionList.size(), 10);
        questionList = questionList.subList(0, maxQuestions);

        userAnswers = new int[questionList.size()];
        for (int i = 0; i < userAnswers.length; i++) {
            userAnswers[i] = -1;
        }

        displayQuestion();
    }

    /**
     * 显示当前题目
     */
    private void displayQuestion() {
        if (currentQuestionIndex >= questionList.size()) {
            showResult();
            return;
        }

        Question question = questionList.get(currentQuestionIndex);

        tvQuestionNumber.setText(String.format("第 %d / %d 题",
                currentQuestionIndex + 1, questionList.size()));

        tvQuestion.setText(question.getContent());

        if (question.isChoice()) {
            String[] options = question.getOptions();
            btnOptionA.setText("A. " + (options != null && options.length > 0 ? options[0] : ""));
            btnOptionB.setText("B. " + (options != null && options.length > 1 ? options[1] : ""));
            btnOptionC.setText("C. " + (options != null && options.length > 2 ? options[2] : ""));
            btnOptionD.setText("D. " + (options != null && options.length > 3 ? options[3] : ""));

            btnOptionC.setVisibility(View.VISIBLE);
            btnOptionD.setVisibility(View.VISIBLE);
        } else if (question.isJudgement()) {
            btnOptionA.setText("正确");
            btnOptionB.setText("错误");
            btnOptionC.setVisibility(View.GONE);
            btnOptionD.setVisibility(View.GONE);
        }

        resetOptionButtons();
        btnNext.setVisibility(View.GONE);
        btnSubmit.setVisibility(View.GONE);
        tvVoiceStatus.setVisibility(View.GONE);

        // 自动播报题目（可选）
        // speakCurrentQuestion();
    }

    /**
     * 选择答案
     */
    private void selectAnswer(int answerIndex) {
        userAnswers[currentQuestionIndex] = answerIndex;
        highlightSelectedOption(answerIndex);
        showNextButton();

        // 停止语音识别
        if (voiceManager.isRecognizing()) {
            voiceManager.stopVoiceRecognition();
        }
    }

    /**
     * 高亮选中选项
     */
    private void highlightSelectedOption(int answerIndex) {
        resetOptionButtons();

        switch (answerIndex) {
            case 0:
                btnOptionA.setSelected(true);
                break;
            case 1:
                btnOptionB.setSelected(true);
                break;
            case 2:
                btnOptionC.setSelected(true);
                break;
            case 3:
                btnOptionD.setSelected(true);
                break;
        }
    }

    /**
     * 重置选项按钮
     */
    private void resetOptionButtons() {
        btnOptionA.setSelected(false);
        btnOptionB.setSelected(false);
        btnOptionC.setSelected(false);
        btnOptionD.setSelected(false);
    }

    /**
     * 显示下一题按钮
     */
    private void showNextButton() {
        if (currentQuestionIndex < questionList.size() - 1) {
            btnNext.setVisibility(View.VISIBLE);
        } else {
            btnSubmit.setVisibility(View.VISIBLE);
        }
    }

    /**
     * 下一题
     */
    private void nextQuestion() {
        currentQuestionIndex++;
        displayQuestion();
    }

    /**
     * 提交答题
     */
    private void submitQuiz() {
        calculateScore();
        showResult();
    }

    /**
     * 计算得分
     */
    private void calculateScore() {
        correctCount = 0;

        for (int i = 0; i < questionList.size(); i++) {
            Question question = questionList.get(i);
            if (userAnswers[i] == question.getCorrectAnswer()) {
                correctCount++;
            }
        }
    }

    /**
     * 显示结果
     */
    private void showResult() {
        Intent intent = new Intent(this, QuizResultActivity.class);
        intent.putExtra("total_questions", questionList.size());
        intent.putExtra("correct_count", correctCount);
        startActivity(intent);
        finish();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // 停止语音识别和合成
        if (voiceManager != null) {
            voiceManager.stopVoiceRecognition();
            voiceManager.stopSpeaking();
        }
    }
}
