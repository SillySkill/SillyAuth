package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.text.TextUtils;
import android.util.Log;

import androidx.camera.core.CameraSelector;

import com.jcoding.aiactivity.utils.PreferenceUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * 摄像头设备管理器
 * 负责检测和管理内置摄像头、USB摄像头和WiFi摄像头
 */
public class CameraDeviceManager {
    private static final String TAG = "CameraDeviceManager";
    private static final String PREF_SELECTED_CAMERA_ID = "selected_camera_id";
    private static final String PREF_WIFI_CAMERA_RTSP = "wifi_camera_rtsp";

    private static CameraDeviceManager instance;
    private Context context;
    private List<CameraInfo> availableCameras;
    private CameraInfo selectedCamera;

    private CameraDeviceManager(Context context) {
        this.context = context.getApplicationContext();
        this.availableCameras = new ArrayList<>();
        loadSelectedCamera();
    }

    public static synchronized CameraDeviceManager getInstance(Context context) {
        if (instance == null) {
            instance = new CameraDeviceManager(context);
        }
        return instance;
    }

    /**
     * 摄像头类型枚举
     */
    public enum CameraType {
        FRONT("前置摄像头"),
        BACK("后置摄像头"),
        USB("USB摄像头"),
        WIFI("WiFi摄像头");

        private String displayName;

