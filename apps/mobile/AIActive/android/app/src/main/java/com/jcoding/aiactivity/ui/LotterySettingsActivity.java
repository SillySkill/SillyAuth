package com.jcoding.aiactivity.ui;

import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.entity.Candidate;
import com.jcoding.aiactivity.manager.LotteryConfigManager;
import com.jcoding.aiactivity.manager.LotteryRiggedConfigManager;
// import com.jcoding.aiactivity.utils.ExcelPrizeDataReader; // 待POI依赖可用后启用

import com.google.gson.JsonObject;

import java.util.ArrayList;
import java.util.List;

/**
 * 抽奖设置页
 * 配置抽奖模式（随机/内定）和内定详情
 */
public class LotterySettingsActivity extends BaseActivity {

    private Switch switchMode;
    private TextView tvModeStatus;
    private TextView tvModeDescription;
    private TextView tvRiggedSummary;
    private LinearLayout layoutRiggedList;
    private Button btnAddRigged;
    private Button btnClearRigged;
    private Button btnBack;
    private Button btnImportFromExcel;
    private TextView tvExcelInfo;
    private TextView tvExcelStatus;
    private Spinner spinnerDefaultLotteryProgram;

    private LotteryRiggedConfigManager riggedConfigManager;
    private LotteryConfigManager lotteryConfigManager;
    private List<LotteryRiggedConfigManager.RiggedConfigItem> riggedList;

    // 抽奖程序选项
    private static class LotteryProgramOption {
        String programId;
        String programName;

        LotteryProgramOption(String programId, String programName) {
            this.programId = programId;
            this.programName = programName;
        }

        @Override
        public String toString() {
            return programName;
        }
    }

