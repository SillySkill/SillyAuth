package com.jcoding.aiactivity.entity;

import java.io.Serializable;
import java.util.Date;

/**
 * 抽奖中奖者实体类
 */
public class LotteryWinner implements Serializable {

    private String name;
    private String prizeName;
    private Date winTime;

    public LotteryWinner(String name, String prizeName, Date winTime) {
        this.name = name;
        this.prizeName = prizeName;
        this.winTime = winTime;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPrizeName() {
        return prizeName;
    }

    public void setPrizeName(String prizeName) {
        this.prizeName = prizeName;
    }

    public Date getTime() {
        return winTime;
    }

    public void setWinTime(Date winTime) {
        this.winTime = winTime;
    }
}
