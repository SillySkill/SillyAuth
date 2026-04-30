package com.jcoding.aiactivity.view;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.util.AttributeSet;
import android.view.View;
import android.view.animation.AccelerateDecelerateInterpolator;

import java.util.ArrayList;
import java.util.Random;

/**
 * 礼花动画View
 * 实现由礼物组成的礼花满屏散开的动画效果
 */
public class FireworksView extends View {

    private Paint paint;
    private Random random;
    private ArrayList<FireworkParticle> particles;
    private boolean isAnimating = false;
    private ValueAnimator animator;

    // 礼花颜色（多彩礼物颜色）
    private static final int[] FIREWORK_COLORS = {
        0xFFFF6B6B, // 红色
        0xFFFFD93D, // 黄色
        0xFF6BCB77, // 绿色
        0xFF4D96FF, // 蓝色
        0xFFFF9F45, // 橙色
        0xFF9B59B6, // 紫色
        0xFF1ABC9C, // 青色
        0xFFE74C3C, // 深红
    };

    // 礼物图标路径（简化版）
    private Path giftPath;

    public FireworksView(Context context) {
        super(context);
        init();
    }

    public FireworksView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public FireworksView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        paint.setStyle(Paint.Style.FILL);
        random = new Random();
        particles = new ArrayList<>();

