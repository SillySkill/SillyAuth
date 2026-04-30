package com.jcoding.aiactivity.adapter;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import com.jcoding.aiactivity.widget.BannerVideoView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.BannerItem;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;

/**
 * 活动轮播适配器
 * 支持图片和视频混合轮播
 */
public class BannerPagerAdapter extends RecyclerView.Adapter<BannerPagerAdapter.ViewHolder> {

    private Context context;
    private List<BannerItem> bannerList;
    private int currentPosition = 0;

    public BannerPagerAdapter(Context context, List<BannerItem> bannerList) {
        this.context = context;
        this.bannerList = bannerList;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_banner, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public long getItemId(int position) {
        // 返回唯一的ID，禁用ViewHolder复用
        return position;
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        BannerItem item = bannerList.get(position);

        android.util.Log.d("BannerPagerAdapter", "onBindViewHolder position=" + position + ", asset=" + item.getAssetPath());

        // 停止之前的视频播放
        if (holder.videoView != null) {
            holder.videoView.stopPlayback();
        }

        if (item.isImage()) {
            // 显示图片
            holder.imageView.setVisibility(View.VISIBLE);
            holder.videoView.setVisibility(View.GONE);

            // 检查是否是默认banner
            if (item.getAssetPath().startsWith("default_")) {
                // 显示默认渐变背景
                holder.imageView.setImageResource(R.drawable.bg_banner_default);
                holder.imageView.setScaleType(ImageView.ScaleType.CENTER_CROP);
                android.util.Log.d("BannerPagerAdapter", "Showing default banner: " + item.getAssetPath());
            } else {
                // 从assets加载图片
                loadImageFromAssets(holder.imageView, item.getAssetPath());
            }

        } else if (item.isVideo()) {
            // 显示视频
            holder.imageView.setVisibility(View.GONE);
            holder.videoView.setVisibility(View.VISIBLE);

            android.util.Log.d("BannerPagerAdapter", "VideoView visibility set to VISIBLE for position " + position);

            // 检查holder.videoView当前Tag是否与当前asset匹配
            Object currentTag = holder.videoView.getTag();
            String currentAsset = (currentTag != null) ? currentTag.toString() : null;

            // 如果Tag不匹配，说明这是不同的视频，需要重新加载
            if (!item.getAssetPath().equals(currentAsset)) {
                android.util.Log.d("BannerPagerAdapter", "Video mismatch: tag=" + currentAsset + ", expected=" + item.getAssetPath() + ", reloading");
                holder.videoView.setTag(item.getAssetPath());
                loadVideoFromAssets(holder.videoView, item.getAssetPath());
            } else {
                android.util.Log.d("BannerPagerAdapter", "Video already loaded for position " + position + ", starting");
                // 视频已加载，直接启动
                holder.videoView.start();
            }
        }
    }

    @Override
    public int getItemCount() {
        return bannerList != null ? bannerList.size() : 0;
    }

    /**
     * 从assets加载图片
     */
    private void loadImageFromAssets(ImageView imageView, String assetPath) {
        try {
            InputStream is = context.getAssets().open(assetPath);
            Bitmap bitmap = BitmapFactory.decodeStream(is);
            if (bitmap != null) {
                imageView.setImageBitmap(bitmap);
            }
            is.close();
        } catch (IOException e) {
            android.util.Log.e("BannerPagerAdapter", "Error loading image: " + assetPath, e);
        }
    }

    /**
     * 从assets加载视频
     * BannerVideoView内部已处理循环播放和错误监听，无需额外设置
     */
    private void loadVideoFromAssets(BannerVideoView videoView, String assetPath) {
        final String tempVideoPath = copyVideoToCache(assetPath);
        if (tempVideoPath == null) {
            android.util.Log.e("BannerPagerAdapter", "Failed to copy video to cache: " + assetPath);
            return;
        }

        android.util.Log.d("BannerPagerAdapter", "Loading video: " + assetPath + ", temp path: " + tempVideoPath);

        // 设置视频路径（BannerVideoView内部会在prepared后自动启动并循环播放）
        videoView.setVideoPath(tempVideoPath);
        android.util.Log.d("BannerPagerAdapter", "Video path set, BannerVideoView will auto-start when prepared");
    }

    /**
     * 复制视频到缓存目录
     */
    private String copyVideoToCache(String assetPath) {
        try {
            android.content.res.AssetFileDescriptor afd = context.getAssets().openFd(assetPath);
            if (afd != null) {
                java.io.FileInputStream fis = new java.io.FileInputStream(afd.getFileDescriptor());
                fis.skip(afd.getStartOffset());

                String tempVideoPath = context.getCacheDir().getPath() + "/temp_banner_" + System.currentTimeMillis() + ".mp4";

                // 复制到临时文件
                java.io.FileOutputStream fos = new java.io.FileOutputStream(tempVideoPath);
                byte[] buffer = new byte[8192];
                int len;
                while ((len = fis.read(buffer)) > -1) {
                    fos.write(buffer, 0, len);
                }
                fos.close();
                fis.close();
                afd.close();

                android.util.Log.d("BannerPagerAdapter", "Video copied to temp file: " + tempVideoPath);
                return tempVideoPath;
            }
        } catch (Exception e) {
            android.util.Log.e("BannerPagerAdapter", "Error copying video: " + assetPath, e);
        }
        return null;
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        public ImageView imageView;
        public BannerVideoView videoView;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.iv_banner_image);
            videoView = itemView.findViewById(R.id.vv_banner_video);
        }
    }
}
