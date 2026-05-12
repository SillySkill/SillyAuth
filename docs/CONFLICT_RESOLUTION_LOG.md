# SillyMD 文档冲突处理记录

> 日期: 2026-05-13
> 触发: CLAUDE.md 更新后，全面检查所有 .md 文档中的信息冲突

---

## 冲突类型 A: 存储服务商名称变更

**旧值**: 阿里云 OSS / 阿里云 CDN / CloudFlare
**新值**: 火山引擎 TOS（自定义域名 resource.sillymd.com）/ 火山引擎 CDN

| 文件 | 行号 | 修改内容 |
|------|------|----------|
| `docs/sillymd.md` | 115-116 | 技术栈表: 存储/CDN 列更新 |
| `docs/sillymd.md` | 2044, 2046 | 备份策略: OSS → TOS |
| `docs/sillymd.md` | ~2212 | rclone 目标: sillymd-oss → sillymd-tos |
| `skills/02-architecture.md` | 19-20 | 技术栈表: 存储/CDN 列更新 |
| `skills/13-infrastructure.md` | 147-148 | CDN 架构图: OSS → TOS |
| `skills/13-infrastructure.md` | 163-164 | rclone 目标: sillymd-oss → sillymd-tos |
| `skills/README.md` | 116 | 存储: 阿里云 OSS → 火山引擎 TOS |

---

## 冲突类型 B: 启动入口变更

**旧值**: `app.main:app` 或 `src/main.py`
**新值**: 生产环境 `src/production.py`，开发环境 `uvicorn main:app --reload`

| 文件 | 行号 | 修改内容 |
|------|------|----------|
| `docs/sillymd.md` | 2074 | Dockerfile CMD: app.main:app → main:app |
| `docs/sillymd.md` | 2242 | 启动命令: 增加 production.py 说明 |
| `skills/13-infrastructure.md` | 24 | Dockerfile CMD: app.main:app → main:app，增加生产入口说明 |
| `skills/14-quickstart.md` | 25 | 启动命令: 改为 main:app + production.py |
| `docs/backend-design/DEVELOPMENT.md` | 125 | 启动命令: 改为 main:app |
| `docs/backend-design/README.md` | 33 | 启动命令: 改为 main:app |
| `docs/backend-design/PROJECT_SUMMARY.md` | 194 | 启动命令: 改为 main:app，增加 production.py |
| `apps/platform/md/docs/API_DOCUMENTATION.md` | 11 | 入口说明: 增加 production.py |
| `apps/platform/md/examples/README.md` | 165 | 启动命令: main.py → production.py |

---

## 冲突类型 C: 部署方式变更

**旧值**: Docker Compose + git clone 部署
**新值**: tar + scp 上传本地代码 + systemctl restart

| 文件 | 行号 | 修改内容 |
|------|------|----------|
| `docs/sillymd.md` | 2055 | 容器化部署章节增加"本地开发参考"标注 |
| `docs/sillymd.md` | new | 新增 §13.2 实际部署方式（生产环境） |
| `docs/sillymd.md` | 2253 | Docker 章节标注"仅本地开发" |
| `skills/13-infrastructure.md` | 1 | 增加生产环境说明 banner |
| `skills/14-quickstart.md` | 1-47 | 整节重写: 删除 git clone + Docker，替换为实际生产部署流程 |

---

## 后续建议

1. `temp/` 目录下的旧文档（如 `old_docs/OPERATIONS_GUIDE.md`）未修改，建议后续清理归档
2. 部分文档仍保留 Dockerfile/Compose 内容（标注为"本地开发参考"），保留原因为本地开发可能仍有参考价值