    private List<LotteryProgramOption> programOptions;
    private ArrayAdapter<LotteryProgramOption> programAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lottery_settings);

        riggedConfigManager = LotteryRiggedConfigManager.getInstance(this);
        lotteryConfigManager = LotteryConfigManager.getInstance(this);

        initProgramOptions();
        initViews();
        setupListeners();
        loadMode();
        loadRiggedList();
        loadDefaultLotteryProgram();
    }

    /**
     * 初始化抽奖程序选项
     */
    private void initProgramOptions() {
        programOptions = new ArrayList<>();

        // 添加"显示选择页面"选项
        programOptions.add(new LotteryProgramOption(null, "显示选择页面"));

        // 添加3D球体抽奖
        programOptions.add(new LotteryProgramOption("lottery_3d", "3D球体抽奖"));

        // 从配置加载其他程序
        try {
            JsonObject lotteryConfig = configManager.getLotteryConfig();
            if (lotteryConfig != null && lotteryConfig.has("lottery")) {
                JsonObject programs = lotteryConfig.getAsJsonObject("lottery");
                for (String programId : programs.keySet()) {
                    JsonObject programData = programs.getAsJsonObject(programId);
                    String programName = programData.get("program_name").getAsString();
                    programOptions.add(new LotteryProgramOption(programId, programName));
                }
            }
        } catch (Exception e) {
            android.util.Log.e("LotterySettings", "加载抽奖程序列表失败", e);
        }
    }

    private void initViews() {
        switchMode = findViewById(R.id.switch_mode);
        tvModeStatus = findViewById(R.id.tv_mode_status);
        tvModeDescription = findViewById(R.id.tv_mode_description);
        tvRiggedSummary = findViewById(R.id.tv_rigged_summary);
        layoutRiggedList = findViewById(R.id.layout_rigged_list);
        btnAddRigged = findViewById(R.id.btn_add_rigged);
        btnClearRigged = findViewById(R.id.btn_clear_rigged);
        btnBack = findViewById(R.id.btn_back);
        btnImportFromExcel = findViewById(R.id.btn_import_from_excel);
        tvExcelInfo = findViewById(R.id.tv_excel_info);
        tvExcelStatus = findViewById(R.id.tv_excel_status);
        spinnerDefaultLotteryProgram = findViewById(R.id.spinner_default_lottery_program);

        // 设置Spinner适配器
        programAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, programOptions);
        programAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerDefaultLotteryProgram.setAdapter(programAdapter);

        // 检查Excel文件
        checkExcelFile();
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        switchMode.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleMode();
            }
        });

        btnAddRigged.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showAddRiggedDialog();
            }
        });

        btnClearRigged.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showClearConfirmDialog();
            }
        });

        // 默认抽奖程序选择监听
        spinnerDefaultLotteryProgram.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                LotteryProgramOption selected = programOptions.get(position);
                configManager.setDefaultLotteryProgram(selected.programId);
                Toast.makeText(LotterySettingsActivity.this,
                    "已设置默认程序：" + selected.programName,
                    Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        // Excel导入按钮
        btnImportFromExcel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                importFromExcel();
            }
        });
    }

    /**
     * 加载当前模式
     */
    private void loadMode() {
        LotteryRiggedConfigManager.LotteryMode mode = riggedConfigManager.getLotteryMode();
        updateModeUI(mode);
    }

    /**
     * 更新模式UI
     */
    private void updateModeUI(LotteryRiggedConfigManager.LotteryMode mode) {
        boolean isRigged = (mode == LotteryRiggedConfigManager.LotteryMode.RIGGED);
        switchMode.setChecked(isRigged);

        if (isRigged) {
            // 内定模式 - 灰度显示
            tvModeStatus.setText("当前模式：内定模式（灰度）");
            tvModeStatus.setTextColor(getResources().getColor(R.color.mode_rigged));
            tvModeDescription.setText("内定模式下，您可以配置每轮抽奖的标的对象（人或奖品）");
            tvModeDescription.setVisibility(View.VISIBLE);
            btnAddRigged.setVisibility(View.VISIBLE);
            btnClearRigged.setVisibility(View.VISIBLE);
            layoutRiggedList.setVisibility(View.VISIBLE);
            tvRiggedSummary.setVisibility(View.VISIBLE);
        } else {
            // 随机模式 - 彩旗显示
            tvModeStatus.setText("当前模式：随机模式（彩旗）");
            tvModeStatus.setTextColor(getResources().getColor(R.color.mode_random));
            tvModeDescription.setText("随机模式下，所有候选人公平参与抽奖，标的对象默认为人");
            tvModeDescription.setVisibility(View.VISIBLE);
            btnAddRigged.setVisibility(View.GONE);
            btnClearRigged.setVisibility(View.GONE);
            layoutRiggedList.setVisibility(View.GONE);
            tvRiggedSummary.setVisibility(View.GONE);
        }
    }

    /**
     * 切换模式
     */
    private void toggleMode() {
        LotteryRiggedConfigManager.LotteryMode currentMode = riggedConfigManager.getLotteryMode();
        LotteryRiggedConfigManager.LotteryMode newMode;

        if (currentMode == LotteryRiggedConfigManager.LotteryMode.RANDOM) {
            // 切换到内定模式
            newMode = LotteryRiggedConfigManager.LotteryMode.RIGGED;
            Toast.makeText(this, "已切换到内定模式", Toast.LENGTH_SHORT).show();
        } else {
            // 切换到随机模式
            newMode = LotteryRiggedConfigManager.LotteryMode.RANDOM;
            Toast.makeText(this, "已切换到随机模式", Toast.LENGTH_SHORT).show();
        }

        riggedConfigManager.setLotteryMode(newMode);
        updateModeUI(newMode);
    }

    /**
     * 加载内定配置列表
     */
    private void loadRiggedList() {
        riggedList = riggedConfigManager.getRiggedConfig();
        layoutRiggedList.removeAllViews();

        if (riggedList.isEmpty()) {
            tvRiggedSummary.setText("暂无内定配置");
            return;
        }

        // 更新摘要
        tvRiggedSummary.setText(riggedConfigManager.getRiggedSummary());

        // 添加每一项
        for (LotteryRiggedConfigManager.RiggedConfigItem item : riggedList) {
            View itemView = createRiggedItemView(item);
            layoutRiggedList.addView(itemView);
        }
    }

    /**
     * 创建内定项视图
     */
    private View createRiggedItemView(LotteryRiggedConfigManager.RiggedConfigItem item) {
        View view = LayoutInflater.from(this).inflate(R.layout.item_rigged_config, layoutRiggedList, false);

        TextView tvRound = view.findViewById(R.id.tv_round);
        TextView tvType = view.findViewById(R.id.tv_type);
        TextView tvPrize = view.findViewById(R.id.tv_prize);
        TextView tvCandidate = view.findViewById(R.id.tv_candidate);
        ImageView btnDelete = view.findViewById(R.id.btn_delete);

        tvRound.setText("第 " + item.round + " 轮");

        // 根据标的对象类型显示不同内容
        if (item.isTargetPerson()) {
            tvType.setText("👤 标的对象：人");
            tvType.setTextColor(getResources().getColor(R.color.mode_random));
            tvCandidate.setText("中奖者：" + item.candidateName);
            tvCandidate.setVisibility(View.VISIBLE);
        } else {
            tvType.setText("🎁 标的对象：奖品");
            tvType.setTextColor(getResources().getColor(R.color.primary));
            tvCandidate.setVisibility(View.GONE);
        }

        tvPrize.setText("奖品：" + item.prizeName);

        btnDelete.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showDeleteConfirmDialog(item);
            }
        });

        return view;
    }

    /**
     * 显示添加内定对话框
     */
    private void showAddRiggedDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_add_rigged, null);
        builder.setView(dialogView);

        Spinner spinRound = dialogView.findViewById(R.id.spin_round);
        Spinner spinTargetType = dialogView.findViewById(R.id.spin_target_type);
        EditText etPrizeName = dialogView.findViewById(R.id.et_prize_name);
        EditText etPrizeDescription = dialogView.findViewById(R.id.et_prize_description);
        Spinner spinCandidate = dialogView.findViewById(R.id.spin_candidate);
        LinearLayout layoutCandidate = dialogView.findViewById(R.id.layout_candidate);

        // 准备轮次选择（1-10轮）
        List<String> rounds = new ArrayList<>();
        for (int i = 1; i <= 10; i++) {
            rounds.add("第 " + i + " 轮");
        }
        ArrayAdapter<String> roundAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, rounds);
        roundAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinRound.setAdapter(roundAdapter);

        // 准备标的对象类型选择
        List<String> targetTypes = new ArrayList<>();
        targetTypes.add("👤 标的对象：人（滚动显示候选人，抽出中奖人）");
        targetTypes.add("🎁 标的对象：奖品（滚动显示奖品，抽出中奖奖品）");
        ArrayAdapter<String> targetTypeAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, targetTypes);
        targetTypeAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinTargetType.setAdapter(targetTypeAdapter);

        // 准备候选人列表
        List<Candidate> candidates = lotteryConfigManager.getAllCandidates();
        List<String> candidateNames = new ArrayList<>();
        for (Candidate c : candidates) {
            candidateNames.add(c.getName() + " (" + c.getDepartment() + ")");
        }
        ArrayAdapter<String> candidateAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, candidateNames);
        candidateAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinCandidate.setAdapter(candidateAdapter);

        // 监听标的对象类型选择
        spinTargetType.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                if (position == 0) {
                    // 标的对象是人：需要选择候选人
                    layoutCandidate.setVisibility(View.VISIBLE);
                } else {
                    // 标的对象是奖品：不需要选择候选人
                    layoutCandidate.setVisibility(View.GONE);
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        builder.setTitle("添加内定配置")
                .setPositiveButton("确定", (dialog, which) -> {
                    int round = spinRound.getSelectedItemPosition() + 1;
                    int targetTypePosition = spinTargetType.getSelectedItemPosition();
                    String prizeName = etPrizeName.getText().toString();
                    String prizeDescription = etPrizeDescription.getText().toString();
                    int candidateIndex = spinCandidate.getSelectedItemPosition();

                    if (prizeName.isEmpty()) {
                        Toast.makeText(LotterySettingsActivity.this, "请输入奖品名称", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    LotteryRiggedConfigManager.TargetType targetType =
                            (targetTypePosition == 0) ? LotteryRiggedConfigManager.TargetType.PERSON
                                                   : LotteryRiggedConfigManager.TargetType.PRIZE;

                    // 如果标的对象是奖品，先添加到奖品列表
                    if (targetType == LotteryRiggedConfigManager.TargetType.PRIZE) {
                        LotteryRiggedConfigManager.PrizeItem prizeItem = new LotteryRiggedConfigManager.PrizeItem();
                        prizeItem.name = prizeName;
                        prizeItem.description = prizeDescription.isEmpty() ? null : prizeDescription;
                        riggedConfigManager.addPrize(prizeItem);
                    }

                    LotteryRiggedConfigManager.RiggedConfigItem item = new LotteryRiggedConfigManager.RiggedConfigItem();
                    item.round = round;
                    item.targetType = targetType;
                    item.prizeName = prizeName;

                    if (targetType == LotteryRiggedConfigManager.TargetType.PERSON) {
                        // 标的对象是人：需要候选人
                        if (candidateIndex >= 0 && candidateIndex < candidates.size()) {
                            Candidate candidate = candidates.get(candidateIndex);
                            item.candidateId = candidate.getId();
                            item.candidateName = candidate.getName();
                        } else {
                            Toast.makeText(LotterySettingsActivity.this, "请选择候选人", Toast.LENGTH_SHORT).show();
                            return;
                        }
                    }
                    // 标的对象是奖品：不需要候选人

                    riggedConfigManager.addRiggedConfig(item);
                    loadRiggedList();
                    Toast.makeText(LotterySettingsActivity.this, "添加成功", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("取消", null);

        builder.create().show();
    }

    /**
     * 显示删除确认对话框
     */
    private void showDeleteConfirmDialog(LotteryRiggedConfigManager.RiggedConfigItem item) {
        String typeText = item.isTargetPerson() ? "人" : "奖品";
        new AlertDialog.Builder(this)
                .setTitle("删除内定配置")
                .setMessage("确定要删除第 " + item.round + " 轮的内定配置吗？（标的对象：" + typeText + "）")
                .setPositiveButton("确定", (dialog, which) -> {
                    riggedConfigManager.removeRiggedConfig(item.id);
                    loadRiggedList();
                    Toast.makeText(this, "删除成功", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("取消", null)
                .show();
    }

    /**
     * 显示清空确认对话框
     */
    private void showClearConfirmDialog() {
        new AlertDialog.Builder(this)
                .setTitle("清空内定配置")
                .setMessage("确定要清空所有内定配置吗？")
                .setPositiveButton("确定", (dialog, which) -> {
                    riggedConfigManager.clearRiggedConfig();
                    loadRiggedList();
                    Toast.makeText(this, "已清空", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("取消", null)
                .show();
    }

    @Override
    protected void showOfflineNotice() {
        // 设置页不显示离线提示
    }

    @Override
    protected void hideOfflineNotice() {
        // 设置页不显示离线提示
    }

    /**
     * 加载默认抽奖程序设置
     */
    private void loadDefaultLotteryProgram() {
        String defaultProgramId = configManager.getDefaultLotteryProgram();

        // 查找匹配的选项
        for (int i = 0; i < programOptions.size(); i++) {
            LotteryProgramOption option = programOptions.get(i);
            String optionId = option.programId;

            // 检查是否匹配（注意两个null也相等）
            if (defaultProgramId == null && optionId == null) {
                spinnerDefaultLotteryProgram.setSelection(i);
                return;
            } else if (defaultProgramId != null && defaultProgramId.equals(optionId)) {
                spinnerDefaultLotteryProgram.setSelection(i);
                return;
            }
        }

        // 如果没有找到匹配，默认选中"显示选择页面"（第一个选项）
        spinnerDefaultLotteryProgram.setSelection(0);
    }

    /**
     * 检查Excel文件
     */
    private void checkExcelFile() {
        // TODO: 待POI依赖可用后实现
        tvExcelInfo.setText("Excel文件: lottery/prizeDate.xlsx");
        tvExcelStatus.setText("Excel导入功能待网络恢复后启用");
        tvExcelStatus.setTextColor(getResources().getColor(R.color.text_secondary));
        btnImportFromExcel.setEnabled(false);
    }

    /**
     * 从Excel导入候选人数据
     */
    private void importFromExcel() {
        // TODO: 待POI依赖可用后实现
        new AlertDialog.Builder(this)
                .setTitle("功能未启用")
                .setMessage("Excel导入功能需要Apache POI库支持。\n\n" +
                        "请在网络连接正常后重新构建项目以下载依赖。\n\n" +
                        "Excel文件格式要求：\n" +
                        "第1列：姓名（必填）\n" +
                        "第2列：电话\n" +
                        "第3列：部门\n" +
                        "第4列：工号")
                .setPositiveButton("确定", null)
                .show();
    }
}
