package com.tencent.cloud.sdktts;

import static com.tencent.cloud.libqcloudtts.engine.offlineModule.auth.AuthErrorCode.OFFLINE_AUTH_SUCCESS;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.text.TextUtils;
import android.util.JsonReader;
import android.view.View;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;
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

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.ByteBuffer;


/**
 * 合成语音的源文本：中文最大支持150个汉字(全角标点符号算一个汉字)、英文最大支持500个字母(半角标点符号算一个字母)
 *
 * 短文本: 少于150个汉字或者英文超过500个字母
 *
 * 该类主要介绍如何对短文本进行语音合成
 * 具体做法：调用基础语音合成接口直接合成(详情见: https://cloud.tencent.com/document/product/1073/37995)
 */
public class TtsDemoActivity extends AppCompatActivity {
    private static final String TAG = TtsDemoActivity.class.getSimpleName();
    private volatile TtsController mTtsController;
    private EditText tv_test_tts;

    private TextView mMsgText;
    private ScrollView mMsgScrollView;

    private QCloudMediaPlayer mediaPlayer; //使用SDK内置播放器
//    private MediaPlayerDemo mediaPlayer;//使用demo中提供的播放器，您可以修改播放器逻辑，源代码位于MediaPlayerDemo.java，与SDK内置播放器一致

    TtsMode mTtsmode = TtsMode.ONLINE;

    //离线参数
    String mOfflineVoiceType = "";//音色名，名称配置位于音色资源目录\voices\config.json 中
    float mOfflineVolume = 1.0f;//离线音量 > 0
    float mOfflineSpeed = 1.0f;//离线语速[0.5,2.0]
    //在线参数
    float mVoiceSpeed = 0f;
    float mVoiceVolume = 0f;
    int mVoiceType = 1001;
    int mPrimaryLanguage = 1; //主语言类型：1-中文（默认）2-英文
    //时间配置
    int mConnectTimeout = 15 *1000; //连接超时默认15000ms(15s) 范围[500,30000] 单位ms ， Mix模式下建议调小此值，以获得更好的体验
    int mReadTimeout = 30 *1000; //读取超时超时默认30000ms(30s) 范围[2200,60000] 单位ms， Mix模式下建议调小此值，以获得更好的体验
    /**
     * mCheckNetworkIntervalTime
     * Mix模式下，已经连接网络，但出现网络错误或者后台错误后的检测间隔时间，用于从离线模式自动切换回在线模式，默认值5分钟
     * 注意：每次检测时将使用所入参的一句文本请求服务器，如果后端合成成功将会额外消耗该句字数的合成额度
     * 大于等于0 单位s, 等于0时持续检测，直到成功
     */
    int mCheckNetworkIntervalTime = 5 * 60;


    boolean isPlay = true;

