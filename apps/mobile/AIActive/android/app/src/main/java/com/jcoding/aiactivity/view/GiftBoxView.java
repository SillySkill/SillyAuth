package com.jcoding.aiactivity.view;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;
import android.view.animation.AccelerateDecelerateInterpolator;
import android.view.animation.BounceInterpolator;

import com.jcoding.aiactivity.entity.Candidate;
import com.jcoding.aiactivity.entity.PrizeData;

/**
 * 礼物盒动画View
 * 实现从礼物盒中弹出奖品的动画效果
 */
public class GiftBoxView extends View {

    private Paint paint;
    private Paint textPaint;
    private Paint boxPaint;
    private Paint ribbonPaint;

    private float boxOpenProgress = 0f;      // 盒子打开进度 0-1
    private float prizePopProgress = 0f;      // 奖品弹出进度 0-1
    private float scale = 1f;                 // 整体缩放
    private boolean isAnimating = false;

    private PrizeData currentPrize;           // 当前奖品（兼容旧代码）
    private Candidate currentWinner;          // 当前中奖者

    // 颜色配置
    private static final int BOX_COLOR = 0xFFFF6B6B;     // 盒子颜色
    private static final int RIBBON_COLOR = 0xFFFFD93D;  // 丝带颜色
    private static final int TEXT_COLOR = 0xFF333333;     // 文字颜色

    public GiftBoxView(Context context) {
        super(context);
        init();
    }

    public GiftBoxView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public GiftBoxView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        boxPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        ribbonPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

        textPaint.setColor(TEXT_COLOR);
        textPaint.setTextSize(48 * getResources().getDisplayMetrics().density);
        textPaint.setTextAlign(Paint.Align.CENTER);
        textPaint.setFakeBoldText(true);

        boxPaint.setColor(BOX_COLOR);
        boxPaint.setStyle(Paint.Style.FILL);

