package com.jcoding.aiactivity.entity;

/**
 * 节目表项
 *
 * Excel导入的每一行数据，包含：
 * - 序号
 * - 时间
 * - 内容
 * - 备注
 * - 匹配的动作
 */
public class ProgramItem {

    private int sequence;              // 序号
    private String time;               // 时间（如："10:00"）
    private String content;             // 节目内容
    private String remark;              // 备注
    private DigitalHumanAction action;  // 匹配的数字人动作
    private int duration;               // 时长（秒），用于进度显示

    public ProgramItem() {
    }

    public ProgramItem(int sequence, String time, String content, String remark) {
        this.sequence = sequence;
        this.time = time;
        this.content = content;
        this.remark = remark;
        this.duration = 30; // 默认30秒
    }

    // Getters and Setters
    public int getSequence() {
        return sequence;
    }

    public void setSequence(int sequence) {
        this.sequence = sequence;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getRemark() {
        return remark;
    }

    public void setRemark(String remark) {
        this.remark = remark;
    }

    public DigitalHumanAction getAction() {
        return action;
    }

    public void setAction(DigitalHumanAction action) {
        this.action = action;
    }

    public int getDuration() {
        return duration;
    }

    public void setDuration(int duration) {
        this.duration = duration;
    }

    /**
     * 获取显示文本（包含序号和内容）
     */
    public String getDisplayText() {
        return sequence + ". " + content;
    }

    /**
     * 获取完整信息（用于日志）
     */
    @Override
    public String toString() {
        return "ProgramItem{" +
                "sequence=" + sequence +
                ", time='" + time + '\'' +
                ", content='" + content + '\'' +
                ", remark='" + remark + '\'' +
                ", action=" + (action != null ? action.getName() : "null") +
                '}';
    }
}
