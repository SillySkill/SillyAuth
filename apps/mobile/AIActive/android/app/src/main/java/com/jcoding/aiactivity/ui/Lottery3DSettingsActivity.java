package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import androidx.appcompat.app.AlertDialog;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.adapter.PrizeConfigAdapter;
import com.jcoding.aiactivity.entity.LotteryPrize;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

/**
 * 3D抽奖设置页面
 */
public class Lottery3DSettingsActivity extends BaseActivity {

    private static final int REQUEST_IMPORT_PARTICIPANTS = 1001;
    private static final int REQUEST_PICK_COLOR = 1002;

    // UI Components
    private TextView tvParticipantCount;
    private RecyclerView rvPrizes;
    private SeekBar seekbarRotationSpeed;
    private SeekBar seekbarCardSize;
    private SeekBar seekbarVolume;
    private TextView tvRotationSpeed;
    private TextView tvCardSize;
    private TextView tvVolume;
    private Button btnCardColor;
    private ToggleButton toggleBgMusic;
    private ToggleButton toggleSoundEffects;

    // Data
    private List<String> participants = new ArrayList<>();
    private List<LotteryPrize> prizes = new ArrayList<>();
    private PrizeConfigAdapter prizeAdapter;

    // Settings
    private float rotationSpeed = 0.3f;
    private float cardSizeScale = 0.5f;
    private int volume = 70;
    private int cardColor = Color.parseColor("#FF6B9D");
    private boolean bgMusicEnabled = false;
    private boolean soundEffectsEnabled = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lottery_3d_settings);

        initViews();
        loadPassedData();
        loadSettings();
        setupListeners();
        setupPrizeList();
        updateParticipantCount();
    }

    private void initViews() {
        tvParticipantCount = findViewById(R.id.tv_participant_count);
        rvPrizes = findViewById(R.id.rv_prizes);
        seekbarRotationSpeed = findViewById(R.id.seekbar_rotation_speed);
        seekbarCardSize = findViewById(R.id.seekbar_card_size);
        seekbarVolume = findViewById(R.id.seekbar_volume);
        tvRotationSpeed = findViewById(R.id.tv_rotation_speed);
        tvCardSize = findViewById(R.id.tv_card_size);
        tvVolume = findViewById(R.id.tv_volume);
        btnCardColor = findViewById(R.id.btn_card_color);
        toggleBgMusic = findViewById(R.id.toggle_bg_music);
        toggleSoundEffects = findViewById(R.id.toggle_sound_effects);

        // Back button
        findViewById(R.id.btn_back).setOnClickListener(v -> finish());

        // Save button
        findViewById(R.id.btn_save).setOnClickListener(v -> saveAndExit());
    }

    private void loadPassedData() {
        // Load data passed from Lottery3DActivity
        Intent intent = getIntent();
        if (intent != null) {
            ArrayList<String> passedParticipants = intent.getStringArrayListExtra("participants");
            if (passedParticipants != null) {
                participants.clear();
                participants.addAll(passedParticipants);
            }

            try {
                ArrayList<LotteryPrize> passedPrizes = (ArrayList<LotteryPrize>) intent.getSerializableExtra("prizes");
                if (passedPrizes != null) {
                    prizes.clear();
                    prizes.addAll(passedPrizes);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void setupListeners() {
        // Import participants
        findViewById(R.id.btn_import_participants).setOnClickListener(v -> importParticipants());

        // Clear participants
        findViewById(R.id.btn_clear_participants).setOnClickListener(v -> clearParticipants());

        // Add prize
        findViewById(R.id.btn_add_prize).setOnClickListener(v -> showAddPrizeDialog());

        // Card color
        btnCardColor.setOnClickListener(v -> showColorPicker());

        // Rotation speed
        seekbarRotationSpeed.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                rotationSpeed = progress / 100f;
                tvRotationSpeed.setText(progress + "%");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // Card size
        seekbarCardSize.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                cardSizeScale = progress / 100f;
                tvCardSize.setText(progress + "%");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // Volume
        seekbarVolume.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                volume = progress;
                tvVolume.setText(progress + "%");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // Background music toggle
        toggleBgMusic.setOnCheckedChangeListener((buttonView, isChecked) -> {
            bgMusicEnabled = isChecked;
        });

        // Sound effects toggle
        toggleSoundEffects.setOnCheckedChangeListener((buttonView, isChecked) -> {
            soundEffectsEnabled = isChecked;
        });
    }

    private void setupPrizeList() {
        prizeAdapter = new PrizeConfigAdapter(new PrizeConfigAdapter.OnPrizeActionListener() {
            @Override
            public void onEditPrize(int position, LotteryPrize prize) {
                showEditPrizeDialog(position, prize);
            }

            @Override
            public void onDeletePrize(int position) {
                confirmDeletePrize(position);
            }
        });

        rvPrizes.setLayoutManager(new LinearLayoutManager(this));
        rvPrizes.setAdapter(prizeAdapter);

        // Load default prizes if empty
        if (prizes.isEmpty()) {
            prizes.add(new LotteryPrize("一等奖", 1, Color.parseColor("#FFD700")));
            prizes.add(new LotteryPrize("二等奖", 3, Color.parseColor("#C0C0C0")));
            prizes.add(new LotteryPrize("三等奖", 5, Color.parseColor("#CD7F32")));
            prizeAdapter.setPrizes(prizes);
        }
    }

    private void updateParticipantCount() {
        tvParticipantCount.setText("当前人数：" + participants.size() + "人");
    }

    private void importParticipants() {
        Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
        intent.setType("text/plain");
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        startActivityForResult(Intent.createChooser(intent, "选择人员名单文件"), REQUEST_IMPORT_PARTICIPANTS);
    }

    private void clearParticipants() {
        new AlertDialog.Builder(this)
                .setTitle("确认清空")
                .setMessage("确定要清空所有参与人员吗？")
                .setPositiveButton("确定", (dialog, which) -> {
                    participants.clear();
                    updateParticipantCount();
                    showToast("已清空参与人员");
                })
                .setNegativeButton("取消", null)
                .show();
    }

    private void showAddPrizeDialog() {
        showPrizeDialog(-1, null);
    }

    private void showEditPrizeDialog(int position, LotteryPrize prize) {
        showPrizeDialog(position, prize);
    }

    private void showPrizeDialog(int position, LotteryPrize prize) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_prize_edit, null);
        builder.setView(dialogView);

        android.widget.EditText etName = dialogView.findViewById(R.id.et_prize_name);
        android.widget.EditText etCount = dialogView.findViewById(R.id.et_prize_count);
        Button btnColor = dialogView.findViewById(R.id.btn_prize_color);
        View viewColorPreview = dialogView.findViewById(R.id.view_color_preview);

        final int[] selectedColor = new int[1];

        if (prize != null) {
            etName.setText(prize.getName());
            etCount.setText(String.valueOf(prize.getTotalCount()));
            selectedColor[0] = prize.getColor();
            viewColorPreview.setBackgroundColor(selectedColor[0]);
        } else {
            selectedColor[0] = Color.parseColor("#FFD700");
            viewColorPreview.setBackgroundColor(selectedColor[0]);
        }

        btnColor.setOnClickListener(v -> {
            // Simple color picker with preset colors
            showColorPickerDialog(selectedColor[0], color -> {
                selectedColor[0] = color;
                viewColorPreview.setBackgroundColor(color);
            });
        });

        builder.setTitle(prize == null ? "添加奖品" : "编辑奖品");
        builder.setPositiveButton("确定", (dialog, which) -> {
            String name = etName.getText().toString().trim();
            String countStr = etCount.getText().toString().trim();

            if (name.isEmpty()) {
                showToast("请输入奖品名称");
                return;
            }

            if (countStr.isEmpty()) {
                showToast("请输入奖品数量");
                return;
            }

            int count = Integer.parseInt(countStr);
            if (count <= 0) {
                showToast("奖品数量必须大于0");
                return;
            }

            LotteryPrize newPrize = new LotteryPrize(name, count, selectedColor[0]);

            if (position >= 0) {
                prizeAdapter.updatePrize(position, newPrize);
                showToast("奖品已更新");
            } else {
                prizeAdapter.addPrize(newPrize);
                showToast("奖品已添加");
            }
        });

        builder.setNegativeButton("取消", null);
        builder.show();
    }

    private void showColorPickerDialog(int currentColor, final ColorPickerCallback callback) {
        String[] colors = {"#FFD700", "#C0C0C0", "#CD7F32", "#FF6B9D", "#4CAF50",
                          "#2196F3", "#9C27B0", "#FF5722", "#795548", "#607D8B"};
        String[] colorNames = {"金色", "银色", "铜色", "粉色", "绿色",
                              "蓝色", "紫色", "橙红", "棕色", "蓝灰"};

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("选择颜色");
        builder.setItems(colorNames, (dialog, which) -> {
            int color = Color.parseColor(colors[which]);
            callback.onColorSelected(color);
        });
        builder.show();
    }

    interface ColorPickerCallback {
        void onColorSelected(int color);
    }

    private void confirmDeletePrize(int position) {
        new AlertDialog.Builder(this)
                .setTitle("确认删除")
                .setMessage("确定要删除这个奖品吗？")
                .setPositiveButton("确定", (dialog, which) -> {
                    prizeAdapter.removePrize(position);
                    showToast("奖品已删除");
                })
                .setNegativeButton("取消", null)
                .show();
    }

    private void showColorPicker() {
        showColorPickerDialog(cardColor, color -> {
            cardColor = color;
            btnCardColor.setBackgroundColor(color);
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_IMPORT_PARTICIPANTS && resultCode == RESULT_OK) {
            if (data != null && data.getData() != null) {
                importParticipantsFromFile(data.getData());
            }
        }
    }

    private void importParticipantsFromFile(Uri uri) {
        try {
            InputStream inputStream = getContentResolver().openInputStream(uri);
            BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));

            String line;
            int count = 0;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) {
                    participants.add(line);
                    count++;
                }
            }

            reader.close();
            inputStream.close();

            updateParticipantCount();
            showToast("成功导入 " + count + " 人");

        } catch (IOException e) {
            e.printStackTrace();
            showToast("导入失败: " + e.getMessage());
        }
    }

    private void loadSettings() {
        // Load settings from SharedPreferences
        // TODO: Implement settings persistence
        rotationSpeed = 0.3f;
        cardSizeScale = 0.5f;
        volume = 70;
        cardColor = Color.parseColor("#FF6B9D");
        bgMusicEnabled = false;
        soundEffectsEnabled = false;

        // Update UI
        seekbarRotationSpeed.setProgress((int) (rotationSpeed * 100));
        tvRotationSpeed.setText((int) (rotationSpeed * 100) + "%");

        seekbarCardSize.setProgress((int) (cardSizeScale * 100));
        tvCardSize.setText((int) (cardSizeScale * 100) + "%");

        seekbarVolume.setProgress(volume);
        tvVolume.setText(volume + "%");

        btnCardColor.setBackgroundColor(cardColor);
        toggleBgMusic.setChecked(bgMusicEnabled);
        toggleSoundEffects.setChecked(soundEffectsEnabled);
    }

    private void saveAndExit() {
        // Save audio settings to SharedPreferences
        getSharedPreferences("lottery_3d", MODE_PRIVATE)
                .edit()
                .putBoolean("bg_music_enabled", bgMusicEnabled)
                .putBoolean("sound_effects_enabled", soundEffectsEnabled)
                .putFloat("volume", volume)
                .apply();

        // Save participants and prizes to pass back to Lottery3DActivity
        Intent resultIntent = new Intent();
        resultIntent.putStringArrayListExtra("participants", new ArrayList<>(participants));
        resultIntent.putExtra("prizes", (java.io.Serializable) new ArrayList<>(prizes));
        setResult(RESULT_OK, resultIntent);

        showToast("设置已保存");
        finish();
    }
}
