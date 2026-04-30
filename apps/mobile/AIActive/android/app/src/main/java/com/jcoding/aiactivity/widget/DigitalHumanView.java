package com.jcoding.aiactivity.widget;

import android.content.Context;
import android.graphics.Matrix;
import android.media.MediaPlayer;
import android.net.Uri;
import android.util.AttributeSet;
import android.util.Log;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.TextureView;
import android.widget.FrameLayout;
import android.widget.ImageView;

import androidx.annotation.Nullable;

import com.jcoding.aiactivity.manager.ConfigManager;

import java.io.File;

/**
 * Digital Human View Component
 * Supports drag and pinch-to-zoom
 */
public class DigitalHumanView extends FrameLayout {

    private static final String TAG = "DigitalHumanView";

    // Video views
    private TextureView shutupVideoView;  // Shut up video
    private TextureView talkVideoView;    // Talking video

    // Backup image views (used for GIF display when video fails)
    private ImageView shutupImageView;
    private ImageView talkImageView;

    // Media players
    private MediaPlayer shutupMediaPlayer;
    private MediaPlayer talkMediaPlayer;

    // Gesture detectors
    private ScaleGestureDetector scaleGestureDetector;
    private GestureDetector gestureDetector;

    // Transform matrix
    private Matrix matrix = new Matrix();
    private float scale = 1.0f;
    private float lastScale = 1.0f;

    // Position info
    private float posX = 0;
    private float posY = 0;
    private float lastTouchX;
    private float lastTouchY;

    // Digital human ID
    private String digitalHumanId;

    // Module ID (quiz, lottery, inner, etc.)
    private String moduleId;

    // Is currently talking
    private boolean isTalking = false;

    // Enable drag and scale (default false = locked state)
    private boolean isDragAndScaleEnabled = false;

    // Whether restoring state (prevent duplicate restore)
    private boolean isRestoringState = false;

    // Triple tap callback interface
    private TripleTapListener tripleTapListener;

    /**
     * Triple tap callback interface
     */
    public interface TripleTapListener {
        void onDigitalHumanTap();
    }

    /**
     * Set triple tap listener
     */
    public void setTripleTapListener(TripleTapListener listener) {
        this.tripleTapListener = listener;
    }

    public DigitalHumanView(Context context) {
        super(context);
        init(context);
    }

