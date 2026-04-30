package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.cardview.widget.CardView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.InnerShowDataManager;
import com.jcoding.aiactivity.manager.QuizPrizeConfigManager;
import com.jcoding.aiactivity.manager.UserLoginManager;
import com.jcoding.aiactivity.manager.InnerShowNetworkClient;
import com.jcoding.aiactivity.manager.InnerShowNetworkConfigManager;

/**
 * 答题结果页
 * 显示答题成绩和中奖信息
 */
public class QuizResultActivity extends BaseActivity {

    private TextView tvScore;
    private TextView tvResult;
    private CardView cardPrize;
    private ImageView ivPrizeImage;
    private TextView tvPrizeLevel;
    private TextView tvPrizeName;
    private TextView tvPrizeDescription;
    private TextView tvPrizeHint;
    private TextView tvNoPrize;
    private Button btnBack;
    private Button btnShare;

    private int totalQuestions;
    private int correctCount;

    private QuizPrizeConfigManager prizeConfigManager;
    private InnerShowDataManager innerShowDataManager;
    private UserLoginManager userLoginManager;
    private InnerShowNetworkClient networkClient;
    private InnerShowNetworkConfigManager networkConfigManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_quiz_result);

        // 获取参数
        totalQuestions = getIntent().getIntExtra("total_questions", 0);
        correctCount = getIntent().getIntExtra("correct_count", 0);

        // 初始化管理器
        prizeConfigManager = QuizPrizeConfigManager.getInstance(this);
        innerShowDataManager = InnerShowDataManager.getInstance(this);
        userLoginManager = UserLoginManager.getInstance(this);
        networkClient = InnerShowNetworkClient.getInstance(this);
        networkConfigManager = InnerShowNetworkConfigManager.getInstance(this);

        initViews();
        displayResult();
        checkAndDisplayPrize();
    }

    private void initViews() {
        tvScore = findViewById(R.id.tv_score);
        tvResult = findViewById(R.id.tv_result);
        cardPrize = findViewById(R.id.card_prize);
        ivPrizeImage = findViewById(R.id.iv_prize_image);
        tvPrizeLevel = findViewById(R.id.tv_prize_level);
        tvPrizeName = findViewById(R.id.tv_prize_name);
        tvPrizeDescription = findViewById(R.id.tv_prize_description);
        tvPrizeHint = findViewById(R.id.tv_prize_hint);
        tvNoPrize = findViewById(R.id.tv_no_prize);
        btnBack = findViewById(R.id.btn_back);
        btnShare = findViewById(R.id.btn_share);

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnShare.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                shareResult();
            }
        });
    }

    /**
     * 显示结果
     */
    private void displayResult() {
        // 计算得分
        int score = (int) ((double) correctCount / totalQuestions * 100);
        tvScore.setText(String.format("得分：%d 分", score));

        // 评价
        if (score >= 90) {
            tvResult.setText("优秀！");
        } else if (score >= 80) {
            tvResult.setText("良好！");
        } else if (score >= 60) {
            tvResult.setText("及格");
        } else {
            tvResult.setText("继续努力");
        }
    }

    /**
     * 检查并显示奖品
     */
    private void checkAndDisplayPrize() {
        // 获取奖品配置
        QuizPrizeConfigManager.PrizeConfig prizeConfig = prizeConfigManager.loadPrizeConfig();

        // 如果未启用奖品功能
        if (!prizeConfig.enabled) {
            tvNoPrize.setText("恭喜完成答题！");
            tvNoPrize.setVisibility(View.VISIBLE);
            cardPrize.setVisibility(View.GONE);
            return;
        }

        // 检查是否需要登录
        if (prizeConfig.requireLogin && !userLoginManager.isLoggedIn()) {
            tvNoPrize.setText("请先登录才能参与奖品活动");
            tvNoPrize.setVisibility(View.VISIBLE);
            cardPrize.setVisibility(View.GONE);
            return;
        }

        // 根据答对数量获取奖品
        QuizPrizeConfigManager.PrizeRule prize = prizeConfigManager.getPrizeByCorrectCount(correctCount);

        if (prize != null) {
            // 显示奖品
            displayPrize(prize);

            // 保存中奖记录
            saveQuizWinner(prize);

            // 推送到内场设备（如果配置启用）
            if (prizeConfig.pushToInner) {
                pushToInnerShow(prize);
            }
        } else {
            // 未中奖
            tvNoPrize.setText(String.format("答对 %d 题，继续加油！", correctCount));
            tvNoPrize.setVisibility(View.VISIBLE);
            cardPrize.setVisibility(View.GONE);
        }
    }

    /**
     * 显示奖品信息
     */
    private void displayPrize(QuizPrizeConfigManager.PrizeRule prize) {
        tvNoPrize.setVisibility(View.GONE);
        cardPrize.setVisibility(View.VISIBLE);

        // 奖品等级
        tvPrizeLevel.setText("🎉 " + prize.level);

        // 奖品名称
        tvPrizeName.setText(prize.name);

        // 奖品描述
        tvPrizeDescription.setText(prize.description);

        // 始终显示默认奖品图片
        ivPrizeImage.setVisibility(View.VISIBLE);
        loadDefaultPrizeImage();

        // 根据奖品等级显示不同的提示
        if ("特等奖".equals(prize.level)) {
            tvPrizeHint.setText("🎊 恭喜您获得特等奖！请截图保存或前往领奖处领取。");
        } else {
            tvPrizeHint.setText("恭喜您中奖啦！请截图保存或前往领奖处领取。");
        }
    }

    /**
     * 加载默认奖品图片
     */
    private void loadDefaultPrizeImage() {
        try {
            // 从assets加载默认奖品图片 - 使用lottery下的奖品图片
            Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(getAssets().open("lottery/circle/static/images/config_prize.png"));
            if (bitmap != null) {
                ivPrizeImage.setImageBitmap(bitmap);
                android.util.Log.d("QuizResultActivity", "默认奖品图片加载成功 (lottery/circle/static/images/config_prize.png)");
            } else {
                android.util.Log.e("QuizResultActivity", "默认奖品图片为null");
                ivPrizeImage.setVisibility(View.GONE);
            }
        } catch (Exception e) {
            android.util.Log.e("QuizResultActivity", "加载默认奖品图片失败: " + e.getMessage());
            ivPrizeImage.setVisibility(View.GONE);
        }
    }

    /**
     * 加载奖品图片（保留原有方法，但不再使用）
     */
    private void loadPrizeImage(String imageUrl) {
        // 此方法已弃用，统一使用loadDefaultPrizeImage()
        loadDefaultPrizeImage();
    }

    /**
     * 保存答题中奖记录
     */
    private void saveQuizWinner(QuizPrizeConfigManager.PrizeRule prize) {
        InnerShowDataManager.QuizWinner winner = new InnerShowDataManager.QuizWinner();

        // 获取当前登录用户信息
        UserLoginManager.UserInfo currentUser = userLoginManager.getCurrentUser();
        if (currentUser != null) {
            winner.userId = currentUser.userId;
            winner.userName = currentUser.userName;
            winner.userPhone = currentUser.userPhone;
        } else {
            winner.userName = "游客";
        }

        // 奖品信息
        winner.prizeName = prize.name;
        winner.prizeLevel = prize.level;
        winner.prizeDescription = prize.description;
        winner.prizeImageUrl = prize.imageUrl;

        // 答题信息
        winner.totalQuestions = totalQuestions;
        winner.correctCount = correctCount;

        // 保存到内场数据管理器
        innerShowDataManager.addQuizWinner(winner);
    }

    /**
     * 推送到内场秀
     */
    private void pushToInnerShow(QuizPrizeConfigManager.PrizeRule prize) {
        InnerShowDataManager.QuizWinner winner = innerShowDataManager.getLatestQuizWinner();

        if (winner != null) {
            // 检查是否是主服务器模式
            if (networkConfigManager.isServerMode()) {
                // 主服务器模式：本设备就是内场秀设备，直接发送本地广播
                Intent broadcast = new Intent("com.jcoding.aiactivity.INNER_SHOW_UPDATE");
                broadcast.putExtra("action", "new_quiz_winner");
                broadcast.putExtra("quiz_winner_id", winner.id);
                broadcast.putExtra("winner_name", winner.userName);
                sendBroadcast(broadcast);
                showToast("中奖信息已推送到内场秀");
            } else {
                // 客户端模式：通过网络推送到内场秀设备
                networkClient.pushQuizWinner(winner, new InnerShowNetworkClient.NetworkCallback() {
                    @Override
                    public void onSuccess(String result) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                showToast("中奖信息已推送到内场秀设备");
                            }
                        });
                    }

                    @Override
                    public void onError(String error) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                showToast("推送失败: " + error + "，已保存到本地");
                            }
                        });
                    }
                });

                // 同时发送本地广播（同一设备的情况）
                Intent broadcast = new Intent("com.jcoding.aiactivity.INNER_SHOW_UPDATE");
                broadcast.putExtra("action", "new_quiz_winner");
                broadcast.putExtra("quiz_winner_id", winner.id);
                broadcast.putExtra("winner_name", winner.userName);
                sendBroadcast(broadcast);
            }
        }
    }

    /**
     * 分享结果
     */
    private void shareResult() {
        // TODO: 实现分享功能
        showToast("分享功能开发中");
    }
}
