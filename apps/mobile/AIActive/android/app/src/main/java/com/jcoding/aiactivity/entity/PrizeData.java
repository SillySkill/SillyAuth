package com.jcoding.aiactivity.entity;

import java.io.Serializable;

/**
 * 礼花抽奖奖品数据实体类
 * 从prizeDate.xls解析而来
 */
public class PrizeData implements Serializable {

    private String name;           // 奖品名称
    private String merchant;       // 商家信息
    private String description;    // 奖品描述
    private int totalCount;        // 总数量
    private int remainingCount;    // 剩余数量

    public PrizeData() {
    }

    public PrizeData(String name, String merchant) {
        this.name = name;
        this.merchant = merchant;
        this.totalCount = 1;
        this.remainingCount = 1;
    }

    public PrizeData(String name, String merchant, String description, int totalCount) {
        this.name = name;
        this.merchant = merchant;
        this.description = description;
        this.totalCount = totalCount;
        this.remainingCount = totalCount;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getMerchant() {
        return merchant;
    }

    public void setMerchant(String merchant) {
        this.merchant = merchant;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public int getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(int totalCount) {
        this.totalCount = totalCount;
    }

    public int getRemainingCount() {
        return remainingCount;
    }

    public void setRemainingCount(int remainingCount) {
        this.remainingCount = remainingCount;
    }

    /**
     * 减少剩余数量
     */
    public void decreaseRemaining() {
        if (remainingCount > 0) {
            remainingCount--;
        }
    }

    /**
     * 是否还有剩余
     */
    public boolean hasRemaining() {
        return remainingCount > 0;
    }

    @Override
    public String toString() {
        return "PrizeData{" +
                "name='" + name + '\'' +
                ", merchant='" + merchant + '\'' +
                ", description='" + description + '\'' +
                ", totalCount=" + totalCount +
                ", remainingCount=" + remainingCount +
                '}';
    }
}
