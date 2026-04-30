# 第十三章：基础设施与部署

> 本文档描述 SillyMD 平台的容器化部署和运维配置。

## 13.1 容器化部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/sillymd
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=sillymd

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 13.2 CI/CD 流水线

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          # 部署脚本
```

## 13.3 监控与日志

| 组件 | 用途 | 优先级 |
|------|------|--------|
| Prometheus | 指标收集 | P1 |
| Grafana | 监控看板 | P1 |
| Sentry | 错误追踪 | P0 |
| ELK Stack | 日志分析 | P1 |

### Prometheus 指标定义

```python
from prometheus_client import Counter, Histogram, Gauge

# 请求计数
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# 请求延迟
request_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency'
)

# 在线用户
online_users = Gauge('online_users', 'Number of online users')

# 收入统计
revenue_total = Gauge('revenue_total', 'Total revenue in AI Points')

# Skills 统计
skills_published = Gauge(
    'skills_published_total',
    'Total published skills',
    ['category', 'type']
)
```

## 13.4 CDN 与静态资源

```
静态资源加速：
├── 前端资源 → CDN 加速
├── Skills 文件 → OSS + CDN
└── 图片资源 → OSS + CDN
```

## 13.5 备份与恢复

```bash
# PostgreSQL 备份脚本（每天凌晨 2 点）
0 2 * * * pg_dump -U postgres -d sillymd | gzip > /backup/sillymd-full-$(date +\%Y\%m\%d).sql.gz

# WAL 归档（增量备份）
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
restore_command = 'cp /backup/wal/%f %p'

# 使用 rclone 同步到 OSS
rclone sync /var/data sillymd-oss:backup \
    --backup-dir sillymd-oss:backup-archive/$(date +%Y%m%d) \
    --max-age 30d
```
