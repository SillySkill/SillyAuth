package com.jcoding.aiactivity.ui;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.webkit.ConsoleMessage;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.utils.Constants;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Web上传页面
 * 使用WebView加载上传页面URL
 */
public class WebUploadActivity extends BaseActivity {

    private WebView webView;
    private Button btnBack;
    private TextView tvOfflineMode;
    private String styleId;
    private int mode;

    // 上传页面URL格式：https://www.jcoding.chat/upload
    private static final String WEB_UPLOAD_BASE_URL = "https://www.jcoding.chat/upload";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_web_upload);

        // 获取参数
        styleId = getIntent().getStringExtra(Constants.EXTRA_STYLE_ID);
        mode = getIntent().getIntExtra(Constants.EXTRA_MODE, Constants.MODE_INVITE_CODE);

        initViews();
        setupWebView();
        setupListeners();
    }

    private void initViews() {
        webView = findViewById(R.id.webview_upload);
        btnBack = findViewById(R.id.btn_back);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);
    }

    private void setupWebView() {
        // 配置WebView
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);

        // 启用调试
        WebView.setWebContentsDebuggingEnabled(true);

        // 添加JavaScript接口
        webView.addJavascriptInterface(new UploadCallback(), "AndroidUploadCallback");

        // 设置WebViewClient
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                view.loadUrl(url);
                return true;
            }
        });

        // 设置WebChromeClient以捕获console.log
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage consoleMessage) {
                Log.d("WebUploadConsole",
                    "[" + consoleMessage.sourceId() + ":" + consoleMessage.lineNumber() + "] " +
                    consoleMessage.messageLevel().name() + ": " + consoleMessage.message());
                return true;
            }
        });

        // 构建上传页面URL，可以添加参数
        String uploadUrl = WEB_UPLOAD_BASE_URL;
        android.util.Log.d("WebUploadActivity", "加载上传页面: " + uploadUrl);

        // 加载上传页面
        webView.loadUrl(uploadUrl);
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 检查WebView是否有历史记录，有则返回上一页
                if (webView != null && webView.canGoBack()) {
                    webView.goBack();
                } else {
                    finish();
                }
            }
        });
    }

    @Override
    public void onBackPressed() {
        // WebView返回键处理
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
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

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (webView != null) {
            webView.destroy();
            webView = null;
        }
    }

    /**
     * JavaScript回调接口
     * 上传成功后，网页会调用此接口
     */
    public class UploadCallback {
        /**
         * 上传成功回调
         * @param resultJson 上传结果的JSON字符串
         */
        @JavascriptInterface
        public void onUploadSuccess(String resultJson) {
            android.util.Log.d("WebUploadActivity", "上传成功回调: " + resultJson);

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        // 解析JSON
                        JSONObject result = new JSONObject(resultJson);
                        String url = result.optString("url", "");
                        String filename = result.optString("filename", "");
                        String fileId = result.optString("file_id", "");
                        long timestamp = result.optLong("timestamp", System.currentTimeMillis());

                        android.util.Log.d("WebUploadActivity", "上传成功: " + url);

                        // 显示成功提示
                        Toast.makeText(WebUploadActivity.this, "上传成功", Toast.LENGTH_SHORT).show();

                        // 返回结果给上一个Activity
                        getIntent().putExtra("upload_success", true);
                        getIntent().putExtra("image_url", url);
                        getIntent().putExtra("filename", filename);
                        getIntent().putExtra("file_id", fileId);
                        getIntent().putExtra("timestamp", timestamp);
                        setResult(RESULT_OK, getIntent());

                        // 延迟关闭，确保数据传递
                        webView.postDelayed(new Runnable() {
                            @Override
                            public void run() {
                                finish();
                            }
                        }, 500);

                    } catch (JSONException e) {
                        android.util.Log.e("WebUploadActivity", "解析上传结果失败", e);
                        Toast.makeText(WebUploadActivity.this, "上传结果解析失败", Toast.LENGTH_SHORT).show();
                    }
                }
            });
        }

        /**
         * 上传失败回调
         * @param errorJson 错误信息的JSON字符串
         */
        @JavascriptInterface
        public void onUploadError(String errorJson) {
            android.util.Log.d("WebUploadActivity", "上传失败回调: " + errorJson);

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(WebUploadActivity.this, "上传失败", Toast.LENGTH_SHORT).show();
                }
            });
        }
    }
}
