package com.jcoding.aiactivity.ui;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.GridLayout;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.utils.PreferenceUtils;
import com.jcoding.aiactivity.utils.Constants;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * 模块选择页
 * 显示所有功能模块入口
 */
public class ModeSelectionActivity extends BaseActivity {

    private Button btnAiShow;          // AI百变秀
    private Button btnQuiz;            // 知识问答
    private Button btnLottery;         // 幸运抽奖
    private Button btnInnerShow;       // 内场秀
    private Button btnInnerController; // 内场秀控制器
    private Button btnSettings;        // 系统设置
    private TextView tvUserName;
    private TextView tvOfflineMode;
    private ImageView ivBackground;    // 背景图片

    // 模块信息列表
    private static class ModuleInfo {
        int index;              // 序号
        String name;            // 模块名称
        String iconFileName;    // 图标文件名
        int buttonId;           // 按钮ID
        Runnable action;        // 点击动作

        ModuleInfo(int index, String name, String iconFileName, int buttonId, Runnable action) {
            this.index = index;
            this.name = name;
            this.iconFileName = iconFileName;
            this.buttonId = buttonId;
            this.action = action;
        }
    }

    private List<ModuleInfo> moduleList = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_mode_selection);

        initModuleList();
        initViews();
        setupListeners();
        loadModuleIcons();
        displayUserInfo();
    }

    /**
     * 初始化模块列表
     */
    private void initModuleList() {
        // 按照viewIcon目录中的文件名格式：序号-模块名称.png
        moduleList.add(new ModuleInfo(1, "AI百变秀", "1-AI百变秀.png", R.id.btn_ai_show, this::navigateToAiShow));
        moduleList.add(new ModuleInfo(2, "知识问答", "2_知识问答.png", R.id.btn_quiz, this::navigateToQuiz));
        moduleList.add(new ModuleInfo(3, "幸运抽奖", "3_幸运抽奖.png", R.id.btn_lottery, this::navigateToLottery));
        moduleList.add(new ModuleInfo(4, "内场秀", "4_内场秀.png", R.id.btn_inner_show, this::navigateToInnerShow));
        moduleList.add(new ModuleInfo(5, "内场秀控制器", "5_内场秀控制器.png", R.id.btn_inner_controller, this::navigateToInnerController));
        moduleList.add(new ModuleInfo(6, "系统设置", "6_系统设置.png", R.id.btn_settings_grid, this::navigateToSettings));
    }

    private void initViews() {
        btnAiShow = findViewById(R.id.btn_ai_show);
        btnQuiz = findViewById(R.id.btn_quiz);
        btnLottery = findViewById(R.id.btn_lottery);
        btnInnerShow = findViewById(R.id.btn_inner_show);
        btnInnerController = findViewById(R.id.btn_inner_controller);
        btnSettings = findViewById(R.id.btn_settings_grid);
        tvUserName = findViewById(R.id.tv_user_name);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);
        ivBackground = findViewById(R.id.iv_background);

        // 加载背景图片
        loadBackgroundImage();

        // 根据配置显示/隐藏AI百变秀入口
        if (!configManager.isAiShowEnabled()) {
            btnAiShow.setVisibility(View.GONE);
        }
    }

    /**
     * 加载模块图标
     */
    private void loadModuleIcons() {
        for (ModuleInfo module : moduleList) {
            Button button = findViewById(module.buttonId);
            if (button != null) {
                // 尝试加载图标
                Bitmap iconBitmap = loadImageFromAssets("viewIcon/" + module.iconFileName);
                if (iconBitmap != null) {
                    // 创建带图标的Drawable
                    android.graphics.drawable.Drawable drawable = new android.graphics.drawable.BitmapDrawable(getResources(), iconBitmap);
                    drawable.setBounds(0, 0, 200, 200); // 设置图标大小
                    button.setCompoundDrawables(null, drawable, null, null); // 图标在文字上方
                    button.setCompoundDrawablePadding(4); // 图标和文字间距（进一步缩小）
                    android.util.Log.d("ModeSelectionActivity", "Loaded icon for " + module.name + " from " + module.iconFileName);
                } else {
                    android.util.Log.w("ModeSelectionActivity", "Failed to load icon for " + module.name + " from " + module.iconFileName);
                }
            }
        }
    }

    /**
     * 从assets加载图片
     */
    private Bitmap loadImageFromAssets(String filePath) {
        try {
            InputStream is = getAssets().open(filePath);
            return BitmapFactory.decodeStream(is);
        } catch (IOException e) {
            android.util.Log.e("ModeSelectionActivity", "Error loading image from assets: " + filePath, e);
            return null;
        }
    }

    /**
     * 加载背景图片
     */
    private void loadBackgroundImage() {
        try {
            InputStream is = getAssets().open("image/model_bk.png");
            Bitmap bitmap = BitmapFactory.decodeStream(is);
            if (bitmap != null && ivBackground != null) {
                ivBackground.setImageBitmap(bitmap);
                android.util.Log.d("ModeSelectionActivity", "Background image loaded successfully");
            } else {
                android.util.Log.w("ModeSelectionActivity", "Failed to load background image");
            }
        } catch (IOException e) {
            android.util.Log.e("ModeSelectionActivity", "Error loading background image", e);
        }
    }

    private void setupListeners() {
        // 为所有模块按钮设置点击监听器
        for (ModuleInfo module : moduleList) {
            Button button = findViewById(module.buttonId);
            if (button != null) {
                button.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        module.action.run();
                    }
                });
            }
        }

        // 根据配置显示/隐藏AI百变秀入口
        if (!configManager.isAiShowEnabled()) {
            btnAiShow.setVisibility(View.GONE);
        }
    }

    /**
     * 显示用户信息
     */
    private void displayUserInfo() {
        String userName = PreferenceUtils.getString(this, Constants.PREF_USER_NAME, "游客");
        if (tvUserName != null) {
            tvUserName.setText("欢迎，" + userName);
        }
    }

    /**
     * 跳转到AI百变秀
     */
    private void navigateToAiShow() {
        android.util.Log.d("ModeSelectionActivity", "navigateToAiShow: Starting PhotoStyleActivity");
        try {
            Intent intent = new Intent(this, PhotoStyleActivity.class);
            startActivity(intent);
            android.util.Log.d("ModeSelectionActivity", "navigateToAiShow: startActivity called");
        } catch (Exception e) {
            android.util.Log.e("ModeSelectionActivity", "navigateToAiShow: Error", e);
            Toast.makeText(this, "启动AI百变秀失败: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * 跳转到知识问答首页
     */
    private void navigateToQuiz() {
        Intent intent = new Intent(this, QuizHomeActivity.class);
        startActivity(intent);
    }

    /**
     * 跳转到幸运抽奖
     */
    private void navigateToLottery() {
        Intent intent = new Intent(this, LotterySelectActivity.class);
        startActivity(intent);
    }

    /**
     * 跳转到内场秀
     */
    private void navigateToInnerShow() {
        Intent intent = new Intent(this, InnerActivity.class);
        startActivity(intent);
    }

    /**
     * 跳转到内场秀控制器
     */
    private void navigateToInnerController() {
        Intent intent = new Intent(this, InnerShowControllerActivity.class);
        startActivity(intent);
    }

    /**
     * 跳转到系统设置
     */
    private void navigateToSettings() {
        Intent intent = new Intent(this, SettingActivity.class);
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
}
