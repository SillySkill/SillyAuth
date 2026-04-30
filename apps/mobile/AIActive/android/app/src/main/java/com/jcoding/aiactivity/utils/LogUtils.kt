package com.jcoding.aiactivity.utils

import android.content.Context
import android.util.Log
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.*

/**
 * 日志工具类
 * 提供统一的日志输出和文件记录功能
 */
object LogUtils {

    private const val TAG = "AIActivity"
    private var isDebug = true
    private var enableFileLog = true
    private lateinit var logDir: File
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault())
    private val fileNameFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

    fun init(context: Context, debug: Boolean = true, fileLog: Boolean = true) {
        isDebug = debug
        enableFileLog = fileLog
        logDir = File(context.getExternalFilesDir(null), "logs")
        if (!logDir.exists()) {
            logDir.mkdirs()
        }
        cleanOldLogs()
    }

    fun d(tag: String, msg: String) {
        if (isDebug) {
            Log.d(TAG, "[$tag] $msg")
            writeToFile("DEBUG", tag, msg)
        }
    }

    fun i(tag: String, msg: String) {
        Log.i(TAG, "[$tag] $msg")
        writeToFile("INFO", tag, msg)
    }

    fun w(tag: String, msg: String) {
        Log.w(TAG, "[$tag] $msg")
        writeToFile("WARN", tag, msg)
    }

    fun e(tag: String, msg: String, throwable: Throwable? = null) {
        Log.e(TAG, "[$tag] $msg", throwable)
        val fullMsg = if (throwable != null) {
            "$msg\n${Log.getStackTraceString(throwable)}"
        } else {
            msg
        }
        writeToFile("ERROR", tag, fullMsg)
    }

    private fun writeToFile(level: String, tag: String, msg: String) {
        if (!enableFileLog) return

        try {
            val logFile = File(logDir, "log_${fileNameFormat.format(Date())}.txt")
            FileWriter(logFile, true).use { writer ->
                writer.append("${dateFormat.format(Date())} $level [$tag] $msg\n")
            }
        } catch (e: Exception) {
            Log.e(TAG, "写入日志文件失败", e)
        }
    }

    private fun cleanOldLogs() {
        try {
            val files = logDir.listFiles() ?: return
            val sevenDaysAgo = System.currentTimeMillis() - 7 * 24 * 60 * 60 * 1000
            files.filter { file -> file.lastModified() < sevenDaysAgo }.forEach { file -> file.delete() }
        } catch (e: Exception) {
            Log.e(TAG, "清理旧日志失败", e)
        }
    }
}
