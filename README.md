# SillyMD 项目仓库

## 项目架构

所有子项目共用同一个后端: `apps/platform/md/server/` (Express.js, 端口8000)

```
silly/
├── apps/                          # 应用项目集合
│   ├── platform/
│   │   └── md/                   # 网站主平台 (React Admin + Vue活动管理)
│   │       └── server/           # Express.js API后端 (共用后端)
│   ├── mobile/                   # 移动应用
│   │   ├── AIActive/             # 活动秀APP (Android)
│   │   ├── one/                  # 一块玩小程序 (微信小程序)
│   │   └── sillyauth/            # 认证码APP (Flutter)
│   └── web/                      # Web应用
│       ├── board/                # 白板协作工具
│       ├── sillychat/            # 聊天工具
│       └── webhook/              # WebSocket中转服务
│
├── common/                        # 共享资源
│   ├── server/                   # 后端服务模板
│   ├── skills/                   # Claude Code Skills定义
│   ├── agents/                   # Claude Code Agents
│   └── assets/                   # 静态资源
│       ├── banner/
│       ├── logo/
│       ├── screenshots/
│       └── kimi/
│
├── docs/                          # 文档
│   ├── backend-design/           # FastAPI后端设计参考
│   ├── 公司资料/
│   ├── 商业/
│   ├── sillymd.md               # SillyMD完整设计文档
│   └── *.md                     # 其他项目文档
│
├── infra/                         # 基础设施配置
│   ├── nginx/                   # Nginx配置
│   ├── SSH/                     # SSH配置
│   └── ssl/                     # SSL证书
│
├── scripts/                       # 工具脚本
│   ├── wechat/                  # 微信监听脚本
│   ├── websocket/               # WebSocket测试脚本
│   └── utils/                   # 通用工具脚本
│
└── xiso/                          # Agent系统配置
```

## 子项目说明

| 项目 | 类型 | 说明 |
|------|------|------|
| `apps/platform/md` | 网站平台 | SillyMD主站，包含管理后台和活动管理 |
| `apps/mobile/AIActive` | Android APP | 活动秀APP，集成腾讯云TTS/ASR |
| `apps/mobile/one` | 微信小程序 | 一块玩小程序 |
| `apps/mobile/sillyauth` | Flutter App | 认证码应用，支持TOTP和生物识别 |
| `apps/web/board` | Web应用 | 白板协作工具 |
| `apps/web/sillychat` | Web应用 | 聊天工具 |
| `apps/web/webhook` | 中转服务 | WebSocket中转服务器 |

## 共用后端配置

后端地址: `http://localhost:8000`

所有子项目通过API调用与后端通信。

## 常用命令

```bash
# 安装后端依赖
cd apps/platform/md/server && npm install

# 启动后端服务
cd apps/platform/md/server && npm start

# 查看项目结构
find . -type d -name "node_modules" -prune -o -type d -print | head -50
```

## 注意事项

- `node_modules/`, `__pycache__/`, `venv/` 是临时构建文件
- `xiso/` 包含Agent系统配置，请勿随意修改
