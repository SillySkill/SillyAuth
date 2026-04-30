package com.jcoding.aiactivity.ui;

import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.manager.InnerShowNetworkClient;
import com.jcoding.aiactivity.manager.InnerShowNetworkConfigManager;
import com.jcoding.aiactivity.manager.InnerShowNetworkServerManager;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.net.InetAddress;
import java.util.ArrayList;
import java.util.List;

/**
 * 内场秀网络设置页
 * 配置局域网通信和主服务器模式
 */
public class InnerShowNetworkSettingsActivity extends BaseActivity {

    private Spinner spinNetworkMode;
    private TextView tvNetworkModeDescription;
    private Switch switchServerMode;
    private EditText editServerIp;
    private EditText editServerPort;
    private EditText editWsPort;
    private Switch switchAutoDiscover;
    private TextView tvServerStatus;
    private TextView tvCurrentIp;
    private Button btnTestConnection;
    private Button btnSave;
    private Button btnBack;
    private Button btnDiscover;

    private InnerShowNetworkConfigManager configManager;
    private InnerShowNetworkServerManager serverManager;
    private InnerShowNetworkClient networkClient;

    private NsdManager nsdManager;
    private NsdManager.DiscoveryListener discoveryListener;
    private NsdManager.RegistrationListener registrationListener;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_inner_show_network_settings);

        configManager = InnerShowNetworkConfigManager.getInstance(this);
        serverManager = InnerShowNetworkServerManager.getInstance(this);
        networkClient = InnerShowNetworkClient.getInstance(this);
        nsdManager = (NsdManager) getSystemService(NSD_SERVICE);

        initViews();
        loadSettings();
        setupListeners();
        updateServerStatus();
    }

    private void initViews() {
        spinNetworkMode = findViewById(R.id.spin_network_mode);
        tvNetworkModeDescription = findViewById(R.id.tv_network_mode_description);
        switchServerMode = findViewById(R.id.switch_server_mode);
        editServerIp = findViewById(R.id.edit_server_ip);
        editServerPort = findViewById(R.id.edit_server_port);
        editWsPort = findViewById(R.id.edit_ws_port);
        switchAutoDiscover = findViewById(R.id.switch_auto_discover);
        tvServerStatus = findViewById(R.id.tv_server_status);
        tvCurrentIp = findViewById(R.id.tv_current_ip);
        btnTestConnection = findViewById(R.id.btn_test_connection);
        btnSave = findViewById(R.id.btn_save);
        btnBack = findViewById(R.id.btn_back);
        btnDiscover = findViewById(R.id.btn_discover);

        // 准备网络模式选项
        List<String> modeOptions = new ArrayList<>();
        for (InnerShowNetworkConfigManager.NetworkMode mode : InnerShowNetworkConfigManager.NetworkMode.values()) {
            modeOptions.add(mode.getName() + " - " + mode.getDescription());
        }

        ArrayAdapter<String> modeAdapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_spinner_item,
                modeOptions
        );
        modeAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinNetworkMode.setAdapter(modeAdapter);

        // 显示当前IP
        tvCurrentIp.setText("本机IP: " + NetworkUtils.getLocalIpAddress());

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    private void loadSettings() {
        // 加载网络模式
        InnerShowNetworkConfigManager.NetworkMode currentMode = configManager.getNetworkMode();
        for (int i = 0; i < InnerShowNetworkConfigManager.NetworkMode.values().length; i++) {
            if (InnerShowNetworkConfigManager.NetworkMode.values()[i] == currentMode) {
                spinNetworkMode.setSelection(i);
                break;
            }
        }
        updateModeDescription(currentMode);

        // 加载主服务器模式
        switchServerMode.setChecked(configManager.isServerMode());

        // 加载服务器配置
        editServerIp.setText(configManager.getServerIp());
        editServerPort.setText(String.valueOf(configManager.getServerPort()));
        editWsPort.setText(String.valueOf(configManager.getWsPort()));

        // 加载自动发现
        switchAutoDiscover.setChecked(configManager.isAutoDiscoverEnabled());
    }

    private void setupListeners() {
        // 网络模式选择监听
        spinNetworkMode.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                InnerShowNetworkConfigManager.NetworkMode selectedMode =
                        InnerShowNetworkConfigManager.NetworkMode.values()[position];
                configManager.setNetworkMode(selectedMode);
                updateModeDescription(selectedMode);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        // 主服务器模式开关监听
        switchServerMode.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                configManager.setServerMode(isChecked);

                if (isChecked) {
                    // 启动服务器
                    startServer();
                } else {
                    // 停止服务器
                    stopServer();
                }
            }
        });

        // 自动发现开关监听
        switchAutoDiscover.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                configManager.setAutoDiscover(isChecked);

                if (isChecked && !configManager.isServerMode()) {
                    // 开始发现服务
                    startDiscovery();
                } else {
                    // 停止发现
                    stopDiscovery();
                }
            }
        });

        // 测试连接按钮监听
        btnTestConnection.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                testConnection();
            }
        });

        // 保存按钮监听
        btnSave.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveSettings();
            }
        });

        // 发现服务器按钮监听
        btnDiscover.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                discoverServer();
            }
        });
    }

    /**
     * 更新模式描述
     */
    private void updateModeDescription(InnerShowNetworkConfigManager.NetworkMode mode) {
        tvNetworkModeDescription.setText(mode.getDescription());

        // 主服务器模式时禁用某些选项
        if (mode == InnerShowNetworkConfigManager.NetworkMode.SERVER) {
            switchServerMode.setEnabled(true);
            editServerIp.setEnabled(false);
            editServerPort.setEnabled(true);
            editWsPort.setEnabled(true);
        } else {
            switchServerMode.setEnabled(false);
            editServerIp.setEnabled(true);
            editServerPort.setEnabled(true);
            editWsPort.setEnabled(true);
        }
    }

    /**
     * 启动服务器
     */
    private void startServer() {
        int httpPort = Integer.parseInt(editServerPort.getText().toString());
        int wsPort = Integer.parseInt(editWsPort.getText().toString());

        boolean success = serverManager.startServer(httpPort, wsPort);

        if (success) {
            showToast("服务器已启动");
            tvServerStatus.setText("服务器状态: 运行中 (" + serverManager.getServerUrl() + ")");

            // 注册网络服务
            registerNsdService(httpPort);
        } else {
            showToast("启动服务器失败");
            switchServerMode.setChecked(false);
        }
    }

    /**
     * 停止服务器
     */
    private void stopServer() {
        serverManager.stopServer();
        tvServerStatus.setText("服务器状态: 已停止");

        // 注销网络服务
        unregisterNsdService();
    }

    /**
     * 注册网络服务
     */
    private void registerNsdService(int port) {
        if (nsdManager != null) {
            configManager.registerService(nsdManager, port, new InnerShowNetworkConfigManager.ServiceRegistrationCallback() {
                @Override
                public void onServiceRegistered(NsdServiceInfo serviceInfo) {
                    showToast("网络服务已注册");
                }

                @Override
                public void onRegistrationFailed(int errorCode) {
                    showToast("网络服务注册失败: " + errorCode);
                }
            });
        }
    }

    /**
     * 注销网络服务
     */
    private void unregisterNsdService() {
        if (nsdManager != null && registrationListener != null) {
            configManager.unregisterService(nsdManager, registrationListener);
        }
    }

    /**
     * 开始发现服务
     */
    private void startDiscovery() {
        if (nsdManager != null) {
            configManager.discoverServices(nsdManager, new InnerShowNetworkConfigManager.ServiceDiscoveryCallback() {
                @Override
                public void onDiscoveryStarted() {
                    showToast("开始发现内场秀设备...");
                }

                @Override
                public void onServiceFound(NsdServiceInfo serviceInfo) {
                    showToast("发现设备: " + serviceInfo.getServiceName());
                }

                @Override
                public void onServiceResolved(NsdServiceInfo serviceInfo) {
                    // 更新服务器IP
                    InetAddress host = serviceInfo.getHost();
                    int port = serviceInfo.getPort();

                    if (host != null) {
                        String ip = host.getHostAddress();
                        editServerIp.setText(ip);
                        editServerPort.setText(String.valueOf(port));
                        showToast("已连接到: " + ip + ":" + port);
                    }
                }

                @Override
                public void onServiceLost(NsdServiceInfo serviceInfo) {
                    showToast("设备已断开");
                }

                @Override
                public void onDiscoveryStopped() {
                }

                @Override
                public void onDiscoveryFailed(int errorCode) {
                    showToast("发现服务失败: " + errorCode);
                }
            });
        }
    }

    /**
     * 停止发现服务
     */
    private void stopDiscovery() {
        if (nsdManager != null && discoveryListener != null) {
            configManager.stopDiscovery(nsdManager, discoveryListener);
        }
    }

    /**
     * 发现服务器（手动触发）
     */
    private void discoverServer() {
        showToast("正在搜索内场秀设备...");
        startDiscovery();
    }

    /**
     * 测试连接
     */
    private void testConnection() {
        String ip = editServerIp.getText().toString();
        int port = Integer.parseInt(editServerPort.getText().toString());

        // 临时更新配置
        configManager.setServerIp(ip);
        configManager.setServerPort(port);

        btnTestConnection.setEnabled(false);
        btnTestConnection.setText("连接中...");

        networkClient.testConnection(new InnerShowNetworkClient.NetworkCallback() {
            @Override
            public void onSuccess(String result) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        btnTestConnection.setEnabled(true);
                        btnTestConnection.setText("测试连接");
                        showToast("连接成功！");
                        tvServerStatus.setText("服务器状态: 已连接 (http://" + ip + ":" + port + ")");
                    }
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        btnTestConnection.setEnabled(true);
                        btnTestConnection.setText("测试连接");
                        showToast("连接失败: " + error);
                        tvServerStatus.setText("服务器状态: 未连接");
                    }
                });
            }
        });
    }

    /**
     * 保存设置
     */
    private void saveSettings() {
        String ip = editServerIp.getText().toString();
        int port = Integer.parseInt(editServerPort.getText().toString());
        int wsPort = Integer.parseInt(editWsPort.getText().toString());

        configManager.setServerIp(ip);
        configManager.setServerPort(port);
        configManager.setWsPort(wsPort);

        showToast("设置已保存");
    }

    /**
     * 更新服务器状态
     */
    private void updateServerStatus() {
        if (serverManager.isRunning()) {
            tvServerStatus.setText("服务器状态: 运行中 (" + serverManager.getServerUrl() + ")");
            switchServerMode.setChecked(true);
        } else {
            tvServerStatus.setText("服务器状态: 已停止");
            switchServerMode.setChecked(false);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();

        // 停止发现
        stopDiscovery();

        // 注销服务
        if (!configManager.isServerMode()) {
            unregisterNsdService();
        }
    }
}
