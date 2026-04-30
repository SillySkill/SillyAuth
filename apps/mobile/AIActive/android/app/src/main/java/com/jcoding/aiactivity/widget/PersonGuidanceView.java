package com.jcoding.aiactivity.widget;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.util.AttributeSet;
import android.view.View;

import androidx.core.content.ContextCompat;

import com.jcoding.aiactivity.R;

/**
 * 人形轮廓引导框
 * 在相机预览上绘制半透明的人形轮廓，引导用户站位
 */
public class PersonGuidanceView extends View {

    private Paint outlinePaint;
    private Paint fillPaint;
    private Paint shoulderPaint;
    private Path headPath;
    private Path bodyPath;
    private Path shoulderPath;

    // 引导框配置（占屏幕约70%）
    private float headRadiusRatio = 0.12f; // 头部半径占屏幕宽度的比例
    private float shoulderWidthRatio = 0.55f; // 肩宽占屏幕宽度的比例（约70%）
    private float bodyHeightRatio = 0.65f; // 身体高度占屏幕高度的比例
    private float centerX;
    private float centerY;

    public PersonGuidanceView(Context context) {
        super(context);
        init();
    }

    public PersonGuidanceView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public PersonGuidanceView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        // 初始化轮廓画笔（60%透明度）
        outlinePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        outlinePaint.setColor(ContextCompat.getColor(getContext(), R.color.guidance_outline));
        outlinePaint.setStyle(Paint.Style.STROKE);
        outlinePaint.setStrokeWidth(8f);
        outlinePaint.setAlpha(153); // 60%透明度 (255 * 0.6 = 153)

        // 初始化填充画笔（20%透明度，淡淡的填充）
        fillPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        fillPaint.setColor(ContextCompat.getColor(getContext(), R.color.guidance_fill));
        fillPaint.setStyle(Paint.Style.FILL);
        fillPaint.setAlpha(51); // 20%透明度 (255 * 0.2 = 51)

        // 初始化肩线画笔（80%透明度）
        shoulderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        shoulderPaint.setColor(ContextCompat.getColor(getContext(), R.color.guidance_shoulder));
        shoulderPaint.setStyle(Paint.Style.STROKE);
        shoulderPaint.setStrokeWidth(12f);
        shoulderPaint.setAlpha(204); // 80%透明度 (255 * 0.8 = 204)
        shoulderPaint.setStrokeCap(Paint.Cap.ROUND);

