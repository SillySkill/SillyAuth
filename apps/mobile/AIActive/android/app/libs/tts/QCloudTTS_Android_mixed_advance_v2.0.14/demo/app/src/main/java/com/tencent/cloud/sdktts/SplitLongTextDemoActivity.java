package com.tencent.cloud.sdktts;

import static com.tencent.cloud.libqcloudtts.engine.offlineModule.auth.AuthErrorCode.OFFLINE_AUTH_SUCCESS;

import android.content.Context;

import android.media.AudioManager;

import android.os.Bundle;


import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import androidx.appcompat.app.AppCompatActivity;

import android.text.TextUtils;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;



import com.tencent.cloud.libqcloudtts.MediaPlayer.QCloudMediaPlayer;
import com.tencent.cloud.libqcloudtts.MediaPlayer.QCloudPlayerCallback;
import com.tencent.cloud.libqcloudtts.MediaPlayer.QPlayerError;
import com.tencent.cloud.libqcloudtts.TtsController;
import com.tencent.cloud.libqcloudtts.TtsError;
import com.tencent.cloud.libqcloudtts.TtsMode;
import com.tencent.cloud.libqcloudtts.TtsResultListener;
import com.tencent.cloud.libqcloudtts.engine.offlineModule.auth.QCloudOfflineAuthInfo;
import com.tencent.cloud.libqcloudtts.utils.AAILogger;


import java.nio.ByteBuffer;
import java.util.ArrayList;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


/**
 * 合成语音的源文本：中文最大支持150个汉字(全角标点符号算一个汉字)、英文最大支持500个字母(半角标点符号算一个字母)
 *
 * 长文本: 超过150个汉字或者英文超过500个字母
 *
 * 该类主要介绍如何对长文本进行语音合成
 * 具体做法：将长文本在Demo层进行切割，再分别调用基础语音合成接口分段合成(详情见: https://cloud.tencent.com/document/product/1073/37995)
 */
public class SplitLongTextDemoActivity extends AppCompatActivity {

    private static final String TAG = SplitLongTextDemoActivity.class.getSimpleName();
    private volatile TtsController mTtsController;
    private EditText tv_test_tts;


    private AudioManager.OnAudioFocusChangeListener listener;

    private QCloudMediaPlayer mediaPlayer; //使用SDK内置播放器
//    private MediaPlayerDemo mediaPlayer;//使用demo中提供的播放器，您可以修改播放器逻辑，源代码位于MediaPlayerDemo.java，与SDK内置播放器一致

    TtsMode mTtsmode = TtsMode.ONLINE;

    //离线参数
    String mOfflineVoiceType = "pb";//音色名，名称配置位于音色资源目录\voices\config.json 中
    float mOfflineVolume = 1.0f;//离线音量 > 0
    float mOfflineSpeed = 1.0f;//离线语速[0.5,2.0]
    //在线参数
    float mVoiceSpeed = 0;
    float mVoiceVolume = 0;
    int mVoiceType = 1001;
    int mPrimaryLanguage = 1;
    //时间配置
    int mConnectTimeout = 15 *1000; //连接超时默认15000ms(15s) 范围[500,30000] 单位ms ， Mix模式下建议调小此值，以获得更好的体验
    int mReadTimeout = 30 *1000; //读取超时超时默认30000ms(30s) 范围[2200,60000] 单位ms， Mix模式下建议调小此值，以获得更好的体验
    /**
     * Mix模式下，已经连接网络，但出现网络错误或者后台错误后的检测间隔时间，用于从离线模式自动切换回在线模式，默认值5分钟
     * 注意：每次检测时将使用所入参的一句文本请求服务器，如果后端合成成功将会额外消耗该句字数的合成额度
     * @param mCheckNetworkIntervalTime 大于等于0 单位s, 等于0时持续检测，直到成功
     */
    int mCheckNetworkIntervalTime = 5 * 60;

    boolean isOfflineAuth = false; //离线引擎是否授权成功

