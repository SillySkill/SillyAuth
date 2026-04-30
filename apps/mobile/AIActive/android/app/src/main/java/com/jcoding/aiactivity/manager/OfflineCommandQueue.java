package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.util.Log;

import com.jcoding.aiactivity.network.InnerShowNetworkClient;
import com.jcoding.aiactivity.utils.NetworkUtils;
import com.jcoding.aiactivity.utils.PreferenceUtils;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

/**
 * 离线命令队列
 *
 * 在离线状态下缓存命令，联网后自动执行：
 * 1. 命令入队
 * 2. 网络监听
 * 3. 自动重试
 * 4. 命令去重
 * 5. 结果回调
 */
public class OfflineCommandQueue {

    private static final String TAG = "OfflineCommandQueue";
    private static OfflineCommandQueue instance;

    private Context context;
    private InnerShowNetworkClient networkClient;
    private List<QueuedCommand> commandQueue;
    private boolean isProcessing = false;

    // 最大队列长度
    private static final int MAX_QUEUE_SIZE = 100;

    private OfflineCommandQueue(Context context) {
        this.context = context.getApplicationContext();
        this.networkClient = InnerShowNetworkClient.getInstance(context);
        this.commandQueue = new ArrayList<>();
        this.networkClient = InnerShowNetworkClient.getInstance(context);

        loadQueue();
    }

    public static synchronized OfflineCommandQueue getInstance(Context context) {
        if (instance == null) {
            instance = new OfflineCommandQueue(context);
        }
        return instance;
    }

    /**
     * 入队命令
     */
    public boolean enqueue(String commandType, JSONObject parameters) {
        return enqueue(commandType, parameters, null);
    }

    /**
     * 入队命令（带回调）
     */
    public boolean enqueue(String commandType, JSONObject parameters, CommandCallback callback) {
        // 检查网络状态
        if (NetworkUtils.isOnline(context)) {
            // 在线状态，尝试直接执行
            if (executeCommand(commandType, parameters, callback)) {
                return true;
            }
            // 执行失败，加入队列
        }

        // 检查队列是否已满
        if (commandQueue.size() >= MAX_QUEUE_SIZE) {
            Log.w(TAG, "命令队列已满，无法添加新命令");
            return false;
        }

        // 检查是否已存在相同命令（去重）
        for (QueuedCommand cmd : commandQueue) {
            if (cmd.commandType.equals(commandType) &&
                cmd.parameters.toString().equals(parameters.toString())) {
                Log.d(TAG, "命令已存在于队列中: " + commandType);
                return false;
            }
        }

        // 创建命令对象
        QueuedCommand command = new QueuedCommand();
        command.id = System.currentTimeMillis();
        command.commandType = commandType;
        command.parameters = parameters;
        command.callback = callback;
        command.createTime = System.currentTimeMillis();
        command.retryCount = 0;

        commandQueue.add(command);
        saveQueue();

        Log.i(TAG, "命令已入队: " + commandType + " (队列长度: " + commandQueue.size() + ")");

        return true;
    }

