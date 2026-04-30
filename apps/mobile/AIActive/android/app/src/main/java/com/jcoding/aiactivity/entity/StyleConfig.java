package com.jcoding.aiactivity.entity;

/**
 * AI风格配置实体
 */
public class StyleConfig {

    private String styleId;          // 风格ID
    private String name;             // 风格名称
    private String prompt;           // AI提示词
    private String previewImage;     // 预览图路径
    private String backImage;        // 背景图路径（KV图，传递给大模型API作为图1）
    private String maskImage;        // 遮罩图片路径（等待生成阶段显示）
    private String[] referenceImages; // 参考图片URL数组
    private int status;              // 状态：1=启用，0=禁用

    public StyleConfig() {
    }

    public StyleConfig(String styleId, String name, String prompt, String previewImage, int status) {
        this.styleId = styleId;
        this.name = name;
        this.prompt = prompt;
        this.previewImage = previewImage;
        this.status = status;
    }

    // Getters and Setters
    public String getStyleId() {
        return styleId;
    }

    public void setStyleId(String styleId) {
        this.styleId = styleId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }

    public String getPreviewImage() {
        return previewImage;
    }

    public void setPreviewImage(String previewImage) {
        this.previewImage = previewImage;
    }

    public String getBackImage() {
        return backImage;
    }

    public void setBackImage(String backImage) {
        this.backImage = backImage;
    }

    public String[] getReferenceImages() {
        return referenceImages;
    }

    public void setReferenceImages(String[] referenceImages) {
        this.referenceImages = referenceImages;
    }

    public String getMaskImage() {
        return maskImage;
    }

    public void setMaskImage(String maskImage) {
        this.maskImage = maskImage;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public boolean isEnabled() {
        return status == 1;
    }
}
