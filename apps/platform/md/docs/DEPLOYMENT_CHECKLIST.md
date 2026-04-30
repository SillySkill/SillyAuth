# 平台部署检查清单 (Phase 1)

> 使用此清单确保系统完整部署和运行
>
> 最后更新: 2026-04-29
> 注意: 旧 server/api/ 系统已废弃, 使用 src/ 模块化架构

---

## 📋 部署前准备

### 环境检查 (Phase 1 - 新架构)

- [ ] **操作系统**: Ubuntu 22.04+ / Windows Server 2019
- [ ] **Python**: 3.9+ 已安装
- [ ] **Node.js**: 18+ 已安装
- [ ] **PostgreSQL**: 14+ 已安装并运行
- [ ] **Git**: 已安装
- [ ] **磁盘空间**: 至少 20GB 可用空间
- [ ] **内存**: 至少 4GB RAM

### 网络配置

- [ ] **端口 80** (HTTP) 已开放
- [ ] **端口 443** (HTTPS) 已开放
- [ ] **端口 5000** (API) 已开放
- [ ] **端口 5432** (PostgreSQL) 已开放（仅内网）
- [ ] **域名**: api.sillymd.com 已配置 DNS
- [ ] **SSL 证书**: 已准备或计划使用 Let's Encrypt

---

## 第一步：数据库部署 (PostgreSQL)

### 1.1 创建数据库

```bash
psql -U postgres
```

```sql
CREATE DATABASE sillymd;
CREATE USER sillyAdmin WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sillymd TO sillyAdmin;
```

- [ ] 数据库创建成功
- [ ] 用户创建成功
- [ ] 权限授予成功

### 1.2 导入数据库架构

```bash
cd E:\silly\apps\platform\md\src\migrations

psql -U sillyAdmin -d sillymd -f 001_init_database.sql
psql -U sillyAdmin -d sillymd -f 002_add_users.sql
# ... 按顺序执行所有迁移
```

- [ ] 主架构导入成功
- [ ] 推送表导入成功
- [ ] 初始数据导入成功

### 1.3 验证数据库

```bash
mysql -u jc_admin -p jc_ai -e "SHOW TABLES;"
```

应该看到 15 个表。

---

## 第二步：后端部署 (Phase 1 - 新入口)

### 2.1 配置环境变量

```bash
# 数据库连接 (必须设置, 无默认值)
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=sillymd
export DB_USER=sillyAdmin
export DB_PASSWORD=your_secure_password

# JWT
export JWT_SECRET=$(openssl rand -base64 32)
```

- [ ] DB_HOST 已设置
- [ ] DB_PORT 已设置
- [ ] DB_NAME 已设置
- [ ] DB_USER 已设置
- [ ] DB_PASSWORD 已设置
- [ ] JWT_SECRET 已生成并设置

### 2.2 安装 Python 依赖

```bash
cd E:\silly\apps\platform\md
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r src/requirements.txt
```

- [ ] 虚拟环境创建成功
- [ ] 依赖安装完成

### 2.3 测试后端

```bash
python src/main.py
```

在另一个终端测试:

```bash
curl http://localhost:5000/api/v1/health
```

- [ ] 后端服务启动成功
- [ ] API 测试通过
- [ ] WebSocket 服务启动成功

---

## 第三步：前端部署 (admin-v2)

### 3.1 安装依赖

```bash
cd E:\silly\apps\platform\md\admin-v2
npm install
```

- [ ] node_modules 创建成功
- [ ] 依赖安装完成

### 3.2 配置环境变量

创建 .env.production:

```env
VITE_API_BASE_URL=https://api.sillymd.com/api/v1
VITE_WS_BASE_URL=wss://api.sillymd.com/ws
```

### 3.3 构建生产版本

```bash
npm run build
```

- [ ] 构建成功
- [ ] dist/ 目录已生成

---

## 📱 第四步：Android 集成

### 4.1 检查依赖

确认 OkHttp 依赖已存在于 build.gradle。

- [ ] OkHttp 依赖已存在

### 4.2 配置服务器地址

编辑 ConfigPushClient.java 配置服务器地址。

- [ ] 服务器地址已配置

### 4.3 启动推送管理器

在 MyApplication.java 中启动推送管理器。

- [ ] 推送管理器已启动

### 4.4 构建和测试

```bash
cd android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

- [ ] APK 构建成功
- [ ] 安装到设备成功

---

## ✅ 第五步：系统测试

### 5.1 后端测试

```bash
python test_api.py
```

- [ ] 所有 API 测试通过

### 5.2 WebSocket 测试

```bash
python test_push_client.py
```

- [ ] WebSocket 连接成功
- [ ] 消息收发正常

### 5.3 前端测试

访问 https://admin.jcoding.tech

- [ ] 页面加载正常
- [ ] 登录功能正常
- [ ] API 调用正常
- [ ] WebSocket 连接成功

### 5.4 Android 测试

```bash
adb logcat | grep -E "ConfigPush|ConfigManager"
```

- [ ] WebSocket 连接成功
- [ ] 设备注册成功
- [ ] 推送接收正常

---

## ✅ 部署完成确认

- [ ] 所有服务运行正常
- [ ] 数据库连接正常
- [ ] API 测试通过 (/api/v1/*)
- [ ] admin-v2 前端访问正常

**检查清单版本**: 2.0.0
**最后更新**: 2026-04-29
