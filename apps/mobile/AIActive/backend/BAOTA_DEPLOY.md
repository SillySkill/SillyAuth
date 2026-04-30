# 宝塔面板部署指南 - 配置同步API

## 🚀 快速开始

### 第一步：登录宝塔面板

**访问地址：**
```
http://你的服务器IP:8888
```

**示例：**
- 如果服务器IP是 `47.100.223.45`
- 访问: `http://47.100.223.45:8888`

**登录凭证：**
- 用户名：通常是 `root` 或安装时设置的用户名
- 密码：安装时显示的随机密码（可通过命令 `bt default` 查看）

**忘记密码？**
```bash
# 在服务器SSH中执行
bt default
# 会显示宝塔面板地址和默认密码
```

---

## 📦 部署步骤

### 方案A：使用一键部署脚本（推荐）

#### 1. 上传部署文件

通过宝塔面板上传以下文件：

```
D:\aiprogram\aiactive\backend\api\config.py
D:\aiprogram\aiactivity\backend\app.py
D:\aiprogram\aiactivity\backend\deploy_baota.sh
D:\aiprogram\aiactivity\backend\requirements.txt
```

**上传位置：**
```
/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/
```

#### 2. 执行部署脚本

在宝塔面板 → 终端 中执行：

```bash
cd /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
bash deploy_baota.sh
```

#### 3. 验证部署

```bash
# 测试API
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version
```

---

### 方案B：手动部署

#### 1. 文件准备

**本地文件位置：**
```
D:\aiprogram\aiactivity\backend\
├── api/
│   ├── __init__.py          ← 新建
│   └── config.py            ← 配置同步API
├── app.py                   ← Flask应用（更新）
├── requirements.txt         ← Python依赖
├── gunicorn_config.py       ← 新建
└── wsgi.py                  ← 新建
```

#### 2. 宝塔面板操作

##### 2.1 上传文件

**步骤：**
1. 登录宝塔面板
2. 点击左侧「文件」
3. 导航到：`/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/`
4. 点击「上传」
5. 上传上述所有文件

**确保文件结构：**
```
/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/
├── api/
│   ├── config.py
│   └── __init__.py
├── app.py
├── requirements.txt
├── gunicorn_config.py
└── wsgi.py
```

##### 2.2 安装Python依赖

**步骤：**
1. 点击左侧「终端」
2. 执行以下命令：

```bash
# 进入项目目录
cd /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

##### 2.3 添加Python项目

**步骤：**
1. 点击左侧「软件商店」
2. 找到「Python项目」或「项目管理」
3. 点击「添加项目」

**配置参数：**
```
项目名称: aiactivity-config
项目路径: /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
Python版本: 3.8 或 3.9 或 3.10
启动文件: app.py
启动方式: gunicorn
端口: 5000
绑定IP: 127.0.0.1
进程数: 2-4
自动启动: ✓
```

**或使用命令行：**
```bash
# 在宝塔终端执行
/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/venv/bin/gunicorn \
  -w 4 -b 127.0.0.1:5000 \
  -c /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/gunicorn_config.py \
  app:app
```

##### 2.4 配置Nginx反向代理

**步骤：**
1. 点击左侧「网站」
2. 找到 `jcoding.chat`
3. 点击「设置」
4. 点击「配置文件」

**在 `server {}` 块内添加（在最后一个 `}` 之前）：**

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

    # 超时设置
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
}
```

**保存并重载：**
1. 点击「保存」
2. 系统会自动测试配置
3. 测试通过后自动重载Nginx

##### 2.5 创建配置存储目录

**在宝塔终端执行：**

```bash
# 创建目录
mkdir -p /var/www/config_storage

# 设置权限
chown -R www-data:www-data /var/www/config_storage

# 验证
ls -la /var/www/config_storage
```

##### 2.6 测试API

**在宝塔终端或本地执行：**

```bash
# 测试版本接口
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version

# 预期响应：
# {"code":200,"message":"success","data":{...}}
```

---

## 🔧 配置Systemd服务（可选）

如果想用systemd管理服务（推荐）：

### 1. 创建服务文件

**在宝塔终端执行：**

```bash
cat > /etc/systemd/system/aiactivity-config.service << 'EOF'
[Unit]
Description=AI Activity Show Config Sync Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
Environment="PATH=/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/venv/bin:/usr/bin"
ExecStart=/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/venv/bin/gunicorn -c /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/gunicorn_config.py app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### 2. 启动服务

```bash
# 重载systemd配置
systemctl daemon-reload

# 启用开机自启
systemctl enable aiactivity-config

