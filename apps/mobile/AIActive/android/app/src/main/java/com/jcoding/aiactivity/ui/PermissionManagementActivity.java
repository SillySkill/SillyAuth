package com.jcoding.aiactivity.ui;

import android.app.AlertDialog;
import android.content.Context;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.security.PermissionManager;

import java.util.ArrayList;
import java.util.List;

/**
 * 权限管理Activity
 *
 * 功能：
 * 1. 用户列表展示
 * 2. 创建用户
 * 3. 删除用户
 * 4. 修改用户角色
 * 5. 启用/禁用用户
 */
public class PermissionManagementActivity extends AppCompatActivity {

    private static final String TAG = "PermissionManagement";

    // UI组件
    private RecyclerView recyclerView;
    private UserAdapter adapter;
    private Button btnAddUser;
    private ImageButton btnBack;
    private TextView tvTitle;

    // 数据
    private List<PermissionManager.UserInfo> users;

    // 管理器
    private PermissionManager permissionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_permission_management);

        permissionManager = PermissionManager.getInstance(this);

        initViews();
        loadUsers();
    }

    private void initViews() {
        // 标题栏
        btnBack = findViewById(R.id.btn_back);
        tvTitle = findViewById(R.id.tv_title);
        tvTitle.setText("权限管理");

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

        // 添加用户按钮
        btnAddUser = findViewById(R.id.btn_add_user);
        btnAddUser.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showAddUserDialog();
            }
        });
    }

    private void loadUsers() {
        users = permissionManager.getAllUsers();
        adapter = new UserAdapter(users);
        recyclerView.setAdapter(adapter);
    }

    /**
     * 显示添加用户对话框
     */
    private void showAddUserDialog() {
        View dialogView = LayoutInflater.from(this).inflate(
            R.layout.dialog_add_user, null);

        EditText etUsername = dialogView.findViewById(R.id.et_username);
        EditText etDisplayName = dialogView.findViewById(R.id.et_display_name);
        RadioGroup rgRole = dialogView.findViewById(R.id.rg_role);

        new AlertDialog.Builder(this)
            .setTitle("添加用户")
            .setView(dialogView)
            .setPositiveButton("添加", (dialog, which) -> {
                String username = etUsername.getText().toString().trim();
                String displayName = etDisplayName.getText().toString().trim();

                int selectedId = rgRole.getCheckedRadioButtonId();
                String role = PermissionManager.ROLE_ADMIN;  // 默认

                if (selectedId == R.id.rb_operator) {
                    role = PermissionManager.ROLE_OPERATOR;
                } else if (selectedId == R.id.rb_observer) {
                    role = PermissionManager.ROLE_OBSERVER;
                }

                if (username.isEmpty()) {
                    Toast.makeText(this, "请输入用户名", Toast.LENGTH_SHORT).show();
                    return;
                }

                if (displayName.isEmpty()) {
                    Toast.makeText(this, "请输入显示名称", Toast.LENGTH_SHORT).show();
                    return;
                }

                // 创建用户
                boolean success = permissionManager.createUser(username, displayName, role);

                if (success) {
                    Toast.makeText(this, "用户已创建", Toast.LENGTH_SHORT).show();
                    loadUsers();  // 刷新列表
                } else {
                    Toast.makeText(this, "创建失败，用户可能已存在", Toast.LENGTH_SHORT).show();
                }
            })
            .setNegativeButton("取消", null)
            .show();
    }

    /**
     * 显示编辑用户对话框
     */
    private void showEditUserDialog(PermissionManager.UserInfo user) {
        // 不能编辑admin用户
        if ("admin".equals(user.username)) {
            Toast.makeText(this, "不能编辑admin用户", Toast.LENGTH_SHORT).show();
            return;
        }

        View dialogView = LayoutInflater.from(this).inflate(
            R.layout.dialog_edit_user, null);

        EditText etDisplayName = dialogView.findViewById(R.id.et_display_name);
        RadioGroup rgRole = dialogView.findViewById(R.id.rg_role);
        Switch swEnabled = dialogView.findViewById(R.id.sw_enabled);

        etDisplayName.setText(user.displayName);
        swEnabled.setChecked(user.enabled);

        // 设置角色
        if (PermissionManager.ROLE_ADMIN.equals(user.role)) {
            rgRole.check(R.id.rb_admin);
        } else if (PermissionManager.ROLE_OPERATOR.equals(user.role)) {
            rgRole.check(R.id.rb_operator);
        } else if (PermissionManager.ROLE_OBSERVER.equals(user.role)) {
            rgRole.check(R.id.rb_observer);
        }

        new AlertDialog.Builder(this)
            .setTitle("编辑用户: " + user.username)
            .setView(dialogView)
            .setPositiveButton("保存", (dialog, which) -> {
                String displayName = etDisplayName.getText().toString().trim();
                boolean enabled = swEnabled.isChecked();

                int selectedId = rgRole.getCheckedRadioButtonId();
                String role = PermissionManager.ROLE_ADMIN;

                if (selectedId == R.id.rb_operator) {
                    role = PermissionManager.ROLE_OPERATOR;
                } else if (selectedId == R.id.rb_observer) {
                    role = PermissionManager.ROLE_OBSERVER;
                }

                // 更新显示名称
                user.displayName = displayName;

                // 更新角色
                permissionManager.setUserRole(user.username, role);

                // 更新启用状态
                permissionManager.setUserEnabled(user.username, enabled);

                Toast.makeText(this, "用户已更新", Toast.LENGTH_SHORT).show();
                loadUsers();  // 刷新列表
            })
            .setNegativeButton("取消", null)
            .show();
    }

    /**
     * 显示用户权限对话框
     */
    private void showUserPermissionsDialog(PermissionManager.UserInfo user) {
        View dialogView = LayoutInflater.from(this).inflate(
            R.layout.dialog_user_permissions, null);

        TextView tvUsername = dialogView.findViewById(R.id.tv_username);
        TextView tvRole = dialogView.findViewById(R.id.tv_role);
        TextView tvPermissions = dialogView.findViewById(R.id.tv_permissions);

        tvUsername.setText("用户: " + user.username);
        tvRole.setText("角色: " + getRoleName(user.role));

        // 获取权限列表
        List<String> permissions = permissionManager.getRolePermissions(user.role);
        StringBuilder permText = new StringBuilder();
        for (String perm : permissions) {
            permText.append("• ").append(getPermissionName(perm)).append("\n");
        }
        tvPermissions.setText(permText.toString());

        new AlertDialog.Builder(this)
            .setTitle("用户权限")
            .setView(dialogView)
            .setPositiveButton("关闭", null)
            .show();
    }

    /**
     * 删除用户
     */
    private void deleteUser(String username) {
        // 不能删除admin用户
        if ("admin".equals(username)) {
            Toast.makeText(this, "不能删除admin用户", Toast.LENGTH_SHORT).show();
            return;
        }

        new AlertDialog.Builder(this)
            .setTitle("确认删除")
            .setMessage("确定要删除用户 " + username + " 吗？")
            .setPositiveButton("删除", (dialog, which) -> {
                boolean success = permissionManager.deleteUser(username);

                if (success) {
                    Toast.makeText(this, "用户已删除", Toast.LENGTH_SHORT).show();
                    loadUsers();  // 刷新列表
                } else {
                    Toast.makeText(this, "删除失败", Toast.LENGTH_SHORT).show();
                }
            })
            .setNegativeButton("取消", null)
            .show();
    }

    private String getRoleName(String role) {
        switch (role) {
            case PermissionManager.ROLE_ADMIN:
                return "管理员";
            case PermissionManager.ROLE_OPERATOR:
                return "操作员";
            case PermissionManager.ROLE_OBSERVER:
                return "观察员";
            default:
                return role;
        }
    }

    private String getPermissionName(String permission) {
        switch (permission) {
            case PermissionManager.PERM_PLAY_CONTROL:
                return "播放控制";
            case PermissionManager.PERM_MEDIA_MANAGE:
                return "媒体管理";
            case PermissionManager.PERM_SETTINGS:
                return "系统设置";
            case PermissionManager.PERM_USER_MANAGE:
                return "用户管理";
            case PermissionManager.PERM_LOG_VIEW:
                return "日志查看";
            case PermissionManager.PERM_SERVER_CONTROL:
                return "服务器控制";
            default:
                return permission;
        }
    }

    // ==================== Adapter ====================

    private class UserAdapter extends RecyclerView.Adapter<UserAdapter.UserViewHolder> {

        private List<PermissionManager.UserInfo> userList;

        public UserAdapter(List<PermissionManager.UserInfo> userList) {
            this.userList = userList;
        }

        @NonNull
        @Override
        public UserViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View view = LayoutInflater.from(parent.getContext()).inflate(
                R.layout.item_user, parent, false);
            return new UserViewHolder(view);
        }

        @Override
        public void onBindViewHolder(@NonNull UserViewHolder holder, int position) {
            holder.bind(userList.get(position));
        }

        @Override
        public int getItemCount() {
            return userList.size();
        }

        class UserViewHolder extends RecyclerView.ViewHolder {
            private ImageView ivAvatar;
            private TextView tvUsername;
            private TextView tvDisplayName;
            private TextView tvRole;
            private Switch swEnabled;
            private ImageButton btnEdit;
            private ImageButton btnPermissions;
            private ImageButton btnDelete;

            public UserViewHolder(@NonNull View itemView) {
                super(itemView);
                ivAvatar = itemView.findViewById(R.id.iv_avatar);
                tvUsername = itemView.findViewById(R.id.tv_username);
                tvDisplayName = itemView.findViewById(R.id.tv_display_name);
                tvRole = itemView.findViewById(R.id.tv_role);
                swEnabled = itemView.findViewById(R.id.sw_enabled);
                btnEdit = itemView.findViewById(R.id.btn_edit);
                btnPermissions = itemView.findViewById(R.id.btn_permissions);
                btnDelete = itemView.findViewById(R.id.btn_delete);
            }

            public void bind(PermissionManager.UserInfo user) {
                tvUsername.setText(user.username);
                tvDisplayName.setText(user.displayName);
                tvRole.setText(getRoleName(user.role));
                swEnabled.setChecked(user.enabled);

                // 根据用户名首字母设置头像
                String firstLetter = user.username.substring(0, 1).toUpperCase();
                ivAvatar.setImageResource(R.drawable.ic_avatar);

                // 编辑按钮
                btnEdit.setOnClickListener(v -> {
                    showEditUserDialog(user);
                });

                // 权限按钮
                btnPermissions.setOnClickListener(v -> {
                    showUserPermissionsDialog(user);
                });

                // 启用/禁用切换
                swEnabled.setOnCheckedChangeListener(null);
                swEnabled.setOnCheckedChangeListener((buttonView, isChecked) -> {
                    permissionManager.setUserEnabled(user.username, isChecked);
                    loadUsers();  // 刷新列表
                });

                // 删除按钮
                btnDelete.setOnClickListener(v -> {
                    deleteUser(user.username);
                });

                // admin用户不允许删除和编辑
                if ("admin".equals(user.username)) {
                    btnDelete.setVisibility(View.GONE);
                    btnEdit.setVisibility(View.GONE);
                } else {
                    btnDelete.setVisibility(View.VISIBLE);
                    btnEdit.setVisibility(View.VISIBLE);
                }
            }
        }
    }
}
