package com.jcoding.aiactivity.utils;

import android.app.Activity;
import android.util.Log;

import com.jcoding.aiactivity.manager.VoiceCommandManager;
import com.jcoding.aiactivity.manager.VoiceManager;
import com.jcoding.aiactivity.ui.VoiceSettingDialog;

/**
 * 语音设置功能集成辅助类
 *
 * 提供简化的集成接口，让任何有语音识别的Activity都能快速添加语音设置功能
 *
 * 使用方法：
 * 1. 在Activity中创建VoiceSettingHelper实例
 * 2. 在语音识别回调中调用checkAndHandleCommand()
 * 3. 如果返回true，说明已处理设置命令，无需继续处理
 *
 * 示例代码：
 * <pre>
 * VoiceSettingHelper voiceSettingHelper = new VoiceSettingHelper(this);
 *
 * voiceManager.startVoiceRecognition(new VoiceManager.VoiceRecognitionCallback() {
 *     @Override
 *     public void onRecognitionResult(String text) {
 *         // 先检查是否是设置命令
 *         if (voiceSettingHelper.checkAndHandleCommand(text)) {
 *             return; // 已处理设置命令
 *         }
 *
 *         // 继续处理其他语音输入
 *         handleNormalVoiceInput(text);
 *     }
 *     ...
 * });
 * </pre>
 */
public class VoiceSettingHelper {

    private static final String TAG = "VoiceSettingHelper";

    private Activity activity;
    private VoiceCommandManager voiceCommandManager;

    /**
     * 构造函数
     * @param activity 上下文Activity
     */
    public VoiceSettingHelper(Activity activity) {
        this.activity = activity;
        this.voiceCommandManager = VoiceCommandManager.getInstance(activity);
    }

    /**
     * 检查并处理语音命令
     *
     * @param text 语音识别的文本
     * @return true表示已处理设置命令，false表示不是设置命令
     */
    public boolean checkAndHandleCommand(String text) {
        if (text == null || text.isEmpty()) {
            return false;
        }

        try {
            // 解析语音命令
            VoiceCommandManager.VoiceCommand command = voiceCommandManager.parseCommand(text);

            if (command != null) {
                // 识别到设置命令
                Log.i(TAG, "识别到设置命令: " + command.description);
                showVoiceSettingDialog(command);
                return true;
            }

            // 不是设置命令
            return false;

        } catch (Exception e) {
            Log.e(TAG, "处理语音命令时出错", e);
            return false;
        }
    }

    /**
     * 显示语音设置对话框
     *
     * @param command 命令对象
     */
    private void showVoiceSettingDialog(VoiceCommandManager.VoiceCommand command) {
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    VoiceSettingDialog dialog = new VoiceSettingDialog(activity, command);
                    dialog.setOnSettingAppliedListener(new VoiceSettingDialog.OnSettingAppliedListener() {
                        @Override
                        public void onSettingApplied(VoiceCommandManager.VoiceCommand command) {
                            Log.i(TAG, "设置已应用: " + command.description);

                            // 可选：添加额外的处理逻辑
                            // 例如：重启Activity以应用某些设置
                            if (needsRestart(command)) {
                                restartActivity();
                            }
                        }
                    });
                    dialog.show();

                } catch (Exception e) {
                    Log.e(TAG, "显示设置对话框失败", e);
                }
            }
        });
    }

    /**
     * 判断是否需要重启Activity以应用设置
     */
    private boolean needsRestart(VoiceCommandManager.VoiceCommand command) {
        // 某些设置可能需要重启Activity才能生效
        // 这里可以根据实际情况添加判断逻辑
        return false;
    }

    /**
     * 重启Activity
     */
    private void restartActivity() {
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                activity.recreate();
            }
        });
    }

    /**
     * 获取当前支持的命令示例（用于提示用户）
     *
     * @return 命令示例数组
     */
    public static String[] getCommandExamples() {
        return new String[]{
            "打开设置",
            "调整数字人位置到左下角",
            "设置数字人大小为200dp",
            "关闭数字人",
            "打开语音设置",
            "调整语速到1.5倍",
            "进入设置页面"
        };
    }

    /**
     * 获取帮助文本
     *
     * @return 格式化的帮助文本
     */
    public static String getHelpText() {
        StringBuilder sb = new StringBuilder();
        sb.append("🎤 语音设置命令使用指南\n\n");
        sb.append("您可以通过语音命令打开和调整设置。\n\n");
        sb.append("支持的命令示例：\n");

        String[] examples = getCommandExamples();
        for (String example : examples) {
            sb.append("• ").append(example).append("\n");
        }

        sb.append("\n默认管理员口令：123456\n");
        sb.append("建议首次使用后修改口令以确保安全。");

        return sb.toString();
    }

    /**
     * 显示帮助对话框
     */
    public static void showHelpDialog(Activity activity) {
        new android.app.AlertDialog.Builder(activity)
                .setTitle("语音设置功能")
                .setMessage(getHelpText())
                .setPositiveButton("知道了", null)
                .show();
    }
}
