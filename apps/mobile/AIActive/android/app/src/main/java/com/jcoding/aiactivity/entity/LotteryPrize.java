package com.jcoding.aiactivity.entity;

import java.io.Serializable;

/**
 * 抽奖奖品实体类
 */
public class LotteryPrize implements Serializable {

    private String name;
    private int totalCount;
    private int color;
    private String imageUri;

    public LotteryPrize(String name, int totalCount, int color) {
        this.name = name;
        this.totalCount = totalCount;
        this.color = color;
    }

    public LotteryPrize(String name, int totalCount, int color, String imageUri) {
        this.name = name;
        this.totalCount = totalCount;
        this.color = color;
        this.imageUri = imageUri;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(int totalCount) {
        this.totalCount = totalCount;
    }

    public int getColor() {
        return color;
    }

    public void setColor(int color) {
        this.color = color;
    }

    public String getImageUri() {
        return imageUri;
    }

    public void setImageUri(String imageUri) {
        this.imageUri = imageUri;
    }
}
