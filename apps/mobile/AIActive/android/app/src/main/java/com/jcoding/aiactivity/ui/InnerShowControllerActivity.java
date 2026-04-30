package com.jcoding.aiactivity.ui;

import android.content.Context;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.InnerShowModule;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.network.InnerShowNetworkClient;

/**
 * 内场秀控制器Activity
 *
 * 运行在控制器设备上，用于远程控制内场秀设备
 *
 * 功能：
 * 1. 连接到内场秀服务器（需要密码）
 * 2. 播放控制（播放、暂停、停止、跳转）
 * 3. 媒体资源管理（上传、启用、禁用）
 * 4. 实时状态显示
 * 5. 连接状态管理
 */
public class InnerShowControllerActivity extends AppCompatActivity {

    private static final String TAG = "InnerShowController";

    // UI组件
    private LinearLayout connectionPanel;
    private EditText etServerAddress;
    private EditText etServerPassword;
    private Button btnConnect;
    private Button btnDisconnect;

    private LinearLayout controlPanel;
    private TextView tvConnectionStatus;
    private TextView tvPlaybackStatus;
    private TextView tvCurrentProgram;
    private TextView tvProgress;
    private SeekBar seekBarProgress;

    private Button btnPlay;
    private Button btnPause;
    private Button btnStop;
    private Button btnPrevious;
    private Button btnNext;

    private ScrollView logScroll;
    private TextView tvLog;

    private ProgressBar progressBar;

    // 管理器
    private ConfigManager configManager;
    private InnerShowNetworkClient networkClient;

    // 状态
    private boolean isConnected = false;
    private boolean isAuthenticated = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 初始化管理器
        configManager = ConfigManager.getInstance(this);
        networkClient = InnerShowNetworkClient.getInstance(this);

        // 设置回调
        networkClient.setClientCallback(clientCallback);

        // 检查是否已保存连接信息
        String savedHost = configManager.getControllerServerHost("");
        String savedPassword = configManager.getControllerServerPassword("");