    List<String> mTetxs;
    Integer cout = 0;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        mTtsmode = (TtsMode)getIntent().getSerializableExtra("mode");

        this.getSupportActionBar().setTitle("长文本合成-当前模式:"+mTtsmode.toString());

        if (mTtsmode == TtsMode.MIX){ //MIX模式下调小超时阈值，以获得更好的体验
            mConnectTimeout = 1500;
            mReadTimeout = 5000;
        }

        setContentView(R.layout.activity_long_text_demo);

        tv_test_tts = (EditText) findViewById(R.id.et_test_tts);


        mTetxs = new ArrayList<>();

        //获得TTS合成器实例
        mTtsController = TtsController.getInstance();
        SecretConfig secretConfig = new SecretConfig();

        /***********************在线参数设置，如果仅用离线合成 不需要设置***************/
        mTtsController.setSecretId(secretConfig.online_secret_id);
        mTtsController.setSecretKey(secretConfig.online_secret_key);
//        ttsController.setToken(null); //STS临时证书鉴权时需要设置Token
        //设置ProjectId 不设置默认使用0，说明：项目功能用于按项目管理云资源，可以对云资源进行分项目管理，详情见 https://console.cloud.tencent.com/project
        mTtsController.setOnlineProjectId(0);

        mTtsController.setOnlineVoiceSpeed(mVoiceSpeed);//设置在线所合成音频的语速,语速，范围：[-2，2]，分别对应不同语速：-2代表0.6倍,-1代表0.8倍,0代表1.0倍（默认）,1代表1.2倍,2代表1.5倍,如果需要更细化的语速，可以保留小数点后一位，例如0.5 1.1 1.8等。
        mTtsController.setOnlineVoiceVolume(mVoiceVolume); //设置在线所合成音频的音量
        mTtsController.setOnlineVoiceType(mVoiceType);//设置在线所合成音频的音色id,完整的音色id列表见https://cloud.tencent.com/document/product/1073/37995
        mTtsController.setOnlineVoiceLanguage(mPrimaryLanguage);//主语言类型：1-中文（默认）2-英文

        mTtsController.setConnectTimeout(mConnectTimeout);
        mTtsController.setReadTimeout(mReadTimeout);
        mTtsController.setCheckNetworkIntervalTime(mCheckNetworkIntervalTime);
        // true: 服务器会返回Subtitles，false: 服务器不返回Subtitles，Subtitles为了精准计算播放器里的playProgress
        mTtsController.setOnlineParam("EnableSubtitle", true);

        /***********************离线线参数设置，如果仅用在线合成 不需要设置***************/
        if (SecretConfig.get().auth_way == 1) {
            boolean refreshAuth = false; //是否强制联网刷新授权(false:仅第一次联网激活下载授权文件; true:每次都联网刷新授权文件，无网络下将激活失败)
            mTtsController.setOfflineAuthParamDoOnline(
                    refreshAuth,
                    secretConfig.offline_online_secret_id,
                    secretConfig.offline_online_secret_key,
                    secretConfig.offline_online_lic_key,
                    secretConfig.offline_online_lic_pk);
        } else {
            mTtsController.setOfflineAuthParamDoOffline(
                secretConfig.offline_lic,
                secretConfig.offline_lic_sign,
                secretConfig.offline_lic_pk);
        }

        if (mTtsmode == TtsMode.OFFLINE || mTtsmode == TtsMode.MIX){//离线或者混合模式下，需要先配置离线合成所需要的资源
            String path = OfflineResourceManager.initOfflineResource(this);//初始化离线资源，demo示例从apk中解压出资源文件
            mTtsController.setOfflineResourceDir(path);
        }
        mTtsController.setOfflineVoiceSpeed(mOfflineSpeed);
        mTtsController.setOfflineVoiceVolume(mOfflineVolume);

