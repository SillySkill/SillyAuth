package com.jcoding.aiactivity.entity;

/**
 * 题目实体
 */
public class Question {

    private String questionId;       // 题目ID
    private String type;             // 题目类型：choice=选择题，judgement=判断题
    private String content;          // 题目内容
    private String[] options;        // 选项（仅选择题）
    private int correctAnswer;       // 正确答案索引：0=A/对，1=B/错，2=C，3=D
    private String explanation;      // 解析

    public Question() {
    }

    public Question(String questionId, String type, String content, int correctAnswer) {
        this.questionId = questionId;
        this.type = type;
        this.content = content;
        this.correctAnswer = correctAnswer;
    }

    // Getters and Setters
    public String getQuestionId() {
        return questionId;
    }

    public void setQuestionId(String questionId) {
        this.questionId = questionId;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String[] getOptions() {
        return options;
    }

    public void setOptions(String[] options) {
        this.options = options;
    }

    public int getCorrectAnswer() {
        return correctAnswer;
    }

    public void setCorrectAnswer(int correctAnswer) {
        this.correctAnswer = correctAnswer;
    }

    public String getExplanation() {
        return explanation;
    }

    public void setExplanation(String explanation) {
        this.explanation = explanation;
    }

    /**
     * 判断是否是选择题
     */
    public boolean isChoice() {
        return "choice".equals(type);
    }

    /**
     * 判断是否是判断题
     */
    public boolean isJudgement() {
        return "judgement".equals(type);
    }
}
