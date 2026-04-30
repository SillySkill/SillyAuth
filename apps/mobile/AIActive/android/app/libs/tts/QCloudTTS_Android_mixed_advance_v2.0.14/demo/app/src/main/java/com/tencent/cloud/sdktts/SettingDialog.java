package com.tencent.cloud.sdktts;


import android.content.Context;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.appcompat.app.AlertDialog;

import com.tencent.cloud.libqcloudtts.TtsMode;

import java.util.ArrayList;
import java.util.List;


public class SettingDialog extends AlertDialog implements View.OnClickListener , SeekBar.OnSeekBarChangeListener {


    public interface OnSettingDialogListener {
        void onListener(SettingDialogConfig config);
    }

    Button mBtnCancel, mBtnOk;
    Context mContext;
    SeekBar mConnTimeBar ,mReadTimeBar,mCheckTimeBar,mOfflineSpeedBar,mOnlineSpeedBar ,mOfflineVolumeBar,mOnlineVolumeBar;
    TextView mConnTimeText ,mReadTimeText,mCheckTimeText, mOfflineSpeedText, mOnlineSpeedText, mOfflineVolumeText, mOnlineVolumeText;



    private Spinner spinner_online_voice;
    private Spinner spinner_offline_voice;
    private Spinner spinner_online_language;
    //定义SpinnerItem类型的List数组作为数据源
    private List<SpinnerItem> online_voiceList;
    private List<SpinnerItem> offline_voiceList;
    private List<SpinnerItem> online_languageList;
    //定义ArrayAdapter适配器作为spinner的数据适配器
    private ArrayAdapter<SpinnerItem> online_voiceAdapter;
    private ArrayAdapter<SpinnerItem> online_languageAdapter;
    private ArrayAdapter<SpinnerItem> offline_voiceAdapter;


    OnSettingDialogListener mlistener;
    SettingDialogConfig config;


    public SettingDialog(Context context, SettingDialogConfig config, OnSettingDialogListener listener) {
        super(context);
        mContext = context;
        this.config = config;
        mlistener = listener;
    }
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        this.setCancelable(false);
        this.setCanceledOnTouchOutside(false);
        setContentView(R.layout.setting_dialog);

        mOfflineSpeedText = findViewById(R.id.offline_speed_text);
        mOfflineSpeedText.setText("" + config.offlineSpeed);
        mOnlineSpeedText = findViewById(R.id.online_speed_text);
        mOnlineSpeedText.setText("" + config.speed + getSpeedText((int) (config.speed * 10) + 20));

        mOfflineVolumeText = findViewById(R.id.offline_volume_text);
        mOfflineVolumeText.setText("" + config.offlineVolume);
        mOnlineVolumeText = findViewById(R.id.online_volume_text);
        mOnlineVolumeText.setText("" + config.volume);

        mConnTimeText = findViewById(R.id.conn_time_text);
        mConnTimeText.setText(" " + config.connectTimeout + "ms");
        mReadTimeText = findViewById(R.id.read_time_text);
        mReadTimeText.setText(" " + config.readTimeout + "ms");
        mCheckTimeText = findViewById(R.id.check_time_text);
        mCheckTimeText.setText(" " + config.CheckNetworkIntervalTime + "s");


        //语速
        mOfflineSpeedBar = findViewById(R.id.offline_speed_bar);//todo 离线
        mOfflineSpeedBar.setMax(15);
        mOfflineSpeedBar.setProgress((int) (config.offlineSpeed * 10) - 5 );
        mOfflineSpeedBar.setOnSeekBarChangeListener(this);

        mOnlineSpeedBar = findViewById(R.id.online_speed_bar);
        mOnlineSpeedBar.setMax(40);
        mOnlineSpeedBar.setProgress((int) (config.speed * 10) + 20 );
        mOnlineSpeedBar.setOnSeekBarChangeListener(this);

        //音量
        mOfflineVolumeBar = findViewById(R.id.offline_volume_bar); //todo 离线
        mOfflineVolumeBar.setMax(99);
        mOfflineVolumeBar.setProgress((int) (config.offlineVolume * 10) - 1);
        mOfflineVolumeBar.setOnSeekBarChangeListener(this);

        mOnlineVolumeBar = findViewById(R.id.online_volume_bar);
        mOnlineVolumeBar.setMax(100);
        mOnlineVolumeBar.setProgress((int) (config.volume * 10));
        mOnlineVolumeBar.setOnSeekBarChangeListener(this);