        //离线音色名称，名称配置位于音色资源目录\voices\config.json 中，可自行指定更多的音色，demo中默认提供"pb"、"femalen"两种，如需其他音色请联系腾讯云商务
        if (mTtsmode == TtsMode.MIX){ //混合模式下查找一下在线音色对应的离线音色，离在线音色对照表位于OfflineVoicesMappingTable.java
            mOfflineVoiceType = OfflineVoicesMappingTable.getOfflineVoice(mVoiceType);
            if (mOfflineVoiceType == null){ //未找到匹配的离线音色
                if (!OfflineResourceManager.getVioceList().isEmpty()){
                    mOfflineVoiceType = OfflineResourceManager.getVioceList().get(0); //从json配置文件中读取第1个音色名作为当前音色,这里只是方便demo示例，您可以直接指定音色名，例如mTtsController.setOfflineVoiceType("pb");
                }
            }
            mTtsController.setOfflineVoiceType(mOfflineVoiceType);
        }else if(mTtsmode == TtsMode.OFFLINE) {
            if (!OfflineResourceManager.getVioceList().isEmpty()){
                mOfflineVoiceType = OfflineResourceManager.getVioceList().get(0); //从json配置文件中读取第1个音色名作为当前音色,这里只是方便demo示例，您可以直接指定音色名，例如mTtsController.setOfflineVoiceType("pb");
            }
            mTtsController.setOfflineVoiceType(mOfflineVoiceType);
        }


        mTtsController.init(this,mTtsmode , new TtsResultListener() {


            /**
             * @param offlineAuthInfo 返回离线sdk授权信息，包含错误码、到期时间、当前设备ID
             *  注意，如果使用离线模式，需要收到此回调后再调用合成接口，否则可能会因授权失败导致合成失败！！！
             */
            @Override
            public void onOfflineAuthInfo(QCloudOfflineAuthInfo offlineAuthInfo) {
                if(offlineAuthInfo.getError().getCode() == OFFLINE_AUTH_SUCCESS.getCode()){
                    isOfflineAuth = true;
                    AAILogger.d(TAG, "tts离线引擎授权成功" + "到期时间："+offlineAuthInfo.getExpireTime() + "deviceid："+offlineAuthInfo.getDeviceId() + "debug info:"+offlineAuthInfo.getResponse());
                } else {
                    AAILogger.d(TAG, "tts离线引擎授权失败,请校验授权信息后重新init:" + offlineAuthInfo.getError().getMessage() + " 到期时间："+offlineAuthInfo.getExpireTime() + "deviceid："+offlineAuthInfo.getDeviceId() + "debug info:"+offlineAuthInfo.getResponse());
                }

            }


            /**
             * 该方法已过期，建议使用其他签名方式的onSynthesizeData
             *
             * @param bytes       语音流
             * @param utteranceId 语句id
             * @param text        文本
             * @param engineType  引擎类型 0:在线 1:离线
             */
            @Override
            public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType) {
                AAILogger.d(TAG, "onSynthesizeData: " + bytes.length + ":" + utteranceId + ":" + text + ":" + engineType);
            }

            /**
             * @param bytes 语音数据
             * @param utteranceId 语句id
             * @param text 文本
             * @param engineType 引擎类型 0:在线 1:离线
             */
            @Override
            public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType, String requestId) {
                AAILogger.d(TAG, "onSynthesizeData: " + bytes.length + ":" + utteranceId + ":" + text + ":" + engineType + ":" + requestId);
            }

