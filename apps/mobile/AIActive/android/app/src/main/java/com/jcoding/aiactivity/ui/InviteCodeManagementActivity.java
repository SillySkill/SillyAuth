package com.jcoding.aiactivity.ui;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Environment;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import android.view.ViewGroup;

import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.jcoding.aiactivity.R;
import com.jcoding.aiactivity.network.ApiService;
import com.jcoding.aiactivity.network.RetrofitClient;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * 邀请码管理Activity
 * 功能：生成邀请码、查看列表、导出Excel
 */
public class InviteCodeManagementActivity extends BaseActivity {

    private ImageButton btnBack;
    private Button btnGenerate;
    private Button btnRefresh;
    private EditText etBatchName;
    private EditText etQuantity;
    private EditText etMaxUsage;
    private EditText etValidDays;
    private RecyclerView rvInviteCodes;
    private ProgressBar progressBar;
    private TextView tvTotal;
    private TextView tvOfflineMode;
    private LinearLayout llSearch;

    private InviteCodeAdapter adapter;
    private List<InviteCodeItem> inviteCodeList = new ArrayList<>();
    private int currentPage = 1;
    private int pageSize = 20;
    private int total = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_invite_code_management);

        initViews();
        setupListeners();
        loadInviteCodes();
    }

    private void initViews() {
        btnBack = findViewById(R.id.btn_back);
        btnGenerate = findViewById(R.id.btn_generate);
        btnRefresh = findViewById(R.id.btn_refresh);
        etBatchName = findViewById(R.id.et_batch_name);
        etQuantity = findViewById(R.id.et_quantity);
        etMaxUsage = findViewById(R.id.et_max_usage);
        etValidDays = findViewById(R.id.et_valid_days);
        rvInviteCodes = findViewById(R.id.rv_invite_codes);
        progressBar = findViewById(R.id.progress_bar);
        tvTotal = findViewById(R.id.tv_total);
        tvOfflineMode = findViewById(R.id.tv_offline_mode);
        // llSearch = findViewById(R.id.ll_search);  // TODO: 布局文件中暂未定义

        // 设置RecyclerView
        adapter = new InviteCodeAdapter(inviteCodeList, new InviteCodeAdapter.OnItemClickListener() {
            @Override
            public void onItemClick(InviteCodeItem item) {
                // 显示详情或复制邀请码
                showToast("邀请码：" + item.code);
            }

            @Override
            public void onDeleteClick(InviteCodeItem item) {
                deleteInviteCode(item.id);
            }

            @Override
            public void onExportClick(String batchName) {
                exportInviteCodes(batchName);
            }
        });
        rvInviteCodes.setLayoutManager(new LinearLayoutManager(this));
        rvInviteCodes.setAdapter(adapter);
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        btnGenerate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                generateInviteCodes();
            }
        });

        btnRefresh.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                currentPage = 1;
                loadInviteCodes();
            }
        });
    }

    /**
     * 生成邀请码
     */
    private void generateInviteCodes() {
        if (!NetworkUtils.isOnline(this)) {
            showToast("离线模式：生成邀请码需要网络连接");
            return;
        }

        String batchName = etBatchName.getText().toString().trim();
        String quantityStr = etQuantity.getText().toString().trim();
        String maxUsageStr = etMaxUsage.getText().toString().trim();
        String validDaysStr = etValidDays.getText().toString().trim();

        if (TextUtils.isEmpty(batchName)) {
            showToast("请输入批次名称");
            return;
        }

        if (TextUtils.isEmpty(quantityStr)) {
            showToast("请输入生成数量");
            return;
        }

        int quantity = Integer.parseInt(quantityStr);
        if (quantity <= 0 || quantity > 1000) {
            showToast("生成数量应在1-1000之间");
            return;
        }

        ProgressDialog progressDialog = new ProgressDialog(this);
        progressDialog.setMessage("正在生成邀请码...");
        progressDialog.setCancelable(false);
        progressDialog.show();

        Map<String, Object> params = new HashMap<>();
        params.put("batch_name", batchName);
        params.put("quantity", quantity);
        params.put("max_usage", TextUtils.isEmpty(maxUsageStr) ? 1 : Integer.parseInt(maxUsageStr));
        if (!TextUtils.isEmpty(validDaysStr)) {
            params.put("valid_days", Integer.parseInt(validDaysStr));
        }
        params.put("created_by", "admin");

        RetrofitClient.getInstance().getApiService()
                .generateInviteCodes(params)
                .enqueue(new Callback<ApiService.GenerateInviteCodesResponse>() {
                    @Override
                    public void onResponse(Call<ApiService.GenerateInviteCodesResponse> call,
                                         Response<ApiService.GenerateInviteCodesResponse> response) {
                        progressDialog.dismiss();
                        if (response.isSuccessful() && response.body() != null) {
                            ApiService.GenerateInviteCodesResponse genResponse = response.body();
                            if (genResponse.code == 200) {
                                showToast("成功生成" + quantity + "个邀请码");
                                // 清空输入框
                                etBatchName.setText("");
                                etQuantity.setText("");
                                etMaxUsage.setText("");
                                etValidDays.setText("");
                                // 刷新列表
                                currentPage = 1;
                                loadInviteCodes();
                                // 询问是否导出
                                showExportDialog(genResponse.data.batchName);
                            } else {
                                showToast("生成失败：" + genResponse.message);
                            }
                        } else {
                            showToast("生成失败");
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiService.GenerateInviteCodesResponse> call, Throwable t) {
                        progressDialog.dismiss();
                        showToast("生成失败：" + t.getMessage());
                    }
                });
    }

    /**
     * 显示导出对话框
     */
    private void showExportDialog(String batchName) {
        new android.app.AlertDialog.Builder(this)
                .setTitle("导出邀请码")
                .setMessage("是否立即导出邀请码到Excel？")
                .setPositiveButton("导出", (dialog, which) -> {
                    exportInviteCodes(batchName);
                })
                .setNegativeButton("稍后", null)
                .show();
    }

    /**
     * 加载邀请码列表
     */
    private void loadInviteCodes() {
        if (!NetworkUtils.isOnline(this)) {
            showToast("离线模式：查看列表需要网络连接");
            return;
        }

        showLoading(true);

        Map<String, String> params = new HashMap<>();
        params.put("page", String.valueOf(currentPage));
        params.put("page_size", String.valueOf(pageSize));

        RetrofitClient.getInstance().getApiService()
                .getInviteCodeList(params)
                .enqueue(new Callback<ApiService.InviteCodeListResponse>() {
                    @Override
                    public void onResponse(Call<ApiService.InviteCodeListResponse> call,
                                         Response<ApiService.InviteCodeListResponse> response) {
                        showLoading(false);
                        if (response.isSuccessful() && response.body() != null) {
                            ApiService.InviteCodeListResponse listResponse = response.body();
                            if (listResponse.code == 200 && listResponse.data != null) {
                                total = listResponse.data.total;
                                inviteCodeList.clear();
                                for (ApiService.InviteCodeData item : listResponse.data.list) {
                                    inviteCodeList.add(new InviteCodeItem(item));
                                }
                                adapter.notifyDataSetChanged();
                                tvTotal.setText("共 " + total + " 个邀请码");
                            }
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiService.InviteCodeListResponse> call, Throwable t) {
                        showLoading(false);
                        showToast("加载失败：" + t.getMessage());
                    }
                });
    }

    /**
     * 删除邀请码
     */
    private void deleteInviteCode(int id) {
        new android.app.AlertDialog.Builder(this)
                .setTitle("删除邀请码")
                .setMessage("确定要删除这个邀请码吗？")
                .setPositiveButton("删除", (dialog, which) -> {
                    if (!NetworkUtils.isOnline(InviteCodeManagementActivity.this)) {
                        showToast("离线模式：删除需要网络连接");
                        return;
                    }

                    Map<String, Object> params = new HashMap<>();
                    List<Integer> ids = new ArrayList<>();
                    ids.add(id);
                    params.put("ids", ids);

                    RetrofitClient.getInstance().getApiService()
                            .deleteInviteCodes(params)
                            .enqueue(new Callback<ApiService.BasicResponse>() {
                                @Override
                                public void onResponse(Call<ApiService.BasicResponse> call,
                                                     Response<ApiService.BasicResponse> response) {
                                    if (response.isSuccessful() && response.body() != null) {
                                        if (response.body().code == 200) {
                                            showToast("删除成功");
                                            loadInviteCodes();
                                        } else {
                                            showToast("删除失败：" + response.body().message);
                                        }
                                    }
                                }

                                @Override
                                public void onFailure(Call<ApiService.BasicResponse> call, Throwable t) {
                                    showToast("删除失败：" + t.getMessage());
                                }
                            });
                })
                .setNegativeButton("取消", null)
                .show();
    }

    /**
     * 导出邀请码
     */
    private void exportInviteCodes(String batchName) {
        if (!NetworkUtils.isOnline(this)) {
            showToast("离线模式：导出需要网络连接");
            return;
        }

        ProgressDialog progressDialog = new ProgressDialog(this);
        progressDialog.setMessage("正在导出...");
        progressDialog.setCancelable(false);
        progressDialog.show();

        Map<String, String> params = new HashMap<>();
        params.put("batch_name", batchName);

        RetrofitClient.getInstance().getApiService()
                .exportInviteCodes(params)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                         Response<ResponseBody> response) {
                        progressDialog.dismiss();
                        if (response.isSuccessful() && response.body() != null) {
                            try {
                                // 保存到文件
                                String fileName = "邀请码_" + batchName + ".csv";
                                File downloadsDir = Environment.getExternalStoragePublicDirectory(
                                        Environment.DIRECTORY_DOWNLOADS);
                                File file = new File(downloadsDir, fileName);

                                FileOutputStream fos = new FileOutputStream(file);
                                fos.write(response.body().bytes());
                                fos.close();

                                showToast("导出成功：" + file.getAbsolutePath());
                            } catch (Exception e) {
                                showToast("保存文件失败：" + e.getMessage());
                            }
                        } else {
                            showToast("导出失败");
                        }
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call, Throwable t) {
                        progressDialog.dismiss();
                        showToast("导出失败：" + t.getMessage());
                    }
                });
    }

    private void showLoading(boolean show) {
        progressBar.setVisibility(show ? View.VISIBLE : View.GONE);
        btnGenerate.setEnabled(!show);
        btnRefresh.setEnabled(!show);
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

    // ========== 数据模型 ==========

    static class InviteCodeItem {
        int id;
        String code;
        String batchName;
        int maxUsage;
        int usedCount;
        int status;
        String validFrom;
        String validUntil;
        String createdAt;

        InviteCodeItem(ApiService.InviteCodeData data) {
            this.id = data.id;
            this.code = data.code;
            this.batchName = data.batchName;
            this.maxUsage = data.maxUsage;
            this.usedCount = data.usedCount;
            this.status = data.status;
            this.validFrom = data.validFrom;
            this.validUntil = data.validUntil;
            this.createdAt = data.createdAt;
        }
    }

    // ========== Adapter ==========

    static class InviteCodeAdapter extends RecyclerView.Adapter<InviteCodeAdapter.ViewHolder> {
        private List<InviteCodeItem> items;
        private OnItemClickListener listener;

        interface OnItemClickListener {
            void onItemClick(InviteCodeItem item);
            void onDeleteClick(InviteCodeItem item);
            void onExportClick(String batchName);
        }

        InviteCodeAdapter(List<InviteCodeItem> items, OnItemClickListener listener) {
            this.items = items;
            this.listener = listener;
        }

        @Override
        public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
            View view = View.inflate(parent.getContext(), R.layout.item_invite_code, null);
            return new ViewHolder(view);
        }

        @Override
        public void onBindViewHolder(ViewHolder holder, int position) {
            InviteCodeItem item = items.get(position);
            holder.tvCode.setText(item.code);
            holder.tvBatchName.setText("批次：" + item.batchName);
            holder.tvUsage.setText("使用：" + item.usedCount + "/" + item.maxUsage);
            holder.tvStatus.setText(item.status == 1 ? "有效" : "禁用");
            holder.tvCreatedAt.setText("创建：" + item.createdAt);

            holder.itemView.setOnClickListener(v -> {
                if (listener != null) listener.onItemClick(item);
            });

            holder.btnDelete.setOnClickListener(v -> {
                if (listener != null) listener.onDeleteClick(item);
            });

            holder.btnExport.setOnClickListener(v -> {
                if (listener != null) listener.onExportClick(item.batchName);
            });
        }

        @Override
        public int getItemCount() {
            return items.size();
        }

        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView tvCode;
            TextView tvBatchName;
            TextView tvUsage;
            TextView tvStatus;
            TextView tvCreatedAt;
            Button btnDelete;
            Button btnExport;

            ViewHolder(View itemView) {
                super(itemView);
                tvCode = itemView.findViewById(R.id.tv_code);
                tvBatchName = itemView.findViewById(R.id.tv_batch_name);
                tvUsage = itemView.findViewById(R.id.tv_usage);
                tvStatus = itemView.findViewById(R.id.tv_status);
                tvCreatedAt = itemView.findViewById(R.id.tv_created_at);
                btnDelete = itemView.findViewById(R.id.btn_delete);
                btnExport = itemView.findViewById(R.id.btn_export);
            }
        }
    }
}
