package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.jcoding.aiactivity.network.ApiService;
import com.jcoding.aiactivity.network.RetrofitClient;
import com.jcoding.aiactivity.utils.NetworkUtils;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import retrofit2.Call;
import retrofit2.Callback;

/**
 * 配置同步管理器 - 完整实现
 * 支持版本检查、文件下载、MD5校验、断点续传
 */
public class ConfigSyncManager {

    private static final String TAG = "ConfigSyncManager";

    // SharedPreferences
    private static final String PREF_NAME = "config_sync";
    private static final String KEY_VERSION = "current_version";
    private static final String KEY_VERSION_CODE = "current_version_code";
    private static final String KEY_LAST_CHECK = "last_check_time";
    private static final String KEY_LAST_UPDATE = "last_update_time";
    private static final String KEY_FILE_HASHES = "file_hashes";

    // 配置
    private static final int MAX_CONCURRENT_DOWNLOADS = 3;
    private static final int DOWNLOAD_TIMEOUT_SECONDS = 120;
    private static final int BUFFER_SIZE = 8192;

    private static ConfigSyncManager instance;
    private final Context context;
    private final SharedPreferences prefs;
    private final ExecutorService executor;
    private final Handler mainHandler;
    private final OkHttpClient httpClient;

    // 配置存储目录
    private final File configDir;

    // 同步状态
    private volatile boolean isSyncing = false;
    private final Map<String, Long> downloadProgress = new ConcurrentHashMap<>();