        headPath = new Path();
        bodyPath = new Path();
        shoulderPath = new Path();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);

        centerX = w / 2f;
        centerY = h / 2f;

        float scale = Math.min(w, h);
        float headRadius = scale * headRadiusRatio;
        float bodyWidth = w * shoulderWidthRatio;
        float bodyHeight = h * bodyHeightRatio;

        // 创建头部圆形路径
        headPath.reset();
        headPath.addCircle(centerX, centerY - bodyHeight * 0.35f, headRadius, Path.Direction.CW);

        // 创建人形身体路径（更真实的轮廓）
        bodyPath.reset();

        // 肩膀和躯干上部
        float shoulderY = centerY - bodyHeight * 0.2f;
        float shoulderX = centerX - bodyWidth * 0.42f; // 左肩
        bodyPath.moveTo(shoulderX, shoulderY);

        // 左臂外侧曲线
        float leftArmX = centerX - bodyWidth * 0.48f;
        bodyPath.quadTo(leftArmX, centerY - bodyHeight * 0.05f,
                        centerX - bodyWidth * 0.35f, centerY + bodyHeight * 0.1f);

        // 左腰
        float leftWaistX = centerX - bodyWidth * 0.32f;
        bodyPath.quadTo(leftWaistX, centerY + bodyHeight * 0.15f,
                        centerX - bodyWidth * 0.28f, centerY + bodyHeight * 0.25f);

        // 臀部左侧
        bodyPath.quadTo(centerX - bodyWidth * 0.35f, centerY + bodyHeight * 0.3f,
                        centerX, centerY + bodyHeight * 0.32f);

        // 臀部右侧（镜像）
        bodyPath.quadTo(centerX + bodyWidth * 0.35f, centerY + bodyHeight * 0.3f,
                        centerX + bodyWidth * 0.28f, centerY + bodyHeight * 0.25f);

        // 右腰
        float rightWaistX = centerX + bodyWidth * 0.32f;
        bodyPath.quadTo(rightWaistX, centerY + bodyHeight * 0.15f,
                        centerX + bodyWidth * 0.35f, centerY + bodyHeight * 0.1f);

        // 右臂外侧曲线
        float rightArmX = centerX + bodyWidth * 0.48f;
        bodyPath.quadTo(rightArmX, centerY - bodyHeight * 0.05f,
                        centerX + bodyWidth * 0.42f, shoulderY);

        // 右肩到颈部
        bodyPath.quadTo(centerX + bodyWidth * 0.38f, shoulderY - bodyHeight * 0.05f,
                        centerX, shoulderY - bodyHeight * 0.08f);

        // 颈部左侧
        bodyPath.quadTo(centerX - bodyWidth * 0.38f, shoulderY - bodyHeight * 0.05f,
                        shoulderX, shoulderY);

        bodyPath.close();

        // 创建肩线路径（虚线效果，更明显）
        shoulderPath.reset();
        float dashLength = 20f;
        float gapLength = 15f;
        float shoulderLineWidth = bodyWidth * 0.84f;
        float shoulderYLine = centerY - bodyHeight * 0.18f;

        // 绘制多条虚线表示肩膀位置
        for (float i = 0; i < 5; i++) {
            float startX = centerX - shoulderLineWidth / 2 + i * (shoulderLineWidth / 4);
            shoulderPath.moveTo(startX, shoulderYLine);
            shoulderPath.lineTo(Math.min(startX + dashLength, centerX + shoulderLineWidth / 2), shoulderYLine);
        }
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // 绘制身体填充（淡色）
        canvas.drawPath(bodyPath, fillPaint);

        // 绘制头部轮廓
        canvas.drawPath(headPath, outlinePaint);

        // 绘制身体轮廓
        canvas.drawPath(bodyPath, outlinePaint);

        // 绘制肩部虚线（更明显的引导线）
        canvas.drawPath(shoulderPath, shoulderPaint);

        // 绘制四个角落的引导点
        drawCornerGuides(canvas);
    }

    /**
     * 绘制四角引导点
     */
    private void drawCornerGuides(Canvas canvas) {
        float margin = Math.min(getWidth(), getHeight()) * 0.1f;
        float cornerSize = 20f;
        float lineWidth = 40f;

        Paint cornerPaint = new Paint(outlinePaint);
        cornerPaint.setStrokeWidth(6f);
        cornerPaint.setAlpha(255);

        // 左上角
        canvas.drawLine(margin, margin + lineWidth, margin, margin + cornerSize, cornerPaint);
        canvas.drawLine(margin, margin, margin + lineWidth, margin, cornerPaint);

        // 右上角
        canvas.drawLine(getWidth() - margin - lineWidth, margin, getWidth() - margin - cornerSize, margin, cornerPaint);
        canvas.drawLine(getWidth() - margin, margin, getWidth() - margin, margin + lineWidth, cornerPaint);

        // 左下角
        canvas.drawLine(margin, getHeight() - margin - lineWidth, margin, getHeight() - margin - cornerSize, cornerPaint);
        canvas.drawLine(margin, getHeight() - margin, margin + lineWidth, getHeight() - margin, cornerPaint);

        // 右下角
        canvas.drawLine(getWidth() - margin - lineWidth, getHeight() - margin, getWidth() - margin - cornerSize, getHeight() - margin, cornerPaint);
        canvas.drawLine(getWidth() - margin, getHeight() - margin - lineWidth, getWidth() - margin, getHeight() - margin - cornerSize, cornerPaint);
    }

    /**
     * 设置头部半径比例
     */
    public void setHeadRadiusRatio(float ratio) {
        this.headRadiusRatio = ratio;
        requestLayout();
        invalidate();
    }

    /**
     * 设置肩宽比例
     */
    public void setShoulderWidthRatio(float ratio) {
        this.shoulderWidthRatio = ratio;
        requestLayout();
        invalidate();
    }

    /**
     * 设置身体高度比例
     */
    public void setBodyHeightRatio(float ratio) {
        this.bodyHeightRatio = ratio;
        requestLayout();
        invalidate();
    }
}
