# 第十四章：快速开始

> 本文档提供 SillyMD 平台的安装部署和快速上手指南。

## 14.1 安装部署

```bash
# 1. 克隆项目
git clone https://github.com/sillymd/platform.git
cd platform

# 2. 后端环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要配置

# 4. 初始化数据库
alembic upgrade head

# 5. 启动后端服务
uvicorn app.main:app --reload

# 6. 前端环境
cd frontend
npm install
npm run dev

# 7. 访问平台
open http://localhost:3000
```

## 14.2 Docker 部署

```bash
# 使用 Docker Compose 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 14.3 SDK 使用

```bash
# 安装 SDK
npm install @sillymd/sdk

# 在代码中使用
import { SillyClient } from '@sillymd/sdk';

const client = new SillyClient({
  apiKey: 'your-api-key',
  endpoint: 'https://api.sillymd.com'
});
```

## 14.4 快速链接

| 链接 | 地址 |
|------|------|
| 官网 | https://www.sillymd.com |
| 文档 | https://www.sillymd.com/docs |
| API | https://www.sillymd.com/api |
| 社区 | https://www.sillymd.com/community |
| GitHub | https://github.com/sillymd |

## 附录：Skills 示例

### 示例 A: 技术 Skill - Python 数据分析模板

```yaml
skill:
  id: "tech-python-data-analysis"
  name: "Python 数据分析模板"
  version: "1.0.0"
  category: "tech"
  type: "free"
  author: "SillyMD Team"
  description: "标准化的 Python 数据分析项目模板"
  tags: ["python", "data", "analysis"]

dependencies:
  - skill_id: "tech-python-base"
    version: ">=1.0.0"

setup:
  requirements:
    - python>=3.8
    - pandas>=1.3.0
    - numpy>=1.21.0
    - matplotlib>=3.4.0

structure:
  - data/           # 数据目录
  - notebooks/      # Jupyter 笔记本
  - src/            # 源代码
  - tests/          # 测试
  - README.md       # 说明文档
```

### 示例 B: 产品 Skill - PRD 模板

```yaml
skill:
  id: "prod-prd-template"
  name: "产品需求文档 (PRD) 模板"
  version: "2.0.0"
  category: "product"
  type: "free"
  author: "SillyMD Product Team"
  description: "标准化的产品需求文档模板"
  tags: ["prd", "product", "template"]

sections:
  - 背景与目标
  - 用户分析
  - 需求列表
  - 功能规格
  - 交互设计
  - 数据指标
  - 发布计划
```

### 示例 C: 商用 Skill - 企业支付网关

```yaml
skill:
  id: "com-payment-gateway"
  name: "企业支付网关解决方案"
  version: "2.1.0"
  category: "tech"
  type: "commercial"
  author: "ACME Technologies"
  description: "完整的企业级支付网关集成方案"
  tags: ["payment", "enterprise", "integration"]
  price: 5000
  license_types: ["team", "enterprise"]

dependencies:
  - skill_id: "tech-api-base"
    version: ">=2.0.0"
  - skill_id: "tech-database-base"
    version: ">=1.5.0"

features:
  - 支持多支付渠道
  - 完整的对账系统
  - 高可用架构
  - 安全合规

digital_proof:
  content_hash: "sha256:3a7b8c9d1e2f...4b5m6n"
  platform_signature: "0x9f8e7d6c5b4a...3210"
  author_signature: "0x123456789abc...def0"
  verified: true
```