            @Override
            public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType, String requestId, String responseJson) {
                AAILogger.d(TAG, "onSynthesizeData: " + bytes.length + ":" + utteranceId + ":" + text + ":" + engineType + ":" + requestId);

                if (mediaPlayer == null){
                    return;
                }
                //将合成语音数据送入SDK内置播放器，如果sdk的内置播放器无法满足您的需求，您也可以使用自己实现的播放器替换
                //SDK内置播放器队列最大支持10个音频,如果队列已经满了
                // 如果需要使用Server端的Subtitles做播放进度的计算，需要将respJson一同enqueue，前提是设置mTtsController.setOnlineParam("EnableSubtitle", true);
                QPlayerError err = mediaPlayer.enqueue(bytes, text, utteranceId, responseJson);

                //将byteBuffer保存到文件
//                try {
//                    File file = File.createTempFile("temp", ".mp3");
//                    OutputStream os = new FileOutputStream(file);
//                    os.write(bytes);
//                    os.flush();
//                    os.close();
////                  QPlayerError err = mediaPlayer.enqueue(file, text, utteranceId);     //播放器也支持文件入参
//                } catch (IOException e) {
//                    return;
//                }

                if (err != null){
                    AAILogger.d(TAG, "mediaPlayer enqueue error" + err.getmMessage());
                }
            }

            /**
             * @param error 错误信息
             * @param text 文本(如果有则返回)
             * @param utteranceId 语句id(如果有则返回)
             */
            @Override
            public void onError(TtsError error, String utteranceId, String text) {
                AAILogger.d(TAG, "onError: " + error.getCode() + ":" + error.getMessage() + ":" + utteranceId);

                if (error.getThrowable() != null) {
                    AAILogger.d(TAG, "Throwable err: " + error.getThrowable().toString());

                }

                if (error.getServiceError() != null) { //返回在线合成的后端错误码

                    if (mTtsmode == TtsMode.MIX){
                        //实际业务上判断一下，如果是混合模式下返回在线合成的后端错误码，应当忽略可不做处理
                        //SDK内会继续调用离线合成继续工作,如果没有日志需求，这里直接return忽略即可
                        //return;
                    }

                    AAILogger.d(TAG, "Server response error: " + error.getServiceError().getCode() + ":" + error.getServiceError().getMessage() + ":" + utteranceId);

                    runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(SplitLongTextDemoActivity.this, "error:" + error.getServiceError().getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    });

                } else {
                    runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(SplitLongTextDemoActivity.this, "error:" + error.getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    });
                }
            }

            @Override
            public void onChunk(ByteBuffer chunk) {

            }
        });


        //初始化SDK内置播放器，如果sdk的内置播放器无法满足您的需求，您也可以使用自己实现的播放器替换
