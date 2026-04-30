# 配置同步部署清单

## ✅ 已完成

### 1. Android客户端修改
- [x] 修复 ConfigSyncManager URL (line 398)
- [x] PhotoStyleActivity 添加配置同步检查
- [x] APK 构建并安装到模拟器

**文件位置**: `android/app/src/main/java/com/jcoding/aiactivity/manager/ConfigSyncManager.java:398`

**关键代码**:
```java
private String buildDownloadUrl(String relativeUrl, String version) {
    String baseUrl = "https://www.jcoding.chat/application/com.jcoding.aiactivity/";
    if (relativeUrl.startsWith("/")) {
        return baseUrl + relativeUrl.substring(1);
    }
    return baseUrl + "api/config/file?version=" + version + "&path=" + relativeUrl;
}
```

---

## ⚠️ 待部署 - 后端服务器

### 方案1: 使用宝塔面板（推荐）

#### 步骤1: 上传文件到服务器

通过宝塔面板文件管理器上传：

**目标路径**: `/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/`

**上传文件列表**:
```
api/config.py          ← 配置同步API
app.py                 ← Flask应用入口 (更新)
requirements.txt       ← Python依赖 (更新)
```

**本地文件位置**:
```
D:\aiprogram\aiactive\backend\api\config.py
D:\aiprogram\aiactive\backend\app.py
D:\aiprogram\aiactive\backend\config_server_requirements.txt
```

#### 步骤2: 安装Python依赖

在宝塔面板 -> 终端 中执行：

```bash
cd /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity

# 安装依赖
pip3 install -r config_server_requirements.txt

# 或者直接安装
pip3 install flask==2.3.0 flask-cors==4.0.0 python-dotenv==1.0.0 gunicorn==21.2.0
```

#### 步骤3: 配置Gunicorn

在宝塔面板 -> Python项目 中添加：

```
项目名称: aiactivity-config
项目路径: /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
Python版本: 3.8+
启动文件: app.py
启动方式: gunicorn
端口: 5000 (绑定到 127.0.0.1)
启动参数: -w 4 -b 127.0.0.1:5000 app:app
```

或手动创建服务（见方案2）

#### 步骤4: 配置Nginx

在宝塔面板 -> 网站 -> 设置 -> 配置文件 中添加：

```nginx
# AI活动秀配置同步API
location /application/com.jcoding.aiactivity/api/config/ {
    proxy_pass http://127.0.0.1:5000/api/config/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
}
```

保存后重载Nginx

#### 步骤5: 创建配置存储目录

```bash
mkdir -p /var/www/config_storage
chown -R www-data:www-data /var/www/config_storage
```

#### 步骤6: 测试API

```bash
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version
```

预期响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "version": "v1.0.0",
    "version_code": 100,
    ...
  }
}
```

---

### 方案2: 使用Systemd服务

如果无法使用宝塔面板，创建systemd服务：

```bash
# 1. 创建服务文件
cat > /etc/systemd/system/aiactivity-config.service << 'EOF'
[Unit]
Description=AI Activity Show Config Sync Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 2. 启动服务
systemctl daemon-reload
systemctl enable aiactivity-config
systemctl start aiactivity-config

# 3. 检查状态
systemctl status aiactivity-config
```

---

## 📤 发布新配置流程

### 步骤1: 准备配置文件

**方法A: 使用快速发布工具**
```bash
cd D:\aiprogram\aiactive\backend

# 准备配置（不发布）
python quick_publish.py --version v1.0.1 --notes "新增国风动漫风格"

# 准备并发布
python quick_publish.py --version v1.0.1 --notes "新增国风动漫风格" --publish
```

**方法B: 手动准备**
```bash
# 在服务器上执行
mkdir -p /var/www/config_storage/v1.0.1/{style,question,lottery,aibeing}

