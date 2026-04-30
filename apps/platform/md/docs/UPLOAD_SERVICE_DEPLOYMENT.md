# AI活动秀 - 照片上传服务部署指南

## 概述

本文档说明如何在服务器 `www.jcoding.chat` 上部署照片上传服务。

## 服务器信息

- **域名**: www.jcoding.chat
- **工作目录**: E:\silly\md
- **服务器地址**: 47.96.133.238

## 文件结构

```
E:\silly\md\
├── server\
│   └── api\
│       ├── main.py              # FastAPI主入口
│       ├── routes\
│       │   └── upload.py        # 上传路由（新增）
│       ├── templates\
│       │   └── upload.html      # 上传页面模板（新增）
│       └── uploads\             # 上传文件保存目录（自动创建）
```

## 新增文件

1. **routes/upload.py** - 上传API路由
   - `GET /application/upload` - 上传页面
   - `POST /application/upload/api` - 上传API
   - `GET /application/uploads/{filename}` - 访问已上传文件
   - `GET /application/health` - 健康检查

2. **templates/upload.html** - 上传页面HTML

## 部署步骤

### 1. 文件上传

将以下文件上传到服务器：

```bash
# 创建目录
mkdir -p E:\silly\md\server\api\templates

# 上传文件
# - routes/upload.py
# - templates/upload.html
```

### 2. 修改main.py

在 `server/api/main.py` 中添加以下内容：

```python
# 导入上传功能路由
from routes.upload import router as upload_router

# 注册上传功能路由（在注册消息系统路由之后）
app.include_router(upload_router)
```

### 3. 重启服务

```bash
# SSH连接到服务器
ssh -i E:\silly\md\.ignore\silly.pem root@47.96.133.238

# 进入项目目录
cd /opt/sillymd  # 或者 E:\silly\md（根据实际部署路径）

# 重启API服务
pm2 restart sillymd-api
# 或者
cd server/api
python main.py
```

### 4. 验证部署

```bash
# 健康检查
curl https://www.jcoding.chat/application/health

# 访问上传页面
# 浏览器打开: https://www.jcoding.chat/application/upload
```

## API文档

### 上传页面

```
GET https://www.jcoding.chat/application/upload
```

返回上传页面的HTML

### 上传API

```
POST https://www.jcoding.chat/application/upload/api
Content-Type: multipart/form-data
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 图片文件 |
| source | String | 否 | 来源标识 (camera/file) |
| style_id | String | 否 | 风格ID |
| user_id | String | 否 | 用户ID |

**响应:**

```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "url": "https://www.jcoding.chat/application/uploads/upload_1234567890_abc123.jpg",
    "filename": "upload_1234567890_abc123.jpg",
    "size": 1048576,
    "style_id": "style001",
    "user_id": "user123",
    "upload_time": "2026-02-05T12:00:00"
  }
}
```

### 访问已上传文件

```
GET https://www.jcoding.chat/application/uploads/{filename}
```

## 配置说明

### 文件类型限制

支持的文件类型：
- `.png`
- `.jpg` / `.jpeg`
- `.gif`
- `.webp`

### 文件大小限制

- 最大文件大小: 16MB

### 上传目录

文件保存在: `E:\silly\md\server\api\uploads\`

## Android端配置

Android端已配置使用新的上传URL：

**文件**: `WebUploadActivity.java`

```java
private static final String WEB_UPLOAD_BASE_URL = "https://www.jcoding.chat/application/upload";
```

## 测试

### 1. 上传页面测试

在浏览器中访问:
```
https://www.jcoding.chat/application/upload
```

应该能看到上传页面界面。

### 2. API测试

使用curl测试:

```bash
curl -X POST https://www.jcoding.chat/application/upload/api \
  -F "file=@test.jpg" \
  -F "source=mobile"
```

### 3. Android应用测试

1. 打开AI活动秀应用
2. 进入AI百变秀
3. 点击拍照按钮
4. 选择"上传照片"
5. 选择图片并上传

## 故障排查

### 上传失败

1. 检查服务是否运行:
   ```bash
   curl https://www.jcoding.chat/application/health
   ```

2. 检查日志:
   ```bash
   pm2 logs sillymd-api
   ```

3. 检查上传目录权限:
   ```bash
   ls -la /opt/sillymd/server/api/uploads
   ```

### 文件访问404

1. 检查文件是否存在
2. 检查文件名是否正确
3. 检查uploads目录权限

## 安全建议

1. **文件类型验证**: 服务器端已实现文件类型验证
2. **文件大小限制**: 最大16MB
3. **唯一文件名**: 使用时间戳+UUID避免文件名冲突
4. **存储位置**: 文件保存在非Web根目录

## 后续优化

1. 添加用户认证（可选）
2. 集成OSS对象存储（可选）
3. 添加图片压缩功能
4. 添加图片水印功能
5. 添加上传日志记录

## 更新日志

### v1.0.0 (2026-02-05)

- ✅ 创建上传API路由
- ✅ 创建上传页面HTML
- ✅ 修改Android端URL配置
- ✅ 部署文档编写

---

## Phase 1 更新: OSS -> TOS 迁移

> 本上传服务正在从阿里云 OSS 迁移至 Volcengine TOS。

### 环境变量变更

| 旧 (OSS) | 新 (TOS) |
|---------|----------|
| `OSS_ACCESS_KEY_ID` | `TOS_ACCESS_KEY` |
| `OSS_ACCESS_KEY_SECRET` | `TOS_SECRET_KEY` |
| `OSS_BUCKET` | `TOS_BUCKET` |
| `OSS_ENDPOINT` | `TOS_ENDPOINT` |

### TOS 配置示例

```bash
export TOS_ACCESS_KEY=your_tos_access_key
export TOS_SECRET_KEY=your_tos_secret_key
export TOS_BUCKET=sillymd-resources
export TOS_ENDPOINT=tos-cn-beijing.volces.com
```

---

**创建时间**: 2026-02-05
**最后更新**: 2026-04-29
**维护人员**: Claude Code
**版本**: v2.0.0
