package com.jcoding.aiactivity.adapter;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.ProgressBar;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.StyleConfig;
import com.jcoding.aiactivity.manager.ConfigManager;

import java.io.InputStream;
import java.util.List;

/**
 * 风格轮播适配器
 * 使用ViewPager2实现全屏图片轮播
 */
public class StyleCarouselAdapter extends RecyclerView.Adapter<StyleCarouselAdapter.ViewHolder> {

    private Context context;
    private List<StyleConfig> styleList;
    private OnItemClickListener listener;
    private ConfigManager configManager;

    public interface OnItemClickListener {
        void onItemClick(StyleConfig style, int position);
    }

    public StyleCarouselAdapter(Context context, List<StyleConfig> styleList, OnItemClickListener listener) {
        this.context = context;
        this.styleList = styleList;
        this.listener = listener;
        this.configManager = ConfigManager.getInstance(context);
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_style_carousel, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        StyleConfig style = styleList.get(position);

        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onItemClick(style, position);
            }
        });

        // 加载风格预览图
        loadImage(holder.imageView, style.getPreviewImage());
    }

    @Override
    public int getItemCount() {
        return styleList != null ? styleList.size() : 0;
    }

    private void loadImage(ImageView imageView, String imagePath) {
        try {
            // 添加style/前缀
            String fullPath = "style/" + imagePath;
            android.util.Log.d("StyleCarouselAdapter", "Loading image: " + fullPath);
            Bitmap bitmap = configManager.loadImageFromAssets(fullPath);
            if (bitmap != null) {
                imageView.setImageBitmap(bitmap);
                android.util.Log.d("StyleCarouselAdapter", "Successfully loaded: " + fullPath);
            } else {
                // 使用默认背景色
                imageView.setBackgroundColor(android.graphics.Color.GRAY);
                android.util.Log.w("StyleCarouselAdapter", "Failed to load image (returned null): " + fullPath);
            }
        } catch (Exception e) {
            android.util.Log.e("StyleCarouselAdapter", "Error loading image: " + imagePath, e);
            e.printStackTrace();
            imageView.setBackgroundColor(android.graphics.Color.GRAY);
        }
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        ImageView imageView;
        ProgressBar progressBar;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.iv_style_image);
            progressBar = itemView.findViewById(R.id.progress_bar);
        }
    }
}
