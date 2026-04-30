package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.VideoView;
import android.widget.ImageView;
import android.widget.Button;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.utils.PreferenceUtils;
import com.jcoding.aiactivity.utils.Constants;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * 启动页
 * 播放启动视频，初始化系统，判断跳转目标
 * 支持多个视频轮播
 */
public class SplashActivity extends BaseActivity {

    private static final long SPLASH_DELAY = 2000;  // 启动页停留时长（毫秒）
    private VideoView videoView;
    private boolean hasNavigated = false;  // 是否已经跳转
    private Handler navigationHandler = new Handler(Looper.getMainLooper());

    // 视频轮播相关
    private java.util.List<File> videoFiles = new java.util.ArrayList<>();
    private int currentVideoIndex = 0;
    private ImageView placeholder;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        initViews();
    }

    /**
     * 初始化视图
     */
    private void initViews() {
        videoView = findViewById(R.id.video_view);
        placeholder = findViewById(R.id.iv_placeholder);
        Button btnSkip = findViewById(R.id.btn_skip);

        // 设置跳过按钮点击事件
        if (btnSkip != null) {
            btnSkip.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    // 取消所有待处理的跳转
                    navigationHandler.removeCallbacksAndMessages(null);
                    // 立即跳转
                    navigateToNext();
                }
            });
        }

        // 在后台复制视频文件，避免阻塞UI
        new Handler(Looper.getMainLooper()).post(new Runnable() {
            @Override
            public void run() {
                loadVideosAsync(placeholder);
            }
        });
    }

    /**
     * 异步加载所有视频并开始播放
     */
    private void loadVideosAsync(ImageView placeholder) {
        new Thread(() -> {
            try {
                // 获取assets目录下所有视频文件
                String[] videoList = getAssets().list("video/load");

                if (videoList == null || videoList.length == 0) {
                    // 没有视频文件，延迟跳转
                    navigationHandler.postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            navigateToNext();
                        }
                    }, SPLASH_DELAY);
                    return;
                }

                // 过滤出视频文件并排序
                java.util.Arrays.sort(videoList);
                videoFiles.clear();

                for (String fileName : videoList) {
                    if (fileName.toLowerCase().endsWith(".mp4") ||
                        fileName.toLowerCase().endsWith(".mov") ||
                        fileName.toLowerCase().endsWith(".avi")) {

                        // 复制视频到缓存
                        String outputFileName = "splash_" + fileName;
                        File videoFile = copyAssetToFile("video/load/" + fileName, outputFileName);

                        if (videoFile != null && videoFile.exists()) {
                            videoFiles.add(videoFile);
                            android.util.Log.d("SplashActivity", "Loaded video: " + fileName);
                        }
                    }
                }

                if (videoFiles.isEmpty()) {
                    // 没有有效视频，延迟跳转
                    navigationHandler.postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            navigateToNext();
                        }
                    }, SPLASH_DELAY);
                    return;
                }

                // 开始播放第一个视频
                currentVideoIndex = 0;
                android.util.Log.d("SplashActivity", "Total videos loaded: " + videoFiles.size());

                new Handler(Looper.getMainLooper()).post(() -> {
                    playCurrentVideo(placeholder);
                });

            } catch (IOException e) {
                e.printStackTrace();
                // 发生错误，延迟跳转
                navigationHandler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        navigateToNext();
                    }
                }, SPLASH_DELAY);
            }
        }).start();
    }

    /**
     * 播放当前视频
     */
    private void playCurrentVideo(ImageView placeholder) {
        if (videoFiles.isEmpty() || currentVideoIndex >= videoFiles.size()) {
            // 所有视频播放完毕，跳转
            navigateToNext();
            return;
        }

        File videoFile = videoFiles.get(currentVideoIndex);
        android.util.Log.d("SplashActivity", "Playing video " + (currentVideoIndex + 1) + "/" + videoFiles.size() + ": " + videoFile.getName());

        try {
            Uri videoUri = Uri.fromFile(videoFile);
            videoView.setVideoURI(videoUri);

            // 设置准备完成监听
            videoView.setOnPreparedListener(mediaPlayer -> {
                // 视频准备好后，隐藏占位图
                if (placeholder != null) {
                    placeholder.setVisibility(View.GONE);
                }
                // 开始播放
                videoView.start();
            });

            // 设置播放完成监听
            videoView.setOnCompletionListener(mediaPlayer -> {
                android.util.Log.d("SplashActivity", "Video " + (currentVideoIndex + 1) + " completed");

                // 播放下一个视频
                currentVideoIndex++;
                if (currentVideoIndex < videoFiles.size()) {
                    // 还有视频，播放下一个
                    playCurrentVideo(placeholder);
                } else {
                    // 所有视频播放完毕，跳转
                    navigateToNext();
                }
            });

            // 设置错误监听
            videoView.setOnErrorListener((mediaPlayer, what, extra) -> {
                android.util.Log.e("SplashActivity", "Video playback error: " + what + ", " + extra);

                // 当前视频播放失败，尝试播放下一个
                currentVideoIndex++;
                if (currentVideoIndex < videoFiles.size()) {
                    playCurrentVideo(placeholder);
                } else {
                    // 没有更多视频，延迟跳转
                    navigationHandler.postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            navigateToNext();
                        }
                    }, SPLASH_DELAY);
                }
                return true;
            });
        } catch (Exception e) {
            e.printStackTrace();
            android.util.Log.e("SplashActivity", "Exception playing video", e);

            // 播放失败时，尝试下一个视频或跳转
            currentVideoIndex++;
            if (currentVideoIndex < videoFiles.size()) {
                playCurrentVideo(placeholder);
            } else {
                navigationHandler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        navigateToNext();
                    }
                }, SPLASH_DELAY);
            }
        }
    }

    /**
     * 将assets中的文件复制到缓存目录
     */
    private File copyAssetToFile(String assetPath, String outputFileName) {
        InputStream is = null;
        OutputStream os = null;
        try {
            // 创建缓存文件
            File outputFile = new File(getCacheDir(), outputFileName);

            // 如果文件已存在，直接返回
            if (outputFile.exists()) {
                return outputFile;
            }

            // 从assets读取
            is = getAssets().open(assetPath);
            os = new FileOutputStream(outputFile);

            byte[] buffer = new byte[8192];
            int len;
            while ((len = is.read(buffer)) != -1) {
                os.write(buffer, 0, len);
            }

            os.flush();
            return outputFile;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        } finally {
            try {
                if (is != null) is.close();
                if (os != null) os.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (videoView != null) {
            videoView.stopPlayback();
        }
        // 清理所有待处理的跳转
        navigationHandler.removeCallbacksAndMessages(null);
    }

    /**
     * 跳转到下一个页面
     */
    private void navigateToNext() {
        // 防止重复跳转
        if (hasNavigated) {
            return;
        }
        hasNavigated = true;

        // 检查是否已登录
        boolean isLoggedIn = PreferenceUtils.getBoolean(this, Constants.PREF_IS_LOGGED_IN, false);

        Intent intent;
        if (isLoggedIn) {
            // 已登录，进入模块选择页
            intent = new Intent(this, ModeSelectionActivity.class);
        } else {
            // 未登录，进入登录页
            intent = new Intent(this, LoginActivity.class);
        }

        startActivity(intent);
        finish();
    }

    @Override
    protected void onNetworkChanged(boolean isOnline, NetworkUtils.NetworkType type) {
        // 启动页不显示网络提示
    }
}
