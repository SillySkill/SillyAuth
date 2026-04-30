package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;

/**
 * 数字人手势辅助类
 * 处理数字人的拖拽、缩放、双击等手势操作
 */
public class DigitalHumanGestureHelper {

    private View containerView;
    private ImageView imageView;
    private Context context;

    // 拖拽相关
    private float dX, dY;
    private float lastX, lastY;
    private boolean isDragging = false;

    // 缩放相关
    private ScaleGestureDetector scaleGestureDetector;
    private float scaleFactor = 1.0f;
    private float minScale = 0.5f;
    private float maxScale = 3.0f;

    // 双击相关
    private android.view.GestureDetector gestureDetector;
    private long lastClickTime = 0;
    private static final long DOUBLE_CLICK_TIME_DELTA = 300;

    // 边界限制
    private int parentWidth, parentHeight;

    // 回调接口
    public interface GestureCallback {
        void onDragStart();
        void onDragEnd();
        void onScaleChanged(float scale);
        void onDoubleClick();
    }

    private GestureCallback callback;

    /**
     * 构造函数
     * @param containerView 数字人容器视图
     * @param imageView 数字人ImageView
     * @param context 上下文
     */
    public DigitalHumanGestureHelper(View containerView, ImageView imageView, Context context) {
        this.containerView = containerView;
        this.imageView = imageView;
        this.context = context;

        initGestureDetectors();
        setupTouchListeners();
    }

    /**
     * 设置手势回调
     */
    public void setGestureCallback(GestureCallback callback) {
        this.callback = callback;
    }

    /**
     * 设置缩放范围
     */
    public void setScaleRange(float minScale, float maxScale) {
        this.minScale = minScale;
        this.maxScale = maxScale;
    }

    /**
     * 初始化手势检测器
     */
    private void initGestureDetectors() {
        // 缩放手势检测器
        scaleGestureDetector = new ScaleGestureDetector(context,
            new ScaleGestureDetector.SimpleOnScaleGestureListener() {
                @Override
                public boolean onScale(ScaleGestureDetector detector) {
                    float newScale = scaleFactor * detector.getScaleFactor();

                    // 限制缩放范围
                    newScale = Math.max(minScale, Math.min(newScale, maxScale));

                    if (newScale != scaleFactor) {
                        scaleFactor = newScale;
                        applyScale();

                        if (callback != null) {
                            callback.onScaleChanged(scaleFactor);
                        }
                    }
                    return true;
                }

                @Override
                public boolean onScaleBegin(ScaleGestureDetector detector) {
                    return true;
                }

                @Override
                public void onScaleEnd(ScaleGestureDetector detector) {
                    super.onScaleEnd(detector);
                }
            });

        // 双击和长按手势检测器
        gestureDetector = new android.view.GestureDetector(context,
            new android.view.GestureDetector.SimpleOnGestureListener() {
                @Override
                public boolean onDoubleTap(android.view.MotionEvent e) {
                    handleDoubleClick();
                    return true;
                }

                @Override
                public boolean onSingleTapConfirmed(android.view.MotionEvent e) {
                    return false;
                }

                @Override
                public void onLongPress(android.view.MotionEvent e) {
                    // 长按可以触发特殊功能，例如恢复默认大小
                    resetToDefault();
                }
            });
    }

