package com.jcoding.aiactivity.model

import com.google.gson.annotations.SerializedName

/**
 * 配置数据模型
 */
data class AppConfig(
    @SerializedName("Aibeing")
    val aibeing: AibeingConfig? = null,

    @SerializedName("style")
    val style: Map<String, StyleConfig>? = null,

    @SerializedName("question")
    val question: QuestionConfig? = null,

    @SerializedName("lottery")
    val lottery: Map<String, LotteryConfig>? = null
)

/**
 * 数字人配置
 */
data class AibeingConfig(
    @SerializedName("project")
    val project: Map<String, AibeingProject>? = null
)

data class AibeingProject(
    @SerializedName("operate")
    val operate: Map<String, List<String>>? = null,

    @SerializedName("main_pic")
    val mainPic: String? = null,

    @SerializedName("voice")
    val voice: String? = null,

    @SerializedName("default_operate")
    val defaultOperate: String? = null,

    @SerializedName("name")
    val name: String? = null
)

/**
 * 风格配置
 */
data class StyleConfig(
    @SerializedName("name")
    val name: String,

    @SerializedName("prompt")
    val prompt: String,

    @SerializedName("preview")
    val preview: String,

    @SerializedName("reference_images")
    val referenceImages: List<String>? = null,

    @SerializedName("status")
    val status: Int = 1
)

/**
 * 题库配置
 */
data class QuestionConfig(
    @SerializedName("classify")
    val classify: List<String>? = null,

    @SerializedName("catalog")
    val catalog: List<QuestionCatalog>? = null,

    @SerializedName("push_prize")
    val pushPrize: Int = 1,

    @SerializedName("default")
    val default: Int = 0,

    @SerializedName("round")
    val round: QuestionRound? = null
)

data class QuestionCatalog(
    @SerializedName("qid")
    val qid: String,

    @SerializedName("catalog_name")
    val catalogName: String,

    @SerializedName("status")
    val status: Int = 1,

    @SerializedName("file")
    val file: String
)

data class QuestionRound(
    @SerializedName("qty")
    val qty: Int = 10,

    @SerializedName("choice")
    val choice: Int = 6,

    @SerializedName("judgement")
    val judgement: Int = 4,

    @SerializedName("prize")
    val prize: Map<String, QuestionPrize>? = null
)

data class QuestionPrize(
    @SerializedName("correct_qty")
    val correctQty: Int,

    @SerializedName("prize")
    val prize: String
)

/**
 * 抽奖配置
 */
data class LotteryConfig(
    @SerializedName("file_name")
    val fileName: String,

    @SerializedName("program_name")
    val programName: String
)

/**
 * 题目数据模型
 */
data class Question(
    @SerializedName("qid")
    val qid: String,

    @SerializedName("type")
    val type: String, // choice: 选择题, judgement: 判断题

    @SerializedName("question")
    val question: String,

    @SerializedName("options")
    val options: List<String>? = null, // 选择题选项

    @SerializedName("answer")
    val answer: String, // 正确答案

    @SerializedName("explanation")
    val explanation: String? = null // 答案解析
)

data class QuestionBank(
    @SerializedName("catalog_name")
    val catalogName: String,

    @SerializedName("questions")
    val questions: List<Question>
)