//        mediaPlayer = new MediaPlayerDemo(new QCloudPlayerCallback() { //使用demo中提供的播放器，您可以修改播放器逻辑，源代码位于MediaPlayerDemo.java，与SDK内置播放器一致
        mediaPlayer = new QCloudMediaPlayer(new QCloudPlayerCallback() { //使用SDK中提供的播放器

            @Override
            public void onTTSPlayStart() {
                AAILogger.d(TAG, "开始播放");
            }

            @Override
            public void onTTSPlayWait() {
                AAILogger.d(TAG, "播放完成，等待音频数据");
            }

            @Override
            public void onTTSPlayResume() {
                AAILogger.d(TAG, "恢复播放");
            }

            @Override
            public void onTTSPlayPause() {
                AAILogger.d(TAG, "暂停播放");
            }

            @Override
            public void onTTSPlayNext(String text, String utteranceId) {
                AAILogger.d(TAG, "开始播放: " + utteranceId + "|" + text);
                if(mediaPlayer.getAudioAvailableQueueSize() > 0){
                    if (mTetxs.size() > 0) {
                        //预合成队列，可以持续添加文本，最大限制20000句
                        TtsError error = mTtsController.synthesize(mTetxs.get(0),cout.toString());
                        if(error == null){
                            cout++;
                            mTetxs.remove(0);
                        }
                    }
                }

            }

            @Override
            public void onTTSPlayStop() {
                AAILogger.d(TAG, "播放停止，内部队列已清空");
            }

            @Override
            public void onTTSPlayError(QPlayerError error) {
                AAILogger.d(TAG, "播放器发生异常");
            }

            /**
             * @param currentWord 当前播放的字符
             * @param currentIndex 当前播放的字符在所在的句子中的下标.
             */
            @Override
            public void onTTSPlayProgress(String currentWord, int currentIndex) {
                AAILogger.d(TAG, "onTTSPlayProgress: " + currentWord + "|" + currentIndex);
            }
        });

        //start按钮
        findViewById(R.id.btn_start).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                mTetxs.clear();
                mTtsController.cancel();
                mediaPlayer.StopPlay();

                String ttsText = tv_test_tts.getText().toString();

                if (TextUtils.isEmpty(ttsText)) {
                    ttsText = "2013年11月习近平在山东农科院召开座谈会时表示，手中有粮心中不慌。保障粮食安全对中国来说是永恒的课题，任何时候都不能放松。2013年7月，在湖北鄂州东港村育种基地，习近平总书记拔起一棵稻苗察看分蘖情况，夸奖“很壮实”，强调粮食安全要靠自己。高屋建瓴，他的论述为保障粮食安全指明方向。接着展现出的是一幅一幅瑰丽变幻的奇景：天姥山隐于云霓明灭之中，引起了诗人探求的想望。诗人进入了梦幻之中，仿佛在月夜清光的照射下，他飞渡过明镜一样的镜湖。明月把他的影" +
                            "子映照在镜湖之上，又送他降落在谢灵运当年曾经歇宿过的地方。他穿上谢灵运当年特制的木屐，登上谢公当年曾经攀登过的石径──青云梯。只见：“半壁见海日，空中闻天鸡。千岩万转路不定，迷花倚石忽已暝。熊咆龙吟殷岩泉，栗深林兮惊层巅。云青青兮欲雨，水澹澹兮生烟。”继飞渡而写山中所见，石径盘旋，深山中光线幽暗，看到海日升空，天鸡高唱，这本是一片曙色；却又于山花迷人、倚石暂憩之中，忽觉暮色降临，旦暮之变何其倏忽。暮色中熊咆龙吟，震响于山谷之间，深林为之战栗，" +
                            "层巅为之惊动。不止有生命的熊与龙以吟、咆表示情感，就连层巅、深林也能战栗、惊动，烟、水、青云都满含阴郁，与诗人的情感，协成一体，形成统一的氛围。前面是浪漫主义地描写天姥山，既高且奇；这里又是浪漫主义地抒情，既深且远。这奇异的境界，已经使人够惊骇的了，但诗人并未到此止步，而诗境却由奇异而转入荒唐，全诗也更进入高潮。北方的风光，千万里冰封冻，千万里雪花飘。远望长城内外，只剩下无边无际白茫茫一片；宽广的黄河上下，顿时失去了滔滔水势。山岭好像银" +
                            "白色的蟒蛇在飞舞，高原上的丘陵好像许多白象在奔跑，它们都想试一试与老天爷比比高。要等到晴天的时候，看红艳艳的阳光和白皑皑的冰雪交相辉映，分外美好。江山如此媚娇，引得无数英雄竞相倾倒。只可惜秦始皇、汉武帝，略差文学才华；唐太宗、宋太祖，稍逊文治功劳。称雄一世的人物，成吉思汗，只知道拉弓射大雕。这些人物全都过去了，数一数能建功立业的英雄人物，还要看今天的人们,播放结束";
                    tv_test_tts.setText(ttsText);
                }
                if (mTtsController == null) {
                    return;
                }


                mTetxs.addAll(split(ttsText)) ;//切分文本示例, 如果入参文本比较长，建议放在子线程操作，避免ANR

                if (!isOfflineAuth && mTtsmode != TtsMode.ONLINE){
                    AAILogger.d(TAG, "离线sdk授权未完成，请稍后重试");
                    return;
                }


                //预合成数量不应超过SDK内播放器可用队列数量，如果sdk内播放器不满足您的需求，您也可以自行实现播放器部分
                for (int i = 0; i < mediaPlayer.getAudioAvailableQueueSize() - 1  ;i++){
                    if (mTetxs.size() > 0) {
                        //预合成队列，可以持续添加文本，最大限制20000句
                        TtsError error = mTtsController.synthesize(mTetxs.get(0),cout.toString());
                        if(error == null){
                            cout++;
                            mTetxs.remove(0);
                        }else {
                            return;
                        }
                    }
                }
            }
        });

        //stop按钮
        findViewById(R.id.btn_stop).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mTetxs.clear();
                if (mTtsController != null) {
                    mTtsController.cancel();
                }
                if (mediaPlayer != null){
                    mediaPlayer.StopPlay();
                }
            }
        });

        //pause按钮
        findViewById(R.id.btn_pause).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (mediaPlayer != null) {
                    mediaPlayer.PausePlay();
                }
            }
        });

        //resume按钮
        findViewById(R.id.btn_resume).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (mediaPlayer != null) {
                    mediaPlayer.ResumePlay();
                }
            }
        });

        //设置按钮
        findViewById(R.id.btn_setting).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                SettingDialogConfig config = new SettingDialogConfig();
                config.connectTimeout = mConnectTimeout;
                config.readTimeout = mReadTimeout;
                config.CheckNetworkIntervalTime = mCheckNetworkIntervalTime;
                config.voiceType = mVoiceType;
                config.speed = mVoiceSpeed;
                config.volume = mVoiceVolume;
                config.primaryLanguage = mPrimaryLanguage;
                config.offlineVoiceType = mOfflineVoiceType;
                config.offlineVolume = mOfflineVolume;
                config.offlineSpeed = mOfflineSpeed;
                config.ttsmode = mTtsmode;

                new SettingDialog(SplitLongTextDemoActivity.this,config,
                        new SettingDialog.OnSettingDialogListener() {
                            @Override
                            public void onListener(SettingDialogConfig config) {

                                mConnectTimeout = config.connectTimeout;
                                mReadTimeout = config.readTimeout;
                                mCheckNetworkIntervalTime = config.CheckNetworkIntervalTime;
                                mVoiceType = config.voiceType;
                                mVoiceSpeed = config.speed;
                                mVoiceVolume = config.volume;
                                mPrimaryLanguage = config.primaryLanguage;

                                mOfflineVoiceType = config.offlineVoiceType;
                                mOfflineVolume = config.offlineVolume;
                                mOfflineSpeed = config.offlineSpeed;

                                mTtsController.setConnectTimeout(mConnectTimeout);
                                mTtsController.setReadTimeout(mReadTimeout);
                                mTtsController.setCheckNetworkIntervalTime(mCheckNetworkIntervalTime);
                                mTtsController.setOnlineVoiceType(mVoiceType);
                                mTtsController.setOnlineVoiceSpeed(mVoiceSpeed);
                                mTtsController.setOnlineVoiceVolume(mVoiceVolume);
                                mTtsController.setOnlineVoiceLanguage(mPrimaryLanguage);

                                //离线
                                mTtsController.setOfflineVoiceSpeed(mOfflineSpeed);
                                mTtsController.setOfflineVoiceVolume(mOfflineVolume);
                                mTtsController.setOfflineVoiceType(mOfflineVoiceType);
                            }
                        }).show();
            }
        });

        requestAudioFocus();
    }


    private void requestAudioFocus() {
        //初始化audio mananger
        listener = new AudioManager.OnAudioFocusChangeListener() {
            @Override
            public void onAudioFocusChange(int focusChange) {
                if (focusChange == AudioManager.AUDIOFOCUS_LOSS) {
                    //丢失焦点，直接
                    mediaPlayer.StopPlay();
                } else if (focusChange == AudioManager.AUDIOFOCUS_LOSS_TRANSIENT) {
                    //丢失焦点，但是马上又能恢复
                } else if (focusChange == AudioManager.AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK) {
                    //降低音量
                } else if (focusChange == AudioManager.AUDIOFOCUS_GAIN) {
                    //获得了音频焦点
                }
            }
        };

        //设置listener
        AudioManager am = (AudioManager) getApplicationContext().getSystemService(Context.AUDIO_SERVICE);
        if (am != null) {
            am.requestAudioFocus(listener, AudioManager.STREAM_MUSIC, AudioManager.AUDIOFOCUS_GAIN);
        }
    }

    private void abandonAudioFocus() {
        AudioManager am = (AudioManager) getApplicationContext().getSystemService(Context.AUDIO_SERVICE);
        if (am != null) {
            am.abandonAudioFocus(listener);
        }
    }

    @Override
    protected void onDestroy() {

        super.onDestroy();

        if (mediaPlayer != null){
            mediaPlayer.StopPlay();
            mediaPlayer = null;
        }
        if (mTtsController != null) {
            TtsController.release();
            mTtsController = null;
        }
        isOfflineAuth = false;
        AAILogger.d(TAG, "onDestroy: ");

        abandonAudioFocus();

    }


    @Override
    protected void onPause() {
        super.onPause();

    }

    @Override
    public void finish() {
        super.finish();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

    }

    /********************************************以下示例将语句分割*************************************/
