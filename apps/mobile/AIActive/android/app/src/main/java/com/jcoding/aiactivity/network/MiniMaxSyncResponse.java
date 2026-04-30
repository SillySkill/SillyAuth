package com.jcoding.aiactivity.network;

import com.google.gson.annotations.SerializedName;

/**
 * MiniMax同步语音合成响应
 * API: POST /v1/t2a_v2
 * 返回: hex编码的音频数据
 */
public class MiniMaxSyncResponse {

    @SerializedName("data")
    private Data data;

    @SerializedName("extra_info")
    private ExtraInfo extraInfo;

    @SerializedName("trace_id")
    private String traceId;

    @SerializedName("base_resp")
    private BaseResp baseResp;

    public Data getData() {
        return data;
    }

    public void setData(Data data) {
        this.data = data;
    }

    public ExtraInfo getExtraInfo() {
        return extraInfo;
    }

    public void setExtraInfo(ExtraInfo extraInfo) {
        this.extraInfo = extraInfo;
    }

    public String getTraceId() {
        return traceId;
    }

    public void setTraceId(String traceId) {
        this.traceId = traceId;
    }

    public BaseResp getBaseResp() {
        return baseResp;
    }

    public void setBaseResp(BaseResp baseResp) {
        this.baseResp = baseResp;
    }

    /**
     * 音频数据
     */
    public static class Data {
        @SerializedName("audio")
        private String audio; // hex编码的音频数据

        @SerializedName("status")
        private int status;

        public String getAudio() {
            return audio;
        }

        public void setAudio(String audio) {
            this.audio = audio;
        }

        public int getStatus() {
            return status;
        }

        public void setStatus(int status) {
            this.status = status;
        }
    }

    /**
     * 额外信息
     */
    public static class ExtraInfo {
        @SerializedName("audio_length")
        private int audioLength;

        @SerializedName("audio_sample_rate")
        private int audioSampleRate;

        @SerializedName("audio_size")
        private int audioSize;

        @SerializedName("bitrate")
        private int bitrate;

        @SerializedName("word_count")
        private int wordCount;

        @SerializedName("usage_characters")
        private int usageCharacters;

        @SerializedName("audio_format")
        private String audioFormat;

        @SerializedName("audio_channel")
        private int audioChannel;

        public int getAudioLength() {
            return audioLength;
        }

        public void setAudioLength(int audioLength) {
            this.audioLength = audioLength;
        }

        public int getAudioSampleRate() {
            return audioSampleRate;
        }

        public void setAudioSampleRate(int audioSampleRate) {
            this.audioSampleRate = audioSampleRate;
        }

        public int getAudioSize() {
            return audioSize;
        }

        public void setAudioSize(int audioSize) {
            this.audioSize = audioSize;
        }

        public int getBitrate() {
            return bitrate;
        }

        public void setBitrate(int bitrate) {
            this.bitrate = bitrate;
        }

        public int getWordCount() {
            return wordCount;
        }

        public void setWordCount(int wordCount) {
            this.wordCount = wordCount;
        }

        public int getUsageCharacters() {
            return usageCharacters;
        }

        public void setUsageCharacters(int usageCharacters) {
            this.usageCharacters = usageCharacters;
        }

        public String getAudioFormat() {
            return audioFormat;
        }

        public void setAudioFormat(String audioFormat) {
            this.audioFormat = audioFormat;
        }

        public int getAudioChannel() {
            return audioChannel;
        }

        public void setAudioChannel(int audioChannel) {
            this.audioChannel = audioChannel;
        }
    }

    /**
     * 基础响应
     */
    public static class BaseResp {
        @SerializedName("status_code")
        private int statusCode;

        @SerializedName("status_msg")
        private String statusMsg;

        public int getStatusCode() {
            return statusCode;
        }

        public void setStatusCode(int statusCode) {
            this.statusCode = statusCode;
        }

        public String getStatusMsg() {
            return statusMsg;
        }

        public void setStatusMsg(String statusMsg) {
            this.statusMsg = statusMsg;
        }
    }
}
