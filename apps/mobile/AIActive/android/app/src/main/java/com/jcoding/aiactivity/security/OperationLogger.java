package com.jcoding.aiactivity.security;

import android.content.Context;
import android.util.Log;

import com.jcoding.aiactivity.utils.PreferenceUtils;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * 操作日志管理器
 *
 * 记录用户操作日志：
 * 1. 登录/登出
 * 2. 播放控制
 * 3. 媒体管理
 * 4. 设置修改
 * 5. 系统操作
 */
public class OperationLogger {

    private static final String TAG = "OperationLogger";
    private static OperationLogger instance;

    private static final int MAX_LOGS = 1000;  // 最多保存1000条日志

    private Context context;
    private SimpleDateFormat dateFormat;

    // 日志级别
    public static final int LEVEL_DEBUG = 0;
    public static final int LEVEL_INFO = 1;
    public static final int LEVEL_WARNING = 2;
    public static final int LEVEL_ERROR = 3;

    // 操作类型
    public static final String ACTION_LOGIN = "login";
    public static final String ACTION_LOGOUT = "logout";
    public static final String ACTION_PLAY = "play";
    public static final String ACTION_PAUSE = "pause";
    public static final String ACTION_STOP = "stop";
    public static final String ACTION_JUMP = "jump";
    public static final String ACTION_MEDIA_UPLOAD = "media_upload";
    public static final String ACTION_MEDIA_ENABLE = "media_enable";
    public static final String ACTION_MEDIA_DISABLE = "media_disable";
    public static final String ACTION_SETTINGS_CHANGE = "settings_change";
    public static final String ACTION_SERVER_START = "server_start";
    public static final String ACTION_SERVER_STOP = "server_stop";
    public static final String ACTION_CLIENT_CONNECT = "client_connect";
    public static final String ACTION_CLIENT_DISCONNECT = "client_disconnect";

    private OperationLogger(Context context) {
        this.context = context.getApplicationContext();
        this.dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
    }

    public static synchronized OperationLogger getInstance(Context context) {
        if (instance == null) {
            instance = new OperationLogger(context);
        }
        return instance;
    }

    /**
     * 记录日志
     */
    public void log(String username, String action, String details) {
        log(username, action, details, LEVEL_INFO);
    }

    /**
     * 记录日志（带级别）
     */
    public void log(String username, String action, String details, int level) {
        try {
            LogEntry entry = new LogEntry();
            entry.timestamp = System.currentTimeMillis();
            entry.username = username != null ? username : "system";
            entry.action = action;
            entry.details = details;
            entry.level = level;

            addLogEntry(entry);

            // 同时输出到Logcat
            String logMsg = String.format("[%s] %s - %s: %s",
                    getLevelString(level), entry.username, action, details);
            switch (level) {
                case LEVEL_DEBUG:
                    Log.d(TAG, logMsg);
                    break;
                case LEVEL_INFO:
                    Log.i(TAG, logMsg);
                    break;
                case LEVEL_WARNING:
                    Log.w(TAG, logMsg);
                    break;
                case LEVEL_ERROR:
                    Log.e(TAG, logMsg);
                    break;
            }

        } catch (Exception e) {
            Log.e(TAG, "记录日志失败", e);
        }
    }

    /**
     * 添加日志条目
     */
    private void addLogEntry(LogEntry entry) {
        try {
            List<LogEntry> logs = getAllLogs();

            // 添加新日志
            logs.add(0, entry);  // 添加到开头

            // 限制日志数量
            if (logs.size() > MAX_LOGS) {
                logs = logs.subList(0, MAX_LOGS);
            }

            saveLogs(logs);

        } catch (Exception e) {
            Log.e(TAG, "添加日志条目失败", e);
        }
    }

    /**
     * 获取所有日志
     */
    public List<LogEntry> getAllLogs() {
        try {
            String json = PreferenceUtils.getString(context, "operation_logs", "[]");
            JSONArray jsonArray = new JSONArray(json);

            List<LogEntry> logs = new ArrayList<>();
            for (int i = 0; i < jsonArray.length(); i++) {
                JSONObject obj = jsonArray.getJSONObject(i);
                LogEntry entry = LogEntry.fromJson(obj);
                logs.add(entry);
            }

            return logs;

        } catch (Exception e) {
            Log.e(TAG, "获取日志失败", e);
            return new ArrayList<>();
        }
    }

