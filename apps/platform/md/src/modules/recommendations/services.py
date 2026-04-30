"""
Recommendations Service
从 ClawHub、GitHub 等来源抓取技能数据，并下载到 TOS 存储
"""

import hashlib
import logging
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# ClawHub API 基础 URL
CLAWHUB_API_BASE = "https://clawhub.ai/api"


class RecommendationsService:
    """推荐服务"""

    def __init__(self, config=None):
        self.config = config or {}
        self.clawhub_base = self.config.get("clawhub_base_url", CLAWHUB_API_BASE)
        self._storage = None
        self._clawhub_skills_folder = "skills"

    def _get_db_config(self):
        """获取数据库配置"""
        try:
            from core.config import get_db_config
            return get_db_config()
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            return None

    def _get_db_cursor(self):
        """获取数据库游标（同步版本，使用 psycopg2）"""
        import psycopg2
        from psycopg2.extras import RealDictCursor

        config = self._get_db_config()
        if not config:
            return None

        try:
            conn = psycopg2.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.user,
                password=config.password,
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            return None

    def _get_storage(self):
        """获取存储服务"""
        if self._storage is None:
            try:
                from modules.storage.services import get_storage_service
                from core.config import get_tos_config

                # 从环境变量加载 TOS 配置
                tos_config = get_tos_config()
                storage_config = {
                    "tos": {
                        "endpoint": tos_config.endpoint,
                        "region": "cn-shanghai",
                        "bucket": tos_config.bucket,
                        "access_key": tos_config.access_key,
                        "secret_key": tos_config.secret_key,
                        "custom_domain": tos_config.custom_domain
                    },
                    "default_folder": tos_config.default_prefix
                }
                self._storage = get_storage_service(storage_config)
            except Exception as e:
                logger.warning(f"Storage service not available: {e}")
        return self._storage

    def cleanup(self):
        """清理资源"""
        pass

    def generate_skill_id(self, name: str) -> str:
        """生成唯一的 skill_id"""
        base_id = name.lower().replace(" ", "-")
        base_id = "".join(c if c.isalnum() or c in "-_" else "" for c in base_id)
        suffix = secrets.token_hex(4)
        return f"clawhub-{base_id[:40]}-{suffix}"

    async def fetch_from_clawhub(self, limit: int = 20) -> List[Dict[str, Any]]:
        """从 ClawHub API 获取热门技能"""
        import httpx

        skills = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.clawhub_base}/skills/popular",
                    params={"limit": limit}
                )
                if response.status_code == 200:
                    data = response.json()
                    skills = data.get("skills", []) or []
                    logger.info(f"从 ClawHub 获取了 {len(skills)} 个技能")
        except Exception as e:
            logger.warning(f"ClawHub API 不可用: {e}，使用内置数据")

        # 如果 API 不可用，使用内置数据
        if not skills:
            skills = self._get_builtin_skills()

        return skills

    def _get_builtin_skills(self) -> List[Dict[str, Any]]:
        """获取内置的热门技能数据（ClawHub 官方技能）"""
        return [
            {
                "name": "Code Assistant",
                "description": "AI-powered code completion and refactoring assistant",
                "author": "openclaw",
                "version": "1.2.0",
                "downloads": 15420,
                "stars": 892,
                "tags": ["coding", "ai", "productivity"],
                "icon": "fa-code",
                "category": "tech",
                "download_url": None,  # 内置技能没有下载链接
            },
            {
                "name": "Web Search",
                "description": "Search the web for current information and news",
                "author": "openclaw",
                "version": "2.0.0",
                "downloads": 28350,
                "stars": 1243,
                "tags": ["search", "information", "browsing"],
                "icon": "fa-globe",
                "category": "tech",
                "download_url": None,
            },
            {
                "name": "File Operations",
                "description": "Read, write, and manage files on your system",
                "author": "openclaw",
                "version": "1.5.0",
                "downloads": 19800,
                "stars": 756,
                "tags": ["files", "system", "storage"],
                "icon": "fa-folder",
                "category": "tech",
                "download_url": None,
            },
            {
                "name": "Git Helper",
                "description": "Enhanced Git operations with interactive UI",
                "author": "community",
                "version": "1.8.0",
                "downloads": 12100,
                "stars": 534,
                "tags": ["git", "version-control", "development"],
                "icon": "fa-code-branch",
                "category": "tech",
                "download_url": None,
            },
            {
                "name": "Translate Pro",
                "description": "Professional translation with 50+ language support",
                "author": "community",
                "version": "2.3.0",
                "downloads": 8900,
                "stars": 421,
                "tags": ["translation", "languages", "communication"],
                "icon": "fa-language",
                "category": "tech",
                "download_url": None,
            },
            {
                "name": "Data Analysis",
                "description": "Analyze and visualize data with AI insights",
                "author": "openclaw",
                "version": "1.1.0",
                "downloads": 6700,
                "stars": 298,
                "tags": ["data", "analytics", "visualization"],
                "icon": "fa-chart-bar",
                "category": "tech",
                "download_url": None,
            },
            {
                "name": "Docker Manager",
                "description": "Manage Docker containers and images with ease",
                "author": "community",
                "version": "1.4.0",
                "downloads": 5400,
                "stars": 267,
                "tags": ["docker", "containers", "devops"],
                "icon": "fa-ship",
                "category": "tech",
                "download_url": None,
            },
            {
                "name": "Database Client",
                "description": "Connect and query multiple database types",
                "author": "community",
                "version": "2.1.0",
                "downloads": 4200,
                "stars": 189,
                "tags": ["database", "sql", "nosql"],
                "icon": "fa-database",
                "category": "tech",
                "download_url": None,
            },
            {
                "name": "API Documentation Generator",
                "description": "Auto-generate API documentation from code",
                "author": "openclaw",
                "version": "1.3.0",
                "downloads": 3800,
                "stars": 156,
                "tags": ["documentation", "api", "developer-tools"],
                "icon": "fa-file-alt",
                "category": "tech",
                "download_url": None,
            },
            {
                "name": "Security Scanner",
                "description": "Scan code for security vulnerabilities",
                "author": "community",
                "version": "1.0.0",
                "downloads": 2900,
                "stars": 134,
                "tags": ["security", "vulnerability", "scanning"],
                "icon": "fa-shield-alt",
                "category": "tech",
                "download_url": None,
            },
        ]

    def translate_to_chinese(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """翻译技能到中文"""
        translations = {
            "Code Assistant": "代码助手",
            "AI-powered code completion and refactoring assistant": "AI驱动的代码补全和重构助手",
            "Web Search": "网页搜索",
            "Search the web for current information and news": "搜索网络获取最新信息和新闻",
            "File Operations": "文件操作",
            "Read, write, and manage files on your system": "在您的系统上读取、写入和管理文件",
            "Git Helper": "Git 助手",
            "Enhanced Git operations with interactive UI": "增强型 Git 操作，带有交互式界面",
            "Translate Pro": "翻译专家",
            "Professional translation with 50+ language support": "支持50多种语言的专业翻译",
            "Data Analysis": "数据分析",
            "Analyze and visualize data with AI insights": "使用 AI 洞察分析和可视化数据",
            "Docker Manager": "Docker 管理器",
            "Manage Docker containers and images with ease": "轻松管理 Docker 容器和镜像",
            "Database Client": "数据库客户端",
            "Connect and query multiple database types": "连接和查询多种数据库类型",
            "API Documentation Generator": "API 文档生成器",
            "Auto-generate API documentation from code": "自动从代码生成 API 文档",
            "Security Scanner": "安全扫描器",
            "Scan code for security vulnerabilities": "扫描代码安全漏洞",
            # Tags
            "coding": "编程",
            "ai": "人工智能",
            "productivity": "效率",
            "search": "搜索",
            "information": "信息",
            "browsing": "浏览",
            "files": "文件",
            "system": "系统",
            "storage": "存储",
            "git": "Git",
            "version-control": "版本控制",
            "translation": "翻译",
            "languages": "语言",
            "communication": "沟通",
            "data": "数据",
            "analytics": "分析",
            "visualization": "可视化",
            "docker": "Docker",
            "containers": "容器",
            "devops": "DevOps",
            "database": "数据库",
            "sql": "SQL",
            "nosql": "NoSQL",
            "documentation": "文档",
            "api": "API",
            "developer-tools": "开发工具",
            "security": "安全",
            "vulnerability": "漏洞",
            "scanning": "扫描",
        }

        result = skill.copy()
        result["name"] = translations.get(skill["name"], skill["name"])
        result["description"] = translations.get(skill["description"], skill["description"])
        result["tags"] = [translations.get(t, t) for t in skill.get("tags", [])]
        return result

    def get_recommended_skills(
        self,
        locale: str = "zh-CN",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取推荐的技能列表（同步版本）"""
        import httpx

        skills = []

        try:
            response = httpx.get(
                f"{self.clawhub_base}/skills/popular",
                params={"limit": limit * 2},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                skills = data.get("skills", []) or []
        except Exception as e:
            logger.warning(f"ClawHub API 不可用: {e}")

        # 如果 API 不可用，使用内置数据
        if not skills:
            skills = self._get_builtin_skills()

        # 翻译（如果需要中文）
        if locale == "zh-CN":
            skills = [self.translate_to_chinese(s) for s in skills]

        return skills[:limit]

    def get_trending_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门技能"""
        # 目前使用相同的数据源
        return self._get_builtin_skills()[:limit]

    def get_latest_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最新技能"""
        # 目前使用相同的数据源
        return self._get_builtin_skills()[:limit]

    # ==================== TOS 存储相关方法 ====================

    def init_clawhub_skills_table(self) -> None:
        """初始化 ClawHub 技能数据库表"""
        conn = self._get_db_cursor()
        if not conn:
            logger.warning("Database not available, skipping table creation")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clawhub_skills (
                    id SERIAL PRIMARY KEY,
                    skill_index INTEGER NOT NULL UNIQUE,  -- 依序编号 1, 2, 3...
                    skill_id VARCHAR(100) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    author VARCHAR(100),
                    version VARCHAR(50),
                    category VARCHAR(50) DEFAULT 'tech',
                    icon VARCHAR(50) DEFAULT 'fa-code',
                    tags TEXT[],  -- PostgreSQL array
                    downloads INTEGER DEFAULT 0,
                    stars INTEGER DEFAULT 0,
                    -- TOS 存储信息
                    tos_key VARCHAR(500),           -- TOS 文件路径
                    tos_url VARCHAR(1000),          -- 完整下载 URL
                    file_size BIGINT DEFAULT 0,     -- 文件大小
                    checksum VARCHAR(128),          -- 文件校验和
                    -- 原始数据
                    raw_data JSONB,                 -- 原始 JSON 数据
                    -- 时间戳
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    -- 状态
                    is_active BOOLEAN DEFAULT TRUE,
                    is_downloaded BOOLEAN DEFAULT FALSE
                )
            """)

            # 创建索引
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_clawhub_skills_skill_index
                ON clawhub_skills(skill_index)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_clawhub_skills_category
                ON clawhub_skills(category)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_clawhub_skills_downloads
                ON clawhub_skills(downloads DESC)
            """)

            conn.commit()
            cur.close()
            conn.close()
            logger.info("ClawHub skills table initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize clawhub_skills table: {e}")
            if conn:
                conn.close()

    def _generate_skill_index(self, skills: List[Dict]) -> List[Dict]:
        """为技能生成依序编号"""
        # 按下载量排序
        sorted_skills = sorted(skills, key=lambda x: x.get("downloads", 0), reverse=True)
        for i, skill in enumerate(sorted_skills, start=1):
            skill["skill_index"] = i
        return sorted_skills

    def sync_clawhub_skills(self) -> Dict[str, Any]:
        """
        从 ClawHub 同步技能数据到数据库和 TOS

        Returns:
            同步结果统计
        """
        # 初始化表
        self.init_clawhub_skills_table()

        # 获取技能数据
        skills = self._get_builtin_skills()

        # 生成依序编号
        skills = self._generate_skill_index(skills)

        conn = self._get_db_cursor()
        storage = self._get_storage()

        stats = {
            "total": len(skills),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "uploaded_to_tos": 0,
            "errors": []
        }

        for skill in skills:
            try:
                skill_id = self.generate_skill_id(skill["name"])

                # 检查是否已存在
                if conn:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT id, skill_index FROM clawhub_skills WHERE skill_index = %s",
                        (skill["skill_index"],)
                    )
                    existing = cur.fetchone()

                    if existing:
                        # 更新
                        cur.execute("""
                            UPDATE clawhub_skills SET
                                name = %s,
                                description = %s,
                                author = %s,
                                version = %s,
                                category = %s,
                                icon = %s,
                                tags = %s,
                                downloads = %s,
                                stars = %s,
                                raw_data = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE skill_index = %s
                        """, (
                            skill["name"],
                            skill["description"],
                            skill["author"],
                            skill["version"],
                            skill.get("category", "tech"),
                            skill.get("icon", "fa-code"),
                            skill.get("tags", []),
                            skill.get("downloads", 0),
                            skill.get("stars", 0),
                            json.dumps(skill),
                            skill["skill_index"]
                        ))
                        stats["updated"] += 1
                    else:
                        # 插入
                        cur.execute("""
                            INSERT INTO clawhub_skills (
                                skill_index, skill_id, name, description, author,
                                version, category, icon, tags, downloads, stars, raw_data
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (skill_index) DO NOTHING
                        """, (
                            skill["skill_index"],
                            skill_id,
                            skill["name"],
                            skill["description"],
                            skill["author"],
                            skill["version"],
                            skill.get("category", "tech"),
                            skill.get("icon", "fa-code"),
                            skill.get("tags", []),
                            skill.get("downloads", 0),
                            skill.get("stars", 0),
                            json.dumps(skill)
                        ))
                        stats["inserted"] += 1

                    conn.commit()
                    cur.close()

                logger.info(f"Synced skill: {skill['name']} (#{skill['skill_index']})")
            except Exception as e:
                logger.error(f"Failed to sync skill {skill.get('name')}: {e}")
                stats["errors"].append({"skill": skill.get("name"), "error": str(e)})

        return stats

    def upload_skill_to_tos(self, skill_index: int, skill_data: Dict) -> Optional[Dict]:
        """
        将技能文件上传到 TOS

        Args:
            skill_index: 技能序号
            skill_data: 技能数据

        Returns:
            TOS 上传结果，包含 key, url, size, checksum
        """
        storage = self._get_storage()
        if not storage:
            logger.warning("Storage service not available")
            return None

        try:
            # 生成文件名
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in skill_data["name"])
            filename = f"clawhub-{skill_index:04d}-{safe_name}.json"
            folder = self._clawhub_skills_folder

            # 准备技能数据（包含 manifest 信息）
            skill_content = {
                "manifest": {
                    "skill_index": skill_index,
                    "skill_id": skill_data.get("skill_id", self.generate_skill_id(skill_data["name"])),
                    "name": skill_data["name"],
                    "description": skill_data["description"],
                    "author": skill_data["author"],
                    "version": skill_data.get("version", "1.0.0"),
                    "category": skill_data.get("category", "tech"),
                    "icon": skill_data.get("icon", "fa-code"),
                    "tags": skill_data.get("tags", []),
                    "source": "clawhub",
                    "created_at": datetime.now().isoformat(),
                },
                "content": {
                    # 这里可以存放实际的技能代码
                    "readme": f"# {skill_data['name']}\n\n{skill_data.get('description', '')}",
                    "main.py": "# Skill implementation here",
                }
            }

            # 转换为 JSON bytes
            content_bytes = json.dumps(skill_content, ensure_ascii=False, indent=2).encode("utf-8")

            # 计算 checksum
            checksum = hashlib.sha256(content_bytes).hexdigest()

            # 上传到 TOS
            result = storage.upload(
                file_content=content_bytes,
                folder=folder,
                filename=filename,
                content_type="application/json"
            )

            # 更新数据库
            conn = self._get_db_cursor()
            if conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE clawhub_skills SET
                        tos_key = %s,
                        tos_url = %s,
                        file_size = %s,
                        checksum = %s,
                        is_downloaded = TRUE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE skill_index = %s
                """, (
                    result.key,
                    result.url,
                    result.size,
                    checksum,
                    skill_index
                ))
                conn.commit()
                cur.close()
                conn.close()

            logger.info(f"Uploaded skill {skill_data['name']} to TOS: {result.key}")

            return {
                "key": result.key,
                "url": result.url,
                "size": result.size,
                "checksum": checksum
            }

        except Exception as e:
            logger.error(f"Failed to upload skill to TOS: {e}")
            return None

    def get_clawhub_skill_by_index(self, skill_index: int) -> Optional[Dict]:
        """根据序号获取 ClawHub 技能"""
        conn = self._get_db_cursor()
        if not conn:
            return None

        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM clawhub_skills WHERE skill_index = %s AND is_active = TRUE",
                (skill_index,)
            )
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get skill by index: {e}")
            return None

    def get_clawhub_skill_download_url(self, skill_index: int) -> Optional[str]:
        """
        获取技能下载 URL（签名 URL）

        Args:
            skill_index: 技能序号

        Returns:
            签名下载 URL
        """
        conn = self._get_db_cursor()
        storage = self._get_storage()

        if not conn or not storage:
            return None

        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT tos_key FROM clawhub_skills WHERE skill_index = %s AND is_active = TRUE AND is_downloaded = TRUE",
                (skill_index,)
            )
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row and row["tos_key"]:
                # 生成签名 URL（有效期 1 小时）
                return storage.get_url(row["tos_key"], signed=True, expires_seconds=3600)
            return None
        except Exception as e:
            logger.error(f"Failed to get download URL: {e}")
            return None

    def list_clawhub_skills(
        self,
        locale: str = "zh-CN",
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        列出 ClawHub 技能（从数据库）

        Args:
            locale: 语言设置
            limit: 返回数量
            offset: 偏移量

        Returns:
            技能列表和总数
        """
        conn = self._get_db_cursor()
        if not conn:
            # 返回内置数据
            skills = self._get_builtin_skills()
            if locale == "zh-CN":
                skills = [self.translate_to_chinese(s) for s in skills]
            return {"skills": skills[:limit], "total": len(skills)}

        try:
            cur = conn.cursor()

            # 获取总数
            cur.execute("SELECT COUNT(*) as count FROM clawhub_skills WHERE is_active = TRUE")
            total_row = cur.fetchone()
            total = total_row["count"] if total_row else 0

            # 获取列表
            cur.execute("""
                SELECT skill_index, skill_id, name, description, author, version,
                       category, icon, tags, downloads, stars, tos_url, is_downloaded
                FROM clawhub_skills
                WHERE is_active = TRUE
                ORDER BY skill_index ASC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()

            skills = []
            for row in rows:
                skill = {
                    "skill_index": row["skill_index"],
                    "skill_id": row["skill_id"],
                    "name": row["name"],
                    "description": row["description"],
                    "author": row["author"],
                    "version": row["version"],
                    "category": row["category"],
                    "icon": row["icon"],
                    "tags": row["tags"] or [],
                    "downloads": row["downloads"],
                    "stars": row["stars"],
                    "download_url": row["tos_url"] if row["is_downloaded"] else None,
                    "source": "clawhub",
                }

                # 翻译
                if locale == "zh-CN":
                    skill = self.translate_to_chinese(skill)

                skills.append(skill)

            cur.close()
            conn.close()

            return {"skills": skills, "total": total}

        except Exception as e:
            logger.error(f"Failed to list clawhub skills: {e}")
            if conn:
                conn.close()
            # fallback 到内置数据
            skills = self._get_builtin_skills()
            if locale == "zh-CN":
                skills = [self.translate_to_chinese(s) for s in skills]
            return {"skills": skills[:limit], "total": len(skills)}


# 创建服务实例
recommendations_service = RecommendationsService()
