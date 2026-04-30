# 配置同步后端部署指南

## 当前状态

### ✅ 客户端已完成
- ConfigSyncManager URL修复
- PhotoStyleActivity自动检查更新
- APK已构建并安装

### ⚠️ 后端待部署
- API接口返回404
- 需要部署Flask应用

---

## 方案A: 通过服务器控制面板部署（推荐）

### 1. 上传文件

通过宝塔面板、FTP或其他方式上传以下文件到服务器：

```
服务器路径: /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/

需要上传的文件:
├── app.py
├── requirements.txt
├── api/
│   └── config.py
└── utils/
    └── config_crypto.py (如果需要加密)
```

### 2. 安装Python依赖

通过宝塔面板或SSH执行：

```bash
# 进入项目目录
cd /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity

# 安装依赖
pip3 install -r requirements.txt

# 或使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置Gunicorn服务

创建 `gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

### 4. 配置Systemd服务

创建 `/etc/systemd/system/aiactivity-config.service`:

```ini
[Unit]
Description=AI Activity Show Config Sync Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
Environment="PATH=/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/venv/bin"
ExecStart=/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
systemctl daemon-reload
systemctl enable aiactivity-config
systemctl start aiactivity-config
systemctl status aiactivity-config
```

### 5. 配置Nginx反向代理

在宝塔面板 -> 网站 -> 设置 -> 配置文件中添加：

```nginx
# AI活动秀配置同步API
location /application/com.jcoding.aiactivity/api/config/ {
    proxy_pass http://127.0.0.1:5000/api/config/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # 支持大文件上传
    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
}
```

重载Nginx：

```bash
nginx -t
nginx -s reload
```

### 6. 创建配置存储目录

```bash
mkdir -p /var/www/config_storage/v1.0.0/{style,question,lottery,aibeing}
chown -R www-data:www-data /var/www/config_storage
```

### 7. 测试API

```bash
# 测试版本接口
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version

# 预期响应:
# {"code": 200, "message": "success", "data": {...}}
```

---

## 方案B: 使用部署脚本（需要SSH访问）

如果可以SSH访问服务器：

1. 修改 `deploy_config_sync.sh` 中的服务器IP
2. 执行脚本：

```bash
cd D:\aiprogram\aiactive\backend
bash deploy_config_sync.sh
```

---

## 上传配置文件并发布版本

### 1. 准备配置文件

将Android assets中的配置文件复制到服务器：

```bash
# 本地执行
cd android/app/src/main/assets

# 上传配置文件到服务器
scp -i e:/silly/md/.ignore/silly.pem -r style/ root@服务器:/var/www/config_storage/v1.0.0/
scp -i e:/silly/md/.ignore/silly.pem -r question/ root@服务器:/var/www/config_storage/v1.0.0/
scp -i e:/silly/md/.ignore/silly.pem -r lottery/ root@服务器:/var/www/config_storage/v1.0.0/
```

### 2. 发布配置版本

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

---

## 验证部署

### 1. 检查服务状态

```bash
# 检查Gunicorn进程
ps aux | grep gunicorn

# 检查端口监听
netstat -tlnp | grep 5000

# 检查服务日志
journalctl -u aiactivity-config -f
```

### 2. 测试API端点

```bash
# 版本信息
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version

# 下载文件
curl "https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/file?version=v1.0.0&path=style/style.json"

# 统计信息
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/stats
```

### 3. App端测试

```bash
# 清除App数据
adb shell pm clear com.jcoding.aiactivity

# 启动App
adb shell monkey -p com.jcoding.aiactivity 1

# 查看同步日志
adb logcat -v time | grep -E "ConfigSync|PhotoStyle"
```

预期日志：
```
I/ConfigSyncManager: 开始检查配置更新...
I/ConfigSyncManager: 当前版本: v1.0.0 (100), 最新版本: v1.0.1 (101)
I/ConfigSyncManager: 发现新版本，开始下载...
D/ConfigSyncManager: 下载成功: style/style.json
I/ConfigSyncManager: 配置更新成功
I/PhotoStyleActivity: 配置更新检查: 配置已更新
```

---

## 常见问题

### API返回404
- 检查Nginx配置是否正确
- 确认Gunicorn服务正在运行
- 检查反向代理路径

### App无网络连接
```bash
# Android模拟器网络配置
adb shell "svc wifi enable"

# 或使用主机网络
# 模拟器设置 -> 网络 -> 选择桥接模式
```

### 配置文件MD5校验失败
- 确认上传的配置文件完整
- 检查文件权限

---

## 维护命令

```bash
# 重启服务
systemctl restart aiactivity-config

# 查看日志
journalctl -u aiactivity-config -n 100 -f

# 更新代码后重启
cd /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
git pull  # 或手动上传文件
systemctl restart aiactivity-config

# 查看更新统计
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/stats
```

---

## 文件位置

### 服务器文件
- 应用代码: `/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/`
- 配置存储: `/var/www/config_storage/`
- 日志文件: `/var/log/journal/` (systemd)
- Nginx配置: `/etc/nginx/sites-available/default`

### 客户端配置
- 本地配置: `/storage/emulated/0/Android/data/com.jcoding.aiactivity/files/config/`
- 默认配置: `android/app/src/main/assets/`