        ribbonPaint.setColor(RIBBON_COLOR);
        ribbonPaint.setStyle(Paint.Style.FILL);
    }

    /**
     * 设置当前奖品并开始动画
     */
    public void setPrizeAndAnimate(PrizeData prize) {
        this.currentPrize = prize;
        this.currentWinner = null;
        startGiftBoxAnimation();
    }

    /**
     * 设置当前中奖者并开始动画
     */
    public void setWinnerAndAnimate(Candidate winner) {
        this.currentWinner = winner;
        this.currentPrize = null;
        startGiftBoxAnimation();
    }

    /**
     * 开始礼物盒动画
     */
    public void startGiftBoxAnimation() {
        if (isAnimating) {
            return;
        }

        isAnimating = true;
        boxOpenProgress = 0f;
        prizePopProgress = 0f;
        scale = 0.5f;

        // 创建动画序列
        AnimatorSet animatorSet = new AnimatorSet();

        // 1. 缩放动画（盒子出现）
        ObjectAnimator scaleAnimator = ObjectAnimator.ofFloat(this, "scale", 0.5f, 1.2f, 1f);
        scaleAnimator.setDuration(500);
        scaleAnimator.setInterpolator(new AccelerateDecelerateInterpolator());

        // 2. 盒子打开动画
        ObjectAnimator boxOpenAnimator = ObjectAnimator.ofFloat(this, "boxOpenProgress", 0f, 1f);
        boxOpenAnimator.setDuration(800);
        boxOpenAnimator.setInterpolator(new AccelerateDecelerateInterpolator());
        boxOpenAnimator.addListener(new AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(Animator animation) {
                // 盒子打开完成后，开始奖品弹出动画
                startPrizePopAnimation();
            }
        });

        // 播放序列：先缩放，再打开盒子
        animatorSet.playSequentially(scaleAnimator, boxOpenAnimator);
        animatorSet.addListener(new AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(Animator animation) {
                // 动画完成
                if (onGiftBoxAnimationListener != null) {
                    onGiftBoxAnimationListener.onAnimationComplete();
                }
            }
        });
        animatorSet.start();
    }

    /**
     * 开始奖品弹出动画
     */
    private void startPrizePopAnimation() {
        ObjectAnimator prizePopAnimator = ObjectAnimator.ofFloat(this, "prizePopProgress", 0f, 1f);
        prizePopAnimator.setDuration(1000);
        prizePopAnimator.setInterpolator(new BounceInterpolator());
        prizePopAnimator.addListener(new AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(Animator animation) {
                isAnimating = false;
            }
        });
        prizePopAnimator.start();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        int centerX = getWidth() / 2;
        int centerY = getHeight() / 2;

        canvas.save();
        canvas.scale(scale, scale, centerX, centerY);

        // 绘制礼物盒
        drawGiftBox(canvas, centerX, centerY);

        // 如果有奖品，绘制奖品
        if (currentPrize != null && prizePopProgress > 0) {
            drawPrize(canvas, centerX, centerY);
        }

        // 如果有中奖者，绘制中奖者
        if (currentWinner != null && prizePopProgress > 0) {
            drawWinner(canvas, centerX, centerY);
        }

        canvas.restore();
    }

    /**
     * 绘制礼物盒
     */
    private void drawGiftBox(Canvas canvas, int centerX, int centerY) {
        float boxSize = 200 * getResources().getDisplayMetrics().density;

        // 盒子主体
        RectF boxRect = new RectF(
            centerX - boxSize / 2,
            centerY - boxSize / 4,
            centerX + boxSize / 2,
            centerY + boxSize / 2
        );

        // 绘制盒子主体
        canvas.drawRect(boxRect, boxPaint);

        // 绘制丝带（垂直）
        float ribbonWidth = boxSize / 6;
        RectF vRibbonRect = new RectF(
            centerX - ribbonWidth / 2,
            boxRect.top,
            centerX + ribbonWidth / 2,
            boxRect.bottom
        );
        canvas.drawRect(vRibbonRect, ribbonPaint);

        // 绘制丝带（水平）
        RectF hRibbonRect = new RectF(
            boxRect.left,
            centerY - boxSize / 6,
            boxRect.right,
            centerY + boxSize / 6
        );
        canvas.drawRect(hRibbonRect, ribbonPaint);

        // 绘制盒子盖子（根据打开进度旋转）
        canvas.save();
        float lidAngle = -boxOpenProgress * 120; // 最大打开120度
        canvas.rotate(lidAngle, centerX, boxRect.top);

        // 盖子主体
        RectF lidRect = new RectF(
            centerX - boxSize / 2 - 10,
            centerY - boxSize / 2 - 20,
            centerX + boxSize / 2 + 10,
            centerY - boxSize / 4
        );
        canvas.drawRect(lidRect, boxPaint);

        // 盖子丝带
        RectF lidRibbonRect = new RectF(
            centerX - ribbonWidth / 2,
            lidRect.top + 10,
            centerX + ribbonWidth / 2,
            lidRect.bottom
        );
        canvas.drawRect(lidRibbonRect, ribbonPaint);

        canvas.restore();
    }

    /**
     * 绘制中奖者
     */
    private void drawWinner(Canvas canvas, int centerX, int centerY) {
        // 中奖者从盒子中心弹出
        float popDistance = 250 * getResources().getDisplayMetrics().density * prizePopProgress;
        float winnerY = centerY - popDistance;

        // 绘制中奖者姓名
        if (currentWinner != null) {
            String winnerText = currentWinner.getName();
            canvas.drawText(winnerText, centerX, winnerY, textPaint);

            // 绘制部门信息
            if (currentWinner.getDepartment() != null && !currentWinner.getDepartment().isEmpty()) {
                textPaint.setTextSize(36 * getResources().getDisplayMetrics().density);
                textPaint.setAlpha((int) (prizePopProgress * 255));
                String departmentText = currentWinner.getDepartment();
                canvas.drawText(departmentText, centerX, winnerY + 60 * getResources().getDisplayMetrics().density, textPaint);
                textPaint.setAlpha(255);
                textPaint.setTextSize(48 * getResources().getDisplayMetrics().density);
            }

            // 不绘制ID
        }

        // 绘制星星装饰
        drawStars(canvas, centerX, winnerY - 50 * getResources().getDisplayMetrics().density);
    }

    /**
     * 绘制奖品
     */
    private void drawPrize(Canvas canvas, int centerX, int centerY) {
        // 奖品从盒子中心弹出
        float popDistance = 250 * getResources().getDisplayMetrics().density * prizePopProgress;
        float prizeY = centerY - popDistance;

        // 绘制奖品名称
        if (currentPrize != null) {
            String prizeText = currentPrize.getName();
            canvas.drawText(prizeText, centerX, prizeY, textPaint);

            // 绘制商家信息
            if (currentPrize.getMerchant() != null && !currentPrize.getMerchant().isEmpty()) {
                textPaint.setTextSize(36 * getResources().getDisplayMetrics().density);
                textPaint.setAlpha((int) (prizePopProgress * 255));
                String merchantText = "来自：" + currentPrize.getMerchant();
                canvas.drawText(merchantText, centerX, prizeY + 60 * getResources().getDisplayMetrics().density, textPaint);
                textPaint.setAlpha(255);
                textPaint.setTextSize(48 * getResources().getDisplayMetrics().density);
            }

            // 绘制描述（如果有）
            if (currentPrize.getDescription() != null && !currentPrize.getDescription().isEmpty()) {
                textPaint.setTextSize(32 * getResources().getDisplayMetrics().density);
                textPaint.setAlpha((int) (prizePopProgress * 200));
                canvas.drawText(currentPrize.getDescription(), centerX, prizeY + 120 * getResources().getDisplayMetrics().density, textPaint);
                textPaint.setAlpha(255);
                textPaint.setTextSize(48 * getResources().getDisplayMetrics().density);
            }
        }

        // 绘制星星装饰
        drawStars(canvas, centerX, prizeY - 50 * getResources().getDisplayMetrics().density);
    }

    /**
     * 绘制星星装饰
     */
    private void drawStars(Canvas canvas, int centerX, float centerY) {
        paint.setColor(0xFFFFD93D);
        paint.setStyle(Paint.Style.FILL);

        int starCount = 8;
        float radius = 100 * getResources().getDisplayMetrics().density;

        for (int i = 0; i < starCount; i++) {
            float angle = (float) (2 * Math.PI * i / starCount);
            float x = centerX + (float) (Math.cos(angle) * radius);
            float y = centerY + (float) (Math.sin(angle) * radius);
            float size = 15 * getResources().getDisplayMetrics().density;

            drawStar(canvas, x, y, size);
        }
    }

    /**
     * 绘制单个星星
     */
    private void drawStar(Canvas canvas, float x, float y, float size) {
        Path path = new Path();
        float halfSize = size / 2;
        float innerRadius = size / 4;

        for (int i = 0; i < 5; i++) {
            float outerAngle = (float) (2 * Math.PI * i / 5 - Math.PI / 2);
            float innerAngle = (float) (2 * Math.PI * (i + 0.5f) / 5 - Math.PI / 2);

            if (i == 0) {
                path.moveTo(
                    x + (float) Math.cos(outerAngle) * halfSize,
                    y + (float) Math.sin(outerAngle) * halfSize
                );
            } else {
                path.lineTo(
                    x + (float) Math.cos(outerAngle) * halfSize,
                    y + (float) Math.sin(outerAngle) * halfSize
                );
            }

            path.lineTo(
                x + (float) Math.cos(innerAngle) * innerRadius,
                y + (float) Math.sin(innerAngle) * innerRadius
            );
        }

        path.close();
        canvas.drawPath(path, paint);
    }

    // Setter方法用于动画

    public void setScale(float scale) {
        this.scale = scale;
        invalidate();
    }

    public void setBoxOpenProgress(float progress) {
        this.boxOpenProgress = progress;
        invalidate();
    }

    public void setPrizePopProgress(float progress) {
        this.prizePopProgress = progress;
        invalidate();
    }

    /**
     * 重置视图状态
     */
    public void reset() {
        boxOpenProgress = 0f;
        prizePopProgress = 0f;
        scale = 1f;
        currentPrize = null;
        currentWinner = null;
        isAnimating = false;
        invalidate();
    }

    /**
     * 礼物盒动画监听器
     */
    public interface OnGiftBoxAnimationListener {
        void onAnimationComplete();
    }

    private OnGiftBoxAnimationListener onGiftBoxAnimationListener;

    public void setOnGiftBoxAnimationListener(OnGiftBoxAnimationListener listener) {
        this.onGiftBoxAnimationListener = listener;
    }
}