        if (!savedHost.isEmpty() && !savedPassword.isEmpty()) {
            // 自动连接
            showConnectionProgress();
            connectToServer(savedHost, savedPassword);
        } else {
            // 显示连接界面
            showConnectionPanel();
        }
    }

    /**
     * 显示连接面板
     */
    private void showConnectionPanel() {
        setContentView(R.layout.activity_inner_show_controller_connection);

        // 初始化UI
        connectionPanel = findViewById(R.id.connection_panel);
        etServerAddress = findViewById(R.id.et_server_address);
        etServerPassword = findViewById(R.id.et_server_password);
        btnConnect = findViewById(R.id.btn_connect);

        // 加载保存的地址
        String savedHost = configManager.getControllerServerHost("");
        if (!savedHost.isEmpty()) {
            etServerAddress.setText(savedHost);
        }

        // 连接按钮点击
        btnConnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String host = etServerAddress.getText().toString().trim();
                String password = etServerPassword.getText().toString().trim();

                if (host.isEmpty()) {
                    Toast.makeText(InnerShowControllerActivity.this, "请输入服务器地址", Toast.LENGTH_SHORT).show();
                    return;
                }

                if (password.isEmpty()) {
                    Toast.makeText(InnerShowControllerActivity.this, "请输入服务器密码", Toast.LENGTH_SHORT).show();
                    return;
                }

                // 保存连接信息
                configManager.setControllerServerHost(host);
                configManager.setControllerServerPassword(password);

                // 连接
                showConnectionProgress();
                connectToServer(host, password);
            }
        });
    }

    /**
     * 显示连接进度
     */
    private void showConnectionProgress() {
        setContentView(R.layout.activity_inner_show_controller_progress);
        progressBar = findViewById(R.id.progress_bar);
        TextView tvMessage = findViewById(R.id.tv_message);
        tvMessage.setText("正在连接到内场秀设备...");
    }

    /**
     * 显示控制面板
     */
    private void showControlPanel() {
        setContentView(R.layout.activity_inner_show_controller);

        // 初始化UI
        tvConnectionStatus = findViewById(R.id.tv_connection_status);
        tvPlaybackStatus = findViewById(R.id.tv_playback_status);
        tvCurrentProgram = findViewById(R.id.tv_current_program);
        tvProgress = findViewById(R.id.tv_progress);
        seekBarProgress = findViewById(R.id.seek_bar_progress);

        btnPlay = findViewById(R.id.btn_play);
        btnPause = findViewById(R.id.btn_pause);
        btnStop = findViewById(R.id.btn_stop);
        btnPrevious = findViewById(R.id.btn_previous);
        btnNext = findViewById(R.id.btn_next);

        btnDisconnect = findViewById(R.id.btn_disconnect);

        logScroll = findViewById(R.id.log_scroll);
        tvLog = findViewById(R.id.tv_log);

        // 播放控制按钮
        btnPlay.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isAuthenticated) {
                    networkClient.play();
                    addLog("发送播放命令");
                }
            }
        });

        btnPause.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isAuthenticated) {
                    networkClient.pause();
                    addLog("发送暂停命令");
                }
            }
        });

        btnStop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isAuthenticated) {
                    networkClient.stop();
                    addLog("发送停止命令");
                }
            }
        });

        btnPrevious.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isAuthenticated) {
                    // 上一个节目需要先获取当前索引
                    networkClient.requestStatus();
                    addLog("请求状态信息");
                }
            }
        });

        btnNext.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isAuthenticated) {
                    networkClient.requestStatus();
                    addLog("请求状态信息");
                }
            }
        });

        // 进度条拖动
        seekBarProgress.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                if (fromUser && isAuthenticated) {
                    // 假设每个节目30秒，计算节目索引
                    int index = progress / 30;
                    networkClient.jumpTo(index);
                    addLog("跳转到第 " + (index + 1) + " 个节目");
                }
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // 断开连接按钮
        btnDisconnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                disconnect();
                showConnectionPanel();
            }
        });

        // 更新状态显示
        updateConnectionStatus();
    }

    /**
     * 连接到服务器
     */
    private void connectToServer(String host, String password) {
        // 解析地址和端口
        String[] parts = host.split(":");
        String serverHost = parts[0];
        int serverPort = 8888;  // 默认端口

        if (parts.length > 1) {
            try {
                serverPort = Integer.parseInt(parts[1]);
            } catch (NumberFormatException e) {
                Log.w(TAG, "无效的端口号，使用默认端口");
            }
        }

        // 启用自动重连
        networkClient.enableAutoReconnect();

        // 连接
        networkClient.connect(serverHost, serverPort, password);

        addLog("正在连接: " + serverHost + ":" + serverPort);
    }

    /**
     * 断开连接
     */
    private void disconnect() {
        networkClient.disableAutoReconnect();
        networkClient.disconnect();

        isConnected = false;
        isAuthenticated = false;

        addLog("已断开连接");
    }

    /**
     * 更新连接状态显示
     */
    private void updateConnectionStatus() {
        if (tvConnectionStatus != null) {
            if (isAuthenticated) {
                tvConnectionStatus.setText("已连接");
                tvConnectionStatus.setTextColor(getResources().getColor(R.color.color_success));
            } else if (isConnected) {
                tvConnectionStatus.setText("认证中...");
                tvConnectionStatus.setTextColor(getResources().getColor(R.color.color_warning));
            } else {
                tvConnectionStatus.setText("未连接");
                tvConnectionStatus.setTextColor(getResources().getColor(R.color.color_error));
            }
        }
    }

    /**
     * 添加日志
     */
    private void addLog(String message) {
        if (tvLog != null) {
            String time = new java.text.SimpleDateFormat("HH:mm:ss").format(new java.util.Date());
            String logEntry = "[" + time + "] " + message + "\n";

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    tvLog.append(logEntry);
                    logScroll.postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            logScroll.fullScroll(ScrollView.FOCUS_DOWN);
                        }
                    }, 100);
                }
            });
        }
    }

    // ==================== 客户端回调 ====================

    private InnerShowNetworkClient.ClientCallback clientCallback = new InnerShowNetworkClient.ClientCallback() {

        @Override
        public void onConnected() {
            Log.i(TAG, "已连接到服务器");
            isConnected = true;
            addLog("已连接到服务器");
            updateConnectionStatus();
        }

        @Override
        public void onAuthenticated() {
            Log.i(TAG, "认证成功");
            isAuthenticated = true;
            addLog("认证成功");
            updateConnectionStatus();

            // 显示控制面板
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    showControlPanel();
                }
            });

            // 请求当前状态
            networkClient.requestStatus();
        }

        @Override
        public void onAuthFailed(String error) {
            Log.e(TAG, "认证失败: " + error);
            isAuthenticated = false;
            addLog("认证失败: " + error);

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(InnerShowControllerActivity.this, "认证失败，请检查密码", Toast.LENGTH_LONG).show();
                    showConnectionPanel();
                }
            });
        }

        @Override
        public void onDisconnected() {
            Log.i(TAG, "已断开连接");
            isConnected = false;
            isAuthenticated = false;
            addLog("已断开连接");
            updateConnectionStatus();
        }

        @Override
        public void onSuccess(String message) {
            addLog("✓ " + message);
        }

        @Override
        public void onPlaybackStatusChanged(InnerShowNetworkClient.PlaybackStatus status) {
            Log.d(TAG, "播放状态更新: " + status.isPlaying);

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    // 更新播放状态
                    if (tvPlaybackStatus != null) {
                        if (status.isPlaying) {
                            tvPlaybackStatus.setText(status.isPaused ? "已暂停" : "播放中");
                        } else {
                            tvPlaybackStatus.setText("已停止");
                        }
                    }

                    // 更新当前节目
                    if (tvCurrentProgram != null) {
                        if (status.currentProgram != null && !status.currentProgram.isEmpty()) {
                            tvCurrentProgram.setText("当前节目: " + status.currentProgram);
                        } else {
                            tvCurrentProgram.setText("当前节目: -");
                        }
                    }

                    // 更新进度
                    if (tvProgress != null && seekBarProgress != null) {
                        tvProgress.setText(status.currentProgress + "s / " + status.totalProgress + "s");
                        seekBarProgress.setMax(status.totalProgress);
                        seekBarProgress.setProgress(status.currentProgress);
                    }
                }
            });
        }

        @Override
        public void onMediaStatusChanged(InnerShowNetworkClient.MediaStatus status) {
            Log.d(TAG, "媒体状态更新: " + status.module);
            addLog("媒体更新: " + status.module.getName());
        }

        @Override
        public void onError(String error) {
            Log.e(TAG, "错误: " + error);
            addLog("✗ " + error);

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(InnerShowControllerActivity.this, error, Toast.LENGTH_SHORT).show();
                }
            });
        }
    };

    @Override
    protected void onDestroy() {
        super.onDestroy();

        // 断开连接
        if (isConnected) {
            disconnect();
        }
    }
}