# 上传配置文件到相应目录
```

### 步骤2: 发布到服务器

```bash
curl -X POST https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/publish \
  -H "Content-Type: application/json" \
  -d '{
    "version": "v1.0.1",
    "release_notes": "新增国风动漫风格",
    "force_update": false,
    "min_compatible_version": "v1.0.0",
    "source_dir": "/var/www/config_storage/v1.0.1"
  }'
```

### 步骤3: App端自动更新

App启动时自动检查并下载更新，无需手动操作。

---

## 🧪 测试验证

### 1. 后端API测试

```bash
# 版本信息
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version

# 下载配置文件
curl "https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/file?version=v1.0.0&path=style/style.json"

# 更新统计
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/stats
```

### 2. App端测试

```bash
# 清除应用数据
adb shell pm clear com.jcoding.aiactivity

# 启动应用
adb shell monkey -p com.jcoding.aiactivity 1

# 监控日志
adb logcat -v time | grep -E "ConfigSync|PhotoStyle"
```

预期日志输出：
```
I/ConfigSyncManager: 开始检查配置更新...
I/ConfigSyncManager: 当前版本: v1.0.0 (100), 最新版本: v1.0.1 (101)
I/ConfigSyncManager: 发现新版本，开始下载...
I/ConfigSyncManager: 配置更新成功
I/PhotoStyleActivity: 配置更新检查: 配置已更新
```

---

## 📁 文件清单

### 需要上传到服务器的文件

| 文件 | 源路径 | 目标路径 | 用途 |
|------|--------|----------|------|
| config.py | `backend/api/config.py` | `/www/wwwroot/.../api/config.py` | 配置同步API |
| app.py | `backend/app.py` | `/www/wwwroot/.../app.py` | Flask应用 |
| requirements.txt | `backend/config_server_requirements.txt` | `/www/wwwroot/.../requirements.txt` | Python依赖 |

### 配置文件存储

| 类型 | 路径 |
|------|------|
| 风格配置 | `/var/www/config_storage/vX.X.X/style/` |
| 题库配置 | `/var/www/config_storage/vX.X.X/question/` |
| 抽奖配置 | `/var/www/config_storage/vX.X.X/lottery/` |
| 数字人配置 | `/var/www/config_storage/vX.X.X/aibeing/` |

---

## 🔧 故障排查

### 问题: API返回404

**检查**:
```bash
# 1. 确认Gunicorn运行
ps aux | grep gunicorn

# 2. 确认端口监听
netstat -tlnp | grep 5000

# 3. 测试本地API
curl http://127.0.0.1:5000/api/config/version

# 4. 检查Nginx配置
nginx -t
```

### 问题: App无网络连接

**模拟器网络配置**:
```bash
# 启用WiFi
adb shell "svc wifi enable"

# 或使用模拟器设置
# 模拟器 -> 设置 -> 网络 -> WiFi -> 开启
```

### 问题: 配置文件MD5校验失败

```bash
# 重新生成MD5
cd /var/www/config_storage/v1.0.1
find . -type f -exec md5sum {} \; > checksums.md5
```

---

## 📞 技术支持

如有问题，请检查：

1. **服务日志**: `journalctl -u aiactivity-config -f`
2. **Nginx日志**: `/var/log/nginx/error.log`
3. **App日志**: `adb logcat -v time | grep ConfigSync`

---

## 📚 相关文档

- [完整部署指南](./DEPLOY_CONFIG_SYNC.md)
- [快速发布工具](./quick_publish.py)
- [部署脚本](./deploy_config_sync.sh)

---

## ✨ 下一步

1. **立即操作**: 登录宝塔面板，上传上述文件
2. **测试API**: 执行 `curl` 命令测试API
3. **发布配置**: 使用 `quick_publish.py` 发布新配置
4. **验证功能**: 在模拟器中验证配置同步

---

**部署完成后，请运行以下命令验证**:

```bash
# 测试API
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version

# 预期输出
{"code":200,"message":"success","data":{...}}
```
