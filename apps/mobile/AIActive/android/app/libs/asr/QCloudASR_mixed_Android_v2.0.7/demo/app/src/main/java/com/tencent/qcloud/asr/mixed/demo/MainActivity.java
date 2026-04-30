package com.tencent.qcloud.asr.mixed.demo;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Context;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.tencent.qcloud.asr.mixed.ASRController;
import com.tencent.qcloud.asr.mixed.demo.databinding.ActivityMainBinding;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.time.Duration;
import java.time.Instant;

public class MainActivity extends AppCompatActivity {

    private ActivityMainBinding binding;
    private HandlerThread thread;
    private ASRController controller;
    private boolean is_running;
    private Listener listener;
    private DataSource data_source;
    private RecordDataSource data_source1;
    private FileDataSource data_source2;
    private String text = "";

    private Handler handler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        View view = binding.getRoot();
        setContentView(view);
        binding.ctrBtn.setEnabled(false);
        controller = ASRController.GlobalInstance();
        thread = new HandlerThread("io");
        thread.start();
        Looper lopper = thread.getLooper();
        listener = new Listener();
        listener.activity = this;
        binding.modeSel.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, new String[]{"混合", "在线", "离线"}));
        binding.modeSel.setSelection(0);
        binding.sourceSel.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, new String[]{"录音", "文件"}));
        binding.sourceSel.setSelection(0);
        data_source1 = new RecordDataSource(this);
        if(!new File(getExternalCacheDir().getAbsolutePath() + "/output.pcm").exists()) {
            copyAssetFile("output.pcm");
        }
        data_source2 = new FileDataSource(getExternalCacheDir().getAbsolutePath() + "/output.pcm");
        handler = new Handler(thread.getLooper()) {
            @Override
            public void handleMessage(@NonNull Message msg) {
                super.handleMessage(msg);
            }
        };

        handler.post(new Runnable() {
            @Override
            public void run() {
                // 离线部分需要进行授权校验，请根据离线证书的类型使用以下一种方式完成校验
                // 按设备授权使用以下方法，授权需要联网，完成授权后可以离线使用（仅离线部分）
                // 设备授权拉取证书需要用到在线的secretid和secretkey,可以通过https://console.cloud.tencent.com/cam/capi获取
                //  ASRController.ASRControllerError err = controller.doDeviceAuth(getApplicationContext(), Common.devSecretId, Common.devSecretKey, "", Common.devLicKey, Common.devLicPk);
                // 按应用授权使用以下方法
                ASRController.ASRControllerError err = controller.doAppAuth(getApplicationContext(), Common.appLic, Common.appLicPk, Common.appLicSign);
                if (err.code == 0) {
                    String file_name = "xnetNew_ch_libwxvoiceembedlvcsr.bin";
                    copyAssetFile(file_name);
                   err = controller.load(getExternalCacheDir().getAbsolutePath(), file_name);
                    if (err.code == 0) {
                        new Handler(Looper.getMainLooper()).post(new Runnable() {
                            @Override
                            public void run() {
                                binding.ctrBtn.setEnabled(true);
                            }
                        });
                        return;
                    }
                }
                ASRController.ASRControllerError finalErr = err;
                new Handler(lopper.getMainLooper()).post(new Runnable() {
                    @Override
                    public void run() {
                        binding.resultText.setText(String.format("Code: %d\nMessage: %s", finalErr.code, finalErr.message));
                    }
                });
            }
        });
        is_running = false;
        controller.setOnlineAuth(Common.appId, Common.secretId, Common.secretKey, Common.tempToken);
        controller.setOnlineParams("16k_zh", 1, 10, null, 0, null, 0, 0, 0, 1, 0,  0);
        binding.ctrBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, 1);
                    return;
                }
                if (is_running) {
                    controller.stop();
                    view.setEnabled(false);
                } else {
                    if (binding.sourceSel.getSelectedItemId() == 0) {
                        data_source = data_source1;
                    } else {
                        data_source = data_source2;
                    }
                    if (binding.modeSel.getSelectedItemId() == 0) {
                        controller.setMode(ASRController.MODE.MIXED);
                    } else if (binding.modeSel.getSelectedItemId() == 1) {
                        controller.setMode(ASRController.MODE.ONLINE);
                    } else {
                        controller.setMode(ASRController.MODE.OFFLINE);
                    }
                    binding.statusText.setText("");
                    controller.setListener(listener);
                    controller.setDataSource(data_source);
                    binding.resultText.setText("");
                    if (data_source.start()) {
                        controller.start();
                        view.setEnabled(false);
                    } else {
                        binding.resultText.setText("DataSource Start Failed");
                    }
                }
            }
        });
    }

    private void copyAssetFile(String name) {
        try {
            String file_name = name;
            InputStream in = getAssets().open(file_name);
            File file = new File(getExternalCacheDir().getAbsolutePath()+"/"+name);
            file.getParentFile().mkdirs();
            file.createNewFile();
            OutputStream out = new FileOutputStream(file);
//            OutputStream out = openFileOutput(file_name, MODE_PRIVATE);
            byte[] buffer = new byte[1024];
            int read;
            while ((read = in.read(buffer)) != -1) {
                out.write(buffer, 0, read);
            }
            in.close();
            out.flush();
            out.close();
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 1) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Log.i("ASRDemo", "Record Granted");
                data_source1 = new RecordDataSource(this);
            } else {
                Log.i("ASRDemo", "Record Denied");
            }
        }
    }

    public class Listener implements ASRController.ASRControllerListener {
        public MainActivity activity;

        @Override
        public void onBegin(String extra) {
            Log.i("ASRController", "Begin");
        }

        @Override
        public void onSlice(String val, String extra) {
            Log.i("ASRController Slice", val);
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    activity.binding.resultText.setText(String.format("%s %s", text, val));
                }
            });
        }

        @Override
        public void onSegment(String val, String extra) {
            Log.i("ASRController Segment", val);
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    activity.binding.resultText.setText(String.format("%s %s", text, val));
                    text = text + " " + val;
                }
            });
        }

        @Override
        public void onStart(String extra) {
            Log.i("ASRController", "Start");
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    activity.binding.ctrBtn.setEnabled(true);
                    activity.binding.ctrBtn.setText("停止");
                    activity.is_running = true;
                }
            });
        }

        @Override
        public void onError(ASRController.ASRControllerError val) {
            Log.i("ASRController", "Error");
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    data_source.stop();
                    activity.binding.ctrBtn.setEnabled(true);
                    activity.binding.ctrBtn.setText("开始");
                    activity.is_running = false;
                    activity.binding.resultText.setText(String.format("Code: %d\nMessage: %s", val.code, val.message));
                }
            });
        }

        @Override
        public void onStop() {
            Log.i("ASRController", "Stop");
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    text = "";
                    if (data_source.stop()) {
                        activity.binding.ctrBtn.setEnabled(true);
                        activity.binding.ctrBtn.setText("开始");
                        activity.is_running = false;
                    } else {
                        activity.binding.resultText.setText("DataSource Stop Failed");
                    }
                }
            });
        }

        @Override
        public void onSwitch(boolean is_online) {
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    activity.binding.statusText.setText(is_online ? "在线" : "离线");
                }
            });
        }
    }

    public interface DataSource extends ASRController.ASRControllerDataSource {
        boolean start();

        boolean stop();
    }

    public class RecordDataSource implements DataSource {

        private AudioRecord recorder;
        private String cacheDir;
        private OutputStream stream;
        private HandlerThread thread;

        @SuppressLint("MissingPermission")
        RecordDataSource(Context context) {
//            int len = AudioRecord.getMinBufferSize(16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT) * 10;
            int len = 16000 * 2 * 3;
            recorder = new AudioRecord(MediaRecorder.AudioSource.MIC, 16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, len);
            cacheDir = context.getExternalCacheDir().getAbsolutePath();
        }

        public boolean start() {
            File out = new File(String.format("%s/cache_%d", cacheDir, System.currentTimeMillis()));
            try {
                stream = new FileOutputStream(out);
                thread = new HandlerThread("write file");
                thread.start();
            } catch (FileNotFoundException e) {
                e.printStackTrace();
                return false;
            }
            recorder.startRecording();
            if (recorder.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING) {
                return true;
            }
            return false;
        }

        public boolean stop() {
            recorder.stop();
            if (recorder.getRecordingState() != AudioRecord.RECORDSTATE_STOPPED) {
                return false;
            }
            try {
                stream.close();
                thread.quitSafely();
            } catch (IOException e) {
                e.printStackTrace();
                return false;
            }
            return true;
        }

        @Override
        public long read(ByteBuffer data) {
            int len = recorder.read(data, data.remaining());
            byte[] tmp = new byte[(int) len];
            data.get(tmp);
            if (len == 0) {
                return 0;
            }
            handler.post(new Runnable() {
                @Override
                public void run() {
                    try {
                        stream.write(tmp);
                        stream.flush();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            });
            return len;
        }

    }

    public class FileDataSource implements DataSource {
        boolean first = true;
        boolean repeat = false;
        RandomAccessFile in;

        FileDataSource(String filepath) {
            try {
                in = new RandomAccessFile(filepath, "r");
            } catch (FileNotFoundException e) {
                e.printStackTrace();
                throw new RuntimeException(e);
            }
        }

        @Override
        public boolean start() {
            first = true;
            try {
                in.seek(0);
            } catch (IOException e) {
                e.printStackTrace();
                return false;
            }
            return true;
        }

        @Override
        public boolean stop() {
            return true;
        }

        @Override
        public long read(ByteBuffer data) {
            if (first) {
                first = false;
                return 0;
            }
            int len = data.remaining();
            byte[] tmp = new byte[len];
            int cur = 0;
            try {
                while (cur < len) {
                    int real_len = in.read(tmp, cur, len - cur);
                    if (real_len == -1) {
                        if(!repeat) {
                            break;
                        }
                        in.seek(0);
                        continue;
                    }
                    cur += real_len;
                }
            } catch (IOException e) {
                e.printStackTrace();
                throw new RuntimeException(e);
            }
            data.put(tmp);
            return len;
        }
    }
}