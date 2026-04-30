package com.jcoding.aiactivity.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.LotteryPrize;

import java.util.ArrayList;
import java.util.List;

/**
 * 奖品配置列表适配器
 */
public class PrizeConfigAdapter extends RecyclerView.Adapter<PrizeConfigAdapter.PrizeViewHolder> {

    private List<LotteryPrize> prizes = new ArrayList<>();
    private OnPrizeActionListener listener;

    public interface OnPrizeActionListener {
        void onEditPrize(int position, LotteryPrize prize);
        void onDeletePrize(int position);
    }

    public PrizeConfigAdapter(OnPrizeActionListener listener) {
        this.listener = listener;
    }

    public void setPrizes(List<LotteryPrize> prizes) {
        this.prizes = prizes;
        notifyDataSetChanged();
    }

    public void addPrize(LotteryPrize prize) {
        prizes.add(prize);
        notifyItemInserted(prizes.size() - 1);
    }

    public void removePrize(int position) {
        if (position >= 0 && position < prizes.size()) {
            prizes.remove(position);
            notifyItemRemoved(position);
        }
    }

    public void updatePrize(int position, LotteryPrize prize) {
        if (position >= 0 && position < prizes.size()) {
            prizes.set(position, prize);
            notifyItemChanged(position);
        }
    }

    public List<LotteryPrize> getPrizes() {
        return prizes;
    }

    @NonNull
    @Override
    public PrizeViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_prize_config, parent, false);
        return new PrizeViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull PrizeViewHolder holder, int position) {
        LotteryPrize prize = prizes.get(position);
        holder.bind(prize, position);
    }

    @Override
    public int getItemCount() {
        return prizes.size();
    }

    class PrizeViewHolder extends RecyclerView.ViewHolder {
        private TextView tvPrizeName;
        private TextView tvPrizeCount;
        private View viewPrizeColor;
        private Button btnEdit;
        private Button btnDelete;

        PrizeViewHolder(@NonNull View itemView) {
            super(itemView);
            tvPrizeName = itemView.findViewById(R.id.tv_prize_name);
            tvPrizeCount = itemView.findViewById(R.id.tv_prize_count);
            viewPrizeColor = itemView.findViewById(R.id.view_prize_color);
            btnEdit = itemView.findViewById(R.id.btn_edit_prize);
            btnDelete = itemView.findViewById(R.id.btn_delete_prize);
        }

        void bind(LotteryPrize prize, int position) {
            tvPrizeName.setText(prize.getName());
            tvPrizeCount.setText("数量：" + prize.getTotalCount());
            viewPrizeColor.setBackgroundColor(prize.getColor());

            btnEdit.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onEditPrize(position, prize);
                }
            });

            btnDelete.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onDeletePrize(position);
                }
            });
        }
    }
}
