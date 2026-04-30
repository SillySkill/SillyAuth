"""
Skills Module Services
Business logic for Skills management operations

Provides CRUD operations, publishing, and statistics for skills
"""

import hashlib
import logging
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# ============================================================================
# Mock Data (for demonstration when database is unavailable)
# ============================================================================

MOCK_SKILLS = [
    {
        'id': 1, 'skill_id': 'jwt-auth-system-abc123', 'name': 'JWT 认证与授权系统',
        'description': '完整的 JWT 认证解决方案，支持用户注册、登录、密码重置、权限管理等核心功能。包含访问令牌和刷新令牌机制，确保系统安全。',
        'author_id': 1, 'author_username': '张明', 'author_avatar': None,
        'category': 'tech', 'type': 'free', 'version': '1.2.0', 'status': 'approved',
        'tags': '认证,JWT,安全,用户管理', 'price': 0, 'is_featured': True,
        'view_count': 15000, 'download_count': 2300, 'favorite_count': 856,
        'rating_avg': 4.9, 'rating_count': 89,
        'created_at': '2026-03-01', 'updated_at': '2026-03-15', 'published_at': '2026-03-02'
    },
    {
        'id': 2, 'skill_id': 'react-ui-components-def456', 'name': 'React UI 组件库系统',
        'description': '基于 React + TypeScript 的现代化组件库，包含 50+ 高质量组件。支持主题定制、深色模式、响应式设计。',
        'author_id': 2, 'author_username': '王磊', 'author_avatar': None,
        'category': 'tech', 'type': 'free', 'version': '2.0.0', 'status': 'approved',
        'tags': 'React,TypeScript,UI组件,前端', 'price': 0, 'is_featured': True,
        'view_count': 20000, 'download_count': 3200, 'favorite_count': 1100,
        'rating_avg': 4.8, 'rating_count': 120,
        'created_at': '2026-02-15', 'updated_at': '2026-03-10', 'published_at': '2026-02-16'
    },
    {
        'id': 3, 'skill_id': 'prd-template-ghi789', 'name': '产品需求文档 (PRD) 模板集',
        'description': '专业的 PRD 撰写模板，涵盖需求背景、目标用户、功能规格、竞品分析、数据指标等完整模块。',
        'author_id': 3, 'author_username': '李婷', 'author_avatar': None,
        'category': 'product', 'type': 'free', 'version': '1.0.0', 'status': 'approved',
        'tags': 'PRD,产品文档,模板,需求管理', 'price': 0, 'is_featured': False,
        'view_count': 12000, 'download_count': 1800, 'favorite_count': 624,
        'rating_avg': 4.7, 'rating_count': 56,
        'created_at': '2026-02-01', 'updated_at': '2026-02-28', 'published_at': '2026-02-02'
    },
    {
        'id': 4, 'skill_id': 'user-growth-hacks-jkl012', 'name': '用户增长黑客实战手册',
        'description': '系统化的用户增长方法论，涵盖获客、激活、留存、变现、推荐全流程。提供大量实战案例。',
        'author_id': 4, 'author_username': '陈静', 'author_avatar': None,
        'category': 'marketing', 'type': 'free', 'version': '1.5.0', 'status': 'approved',
        'tags': '增长,AARRR,运营,用户', 'price': 0, 'is_featured': False,
        'view_count': 8000, 'download_count': 1200, 'favorite_count': 398,
        'rating_avg': 4.5, 'rating_count': 45,
        'created_at': '2026-01-20', 'updated_at': '2026-02-20', 'published_at': '2026-01-21'
    },
    {
        'id': 5, 'skill_id': 'redis-cache-architecture-mno345', 'name': 'Redis 高性能缓存架构',
        'description': '基于 Redis 的分布式缓存解决方案，包含缓存策略设计、数据一致性保证、集群部署方案。',
        'author_id': 1, 'author_username': '张明', 'author_avatar': None,
        'category': 'tech', 'type': 'commercial', 'version': '1.1.0', 'status': 'approved',
        'tags': 'Redis,缓存,分布式,架构', 'price': 99, 'is_featured': True,
        'view_count': 18000, 'download_count': 2800, 'favorite_count': 934,
        'rating_avg': 4.9, 'rating_count': 102,
        'created_at': '2026-03-05', 'updated_at': '2026-03-18', 'published_at': '2026-03-06'
    },
    {
        'id': 6, 'skill_id': 'social-media-strategy-pqr678', 'name': '社交媒体运营策略指南',
        'description': '全方位的社交媒体运营方案，覆盖抖音、小红书、视频号等主流平台。',
        'author_id': 3, 'author_username': '李婷', 'author_avatar': None,
        'category': 'marketing', 'type': 'commercial', 'version': '1.0.0', 'status': 'approved',
        'tags': '社交媒体,运营,抖音,小红书', 'price': 199, 'is_featured': False,
        'view_count': 10000, 'download_count': 1500, 'favorite_count': 520,
        'rating_avg': 4.8, 'rating_count': 78,
        'created_at': '2026-02-25', 'updated_at': '2026-03-12', 'published_at': '2026-02-26'
    },
    {
        'id': 7, 'skill_id': 'b2b-saas-growth-stu901', 'name': 'B2B SaaS 增长策略框架',
        'description': '专为 B2B SaaS 产品设计的增长框架，包含 PLG 产品驱动增长、客户成功体系。',
        'author_id': 3, 'author_username': '李婷', 'author_avatar': None,
        'category': 'product', 'type': 'commercial', 'version': '1.0.0', 'status': 'approved',
        'tags': 'SaaS,B2B,增长,PLG', 'price': 149, 'is_featured': False,
        'view_count': 6000, 'download_count': 980, 'favorite_count': 312,
        'rating_avg': 4.7, 'rating_count': 34,
        'created_at': '2026-02-10', 'updated_at': '2026-02-25', 'published_at': '2026-02-11'
    },
    {
        'id': 8, 'skill_id': 'microservice-patterns-vwx234', 'name': '微服务架构设计模式',
        'description': '企业级微服务架构设计方案，包含服务拆分策略、API 网关设计、服务发现与配置中心。',
        'author_id': 1, 'author_username': '张明', 'author_avatar': None,
        'category': 'tech', 'type': 'commercial', 'version': '2.1.0', 'status': 'approved',
        'tags': '微服务,架构,Docker,K8s', 'price': 299, 'is_featured': True,
        'view_count': 9000, 'download_count': 1100, 'favorite_count': 456,
        'rating_avg': 5.0, 'rating_count': 67,
        'created_at': '2026-03-08', 'updated_at': '2026-03-20', 'published_at': '2026-03-09'
    },
    {
        'id': 9, 'skill_id': 'figma-design-system-yza567', 'name': 'Figma 设计组件库规范',
        'description': '完整的 Figma 设计规范，包含组件命名、样式系统、设计令牌等。帮助团队保持设计一致性。',
        'author_id': 2, 'author_username': '王磊', 'author_avatar': None,
        'category': 'design', 'type': 'free', 'version': '1.0.0', 'status': 'approved',
        'tags': 'Figma,设计,UI,规范', 'price': 0, 'is_featured': False,
        'view_count': 14000, 'download_count': 2100, 'favorite_count': 780,
        'rating_avg': 4.6, 'rating_count': 89,
        'created_at': '2026-01-25', 'updated_at': '2026-02-15', 'published_at': '2026-01-26'
    },
    {
        'id': 10, 'skill_id': 'data-visualization-bcd890', 'name': '数据分析可视化报表',
        'description': '基于 ECharts 的数据可视化报表模板，支持折线图、柱状图、饼图、地图等多种图表类型。',
        'author_id': 4, 'author_username': '陈静', 'author_avatar': None,
        'category': 'design', 'type': 'free', 'version': '1.2.0', 'status': 'approved',
        'tags': '数据可视化,ECharts,报表,图表', 'price': 0, 'is_featured': False,
        'view_count': 11000, 'download_count': 1900, 'favorite_count': 645,
        'rating_avg': 4.7, 'rating_count': 78,
        'created_at': '2026-02-05', 'updated_at': '2026-02-28', 'published_at': '2026-02-06'
    },
    {
        'id': 11, 'skill_id': 'devops-pipeline-efg123', 'name': '企业级 DevOps 流水线',
        'description': '完整的 DevOps 流水线配置，包含 GitLab CI/CD、Docker、Kubernetes 自动化部署方案。',
        'author_id': 1, 'author_username': '张明', 'author_avatar': None,
        'category': 'tech', 'type': 'commercial', 'version': '1.5.0', 'status': 'approved',
        'tags': 'DevOps,CI/CD,Docker,K8s', 'price': 199, 'is_featured': True,
        'view_count': 12000, 'download_count': 1600, 'favorite_count': 534,
        'rating_avg': 4.8, 'rating_count': 91,
        'created_at': '2026-03-01', 'updated_at': '2026-03-15', 'published_at': '2026-03-02'
    },
    {
        'id': 12, 'skill_id': 'ux-research-template-hij456', 'name': 'UX 用户研究模板集',
        'description': '专业的用户研究文档模板，包含用户访谈、问卷调查、可用性测试等研究方法。',
        'author_id': 2, 'author_username': '王磊', 'author_avatar': None,
        'category': 'design', 'type': 'free', 'version': '1.0.0', 'status': 'approved',
        'tags': 'UX,用户研究,设计,模板', 'price': 0, 'is_featured': False,
        'view_count': 7500, 'download_count': 1350, 'favorite_count': 456,
        'rating_avg': 4.5, 'rating_count': 45,
        'created_at': '2026-02-12', 'updated_at': '2026-02-28', 'published_at': '2026-02-13'
    },
]

