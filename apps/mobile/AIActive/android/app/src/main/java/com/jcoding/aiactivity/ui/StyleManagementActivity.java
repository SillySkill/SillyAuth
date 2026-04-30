package com.jcoding.aiactivity.ui;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.StyleConfig;
import com.jcoding.aiactivity.adapter.StyleManagementAdapter;
import com.jcoding.aiactivity.manager.ConfigManager;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * 风格管理Activity
 * 管理AI百变秀中的风格启用/禁用状态
 */
public class StyleManagementActivity extends BaseActivity {

    private static final String TAG = "StyleManagement";

    private RecyclerView recyclerView;
    private StyleManagementAdapter adapter;
    private List<StyleConfig> styleList;
    private ConfigManager configManager;

    private Button btnBack;
    private Button btnSelectAll;
    private Button btnDeselectAll;
    private TextView tvEmptyView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_style_management);

        Log.d(TAG, "========== onCreate 开始 ==========");

        // 显示启动Toast
        Toast.makeText(this, "风格管理页面已启动", Toast.LENGTH_SHORT).show();

        configManager = ConfigManager.getInstance(this);
        Log.d(TAG, "ConfigManager已获取");

        initViews();
        Log.d(TAG, "initViews完成");

        loadStyles();
        Log.d(TAG, "loadStyles完成");

        setupListeners();
        Log.d(TAG, "setupListeners完成");

        // 延迟显示调试信息
        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() {
            @Override
            public void run() {
                int count = styleList != null ? styleList.size() : 0;
                String msg = "当前风格数量: " + count;
                Toast.makeText(StyleManagementActivity.this, msg, Toast.LENGTH_LONG).show();
                Log.d(TAG, msg);
            }
        }, 500);

        Log.d(TAG, "========== onCreate 完成 ==========");
    }

    private void initViews() {
        recyclerView = findViewById(R.id.recycler_view);
        btnBack = findViewById(R.id.btn_back);
        btnSelectAll = findViewById(R.id.btn_select_all);
        btnDeselectAll = findViewById(R.id.btn_deselect_all);
        tvEmptyView = findViewById(R.id.tv_empty_view);

        Log.d(TAG, "========== initViews 开始 ==========");
        Log.d(TAG, "RecyclerView: " + (recyclerView != null ? "找到" : "未找到"));
        Log.d(TAG, "tvEmptyView: " + (tvEmptyView != null ? "找到" : "未找到"));

        // 设置RecyclerView
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        Log.d(TAG, "LinearLayoutManager已设置");

        styleList = new ArrayList<>();
        adapter = new StyleManagementAdapter(this, styleList, new StyleManagementAdapter.OnItemClickListener() {
            @Override
            public void onEnableClick(StyleConfig style) {
                configManager.setStyleEnabled(style.getStyleId(), true);
                Toast.makeText(StyleManagementActivity.this,
                    "已启用: " + style.getName(), Toast.LENGTH_SHORT).show();
                // 刷新列表以更新状态显示
                adapter.notifyDataSetChanged();
            }

            @Override
            public void onDisableClick(StyleConfig style) {
                configManager.setStyleEnabled(style.getStyleId(), false);
                Toast.makeText(StyleManagementActivity.this,
                    "已禁用: " + style.getName(), Toast.LENGTH_SHORT).show();
                // 刷新列表以更新状态显示
                adapter.notifyDataSetChanged();
            }

            @Override
            public void onDeleteClick(StyleConfig style) {
                configManager.setStyleEnabled(style.getStyleId(), false);
                Toast.makeText(StyleManagementActivity.this,
                    "已删除: " + style.getName(), Toast.LENGTH_SHORT).show();
                // 刷新列表以更新状态显示
                adapter.notifyDataSetChanged();
            }
        });

        recyclerView.setAdapter(adapter);
        Log.d(TAG, "Adapter已设置到RecyclerView");
        Log.d(TAG, "RecyclerView可见性: " + recyclerView.getVisibility());
        Log.d(TAG, "RecyclerView宽度: " + recyclerView.getWidth() + ", 高度: " + recyclerView.getHeight());
        Log.d(TAG, "========== initViews 完成 ==========");
    }

    @Override
    protected void onResume() {
        super.onResume();
        // 每次返回时重新加载，确保配置最新
        loadStyles();
    }

    private void loadStyles() {
        Log.d(TAG, "========== 开始加载风格配置 ==========");

        // 先检查ConfigManager中的styleConfigs数量
        Log.d(TAG, "调用getAllStyleConfigs之前");

        // 加载所有风格（包括禁用的）
        List<StyleConfig> allStyles = configManager.getAllStyleConfigs();
        Log.d(TAG, "从ConfigManager获取到 " + (allStyles != null ? allStyles.size() : "null") + " 个风格");

        // 打印每个风格的详细信息
        if (allStyles != null && !allStyles.isEmpty()) {
            for (int i = 0; i < allStyles.size(); i++) {
                StyleConfig style = allStyles.get(i);
                Log.d(TAG, "风格[" + i + "]: " + style.getName() +
                          " (ID: " + style.getStyleId() +
                          ", 预览: " + style.getPreviewImage() +
                          ", 启用: " + style.isEnabled() + ")");
            }
        } else {
            Log.e(TAG, "风格列表为空或null！");
        }

        // 如果为空，尝试重新加载
        if (allStyles == null || allStyles.isEmpty()) {
            Log.w(TAG, "风格列表为空，尝试重新加载ConfigManager");
            configManager.reload();
            allStyles = configManager.getAllStyleConfigs();
            Log.d(TAG, "重新加载后获取到 " + (allStyles != null ? allStyles.size() : 0) + " 个风格");
        }

        styleList.clear();
        if (allStyles != null) {
            styleList.addAll(allStyles);
        }
        Log.d(TAG, "styleList现在有 " + styleList.size() + " 个风格");

        adapter.notifyDataSetChanged();
        Log.d(TAG, "调用了adapter.notifyDataSetChanged()");

        // 显示/隐藏空状态提示
        if (styleList.isEmpty()) {
            recyclerView.setVisibility(View.GONE);
            tvEmptyView.setVisibility(View.VISIBLE);
            tvEmptyView.setText("暂无风格配置\n\n请确保 assets/style/style.json 文件存在且格式正确\n\n当前配置数量: 0");
            Log.w(TAG, "风格列表为空！");
        } else {
            recyclerView.setVisibility(View.VISIBLE);
            tvEmptyView.setVisibility(View.GONE);
            Log.d(TAG, "成功加载 " + styleList.size() + " 个风格");

            // 打印所有风格信息
            for (StyleConfig style : styleList) {
                Log.d(TAG, "风格: " + style.getName() + " (" + style.getStyleId() + "), 预览图: " + style.getPreviewImage());
            }
        }
    }

    private void setupListeners() {
        // 返回按钮
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        // 全选按钮
        btnSelectAll.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                for (StyleConfig style : styleList) {
                    configManager.setStyleEnabled(style.getStyleId(), true);
                }
                adapter.notifyDataSetChanged();
                Toast.makeText(StyleManagementActivity.this, "已启用所有风格", Toast.LENGTH_SHORT).show();
            }
        });

        // 全不选按钮
        btnDeselectAll.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                for (StyleConfig style : styleList) {
                    configManager.setStyleEnabled(style.getStyleId(), false);
                }
                adapter.notifyDataSetChanged();
                Toast.makeText(StyleManagementActivity.this, "已禁用所有风格", Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    protected void onNetworkChanged(boolean isOnline, NetworkUtils.NetworkType type) {
        // 不显示网络提示
    }
}
