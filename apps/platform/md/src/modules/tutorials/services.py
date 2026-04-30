"""
技术教程服务层
处理教程相关的业务逻辑
"""

import json
from typing import Optional, Dict, Any, List

from core.db_adapter import get_db_cursor


class TutorialService:
    """教程服务"""

    @staticmethod
    def _select_title_desc(lang: str, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据语言选择标题、描述、内容的辅助方法。

        Args:
            lang: 语言代码 ("zh-CN" 或其他)
            row: 数据库行字典

        Returns:
            包含 title/description/content 的字典
        """
        result = {}

        # 标题：中文直接用，英文回退到中文
        result["title"] = row["title_zh_CN"] if lang == "zh-CN" else (row.get("title_en") or row["title_zh_CN"])

        # 描述：中文直接用，英文回退到中文
        result["description"] = row["description_zh_CN"] if lang == "zh-CN" else (row.get("description_en") or row["description_zh_CN"])

        # 内容（可选字段）
        if "content_zh_CN" in row or "content_en" in row:
            result["content"] = row.get("content_zh_CN") if lang == "zh-CN" else row.get("content_en")

        return result

    @staticmethod
    def _parse_tags(tags_str: Optional[str]) -> List[str]:
        """解析逗号分隔的标签字符串为列表"""
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

    @staticmethod
    def _format_datetime(dt) -> Optional[str]:
        """将 datetime 对象格式化为 ISO 字符串"""
        if dt is None:
            return None
        try:
            return dt.isoformat()
        except AttributeError:
            return str(dt) if dt else None

    # ============================================
    # 公共方法
    # ============================================

    @staticmethod
    def list_tutorials(
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        difficulty: Optional[str] = None,
        featured: Optional[bool] = None,
        is_published: bool = True,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        lang: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        获取教程列表（分页、筛选、搜索）。

        Args:
            category: 工具分类
            subcategory: 子分类
            difficulty: 难度级别
            featured: 是否精选
            is_published: 是否已发布
            page: 页码
            page_size: 每页数量
            search: 搜索关键词
            lang: 语言

        Returns:
            {"success": True, "data": {...}}
        """
        with get_db_cursor() as cur:
            # 构建查询条件
            conditions = ["is_published = %s"]
            params = [is_published]

            if category:
                conditions.append("category = %s")
                params.append(category)

            if subcategory:
                conditions.append("subcategory = %s")
                params.append(subcategory)

            if difficulty:
                conditions.append("difficulty = %s")
                params.append(difficulty)

            if featured is not None:
                conditions.append("featured = %s")
                params.append(featured)

            if search:
                conditions.append(
                    "(title_zh_CN ILIKE %s OR title_en ILIKE %s "
                    "OR description_zh_CN ILIKE %s OR description_en ILIKE %s)"
                )
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

            where_clause = " AND ".join(conditions)

            # 查询总数
            count_query = f"SELECT COUNT(*) as total FROM tutorials WHERE {where_clause}"
            cur.execute(count_query, params)
            total = cur.fetchone()["total"]

            # 查询列表
            offset = (page - 1) * page_size
            list_query = f"""
                SELECT
                    id, tutorial_key, slug,
                    title_zh_CN, title_en,
                    description_zh_CN, description_en,
                    category, subcategory, difficulty, tags,
                    thumbnail, video_url, video_type, video_duration,
                    github_url, documentation_url,
                    view_count, like_count, featured, is_published,
                    created_at, updated_at
                FROM tutorials
                WHERE {where_clause}
                ORDER BY position ASC, created_at DESC
                LIMIT %s OFFSET %s
            """
            cur.execute(list_query, params + [page_size, offset])
            rows = cur.fetchall()

            # 格式化结果
            items = []
            for row in rows:
                localized = TutorialService._select_title_desc(lang, row)
                tags_list = TutorialService._parse_tags(row["tags"])

                items.append({
                    "id": row["id"],
                    "tutorial_key": row["tutorial_key"],
                    "slug": row["slug"],
                    "title": localized["title"],
                    "title_zh_CN": row["title_zh_CN"],
                    "title_en": row["title_en"],
                    "description": localized["description"],
                    "description_zh_CN": row["description_zh_CN"],
                    "description_en": row["description_en"],
                    "category": row["category"],
                    "subcategory": row["subcategory"],
                    "difficulty": row["difficulty"],
                    "tags": tags_list,
                    "thumbnail": row["thumbnail"],
                    "video_url": row["video_url"],
                    "video_type": row["video_type"],
                    "video_duration": row["video_duration"],
                    "github_url": row["github_url"],
                    "documentation_url": row["documentation_url"],
                    "view_count": row["view_count"],
                    "like_count": row["like_count"],
                    "featured": row["featured"],
                    "is_published": row["is_published"],
                    "created_at": TutorialService._format_datetime(row["created_at"]),
                    "updated_at": TutorialService._format_datetime(row["updated_at"]),
                })

            return {
                "success": True,
                "data": {
                    "items": items,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size,
                }
            }

    @staticmethod
    def get_featured(limit: int = 6, lang: str = "zh-CN") -> Dict[str, Any]:
        """
        获取精选教程列表。

        Args:
            limit: 返回数量
            lang: 语言

        Returns:
            {"success": True, "data": {...}}
        """
        with get_db_cursor() as cur:
            query = """
                SELECT
                    id, slug,
                    title_zh_CN, title_en,
                    description_zh_CN, description_en,
                    category, difficulty, thumbnail,
                    video_url, video_duration,
                    view_count, like_count
                FROM tutorials
                WHERE featured = TRUE AND is_published = TRUE
                ORDER BY position ASC, view_count DESC
                LIMIT %s
            """
            cur.execute(query, (limit,))
            rows = cur.fetchall()

            items = []
            for row in rows:
                localized = TutorialService._select_title_desc(lang, row)
                items.append({
                    "id": row["id"],
                    "slug": row["slug"],
                    "title": localized["title"],
                    "description": localized["description"],
                    "category": row["category"],
                    "difficulty": row["difficulty"],
                    "thumbnail": row["thumbnail"],
                    "video_url": row["video_url"],
                    "video_duration": row["video_duration"],
                    "view_count": row["view_count"],
                    "like_count": row["like_count"],
                })

            return {
                "success": True,
                "data": {
                    "items": items,
                    "total": len(items),
                }
            }

    @staticmethod
    def get_categories() -> Dict[str, Any]:
        """
        获取教程分类统计。

        从数据库 GROUP BY category 查询，10 个硬编码分类作为基础。
        数据库中不在硬编码列表中的分类不会被返回。

        Returns:
            {"success": True, "data": {...}}
        """
        with get_db_cursor() as cur:
            query = """
                SELECT category, COUNT(*) as count
                FROM tutorials
                WHERE is_published = TRUE
                GROUP BY category
            """
            cur.execute(query)
            rows = cur.fetchall()

            categories = {
                "claude-code": {"name": "Claude Code", "icon": "\U0001f916", "count": 0},
                "openclaw": {"name": "OpenClaw", "icon": "\U0001f99e", "count": 0},
                "cursor": {"name": "Cursor", "icon": "\u26a1", "count": 0},
                "windsurf": {"name": "Windsurf", "icon": "\U0001f30a", "count": 0},
                "copilot": {"name": "GitHub Copilot", "icon": "\u2708\ufe0f", "count": 0},
                "bolt": {"name": "Bolt.new", "icon": "\u26a1", "count": 0},
                "new": {"name": "v0.dev", "icon": "\U0001f195", "count": 0},
                "codeium": {"name": "Codeium", "icon": "\U0001f48e", "count": 0},
                "tabnine": {"name": "Tabnine", "icon": "9\ufe0f\u20e3", "count": 0},
                "continue": {"name": "Continue", "icon": "\u25b6\ufe0f", "count": 0},
            }

            for row in rows:
                if row["category"] in categories:
                    categories[row["category"]]["count"] = row["count"]

            return {
                "success": True,
                "data": categories,
            }

    @staticmethod
    def get_tutorial(id_or_slug: str, lang: str = "zh-CN") -> Dict[str, Any]:
        """
        获取教程详情（含章节列表），自动递增 view_count。

        支持通过整数 ID 或字符串 slug 查询。

        Args:
            id_or_slug: 教程 ID（数字字符串）或 slug
            lang: 语言

        Returns:
            {"success": True, "data": {...}}

        Raises:
            ValueError: 教程不存在时抛出，由路由层转换为 404
        """
        with get_db_cursor() as cur:
            # 查询教程（支持 ID 或 slug）
            if id_or_slug.isdigit():
                query = "SELECT * FROM tutorials WHERE id = %s"
                cur.execute(query, (int(id_or_slug),))
            else:
                query = "SELECT * FROM tutorials WHERE slug = %s"
                cur.execute(query, (id_or_slug,))

            tutorial = cur.fetchone()

            if not tutorial:
                raise ValueError("教程不存在")

            tutorial_id = tutorial["id"]

            # 增加浏览次数（get_db_cursor 会在 with 块结束时自动 commit）
            update_query = "UPDATE tutorials SET view_count = view_count + 1 WHERE id = %s"
            cur.execute(update_query, (tutorial_id,))

            # 获取章节
            chapter_query = """
                SELECT
                    id, chapter_order, chapter_key,
                    title_zh_CN, title_en,
                    description_zh_CN, description_en,
                    content_zh_CN, content_en,
                    video_url, video_start_time, video_end_time,
                    is_free, code_snippets, attachments
                FROM tutorial_chapters
                WHERE tutorial_id = %s
                ORDER BY chapter_order
            """
            cur.execute(chapter_query, (tutorial_id,))
            chapter_rows = cur.fetchall()

            # 格式化章节数据
            chapter_list = []
            for chapter in chapter_rows:
                localized = TutorialService._select_title_desc(lang, chapter)
                chapter_list.append({
                    "id": chapter["id"],
                    "chapter_order": chapter["chapter_order"],
                    "chapter_key": chapter["chapter_key"],
                    "title": localized["title"],
                    "title_zh_CN": chapter["title_zh_CN"],
                    "title_en": chapter["title_en"],
                    "description": chapter["description_zh_CN"] if lang == "zh-CN" else chapter.get("description_en"),
                    "description_zh_CN": chapter["description_zh_CN"],
                    "description_en": chapter.get("description_en"),
                    "content": chapter.get("content_zh_CN") if lang == "zh-CN" else chapter.get("content_en"),
                    "content_zh_CN": chapter.get("content_zh_CN"),
                    "content_en": chapter.get("content_en"),
                    "video_url": chapter["video_url"],
                    "video_start_time": chapter["video_start_time"],
                    "video_end_time": chapter["video_end_time"],
                    "is_free": chapter["is_free"],
                    "code_snippets": json.loads(chapter["code_snippets"]) if chapter.get("code_snippets") else [],
                    "attachments": json.loads(chapter["attachments"]) if chapter.get("attachments") else [],
                })

            # 解析标签
            tags_list = TutorialService._parse_tags(tutorial.get("tags"))

            # 根据语言选择标题、描述、内容
            localized = TutorialService._select_title_desc(lang, tutorial)

            return {
                "success": True,
                "data": {
                    "id": tutorial["id"],
                    "tutorial_key": tutorial["tutorial_key"],
                    "slug": tutorial["slug"],
                    "title": localized["title"],
                    "title_zh_CN": tutorial["title_zh_CN"],
                    "title_en": tutorial.get("title_en"),
                    "description": localized["description"],
                    "description_zh_CN": tutorial["description_zh_CN"],
                    "description_en": tutorial.get("description_en"),
                    "content": localized.get("content"),
                    "content_zh_CN": tutorial.get("content_zh_CN"),
                    "content_en": tutorial.get("content_en"),
                    "category": tutorial["category"],
                    "subcategory": tutorial.get("subcategory"),
                    "difficulty": tutorial["difficulty"],
                    "tags": tags_list,
                    "thumbnail": tutorial.get("thumbnail"),
                    "video_url": tutorial.get("video_url"),
                    "video_type": tutorial.get("video_type"),
                    "video_duration": tutorial.get("video_duration"),
                    "video_file_size": tutorial.get("video_file_size"),
                    "github_url": tutorial.get("github_url"),
                    "documentation_url": tutorial.get("documentation_url"),
                    "official_website": tutorial.get("official_website"),
                    "view_count": tutorial["view_count"],
                    "like_count": tutorial["like_count"],
                    "featured": tutorial["featured"],
                    "is_pinned": tutorial.get("is_pinned", False),
                    "is_published": tutorial["is_published"],
                    "chapters": chapter_list,
                    "created_at": TutorialService._format_datetime(tutorial.get("created_at")),
                    "updated_at": TutorialService._format_datetime(tutorial.get("updated_at")),
                }
            }

    @staticmethod
    def record_view(tutorial_id: int) -> Dict[str, Any]:
        """
        记录教程浏览次数。

        Args:
            tutorial_id: 教程 ID

        Returns:
            {"success": True, "data": {"view_count": N}}

        Raises:
            ValueError: 教程不存在时抛出
        """
        with get_db_cursor() as cur:
            # 检查教程是否存在
            cur.execute("SELECT id, view_count FROM tutorials WHERE id = %s", (tutorial_id,))
            tutorial = cur.fetchone()

            if not tutorial:
                raise ValueError("教程不存在")

            # 增加浏览次数
            cur.execute(
                "UPDATE tutorials SET view_count = view_count + 1 WHERE id = %s",
                (tutorial_id,)
            )

            return {
                "success": True,
                "data": {
                    "view_count": tutorial["view_count"] + 1,
                }
            }

    @staticmethod
    def like_tutorial(tutorial_id: int) -> Dict[str, Any]:
        """
        点赞教程。

        Args:
            tutorial_id: 教程 ID

        Returns:
            {"success": True, "data": {"like_count": N}}

        Raises:
            ValueError: 教程不存在时抛出
        """
        with get_db_cursor() as cur:
            # 检查教程是否存在
            cur.execute("SELECT id, like_count FROM tutorials WHERE id = %s", (tutorial_id,))
            tutorial = cur.fetchone()

            if not tutorial:
                raise ValueError("教程不存在")

            # 增加点赞数
            cur.execute(
                "UPDATE tutorials SET like_count = like_count + 1 WHERE id = %s",
                (tutorial_id,)
            )

            return {
                "success": True,
                "data": {
                    "like_count": tutorial["like_count"] + 1,
                }
            }
