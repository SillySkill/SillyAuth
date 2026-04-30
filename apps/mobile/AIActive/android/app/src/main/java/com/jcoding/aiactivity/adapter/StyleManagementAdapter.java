package com.jcoding.aiactivity.adapter;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.StyleConfig;
import com.jcoding.aiactivity.manager.ConfigManager;

import java.util.List;

/**
 * 风格管理Adapter
 * 显示风格列表，支持启用/禁用/删除操作
 */
public class StyleManagementAdapter extends RecyclerView.Adapter<StyleManagementAdapter.ViewHolder> {

    private Context context;
    private List<StyleConfig> styleList;
    private OnItemClickListener listener;
    private ConfigManager configManager;

    public interface OnItemClickListener {
        void onEnableClick(StyleConfig style);
        void onDisableClick(StyleConfig style);
        void onDeleteClick(StyleConfig style);
    }

    public StyleManagementAdapter(Context context, List<StyleConfig> styleList, OnItemClickListener listener) {
        this.context = context;
        this.styleList = styleList;
        this.listener = listener;
        this.configManager = ConfigManager.getInstance(context);
        android.util.Log.d("StyleAdapter", "创建Adapter，风格数量: " + (styleList != null ? styleList.size() : 0));
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_style_management, parent, false);
        android.util.Log.d("StyleAdapter", "onCreateViewHolder");
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        StyleConfig style = styleList.get(position);

        android.util.Log.d("StyleAdapter", "onBindViewHolder[" + position + "]: " + style.getName());

        // 设置风格名称
        holder.tvStyleName.setText(style.getName());
        holder.tvStyleId.setText("ID: " + style.getStyleId());

        // 设置预览图
        String previewPath = "style/" + style.getPreviewImage();
        Bitmap bitmap = configManager.loadImageFromAssets(previewPath);
        if (bitmap != null) {
            holder.ivPreview.setImageBitmap(bitmap);
        } else {
            // 如果图片加载失败，显示灰色背景
            holder.ivPreview.setBackgroundColor(Color.parseColor("#CCCCCC"));
        }

        // 获取当前启用状态
        boolean isEnabled = configManager.isStyleEnabled(style.getStyleId());

        // 更新状态显示
        updateStatusDisplay(holder, isEnabled);

        // 启用按钮点击
        holder.btnEnable.setOnClickListener(v -> {
            if (listener != null) {
                listener.onEnableClick(style);
            }
            // 立即更新UI显示
            updateStatusDisplay(holder, true);
        });

        // 禁用按钮点击
        holder.btnDisable.setOnClickListener(v -> {
            if (listener != null) {
                listener.onDisableClick(style);
            }
            // 立即更新UI显示
            updateStatusDisplay(holder, false);
        });

        // 删除按钮点击
        holder.btnDelete.setOnClickListener(v -> {
            if (listener != null) {
                listener.onDeleteClick(style);
            }
            // 立即更新UI显示为禁用
            updateStatusDisplay(holder, false);
        });

        android.util.Log.d("StyleAdapter", "绑定完成[" + position + "]: " + style.getName() + ", 启用=" + isEnabled);
    }

    /**
     * 更新状态显示
     */
    private void updateStatusDisplay(ViewHolder holder, boolean isEnabled) {
        if (isEnabled) {
            holder.tvStatus.setText("已启用");
            holder.tvStatus.setTextColor(Color.parseColor("#4CAF50"));
        } else {
            holder.tvStatus.setText("已禁用");
            holder.tvStatus.setTextColor(Color.parseColor("#F44336"));
        }
    }

    @Override
    public int getItemCount() {
        int count = styleList != null ? styleList.size() : 0;
        android.util.Log.d("StyleAdapter", "getItemCount: " + count);
        return count;
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        ImageView ivPreview;
        TextView tvStyleName;
        TextView tvStyleId;
        TextView tvStatus;
        Button btnEnable;
        Button btnDisable;
        Button btnDelete;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            ivPreview = itemView.findViewById(R.id.iv_preview);
            tvStyleName = itemView.findViewById(R.id.tv_style_name);
            tvStyleId = itemView.findViewById(R.id.tv_style_id);
            tvStatus = itemView.findViewById(R.id.tv_status);
            btnEnable = itemView.findViewById(R.id.btn_enable);
            btnDisable = itemView.findViewById(R.id.btn_disable);
            btnDelete = itemView.findViewById(R.id.btn_delete);
        }
    }
}
