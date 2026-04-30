package com.jcoding.aiactivity.adapter;

import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.ui.LotterySelectActivity;

import java.util.List;

/**
 * 抽奖程序适配器
 */
public class LotteryProgramAdapter extends BaseAdapter {

    private List<LotterySelectActivity.LotteryProgram> programs;
    private OnItemClickListener listener;

    public LotteryProgramAdapter(List<LotterySelectActivity.LotteryProgram> programs,
                                  OnItemClickListener listener) {
        this.programs = programs;
        this.listener = listener;
    }

    @Override
    public int getCount() {
        return programs != null ? programs.size() : 0;
    }

    @Override
    public Object getItem(int position) {
        return programs.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;
        if (convertView == null) {
            convertView = View.inflate(parent.getContext(), R.layout.item_lottery_program, null);
            holder = new ViewHolder();
            holder.tvName = convertView.findViewById(R.id.tv_program_name);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        LotterySelectActivity.LotteryProgram program = programs.get(position);
        holder.tvName.setText(program.getProgramName());

        convertView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (listener != null) {
                    listener.onItemClick(program);
                }
            }
        });

        return convertView;
    }

    static class ViewHolder {
        TextView tvName;
    }

    public interface OnItemClickListener {
        void onItemClick(LotterySelectActivity.LotteryProgram program);
    }
}
