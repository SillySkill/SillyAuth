package com.tencent.cloud.sdktts.ui;

import android.content.Context;
import android.util.AttributeSet;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.google.android.material.slider.Slider;

public class FormSlider extends LinearLayout {

    private TextView title;
    private Slider slider;
    private View blank;

    public FormSlider(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        setOrientation(HORIZONTAL);
        setGravity(Gravity.CENTER_VERTICAL);
        title = new TextView(context);
        title.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, 0));
        addView(title);
        slider = new Slider(context);
        slider.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT, 0));
        addView(slider);
        setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    public void setTitle(String title) {
        this.title.setText(title);
    }

    public void setSlider(float min, float max, float step) {
        slider.setStepSize(step);
        slider.setValueFrom(min);
        slider.setValueTo(max);
    }

    public void setValue(float value) {
        slider.setValue(value);
    }

    public float getValue() {
        return slider.getValue();
    }

}