    public DigitalHumanView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    public DigitalHumanView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init(context);
    }

    private void init(Context context) {
        // Initialize video views
        shutupVideoView = new TextureView(context);
        talkVideoView = new TextureView(context);

        shutupImageView = new ImageView(context);
        talkImageView = new ImageView(context);

        // Add all views to the layout
        LayoutParams params = new LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT
        );
        addView(shutupVideoView, params);
        addView(talkVideoView, params);
        addView(shutupImageView, params);
        addView(talkImageView, params);

        // Initially hide all views
        shutupVideoView.setVisibility(GONE);
        talkVideoView.setVisibility(GONE);
        shutupImageView.setVisibility(GONE);
        talkImageView.setVisibility(GONE);

        // Initialize gesture detectors
        scaleGestureDetector = new ScaleGestureDetector(context, new ScaleListener());
        gestureDetector = new GestureDetector(context, new GestureListener());
    }

    /**
     * Load digital human
     * @param digitalHumanId Digital human ID (e.g., "JC2026012100001")
     */
    public void loadDigitalHuman(String digitalHumanId) {
        this.digitalHumanId = digitalHumanId;
        Log.d(TAG, "loadDigitalHuman: " + digitalHumanId);

        // First try GIF animation
        loadGifAnimation(digitalHumanId);
    }

    /**
     * Load GIF animation
     */
    private void loadGifAnimation(String digitalHumanId) {
        // Get default GIF path from DigitalHumanManager and load it
        // Note: config.json already contains full path like "aibeing/JC2026012100001/10.gif"
        com.jcoding.aiactivity.manager.DigitalHumanManager manager = com.jcoding.aiactivity.manager.DigitalHumanManager.getInstance(getContext());
        String gifPath = manager.getDefaultGif();
        // Construct full path to assets (config already has the full path)
        String fullGifPath = "file:///android_asset/" + gifPath;
        setDigitalHumanGif(fullGifPath, false);
    }

    /**
     * Set digital human GIF
     */
    public void setDigitalHumanGif(String gifPath, boolean isTalking) {
        Log.d(TAG, "setDigitalHumanGif: " + gifPath + ", isTalking=" + isTalking);

        // Extract asset path from file:///android_asset/ URI
        String assetPath = gifPath.replace("file:///android_asset/", "");
        Log.d(TAG, "Extracted asset path: " + assetPath);

        // Copy GIF to cache and load it
        copyGifToCacheAndLoad(assetPath, isTalking);
    }

    /**
     * Copy GIF from assets to cache directory and load it
     */
    private void copyGifToCacheAndLoad(String assetPath, boolean isTalking) {
        Log.d(TAG, "Starting background thread to copy GIF: " + assetPath);
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Log.d(TAG, "Opening asset file: " + assetPath);
                    // Open asset file
                    java.io.InputStream is = getContext().getAssets().open(assetPath);
                    java.io.File tempFile = new java.io.File(getContext().getCacheDir(), "digital_human_" + System.currentTimeMillis() + ".gif");
                    Log.d(TAG, "Temp file path: " + tempFile.getAbsolutePath());

                    // Copy to cache
                    java.io.FileOutputStream fos = new java.io.FileOutputStream(tempFile);
                    byte[] buffer = new byte[8192];
                    int len;
                    long totalBytes = 0;
                    while ((len = is.read(buffer)) != -1) {
                        fos.write(buffer, 0, len);
                        totalBytes += len;
                    }
                    fos.close();
                    is.close();
                    Log.d(TAG, "GIF copied to cache: " + totalBytes + " bytes");

                    // Load on UI thread
                    final String cachePath = tempFile.getAbsolutePath();
                    Log.d(TAG, "Posting to UI thread to load GIF: " + cachePath);
                    post(new Runnable() {
                        @Override
                        public void run() {
                            Log.d(TAG, "Loading GIF into ImageView, isTalking=" + isTalking);
                            if (isTalking) {
                                com.bumptech.glide.Glide.with(getContext())
                                        .asGif()
                                        .load(new java.io.File(cachePath))
                                        .into(talkImageView);
                                showTalkView();
                            } else {
                                com.bumptech.glide.Glide.with(getContext())
                                        .asGif()
                                        .load(new java.io.File(cachePath))
                                        .into(shutupImageView);
                                showShutupView();
                            }
                            Log.d(TAG, "GIF load request submitted to Glide");
                        }
                    });

                } catch (Exception e) {
                    Log.e(TAG, "Error loading GIF from assets: " + assetPath, e);
                }
            }
        }).start();
    }

    /**
     * Show shut up view
     */
    private void showShutupView() {
        post(new Runnable() {
            @Override
            public void run() {
                shutupVideoView.setVisibility(GONE);
                talkVideoView.setVisibility(GONE);

                shutupImageView.setVisibility(GONE);
                talkImageView.setVisibility(GONE);

                shutupImageView.setVisibility(VISIBLE);
                isTalking = false;
            }
        });
    }

    /**
     * Show talking view
     */
    private void showTalkView() {
        post(new Runnable() {
            @Override
            public void run() {
                shutupVideoView.setVisibility(GONE);
                talkVideoView.setVisibility(GONE);

                shutupImageView.setVisibility(GONE);
                talkImageView.setVisibility(GONE);

                talkImageView.setVisibility(VISIBLE);
                isTalking = true;
            }
        });
    }

    /**
     * Start talking animation
     */
    public void startTalking() {
        Log.d(TAG, "startTalking");
        isTalking = true;
        // Update GIF based on state
        // The actual GIF switching is handled by DigitalHumanManager
    }

    /**
     * Stop talking animation
     */
    public void stopTalking() {
        Log.d(TAG, "stopTalking");
        isTalking = false;
    }

    /**
     * Enable or disable drag and scale
     * @param enabled true=enable, false=disable
     */
    public void setDragAndScaleEnabled(boolean enabled) {
        this.isDragAndScaleEnabled = enabled;
        Log.d(TAG, "Drag and scale: " + (enabled ? "ENABLED" : "DISABLED"));
    }

    /**
     * Get whether drag and scale is enabled
     * @return true=enabled, false=disabled
     */
    public boolean isDragAndScaleEnabled() {
        return isDragAndScaleEnabled;
    }

    /**
     * Set module ID
     */
    public void setModuleId(String moduleId) {
        this.moduleId = moduleId;
    }

    /**
     * Handle touch event
     */
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // If drag and scale is disabled, don't handle touch events
        if (!isDragAndScaleEnabled) {
            return false;
        }

        scaleGestureDetector.onTouchEvent(event);
        gestureDetector.onTouchEvent(event);

        switch (event.getAction() & MotionEvent.ACTION_MASK) {
            case MotionEvent.ACTION_DOWN:
                lastTouchX = event.getX();
                lastTouchY = event.getY();
                break;

            case MotionEvent.ACTION_MOVE:
                if (!scaleGestureDetector.isInProgress()) {
                    float dx = event.getX() - lastTouchX;
                    float dy = event.getY() - lastTouchY;

                    posX += dx;
                    posY += dy;

                    setX(posX);
                    setY(posY);
                }
                break;

            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                // Save position after drag
                saveDigitalHumanState();
                break;
        }

        return true;
    }

    /**
     * Scale gesture listener
     */
    private class ScaleListener extends ScaleGestureDetector.SimpleOnScaleGestureListener {
        @Override
        public boolean onScale(ScaleGestureDetector detector) {
            float scaleFactor = detector.getScaleFactor();

            // Only allow zoom in (scale up), no zoom out
            if (scaleFactor < 1.0f) {
                scaleFactor = 1.0f;
            }

            // Apply scale limit
            float newScale = scale * scaleFactor;
            // Allow 3x default zoom in limit (based on moduleId)
            float maxScale = 3.0f;
            if ("aishow".equals(moduleId)) {
                maxScale = Float.MAX_VALUE; // Unlimited zoom for aishow
            }
            scale = Math.min(newScale, maxScale);
            scale = Math.max(0.5f, scale);

            setScaleX(scale);
            setScaleY(scale);

            return true;
        }

        @Override
        public void onScaleEnd(ScaleGestureDetector detector) {
            lastScale = scale;
            // Save state after scale
            saveDigitalHumanState();
        }
    }

    /**
     * Gesture listener
     */
    private class GestureListener extends GestureDetector.SimpleOnGestureListener {
        @Override
        public boolean onSingleTapConfirmed(android.view.MotionEvent e) {
            // Single tap: triple tap to enable drag
            if (tripleTapListener != null) {
                tripleTapListener.onDigitalHumanTap();
            }
            return true;
        }

        @Override
        public boolean onDoubleTap(android.view.MotionEvent e) {
            // Double tap: reset to default scale
            scale = 1.0f;
            lastScale = 1.0f;
            setScaleX(scale);
            setScaleY(scale);
            Log.d(TAG, "Double tap: reset scale to 1.0");
            return true;
        }

        @Override
        public void onLongPress(android.view.MotionEvent e) {
            // Long press: enable drag and scale
            if (!isDragAndScaleEnabled) {
                setDragAndScaleEnabled(true);
                Log.d(TAG, "Long press: enabled drag and scale");
            }
        }
    }

    /**
     * Save digital human state to SharedPreferences
     */
    private void saveDigitalHumanState() {
        com.jcoding.aiactivity.utils.PreferenceUtils.putFloat(getContext(), "digital_human_scale", scale);
        com.jcoding.aiactivity.utils.PreferenceUtils.putFloat(getContext(), "digital_human_x", posX);
        com.jcoding.aiactivity.utils.PreferenceUtils.putFloat(getContext(), "digital_human_y", posY);
        com.jcoding.aiactivity.utils.PreferenceUtils.putBoolean(getContext(), "digital_human_enabled", isDragAndScaleEnabled);
        Log.d(TAG, "State saved: scale=" + scale + ", pos=(" + posX + "," + posY + "), enabled=" + isDragAndScaleEnabled);
    }

    /**
     * Restore digital human state from SharedPreferences
     */
    public void restoreDigitalHumanState() {
        if (isRestoringState) {
            return;
        }

        isRestoringState = true;

        scale = com.jcoding.aiactivity.utils.PreferenceUtils.getFloat(getContext(), "digital_human_scale", 1.0f);
        posX = com.jcoding.aiactivity.utils.PreferenceUtils.getFloat(getContext(), "digital_human_x", 0f);
        posY = com.jcoding.aiactivity.utils.PreferenceUtils.getFloat(getContext(), "digital_human_y", 0f);
        isDragAndScaleEnabled = com.jcoding.aiactivity.utils.PreferenceUtils.getBoolean(getContext(), "digital_human_enabled", false);

        setScaleX(scale);
        setScaleY(scale);
        setX(posX);
        setY(posY);
        setDragAndScaleEnabled(isDragAndScaleEnabled);

        Log.d(TAG, "State restored: scale=" + scale + ", pos=(" + posX + "," + posY + "), enabled=" + isDragAndScaleEnabled);

        isRestoringState = false;
    }

    /**
     * Release media players
     */
    private void releaseMediaPlayer() {
        if (shutupMediaPlayer != null) {
            shutupMediaPlayer.release();
            shutupMediaPlayer = null;
        }

        if (talkMediaPlayer != null) {
            talkMediaPlayer.release();
            talkMediaPlayer = null;
        }
    }
}
