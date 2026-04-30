package com.jcoding.aiactivity.ui;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.InnerShowModule;
import com.jcoding.aiactivity.manager.BackgroundMediaManager;
import com.jcoding.aiactivity.manager.MediaResourceManager;
import com.jcoding.aiactivity.network.InnerShowNetworkClient;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * 媒体资源管理Activity
 *
 * 功能：
 * 1. 按模块和类型分类显示媒体
 * 2. 上传新媒体文件
 * 3. 启用/禁用媒体
 * 4. 预览媒体
 * 5. 删除媒体
 */
public class MediaManagementActivity extends AppCompatActivity {

    private static final String TAG = "MediaManagement";
    private static final int REQUEST_CODE_PICK_FILE = 1001;

    // UI组件
    private RecyclerView recyclerView;
    private MediaAdapter adapter;
    private Button btnUpload;
    private TextView tvTitle;
    private ImageButton btnBack;

    // 数据
    private List<MediaItemGroup> mediaGroups;
    private InnerShowModule currentModuleFilter = null;  // null = 显示所有模块
    private String currentTypeFilter = null;            // null = 显示所有类型

    // 管理器
    private MediaResourceManager mediaManager;
    private BackgroundMediaManager backgroundMediaManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_media_management);

        mediaManager = MediaResourceManager.getInstance(this);
        backgroundMediaManager = BackgroundMediaManager.getInstance(this);

        initViews();
        loadMediaData();
    }

    private void initViews() {
        // 标题栏
        btnBack = findViewById(R.id.btn_back);
        tvTitle = findViewById(R.id.tv_title);
        tvTitle.setText("媒体资源管理");

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

        // 上传按钮
        btnUpload = findViewById(R.id.btn_upload);
        btnUpload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showUploadDialog();
            }
        });
    }

    private void loadMediaData() {
        mediaGroups = new ArrayList<>();

        // 按模块和类型分组
        for (InnerShowModule module : InnerShowModule.values()) {
            // 背景图片
            List<MediaResourceManager.MediaItem> backgrounds =
                mediaManager.getModuleMedia(module, "background");
            if (!backgrounds.isEmpty()) {
                MediaItemGroup group = new MediaItemGroup();
                group.module = module;
                group.type = "background";
                group.typeName = "背景图片";
                group.items = backgrounds;
                mediaGroups.add(group);
            }

            // 背景音乐
            List<MediaResourceManager.MediaItem> music =
                mediaManager.getModuleMedia(module, "music");
            if (!music.isEmpty()) {
                MediaItemGroup group = new MediaItemGroup();
                group.module = module;
                group.type = "music";
                group.typeName = "背景音乐";
                group.items = music;
                mediaGroups.add(group);
            }

            // 贴纸
            List<MediaResourceManager.MediaItem> stickers =
                mediaManager.getModuleMedia(module, "sticker");
            if (!stickers.isEmpty()) {
                MediaItemGroup group = new MediaItemGroup();
                group.module = module;
                group.type = "sticker";
                group.typeName = "贴纸素材";
                group.items = stickers;
                mediaGroups.add(group);
            }
        }

        // 设置适配器
        adapter = new MediaAdapter(mediaGroups);
        recyclerView.setAdapter(adapter);
    }

    /**
     * 显示上传对话框
     */
    private void showUploadDialog() {
        View dialogView = LayoutInflater.from(this).inflate(
            R.layout.dialog_media_upload, null);

        EditText etName = dialogView.findViewById(R.id.et_name);
        LinearLayout llModule = dialogView.findViewById(R.id.ll_module);
        EditText etModule = dialogView.findViewById(R.id.et_module);
        LinearLayout llType = dialogView.findViewById(R.id.ll_type);
        EditText etType = dialogView.findViewById(R.id.et_type);
        Button btnSelectFile = dialogView.findViewById(R.id.btn_select_file);
        TextView tvFilePath = dialogView.findViewById(R.id.tv_file_path);
        ProgressBar progressBar = dialogView.findViewById(R.id.progress_bar);

        final String[] selectedFilePath = {null};

        // 选择文件
        btnSelectFile.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.setType("*/*");
                startActivityForResult(intent, REQUEST_CODE_PICK_FILE);
            }
        });

        AlertDialog dialog = new AlertDialog.Builder(this)
            .setTitle("上传媒体文件")
            .setView(dialogView)
            .setPositiveButton("上传", null)
            .setNegativeButton("取消", null)
            .create();

        dialog.setOnShowListener(dialogInterface -> {
            Button positiveBtn = dialog.getButton(AlertDialog.BUTTON_POSITIVE);
            positiveBtn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    String name = etName.getText().toString().trim();
                    String moduleStr = etModule.getText().toString().trim();
                    String type = etType.getText().toString().trim();

                    if (name.isEmpty()) {
                        Toast.makeText(MediaManagementActivity.this, "请输入媒体名称",
                            Toast.LENGTH_SHORT).show();
                        return;
                    }

                    if (moduleStr.isEmpty()) {
                        Toast.makeText(MediaManagementActivity.this, "请输入适用模块",
                            Toast.LENGTH_SHORT).show();
                        return;
                    }

                    if (type.isEmpty()) {
                        Toast.makeText(MediaManagementActivity.this, "请输入媒体类型",
                            Toast.LENGTH_SHORT).show();
                        return;
                    }

                    if (selectedFilePath[0] == null) {
                        Toast.makeText(MediaManagementActivity.this, "请选择文件",
                            Toast.LENGTH_SHORT).show();
                        return;
                    }

                    // 解析模块
                    InnerShowModule module = InnerShowModule.fromId(moduleStr);

                    // 执行上传
                    uploadMedia(name, module, type, selectedFilePath[0], progressBar, dialog);
                }
            });
        });

        dialog.show();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_CODE_PICK_FILE && resultCode == RESULT_OK) {
            if (data != null && data.getData() != null) {
                Uri uri = data.getData();
                String path = getPathFromUri(this, uri);

                // TODO: 在上传对话框中显示文件路径
                Toast.makeText(this, "已选择文件: " + path, Toast.LENGTH_SHORT).show();
            }
        }
    }

    /**
     * 从Uri获取文件路径
     */
    private String getPathFromUri(Context context, Uri uri) {
        // 简化实现，实际项目中需要更完善的处理
        return uri.getPath();
    }

    /**
     * 上传媒体文件（带进度跟踪）
     */
    private void uploadMedia(String name, InnerShowModule module, String type,
                            String filePath, ProgressBar progressBar, AlertDialog dialog) {
        // 使用FileTransferManager进行文件传输
        com.jcoding.aiactivity.network.FileTransferManager transferManager =
            com.jcoding.aiactivity.network.FileTransferManager.getInstance(this);

        // 显示进度对话框
        ProgressDialog progressDialog = new ProgressDialog(this);
        progressDialog.setMessage("正在上传... 0%");
        progressDialog.setCancelable(false);
        progressDialog.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
        progressDialog.setMax(100);
        progressDialog.show();

        // 开始传输
        String transferId = transferManager.uploadFile(filePath,
            new com.jcoding.aiactivity.network.FileTransferManager.TransferListener() {
                @Override
                public void onProgress(String id, int progress, long bytesTransferred, long totalBytes) {
                    runOnUiThread(() -> {
                        progressDialog.setProgress(progress);
                        progressDialog.setMessage("正在上传... " + progress + "%");
                        if (progressBar != null) {
                            progressBar.setProgress(progress);
                        }
                    });
                }

                @Override
                public void onCompleted(String id, java.io.File file) {
                    runOnUiThread(() -> {
                        progressDialog.dismiss();
                        dialog.dismiss();

                        // 上传完成后，将文件信息保存到媒体管理器
                        boolean success = mediaManager.uploadMedia(filePath, name, type,
                            new InnerShowModule[]{module});

                        if (success) {
                            Toast.makeText(MediaManagementActivity.this,
                                "上传成功", Toast.LENGTH_SHORT).show();
                            loadMediaData();  // 重新加载数据
                        } else {
                            Toast.makeText(MediaManagementActivity.this,
                                "保存媒体信息失败", Toast.LENGTH_SHORT).show();
                        }
                    });
                }

                @Override
                public void onError(String id, String error) {
                    runOnUiThread(() -> {
                        progressDialog.dismiss();
                        Toast.makeText(MediaManagementActivity.this,
                            "上传失败: " + error, Toast.LENGTH_LONG).show();
                    });
                }
            });

        if (transferId == null) {
            progressDialog.dismiss();
            Toast.makeText(this, "无法启动传输", Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * 切换媒体启用状态
     */
    private void toggleMediaEnabled(String mediaId, boolean enabled) {
        if (enabled) {
            mediaManager.enableMedia(mediaId);
            Toast.makeText(this, "已启用", Toast.LENGTH_SHORT).show();
        } else {
            mediaManager.disableMedia(mediaId);
            Toast.makeText(this, "已禁用", Toast.LENGTH_SHORT).show();
        }
        loadMediaData();
    }

    /**
     * 删除媒体
     */
    private void deleteMedia(String mediaId) {
        new AlertDialog.Builder(this)
            .setTitle("确认删除")
            .setMessage("确定要删除这个媒体吗？")
            .setPositiveButton("删除", (dialog, which) -> {
                boolean success = mediaManager.removeMediaItem(mediaId);
                if (success) {
                    Toast.makeText(this, "删除成功", Toast.LENGTH_SHORT).show();
                    loadMediaData();
                } else {
                    Toast.makeText(this, "删除失败", Toast.LENGTH_SHORT).show();
                }
            })
            .setNegativeButton("取消", null)
            .show();
    }

    /**
     * 预览媒体
     */
    private void previewMedia(MediaResourceManager.MediaItem item) {
        View previewView = LayoutInflater.from(this).inflate(
            R.layout.dialog_media_preview, null);

        ImageView imageView = previewView.findViewById(R.id.image_preview);
        TextView tvInfo = previewView.findViewById(R.id.tv_info);

        // 加载预览图
        if (item.type.equals("background") || item.type.equals("sticker")) {
            Bitmap bitmap = mediaManager.loadMediaImage(item.id);
            if (bitmap != null) {
                imageView.setImageBitmap(bitmap);
            }
        }

        // 显示信息
        String info = "名称: " + item.name + "\n" +
                     "类型: " + item.type + "\n" +
                     "路径: " + item.path + "\n" +
                     "状态: " + (item.enabled ? "已启用" : "已禁用");
        tvInfo.setText(info);

        new AlertDialog.Builder(this)
            .setTitle("媒体预览")
            .setView(previewView)
            .setPositiveButton("关闭", null)
            .show();
    }

    /**
     * 设置媒体为模块背景
     */
    private void setAsBackground(MediaResourceManager.MediaItem item) {
        InnerShowModule module = item.getModule();
        if (module == null) {
            Toast.makeText(this, "该媒体没有关联模块", Toast.LENGTH_SHORT).show();
            return;
        }

        backgroundMediaManager.setBackgroundImage(module, item.path);

        String msg = "已设置为" + module.getName() + "的背景";
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }

    // ==================== Adapter ====================

    private class MediaAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

        private List<MediaItemGroup> groups;

        private static final int TYPE_GROUP = 0;
        private static final int TYPE_ITEM = 1;

        public MediaAdapter(List<MediaItemGroup> groups) {
            this.groups = groups;
        }

        @Override
        public int getItemViewType(int position) {
            // 计算当前位置是组标题还是项目
            int currentPos = 0;
            for (MediaItemGroup group : groups) {
                if (currentPos == position) {
                    return TYPE_GROUP;
                }
                currentPos++;

                for (int i = 0; i < group.items.size(); i++) {
                    if (currentPos == position) {
                        return TYPE_ITEM;
                    }
                    currentPos++;
                }
            }
            return TYPE_ITEM;
        }

        @NonNull
        @Override
        public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            if (viewType == TYPE_GROUP) {
                View view = LayoutInflater.from(parent.getContext()).inflate(
                    R.layout.item_media_group, parent, false);
                return new GroupViewHolder(view);
            } else {
                View view = LayoutInflater.from(parent.getContext()).inflate(
                    R.layout.item_media_item, parent, false);
                return new ItemViewHolder(view);
            }
        }

        @Override
        public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
            int viewType = getItemViewType(position);

            if (viewType == TYPE_GROUP) {
                GroupViewHolder groupHolder = (GroupViewHolder) holder;
                MediaItemGroup group = getGroupAtPosition(position);
                if (group != null) {
                    groupHolder.bind(group);
                }
            } else {
                ItemViewHolder itemHolder = (ItemViewHolder) holder;
                MediaResourceManager.MediaItem item = getItemAtPosition(position);
                if (item != null) {
                    itemHolder.bind(item);
                }
            }
        }

        @Override
        public int getItemCount() {
            int count = 0;
            for (MediaItemGroup group : groups) {
                count++;  // 组标题
                count += group.items.size();  // 项目
            }
            return count;
        }

        private MediaItemGroup getGroupAtPosition(int position) {
            int currentPos = 0;
            for (MediaItemGroup group : groups) {
                if (currentPos == position) {
                    return group;
                }
                currentPos++;
                currentPos += group.items.size();
            }
            return null;
        }

        private MediaResourceManager.MediaItem getItemAtPosition(int position) {
            int currentPos = 0;
            for (MediaItemGroup group : groups) {
                currentPos++;  // 跳过组标题
                for (MediaResourceManager.MediaItem item : group.items) {
                    if (currentPos == position) {
                        return item;
                    }
                    currentPos++;
                }
            }
            return null;
        }
    }

    private class GroupViewHolder extends RecyclerView.ViewHolder {
        private TextView tvModuleName;
        private TextView tvTypeName;

        public GroupViewHolder(@NonNull View itemView) {
            super(itemView);
            tvModuleName = itemView.findViewById(R.id.tv_module_name);
            tvTypeName = itemView.findViewById(R.id.tv_type_name);
        }

        public void bind(MediaItemGroup group) {
            tvModuleName.setText(group.module.getName());
            tvTypeName.setText(group.typeName);
        }
    }

    private class ItemViewHolder extends RecyclerView.ViewHolder {
        private ImageView imageView;
        private TextView tvName;
        private Switch swEnabled;
        private ImageButton btnPreview;
        private ImageButton btnSetBackground;
        private ImageButton btnDelete;

        public ItemViewHolder(@NonNull View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.image_view);
            tvName = itemView.findViewById(R.id.tv_name);
            swEnabled = itemView.findViewById(R.id.sw_enabled);
            btnPreview = itemView.findViewById(R.id.btn_preview);
            btnSetBackground = itemView.findViewById(R.id.btn_set_background);
            btnDelete = itemView.findViewById(R.id.btn_delete);
        }

        public void bind(MediaResourceManager.MediaItem item) {
            tvName.setText(item.name);
            swEnabled.setChecked(item.enabled);

            // 加载缩略图
            if (item.type.equals("background") || item.type.equals("sticker")) {
                Bitmap bitmap = mediaManager.loadMediaImage(item.id);
                if (bitmap != null) {
                    imageView.setImageBitmap(bitmap);
                } else {
                    imageView.setImageResource(R.drawable.ic_placeholder);
                }
            } else {
                imageView.setImageResource(R.drawable.ic_music);
            }

            // 启用/禁用切换
            swEnabled.setOnCheckedChangeListener(null);
            swEnabled.setOnCheckedChangeListener((buttonView, isChecked) -> {
                toggleMediaEnabled(item.id, isChecked);
            });

            // 预览按钮
            btnPreview.setOnClickListener(v -> {
                previewMedia(item);
            });

            // 设为背景按钮（仅背景类型）
            if (item.type.equals("background")) {
                btnSetBackground.setVisibility(View.VISIBLE);
                btnSetBackground.setOnClickListener(v -> {
                    setAsBackground(item);
                });
            } else {
                btnSetBackground.setVisibility(View.GONE);
            }

            // 删除按钮
            btnDelete.setOnClickListener(v -> {
                deleteMedia(item.id);
            });
        }
    }

    // ==================== 数据类 ====================

    private static class MediaItemGroup {
        InnerShowModule module;
        String type;
        String typeName;
        List<MediaResourceManager.MediaItem> items;
    }
}