        // 创建礼物图标路径
        createGiftPath();
    }

    /**
     * 创建礼物图标路径
     */
    private void createGiftPath() {
        giftPath = new Path();
        // 简化的礼物盒子形状
        giftPath.moveTo(0, 0.4f);
        giftPath.lineTo(0.3f, 0.4f);
        giftPath.lineTo(0.3f, 0.7f);
        giftPath.lineTo(0, 0.7f);
        giftPath.close();
        // 盖子
        giftPath.moveTo(-0.1f, 0.4f);
        giftPath.lineTo(0.4f, 0.4f);
        giftPath.lineTo(0.4f, 0.3f);
        giftPath.lineTo(-0.1f, 0.3f);
        giftPath.close();
        // 丝带
        giftPath.moveTo(0.15f, 0.3f);
        giftPath.lineTo(0.15f, 0.7f);
    }

    /**
     * 开始礼花动画
     */
    public void startFireworks() {
        if (isAnimating) {
            return;
        }

        isAnimating = true;
        createParticles();

        animator = ValueAnimator.ofFloat(0f, 1f);
        animator.setDuration(3000); // 3秒动画
        animator.setInterpolator(new AccelerateDecelerateInterpolator());
        animator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
            @Override
            public void onAnimationUpdate(ValueAnimator animation) {
                float progress = (float) animation.getAnimatedValue();
                updateParticles(progress);
                invalidate();
            }
        });
        animator.addListener(new AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(Animator animation) {
                isAnimating = false;
                if (onFireworksEndListener != null) {
                    onFireworksEndListener.onFireworksEnd();
                }
            }
        });
        animator.start();
    }

    /**
     * 创建礼花粒子
     */
    private void createParticles() {
        particles.clear();

        // 创建多个礼花中心点（屏幕不同位置）
        int centerX = getWidth() / 2;
        int centerY = getHeight() / 2;

        // 创建5-8个礼花中心
        int fireworkCount = 5 + random.nextInt(4);
        for (int f = 0; f < fireworkCount; f++) {
            // 随机礼花中心位置
            int fx = centerX + (random.nextInt(getWidth()) - centerX) / 2;
            int fy = centerY + (random.nextInt(getHeight()) - centerY) / 2;

            // 每个礼花包含15-25个礼物粒子
            int particleCount = 15 + random.nextInt(11);
            for (int i = 0; i < particleCount; i++) {
                FireworkParticle particle = new FireworkParticle();
                particle.x = fx;
                particle.y = fy;
                particle.startX = fx;
                particle.startY = fy;

                // 随机角度（0-360度）
                double angle = (random.nextDouble() * Math.PI * 2);
                // 随机距离（屏幕宽度的20%-60%）
                float distance = (getWidth() * 0.2f) + (random.nextFloat() * getWidth() * 0.4f);

                particle.targetX = fx + (float) (Math.cos(angle) * distance);
                particle.targetY = fy + (float) (Math.sin(angle) * distance);

                // 随机颜色
                particle.color = FIREWORK_COLORS[random.nextInt(FIREWORK_COLORS.length)];

                // 随机大小（20-40dp）
                float density = getResources().getDisplayMetrics().density;
                particle.size = 20 + random.nextInt(21);
                particle.size *= density;

                // 随机旋转角度
                particle.rotation = random.nextFloat() * 360;
                particle.rotationSpeed = (random.nextFloat() - 0.5f) * 10;

                // 随机延迟（0-0.5）
                particle.delay = random.nextFloat() * 0.5f;

                particles.add(particle);
            }
        }
    }

    /**
     * 更新粒子位置
     */
    private void updateParticles(float progress) {
        for (FireworkParticle particle : particles) {
            // 考虑延迟
            float effectiveProgress = Math.max(0, Math.min(1, (progress - particle.delay) / (1 - particle.delay)));

            // 使用缓动函数
            float easedProgress = easeOutCubic(effectiveProgress);

            // 更新位置
            particle.currentX = particle.startX + (particle.targetX - particle.startX) * easedProgress;
            particle.currentY = particle.startY + (particle.targetY - particle.startY) * easedProgress;

            // 更新旋转
            particle.currentRotation = particle.rotation + particle.rotationSpeed * progress * 360;

            // 更新透明度（动画结束时淡出）
            if (progress > 0.8f) {
                particle.alpha = 1 - ((progress - 0.8f) / 0.2f);
            } else {
                particle.alpha = 1;
            }

            // 更新缩放（从小到大）
            particle.scale = Math.min(1, effectiveProgress * 1.5f);
        }
    }

    /**
     * 缓出三次函数
     */
    private float easeOutCubic(float t) {
        return 1 - (float) Math.pow(1 - t, 3);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // 绘制所有礼物粒子
        for (FireworkParticle particle : particles) {
            drawGift(canvas, particle);
        }
    }

    /**
     * 绘制单个礼物
     */
    private void drawGift(Canvas canvas, FireworkParticle particle) {
        canvas.save();

        // 移动到粒子位置
        canvas.translate(particle.currentX, particle.currentY);

        // 应用旋转
        canvas.rotate(particle.currentRotation);

        // 应用缩放
        canvas.scale(particle.scale, particle.scale);

        // 设置透明度
        int alpha = (int) (particle.alpha * 255);
        paint.setAlpha(alpha);
        paint.setColor(particle.color);

        // 绘制礼物（使用简化形状）
        float size = particle.size;
        canvas.drawRect(-size/2, -size/4, size/2, size/4, paint);
        canvas.drawRect(-size/3, -size/2, size/3, -size/4, paint);
        // 丝带
        paint.setColor(0xFFFFFFFF);
        canvas.drawRect(-size/10, -size/4, size/10, size/4, paint);
        canvas.drawRect(-size/2, -size/3, size/2, -size/4 + size/30, paint);

        canvas.restore();
    }

    /**
     * 停止动画
     */
    public void stopFireworks() {
        if (animator != null && animator.isRunning()) {
            animator.cancel();
        }
        isAnimating = false;
        particles.clear();
        invalidate();
    }

    /**
     * 礼花粒子类
     */
    private static class FireworkParticle {
        float x, y;
        float startX, startY;
        float targetX, targetY;
        float currentX, currentY;
        int color;
        float size;
        float rotation;
        float rotationSpeed;
        float currentRotation;
        float delay;
        float alpha;
        float scale;
    }

    /**
     * 礼花结束监听器
     */
    public interface OnFireworksEndListener {
        void onFireworksEnd();
    }

    private OnFireworksEndListener onFireworksEndListener;

    public void setOnFireworksEndListener(OnFireworksEndListener listener) {
        this.onFireworksEndListener = listener;
    }
}