# ============================================================================
# Configuration
# ============================================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "sillymd",
    "user": "sillyAdmin",
    "password": ""
}


def get_db_config() -> Dict[str, Any]:
    """Get database configuration from .env"""
    from core.config import get_db_config as get_config
    db_cfg = get_config()
    return {
        "host": db_cfg.host,
        "port": db_cfg.port,
        "database": db_cfg.database,
        "user": db_cfg.user,
        "password": db_cfg.password
    }


def get_db_cursor():
    """Get database cursor with auto-commit"""
    try:
        from server.api.database import get_db_cursor as server_get_db_cursor
        return server_get_db_cursor(get_db_config())
    except ImportError:
        # Fallback: use psycopg2 directly
        import psycopg2
        from psycopg2.extras import RealDictCursor

        config = get_db_config()
        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"]
        )
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=RealDictCursor)
        return cur


# ============================================================================
# Skill Service
# ============================================================================

class SkillService:
    """Service class for skill management operations"""

    @staticmethod
    def generate_skill_id(name: str) -> str:
        """Generate a unique skill_id from name"""
        # Convert name to lowercase, replace spaces with hyphens
        base_id = name.lower().replace(' ', '-')
        # Remove invalid characters
        base_id = ''.join(c if c.isalnum() or c in '-_' else '' for c in base_id)
        # Add random suffix for uniqueness
        suffix = secrets.token_hex(4)
        return f"{base_id[:40]}-{suffix}"

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_skill_by_id(self, skill_id: int) -> Optional[Dict[str, Any]]:
        """
        Get skill by internal ID

        Args:
            skill_id: Skill internal ID

        Returns:
            Skill dict or None
        """
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT s.*, u.username as author_username, u.avatar_url as author_avatar
                FROM skills s
                JOIN users u ON s.author_id = u.id
                WHERE s.id = %s AND s.is_deleted = FALSE
            """, (skill_id,))
            return cur.fetchone()

    def get_skill_by_skill_id(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """
        Get skill by skill_id (external identifier)

        Args:
            skill_id: Skill external identifier

        Returns:
            Skill dict or None
        """
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT s.*, u.username as author_username, u.avatar_url as author_avatar
                FROM skills s
                JOIN users u ON s.author_id = u.id
                WHERE s.skill_id = %s AND s.is_deleted = FALSE
            """, (skill_id,))
            return cur.fetchone()

    def create_skill(
        self,
        author_id: int,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new skill

        Args:
            author_id: Author user ID
            data: Skill creation data

        Returns:
            Created skill dict or None if failed
        """
        # Generate skill_id if not provided
        skill_id = data.get('skill_id')
        if not skill_id:
            skill_id = self.generate_skill_id(data['name'])

        # Check if skill_id already exists
        existing = self.get_skill_by_skill_id(skill_id)
        if existing:
            logger.warning(f"Skill ID already exists: {skill_id}")
            return None

        # Compute content hash
        content_hash = self.compute_content_hash(data.get('code_content', ''))

        # Prepare license types as JSONB
        license_types = data.get('license_types')
        if license_types:
            license_types = '["' + '","'.join(license_types) + '"]'
        else:
            license_types = '[]'

        try:
            with get_db_cursor() as cur:
                # Insert skill
                cur.execute("""
                    INSERT INTO skills (
                        skill_id, name, description, author_id, category, type,
                        version, status, code_content, content_hash, price,
                        license_types, tags, is_deleted
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE
                    )
                    RETURNING id, skill_id, name, category, type, version, status,
                              price, created_at, updated_at
                """, (
                    skill_id,
                    data['name'],
                    data.get('description'),
                    author_id,
                    data['category'],
                    data.get('type', 'free'),
                    data.get('version', '1.0.0'),
                    'draft',
                    data.get('code_content', ''),
                    content_hash,
                    data.get('price', 0),
                    license_types,
                    ','.join(data.get('tags', [])) if data.get('tags') else ''
                ))

                skill = cur.fetchone()

                # Create initial version record
                cur.execute("""
                    INSERT INTO skill_versions (
                        skill_id, version, content, content_hash, commit_message, author_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                """, (
                    skill['id'],
                    data.get('version', '1.0.0'),
                    data.get('code_content', ''),
                    content_hash,
                    'Initial version',
                    author_id
                ))

                # Handle tags
                if data.get('tags'):
                    for tag_name in data['tags']:
                        # Insert or get tag
                        cur.execute("""
                            INSERT INTO tags (name, usage_count)
                            VALUES (%s, 1)
                            ON CONFLICT (name) DO UPDATE SET usage_count = tags.usage_count + 1
                            RETURNING id
                        """, (tag_name,))
                        tag_row = cur.fetchone()

                        # Link tag to skill
                        cur.execute("""
                            INSERT INTO skill_tags (skill_id, tag_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """, (skill['id'], tag_row['id']))

                logger.info(f"Skill created: {skill_id} by user {author_id}")
                return skill

        except Exception as e:
            logger.error(f"Failed to create skill: {str(e)}")
            return None

    def update_skill(
        self,
        skill_id: int,
        author_id: int,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing skill

        Args:
            skill_id: Skill internal ID
            author_id: User ID (for authorization check)
            data: Update data

        Returns:
            Updated skill dict or None if failed
        """
        # Check if skill exists and user is the author
        existing = self.get_skill_by_id(skill_id)
        if not existing:
            logger.warning(f"Skill not found: {skill_id}")
            return None

        if existing['author_id'] != author_id:
            logger.warning(f"User {author_id} not authorized to update skill {skill_id}")
            return None

        # Build update query dynamically
        update_fields = []
        values = []

        allowed_fields = [
            'name', 'description', 'category', 'type', 'price',
            'repo_url', 'tags'
        ]

        for field in allowed_fields:
            if field in data and data[field] is not None:
                if field == 'tags':
                    # Handle tags separately
                    continue
                update_fields.append(f"{field} = %s")
                values.append(data[field])

        # Handle content update
        content_hash = None
        if 'code_content' in data and data['code_content'] is not None:
            content_hash = self.compute_content_hash(data['code_content'])
            update_fields.append("content_hash = %s")
            values.append(content_hash)

            # Create new version
            new_version = data.get('version', existing['version'])
            cur = None
            try:
                with get_db_cursor() as cur:
                    cur.execute("""
                        INSERT INTO skill_versions (
                            skill_id, version, content, content_hash, commit_message, author_id
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        skill_id,
                        new_version,
                        data['code_content'],
                        content_hash,
                        data.get('commit_message', 'Update'),
                        author_id
                    ))
            except Exception as e:
                logger.error(f"Failed to create version: {str(e)}")

        # Handle license_types
        if 'license_types' in data:
            license_types = data['license_types']
            if license_types:
                license_types = '["' + '","'.join(license_types) + '"]'
            else:
                license_types = '[]'
            update_fields.append("license_types = %s")
            values.append(license_types)

        if not update_fields:
            return existing

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(skill_id)

        query = f"""
            UPDATE skills
            SET {', '.join(update_fields)}
            WHERE id = %s AND is_deleted = FALSE
            RETURNING *
        """

        try:
            with get_db_cursor() as cur:
                cur.execute(query, values)
                updated_skill = cur.fetchone()

                # Handle tags update
                if 'tags' in data and data['tags'] is not None:
                    # Remove existing tags
                    cur.execute("DELETE FROM skill_tags WHERE skill_id = %s", (skill_id,))

                    # Add new tags
                    for tag_name in data['tags']:
                        cur.execute("""
                            INSERT INTO tags (name, usage_count)
                            VALUES (%s, 1)
                            ON CONFLICT (name) DO UPDATE SET usage_count = tags.usage_count + 1
                            RETURNING id
                        """, (tag_name,))
                        tag_row = cur.fetchone()
                        cur.execute("""
                            INSERT INTO skill_tags (skill_id, tag_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """, (skill_id, tag_row['id']))

                logger.info(f"Skill updated: {skill_id} by user {author_id}")
                return updated_skill

        except Exception as e:
            logger.error(f"Failed to update skill: {str(e)}")
            return None

    def delete_skill(self, skill_id: int, author_id: int) -> bool:
        """
        Soft delete a skill

        Args:
            skill_id: Skill internal ID
            author_id: User ID (for authorization check)

        Returns:
            True if deleted, False otherwise
        """
        existing = self.get_skill_by_id(skill_id)
        if not existing:
            return False

        if existing['author_id'] != author_id:
            logger.warning(f"User {author_id} not authorized to delete skill {skill_id}")
            return False

        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    UPDATE skills
                    SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (skill_id,))

                logger.info(f"Skill deleted: {skill_id} by user {author_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to delete skill: {str(e)}")
            return False

    def publish_skill(self, skill_id: int, author_id: int) -> Optional[Dict[str, Any]]:
        """
        Publish a skill (change status to reviewing)

        Args:
            skill_id: Skill internal ID
            author_id: User ID (for authorization check)

        Returns:
            Updated skill dict or None if failed
        """
        existing = self.get_skill_by_id(skill_id)
        if not existing:
            return None

        if existing['author_id'] != author_id:
            return None

        if existing['status'] not in ['draft', 'rejected']:
            logger.warning(f"Cannot publish skill in status: {existing['status']}")
            return None

        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    UPDATE skills
                    SET status = 'reviewing', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND is_deleted = FALSE
                    RETURNING *
                """, (skill_id,))

                skill = cur.fetchone()
                logger.info(f"Skill published: {skill_id} by user {author_id}")
                return skill

        except Exception as e:
            logger.error(f"Failed to publish skill: {str(e)}")
            return None

    def unpublish_skill(self, skill_id: int, author_id: int) -> Optional[Dict[str, Any]]:
        """
        Unpublish a skill (revert to draft status)

        Args:
            skill_id: Skill internal ID
            author_id: User ID (for authorization check)

        Returns:
            Updated skill dict or None if failed
        """
        existing = self.get_skill_by_id(skill_id)
        if not existing:
            return None

        if existing['author_id'] != author_id:
            return None

        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    UPDATE skills
                    SET status = 'draft', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND is_deleted = FALSE
                    RETURNING *
                """, (skill_id,))

                skill = cur.fetchone()
                logger.info(f"Skill unpublished: {skill_id} by user {author_id}")
                return skill

        except Exception as e:
            logger.error(f"Failed to unpublish skill: {str(e)}")
            return None

    def list_skills(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        type: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        status: str = 'approved',
        lang: str = 'en'
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List skills with filtering and pagination

        Args:
            category: Filter by category
            tag: Filter by tag
            search: Search keyword
            type: Filter by type (free/commercial)
            page: Page number (1-indexed)
            limit: Items per page
            status: Filter by status
            lang: Language code for localized fields (en/zh/ja/ko/de/ru)

        Returns:
            Tuple of (skills list, total count)
        """
        offset = (page - 1) * limit

        # Build query conditions
        conditions = ["s.is_deleted = FALSE"]
        params = []

        if status:
            conditions.append("s.status = %s")
            params.append(status)

        if category:
            conditions.append("s.category = %s")
            params.append(category)

        if type:
            conditions.append("s.type = %s")
            params.append(type)

        if search:
            # Search in both original and translated fields
            lang_name = f"s.name_{lang}" if lang != 'en' else "s.name"
            lang_desc = f"s.description_{lang}" if lang != 'en' else "s.description"
            conditions.append(f"(s.name ILIKE %s OR s.description ILIKE %s OR {lang_name} ILIKE %s OR {lang_desc} ILIKE %s)")
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

        if tag:
            conditions.append("""
                s.id IN (
                    SELECT st.skill_id FROM skill_tags st
                    JOIN tags t ON st.tag_id = t.id
                    WHERE t.name = %s
                )
            """)
            params.append(tag)

        where_clause = " AND ".join(conditions)

        # Build localized field selection
        name_field = f"COALESCE(s.name_{lang}, s.name) as display_name" if lang != 'en' else "s.name as display_name"
        desc_field = f"COALESCE(s.description_{lang}, s.description) as display_description" if lang != 'en' else "s.description as display_description"

        try:
            with get_db_cursor() as cur:
                # Get total count
                count_query = f"""
                    SELECT COUNT(*) as total
                    FROM skills s
                    WHERE {where_clause}
                """
                cur.execute(count_query, params)
                total = cur.fetchone()['total']

                # Get skills with localized fields
                query = f"""
                    SELECT s.*, u.username as author_username, u.avatar_url as author_avatar,
                           {name_field}, {desc_field}
                    FROM skills s
                    JOIN users u ON s.author_id = u.id
                    WHERE {where_clause}
                    ORDER BY s.created_at DESC
                    LIMIT %s OFFSET %s
                """
                params.extend([limit, offset])

                cur.execute(query, params)
                skills = cur.fetchall()

                return skills, total

        except Exception as e:
            logger.error(f"Failed to list skills: {str(e)}")
            # Return mock data for demonstration
            return MOCK_SKILLS[offset:offset+limit], len(MOCK_SKILLS)

    def get_skill_stats(self, skill_id: int) -> Optional[Dict[str, Any]]:
        """
        Get skill statistics

        Args:
            skill_id: Skill internal ID

        Returns:
            Statistics dict or None if skill not found
        """
        existing = self.get_skill_by_id(skill_id)
        if not existing:
            return None

        try:
            with get_db_cursor() as cur:
                # Get comment count
                cur.execute("""
                    SELECT COUNT(*) as comment_count
                    FROM skill_comments
                    WHERE skill_id = %s AND is_deleted = FALSE
                """, (skill_id,))
                comment_count = cur.fetchone()['comment_count']

                return {
                    'skill_id': skill_id,
                    'view_count': existing['view_count'],
                    'download_count': existing['download_count'],
                    'favorite_count': existing['favorite_count'],
                    'rating_avg': float(existing['rating_avg']) if existing['rating_avg'] else 0.0,
                    'rating_count': existing['rating_count'],
                    'total_comments': comment_count
                }

        except Exception as e:
            logger.error(f"Failed to get skill stats: {str(e)}")
            return None

    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories with skill counts

        Returns:
            List of category dicts
        """
        categories = [
            {'key': 'tech', 'name': '技术', 'name_en': 'Tech', 'description': '技术相关 Skills'},
            {'key': 'product', 'name': '产品', 'name_en': 'Product', 'description': '产品相关 Skills'},
            {'key': 'design', 'name': '设计', 'name_en': 'Design', 'description': '设计相关 Skills'},
            {'key': 'marketing', 'name': '市场', 'name_en': 'Marketing', 'description': '市场相关 Skills'},
            {'key': 'ops', 'name': '运营', 'name_en': 'Operations', 'description': '运营相关 Skills'},
        ]

        try:
            with get_db_cursor() as cur:
                for cat in categories:
                    cur.execute("""
                        SELECT COUNT(*) as count
                        FROM skills
                        WHERE category = %s AND is_deleted = FALSE AND status = 'approved'
                    """, (cat['key'],))
                    cat['skill_count'] = cur.fetchone()['count']

                return categories

        except Exception as e:
            logger.error(f"Failed to get categories: {str(e)}")
            # Calculate skill counts from mock data
            for cat in categories:
                cat['skill_count'] = len([s for s in MOCK_SKILLS if s['category'] == cat['key']])
            return categories

    def increment_view_count(self, skill_id: int) -> bool:
        """
        Increment skill view count

        Args:
            skill_id: Skill internal ID

        Returns:
            True if successful
        """
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    UPDATE skills
                    SET view_count = view_count + 1
                    WHERE id = %s
                """, (skill_id,))
                return True

        except Exception as e:
            logger.error(f"Failed to increment view count: {str(e)}")
            return False

    def increment_download_count(self, skill_id: int) -> bool:
        """
        Increment skill download count

        Args:
            skill_id: Skill internal ID

        Returns:
            True if successful
        """
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    UPDATE skills
                    SET download_count = download_count + 1
                    WHERE id = %s
                """, (skill_id,))
                return True

        except Exception as e:
            logger.error(f"Failed to increment download count: {str(e)}")
            return False

    def get_skill_versions(self, skill_id: int) -> List[Dict[str, Any]]:
        """
        Get skill version history

        Args:
            skill_id: Skill internal ID

        Returns:
            List of version dicts
        """
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT version, content_hash, commit_message, created_at
                    FROM skill_versions
                    WHERE skill_id = %s
                    ORDER BY created_at DESC
                """, (skill_id,))
                return cur.fetchall()

        except Exception as e:
            logger.error(f"Failed to get skill versions: {str(e)}")
            return []


# Singleton instance
skill_service = SkillService()
