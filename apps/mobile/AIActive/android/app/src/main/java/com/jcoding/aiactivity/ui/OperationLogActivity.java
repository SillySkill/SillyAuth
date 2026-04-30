package com.jcoding.aiactivity.ui;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.Filter;
import android.widget.Filterable;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.security.OperationLogger;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * 操作日志Activity
 *
 * 功能：
 * 1. 显示所有操作日志
 * 2. 按用户过滤
 * 3. 按操作类型过滤
 * 4. 按时间范围过滤
 * 5. 清空日志
 */
public class OperationLogActivity extends AppCompatActivity {

    private static final String TAG = "OperationLog";

    // UI组件
    private RecyclerView recyclerView;
    private LogAdapter adapter;
    private Button btnFilterUser;
    private Button btnFilterAction;
    private Button btnFilterTime;
    private Button btnClearLogs;
    private ImageButton btnBack;
    private TextView tvTitle;

    // 数据
    private List<OperationLogger.LogEntry> allLogs;
    private List<OperationLogger.LogEntry> filteredLogs;

    // 过滤条件
    private String filterUser = null;
    private String filterAction = null;
    private Long filterStartTime = null;
    private Long filterEndTime = null;

    // 管理器
    private OperationLogger logger;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_operation_log);

        logger = OperationLogger.getInstance(this);

        initViews();
        loadLogs();
    }

    private void initViews() {
        // 标题栏
        btnBack = findViewById(R.id.btn_back);
        tvTitle = findViewById(R.id.tv_title);
        tvTitle.setText("操作日志");

        // 返回按钮
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        // RecyclerView
        recyclerView = findViewById(R.id.recycler_view);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        // 过滤按钮
        btnFilterUser = findViewById(R.id.btn_filter_user);
        btnFilterAction = findViewById(R.id.btn_filter_action);
        btnFilterTime = findViewById(R.id.btn_filter_time);
        btnClearLogs = findViewById(R.id.btn_clear_logs);

        // 按用户过滤
        btnFilterUser.setOnClickListener(v -> showUserFilterDialog());

        // 按操作类型过滤
        btnFilterAction.setOnClickListener(v -> showActionFilterDialog());

        // 按时间范围过滤
        btnFilterTime.setOnClickListener(v -> showTimeFilterDialog());

        // 清空日志
        btnClearLogs.setOnClickListener(v -> {
            new androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("确认清空")
                .setMessage("确定要清空所有日志吗？此操作不可恢复。")
                .setPositiveButton("清空", (dialog, which) -> {
                    logger.clearLogs();
                    loadLogs();
                    Toast.makeText(this, "日志已清空", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("取消", null)
                .show();
        });
    }

    private void loadLogs() {
        allLogs = logger.getAllLogs();
        filteredLogs = new ArrayList<>(allLogs);

        adapter = new LogAdapter(filteredLogs);
        recyclerView.setAdapter(adapter);

        // 滚动到顶部
        recyclerView.scrollToPosition(0);
    }

    private void applyFilters() {
        filteredLogs = new ArrayList<>(allLogs);

        // 按用户过滤
        if (filterUser != null) {
            filteredLogs = logger.getLogsByUser(filterUser);
        }

        // 按操作类型过滤
        if (filterAction != null) {
            List<OperationLogger.LogEntry> tempLogs = new ArrayList<>();
            for (OperationLogger.LogEntry entry : filteredLogs) {
                if (entry.action.equals(filterAction)) {
                    tempLogs.add(entry);
                }
            }
            filteredLogs = tempLogs;
        }

        // 按时间范围过滤
        if (filterStartTime != null && filterEndTime != null) {
            List<OperationLogger.LogEntry> tempLogs = new ArrayList<>();
            for (OperationLogger.LogEntry entry : filteredLogs) {
                if (entry.timestamp >= filterStartTime && entry.timestamp <= filterEndTime) {
                    tempLogs.add(entry);
                }
            }
            filteredLogs = tempLogs;
        }

        adapter = new LogAdapter(filteredLogs);
        recyclerView.setAdapter(adapter);
    }

    /**
     * 显示用户过滤对话框
     */
    private void showUserFilterDialog() {
        String[] users = getAllUsers();

        new androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("按用户过滤")
            .setItems(users, (dialog, which) -> {
                filterUser = users[which];
                btnFilterUser.setText("用户: " + filterUser);
                applyFilters();
            })
            .setNegativeButton("清除过滤", (dialog, which) -> {
                filterUser = null;
                btnFilterUser.setText("按用户过滤");
                applyFilters();
            })
            .show();
    }

    /**
     * 显示操作类型过滤对话框
     */
    private void showActionFilterDialog() {
        String[] actions = {
            "全部", "登录", "登出", "播放", "暂停", "停止", "跳转",
            "上传媒体", "启用媒体", "禁用媒体", "修改设置",
            "启动服务器", "停止服务器", "客户端连接", "客户端断开"
        };

        new androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("按操作过滤")
            .setItems(actions, (dialog, which) -> {
                if (which == 0) {
                    filterAction = null;
                } else {
                    String actionKey = getActionKey(which);
                    filterAction = actionKey;
                }
                btnFilterAction.setText("操作: " + actions[which]);
                applyFilters();
            })
            .setNegativeButton("清除过滤", (dialog, which) -> {
                filterAction = null;
                btnFilterAction.setText("按操作过滤");
                applyFilters();
            })
            .show();
    }

    /**
     * 显示时间范围过滤对话框
     */
    private void showTimeFilterDialog() {
        String[] timeRanges = {
            "全部", "最近1小时", "最近24小时", "最近7天", "最近30天"
        };

        new androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("按时间过滤")
            .setItems(timeRanges, (dialog, which) -> {
                long now = System.currentTimeMillis();

                switch (which) {
                    case 0:  // 全部
                        filterStartTime = null;
                        filterEndTime = null;
                        break;
                    case 1:  // 最近1小时
                        filterStartTime = now - 60 * 60 * 1000;
                        filterEndTime = now;
                        break;
                    case 2:  // 最近24小时
                        filterStartTime = now - 24 * 60 * 60 * 1000;
                        filterEndTime = now;
                        break;
                    case 3:  // 最近7天
                        filterStartTime = now - 7 * 24 * 60 * 60 * 1000;
                        filterEndTime = now;
                        break;
                    case 4:  // 最近30天
                        filterStartTime = now - 30 * 24 * 60 * 60 * 1000;
                        filterEndTime = now;
                        break;
                }

                btnFilterTime.setText("时间: " + timeRanges[which]);
                applyFilters();
            })
            .setNegativeButton("清除过滤", (dialog, which) -> {
                filterStartTime = null;
                filterEndTime = null;
                btnFilterTime.setText("按时间过滤");
                applyFilters();
            })
            .show();
    }

    private String[] getAllUsers() {
        List<String> userList = new ArrayList<>();
        userList.add("全部");

        for (OperationLogger.LogEntry entry : allLogs) {
            if (!userList.contains(entry.username)) {
                userList.add(entry.username);
            }
        }

        return userList.toArray(new String[0]);
    }

    private String getActionKey(int index) {
        switch (index) {
            case 1: return OperationLogger.ACTION_LOGIN;
            case 2: return OperationLogger.ACTION_LOGOUT;
            case 3: return OperationLogger.ACTION_PLAY;
            case 4: return OperationLogger.ACTION_PAUSE;
            case 5: return OperationLogger.ACTION_STOP;
            case 6: return OperationLogger.ACTION_JUMP;
            case 7: return OperationLogger.ACTION_MEDIA_UPLOAD;
            case 8: return OperationLogger.ACTION_MEDIA_ENABLE;
            case 9: return OperationLogger.ACTION_MEDIA_DISABLE;
            case 10: return OperationLogger.ACTION_SETTINGS_CHANGE;
            case 11: return OperationLogger.ACTION_SERVER_START;
            case 12: return OperationLogger.ACTION_SERVER_STOP;
            case 13: return OperationLogger.ACTION_CLIENT_CONNECT;
            case 14: return OperationLogger.ACTION_CLIENT_DISCONNECT;
            default: return null;
        }
    }

    // ==================== Adapter ====================

    private class LogAdapter extends RecyclerView.Adapter<LogAdapter.LogViewHolder> {

        private List<OperationLogger.LogEntry> logs;
        private SimpleDateFormat timeFormat = new SimpleDateFormat("MM-dd HH:mm:ss", Locale.getDefault());

        public LogAdapter(List<OperationLogger.LogEntry> logs) {
            this.logs = logs;
        }

        @NonNull
        @Override
        public LogViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View view = LayoutInflater.from(parent.getContext()).inflate(
                R.layout.item_log_entry, parent, false);
            return new LogViewHolder(view);
        }

        @Override
        public void onBindViewHolder(@NonNull LogViewHolder holder, int position) {
            holder.bind(logs.get(position));
        }

        @Override
        public int getItemCount() {
            return logs.size();
        }

        class LogViewHolder extends RecyclerView.ViewHolder {
            private TextView tvTime;
            private TextView tvUser;
            private TextView tvAction;
            private TextView tvDetails;
            private TextView tvLevel;
            private View levelIndicator;

            public LogViewHolder(@NonNull View itemView) {
                super(itemView);
                tvTime = itemView.findViewById(R.id.tv_time);
                tvUser = itemView.findViewById(R.id.tv_user);
                tvAction = itemView.findViewById(R.id.tv_action);
                tvDetails = itemView.findViewById(R.id.tv_details);
                tvLevel = itemView.findViewById(R.id.tv_level);
                levelIndicator = itemView.findViewById(R.id.level_indicator);
            }

            public void bind(OperationLogger.LogEntry entry) {
                tvTime.setText(timeFormat.format(new Date(entry.timestamp)));
                tvUser.setText(entry.username);
                tvAction.setText(entry.getActionName());
                tvDetails.setText(entry.details);
                tvLevel.setText(entry.getLevelName());

                // 根据级别设置颜色
                int levelColor = getLevelColor(entry.level);
                tvLevel.setTextColor(levelColor);
                levelIndicator.setBackgroundColor(levelColor);

                // 根据级别设置背景
                int bgColor = getLevelBackgroundColor(entry.level);
                if (bgColor != 0) {
                    itemView.setBackgroundResource(bgColor);
                }
            }

            private int getLevelColor(int level) {
                switch (level) {
                    case OperationLogger.LEVEL_DEBUG:
                        return getResources().getColor(R.color.textSecondary);
                    case OperationLogger.LEVEL_INFO:
                        return getResources().getColor(R.color.textPrimary);
                    case OperationLogger.LEVEL_WARNING:
                        return getResources().getColor(R.color.color_warning);
                    case OperationLogger.LEVEL_ERROR:
                        return getResources().getColor(R.color.color_error);
                    default:
                        return getResources().getColor(R.color.textPrimary);
                }
            }

            private int getLevelBackgroundColor(int level) {
                switch (level) {
                    case OperationLogger.LEVEL_WARNING:
                        return R.drawable.bg_log_warning;
                    case OperationLogger.LEVEL_ERROR:
                        return R.drawable.bg_log_error;
                    default:
                        return 0;
                }
            }
        }
    }
}
