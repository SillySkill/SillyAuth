package com.tencent.cloud.sdktts;

import androidx.appcompat.app.AppCompatActivity;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.LinearLayout;
import android.widget.RadioButton;

import com.tencent.cloud.sdktts.ui.FormInput;

public class ConfigActivity extends AppCompatActivity {

    private FormInput online_secret_id;
    private FormInput online_secret_key;

    private FormInput offline_secret_id;
    private FormInput offline_secret_key;
    private FormInput offline_lic_dev_key;
    private FormInput offline_lic_dev_pk;

    private FormInput offline_lic;
    private FormInput offline_lic_sign;
    private FormInput offline_lic_pk;

    private LinearLayout app_container;
    private LinearLayout dev_container;

    private RadioButton btn_app;
    private RadioButton btn_dev;

    private Button btn_save;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_config);
        ShareUtils.unmarshal(getApplicationContext(), SecretConfig.get());
        online_secret_id = findViewById(R.id.input_online_secretid);
        online_secret_id.setTitle("SecretID");
        online_secret_id.setValue(SecretConfig.get().online_secret_id);
        online_secret_key = findViewById(R.id.input_online_secretkey);
        online_secret_key.setTitle("SecretKey");
        online_secret_key.setValue(SecretConfig.get().online_secret_key);

        btn_app = findViewById(R.id.btn_app);
        btn_app.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                if (b) {
                    app_container.setVisibility(View.VISIBLE);
                    dev_container.setVisibility(View.GONE);
                }
            }
        });

        btn_dev = findViewById(R.id.btn_device);
        btn_dev.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                if (b) {
                    app_container.setVisibility(View.GONE);
                    dev_container.setVisibility(View.VISIBLE);
                }
            }
        });

        app_container = findViewById(R.id.container_app);
        offline_lic = findViewById(R.id.input_offline_lic);
        offline_lic.setTitle("License");
        offline_lic.setValue(SecretConfig.get().offline_lic);
        offline_lic_sign = findViewById(R.id.input_offline_lic_sign);
        offline_lic_sign.setTitle("LicenseSign");
        offline_lic_sign.setValue(SecretConfig.get().offline_lic_sign);
        offline_lic_pk = findViewById(R.id.input_offline_lic_pk);
        offline_lic_pk.setTitle("LicensePK");
        offline_lic_pk.setValue(SecretConfig.get().offline_lic_pk);

        dev_container = findViewById(R.id.container_device);
        offline_secret_id = findViewById(R.id.input_offline_secretid);
        offline_secret_id.setTitle("SecretID");
        offline_secret_id.setValue(SecretConfig.get().offline_online_secret_id);
        offline_secret_key = findViewById(R.id.input_offline_secretkey);
        offline_secret_key.setTitle("SecretKey");
        offline_secret_key.setValue(SecretConfig.get().offline_online_secret_key);
        offline_lic_dev_key = findViewById(R.id.input_offline_lic_dev_key);
        offline_lic_dev_key.setTitle("LicenseKey");
        offline_lic_dev_key.setValue(SecretConfig.get().offline_online_lic_key);
        offline_lic_dev_pk = findViewById(R.id.input_offline_lic_dev_pk);
        offline_lic_dev_pk.setTitle("LicensePK");
        offline_lic_dev_pk.setValue(SecretConfig.get().offline_online_lic_pk);

        btn_dev.setChecked(SecretConfig.get().auth_way == 1);
        btn_app.setChecked(SecretConfig.get().auth_way == 2);

        btn_save = findViewById(R.id.btn_save);
        btn_save.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                SecretConfig.get().online_secret_id = online_secret_id.getValue();
                SecretConfig.get().online_secret_key = online_secret_key.getValue();
                SecretConfig.get().offline_lic = offline_lic.getValue();
                SecretConfig.get().offline_lic_pk = offline_lic_pk.getValue();
                SecretConfig.get().offline_lic_sign = offline_lic_sign.getValue();
                SecretConfig.get().offline_online_secret_id = offline_secret_id.getValue();
                SecretConfig.get().offline_online_secret_key = offline_secret_key.getValue();
                SecretConfig.get().offline_online_lic_key = offline_lic_dev_key.getValue();
                SecretConfig.get().offline_online_lic_pk = offline_lic_dev_pk.getValue();
                SecretConfig.get().auth_way = btn_dev.isChecked() ? 1 : 2;
                ShareUtils.marshal(ConfigActivity.this.getApplicationContext(), SecretConfig.get());
                ConfigActivity.this.onBackPressed();
            }
        });

    }
}