        //时间
        mConnTimeBar = findViewById(R.id.conn_time_bar);
        mConnTimeBar.setMax(30000 - 500);
        mConnTimeBar.setProgress(config.connectTimeout - 500);
        mConnTimeBar.setOnSeekBarChangeListener(this);

        mReadTimeBar = findViewById(R.id.read_time_bar);
        mReadTimeBar.setMax(60000 - 2200);
        mReadTimeBar.setProgress(config.readTimeout - 2200);
        mReadTimeBar.setOnSeekBarChangeListener(this);

        mCheckTimeBar= findViewById(R.id.check_time_bar);
        mCheckTimeBar.setMax(600);
        mCheckTimeBar.setProgress(config.CheckNetworkIntervalTime);
        mCheckTimeBar.setOnSeekBarChangeListener(this);

        //确定
        mBtnCancel = (Button) findViewById(R.id.btn_cancel);
        mBtnCancel.setOnClickListener(this);
        mBtnOk = (Button) findViewById(R.id.btn_ok);
        mBtnOk.setOnClickListener(this);

        setOnlineVoiceTypeSpinner();
        setOnlineLanguageSpinner();
        setOfflineVoiceTypeSpinner();

    }
    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btn_cancel:
                this.dismiss();
                break;
            case R.id.btn_ok:
                mlistener.onListener(config);
                this.dismiss();
                break;
            default:
                break;
        }
    }



    private void setOnlineVoiceTypeSpinner() {


        spinner_online_voice = (Spinner) findViewById(R.id.online_spinner_voice);

        online_voiceList = new ArrayList<SpinnerItem>();
        //设置音色 更多音色id可查看官网文档https://cloud.tencent.com/document/product/1073/3799
        online_voiceList.add(new SpinnerItem(1001, "智瑜(女)"));
        online_voiceList.add(new SpinnerItem(101001, "智瑜(精品-女)"));
        online_voiceList.add(new SpinnerItem(1002, "智聆(女)"));
        online_voiceList.add(new SpinnerItem(101002, "智聆(精品-女)"));
        online_voiceList.add(new SpinnerItem(1004, "智云(男)"));
        online_voiceList.add(new SpinnerItem(101004, "智云(精品-男)"));
        online_voiceList.add(new SpinnerItem(1005, "智莉(女)"));
        online_voiceList.add(new SpinnerItem(101005, "智莉(精品-女)"));
        online_voiceList.add(new SpinnerItem(101003, "智美(精品-女)"));
        online_voiceList.add(new SpinnerItem(1007, "智娜(女)"));
        online_voiceList.add(new SpinnerItem(101007, "智娜(精品-女)"));
        online_voiceList.add(new SpinnerItem(101006, "智言(精品-女)"));
        online_voiceList.add(new SpinnerItem(101014, "智宁(精品-男)"));
        online_voiceList.add(new SpinnerItem(101016, "智甜(精品-女)"));
        online_voiceList.add(new SpinnerItem(1017, "智蓉(女)"));
        online_voiceList.add(new SpinnerItem(101017, "智蓉(精品-女)"));
        online_voiceList.add(new SpinnerItem(1008, "智琪(女)"));
        online_voiceList.add(new SpinnerItem(101008, "智琪(精品-女)"));
        online_voiceList.add(new SpinnerItem(10510000, "智逍遥(男)"));

        //为spinner定义适配器，也就是将数据源存入adapter，这里需要三个参数
        online_voiceAdapter = new ArrayAdapter<SpinnerItem>(mContext, android.R.layout.simple_spinner_item, online_voiceList);

        //为适配器设置下拉列表下拉时的菜单样式。
        online_voiceAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);

        //为spinner绑定我们定义好的数据适配器
        spinner_online_voice.setAdapter(online_voiceAdapter);

        //获取原值
        for(int i = 0;i < online_voiceList.size(); i ++){
            if (online_voiceList.get(i).getID() == config.voiceType){
                spinner_online_voice.setSelection(i);
            }
        }


        //为spinner绑定监听器，这里我们使用匿名内部类的方式实现监听器
        spinner_online_voice.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                config.voiceType =  online_voiceAdapter.getItem(position).getID();

                if (config.ttsmode == TtsMode.MIX){ //如果是混合模式，同步修改一下离线音色

                    String voiceType = OfflineVoicesMappingTable.getOfflineVoice(config.voiceType);
                    if (voiceType != null){ //找到了匹配的离线音色，同步修改一下离线音色
                        config.offlineVoiceType = voiceType;
                        setOfflineVoiceTypeSpinner();//刷新UI
                    }
                }
            }
            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });
    }

    private void setOnlineLanguageSpinner() {
        spinner_online_language = (Spinner) findViewById(R.id.online_spinner_language);

        online_languageList = new ArrayList<SpinnerItem>();
        online_languageList.add(new SpinnerItem(1, "中文"));
        online_languageList.add(new SpinnerItem(2, "英文"));

        online_languageAdapter = new ArrayAdapter<SpinnerItem>(mContext, android.R.layout.simple_spinner_item, online_languageList);

        online_languageAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);

        spinner_online_language.setAdapter(online_languageAdapter);

        spinner_online_language.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                config.primaryLanguage =  online_languageAdapter.getItem(position).getID();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });
    }

    private void setOfflineVoiceTypeSpinner() {


        spinner_offline_voice = (Spinner) findViewById(R.id.offline_spinner_voice);
        offline_voiceList = new ArrayList<SpinnerItem>();

        //从json配置文件获取音色列表
        for (int i = 0;i<OfflineResourceManager.getVioceList().size();++i){
            offline_voiceList.add(new SpinnerItem(i, OfflineResourceManager.getVioceList().get(i)));
        }

        offline_voiceAdapter = new ArrayAdapter<SpinnerItem>(mContext, android.R.layout.simple_spinner_item, offline_voiceList);
        offline_voiceAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner_offline_voice.setAdapter(offline_voiceAdapter);


        //获取原值
        for (int i = 0;i<OfflineResourceManager.getVioceList().size();++i){
            if (config.offlineVoiceType.equals(OfflineResourceManager.getVioceList().get(i))){
                spinner_offline_voice.setSelection(i);
            }
        }

        //为spinner绑定监听器，这里我们使用匿名内部类的方式实现监听器
        spinner_offline_voice.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                config.offlineVoiceType =  offline_voiceAdapter.getItem(position).getValue();
            }
            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });
    }





    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        switch (seekBar.getId()){
            case R.id.offline_speed_bar :
                config.offlineSpeed = ((float)progress + 5)/10;
                mOfflineSpeedText.setText("" + config.offlineSpeed);
                break;
            case R.id.online_speed_bar :
                config.speed = ((float)progress - 20)/10;
                mOnlineSpeedText.setText("" + config.speed + getSpeedText((int) (config.speed * 10) + 20));
                break;
            case R.id.offline_volume_bar :
                config.offlineVolume = ((float)progress + 1)/10;
                mOfflineVolumeText.setText("" + config.offlineVolume);
                break;
            case R.id.online_volume_bar :
                config.volume = (float)progress/10;
                mOnlineVolumeText.setText("" + config.volume);
                break;
            case R.id.conn_time_bar :
                config.connectTimeout = progress + 500;
                mConnTimeText.setText(" " + config.connectTimeout + "ms");
                break;
            case R.id.read_time_bar :
                config.readTimeout = progress + 2200;
                mReadTimeText.setText(" " + config.readTimeout + "ms");
                break;
            case R.id.check_time_bar :
                config.CheckNetworkIntervalTime = progress;
                mCheckTimeText.setText(" " + config.CheckNetworkIntervalTime + "s");
                break;
            default:
        }
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {
    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {
    }



//标注一下speed对应的语速值
    private String getSpeedText(int v){
        switch (v){
            case 0:
                return "(0.6倍语速)"; //对应speed值为 -2.0
            case 10:
                return "(0.8倍语速)"; //对应speed值为 -1.0
            case 20:
                return "(正常语速)"; //对应speed值为 0
            case 30:
                return "(1.2倍语速)"; //对应speed值为 1.0
            case 40:
                return "(1.5倍语速)"; //对应speed值为 2.0
            default:
                return "";
        }
    }

    public class SpinnerItem {
        private int ID = 0;
        private String Value = "";

        public SpinnerItem() {
            ID = 0;
            Value = "";
        }

        public SpinnerItem(int iD, String value) {
            ID = iD;
            Value = value;
        }

        @Override
        public String toString() {

            // 如果传入适配器的对象不是字符串的情况下，直接就使用对象.toString()
            return Value;
        }

        public int getID() {
            return ID;
        }

        public void setID(int iD) {
            ID = iD;
        }

        public String getValue() {
            return Value;
        }

        public void setValue(String value) {
            Value = value;
        }
    }

}



