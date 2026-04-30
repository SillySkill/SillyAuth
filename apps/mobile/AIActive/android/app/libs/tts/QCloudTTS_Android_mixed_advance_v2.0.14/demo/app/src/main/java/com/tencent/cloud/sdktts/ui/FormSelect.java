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

public class FormSelect extends LinearLayout {

    public static class Options {
        int value = 0;
        String label = "";

        public Options(int value, String label) {
            this.value = value;
            this.label = label;
        }

        @NonNull
        @Override
        public String toString() {
            return label;
        }
    }

    private TextView title;
    private Spinner spinner;
    private View blank;
    private Options[] options;

    public FormSelect(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        setGravity(Gravity.CENTER_VERTICAL);
        title = new TextView(context);
        title.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, 0));
        addView(title);
        blank = new View(context);
        blank.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.MATCH_PARENT, 1));
        addView(blank);
        spinner = new Spinner(context);
        spinner.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, 0));
        addView(spinner);
        setLayoutParams(new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        setOrientation(HORIZONTAL);
    }

    public void setTitle(String title) {
        this.title.setText(title);
    }

    public void setOptions(Options[] options) {
        this.options = options;
        this.spinner.setAdapter(new ArrayAdapter<Options>(getContext(), android.R.layout.simple_spinner_item, options));
    }

    public Options getSelectOptions() {
        return (Options) this.spinner.getSelectedItem();
    }

}
