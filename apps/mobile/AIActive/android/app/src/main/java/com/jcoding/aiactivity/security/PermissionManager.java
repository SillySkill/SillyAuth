package com.jcoding.aiactivity.security;

import android.content.Context;
import android.util.Log;

import com.jcoding.aiactivity.utils.PreferenceUtils;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

/**
 * 权限管理器
 *
 * 管理用户权限和操作权限：
 * 1. 用户角色管理（管理员、操作员、观察员）
 * 2. 操作权限控制
 * 3. 权限验证
 * 4. 操作日志记录
 */
public class PermissionManager {

    private static final String TAG = "PermissionManager";
    private static PermissionManager instance;

    private Context context;

    // 角色定义
    public static final String ROLE_ADMIN = "admin";           // 管理员：所有权限
    public static final String ROLE_OPERATOR = "operator";     // 操作员：播放控制权限
    public static final String ROLE_OBSERVER = "observer";     // 观察员：仅查看权限

    // 操作权限
    public static final String PERM_PLAY_CONTROL = "play_control";        // 播放控制
    public static final String PERM_MEDIA_MANAGE = "media_manage";        // 媒体管理
    public static final String PERM_SETTINGS = "settings";                // 系统设置
    public static final String PERM_USER_MANAGE = "user_manage";          // 用户管理
    public static final String PERM_LOG_VIEW = "log_view";                // 日志查看
    public static final String PERM_SERVER_CONTROL = "server_control";    // 服务器控制

    private PermissionManager(Context context) {
        this.context = context.getApplicationContext();
        initializeDefaultRoles();
    }

    public static synchronized PermissionManager getInstance(Context context) {
        if (instance == null) {
            instance = new PermissionManager(context);
        }
        return instance;
    }

    /**
     * 初始化默认角色
     */
    private void initializeDefaultRoles() {
        // 确保至少有一个管理员
        if (!hasUser("admin")) {
            createUser("admin", "管理员", ROLE_ADMIN);
        }
    }

    /**
     * 创建用户
     */
    public boolean createUser(String username, String displayName, String role) {
        try {
            List<UserInfo> users = getAllUsers();

            // 检查用户是否已存在
            for (UserInfo user : users) {
                if (user.username.equals(username)) {
                    Log.w(TAG, "用户已存在: " + username);
                    return false;
                }
            }

            // 创建新用户
            UserInfo newUser = new UserInfo();
            newUser.username = username;
            newUser.displayName = displayName;
            newUser.role = role;
            newUser.createTime = System.currentTimeMillis();
            newUser.enabled = true;

            users.add(newUser);
            saveUsers(users);

            Log.i(TAG, "用户已创建: " + username + " (" + role + ")");
            return true;

        } catch (Exception e) {
            Log.e(TAG, "创建用户失败", e);
            return false;
        }
    }

    /**
     * 删除用户
     */
    public boolean deleteUser(String username) {
        // 不能删除admin用户
        if ("admin".equals(username)) {
            Log.w(TAG, "不能删除admin用户");
            return false;
        }

        try {
            List<UserInfo> users = getAllUsers();

            for (int i = 0; i < users.size(); i++) {
                if (users.get(i).username.equals(username)) {
                    users.remove(i);
                    saveUsers(users);

                    Log.i(TAG, "用户已删除: " + username);
                    return true;
                }
            }

            return false;

        } catch (Exception e) {
            Log.e(TAG, "删除用户失败", e);
            return false;
        }
    }

