# 腾讯云离在线语音合成（android）

### 合成接口
 <br />


####  获得TTS合成器实例

```java
//获得实例
TtsController mTtsController = TtsController.getInstance();  

//销毁实例
TtsController.release();
```

 <br />

#### 初始化引擎
```java
mTtsController.init(Context context,TtsMode mode,TtsResultListener listener) 
```
**TtsMode**: TTS合成器工作模式参数（如果您下载的压缩包为"xxx_offline.zip"，则支持以下三种模式，如果为"xxx_online.zip"，则仅支持在线模式）

| 枚举      | 说明 |
| ----------- | ----------- |
| TtsMode.OFFLINE   | 离线       |
| TtsMode.ONLINE   | 在线        |
| TtsMode.MIX   | 混合        |

**TtsResultListener**: 合成监听器，用于获取合成结果

 <br />

####  在线模式参数配置(不使用则不需要配置)

**TtsController配置参数方法**

| 接口       |    说明 |
| -------------- | -------------- |
| setAppId(long l)   | 配置腾讯云appi       |
| setSecretId(String s)   | 配置腾讯云SecretId        |
| setSecretKey(String s)   | 配置腾讯云SecretKey        |
| setToken(String s)   | STS临时证书鉴权时需要设置Token        |
| setOnlineVoiceSpeed(float f)     | 设置在线所合成音频的语速,语速，范围：[-2，2]，分别对应不同语速：-2代表0.6倍,-1代表0.8倍,0代表1.0倍（默认）,1代表1.2倍,2代表1.5倍,如果需要更细化的语速，可以保留小数点后一位，例如0.5 1.1 1.8等。        |
| setOnlineVoiceVolume(float f)   | 设置在线所合成音频的音量       |
| setOnlineVoiceType(int i)   | 设置在线所合成音频的音色id,完整的音色id列表见https://cloud.tencent.com/document/product/1073/37995        |
| setOnlineVoiceLanguage(int i)   | 主语言类型：1-中文（默认）2-英文        |
| setOnlineCodec(String s)   | 在线模式编码格式，非业务必要不建议更改:默认mp3，目前支持"mp3"\"wav"\"pcm",如更改为pcm不支持播放        |
| setConnectTimeout(int i)   | 连接超时默认15000ms(15s) 范围[500,30000] 单位ms ， Mix模式下建议调小此值，以获得更好的体验        |
| setReadTimeout(int i)   | 读取超时超时默认30000ms(30s) 范围[2200,60000] 单位ms， Mix模式下建议调小此值，以获得更好的体验        |
| setCheckNetworkIntervalTime(int i)   | Mix模式下，已经连接网络，但出现网络错误或者后台错误后的检测间隔时间，用于从离线模式自动切换回在线模式，默认值5分钟 |

**示例**
```java
mTtsController.setAppId(0L);
mTtsController.setSecretId("AKIDs*********LbFHp7");
mTtsController.setSecretKey("D9tdAM******Lmxvc2");
mttsController.setToken(null);
mTtsController.setOnlineVoiceSpeed(mVoiceSpeed);
mTtsController.setOnlineVoiceVolume(1.0);
mTtsController.setOnlineVoiceType(1001);
mTtsController.setOnlineVoiceLanguage(1);
mTtsController.setOnlineCodec("mp3");
mTtsController.setConnectTimeout(15 *1000);
mTtsController.setReadTimeout(30 *1000);
mTtsController.setCheckNetworkIntervalTime(5 * 60);

```

 <br />

#### 离线线模式参数配置(不使用则不需要配置)

**TtsController配置参数方法**

| 接口       |    说明 |
| -------------- | -------------- |
| setOfflineVoiceSpeed(long l)   | 离线音量 > 0       |
| setOfflineVoiceVolume(long l)   | 离线语速[0.5,2.0]        |
| setOfflineVoiceType(String s)   | 离线音色名称，名称配置位于音色资源目录\voices\config.json 中，可自行删除或增加音色，音色需要授权，对应音色如未授权合成时会报错，可联系腾讯云商务购买。 |
| setOfflineResourceDir(path) | 设置离线模型资源所在路径 |
| setOfflineAuthParamDoOnline(boolean refreshAuth,String SecretId, String SecretKey, String licKey, String licPk) | 在线拉取鉴权文件接口，首次激活离线SDK模块需要联网。refreshAuth：是否强制联网刷新授权(false:仅第一次联网激活下载授权文件; true:每次都联网刷新授权文件，无网络下将激活失败) ；secret_id/secret_key:购买离线SDK所在账号的腾讯云授权凭证，请从官网控制台获取；lic_key/lic_pk:离线SDK的LicenseKey、LicensePk，请从官网控制台获取。 |
| setOfflineAuthParamDoOffline(String lic, String authSign, String licPk) | 纯离线授权接口，首次激活离线SDK模块也不需要需要联，仅支持按应用授权方式；lic /authSign/licPk：离线SDK的 AuthLicense、AuthSign、LicensePk，请从官网控制台获取。 |

**示例**

```java
mTtsController.setOfflineResourceDir("/sdcard/res");
mTtsController.setOfflineVoiceSpeed(1.0f);
mTtsController.setOfflineVoiceVolume(1.0f);
mTtsController.setOfflineVoiceType("pb");
```

<br>

#### 合成文本入参接口

| 接口                                        | 说明                                                         |
| ------------------------------------------- | ------------------------------------------------------------ |
| synthesize(String text, String utteranceId) | text为需要合成的文本；utteranceId为标记该文本的id, 将随合成结果返回宿主层 |
| synthesize(String text)                     | text为需要合成的文本                                         |