//分割成语句
    private List<String> split(String text) {
        String text1 = filterEmoji(text, " ");
        List<String> lines = new ArrayList<>();
        String[] sArr = separatedText(text1, "[:：。！？!?]").toArray(new String[]{});
        for (int i = 0; i < sArr.length; ++i) {
            //检查语句是否过长
            String s = sArr[i];
            if (s.getBytes().length > 150) {
                //按照逗号和分号分割
                String[] s2Arr = separatedText(s, "[，；,;]").toArray(new String[]{});
                for (int j = 0; j < s2Arr.length; j++) {
                    for (int k = 0; k < (int) (Math.ceil(s2Arr[j].length() / 80f)); ++k) {
                        String str = s2Arr[j].substring(k * 80, Math.min(s2Arr[j].length(), (k + 1) * 80));
                        if (!isEmpty(str) && !isPunct(str)) {
                            lines.add(str);
                        }
                    }
                }
            } else {
                if (!isEmpty(s) && !isPunct(s)) {
                    lines.add(s);
                }
            }
        }
        return lines;
    }

    private boolean isPunct(String str) { //检测是否全为标点

        Pattern pattern4 = Pattern.compile("\\p{Punct}+");
        Matcher matcher4 = pattern4.matcher(str);
        if (matcher4.matches()) {
            return true;
        }
        return false;
    }

    private boolean isEmpty(String... strings) {
        for (String str : strings) {
            if (str == null || str.trim().length() == 0)
                return true;
        }
        return false;
    }

    private List<String> separatedText(String text, String split) {
        List<String> lines = new ArrayList<>();
        int loc = 0;
        for (int i = 0; i < text.length(); i++) {
            String iText = text.substring(i, i + 1);
            if (split.contains(iText)) {
                String subString = text.substring(loc, i + 1);
                Pattern p = Pattern.compile("[\u4e00-\u9fa5]|[A-Z]|[a-z]|[0-9]");
                Matcher m = p.matcher(subString);
                if (m.find()) {
                    lines.add(subString);
                    loc = i + 1;
                }
            }
            if (i + 1 == text.length() && split.contains(iText) == false) {//判断最后一个字符是否包含分隔符,如果不包含把最后一句添加到数组
                String subString = text.substring(loc, i + 1);
                Pattern p = Pattern.compile("[\u4e00-\u9fa5]|[A-Z]|[a-z]|[0-9]");
                Matcher m = p.matcher(subString);
                if (!m.find()) {//无效的文本的处理
                    if (lines.size() != 0) {//取前一个有效的文本，进行拼接
                        String lastString = lines.get(lines.size() - 1);
                        lastString = lastString + subString;
                        lines.set(lines.size() - 1, lastString);
                    }
                } else {
                    lines.add(subString);
                }
            }
        }
        return lines;
    }


    /**
     * emoji表情替换
     *
     * @param source  原字符串
     * @param slipStr emoji表情替换成的字符串
     * @return 过滤后的字符串
     */
    private String filterEmoji(String source, String slipStr) {
        if (!TextUtils.isEmpty(source)) {
            return source.replaceAll("[\\ud800\\udc00-\\udbff\\udfff\\ud800-\\udfff]", slipStr);
        } else {
            return source;
        }
    }

}