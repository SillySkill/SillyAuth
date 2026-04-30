package com.tencent.cloud.sdktts;

import android.content.res.AssetManager;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.os.Bundle;
import android.util.JsonReader;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.tencent.cloud.libqcloudtts.TtsController;
import com.tencent.cloud.libqcloudtts.TtsError;
import com.tencent.cloud.libqcloudtts.TtsMode;
import com.tencent.cloud.libqcloudtts.TtsResultListener;
import com.tencent.cloud.libqcloudtts.engine.offlineModule.auth.QCloudOfflineAuthInfo;
import com.tencent.cloud.libqcloudtts.utils.AAILogger;
import com.tencent.cloud.sdktts.ui.FormInput;
import com.tencent.cloud.sdktts.ui.FormSelect;
import com.tencent.cloud.sdktts.ui.FormSlider;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.Executors;

@ShareKey(key = "TTSOfflineStreamActivity")
public class TTSOfflineStreamActivity extends AppCompatActivity implements TtsResultListener {
    private static final String TAG = TTSOfflineStreamActivity.class.getSimpleName();
    private TtsController controller;
    private TextView text_result;
    private Button btn_synthesize;
    private Button btn_stop;
    private AudioTrack audio_track;
    private FormInput text_input;
    private FormSelect voice_select;
    private FormSlider volume_slider;
    private FormSlider speed_slider;
    private boolean running;
    @ShareKey(key = "text")
    public String text = "语音合成可以将文本转换为语音,实现让机器开口说话";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ttsoffline_stream);
        ShareUtils.unmarshal(this, this);
        text_result = findViewById(R.id.text_result);
        btn_synthesize = findViewById(R.id.btn_synthesize);
        btn_synthesize.setEnabled(false);
        btn_synthesize.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                TTSOfflineStreamActivity.this.on_synthesize();
            }
        });
        btn_stop = findViewById(R.id.btn_stop_stream);
        btn_stop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(audio_track.getPlayState() != AudioTrack.PLAYSTATE_STOPPED) {
                    audio_track.stop();
                }
            }
        });
        voice_select = findViewById(R.id.select_voice);
        voice_select.setTitle("音色");
        List<FormSelect.Options> list = new ArrayList<>();
        try {
            String line = "";
            BufferedReader br = new BufferedReader(new InputStreamReader(getAssets().open("voices/config.json")));
            StringBuilder sb = new StringBuilder();
            while((line = br.readLine()) != null) {
                sb.append(line);
            }
            JSONObject config = new JSONObject(sb.toString());
            for (Iterator<String> it = config.keys(); it.hasNext(); ) {
                String key = it.next();
                list.add(new FormSelect.Options(0, key));
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }
        voice_select.setOptions(list.toArray(new FormSelect.Options[0]));
        volume_slider = findViewById(R.id.slider_volume);
        volume_slider.setTitle("音量");
        volume_slider.setSlider(0, 10, 0.1f);
        volume_slider.setValue(1.0f);
        speed_slider = findViewById(R.id.slider_speed);
        speed_slider.setTitle("音速");
        speed_slider.setSlider(0.5f, 2, 0.1f);
        speed_slider.setValue(1.0f);
        text_input = findViewById(R.id.input_text);
        text_input.setTitle("文本");
        text_input.setValue(text);
        controller = TtsController.getInstance();
        this.running = false;
        this.init_auth();
    }


    @Override
    public void onStart() {
        super.onStart();
        this.audio_track = new AudioTrack(AudioManager.STREAM_MUSIC, 16000, AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT, AudioTrack.getMinBufferSize(16000, AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT), AudioTrack.MODE_STREAM);
    }

    @Override
    public void onStop() {
        super.onStop();
        audio_track.stop();
        audio_track = null;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        TtsController.release();
    }


    private void init_auth() {
        SecretConfig secretConfig = SecretConfig.get();
        /***********************离线线参数设置***************/
        if (SecretConfig.get().auth_way == 1) {
            boolean refreshAuth = false; //是否强制联网刷新授权(false:仅第一次联网激活下载授权文件; true:每次都联网刷新授权文件，无网络下将激活失败)
            controller.setOfflineAuthParamDoOnline(
                    refreshAuth,
                    secretConfig.offline_online_secret_id,
                    secretConfig.offline_online_secret_key,
                    secretConfig.offline_online_lic_key,
                    secretConfig.offline_online_lic_pk);
        } else {
            controller.setOfflineAuthParamDoOffline(
                    secretConfig.offline_lic,
                    secretConfig.offline_lic_sign,
                    secretConfig.offline_lic_pk);
        }
        String path = OfflineResourceManager.initOfflineResource(this); //初始化离线资源，demo示例从apk中解压出资源文件
        controller.setOfflineResourceDir(path); //配置资源文件夹目录
        controller.init(this.getApplicationContext(), TtsMode.OFFLINE, this);
    }

    private void on_synthesize() {
        if(running) {
            controller.cancel();
            running = false;
            btn_synthesize.setText("合成");
        }else {
            running = true;
            if (audio_track.getPlayState() != AudioTrack.PLAYSTATE_PLAYING) {
                audio_track.play();
            }
            this.text = this.text_input.getValue();
            ShareUtils.marshal(this, this);
            controller.setOfflineVoiceType(this.voice_select.getSelectOptions().toString());
            controller.setOfflineVoiceVolume(this.volume_slider.getValue());
            controller.setOfflineVoiceSpeed(this.speed_slider.getValue());
            controller.synthesize(this.text);
            btn_synthesize.setText("取消");
        }
    }

    @Override
    public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType) {

    }

    @Override
    public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType, String requestId) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    File file = null;
                    file = new File(getExternalFilesDir("").getAbsolutePath()+"/temp.wav");
                    OutputStream os = new FileOutputStream(file);
                        os.write(bytes);
                    os.flush();
                    os.close();
                    TTSOfflineStreamActivity.this.text_result.setText(String.format("合成完毕,音频路径为 %s", file.getAbsolutePath()));
                    running = false;
                    btn_synthesize.setText("合成");
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }
        });
    }

    @Override
    public void onSynthesizeData(byte[] bytes, String utteranceId, String text, int engineType, String requestId, String respJson) {

    }

    @Override
    public void onError(TtsError error, String utteranceId, String text) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                String result = String.format("Code: %d\nMessage: %s\n", error.getCode(), error.getMessage());
                if (error.getServiceError() != null) {
                    result += String.format("Server Response: %s", error.getServiceError().getResponse());
                }
                running = false;
                btn_synthesize.setText("合成");
                text_result.setText(result);
            }
        });
    }

    @Override
    public void onOfflineAuthInfo(QCloudOfflineAuthInfo offlineAuthInfo) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                btn_synthesize.setEnabled(true);
                String result = String.format("授权到期时间: %s\n授权音色: %s\n", offlineAuthInfo.getExpireTime(), offlineAuthInfo.getVoiceAuthList());
                text_result.setText(result);
            }
        });
    }

    @Override
    public void onChunk(ByteBuffer chunk) {
        try {
            byte[] data = chunk.array();
            audio_track.write(data, 0, data.length);
        }catch (Exception e) {
            AAILogger.e(TAG, Log.getStackTraceString(e));
        }
    }
}