        CameraType(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    /**
     * 摄像头信息类
     */
    public static class CameraInfo {
        private String cameraId;          // Camera2的cameraId或自定义ID
        private String cameraName;        // 显示名称
        private CameraType type;          // 摄像头类型
        private String rtspUrl;           // WiFi摄像头的RTSP地址

        public CameraInfo(String cameraId, String cameraName, CameraType type) {
            this.cameraId = cameraId;
            this.cameraName = cameraName;
            this.type = type;
        }

        public CameraInfo(String cameraId, String cameraName, CameraType type, String rtspUrl) {
            this.cameraId = cameraId;
            this.cameraName = cameraName;
            this.type = type;
            this.rtspUrl = rtspUrl;
        }

        public String getCameraId() {
            return cameraId;
        }

        public String getCameraName() {
            return cameraName;
        }

        public CameraType getType() {
            return type;
        }

        public String getRtspUrl() {
            return rtspUrl;
        }

        @Override
        public String toString() {
            return cameraName;
        }
    }

    /**
     * 检测所有可用的摄像头设备
     */
    public void detectCameras() {
        availableCameras.clear();
        CameraManager cameraManager = (CameraManager) context.getSystemService(Context.CAMERA_SERVICE);

        if (cameraManager != null) {
            try {
                String[] cameraIds = cameraManager.getCameraIdList();

                for (String cameraId : cameraIds) {
                    CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(cameraId);
                    Integer facing = characteristics.get(CameraCharacteristics.LENS_FACING);

                    if (facing != null) {
                        CameraType type;
                        String cameraName;

                        // 判断是前置还是后置摄像头
                        if (facing == CameraCharacteristics.LENS_FACING_FRONT) {
                            type = CameraType.FRONT;
                            cameraName = "前置摄像头";
                        } else if (facing == CameraCharacteristics.LENS_FACING_BACK) {
                            type = CameraType.BACK;
                            cameraName = "后置摄像头";
                        } else {
                            // 外置摄像头（如USB摄像头）
                            type = CameraType.USB;
                            cameraName = "USB摄像头 " + cameraId;
                        }

                        CameraInfo info = new CameraInfo(cameraId, cameraName, type);
                        availableCameras.add(info);
                        Log.d(TAG, "检测到摄像头: " + cameraName + " (ID: " + cameraId + ")");
                    }
                }
            } catch (CameraAccessException e) {
                Log.e(TAG, "访问摄像头失败", e);
            }
        }

        // 添加WiFi摄像头（如果已配置）
        String wifiRtspUrl = PreferenceUtils.getString(context, PREF_WIFI_CAMERA_RTSP, "");
        if (!TextUtils.isEmpty(wifiRtspUrl)) {
            CameraInfo wifiCamera = new CameraInfo("wifi_camera", "WiFi摄像头", CameraType.WIFI, wifiRtspUrl);
            availableCameras.add(wifiCamera);
            Log.d(TAG, "检测到WiFi摄像头: " + wifiRtspUrl);
        }

        Log.d(TAG, "总共检测到 " + availableCameras.size() + " 个摄像头设备");
    }

    /**
     * 获取所有可用的摄像头列表
     */
    public List<CameraInfo> getAvailableCameras() {
        if (availableCameras.isEmpty()) {
            detectCameras();
        }
        return availableCameras;
    }

    /**
     * 获取选中的摄像头
     */
    public CameraInfo getSelectedCamera() {
        if (selectedCamera == null) {
            // 默认选择后置摄像头
            detectCameras();
            for (CameraInfo camera : availableCameras) {
                if (camera.getType() == CameraType.BACK) {
                    selectedCamera = camera;
                    break;
                }
            }
            // 如果没有后置摄像头，选择第一个可用的
            if (selectedCamera == null && !availableCameras.isEmpty()) {
                selectedCamera = availableCameras.get(0);
            }
        }
        return selectedCamera;
    }

    /**
     * 设置选中的摄像头
     */
    public void setSelectedCamera(CameraInfo camera) {
        this.selectedCamera = camera;
        if (camera != null) {
            PreferenceUtils.putString(context, PREF_SELECTED_CAMERA_ID, camera.getCameraId());
            Log.d(TAG, "已选择摄像头: " + camera.getCameraName());
        }
    }

    /**
     * 根据cameraId获取CameraInfo
     */
    public CameraInfo getCameraById(String cameraId) {
        for (CameraInfo camera : availableCameras) {
            if (camera.getCameraId().equals(cameraId)) {
                return camera;
            }
        }
        return null;
    }

    /**
     * 设置WiFi摄像头的RTSP地址
     */
    public void setWifiCameraRtspUrl(String rtspUrl) {
        PreferenceUtils.putString(context, PREF_WIFI_CAMERA_RTSP, rtspUrl);
        // 重新检测摄像头列表
        detectCameras();
    }

    /**
     * 获取WiFi摄像头的RTSP地址
     */
    public String getWifiCameraRtspUrl() {
        return PreferenceUtils.getString(context, PREF_WIFI_CAMERA_RTSP, "");
    }

    /**
     * 加载之前保存的摄像头选择
     */
    private void loadSelectedCamera() {
        String savedCameraId = PreferenceUtils.getString(context, PREF_SELECTED_CAMERA_ID, "");
        if (!TextUtils.isEmpty(savedCameraId)) {
            detectCameras();
            selectedCamera = getCameraById(savedCameraId);
            if (selectedCamera == null) {
                Log.w(TAG, "未找到之前选择的摄像头ID: " + savedCameraId);
            }
        }
    }

    /**
     * 获取CameraSelector用于CameraX
     * 注意：WiFi摄像头不支持CameraX，需要特殊处理
     */
    public CameraSelector getCameraSelector() {
        CameraInfo camera = getSelectedCamera();
        if (camera == null) {
            return CameraSelector.DEFAULT_BACK_CAMERA;
        }

        switch (camera.getType()) {
            case FRONT:
                return CameraSelector.DEFAULT_FRONT_CAMERA;
            case BACK:
            case USB:
                // 对于USB摄像头，尝试使用后置摄像头选择器
                return CameraSelector.DEFAULT_BACK_CAMERA;
            case WIFI:
                // WiFi摄像头不支持CameraX，需要返回null并使用其他方式
                return null;
            default:
                return CameraSelector.DEFAULT_BACK_CAMERA;
        }
    }

    /**
     * 检查当前选择的摄像头是否需要使用RTSP流
     */
    public boolean isRtspCamera() {
        CameraInfo camera = getSelectedCamera();
        return camera != null && camera.getType() == CameraType.WIFI;
    }
}
