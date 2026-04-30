package com.jcoding.aiactivity.ui;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.InnerShowModule;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.manager.MediaResourceManager;
import com.jcoding.aiactivity.network.InnerShowNetworkServer;

import java.util.ArrayList;
import java.util.List;

/**
 * 内场秀设置Activity
 *
 * 管理内场秀相关的所有配置：
 * 1. 服务器设置（密码、端口）
 * 2. 控制器设置（连接地址、密码）
 * 3. 子模块设置（广播、静音、语音）
 * 4. 媒体管理
 * 5. 权限管理
 */
public class InnerShowSettingsActivity extends BaseActivity {

    private static final String TAG = "InnerShowSettings";

    // UI组件
    private EditText etServerPassword;
    private EditText etServerPort;
    private Button btnSaveServer;
    private TextView tvServerStatus;

    private EditText etControllerHost;
    private EditText etControllerPassword;
    private Button btnSaveController;
    private Button btnTestConnection;

    // 子模块设置
    private Switch swWarmupAcceptBroadcast;
    private Switch swWarmupBroadcastMuted;
    private Switch swWarmupVoiceEnabled;

    private Switch swHostingAcceptBroadcast;
    private Switch swHostingBroadcastMuted;
    private Switch swHostingVoiceEnabled;

    private Switch swTeabreakAcceptBroadcast;
    private Switch swTeabreakBroadcastMuted;
    private Switch swTeabreakVoiceEnabled;

    private Button btnMediaManagement;
    private Button btnPermissionManagement;
    private Button btnOperationLogs;

