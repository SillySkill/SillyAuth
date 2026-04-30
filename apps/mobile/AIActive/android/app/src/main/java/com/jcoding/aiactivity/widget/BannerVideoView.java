package com.jcoding.aiactivity.widget;

import android.content.Context;
import android.graphics.SurfaceTexture;
import android.media.MediaPlayer;
import android.net.Uri;
import android.util.AttributeSet;
import android.view.Surface;
import android.view.TextureView;
import android.widget.FrameLayout;

import java.io.File;

/**
 * Banner Video View - uses TextureView + MediaPlayer for better video playback
 */
public class BannerVideoView extends FrameLayout {

    private TextureView textureView;
    private MediaPlayer mediaPlayer;
    private boolean isPrepared = false;
    private boolean shouldLoop = true;
    private boolean shouldAutoStart = false; // 是否在prepared后自动播放
    private Surface mediaSurface; // 保持Surface引用，防止被GC回收

    public BannerVideoView(Context context) {
        super(context);
        init(context);
    }

    public BannerVideoView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    public BannerVideoView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init(context);
    }

    @Override
    public void setVisibility(int visibility) {
        super.setVisibility(visibility);
        android.util.Log.d("BannerVideoView", "setVisibility called: " + visibility + ", VISIBLE=" + VISIBLE);
        if (visibility == VISIBLE && textureView != null) {
            android.util.Log.d("BannerVideoView", "TextureView visibility: " + textureView.getVisibility());
            textureView.setVisibility(VISIBLE);
        }
    }

    private void init(Context context) {
        textureView = new TextureView(context);
        LayoutParams params = new LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT
        );
        addView(textureView, params);

        // 设置透明背景，避免遮挡视频
        setBackgroundColor(android.graphics.Color.TRANSPARENT);
        textureView.setOpaque(false);
        android.util.Log.d("BannerVideoView", "BannerVideoView initialized, background set to TRANSPARENT");

        textureView.setSurfaceTextureListener(new TextureView.SurfaceTextureListener() {
            @Override
            public void onSurfaceTextureAvailable(android.graphics.SurfaceTexture surface, int width, int height) {
                android.util.Log.d("BannerVideoView", "Surface available, size: " + width + "x" + height);
                startMediaPlayer(surface);
            }

            @Override
            public void onSurfaceTextureSizeChanged(android.graphics.SurfaceTexture surface, int width, int height) {
                android.util.Log.d("BannerVideoView", "Surface size changed: " + width + "x" + height);
                updateTextureViewSize();
            }

            @Override
            public boolean onSurfaceTextureDestroyed(android.graphics.SurfaceTexture surface) {
                android.util.Log.d("BannerVideoView", "Surface texture destroyed");
                // 释放MediaPlayer但不要销毁SurfaceTexture（返回false）
                releaseMediaPlayer();
                return false; // 返回false让系统管理SurfaceTexture的生命周期
            }

            @Override
            public void onSurfaceTextureUpdated(android.graphics.SurfaceTexture surface) {
                // 视频帧更新回调
            }
        });
    }

    public void setVideoPath(String path) {
        android.util.Log.d("BannerVideoView", "Setting video path: " + path);

        // 保存视频路径
        this.currentVideoPath = path;

        releaseMediaPlayer();

        mediaPlayer = new MediaPlayer();
        mediaPlayer.setOnPreparedListener(new MediaPlayer.OnPreparedListener() {
            @Override
            public void onPrepared(MediaPlayer mp) {
                android.util.Log.d("BannerVideoView", "MediaPlayer prepared");
                android.util.Log.d("BannerVideoView", "Video size: " + mp.getVideoWidth() + "x" + mp.getVideoHeight());
                android.util.Log.d("BannerVideoView", "View size: " + getWidth() + "x" + getHeight());
                isPrepared = true;
                mp.setLooping(shouldLoop);

                // Use MediaPlayer's built-in scaling instead of custom transform
                mp.setVideoScalingMode(android.media.MediaPlayer.VIDEO_SCALING_MODE_SCALE_TO_FIT_WITH_CROPPING);

                if (shouldAutoStart) {
                    mp.start();
                    android.util.Log.d("BannerVideoView", "Video started with built-in scaling (auto-start)");
                    shouldAutoStart = false; // 重置标志
                } else {
                    android.util.Log.d("BannerVideoView", "Video prepared but not started (waiting for start() call)");
                }
            }
        });

        mediaPlayer.setOnErrorListener(new MediaPlayer.OnErrorListener() {
            @Override
            public boolean onError(MediaPlayer mp, int what, int extra) {
                android.util.Log.e("BannerVideoView", "MediaPlayer error: what=" + what + ", extra=" + extra);
                return false;
            }
        });

        mediaPlayer.setOnCompletionListener(new MediaPlayer.OnCompletionListener() {
            @Override
            public void onCompletion(MediaPlayer mp) {
                android.util.Log.d("BannerVideoView", "Video playback completed, looping=" + shouldLoop);
                if (shouldLoop) {
                    // 确保视频循环播放
                    mp.start();
                    android.util.Log.d("BannerVideoView", "Video restarted for looping");
                }
            }
        });

        try {
            File videoFile = new File(path);
            Uri uri = Uri.fromFile(videoFile);
            mediaPlayer.setDataSource(getContext(), uri);
            mediaPlayer.prepareAsync();
        } catch (Exception e) {
            android.util.Log.e("BannerVideoView", "Error setting data source", e);
        }
    }

    private void startMediaPlayer(android.graphics.SurfaceTexture surfaceTexture) {
        if (mediaPlayer != null && !isPrepared) {
            // 保存Surface引用，防止被GC回收
            if (mediaSurface != null) {
                mediaSurface.release();
            }
            mediaSurface = new android.view.Surface(surfaceTexture);
            mediaPlayer.setSurface(mediaSurface);
            android.util.Log.d("BannerVideoView", "Surface set to MediaPlayer");
        }
    }

    public void setLooping(boolean looping) {
        this.shouldLoop = looping;
        if (mediaPlayer != null && isPrepared) {
            mediaPlayer.setLooping(looping);
        }
    }

    // 保存当前视频路径，用于重启MediaPlayer
    private String currentVideoPath;

    /**
     * 获取当前视频路径
     */
    public String getVideoPath() {
        return currentVideoPath;
    }

    public void start() {
        android.util.Log.d("BannerVideoView", "start() called: mediaPlayer=" + (mediaPlayer != null) + ", isPrepared=" + isPrepared + ", visibility=" + getVisibility() + ", textureView.available=" + (textureView != null && textureView.isAvailable()));

        if (mediaPlayer != null && isPrepared) {
            // 检查Surface是否有效
            if (textureView != null && textureView.isAvailable()) {
                try {
                    // 如果已经在播放，不需要重新启动
                    if (mediaPlayer.isPlaying()) {
                        android.util.Log.d("BannerVideoView", "Video already playing");
                        return;
                    }

                    // 直接启动视频
                    mediaPlayer.start();
                    android.util.Log.d("BannerVideoView", "Video started successfully");

                    // 强制刷新视图
                    textureView.invalidate();

                } catch (IllegalStateException e) {
                    android.util.Log.e("BannerVideoView", "Error starting video: " + e.getMessage());
                    // 不要重新加载，这会导致视频无法显示
                }
            } else {
                android.util.Log.w("BannerVideoView", "TextureView not available, cannot start video");
            }
        } else if (mediaPlayer != null && !isPrepared) {
            // 视频还在加载中，设置标志在prepared后自动播放
            shouldAutoStart = true;
            android.util.Log.d("BannerVideoView", "Video not ready yet, will auto-start when prepared");
        } else {
            android.util.Log.w("BannerVideoView", "Cannot start video: mediaPlayer=" + (mediaPlayer != null) + ", isPrepared=" + isPrepared);
        }
    }

    /**
     * 重新加载视频
     */
    private void reloadVideo() {
        if (currentVideoPath == null) {
            android.util.Log.w("BannerVideoView", "No video path to reload");
            return;
        }

        android.util.Log.d("BannerVideoView", "Reloading video: " + currentVideoPath);
        releaseMediaPlayer();
        setVideoPath(currentVideoPath);
    }

    public void stopPlayback() {
        if (mediaPlayer != null) {
            mediaPlayer.stop();
            android.util.Log.d("BannerVideoView", "Video stopped");
        }
    }

    public void pause() {
        if (mediaPlayer != null && isPrepared) {
            mediaPlayer.pause();
            android.util.Log.d("BannerVideoView", "Video paused");
        }
    }

    private void releaseMediaPlayer() {
        if (mediaPlayer != null) {
            mediaPlayer.release();
            mediaPlayer = null;
            isPrepared = false;
            android.util.Log.d("BannerVideoView", "MediaPlayer released");
        }
        // 释放Surface资源
        if (mediaSurface != null) {
            mediaSurface.release();
            mediaSurface = null;
            android.util.Log.d("BannerVideoView", "Surface released");
        }
    }

    /**
     * Update TextureView transform matrix (not used with MediaPlayer scaling)
     */
    private void updateTextureViewSize() {
        // Not needed - using MediaPlayer's built-in scaling
    }

    @Override
    protected void onDetachedFromWindow() {
        super.onDetachedFromWindow();
        releaseMediaPlayer();
    }
}