    boolean isOfflineAuth = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tts_demo);
        tv_test_tts = (EditText) findViewById(R.id.et_test_tts);
        tv_test_tts.setText("腾讯云语音合成技术可以将任意文本转化为语音，实现让机器和应用张口说话。");
        mMsgText = findViewById(R.id.showText);
        mMsgScrollView = findViewById(R.id.scroll_view);

        mTtsmode = (TtsMode)getIntent().getSerializableExtra("mode");

        this.getSupportActionBar().setTitle("腾讯云语音合成-当前模式:"+mTtsmode.toString());

        if (mTtsmode == TtsMode.MIX){ //MIX模式下调小超时阈值，以获得更好的体验
            mConnectTimeout = 1500;
            mReadTimeout = 5000;
        }

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
//        mTtsController.setOnlineRegion("ap-singapore");
        // mTtsController.setOnlineEnableSubtitle(true);
        /***********************以上为 在线参数设置 ，如果仅用离线合成 不需要设置***************/


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
            String path = OfflineResourceManager.initOfflineResource(this); //初始化离线资源，demo示例从apk中解压出资源文件
            mTtsController.setOfflineResourceDir(path); //配置资源文件夹目录
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

        /***********************以上为 离线线参数设置，如果仅用在线合成 不需要设置***************/

        mTtsController.init(this,mTtsmode , new TtsResultListener() {


            /**
             * @param offlineAuthInfo 返回离线sdk授权信息，包含错误码、到期时间、当前设备ID
             *  注意，如果使用离线模式，需要收到此回调后再调用合成接口，否则可能会因授权失败导致合成失败！！！
             */
            @Override
            public void onOfflineAuthInfo(QCloudOfflineAuthInfo offlineAuthInfo) {
                String s = offlineAuthInfo.toString();
                if(offlineAuthInfo.getError().getCode() == OFFLINE_AUTH_SUCCESS.getCode()){
                    isOfflineAuth = true;
                    AAILogger.d(TAG, "tts离线引擎授权成功" + " 到期时间："+offlineAuthInfo.getExpireTime() + " deviceid："+offlineAuthInfo.getDeviceId() + " debug info:"+offlineAuthInfo.getResponse() + " auth voice list:"+offlineAuthInfo.getVoiceAuthList());
                    ShowMsg("tts离线引擎授权成功" + "\n到期时间："+offlineAuthInfo.getExpireTime() + "\ndeviceid："+offlineAuthInfo.getDeviceId() + "\ndebug info:"+offlineAuthInfo.getResponse()+ "\nauth voice list:"+offlineAuthInfo.getVoiceAuthList());
                } else {
                    AAILogger.d(TAG, "tts离线引擎授权失败:" + offlineAuthInfo.getError().getMessage() + " 到期时间："+offlineAuthInfo.getExpireTime() + " deviceid："+offlineAuthInfo.getDeviceId() + " debug info:"+offlineAuthInfo.getResponse()+ " auth voice list:"+offlineAuthInfo.getVoiceAuthList());
                    ShowMsg("tts离线引擎授权失败:" + offlineAuthInfo.getError().getMessage() + " \n到期时间："+offlineAuthInfo.getExpireTime() + "\ndeviceid："+offlineAuthInfo.getDeviceId() + "\ndebug info:"+offlineAuthInfo.getResponse()+ "\nauth voice list:"+offlineAuthInfo.getVoiceAuthList());
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
             * @param bytes       语音流
             * @param utteranceId 语句id
             * @param text        文本
             * @param engineType  引擎类型 0:在线 1:离线
             * @param requestId   请求ID，仅engineType为0时不为null，用于排查问题
             */
            @Override
            public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType, String requestId) {

            }

            /**
             * @param bytes 语音数据
             * @param utteranceId 语句id
             * @param text 文本
             * @param engineType 引擎类型 0:在线 1:离线
             */
            @Override
            public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType, String requestId, String respJson) {
                AAILogger.d(TAG, "onSynthesizeData: " + bytes.length + ":" + utteranceId + ":" + text + ":" + engineType);
                ShowMsg("success:"+"data length=" + bytes.length + "   text = "+ text + "    requestId = " + requestId);
                if (respJson != null) {
                    try {
                        JSONObject object = new JSONObject(respJson);
                        AAILogger.d(TAG, "Subtitles: " + object.getJSONObject("Response").getJSONObject("Subtitles").toString());
                    }catch (Exception e){
                        ShowMsg(e.getMessage());
                    }
                }

                if (isPlay) {
                    if (mediaPlayer == null)return;
                    //将合成语音数据送入SDK内置播放器，如果sdk的内置播放器无法满足您的需求，您也可以使用自己实现的播放器替换
                    // 如果需要使用Server端的Subtitles做播放进度的计算，需要将respJson一同enqueue，前提是设置mTtsController.setOnlineParam("EnableSubtitle", true);
                    QPlayerError err = mediaPlayer.enqueue(bytes, text, utteranceId, respJson);
                    if (err != null){
                        AAILogger.d(TAG, "mediaPlayer enqueue error" + err.getmMessage());
                        ShowMsg("mediaPlayer enqueue error" + err.getmMessage());
                    }
                } else {
                    //将byteBuffer保存到文件
                    try {
                        File file = null;
                        if (engineType == 1){
                            file = File.createTempFile("temp", ".wav");
                        } else {
                            file = File.createTempFile("temp", ".mp3");
                        }

                        OutputStream os = new FileOutputStream(file);
                        os.write(bytes);
                        os.flush();
                        os.close();
                        //QPlayerError err = mediaPlayer.enqueue(file, text, utteranceId);     //播放器也支持文件入参
                        AAILogger.d(TAG, "file: "+file.toString());
                        ShowMsg("合成成功,保存音频文件路径为：" + file.toString());

                    } catch (IOException e) {
                        ShowMsg("合成成功,保存音频文件失败：" + e.toString());
                        return;
                    }
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


                if (error.getServiceError() != null) { //后端返回的错误，错误码见 https://cloud.tencent.com/document/product/1073/37995

                    if (mTtsmode == TtsMode.MIX){
                        //实际业务上判断一下，如果是混合模式下返回在线合成的后端错误码，应当忽略可不做处理
                        //SDK内会继续调用离线合成继续工作,如果没有日志需求，这里直接return忽略即可
                        //return;
                    }

                    AAILogger.d(TAG, "Server response error: " + error.getServiceError().getCode() + ":" + error.getServiceError().getMessage() + ":" + utteranceId);

                    ShowMsg("Server response error：" + error.getServiceError().getCode() + ":" + error.getServiceError().getMessage());
                    if (error.getServiceError().getResponse() != null){
                        ShowMsg("Server response :" + error.getServiceError().getResponse());
                    }

                    runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(TtsDemoActivity.this, "error:" + error.getServiceError().getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    });
                } else {
                    ShowMsg("合成失败：" + error.getCode() + ":" + error.getMessage());
                    runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(TtsDemoActivity.this, "error:" + error.getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    });
                }

                if (error.getThrowable() != null) {
                    AAILogger.d(TAG, "Throwable err: " + error.getThrowable().toString());
                    ShowMsg("Throwable err：" + error.getThrowable().toString());

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
                ShowMsg("开始播放");
            }

            @Override
            public void onTTSPlayWait() {
                AAILogger.d(TAG, "播放完成，等待音频数据");
                ShowMsg("播放完成，等待音频数据");
            }

            @Override
            public void onTTSPlayResume() {
                AAILogger.d(TAG, "恢复播放");
                ShowMsg("恢复播放");
            }

            @Override
            public void onTTSPlayPause() {
                AAILogger.d(TAG, "暂停播放");
                ShowMsg("暂停播放");
            }

            @Override
            public void onTTSPlayNext(String text, String utteranceId) {
                AAILogger.d(TAG, "开始播放: " + utteranceId + "|" + text);
                ShowMsg("即将播放:"+utteranceId + ":" + text);
            }

            @Override
            public void onTTSPlayStop() {
                AAILogger.d(TAG, "播放停止，内部队列已清空");
                ShowMsg("播放停止或手动取消");
            }

            @Override
            public void onTTSPlayError(QPlayerError error) {
                AAILogger.d(TAG, "播放器发生异常:"+error.getmCode() + ":" + error.getmMessage());
                ShowMsg("播放器发生异常:"+error.getmCode() + ":" + error.getmMessage());
            }

            /**
             * @param currentWord 当前播放的字符
             * @param currentIndex 当前播放的字符在所在的句子中的下标.
             */
            @Override
            public void onTTSPlayProgress(String currentWord, int currentIndex) {
                AAILogger.d(TAG, "onTTSPlayProgress: " + currentWord + "|" + currentIndex);
                ShowMsg("onTTSPlayProgress:" + "|" + currentWord + "|" + currentIndex );
            }
        });

        //合成并播放按钮
        findViewById(R.id.btn_speech).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                if (!isOfflineAuth && mTtsmode != TtsMode.ONLINE){
                    ShowMsg("离线sdk授权未完成，请在收到onOfflineAuthInfo回调后重试");
                    return;
                }

                String ttsText = tv_test_tts.getText().toString();
