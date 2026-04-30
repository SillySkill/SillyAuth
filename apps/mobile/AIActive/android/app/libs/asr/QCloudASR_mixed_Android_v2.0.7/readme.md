# Android SDK
## 开发相关

### 开发准备
- 支持 Android 4.1 以上版本 API LEVEL 16
- 不支持模拟器

### 硬件要求

- CPU: 支持armv7,armv8指令集,主频1.5GHz以上
- 独占内存: 至少200M
- 独占存储: 至少40M

### 下载安装SDK
- SDK包含demo和SDK两部分

#### 简介

SDK支持离线,在线及混合三种模式.其中ASRController为SDK的核心类,包含授权设置,参数设置,模式设置和运行控制.使用时需根据业务所需要的模式进行授权设置,参数设置和模式设置(详见接口说明部分).

运行控制对于三种模式逻辑是一致的,进行识别前需设置数据源和事件监听,start与stop用于控制整体流程,调用start后成功开始回调onStart,失败回调onError,调用stop后成功停止回调onStop,失败回调onError,其余回调均为识别过程中的事件消息(详见接口说明部分)


### 接口说明

#### ASRController
语音识别控制类

- **GlobalInstance**
```
static ASRController GlobalInstance()
```
获取语音识别控制类全局实例

- **setMode**
```
void setMode(MODE val)
```
设置控制器模式.支持离线模式、在线模式和混合模式

- **doAppAuth**
```
ASRControllerError doAppAuth(Context context, String lic, String licPk, String authSign)
```
按应用授权(仅对离线模式和混合模式生效)

**参数**
|          |                         |
| -------- | ----------------------- |
| context  | Android Context         |
| lic      | 离线SDK授权 LicenseKey  |
| licPk    | 离线SDK授权 LicensePk   |
| authSign | 离线SDK授权 LicenseSign |

- **doDeviceAuth**
```
ASRControllerError doDeviceAuth(Context context, String secretId, String secretKey, String token, String licKey, String licPk)
```
按设备授权(仅对离线模式和混合模式生效)

**参数**
|           |                                                              |
| --------- | ------------------------------------------------------------ |
| context   | Android Context                                              |
| secretId  | 腾讯云secret_id,通过https://console.cloud.tencent.com/cam/capi获取 |
| secretKey | 腾讯云  secret_key,通过https://console.cloud.tencent.com/cam/capi获取 |
| token     | 腾讯云 STS鉴权token,使用STS临时鉴权时使用，不使用STS鉴权传null |
| licKey    | 离线SDK授权 LicenseKey                                       |
| licPk     | 离线SDK授权 LicensePk                                        |

- **load**
```
ASRControllerError load(String path, String name)
```
载入模型(仅对离线模式和混合模式生效),需再授权完成后调用

**参数**
|      |                  |
| ---- | ---------------- |
| path | 模型所在文件目录 |
| name | 模型名称         |

- **unload**
```
ASRControllerError unload()
```
卸载模型(仅对离线模式和混合模式生效),与load配对使用

- **setOnlineAuth**
```
void setOnlineAuth(String appId, String secretId, String secretKey, String token)
```
设置在线认证参数(仅对在线模式和混合模式生效)

**参数**
|           |                 |
| --------- | --------------- |
| appId     | 腾讯云appID     |
| secretId  | 腾讯云secretId  |
| secretKey | 腾讯云secretKey |
| token     | 腾讯云临时token |

**setOnlineParams**
```
void setOnlineParams(String engine_model_type, int needvad, int voice_format, String hotword_id, int reinforce_hotword, String customization_id, int filter_dirty, int filter_modal, int filter_punc, int convert_num_mode, int word_info, int vad_silence_time, float noise_threshold)
```
设置在线识别参数(仅对在线模式和混合模式生效),默认参数请参考demo示例

**参数**
|                   |                                           |
| ----------------- | ----------------------------------------- |
| engine_model_type | 请参考API文档                             |
| needvad           | 请参考API文档                             |
| voice_format      | SDK仅支持1(pcm)和10(opus),请参考API文档   |
| hotword_id        | 请参考API文档                             |
| reinforce_hotword | 请参考API文档                             |
| customization_id  | 请参考API文档                             |
| filter_dirty      | 请参考API文档                             |
| filter_modal      | 请参考API文档                             |
| filter_punc       | 请参考API文档                             |
| convert_num_mode  | 请参考API文档                             |
| word_info         | 请参考API文档                             |
| vad_silence_time  | 传入小于等于0 SDK忽略该参数,请参考API文档 |
| noise_threshold   | 请参考API文档                             |

- **start**
```
void start()
```
开始识别,请在设置ASRControllerDataSource和ASRControllerListener后调用

- **stop**
```
void stop()
```
停止识别

#### ASRControllerError
包含错误码及错误信息
**错误码**
|                    |     |                |
| ------------------ | --- | -------------- |
| UNKNOWN            | -1  | 未知错误       |
| SUCCESS            | 0   | 成功           |
| NETWORK_ERROR      | 1   | 网络错误       |
| SERVER_ERROR       | 2   | 服务器错误     |
| ENGINE_INIT_ERROR  | 3   | 引擎初始化错误 |
| ENGINE_AUTH_ERROR  | 4   | 引擎认证错误   |
| DATASOURCE_INVALID | 5   | 数据源错误     |
| STATE_ERROR        | 6   | 状态错误       |
| ENGINE_ERROR       | 7   | 引擎错误       |
| ONLINE_AUTH_ERROR  | 8   | 在线认证错误   |

#### ASRControllerListener
用于同步识别过程中的事件

onBegin,onSlice,onSegment与一段话识别有关,调用有以下几种情况
1. onBegin->onSlice->onSegment
2. onBegin->onSegment
3. onSegment

- **onBegin**
```
void onBegin(String extra)
```
一段话开始识别

**参数**
|       |                                                                |
| ----- | -------------------------------------------------------------- |
| extra | 在线模式及混合模式处于在线状态时为服务端返回信息,请参考API文档 |

- **onSlice**
```
void onSlice(String val, String extra)
```
一段话开始识别中

**参数**
|       |                                                                |
| ----- | -------------------------------------------------------------- |
| val   | 非稳态识别结果                                                 |
| extra | 在线模式及混合模式处于在线状态时为服务端返回信息,请参考API文档 |

- **onSegment**
```
void onSegment(String val, String extra)
```
一段话开始识别结束

**参数**
|       |                                                                |
| ----- | -------------------------------------------------------------- |
| val   | 稳态识别结果                                                   |
| extra | 在线模式及混合模式处于在线状态时为服务端返回信息,请参考API文档 |

- **onStart**
```
void onStart(String extra)
```
识别任务开始

**参数**
|       |                                                                |
| ----- | -------------------------------------------------------------- |
| extra | 在线模式及混合模式处于在线状态时为服务端返回信息,请参考API文档 |

- **onError**
```
void onError(ASRControllerError val)
```
识别任务结束

**参数**
|     |          |
| --- | -------- |
| val | 错误信息 |

**onStop**
```
void onStop()
```
识别任务停止 

**onSwitch**
```
void onSwitch(boolean is_online)
```
模式切换(仅混合)

**参数**
|           |                                |
| --------- | ------------------------------ |
| is_online | true为在线状态,false为离线状态 |

#### ASRControllerDataSource
提供16000Hz,16bit(le),单声道的数据源用于识别

- **read**
```
long read(ByteBuffer data)
```
**参数**
|            |          |
| ---------- | -------- |
| ByteBuffer | 传入数据 |

返回实际写入长度