    /**
     * 检查用户是否存在
     */
    public boolean hasUser(String username) {
        List<UserInfo> users = getAllUsers();
        for (UserInfo user : users) {
            if (user.username.equals(username)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 获取用户信息
     */
    public UserInfo getUser(String username) {
        List<UserInfo> users = getAllUsers();
        for (UserInfo user : users) {
            if (user.username.equals(username)) {
                return user;
            }
        }
        return null;
    }

    /**
     * 获取所有用户
     */
    public List<UserInfo> getAllUsers() {
        try {
            String json = PreferenceUtils.getString(context, "users_json", "[]");
            JSONArray jsonArray = new JSONArray(json);

            List<UserInfo> users = new ArrayList<>();
            for (int i = 0; i < jsonArray.length(); i++) {
                JSONObject obj = jsonArray.getJSONObject(i);
                UserInfo user = UserInfo.fromJson(obj);
                users.add(user);
            }

            return users;

        } catch (Exception e) {
            Log.e(TAG, "获取用户列表失败", e);
            return new ArrayList<>();
        }
    }

    /**
     * 保存用户列表
     */
    private void saveUsers(List<UserInfo> users) {
        try {
            JSONArray jsonArray = new JSONArray();
            for (UserInfo user : users) {
                jsonArray.put(user.toJson());
            }

            PreferenceUtils.putString(context, "users_json", jsonArray.toString());

        } catch (Exception e) {
            Log.e(TAG, "保存用户列表失败", e);
        }
    }

    /**
     * 检查用户权限
     */
    public boolean hasUserPermission(String username, String permission) {
        UserInfo user = getUser(username);
        if (user == null || !user.enabled) {
            return false;
        }

        return hasPermission(user.role, permission);
    }

    /**
     * 检查角色是否有权限
     */
    public boolean hasPermission(String role, String permission) {
        switch (role) {
            case ROLE_ADMIN:
                // 管理员拥有所有权限
                return true;

            case ROLE_OPERATOR:
                // 操作员权限
                return permission.equals(PERM_PLAY_CONTROL) ||
                       permission.equals(PERM_LOG_VIEW);

            case ROLE_OBSERVER:
                // 观察员权限
                return permission.equals(PERM_LOG_VIEW);

            default:
                return false;
        }
    }

    /**
     * 获取角色的所有权限
     */
    public List<String> getRolePermissions(String role) {
        List<String> permissions = new ArrayList<>();

        if (ROLE_ADMIN.equals(role)) {
            permissions.add(PERM_PLAY_CONTROL);
            permissions.add(PERM_MEDIA_MANAGE);
            permissions.add(PERM_SETTINGS);
            permissions.add(PERM_USER_MANAGE);
            permissions.add(PERM_LOG_VIEW);
            permissions.add(PERM_SERVER_CONTROL);

        } else if (ROLE_OPERATOR.equals(role)) {
            permissions.add(PERM_PLAY_CONTROL);
            permissions.add(PERM_LOG_VIEW);

        } else if (ROLE_OBSERVER.equals(role)) {
            permissions.add(PERM_LOG_VIEW);
        }

        return permissions;
    }

    /**
     * 启用/禁用用户
     */
    public boolean setUserEnabled(String username, boolean enabled) {
        UserInfo user = getUser(username);
        if (user == null) {
            return false;
        }

        user.enabled = enabled;
        saveUsers(getAllUsers());

        Log.i(TAG, "用户已" + (enabled ? "启用" : "禁用") + ": " + username);
        return true;
    }

    /**
     * 修改用户角色
     */
    public boolean setUserRole(String username, String newRole) {
        // 不能修改admin的角色
        if ("admin".equals(username)) {
            Log.w(TAG, "不能修改admin的角色");
            return false;
        }

        UserInfo user = getUser(username);
        if (user == null) {
            return false;
        }

        user.role = newRole;
        saveUsers(getAllUsers());

        Log.i(TAG, "用户角色已修改: " + username + " -> " + newRole);
        return true;
    }

    /**
     * 用户信息数据类
     */
    public static class UserInfo {
        public String username;
        public String displayName;
        public String role;
        public long createTime;
        public boolean enabled;

        public static UserInfo fromJson(JSONObject obj) {
            UserInfo user = new UserInfo();
            try {
                user.username = obj.getString("username");
                user.displayName = obj.getString("display_name");
                user.role = obj.getString("role");
                user.createTime = obj.optLong("create_time", System.currentTimeMillis());
                user.enabled = obj.optBoolean("enabled", true);
            } catch (Exception e) {
                Log.e("UserInfo", "解析JSON失败", e);
            }
            return user;
        }

        public JSONObject toJson() {
            JSONObject obj = new JSONObject();
            try {
                obj.put("username", username);
                obj.put("display_name", displayName);
                obj.put("role", role);
                obj.put("create_time", createTime);
                obj.put("enabled", enabled);
            } catch (Exception e) {
                Log.e("UserInfo", "转换为JSON失败", e);
            }
            return obj;
        }
    }
}
