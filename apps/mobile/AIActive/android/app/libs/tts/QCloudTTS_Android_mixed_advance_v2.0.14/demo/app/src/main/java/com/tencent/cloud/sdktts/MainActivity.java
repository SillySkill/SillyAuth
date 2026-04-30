package com.tencent.cloud.sdktts;


import android.Manifest;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import com.tencent.cloud.libqcloudtts.TtsMode;
import com.tencent.cloud.libqcloudtts.utils.AAILogger;

public class MainActivity extends AppCompatActivity {
    private ListView listView;
    private String datas[] = {"账户信息", "短文本-语音合成demo", "长文本-语音合成demo", "流式合成-仅离线"};//准备数据源
    private ArrayAdapter<String> adapter;

    private TtsMode mTtsmode = TtsMode.ONLINE;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        AAILogger.enableDebug();
        AAILogger.setNeedLogFile(true,getApplicationContext());
        setContentView(R.layout.activity_main);
        ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_PHONE_STATE}, 1);
        ShareUtils.unmarshal(getApplicationContext(), SecretConfig.get());
        listView = (ListView) findViewById(R.id.lv);
        //实例化ArrayAdapter
        adapter = new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, datas);
        //设置适配器
        listView.setAdapter(adapter);
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent intent;
                switch (position) {
                    case 0:
                        intent = new Intent(MainActivity.this, ConfigActivity.class);
                        startActivity(intent);
                        return;
                    case 1:
                        intent = new Intent(MainActivity.this, TtsDemoActivity.class);
                        break;
                    case 2:
                        intent = new Intent(MainActivity.this, SplitLongTextDemoActivity.class);
                        break;
                    case 3:
                        intent = new Intent(MainActivity.this, TTSOfflineStreamActivity.class);
                        startActivity(intent);
                        return;
                    default:
                        intent = new Intent(MainActivity.this, TtsDemoActivity.class);
                }
                ChoiceMode(intent);

            }
        });
    }


    private void ChoiceMode(Intent intent) {
        final String[] items = {"在线模式", "离线模式", "离在线混合模式"};

        AlertDialog.Builder singleChoiceDialog =
                new AlertDialog.Builder(MainActivity.this);
        singleChoiceDialog.setTitle("请选择一个工作模式");
        singleChoiceDialog.setSingleChoiceItems(items, 0,
                new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        switch (which) {
                            case 0:
                                mTtsmode = TtsMode.ONLINE;
                                break;
                            case 1:
                                mTtsmode = TtsMode.OFFLINE;
                                break;
                            case 2:
                                mTtsmode = TtsMode.MIX;
                                break;
                        }
                    }
                });
        singleChoiceDialog.setPositiveButton("确定",
                new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        intent.putExtra("mode", mTtsmode);
                        startActivity(intent);
                        Toast.makeText(MainActivity.this,
                                "你选择了" + mTtsmode.toString(),
                                Toast.LENGTH_SHORT).show();


                    }
                });
        singleChoiceDialog.setCancelable(false).show();
    }


    @Override
    protected void onResume() {
        super.onResume();
        mTtsmode = TtsMode.ONLINE;
    }

}