    private ConfigSyncManager(Context context) {
        this.context = context.getApplicationContext();
        this.prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        this.executor = Executors.newFixedThreadPool(MAX_CONCURRENT_DOWNLOADS);
        this.mainHandler = new Handler(Looper.getMainLooper());

        // 配置HTTP客户端
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(DOWNLOAD_TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build();

        // 配置存储目录（使用外部存储，避免assets只读限制）
        this.configDir = new File(context.getExternalFilesDir(null), "config");
        if (!configDir.exists()) {
            configDir.mkdirs();
        }

        // 创建子目录
        new File(configDir, "style").mkdirs();
        new File(configDir, "question").mkdirs();
        new File(configDir, "lottery").mkdirs();
        new File(configDir, "aibeing").mkdirs();

        Log.d(TAG, "配置同步管理器初始化完成，存储路径: " + configDir.getAbsolutePath());
    }

    public static synchronized ConfigSyncManager getInstance(Context context) {
        if (instance == null) {
            instance = new ConfigSyncManager(context);
        }
        return instance;
    }

    /**
     * 检查并更新配置
     */
    public void checkAndUpdate(ConfigUpdateCallback callback) {
        if (isSyncing) {
            notifyError(callback, "正在同步中，请稍后再试");
            return;
        }

        // 检查网络状态
        if (!NetworkUtils.isOnline(context)) {
            notifyError(callback, "无网络连接");
            return;
        }

        isSyncing = true;
        Log.i(TAG, "开始检查配置更新...");

        // 获取最新版本信息
        RetrofitClient.getInstance().getApiService()
                .getConfigVersion()
                .enqueue(new Callback<ApiService.ConfigVersionResponse>() {
                    @Override
                    public void onResponse(Call<ApiService.ConfigVersionResponse> call,
                                         retrofit2.Response<ApiService.ConfigVersionResponse> response) {
                        if (response.isSuccessful() && response.body() != null
                                && response.body().code == 200) {
                            ApiService.ConfigVersionResponse.Data versionInfo = response.body().data;
                            executor.execute(() -> processVersionInfo(versionInfo, callback));
                        } else {
                            isSyncing = false;
                            notifyError(callback, "获取版本信息失败");
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiService.ConfigVersionResponse> call, Throwable t) {
                        isSyncing = false;
                        notifyError(callback, "网络请求失败: " + t.getMessage());
                    }
                });
    }

    /**
     * 处理版本信息并决定是否需要更新
     */
    private void processVersionInfo(ApiService.ConfigVersionResponse.Data versionInfo,
                                    ConfigUpdateCallback callback) {
        try {
            String currentVersion = getCurrentVersion();
            int currentVersionCode = getCurrentVersionCode();
            String latestVersion = versionInfo.version;
            int latestVersionCode = versionInfo.version_code;

            Log.i(TAG, String.format("当前版本: %s (%d), 最新版本: %s (%d)",
                    currentVersion, currentVersionCode, latestVersion, latestVersionCode));

            // 检查是否需要更新
            if (latestVersionCode <= currentVersionCode) {
                isSyncing = false;
                Log.i(TAG, "当前已是最新版本");
                notifySuccess(callback, false, "当前已是最新版本");
                return;
            }

            // 检查最低兼容版本
            if (versionInfo.min_compatible_version != null) {
                String minVersion = versionInfo.min_compatible_version;
                if (!isCompatible(currentVersion, minVersion)) {
                    isSyncing = false;
                    notifyError(callback, "应用版本过低，请更新应用");
                    return;
                }
            }

            // 需要更新，开始下载
            Log.i(TAG, "发现新版本，开始下载...");

            // 解析文件列表
            List<FileInfo> files = parseFiles(versionInfo);
            List<String> deletedFiles = parseDeletedFiles(versionInfo);

            // 备份当前配置
            backupCurrentConfig();
            Log.i(TAG, "当前配置已备份");

            // 下载文件
            boolean success = downloadFiles(files, latestVersion, callback);

            if (success) {
                // 删除过期的文件
                deleteFiles(deletedFiles);

                // 更新版本信息
                saveVersion(latestVersion, latestVersionCode);

                // 保存文件哈希
                saveFileHashes(files);

                // 重新加载配置
                ConfigManager.getInstance(context).reload();

                // 上报更新结果
                reportUpdate(currentVersion, latestVersion, true, files.size());

                isSyncing = false;
                Log.i(TAG, "配置更新成功");
                notifySuccess(callback, true, "配置更新成功");
            } else {
                // 下载失败，恢复备份
                Log.e(TAG, "文件下载失败，正在恢复备份...");
                restoreBackup();
                isSyncing = false;
                notifyError(callback, "文件下载失败，已恢复原配置");
            }

        } catch (Exception e) {
            Log.e(TAG, "处理版本信息失败", e);
            isSyncing = false;
            notifyError(callback, "处理版本信息失败: " + e.getMessage());
        }
    }

    /**
     * 解析文件列表
     */
    private List<FileInfo> parseFiles(ApiService.ConfigVersionResponse.Data versionInfo) {
        List<FileInfo> files = new ArrayList<>();

        if (versionInfo.files == null) {
            return files;
        }

        try {
            JSONArray jsonArray = new JSONArray(versionInfo.files);
            for (int i = 0; i < jsonArray.length(); i++) {
                JSONObject fileObj = jsonArray.getJSONObject(i);
                FileInfo fileInfo = new FileInfo();
                fileInfo.path = fileObj.getString("path");
                fileInfo.size = fileObj.optLong("size", 0);
                fileInfo.md5 = fileObj.getString("md5");
                fileInfo.url = fileObj.getString("url");
                fileInfo.compressed = fileObj.optBoolean("compressed", false);
                fileInfo.essential = fileObj.optBoolean("essential", true);
                files.add(fileInfo);
            }
        } catch (JSONException e) {
            Log.e(TAG, "解析文件列表失败", e);
        }

        return files;
    }

    /**
     * 解析删除文件列表
     */
    private List<String> parseDeletedFiles(ApiService.ConfigVersionResponse.Data versionInfo) {
        // 暂时返回空列表，因为ConfigVersionResponse.Data中没有deleted_files字段
        // 如需支持，需要先在ApiService.ConfigVersionResponse.Data中添加deleted_files字段
        return new ArrayList<>();
    }

    /**
     * 下载文件列表
     */
    private boolean downloadFiles(List<FileInfo> files, String version,
                                  ConfigUpdateCallback callback) {
        int total = files.size();
        int downloaded = 0;
        int failed = 0;

        for (FileInfo file : files) {
            // 检查是否已下载且未更改
            if (isFileUpToDate(file)) {
                Log.d(TAG, "跳过未更改的文件: " + file.path);
                downloaded++;
                continue;
            }

            // 下载文件
            boolean success = downloadFile(file, version);

            if (success) {
                downloaded++;
                // 通知进度
                int progress = (int) ((downloaded * 100.0) / total);
                notifyProgress(callback, progress, String.format("下载中 %d/%d", downloaded, total));
            } else {
                failed++;
                if (file.essential) {
                    // 必需文件下载失败，终止更新
                    Log.e(TAG, "必需文件下载失败: " + file.path);
                    return false;
                }
            }
        }

        return failed == 0;
    }

    /**
     * 下载单个文件
     */
    private boolean downloadFile(FileInfo fileInfo, String version) {
        Log.d(TAG, "开始下载: " + fileInfo.path);

        File outputFile = new File(configDir, fileInfo.path);
        outputFile.getParentFile().mkdirs();

        // 如果支持断点续传且文件已部分下载
        long downloadedBytes = 0;
        if (outputFile.exists()) {
            downloadedBytes = outputFile.length();
        }

        // 构建请求（支持断点续传）
        Request.Builder requestBuilder = new Request.Builder()
                .url(buildDownloadUrl(fileInfo.url, version));

        if (downloadedBytes > 0) {
            requestBuilder.addHeader("Range", "bytes=" + downloadedBytes + "-");
        }

        Request request = requestBuilder.build();

        InputStream inputStream = null;
        FileOutputStream outputStream = null;

        try {
            Response response = httpClient.newCall(request).execute();

            if (!response.isSuccessful() && response.code() != 206) {
                Log.e(TAG, "下载失败: " + response.code());
                return false;
            }

            inputStream = new BufferedInputStream(response.body().byteStream());
            outputStream = new FileOutputStream(outputFile, downloadedBytes > 0);

            byte[] buffer = new byte[BUFFER_SIZE];
            int bytesRead;
            long totalBytesRead = downloadedBytes;

            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
                totalBytesRead += bytesRead;

                // 更新下载进度
                downloadProgress.put(fileInfo.path, totalBytesRead);
            }

            outputStream.flush();

            // 验证MD5
            try {
                String actualMd5 = calculateMd5(outputFile);
                if (!actualMd5.equalsIgnoreCase(fileInfo.md5)) {
                    Log.e(TAG, String.format("MD5校验失败: %s, 期望: %s, 实际: %s",
                            fileInfo.path, fileInfo.md5, actualMd5));
                    outputFile.delete();
                    return false;
                }
            } catch (Exception e) {
                Log.e(TAG, "MD5计算失败: " + fileInfo.path, e);
                outputFile.delete();
                return false;
            }

            Log.d(TAG, "下载成功: " + fileInfo.path);
            return true;

        } catch (IOException e) {
            Log.e(TAG, "下载文件异常: " + fileInfo.path, e);
            return false;
        } finally {
            try {
                if (inputStream != null) inputStream.close();
                if (outputStream != null) outputStream.close();
            } catch (IOException e) {
                Log.e(TAG, "关闭流失败", e);
            }
        }
    }

    /**
     * 构建下载URL
     */
    private String buildDownloadUrl(String relativeUrl, String version) {
        // 使用与RetrofitClient相同的BASE_URL
        String baseUrl = "https://www.jcoding.chat/application/com.jcoding.aiactivity/";
        if (relativeUrl.startsWith("/")) {
            return baseUrl + relativeUrl.substring(1); // 移除开头的/
        }
        return baseUrl + "api/config/file?version=" + version + "&path=" + relativeUrl;
    }

    /**
     * 检查文件是否已更新
     */
    private boolean isFileUpToDate(FileInfo fileInfo) {
        File file = new File(configDir, fileInfo.path);
        if (!file.exists()) {
            return false;
        }

        try {
            String actualMd5 = calculateMd5(file);
            return actualMd5.equalsIgnoreCase(fileInfo.md5);
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 计算文件MD5
     */
    private String calculateMd5(File file) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        InputStream inputStream = null;

        try {
            inputStream = new java.io.FileInputStream(file);
            byte[] buffer = new byte[BUFFER_SIZE];
            int bytesRead;

            while ((bytesRead = inputStream.read(buffer)) != -1) {
                md.update(buffer, 0, bytesRead);
            }

        } finally {
            if (inputStream != null) {
                inputStream.close();
            }
        }

        byte[] digest = md.digest();
        StringBuilder sb = new StringBuilder();
        for (byte b : digest) {
            sb.append(String.format("%02x", b));
        }

        return sb.toString();
    }

    /**
     * 删除文件
     */
    private void deleteFiles(List<String> filePaths) {
        for (String path : filePaths) {
            File file = new File(configDir, path);
            if (file.exists()) {
                if (file.delete()) {
                    Log.d(TAG, "已删除文件: " + path);
                } else {
                    Log.w(TAG, "删除文件失败: " + path);
                }
            }
        }
    }

    /**
     * 保存文件哈希
     */
    private void saveFileHashes(List<FileInfo> files) {
        try {
            JSONObject hashes = new JSONObject();
            for (FileInfo file : files) {
                hashes.put(file.path, file.md5);
            }
            prefs.edit().putString(KEY_FILE_HASHES, hashes.toString()).apply();
        } catch (Exception e) {
            Log.e(TAG, "保存文件哈希失败", e);
        }
    }

    /**
     * 检查版本兼容性
     */
    private boolean isCompatible(String currentVersion, String minVersion) {
        // 简化版本比较
        String current = currentVersion.replace("v", "").replace(".", "");
        String min = minVersion.replace("v", "").replace(".", "");

        try {
            int currentCode = Integer.parseInt(current);
            int minCode = Integer.parseInt(min);
            return currentCode >= minCode;
        } catch (NumberFormatException e) {
            return true;
        }
    }

    /**
     * 上报更新结果
     */
    private void reportUpdate(String oldVersion, String newVersion, boolean success, int fileCount) {
        executor.execute(() -> {
            try {
                // 构建报告数据Map
                Map<String, Object> report = new java.util.HashMap<>();
                report.put("device_id", getDeviceId());
                report.put("old_version", oldVersion);
                report.put("new_version", newVersion);
                report.put("status", success ? "success" : "failed");
                report.put("downloaded_files", fileCount);
                report.put("failed_files", new java.util.ArrayList<>());
                report.put("duration_ms", 0);

                RetrofitClient.getInstance().getApiService()
                        .reportUpdateResult(report)
                        .enqueue(new Callback<ApiService.BasicResponse>() {
                            @Override
                            public void onResponse(Call<ApiService.BasicResponse> call,
                                                 retrofit2.Response<ApiService.BasicResponse> response) {
                                if (response.isSuccessful() && response.body() != null
                                        && response.body().code == 200) {
                                    Log.i(TAG, "更新结果上报成功");
                                }
                            }

                            @Override
                            public void onFailure(Call<ApiService.BasicResponse> call, Throwable t) {
                                Log.e(TAG, "更新结果上报失败", t);
                            }
                        });
            } catch (Exception e) {
                Log.e(TAG, "上报更新结果异常", e);
            }
        });
    }

    /**
     * 获取设备唯一标识
     */
    private String getDeviceId() {
        return android.provider.Settings.Secure.getString(
                context.getContentResolver(),
                android.provider.Settings.Secure.ANDROID_ID
        );
    }

    /**
     * 获取当前版本号
     */
    public String getCurrentVersion() {
        return prefs.getString(KEY_VERSION, "v1.0.0");
    }

    /**
     * 获取当前版本代码
     */
    public int getCurrentVersionCode() {
        return prefs.getInt(KEY_VERSION_CODE, 100);
    }

    /**
     * 保存版本号
     */
    private void saveVersion(String version, int versionCode) {
        prefs.edit()
                .putString(KEY_VERSION, version)
                .putInt(KEY_VERSION_CODE, versionCode)
                .putLong(KEY_LAST_CHECK, System.currentTimeMillis())
                .putLong(KEY_LAST_UPDATE, System.currentTimeMillis())
                .apply();

        Log.d(TAG, String.format("版本已更新: %s (%d)", version, versionCode));
    }

    /**
     * 获取配置文件路径
     */
    public File getConfigDir() {
        return configDir;
    }

    /**
     * 释放资源
     */
    public void release() {
        if (executor != null && !executor.isShutdown()) {
            executor.shutdown();
        }
    }

    // ========== 备份和恢复方法 ==========

    /**
     * 备份当前配置
     */
    private void backupCurrentConfig() {
        try {
            File backupDir = new File(context.getExternalFilesDir(null), "config_backup");
            deleteDirectory(backupDir);
            copyDirectory(configDir, backupDir);
            Log.i(TAG, "Config backed up to: " + backupDir.getAbsolutePath());
        } catch (Exception e) {
            Log.e(TAG, "Failed to backup config", e);
        }
    }

    /**
     * 恢复备份的配置
     */
    private void restoreBackup() {
        try {
            File backupDir = new File(context.getExternalFilesDir(null), "config_backup");
            if (!backupDir.exists()) {
                Log.w(TAG, "No backup found to restore");
                return;
            }

            deleteDirectory(configDir);
            copyDirectory(backupDir, configDir);
            Log.i(TAG, "Config restored from backup");
        } catch (Exception e) {
            Log.e(TAG, "Failed to restore backup", e);
        }
    }

    /**
     * 递归删除目录
     */
    private void deleteDirectory(File directory) {
        if (directory == null || !directory.exists()) {
            return;
        }

        File[] files = directory.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.isDirectory()) {
                    deleteDirectory(file);
                } else {
                    file.delete();
                }
            }
        }
        directory.delete();
    }

    /**
     * 递归复制目录
     */
    private void copyDirectory(File source, File target) throws IOException {
        if (source == null || !source.exists()) {
            return;
        }

        target.mkdirs();

        File[] files = source.listFiles();
        if (files != null) {
            for (File file : files) {
                File targetFile = new File(target, file.getName());
                if (file.isDirectory()) {
                    copyDirectory(file, targetFile);
                } else {
                    copyFile(file, targetFile);
                }
            }
        }
    }

    /**
     * 复制文件
     */
    private void copyFile(File source, File target) throws IOException {
        try (java.io.FileInputStream fis = new java.io.FileInputStream(source);
             java.io.FileOutputStream fos = new java.io.FileOutputStream(target)) {
            byte[] buffer = new byte[8192];
            int len;
            while ((len = fis.read(buffer)) > 0) {
                fos.write(buffer, 0, len);
            }
        }
    }

    // ========== 回调通知方法 ==========

    private void notifySuccess(ConfigUpdateCallback callback, boolean updated, String message) {
        if (callback != null) {
            mainHandler.post(() -> callback.onSuccess(updated, message));
        }
    }

    private void notifyError(ConfigUpdateCallback callback, String error) {
        if (callback != null) {
            mainHandler.post(() -> callback.onError(error));
        }
    }

    private void notifyProgress(ConfigUpdateCallback callback, int progress, String message) {
        if (callback != null) {
            mainHandler.post(() -> callback.onProgress(progress, message));
        }
    }

    // ========== 回调接口 ==========

    public interface ConfigUpdateCallback {
        void onSuccess(boolean updated, String message);
        void onError(String error);
        void onProgress(int progress, String message);
    }

    // ========== 内部类 ==========

    private static class FileInfo {
        String path;
        long size;
        String md5;
        String url;
        boolean compressed;
        boolean essential;
    }
}
