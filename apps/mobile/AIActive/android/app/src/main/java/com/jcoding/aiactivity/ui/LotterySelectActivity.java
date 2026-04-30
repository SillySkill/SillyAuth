package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.GridView;
import android.widget.TextView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.adapter.LotteryProgramAdapter;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 抽奖程序选择页
 */
public class LotterySelectActivity extends BaseActivity {

    private GridView gridView;
    private LotteryProgramAdapter adapter;
    private Button btnBack;
    private TextView tvTitle;
    private TextView tvOfflineMode;

    private List<LotteryProgram> programList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lottery_select);

        // 检查是否配置了默认抽奖程序
        String defaultProgramId = configManager.getDefaultLotteryProgram();
        if (defaultProgramId != null) {
            android.util.Log.d("LotterySelect", "检测到默认程序配置: " + defaultProgramId);
            // 直接启动默认程序
            LotteryProgram program = new LotteryProgram();
            program.setProgramId(defaultProgramId);

            // 获取程序名称
            String programName = configManager.getDefaultLotteryProgramName();
            if (programName != null) {
                program.setProgramName(programName);
            } else {
                program.setProgramName("抽奖程序");
            }

            program.setFileName("");  // 这里不需要文件名

            startLottery(program);
            finish();  // 关闭选择页面
            return;
        }

        // 没有配置默认程序，显示选择页面
        initViews();
        loadPrograms();
    }

    private void initViews() {
        gridView = findViewById(R.id.grid_programs);
        btnBack = findViewById(R.id.btn_back);
        tvTitle = findViewById(R.id.tv_title);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);

        programList = new ArrayList<>();
        adapter = new LotteryProgramAdapter(programList, new LotteryProgramAdapter.OnItemClickListener() {
            @Override
            public void onItemClick(LotteryProgram program) {
                startLottery(program);
            }
        });
        gridView.setAdapter(adapter);

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    /**
     * 加载抽奖程序列表
     */
    private void loadPrograms() {
        try {
            // 添加3D球体抽奖选项（固定在第一位）
            LotteryProgram program3D = new LotteryProgram();
            program3D.setProgramId("lottery_3d");
            program3D.setFileName("3d_lottery");
            program3D.setProgramName("3D球体抽奖");
            programList.add(program3D);
            android.util.Log.d("LotterySelect", "添加了3D球体抽奖，当前数量: " + programList.size());

            // 从配置加载其他程序
            JsonObject lotteryConfig = configManager.getLotteryConfig();
            android.util.Log.d("LotterySelect", "lotteryConfig = " + (lotteryConfig != null ? lotteryConfig.toString() : "null"));

            if (lotteryConfig != null && lotteryConfig.has("lottery")) {
                JsonObject programs = lotteryConfig.getAsJsonObject("lottery");
                android.util.Log.d("LotterySelect", "programs.keySet().size() = " + programs.keySet().size());

                for (String programId : programs.keySet()) {
                    JsonObject programData = programs.getAsJsonObject(programId);
                    String fileName = programData.get("file_name").getAsString();
                    String programName = programData.get("program_name").getAsString();

                    LotteryProgram program = new LotteryProgram();
                    program.setProgramId(programId);
                    program.setFileName(fileName);
                    program.setProgramName(programName);
                    programList.add(program);
                    android.util.Log.d("LotterySelect", "添加程序: " + programName + " (" + programId + ")");

                }
            } else {
                android.util.Log.w("LotterySelect", "lotteryConfig为null或不包含lottery节点");
            }
        } catch (Exception e) {
            android.util.Log.e("LotterySelect", "加载抽奖程序失败", e);
            e.printStackTrace();
        }

        android.util.Log.d("LotterySelect", "最终程序数量: " + programList.size());
        adapter.notifyDataSetChanged();
    }

    /**
     * 启动抽奖
     */
    private void startLottery(LotteryProgram program) {
        android.util.Log.d("LotterySelect", "startLottery: programId=" + program.getProgramId() +
            ", programName=" + program.getProgramName());

        Intent intent;
        // 根据programId判断启动哪个Activity
        if ("lottery_3d".equals(program.getProgramId())) {
            // 3D球体抽奖启动Lottery3DActivity
            android.util.Log.d("LotterySelect", "启动Lottery3DActivity");
            intent = new Intent(this, Lottery3DActivity.class);
        } else if ("jlot10004".equals(program.getProgramId()) || "fireworks".equals(program.getFileName())) {
            // 礼花抽奖启动FireworksLotteryActivity
            android.util.Log.d("LotterySelect", "启动FireworksLotteryActivity");
            intent = new Intent(this, FireworksLotteryActivity.class);
        } else {
            // 其他程序启动LotteryActivity
            android.util.Log.d("LotterySelect", "启动LotteryActivity");
            intent = new Intent(this, LotteryActivity.class);
        }
        intent.putExtra("program_id", program.getProgramId());
        intent.putExtra("program_name", program.getProgramName());
        intent.putExtra("file_name", program.getFileName());
        startActivity(intent);
    }

    @Override
    protected void showOfflineNotice() {
        if (tvOfflineMode != null) {
            tvOfflineMode.setVisibility(View.VISIBLE);
        }
    }

    @Override
    protected void hideOfflineNotice() {
        if (tvOfflineMode != null) {
            tvOfflineMode.setVisibility(View.GONE);
        }
    }

    /**
     * 抽奖程序实体
     */
    public static class LotteryProgram {
        private String programId;
        private String fileName;
        private String programName;

        public String getProgramId() {
            return programId;
        }

        public void setProgramId(String programId) {
            this.programId = programId;
        }

        public String getFileName() {
            return fileName;
        }

        public void setFileName(String fileName) {
            this.fileName = fileName;
        }

        public String getProgramName() {
            return programName;
        }

        public void setProgramName(String programName) {
            this.programName = programName;
        }
    }
}