    /**
     * 设置触摸监听器
     */
    private void setupTouchListeners() {
        containerView.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, android.view.MotionEvent event) {
                // 先让缩放检测器处理
                scaleGestureDetector.onTouchEvent(event);
                gestureDetector.onTouchEvent(event);

                // 如果正在缩放，不处理拖拽
                if (scaleGestureDetector.isInProgress()) {
                    return true;
                }

                switch (event.getAction()) {
                    case android.view.MotionEvent.ACTION_DOWN:
                        handleActionDown(event);
                        return true;

                    case android.view.MotionEvent.ACTION_MOVE:
                        if (isDragging) {
                            handleActionMove(event);
                            return true;
                        }
                        break;

                    case android.view.MotionEvent.ACTION_UP:
                    case android.view.MotionEvent.ACTION_CANCEL:
                        handleActionUp();
                        return true;
                }

                return false;
            }
        });
    }

    /**
     * 处理按下事件
     */
    private void handleActionDown(android.view.MotionEvent event) {
        dX = containerView.getX() - event.getRawX();
        dY = containerView.getY() - event.getRawY();
        lastX = event.getRawX();
        lastY = event.getRawY();
        isDragging = false;

        // 获取父视图尺寸用于边界检查
        if (containerView.getParent() instanceof View) {
            View parent = (View) containerView.getParent();
            parentWidth = parent.getWidth();
            parentHeight = parent.getHeight();
        }
    }

    /**
     * 处理移动事件
     */
    private void handleActionMove(android.view.MotionEvent event) {
        float deltaX = Math.abs(event.getRawX() - lastX);
        float deltaY = Math.abs(event.getRawY() - lastY);

        // 判断是否开始拖拽（移动距离超过阈值）
        if (!isDragging && (deltaX > 10 || deltaY > 10)) {
            isDragging = true;
            if (callback != null) {
                callback.onDragStart();
            }
        }

        if (isDragging) {
            float newX = event.getRawX() + dX;
            float newY = event.getRawY() + dY;

            // 应用边界限制
            newX = constrainX(newX);
            newY = constrainY(newY);

            containerView.setX(newX);
            containerView.setY(newY);

            lastX = event.getRawX();
            lastY = event.getRawY();
        }
    }

    /**
     * 处理抬起事件
     */
    private void handleActionUp() {
        if (isDragging) {
            isDragging = false;
            if (callback != null) {
                callback.onDragEnd();
            }
        }
    }

    /**
     * 处理双击事件
     */
    private void handleDoubleClick() {
        long clickTime = System.currentTimeMillis();
        if (clickTime - lastClickTime < DOUBLE_CLICK_TIME_DELTA) {
            // 双击切换大小
            if (scaleFactor > 1.5f) {
                // 缩小到默认大小
                scaleFactor = 1.0f;
            } else {
                // 放大到1.5倍
                scaleFactor = 1.5f;
            }
            applyScale();

            if (callback != null) {
                callback.onDoubleClick();
            }
        }
        lastClickTime = clickTime;
    }

    /**
     * 应用缩放
     */
    private void applyScale() {
        imageView.setScaleX(scaleFactor);
        imageView.setScaleY(scaleFactor);
    }

    /**
     * X坐标边界限制
     */
    private float constrainX(float x) {
        float viewWidth = containerView.getWidth();
        float minX = -viewWidth * (scaleFactor - 1) / 2;
        float maxX = parentWidth - viewWidth + viewWidth * (scaleFactor - 1) / 2;
        return Math.max(minX, Math.min(x, maxX));
    }

    /**
     * Y坐标边界限制
     */
    private float constrainY(float y) {
        float viewHeight = containerView.getHeight();
        float minY = -viewHeight * (scaleFactor - 1) / 2;
        float maxY = parentHeight - viewHeight + viewHeight * (scaleFactor - 1) / 2;
        return Math.max(minY, Math.min(y, maxY));
    }

    /**
     * 重置到默认状态
     */
    public void resetToDefault() {
        scaleFactor = 1.0f;
        applyScale();

        // 重置位置到初始位置（右下角）
        FrameLayout.LayoutParams params = (FrameLayout.LayoutParams) containerView.getLayoutParams();
        containerView.setX(0);
        containerView.setY(0);

        if (callback != null) {
            callback.onScaleChanged(1.0f);
        }
    }

    /**
     * 获取当前缩放比例
     */
    public float getScaleFactor() {
        return scaleFactor;
    }

    /**
     * 设置缩放比例
     */
    public void setScaleFactor(float scale) {
        this.scaleFactor = Math.max(minScale, Math.min(scale, maxScale));
        applyScale();

        if (callback != null) {
            callback.onScaleChanged(this.scaleFactor);
        }
    }

    /**
     * 释放资源
     */
    public void release() {
        if (containerView != null) {
            containerView.setOnTouchListener(null);
        }
        callback = null;
    }
}