//                tv_test_tts.setText("");

                if (TextUtils.isEmpty(ttsText) || mTtsController == null) {
                    ShowMsg("请输入文本后再合成");
                    return;
                }
//                CleanMsg();
                isPlay = true;
                //预合成队列，可以持续添加文本，最大限制20000句
                TtsError error = mTtsController.synthesize(ttsText);
//                TtsError error = mTtsController.synthesize(ttsText,"第一句");
                if (error != null){
                    ShowMsg("合成发生错误:"+error.getMessage());
                }
            }
        });

        //合成不播放按钮
        findViewById(R.id.btn_synthesis).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                if (!isOfflineAuth && mTtsmode != TtsMode.ONLINE){
                    ShowMsg("离线sdk授权未完成，请稍后重试");
                    return;
                }

                String ttsText = tv_test_tts.getText().toString();
//                tv_test_tts.setText("");
                if (TextUtils.isEmpty(ttsText) || mTtsController == null) {
                    ShowMsg("请输入文本后再合成");
                    return;
                }
//                CleanMsg();
                isPlay = false;
                //预合成队列，可以持续添加文本，最大限制20000句
                TtsError error = mTtsController.synthesize(ttsText);
//                TtsError error = mTtsController.synthesize(ttsText,"第一句");
                if (error != null){
                    ShowMsg("合成发生错误:"+error.getMessage());
                }
            }
        });

        //取消合成按钮
        findViewById(R.id.btn_cancel).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (mTtsController != null) {
                    mTtsController.cancel();
                }
            }
        });

        //取消播放按钮
        findViewById(R.id.btn_cancel_play).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (mediaPlayer != null) {
                    mediaPlayer.StopPlay();
                }
            }
        });


        //暂停播放按钮
        findViewById(R.id.btn_pause_play).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (mediaPlayer != null) {
                    mediaPlayer.PausePlay();
                }
            }
        });

        //恢复播放按钮
        findViewById(R.id.btn_resume_play).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (mediaPlayer != null) {
                    mediaPlayer.ResumePlay();
                }
            }
        });

        //设置弹窗
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

                new SettingDialog(TtsDemoActivity.this,config,
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

    }



    //日志信息框
    private void ShowMsg(String message) {
        AAILogger.i(TAG, message);
        new Thread() {
            public void run() {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        mMsgText.append(message + "\n");
                        mMsgScrollView.fullScroll(ScrollView.FOCUS_DOWN);
                    }
                });
            }
        }.start();
    }
    private void CleanMsg() {
        mMsgText.setText("");
    }







}