    /**
     * 根据用户过滤日志
     */
    public List<LogEntry> getLogsByUser(String username) {
        List<LogEntry> allLogs = getAllLogs();
        List<LogEntry> filteredLogs = new ArrayList<>();

        for (LogEntry entry : allLogs) {
            if (entry.username.equals(username)) {
                filteredLogs.add(entry);
            }
        }

        return filteredLogs;
    }

    /**
     * 根据操作类型过滤日志
     */
    public List<LogEntry> getLogsByAction(String action) {
        List<LogEntry> allLogs = getAllLogs();
        List<LogEntry> filteredLogs = new ArrayList<>();

        for (LogEntry entry : allLogs) {
            if (entry.action.equals(action)) {
                filteredLogs.add(entry);
            }
        }

        return filteredLogs;
    }

    /**
     * 根据时间范围过滤日志
     */
    public List<LogEntry> getLogsByTimeRange(long startTime, long endTime) {
        List<LogEntry> allLogs = getAllLogs();
        List<LogEntry> filteredLogs = new ArrayList<>();

        for (LogEntry entry : allLogs) {
            if (entry.timestamp >= startTime && entry.timestamp <= endTime) {
                filteredLogs.add(entry);
            }
        }

        return filteredLogs;
    }

    /**
     * 清空所有日志
     */
    public void clearLogs() {
        PreferenceUtils.putString(context, "operation_logs", "[]");
        Log.i(TAG, "日志已清空");
    }

    /**
     * 保存日志
     */
    private void saveLogs(List<LogEntry> logs) {
        try {
            JSONArray jsonArray = new JSONArray();
            for (LogEntry entry : logs) {
                jsonArray.put(entry.toJson());
            }

            PreferenceUtils.putString(context, "operation_logs", jsonArray.toString());

        } catch (Exception e) {
            Log.e(TAG, "保存日志失败", e);
        }
    }

    /**
     * 获取级别字符串
     */
    private String getLevelString(int level) {
        switch (level) {
            case LEVEL_DEBUG: return "DEBUG";
            case LEVEL_INFO: return "INFO";
            case LEVEL_WARNING: return "WARN";
            case LEVEL_ERROR: return "ERROR";
            default: return "UNKNOWN";
        }
    }

    /**
     * 日志条目数据类
     */
    public static class LogEntry {
        public long timestamp;
        public String username;
        public String action;
        public String details;
        public int level;

        public static LogEntry fromJson(JSONObject obj) {
            LogEntry entry = new LogEntry();
            try {
                entry.timestamp = obj.optLong("timestamp", System.currentTimeMillis());
                entry.username = obj.optString("username", "system");
                entry.action = obj.optString("action", "");
                entry.details = obj.optString("details", "");
                entry.level = obj.optInt("level", LEVEL_INFO);
            } catch (Exception e) {
                Log.e("LogEntry", "解析JSON失败", e);
            }
            return entry;
        }

        public JSONObject toJson() {
            JSONObject obj = new JSONObject();
            try {
                obj.put("timestamp", timestamp);
                obj.put("username", username);
                obj.put("action", action);
                obj.put("details", details);
                obj.put("level", level);
            } catch (Exception e) {
                Log.e("LogEntry", "转换为JSON失败", e);
            }
            return obj;
        }

        /**
         * 获取格式化的时间字符串
         */
        public String getFormattedTime() {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
            return sdf.format(new Date(timestamp));
        }

        /**
         * 获取操作类型名称
         */
        public String getActionName() {
            switch (action) {
                case ACTION_LOGIN: return "登录";
                case ACTION_LOGOUT: return "登出";
                case ACTION_PLAY: return "播放";
                case ACTION_PAUSE: return "暂停";
                case ACTION_STOP: return "停止";
                case ACTION_JUMP: return "跳转";
                case ACTION_MEDIA_UPLOAD: return "上传媒体";
                case ACTION_MEDIA_ENABLE: return "启用媒体";
                case ACTION_MEDIA_DISABLE: return "禁用媒体";
                case ACTION_SETTINGS_CHANGE: return "修改设置";
                case ACTION_SERVER_START: return "启动服务器";
                case ACTION_SERVER_STOP: return "停止服务器";
                case ACTION_CLIENT_CONNECT: return "客户端连接";
                case ACTION_CLIENT_DISCONNECT: return "客户端断开";
                default: return action;
            }
        }

        /**
         * 获取级别名称
         */
        public String getLevelName() {
            switch (level) {
                case LEVEL_DEBUG: return "调试";
                case LEVEL_INFO: return "信息";
                case LEVEL_WARNING: return "警告";
                case LEVEL_ERROR: return "错误";
                default: return "未知";
            }
        }
    }
}