# 启动服务
systemctl start aiactivity-config

# 查看状态
systemctl status aiactivity-config

# 查看日志
journalctl -u aiactivity-config -f
```

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
# 检查Gunicorn进程
ps aux | grep gunicorn

# 检查端口监听
netstat -tlnp | grep 5000

# 或使用ss命令
ss -tlnp | grep 5000
```

### 2. 测试API接口

```bash
# 版本信息
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version

# 应返回：{"code":200,"message":"success","data":{...}}

# 统计信息
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/stats
```

### 3. 查看日志

```bash
# Gunicorn日志
tail -f /var/log/aiactivity-config/error.log

# Systemd日志
journalctl -u aiactivity-config -f

# Nginx日志
tail -f /www/wwwlogs/jcoding.chat.log
```

---

## 📤 发布配置文件

### 1. 准备配置文件

```bash
# 在服务器上创建版本目录
mkdir -p /var/www/config_storage/v1.0.0/{style,question,lottery,aibeing}

# 从本地上传配置文件（通过宝塔文件管理或SCP）
# 将 android/app/src/main/assets/ 中的文件上传到对应目录
```

**目录结构：**
```
/var/www/config_storage/v1.0.0/
├── style/
│   └── style.json
├── question/
│   ├── config.json
│   ├── 人民防空知识.json
│   └── ...
├── lottery/
│   └── config.json
└── aibeing/
    └── config.json
```

### 2. 发布版本

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

## 🐛 故障排查

### 问题1：API返回502 Bad Gateway

**原因：** Gunicorn服务未启动

**解决：**
```bash
# 检查Gunicorn进程
ps aux | grep gunicorn

# 启动服务
systemctl start aiactivity-config

# 或手动启动
/www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity/venv/bin/gunicorn \
  -w 4 -b 127.0.0.1:5000 app:app
```

### 问题2：API返回404 Not Found

**原因：** Nginx配置不正确

**解决：**
```bash
# 测试Nginx配置
nginx -t

# 查看Nginx错误日志
tail -f /www/wwwlogs/jcoding.chat.error.log

# 确认配置中包含 /application/com.jcoding.aiactivity/api/config/
```

### 问题3：端口5000被占用

**解决：**
```bash
# 查看占用端口的进程
netstat -tlnp | grep 5000

# 杀死进程
kill -9 <PID>

# 或修改配置使用其他端口
```

### 问题4：权限问题

**解决：**
```bash
# 设置正确的文件所有者
chown -R www-data:www-data /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity

# 设置正确的权限
chmod -R 755 /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity
```

---

## 📞 宝塔面板常用操作

### 查看面板信息
```bash
bt
```

### 重置面板密码
```bash
bt default
```

### 查看面板日志
```bash
bt logs
```

### 停止面板
```bash
bt stop
```

### 启动面板
```bash
bt start
```

### 重启面板
```bash
bt restart
```

---

## 📊 部署检查清单

- [ ] 登录宝塔面板
- [ ] 上传所有必需文件
- [ ] 创建Python虚拟环境
- [ ] 安装Python依赖
- [ ] 配置Gunicorn或Python项目
- [ ] 配置Nginx反向代理
- [ ] 创建配置存储目录
- [ ] 测试API接口
- [ ] 配置Systemd服务（可选）
- [ ] 上传配置文件
- [ ] 发布第一个版本
- [ ] 在Android客户端测试

---

## 🎯 快速命令参考

```bash
# === 宝塔面板登录 ===
# 访问: http://你的服务器IP:8888

# === 部署相关 ===
# 一键部署
cd /www/wwwroot/jcoding.chat/application/com.jcoding.aiactivity && bash deploy_baota.sh

# 查看服务状态
systemctl status aiactivity-config

# 重启服务
systemctl restart aiactivity-config

# 查看日志
journalctl -u aiactivity-config -f

# === 测试相关 ===
# 测试API
curl https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/version

# 测试本地连接
curl http://127.0.0.1:5000/api/config/version

# === 配置相关 ===
# 上传配置文件到
# /var/www/config_storage/vX.X.X/

# 发布版本
curl -X POST https://www.jcoding.chat/application/com.jcoding.aiactivity/api/config/publish \
  -H "Content-Type: application/json" \
  -d '{"version":"v1.0.1","release_notes":"更新说明"}'
```

---

## 📝 相关文档

- [完整部署指南](./DEPLOY_CONFIG_SYNC.md)
- [测试验证指南](./TEST_CONFIG_SYNC.md)
- [部署清单](./DEPLOYMENT_CHECKLIST.md)
