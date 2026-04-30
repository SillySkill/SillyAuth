package com.jcoding.aiactivity.opengl;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.util.Log;

/**
 * 卡片纹理生成器
 * 用于生成带有文字和背景的卡片位图
 */
public class CardTextureGenerator {

    private static final String TAG = "CardTextureGenerator";

    private Context context;
    private int cardWidth = 256;
    private int cardHeight = 384;

    // 默认颜色
    private int backgroundColor = Color.parseColor("#FF6B9D");
    private int textColor = Color.WHITE;
    private float textSize = 48f;

    public CardTextureGenerator(Context context) {
        this.context = context;
    }

    /**
     * 生成卡片位图
     * @param text 卡片文字
     * @return 生成的位图
     */
    public Bitmap generateCard(String text) {
        Bitmap bitmap = Bitmap.createBitmap(cardWidth, cardHeight, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);

        // 绘制背景
        Paint bgPaint = new Paint();
        bgPaint.setColor(backgroundColor);
        bgPaint.setStyle(Paint.Style.FILL);
        canvas.drawRoundRect(0, 0, cardWidth, cardHeight, 20, 20, bgPaint);

        // 绘制边框
        Paint borderPaint = new Paint();
        borderPaint.setColor(Color.WHITE);
        borderPaint.setStyle(Paint.Style.STROKE);
        borderPaint.setStrokeWidth(4);
        canvas.drawRoundRect(2, 2, cardWidth - 2, cardHeight - 2, 20, 20, borderPaint);

        // 绘制文字
        Paint textPaint = new Paint();
        textPaint.setColor(textColor);
        textPaint.setTextSize(textSize);
        textPaint.setAntiAlias(true);
        textPaint.setTextAlign(Paint.Align.CENTER);

        // 计算文字位置（居中）
        Rect textBounds = new Rect();
        textPaint.getTextBounds(text, 0, text.length(), textBounds);
        float x = cardWidth / 2f;
        float y = (cardHeight - textBounds.height()) / 2f + textBounds.height();

        // 如果文字太宽，缩小字号
        while (textBounds.width() > cardWidth - 40) {
            textPaint.setTextSize(textPaint.getTextSize() * 0.9f);
            textPaint.getTextBounds(text, 0, text.length(), textBounds);
        }

        canvas.drawText(text, x, y, textPaint);

        return bitmap;
    }

    /**
     * 生成奖品卡片
     * @param prizeName 奖品名称
     * @param color 背景颜色
     * @return 生成的位图
     */
    public Bitmap generatePrizeCard(String prizeName, int color) {
        int originalColor = backgroundColor;
        backgroundColor = color;
        Bitmap bitmap = generateCard(prizeName);
        backgroundColor = originalColor;
        return bitmap;
    }

    /**
     * 批量生成人员卡片
     * @param names 人员姓名列表
     * @return 位图列表
     */
    public Bitmap[] generatePersonCards(String[] names) {
        Bitmap[] bitmaps = new Bitmap[names.length];
        for (int i = 0; i < names.length; i++) {
            bitmaps[i] = generateCard(names[i]);
        }
        return bitmaps;
    }

    /**
     * 设置卡片尺寸
     */
    public void setCardSize(int width, int height) {
        this.cardWidth = width;
        this.cardHeight = height;
    }

    /**
     * 设置背景颜色
     */
    public void setBackgroundColor(int color) {
        this.backgroundColor = color;
    }

    /**
     * 设置文字颜色
     */
    public void setTextColor(int color) {
        this.textColor = color;
    }

    /**
     * 设置文字大小
     */
    public void setTextSize(float size) {
        this.textSize = size;
    }

    /**
     * 回收位图
     */
    public static void recycleBitmaps(Bitmap[] bitmaps) {
        if (bitmaps == null) return;
        for (Bitmap bitmap : bitmaps) {
            if (bitmap != null && !bitmap.isRecycled()) {
                bitmap.recycle();
            }
        }
    }
}