    // 管理器
    private ConfigManager configManager;
    private InnerShowNetworkServer networkServer;
    private MediaResourceManager mediaResourceManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_inner_show_settings);

        configManager = ConfigManager.getInstance(this);
        networkServer = InnerShowNetworkServer.getInstance(this);
        mediaResourceManager = MediaResourceManager.getInstance(this);

        initViews();
        loadSettings();
        setupListeners();
        updateServerStatus();
    }

    private void initViews() {
        // 服务器设置
        etServerPassword = findViewById(R.id.et_server_password);
        etServerPort = findViewById(R.id.et_server_port);
        btnSaveServer = findViewById(R.id.btn_save_server);
        tvServerStatus = findViewById(R.id.tv_server_status);

        // 控制器设置
        etControllerHost = findViewById(R.id.et_controller_host);
        etControllerPassword = findViewById(R.id.et_controller_password);
        btnSaveController = findViewById(R.id.btn_save_controller);
        btnTestConnection = findViewById(R.id.btn_test_connection);

        // 暖场秀设置
        swWarmupAcceptBroadcast = findViewById(R.id.sw_warmup_accept_broadcast);
        swWarmupBroadcastMuted = findViewById(R.id.sw_warmup_broadcast_muted);
        swWarmupVoiceEnabled = findViewById(R.id.sw_warmup_voice_enabled);

        // 主持秀设置
        swHostingAcceptBroadcast = findViewById(R.id.sw_hosting_accept_broadcast);
        swHostingBroadcastMuted = findViewById(R.id.sw_hosting_broadcast_muted);
        swHostingVoiceEnabled = findViewById(R.id.sw_hosting_voice_enabled);

        // 茶歇秀设置
        swTeabreakAcceptBroadcast = findViewById(R.id.sw_teabreak_accept_broadcast);
        swTeabreakBroadcastMuted = findViewById(R.id.sw_teabreak_broadcast_muted);
        swTeabreakVoiceEnabled = findViewById(R.id.sw_teabreak_voice_enabled);

        // 其他功能
        btnMediaManagement = findViewById(R.id.btn_media_management);
        btnPermissionManagement = findViewById(R.id.btn_permission_management);
        btnOperationLogs = findViewById(R.id.btn_operation_logs);
    }

    private void loadSettings() {
        // 服务器设置
        etServerPassword.setText(configManager.getInnerShowServerPassword());
        etServerPort.setText(String.valueOf(configManager.getInnerShowServerPort(8888)));

        // 控制器设置
        etControllerHost.setText(configManager.getControllerServerHost(""));
        etControllerPassword.setText(configManager.getControllerServerPassword(""));

        // 暖场秀设置
        swWarmupAcceptBroadcast.setChecked(configManager.getInnerShowAcceptBroadcast("warmup"));
        swWarmupBroadcastMuted.setChecked(configManager.getInnerShowBroadcastMuted("warmup"));
        swWarmupVoiceEnabled.setChecked(configManager.getInnerShowVoiceEnabled("warmup"));

        // 主持秀设置
        swHostingAcceptBroadcast.setChecked(configManager.getInnerShowAcceptBroadcast("hosting"));
        swHostingBroadcastMuted.setChecked(configManager.getInnerShowBroadcastMuted("hosting"));
        swHostingVoiceEnabled.setChecked(configManager.getInnerShowVoiceEnabled("hosting"));

        // 茶歇秀设置
        swTeabreakAcceptBroadcast.setChecked(configManager.getInnerShowAcceptBroadcast("tea_break"));
        swTeabreakBroadcastMuted.setChecked(configManager.getInnerShowBroadcastMuted("tea_break"));
        swTeabreakVoiceEnabled.setChecked(configManager.getInnerShowVoiceEnabled("tea_break"));
    }

    private void setupListeners() {
        // 保存服务器设置
        btnSaveServer.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveServerSettings();
            }
        });

        // 保存控制器设置
        btnSaveController.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveControllerSettings();
            }
        });

        // 测试连接
        btnTestConnection.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                testConnection();
            }
        });

        // 暖场秀设置
        setupModuleSwitches("warmup", swWarmupAcceptBroadcast, swWarmupBroadcastMuted, swWarmupVoiceEnabled);

        // 主持秀设置
        setupModuleSwitches("hosting", swHostingAcceptBroadcast, swHostingBroadcastMuted, swHostingVoiceEnabled);

        // 茶歇秀设置
        setupModuleSwitches("tea_break", swTeabreakAcceptBroadcast, swTeabreakBroadcastMuted, swTeabreakVoiceEnabled);

        // 媒体管理
        btnMediaManagement.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(InnerShowSettingsActivity.this, MediaManagementActivity.class);
                startActivity(intent);
            }
        });

        // 权限管理
        btnPermissionManagement.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(InnerShowSettingsActivity.this, PermissionManagementActivity.class);
                startActivity(intent);
            }
        });

        // 操作日志
        btnOperationLogs.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(InnerShowSettingsActivity.this, OperationLogActivity.class);
                startActivity(intent);
            }
        });
    }

    private void setupModuleSwitches(final String moduleId, Switch acceptBroadcast,
                                     Switch broadcastMuted, Switch voiceEnabled) {
        // 接受广播
        acceptBroadcast.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                configManager.setInnerShowAcceptBroadcast(moduleId, isChecked);
            }
        });

        // 广播静音
        broadcastMuted.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                configManager.setInnerShowBroadcastMuted(moduleId, isChecked);
            }
        });

        // 语音启用
        voiceEnabled.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                configManager.setInnerShowVoiceEnabled(moduleId, isChecked);
            }
        });
    }

    private void saveServerSettings() {
        String password = etServerPassword.getText().toString().trim();
        String portStr = etServerPort.getText().toString().trim();

        if (TextUtils.isEmpty(password)) {
            Toast.makeText(this, "请输入服务器密码", Toast.LENGTH_SHORT).show();
            return;
        }

        if (TextUtils.isEmpty(portStr)) {
            Toast.makeText(this, "请输入服务器端口", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            int port = Integer.parseInt(portStr);
            if (port < 1024 || port > 65535) {
                Toast.makeText(this, "端口范围：1024-65535", Toast.LENGTH_SHORT).show();
                return;
            }

            // 保存设置
            configManager.setInnerShowServerPassword(password);
            configManager.setInnerShowServerPort(port);

            Toast.makeText(this, "服务器设置已保存", Toast.LENGTH_SHORT).show();

            // 如果服务器正在运行，提示需要重启
            if (networkServer.isRunning()) {
                new AlertDialog.Builder(this)
                    .setTitle("提示")
                    .setMessage("服务器正在运行，需要重启才能应用新设置")
                    .setPositiveButton("重启服务器", (dialog, which) -> {
                        networkServer.stopServer();
                        networkServer.startServer();
                        updateServerStatus();
                    })
                    .setNegativeButton("稍后", null)
                    .show();
            }

        } catch (NumberFormatException e) {
            Toast.makeText(this, "端口格式错误", Toast.LENGTH_SHORT).show();
        }
    }

    private void saveControllerSettings() {
        String host = etControllerHost.getText().toString().trim();
        String password = etControllerPassword.getText().toString().trim();

        if (TextUtils.isEmpty(host)) {
            Toast.makeText(this, "请输入服务器地址", Toast.LENGTH_SHORT).show();
            return;
        }

        if (TextUtils.isEmpty(password)) {
            Toast.makeText(this, "请输入服务器密码", Toast.LENGTH_SHORT).show();
            return;
        }

        // 保存设置
        configManager.setControllerServerHost(host);
        configManager.setControllerServerPassword(password);

        Toast.makeText(this, "控制器设置已保存", Toast.LENGTH_SHORT).show();
    }

    private void testConnection() {
        String host = etControllerHost.getText().toString().trim();
        String password = etControllerPassword.getText().toString().trim();

        if (TextUtils.isEmpty(host) || TextUtils.isEmpty(password)) {
            Toast.makeText(this, "请先保存控制器设置", Toast.LENGTH_SHORT).show();
            return;
        }

        // 解析地址和端口
        String[] parts = host.split(":");
        String serverHost = parts[0];
        int serverPort = 8888;

        if (parts.length > 1) {
            try {
                serverPort = Integer.parseInt(parts[1]);
            } catch (NumberFormatException e) {
                Toast.makeText(this, "地址格式错误", Toast.LENGTH_SHORT).show();
                return;
            }
        }

        // TODO: 实现连接测试
        Toast.makeText(this, "连接测试功能开发中", Toast.LENGTH_SHORT).show();
    }

    private void updateServerStatus() {
        if (networkServer.isRunning()) {
            int port = networkServer.getServerPort();
            int clients = networkServer.getConnectedClientsCount();
            tvServerStatus.setText("运行中 | 端口: " + port + " | 连接数: " + clients);
            tvServerStatus.setTextColor(getResources().getColor(R.color.color_success));
        } else {
            tvServerStatus.setText("未运行");
            tvServerStatus.setTextColor(getResources().getColor(R.color.textSecondary));
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        updateServerStatus();
    }
}
