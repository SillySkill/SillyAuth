package com.jcoding.aiactivity.utils

import android.content.Context
import java.io.*

/**
 * 文件工具类
 * 提供文件读写、复制、删除等操作
 */
object FileUtils {

    /**
     * 从assets读取文件（Java兼容方法）
     */
    @JvmStatic
    fun readAssetFile(context: Context, fileName: String): String? {
        return readTextFromAssets(context, fileName)
    }

    /**
     * 从assets读取文本文件
     */
    fun readTextFromAssets(context: Context, fileName: String): String? {
        return try {
            context.assets.open(fileName).use { inputStream ->
                BufferedReader(InputStreamReader(inputStream, "UTF-8")).use { reader ->
                    reader.readText()
                }
            }
        } catch (e: Exception) {
            LogUtils.e("FileUtils", "读取assets文件失败: $fileName", e)
            null
        }
    }

    /**
     * 从assets读取JSON文件并解析
     */
    fun readJsonFromAssets(context: Context, fileName: String): String? {
        return readTextFromAssets(context, fileName)
    }

    /**
     * 复制assets文件到指定目录
     */
    fun copyAssetFile(context: Context, assetPath: String, destPath: String): Boolean {
        return try {
            val destFile = File(destPath)
            destFile.parentFile?.mkdirs()

            context.assets.open(assetPath).use { input ->
                FileOutputStream(destFile).use { output ->
                    input.copyTo(output)
                }
            }
            true
        } catch (e: Exception) {
            LogUtils.e("FileUtils", "复制assets文件失败: $assetPath -> $destPath", e)
            false
        }
    }

    /**
     * 复制assets目录到指定目录
     */
    fun copyAssetFolder(context: Context, assetPath: String, destPath: String): Boolean {
        return try {
            val assets = context.assets.list(assetPath) ?: return false
            val destDir = File(destPath)
            if (!destDir.exists()) {
                destDir.mkdirs()
            }

            for (asset in assets) {
                val assetFullPath = if (assetPath.isEmpty()) asset else "$assetPath/$asset"
                val destFullPath = "$destPath/$asset"

                if (isAssetDirectory(context, assetFullPath)) {
                    copyAssetFolder(context, assetFullPath, destFullPath)
                } else {
                    copyAssetFile(context, assetFullPath, destFullPath)
                }
            }
            true
        } catch (e: Exception) {
            LogUtils.e("FileUtils", "复制assets目录失败: $assetPath -> $destPath", e)
            false
        }
    }

    /**
     * 判断assets路径是否为目录
     */
    private fun isAssetDirectory(context: Context, path: String): Boolean {
        return try {
            val list = context.assets.list(path)
            list != null && list.isNotEmpty()
        } catch (e: Exception) {
            false
        }
    }

    /**
     * 写入文本到文件
     */
    fun writeTextToFile(text: String, filePath: String): Boolean {
        return try {
            val file = File(filePath)
            file.parentFile?.mkdirs()
            FileWriter(file).use { writer ->
                writer.write(text)
            }
            true
        } catch (e: Exception) {
            LogUtils.e("FileUtils", "写入文件失败: $filePath", e)
            false
        }
    }

    /**
     * 读取文本文件
     */
    fun readTextFromFile(filePath: String): String? {
        return try {
            File(filePath).readText()
        } catch (e: Exception) {
            LogUtils.e("FileUtils", "读取文件失败: $filePath", e)
            null
        }
    }

    /**
     * 删除文件
     */
    fun deleteFile(filePath: String): Boolean {
        return try {
            val file = File(filePath)
            if (file.exists()) {
                file.delete()
            } else {
                true
            }
        } catch (e: Exception) {
            LogUtils.e("FileUtils", "删除文件失败: $filePath", e)
            false
        }
    }

    /**
     * 删除目录及其内容
     */
    fun deleteDirectory(dirPath: String): Boolean {
        return try {
            val dir = File(dirPath)
            if (dir.exists() && dir.isDirectory) {
                dir.deleteRecursively()
            } else {
                true
            }
        } catch (e: Exception) {
            LogUtils.e("FileUtils", "删除目录失败: $dirPath", e)
            false
        }
    }

    /**
     * 获取文件大小
     */
    fun getFileSize(filePath: String): Long {
        return try {
            File(filePath).length()
        } catch (e: Exception) {
            0L
        }
    }

    /**
     * 获取目录大小
     */
    fun getDirectorySize(dirPath: String): Long {
        return try {
            val dir = File(dirPath)
            if (dir.exists() && dir.isDirectory) {
                dir.walkTopDown().filter { it.isFile }.map { it.length() }.sum()
            } else {
                0L
            }
        } catch (e: Exception) {
            0L
        }
    }

    /**
     * 格式化文件大小
     */
    fun formatFileSize(size: Long): String {
        return when {
            size < 1024 -> "$size B"
            size < 1024 * 1024 -> String.format("%.2f KB", size / 1024.0)
            size < 1024 * 1024 * 1024 -> String.format("%.2f MB", size / (1024.0 * 1024))
            else -> String.format("%.2f GB", size / (1024.0 * 1024 * 1024))
        }
    }

    /**
     * 确保目录存在
     */
    fun ensureDirectory(dirPath: String): Boolean {
        return try {
            val dir = File(dirPath)
            if (!dir.exists()) {
                dir.mkdirs()
            } else {
                true
            }
        } catch (e: Exception) {
            LogUtils.e("FileUtils", "创建目录失败: $dirPath", e)
            false
        }
    }
}