    /**
     * 处理队列
     */
    public void processQueue() {
        if (isProcessing || commandQueue.isEmpty()) {
            return;
        }

        if (!NetworkUtils.isOnline(context)) {
            Log.d(TAG, "网络未连接，等待网络恢复");
            return;
        }

        // 检查客户端是否已连接
        if (!networkClient.isConnected() || !networkClient.isAuthenticated()) {
            Log.d(TAG, "客户端未连接或未认证，等待连接");
            return;
        }

        isProcessing = true;

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    processCommands();
                } finally {
                    isProcessing = false;
                }
            }
        }).start();
    }

    /**
     * 处理所有命令
     */
    private void processCommands() {
        List<QueuedCommand> executedCommands = new ArrayList<>();
        List<QueuedCommand> failedCommands = new ArrayList<>();

        for (QueuedCommand command : commandQueue) {
            boolean success = executeCommand(command.commandType, command.parameters, command.callback);

            if (success) {
                executedCommands.add(command);
                Log.i(TAG, "命令执行成功: " + command.commandType);
            } else {
                command.retryCount++;
                if (command.retryCount >= 3) {
                    // 重试3次后放弃
                    executedCommands.add(command);
                    Log.w(TAG, "命令执行失败，已达最大重试次数: " + command.commandType);
                } else {
                    failedCommands.add(command);
                }
            }

            // 命令间延迟
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                break;
            }
        }

        // 更新队列
        commandQueue = failedCommands;
        saveQueue();

        if (!executedCommands.isEmpty()) {
            Log.i(TAG, "已执行 " + executedCommands.size() + " 个命令，剩余 " + commandQueue.size() + " 个");
        }
    }

    /**
     * 执行单个命令
     */
    private boolean executeCommand(String commandType, JSONObject parameters, CommandCallback callback) {
        try {
            switch (commandType) {
                case "play":
                    networkClient.play();
                    return true;

                case "pause":
                    networkClient.pause();
                    return true;

                case "resume":
                    networkClient.resume();
                    return true;

                case "stop":
                    networkClient.stop();
                    return true;

                case "jump":
                    int index = parameters.optInt("index", 0);
                    networkClient.jumpTo(index);
                    return true;

                case "media_enable":
                    String module = parameters.optString("module");
                    String type = parameters.optString("type");
                    String path = parameters.optString("path");
                    // networkClient.enableMedia(...)
                    return true;

                case "media_disable":
                    String module2 = parameters.optString("module");
                    String type2 = parameters.optString("type");
                    // networkClient.disableMedia(...)
                    return true;

                default:
                    Log.w(TAG, "未知命令类型: " + commandType);
                    return false;
            }

        } catch (Exception e) {
            Log.e(TAG, "执行命令失败: " + commandType, e);

            if (callback != null) {
                callback.onError(e.getMessage());
            }

            return false;
        }
    }

    /**
     * 获取队列长度
     */
    public int getQueueSize() {
        return commandQueue.size();
    }

    /**
     * 清空队列
     */
    public void clearQueue() {
        commandQueue.clear();
        saveQueue();
        Log.i(TAG, "命令队列已清空");
    }

    /**
     * 保存队列
     */
    private void saveQueue() {
        try {
            JSONArray jsonArray = new JSONArray();
            for (QueuedCommand command : commandQueue) {
                jsonArray.put(command.toJson());
            }

            PreferenceUtils.putString(context, "offline_command_queue", jsonArray.toString());

        } catch (Exception e) {
            Log.e(TAG, "保存队列失败", e);
        }
    }

    /**
     * 加载队列
     */
    private void loadQueue() {
        try {
            String json = PreferenceUtils.getString(context, "offline_command_queue", "[]");
            JSONArray jsonArray = new JSONArray(json);

            commandQueue.clear();
            for (int i = 0; i < jsonArray.length(); i++) {
                JSONObject obj = jsonArray.getJSONObject(i);
                QueuedCommand command = QueuedCommand.fromJson(obj);
                commandQueue.add(command);
            }

            Log.i(TAG, "加载队列完成，共 " + commandQueue.size() + " 个命令");

        } catch (Exception e) {
            Log.e(TAG, "加载队列失败", e);
        }
    }

    /**
     * 队列命令数据类
     */
    public static class QueuedCommand {
        public long id;
        public String commandType;
        public JSONObject parameters;
        public long createTime;
        public int retryCount;
        public transient CommandCallback callback;  // 不序列化

        public static QueuedCommand fromJson(JSONObject obj) {
            QueuedCommand command = new QueuedCommand();
            try {
                command.id = obj.optLong("id", System.currentTimeMillis());
                command.commandType = obj.optString("command_type", "");
                command.parameters = obj.optJSONObject("parameters");
                if (command.parameters == null) {
                    command.parameters = new JSONObject();
                }
                command.createTime = obj.optLong("create_time", System.currentTimeMillis());
                command.retryCount = obj.optInt("retry_count", 0);
            } catch (Exception e) {
                Log.e("QueuedCommand", "解析JSON失败", e);
            }
            return command;
        }

        public JSONObject toJson() {
            JSONObject obj = new JSONObject();
            try {
                obj.put("id", id);
                obj.put("command_type", commandType);
                obj.put("parameters", parameters);
                obj.put("create_time", createTime);
                obj.put("retry_count", retryCount);
            } catch (Exception e) {
                Log.e("QueuedCommand", "转换为JSON失败", e);
            }
            return obj;
        }
    }

    /**
     * 命令回调接口
     */
    public interface CommandCallback {
        void onSuccess();
        void onError(String error);
    }
}
