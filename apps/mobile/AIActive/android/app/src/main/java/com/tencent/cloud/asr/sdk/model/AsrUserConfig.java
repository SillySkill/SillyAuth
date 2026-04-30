package com.tencent.cloud.asr.sdk.model;

/**
 * ASR用户配置存根类
 */
public class AsrUserConfig {
    public static final int ENGINE_MODEL_TYPE_16K_ZH = 0;
    public static final int ENGINE_MODEL_TYPE_8K_ZH = 1;
    public static final int ENGINE_MODEL_TYPE_16K_EN = 2;

    // 公开字段，直接访问
    public int engineModelType;
    private int filterDirty;
    private int filterModal;
    private int convert_num_mode;

    public void setEngineModelType(int engineModelType) {
        this.engineModelType = engineModelType;
    }

    public int getEngineModelType() {
        return engineModelType;
    }

    public void setFilterDirty(int filterDirty) {
        this.filterDirty = filterDirty;
    }

    public void setFilterModal(int filterModal) {
        this.filterModal = filterModal;
    }

    public void setConvert_num_mode(int convert_num_mode) {
        this.convert_num_mode = convert_num_mode;
    }
}
