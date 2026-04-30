package com.cosfun.luckdraw;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

public class MainActivity extends AppCompatActivity {
LuckDraw luckDraw;
    Button start;
    Button stop;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        start=(Button) findViewById(R.id.start);
        stop=(Button) findViewById(R.id.stop);

        luckDraw=(LuckDraw) findViewById(R.id.luckdraw);
        start.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                luckDraw.start();
            }
        });
        stop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                luckDraw.stop();
            }
        });

    }
}
