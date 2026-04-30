package com.jcoding.aiactivity.entity;

import java.util.HashMap;
import java.util.Map;

/**
 * 内场秀子模块配置
 *
 * 每个子模块都有独立的配置：
 * - 是否接收广播信息
 * - 广播信息静音
 * - 是否开启语音设置
 */
public class InnerShowModuleConfig {

    private InnerShowModule module;
    private boolean acceptBroadcast;      // 是否接收广播信息
    private boolean broadcastMuted;       // 广播信息静音
    private boolean voiceEnabled;         // 是否开启语音功能

    public InnerShowModuleConfig(InnerShowModule module) {
        this.module = module;
        // 默认配置
        this.acceptBroadcast = true;
        this.broadcastMuted = false;
        this.voiceEnabled = true;
    }

    public InnerShowModule getModule() {
        return module;
    }

    public void setModule(InnerShowModule module) {
        this.module = module;
    }

    public boolean isAcceptBroadcast() {
        return acceptBroadcast;
    }

    public void setAcceptBroadcast(boolean acceptBroadcast) {
        this.acceptBroadcast = acceptBroadcast;
    }

    public boolean isBroadcastMuted() {
        return broadcastMuted;
    }

    public void setBroadcastMuted(boolean broadcastMuted) {
        this.broadcastMuted = broadcastMuted;
    }

    public boolean isVoiceEnabled() {
        return voiceEnabled;
    }

    public void setVoiceEnabled(boolean voiceEnabled) {
        this.voiceEnabled = voiceEnabled;
    }

    /**
     * 转换为Map（用于存储）
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("module_id", module.getId());
        map.put("accept_broadcast", acceptBroadcast);
        map.put("broadcast_muted", broadcastMuted);
        map.put("voice_enabled", voiceEnabled);
        return map;
    }

    /**
     * 从Map创建
     */
    public static InnerShowModuleConfig fromMap(Map<String, Object> map) {
        String moduleId = (String) map.get("module_id");
        InnerShowModule module = InnerShowModule.fromId(moduleId);

        InnerShowModuleConfig config = new InnerShowModuleConfig(module);
        config.acceptBroadcast = Boolean.TRUE.equals(map.get("accept_broadcast"));
        config.broadcastMuted = Boolean.TRUE.equals(map.get("broadcast_muted"));
        config.voiceEnabled = Boolean.TRUE.equals(map.get("voice_enabled"));

        return config;
    }
}
