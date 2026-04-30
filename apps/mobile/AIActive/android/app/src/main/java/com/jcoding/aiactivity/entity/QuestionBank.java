package com.jcoding.aiactivity.entity;

import java.util.List;

/**
 * 题库实体
 */
public class QuestionBank {

    private String bankId;           // 题库ID
    private String bankName;         // 题库名称
    private int status;              // 状态：1=启用，0=禁用
    private String fileName;         // 题库文件名
    private List<Question> questions; // 题目列表

    public QuestionBank() {
    }

    public QuestionBank(String bankId, String bankName, String fileName, int status) {
        this.bankId = bankId;
        this.bankName = bankName;
        this.fileName = fileName;
        this.status = status;
    }

    // Getters and Setters
    public String getBankId() {
        return bankId;
    }

    public void setBankId(String bankId) {
        this.bankId = bankId;
    }

    public String getBankName() {
        return bankName;
    }

    public void setBankName(String bankName) {
        this.bankName = bankName;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public List<Question> getQuestions() {
        return questions;
    }

    public void setQuestions(List<Question> questions) {
        this.questions = questions;
    }

    public boolean isEnabled() {
        return status == 1;
    }

    /**
     * 获取题目总数
     */
    public int getQuestionCount() {
        return questions != null ? questions.size() : 0;
    }
}
