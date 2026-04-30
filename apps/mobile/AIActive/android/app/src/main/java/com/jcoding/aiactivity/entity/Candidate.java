package com.jcoding.aiactivity.entity;

/**
 * 抽奖候选人实体
 */
public class Candidate {

    private String id;
    private String name;
    private String phone;
    private String department;

    public Candidate() {
    }

    public Candidate(String id, String name, String phone, String department) {
        this.id = id;
        this.name = name;
        this.phone = phone;
        this.department = department;
    }

    // Getters and Setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    @Override
    public String toString() {
        return name + " (" + department + ")";
    }
}