**示例**

```java
//内部有维护队列，可持续添加语句，SDK内将依次合成
TtsError error = null;
error = mTtsController.synthesize("今天天气不错","第1句");
error = mTtsController.synthesize("腾讯云语音合成","第2句");
error = mTtsController.synthesize("腾讯云AI","第3句");
error = mTtsController.synthesize("腾讯云AI","第4句");

//取消未合成的任务并清空内部队列
mTtsController.cancel();
```






#### 合成监听器，用于获取合成结果
实例化*TtsResultListener*时，默认需要重写*onSynthesizeData()*和*onError()*方法

**onSynthesizeData()方法签名说明**

| 参数         |    说明 |
| -------------- | -------------- |
| byte[] bytes   | 语音数据       |
| String utteranceId   | 语句id       |
| String text  | 文本 |
| int engineType   | 引擎类型 0:在线 1:离线      |

**onError()方法签名说明**

| 参数         |    说明 |
| -------------- | -------------- |
| TtsError error   | 错误信息，无错误返回null |
| String utteranceId   | 语句id(如果有则返回)       |
| String text  | 文本(如果有则返回) |

**onOfflineAuthInfo()方法签名说明**

| 参数                                 | 说明                                                         |
| ------------------------------------ | ------------------------------------------------------------ |
| offlineAuthInfo.getExpireTime()      | 授权到期时间                                                 |
| offlineAuthInfo.getError().getCode() | 0为授权成功，其他为失败                                      |
| offlineAuthInfo.getResponse()        | 使用在线拉取授权文件的方式鉴权时，服务器返回的Response数据（仅授权失败时需要关注） |





**示例**

```java
TtsResultListener listener = new TtsResultListener() {

    @Override
    public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType) {
    	// 您可以在这里将音频保存或者送入播放接口播放，可调用播放器入参接口入参
    }
    
    @Override
    public void onError(TtsError error, String utteranceId, String text) {
        // 您可以在这里添加错误后处理
        //注：实际业务上判断一下，如果是混合模式下返回在线合成的后端错误码，应当忽略，可不做处理，SDK内会调用离线合成继续工作
    }
  
    @Override
    public void onOfflineAuthInfo(QCloudOfflineAuthInfo offlineAuthInfo) {
          //offlineAuthInfo 返回离线sdk授权信息，包含错误码、到期时间、当前设备ID、已授权的音色列表
           //注意，如果使用离线模式，需要收到此回调后再调用合成接口，否则可能会因授权失败导致合成失败！！！
   }

    @Override
    void onChunk(ByteBuffer chunk) {
        // 离线合成返回的流式数据,格式为16k 单通道pcm
    }
}
```

---

### 播放接口
<br>

#### 初始化播放器

如果sdk的内置播放器无法满足您的需求，您也可以使用自己实现的播放器替换。demo中也额外提供了一份播放器源码，您可以修改播放器逻辑，源代码位于MediaPlayerDemo.java，与SDK内置播放器一致。

```java

//使用SDK中提供的播放器
QCloudMediaPlayer mediaPlayer = new QCloudMediaPlayer(new QCloudPlayerCallback() { 
    
    @Override
    public void onTTSPlayStart() {
        Log.d(TAG, "开始播放");
    }

    @Override
    public void onTTSPlayWait() {
        Log.d(TAG, "播放完成，等待音频数据");
    }

    @Override
    public void onTTSPlayResume() {
        Log.d(TAG, "恢复播放");
    }

    @Override
    public void onTTSPlayPause() {
        Log.d(TAG, "暂停播放");
    }

    @Override
    public void onTTSPlayNext(String text, String utteranceId) {
        Log.d(TAG, "开始播放: " + utteranceId + "|" + text);
    }

    @Override
    public void onTTSPlayStop() {
        Log.d(TAG, "播放停止，内部队列已清空");
    }

    @Override
    public void onTTSPlayError(QPlayerError error) {
        Log.d(TAG, "播放器发生异常:"+error.getmCode() + ":" + error.getmMessage());
    }

    /**
     * @param currentWord 当前播放的字符（此为预估值）
     * @param currentIndex 当前播放的字符在所在的句子中的下标（此为预估值）
     */
    @Override
    public void onTTSPlayProgress(String currentWord, int currentIndex) {
        Log.d(TAG, "onTTSPlayProgress: " + currentWord + "|" + currentIndex);
    }
});
```

<br>

#### 播放器入参

**enqueue()方法签名说明**

| 参数         |    说明 |
| -------------- | -------------- |
| byte[] bytes   | 返回音频流，通过传入字节数组播放 |
| File audio   | 返回音频文件，通过传入文件播放     |
| String text  | 音频对应的文本 |
| String utteranceId  | 文本id |

**示例**

```java
//通过音频数据入参
QPlayerError err = mediaPlayer.enqueue(byte[] bytes,String text,String utteranceId);

//通过音频文件入参
QPlayerError err = mediaPlayer.enqueue(File audio,String text,String utteranceId);
```

### 离线音色名称
||
|-|
M206       --- 智皓
db1        --- 智聆
db3        --- 智萌
db7        --- 智甜
f0         --- 智莉
f2         --- 智芸
femozhifou --- 智蓉
fn         --- 智瑜
kefu       --- 智美
kefu2      --- 智娜
kefu3      --- 智琪
m0         --- 智云
m25        --- 智华
memozhifou --- 智靖
newsman    --- 智宁
pb         --- 智逍遥
xiaowei    --- 智言
