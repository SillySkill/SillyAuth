package com.jcoding.aiactivity

import android.app.Application
import android.content.Context
import androidx.multidex.MultiDex
import com.jcoding.aiactivity.manager.ConfigManager
import com.jcoding.aiactivity.network.ConfigPushManager
// import com.jcoding.aiactivity.manager.SpeechSynthesizerManager  // 暂时注释
// import com.jcoding.aiactivity.manager.SpeechRecognizerManager  // 暂时注释
import com.jcoding.aiactivity.utils.LogUtils

/**
 * AI活动秀应用程序类
 * 负责全局初始化和配置管理
 */
class AIApplication : Application() {

    companion object {
        private lateinit var instance: AIApplication

        @JvmStatic
        fun getInstance(): AIApplication = instance

        @JvmStatic
        fun getContext(): Context = instance.applicationContext
    }

    override fun attachBaseContext(base: Context?) {
        super.attachBaseContext(base)
        MultiDex.install(this)
    }

    override fun onCreate() {
        super.onCreate()
        instance = this

        // 初始化日志工具
        LogUtils.init(this)

        // 初始化配置管理器
        ConfigManager.getInstance(this)

        // 初始化TTS和ASR模块
        initializeVoiceModules()

        // 初始化推送服务
        initializePushService()

        LogUtils.d("AIApplication", "应用初始化完成")
    }

    /**
     * 初始化语音模块（TTS和ASR）
     * 暂时注释以快速构建测试候选人功能
     */
    private fun initializeVoiceModules() {
        /*
        try {
            val configManager = ConfigManager.getInstance(this)

            // 初始化TTS（语音合成）
            val ttsLicenseId = configManager.ttsLicenseId
            val ttsLicenseKey = configManager.ttsLicenseKey
            val ttsLicensePk = configManager.ttsLicensePk

            if (ttsLicenseId.isNotEmpty() && ttsLicenseKey.isNotEmpty() && ttsLicensePk.isNotEmpty()) {
                val ttsManager = SpeechSynthesizerManager.getInstance(this)
                ttsManager.setConfig(ttsLicenseId, ttsLicenseKey, ttsLicensePk)
                LogUtils.d("AIApplication", "TTS初始化成功 - LicenseId: $ttsLicenseId")
            } else {
                LogUtils.w("AIApplication", "TTS配置不完整，跳过初始化")
            }

            // 初始化ASR（语音识别）
            val asrLicenseId = configManager.asrLicenseId
            val asrLicenseKey = configManager.asrLicenseKey
            val asrLicensePk = configManager.asrLicensePk

            if (asrLicenseId.isNotEmpty() && asrLicenseKey.isNotEmpty() && asrLicensePk.isNotEmpty()) {
                val asrManager = SpeechRecognizerManager.getInstance(this)
                asrManager.setConfig(asrLicenseId, asrLicenseKey, asrLicensePk)
                LogUtils.d("AIApplication", "ASR初始化成功 - LicenseId: $asrLicenseId")
            } else {
                LogUtils.w("AIApplication", "ASR配置不完整，跳过初始化")
            }

        } catch (e: Exception) {
            LogUtils.e("AIApplication", "初始化语音模块失败", e)
        }
        */
    }

    /**
     * 初始化推送服务
     */
    private fun initializePushService() {
        try {
            val pushManager = ConfigPushManager.getInstance(this)
            pushManager.start()
            LogUtils.d("AIApplication", "推送服务已启动")
        } catch (e: Exception) {
            LogUtils.e("AIApplication", "启动推送服务失败", e)
        }
    }
}
