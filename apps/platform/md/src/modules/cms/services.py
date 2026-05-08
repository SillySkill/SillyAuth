"""
CMS Module Services
Business logic for content management operations

Provides article and category management services
"""

import os
import logging
import math
import re
import ast
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .schemas import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListItem,
    ArticleList,
    ArticleSearchResult,
    FeaturedArticlesResponse,
    AuthorInfo,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryList,
    CategoryWithArticles,
    ArticleType,
    ArticleStatus,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

from core.db_adapter import get_db_cursor

# Module configuration defaults
MODULE_CONFIG = {
    "max_article_length": 100000,
    "allowed_content_types": ["markdown", "html"],
    "featured_articles_limit": 10
}

def generate_slug(title: str) -> str:
    """
    Generate URL-friendly slug from title.

    Args:
        title: Article title

    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove non-alphanumeric characters (except hyphens)
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


# ============================================================================
# Article Service
# ============================================================================

def _parse_metadata(metadata):
    """Clean metadata, handling surrogate pairs from broken JSON encoding."""
    if isinstance(metadata, str):
        if not metadata.strip():
            return {}
        # Try json.loads first (standard JSON from json.dumps)
        try:
            result = json.loads(metadata)
            if isinstance(result, dict):
                return _clean_surrogates(result)
            return result
        except Exception:
            pass
        # Fall back to ast.literal_eval (for Python literal strings)
        try:
            result = ast.literal_eval(metadata)
            if isinstance(result, dict):
                return _clean_surrogates(result)
            return result
        except Exception:
            pass
        return {}
    return metadata if isinstance(metadata, dict) else {}


def _clean_surrogates(obj):
    """Recursively fix surrogate pairs in strings within dicts/lists."""
    if isinstance(obj, str):
        return obj.encode('utf-8', errors='surrogateescape').decode('utf-8', errors='replace')
    elif isinstance(obj, list):
        return [_clean_surrogates(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: _clean_surrogates(v) for k, v in obj.items()}
    return obj


class ArticleService:
    """Service for managing articles."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Article Service.

        Args:
            config: Module configuration dictionary
        """
        self._config = config or MODULE_CONFIG
        self._articles: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        self._article_likes: Dict[int, set] = {}  # article_id -> set of user_ids

    def _validate_content(self, content: str) -> bool:
        """Validate article content length."""
        max_length = self._config.get("max_article_length", 100000)
        return len(content) <= max_length

    def create_article(self, author_id: int, data: ArticleCreate) -> Optional[ArticleResponse]:
        """
        Create a new article.

        Args:
            author_id: Author's user ID
            data: Article creation data

        Returns:
            Created article response or None if failed
        """
        # Validate content length
        if not self._validate_content(data.content):
            logger.warning(f"Article content exceeds max length: {len(data.content)}")
            return None

        # Generate slug
        base_slug = generate_slug(data.title)
        slug = base_slug

        # Check for duplicate slug and append number if needed
        counter = 1
        with get_db_cursor() as cur:
            while True:
                cur.execute(
                    "SELECT id FROM articles WHERE slug = %s",
                    (slug,)
                )
                if not cur.fetchone():
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1

        # Get author info
        author = self._get_author_info(author_id)

        # Create article
        article_id = self._next_id
        self._next_id += 1

        now = datetime.utcnow()
        article_data = {
            "id": article_id,
            "title": data.title,
            "content": data.content,
            "type": data.type.value,
            "slug": slug,
            "excerpt": data.excerpt,
            "cover_image": data.cover_image,
            "tags": data.tags,
            "featured": data.featured,
            "status": data.status.value,
            "view_count": 0,
            "like_count": 0,
            "category_id": data.category_id,
            "author_id": author_id,
            "metadata": data.metadata,
            "created_at": now,
            "updated_at": now,
            "published_at": now if data.status == ArticleStatus.PUBLISHED else None
        }

        # Store in memory for testing
        self._articles[article_id] = article_data

        # Insert into database
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO articles (
                        title, content, type, slug, excerpt, cover_image,
                        tags, featured, status, view_count, like_count,
                        category_id, author_id, metadata, created_at, updated_at, published_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    article_data["title"],
                    article_data["content"],
                    article_data["type"],
                    article_data["slug"],
                    article_data["excerpt"],
                    article_data["cover_image"],
                    ",".join(article_data["tags"]) if article_data["tags"] else None,
                    article_data["featured"],
                    article_data["status"],
                    article_data["view_count"],
                    article_data["like_count"],
                    article_data["category_id"],
                    article_data["author_id"],
                    str(article_data["metadata"]),
                    article_data["created_at"],
                    article_data["updated_at"],
                    article_data["published_at"]
                ))
                result = cur.fetchone()
                if result:
                    article_data["id"] = result["id"]
                    article_id = result["id"]
        except Exception as e:
            logger.debug(f"Database insert skipped: {e}")

        # Get category name if category_id is set
        category_name = None
        if article_data["category_id"]:
            category_name = self._get_category_name(article_data["category_id"])

        return ArticleResponse(
            id=article_id,
            title=article_data["title"],
            content=article_data["content"],
            type=ArticleType(article_data["type"]),
            slug=article_data["slug"],
            excerpt=article_data["excerpt"],
            cover_image=article_data["cover_image"],
            tags=article_data["tags"],
            featured=article_data["featured"],
            status=ArticleStatus(article_data["status"]),
            view_count=article_data["view_count"],
            like_count=article_data["like_count"],
            category_id=article_data["category_id"],
            category_name=category_name,
            author=author,
            metadata=article_data["metadata"],
            created_at=article_data["created_at"],
            updated_at=article_data["updated_at"],
            published_at=article_data["published_at"]
        )

    def update_article(self, article_id: int, data: ArticleUpdate) -> Optional[ArticleResponse]:
        """
        Update an existing article.

        Args:
            article_id: Article ID
            data: Article update data

        Returns:
            Updated article response or None if not found
        """
        # Get existing article
        article = self._get_article_by_id(article_id)
        if not article:
            return None

        # Build update fields
        update_fields = []
        values = []

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                if field == "type":
                    value = value.value
                elif field == "status":
                    value = value.value
                elif field == "tags":
                    value = ",".join(value) if value else None
                update_fields.append(f"{field} = %s")
                values.append(value)

        if not update_fields:
            return None

        update_fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        values.append(article_id)

        # If status changed to published, set published_at
        if data.status and data.status == ArticleStatus.PUBLISHED:
            update_fields.append("published_at = %s")
            values.insert(-1, datetime.utcnow())

        # Update in database
        try:
            with get_db_cursor() as cur:
                cur.execute(f"""
                    UPDATE articles
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """, values)
        except Exception as e:
            logger.debug(f"Database update skipped: {e}")

        # Update in memory cache
        if article_id in self._articles:
            for field, value in update_data.items():
                if field == "type":
                    self._articles[article_id][field] = value.value
                elif field == "status":
                    self._articles[article_id][field] = value.value
                elif field == "tags":
                    self._articles[article_id][field] = value if value else []
                else:
                    self._articles[article_id][field] = value
            self._articles[article_id]["updated_at"] = datetime.utcnow()

        return self.get_article(article_id)

    def delete_article(self, article_id: int) -> bool:
        """
        Delete an article.

        Args:
            article_id: Article ID

        Returns:
            True if deleted, False if not found
        """
        # Check if article exists
        article = self._get_article_by_id(article_id)
        if not article:
            return False

        # Delete from database
        try:
            with get_db_cursor() as cur:
                cur.execute("DELETE FROM articles WHERE id = %s", (article_id,))
        except Exception as e:
            logger.debug(f"Database delete skipped: {e}")

        # Delete from memory cache
        if article_id in self._articles:
            del self._articles[article_id]

        # Clean up likes
        if article_id in self._article_likes:
            del self._article_likes[article_id]

        return True

    def get_article(self, article_id: int, increment_views: bool = True) -> Optional[ArticleResponse]:
        """
        Get an article by ID with optional view count increment.

        Args:
            article_id: Article ID
            increment_views: Whether to increment view count

        Returns:
            Article response or None if not found
        """
        article = self._get_article_by_id(article_id)
        if not article:
            return None

        # Increment view count
        if increment_views:
            try:
                with get_db_cursor() as cur:
                    cur.execute(
                        "UPDATE articles SET view_count = view_count + 1 WHERE id = %s",
                        (article_id,)
                    )
            except Exception as e:
                logger.debug(f"Database update skipped: {e}")

            if article_id in self._articles:
                self._articles[article_id]["view_count"] += 1
                article = self._articles[article_id]

        # Get category name
        category_name = None
        if article.get("category_id"):
            category_name = self._get_category_name(article["category_id"])

        # Get author info
        author = self._get_author_info(article.get("author_id"))

        # Parse tags
        tags = article.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        # Parse metadata
        metadata = _parse_metadata(article.get("metadata", {}))

        return ArticleResponse(
            id=article["id"],
            title=article["title"],
            content=article["content"],
            type=ArticleType(article["type"]),
            slug=article["slug"],
            excerpt=article.get("excerpt"),
            cover_image=article.get("cover_image"),
            tags=tags,
            featured=article.get("featured", False),
            status=ArticleStatus(article["status"]),
            view_count=article.get("view_count", 0),
            like_count=article.get("like_count", 0),
            category_id=article.get("category_id"),
            category_name=category_name,
            author=author,
            metadata=metadata,
            created_at=article["created_at"],
            updated_at=article["updated_at"],
            published_at=article.get("published_at")
        )

    def list_articles(
        self,
        category_id: Optional[int] = None,
        tag: Optional[str] = None,
        author_id: Optional[int] = None,
        article_type: Optional[ArticleType] = None,
        status: Optional[ArticleStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ArticleListItem], int]:
        """
        List articles with filtering and pagination.

        Args:
            category_id: Filter by category ID
            tag: Filter by tag
            author_id: Filter by author ID
            article_type: Filter by article type
            status: Filter by status (default: published only)
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (article list, total count)
        """
        if status is None:
            status = ArticleStatus.PUBLISHED

        articles = []
        total = 0

        try:
            with get_db_cursor() as cur:
                # Build query conditions
                conditions = ["status = %s"]
                params = [status.value]

                if category_id is not None:
                    conditions.append("category_id = %s")
                    params.append(category_id)

                if tag:
                    conditions.append("tags LIKE %s")
                    params.append(f"%{tag}%")

                if author_id is not None:
                    conditions.append("author_id = %s")
                    params.append(author_id)

                if article_type:
                    conditions.append("type = %s")
                    params.append(article_type.value)

                # Count total
                count_query = f"SELECT COUNT(*) as total FROM articles WHERE {' AND '.join(conditions)}"
                cur.execute(count_query, params)
                total = cur.fetchone()["total"]

                # Get paginated results
                offset = (page - 1) * limit
                list_query = f"""
                    SELECT a.*, c.name as category_name, u.username as author_username, u.avatar_url as author_avatar
                    FROM articles a
                    LEFT JOIN categories c ON a.category_id = c.id
                    LEFT JOIN users u ON a.author_id = u.id
                    WHERE {' AND '.join(conditions)}
                    ORDER BY a.created_at DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(list_query, params + [limit, offset])
                rows = cur.fetchall()

                for row in rows:
                    tags = row.get("tags", "")
                    if isinstance(tags, str):
                        tags = [t.strip() for t in tags.split(",") if t.strip()]

                    articles.append(ArticleListItem(
                        id=row["id"],
                        title=row["title"],
                        type=ArticleType(row["type"]),
                        slug=row["slug"],
                        excerpt=row.get("excerpt"),
                        cover_image=row.get("cover_image"),
                        tags=tags,
                        featured=row.get("featured", False),
                        view_count=row.get("view_count", 0),
                        like_count=row.get("like_count", 0),
                        category_id=row.get("category_id"),
                        category_name=row.get("category_name"),
                        author_username=row.get("author_username"),
                        author_avatar=row.get("author_avatar"),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"]
                    ))

        except Exception as e:
            logger.debug(f"Database query skipped: {e}")
            # Fall back to in-memory cache
            for article in self._articles.values():
                if article["status"] != status.value:
                    continue
                if category_id and article.get("category_id") != category_id:
                    continue
                if tag and tag not in article.get("tags", []):
                    continue
                if author_id and article.get("author_id") != author_id:
                    continue
                if article_type and article["type"] != article_type.value:
                    continue
                total += 1
                if total > offset and len(articles) < limit:
                    category_name = self._get_category_name(article.get("category_id")) if article.get("category_id") else None
                    author = self._get_author_info(article.get("author_id"))
                    articles.append(ArticleListItem(
                        id=article["id"],
                        title=article["title"],
                        type=ArticleType(article["type"]),
                        slug=article["slug"],
                        excerpt=article.get("excerpt"),
                        cover_image=article.get("cover_image"),
                        tags=article.get("tags", []),
                        featured=article.get("featured", False),
                        view_count=article.get("view_count", 0),
                        like_count=article.get("like_count", 0),
                        category_id=article.get("category_id"),
                        category_name=category_name,
                        author_username=author.username if author else None,
                        author_avatar=author.avatar_url if author else None,
                        created_at=article["created_at"],
                        updated_at=article["updated_at"]
                    ))

        return articles, total

    def search_articles(
        self,
        query: str,
        page: int = 1,
        limit: int = 20
    ) -> ArticleSearchResult:
        """
        Search articles by keyword.

        Args:
            query: Search query string
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Search result with matching articles
        """
        search_pattern = f"%{query}%"
        articles = []
        total = 0

        try:
            with get_db_cursor() as cur:
                # Search in title, content, and tags
                conditions = [
                    "status = %s",
                    "(title ILIKE %s OR content ILIKE %s OR tags ILIKE %s)"
                ]
                params = [ArticleStatus.PUBLISHED.value, search_pattern, search_pattern, search_pattern]

                # Count total
                count_query = f"SELECT COUNT(*) as total FROM articles WHERE {' AND '.join(conditions)}"
                cur.execute(count_query, params)
                total = cur.fetchone()["total"]

                # Get paginated results
                offset = (page - 1) * limit
                list_query = f"""
                    SELECT a.*, c.name as category_name, u.username as author_username, u.avatar_url as author_avatar
                    FROM articles a
                    LEFT JOIN categories c ON a.category_id = c.id
                    LEFT JOIN users u ON a.author_id = u.id
                    WHERE {' AND '.join(conditions)}
                    ORDER BY a.view_count DESC, a.created_at DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(list_query, params + [limit, offset])
                rows = cur.fetchall()

                for row in rows:
                    tags = row.get("tags", "")
                    if isinstance(tags, str):
                        tags = [t.strip() for t in tags.split(",") if t.strip()]

                    articles.append(ArticleListItem(
                        id=row["id"],
                        title=row["title"],
                        type=ArticleType(row["type"]),
                        slug=row["slug"],
                        excerpt=row.get("excerpt"),
                        cover_image=row.get("cover_image"),
                        tags=tags,
                        featured=row.get("featured", False),
                        view_count=row.get("view_count", 0),
                        like_count=row.get("like_count", 0),
                        category_id=row.get("category_id"),
                        category_name=row.get("category_name"),
                        author_username=row.get("author_username"),
                        author_avatar=row.get("author_avatar"),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"]
                    ))

        except Exception as e:
            logger.debug(f"Database search skipped: {e}")

        pages = math.ceil(total / limit) if total > 0 else 1

        return ArticleSearchResult(
            items=articles,
            total=total,
            query=query,
            page=page,
            limit=limit,
            pages=pages
        )

    def like_article(self, user_id: int, article_id: int) -> Optional[int]:
        """
        Like an article.

        Args:
            user_id: User ID
            article_id: Article ID

        Returns:
            New like count or None if article not found
        """
        article = self._get_article_by_id(article_id)
        if not article:
            return None

        # Check if already liked
        if article_id not in self._article_likes:
            self._article_likes[article_id] = set()

        if user_id in self._article_likes[article_id]:
            # Unlike
            self._article_likes[article_id].discard(user_id)
            like_change = -1
        else:
            # Like
            self._article_likes[article_id].add(user_id)
            like_change = 1

        # Update in database
        try:
            with get_db_cursor() as cur:
                cur.execute(
                    "UPDATE articles SET like_count = like_count + %s WHERE id = %s",
                    (like_change, article_id)
                )
        except Exception as e:
            logger.debug(f"Database update skipped: {e}")

        # Update in memory
        if article_id in self._articles:
            self._articles[article_id]["like_count"] = article.get("like_count", 0) + like_change

        # Return new count
        new_count = article.get("like_count", 0) + like_change
        return max(0, new_count)

    def get_featured(self, limit: int = 10) -> FeaturedArticlesResponse:
        """
        Get featured articles.

        Args:
            limit: Maximum number of articles to return

        Returns:
            Featured articles response
        """
        limit = min(limit, self._config.get("featured_articles_limit", 10))
        articles = []

        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT a.*, c.name as category_name, u.username as author_username, u.avatar_url as author_avatar
                    FROM articles a
                    LEFT JOIN categories c ON a.category_id = c.id
                    LEFT JOIN users u ON a.author_id = u.id
                    WHERE a.featured = TRUE AND a.status = %s
                    ORDER BY a.view_count DESC, a.created_at DESC
                    LIMIT %s
                """, (ArticleStatus.PUBLISHED.value, limit))
                rows = cur.fetchall()

                for row in rows:
                    tags = row.get("tags", "")
                    if isinstance(tags, str):
                        tags = [t.strip() for t in tags.split(",") if t.strip()]

                    articles.append(ArticleListItem(
                        id=row["id"],
                        title=row["title"],
                        type=ArticleType(row["type"]),
                        slug=row["slug"],
                        excerpt=row.get("excerpt"),
                        cover_image=row.get("cover_image"),
                        tags=tags,
                        featured=True,
                        view_count=row.get("view_count", 0),
                        like_count=row.get("like_count", 0),
                        category_id=row.get("category_id"),
                        category_name=row.get("category_name"),
                        author_username=row.get("author_username"),
                        author_avatar=row.get("author_avatar"),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"]
                    ))

        except Exception as e:
            logger.debug(f"Database query skipped: {e}")

        return FeaturedArticlesResponse(
            items=articles,
            total=len(articles)
        )

    def get_hero_slides(self, limit: int = 5) -> list:
        """
        Get featured articles as hero slides for homepage.

        Args:
            limit: Maximum number of slides

        Returns:
            List of slide dicts with type, src, title, title_parts, description, badge, actions
        """
        slides = []
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT a.title, a.slug, a.excerpt, a.cover_image, a.type,
                           a.metadata,
                           u.username as author_username, u.avatar_url as author_avatar
                    FROM articles a
                    LEFT JOIN users u ON a.author_id = u.id
                    WHERE a.is_featured = TRUE AND a.status = 'published'
                    ORDER BY a.view_count DESC, a.created_at DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                for row in rows:
                    metadata = _parse_metadata(row.get("metadata", {}))

                    article_type = row.get("type", "article")
                    slide_type = "video" if article_type == "video" else "image"

                    title_parts = metadata.get("title_parts", None)
                    if not title_parts:
                        title_parts = [{"text": row["title"], "gradient": False, "break": False}]

                    slide = {
                        "type": slide_type,
                        "src": row.get("cover_image") or "/static/img/hero-default.svg",
                        "poster": metadata.get("poster", ""),
                        "title": row["title"],
                        "title_parts": title_parts,
                        "description": row.get("excerpt") or row["title"],
                        "badge": metadata.get("badge", "精选"),
                        "actions": metadata.get("actions", [
                            {
                                "url": f"/articles/{row['slug']}",
                                "style": "btn-primary btn-lg",
                                "icon": "fas fa-book-open",
                                "label": "阅读更多"
                            }
                        ])
                    }
                    slides.append(slide)
        except Exception as e:
            logger.debug(f"Failed to get hero slides: {e}")
        return slides

    def _format_stat(self, count: int, suffix: str = "+") -> str:
        """Format stat value: e.g., 10000 -> '10K+', 2500 -> '2.5K+'."""
        if count >= 10000:
            val = count / 1000
            if val == int(val):
                return f"{int(val)}K+"
            return f"{val:.1f}K+"
        elif count >= 1000:
            return f"{count/1000:.1f}K+"
        return f"{count}{suffix}"

    def get_homepage_stats(self) -> list:
        """
        Get aggregate statistics for homepage.

        Queries multiple tables to compute platform-wide stats.

        Returns:
            List of stat dicts with value and label
        """
        stats = []
        try:
            with get_db_cursor() as cur:
                # Skills count
                try:
                    cur.execute("SELECT COUNT(*) as count FROM skills WHERE status = 'approved' AND is_deleted = FALSE")
                    skills_count = cur.fetchone()["count"]
                except Exception:
                    skills_count = 0

                # Distinct vendors (authors with approved skills)
                try:
                    cur.execute("SELECT COUNT(DISTINCT author_id) as count FROM skills WHERE status = 'approved' AND is_deleted = FALSE")
                    vendors_count = cur.fetchone()["count"]
                except Exception:
                    vendors_count = 0

                # Teams count
                try:
                    cur.execute("SELECT COUNT(*) as count FROM teams")
                    teams_count = cur.fetchone()["count"]
                except Exception:
                    teams_count = 0

                # AI accuracy from config/system_settings
                ai_accuracy = "99.9%"
                try:
                    cur.execute("SELECT value FROM system_settings WHERE key = 'ai_accuracy'")
                    row = cur.fetchone()
                    if row:
                        ai_accuracy = row["value"]
                except Exception:
                    pass

            if skills_count > 0:
                stats.append({"value": self._format_stat(skills_count), "label": "Skills"})
            if vendors_count > 0:
                stats.append({"value": self._format_stat(vendors_count), "label": "认证供应商"})
            if teams_count > 0:
                stats.append({"value": self._format_stat(teams_count), "label": "企业团队"})
            stats.append({"value": ai_accuracy, "label": "AI 审核准确率"})
        except Exception as e:
            logger.debug(f"Failed to get homepage stats: {e}")
        return stats

    def get_homepage_features(self) -> list:
        """
        Get platform features for homepage.

        Queries articles with type='feature' and extracts icon/items from metadata.

        Returns:
            List of feature dicts with icon, title, description, items
        """
        features = []
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT a.title, a.summary, a.metadata
                    FROM articles a
                    WHERE a.type = 'feature' AND a.status = 'published'
                    ORDER BY a.view_count DESC, a.created_at DESC
                    LIMIT 3
                """)
                rows = cur.fetchall()
                for row in rows:
                    metadata = _parse_metadata(row.get("metadata", {}))
                    features.append({
                        "icon": metadata.get("icon", "🚀"),
                        "title": row["title"],
                        "description": row.get("summary", ""),
                        "items": metadata.get("items", [])
                    })
        except Exception as e:
            logger.debug(f"Failed to get homepage features: {e}")
        return features

    def get_homepage_vendors(self, limit: int = 8) -> list:
        """
        Get vendor/provider list for homepage.

        Queries distinct skill authors from the database.

        Args:
            limit: Maximum number of vendors to return

        Returns:
            List of vendor dicts with tiered badge, avatar, name, stats
        """
        vendors = []
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT u.id, u.username, u.avatar_url,
                        COUNT(s.id) as skills_count,
                        COALESCE(SUM(s.download_count), 0) as total_downloads
                    FROM skills s
                    JOIN users u ON s.author_id = u.id
                    WHERE s.is_deleted = FALSE AND s.status = 'approved'
                    GROUP BY u.id, u.username, u.avatar_url
                    ORDER BY total_downloads DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                for row in rows:
                    total_downloads = row["total_downloads"]
                    # Tiered badge based on download count
                    if total_downloads >= 50000:
                        badge_icon = "fas fa-crown"
                        badge_label = "金牌供应商"
                        badge_color = "var(--accent)"
                    elif total_downloads >= 10000:
                        badge_icon = "fas fa-award"
                        badge_label = "优质供应商"
                        badge_color = "var(--primary-light)"
                    else:
                        badge_icon = "fas fa-check-circle"
                        badge_label = "认证供应商"
                        badge_color = "var(--secondary)"

                    # Compute rating based on downloads
                    rating = round(min(5.0, 4.0 + (total_downloads / 100000) * 1.0), 1)

                    vendors.append({
                        "badge_icon": badge_icon,
                        "badge_label": badge_label,
                        "badge_color": badge_color,
                        "avatar": row.get("avatar_url") or "/static/img/avatar-default.svg",
                        "name": row["username"],
                        "title": "AI Skills 开发者",
                        "bio": f"发布了 {row['skills_count']} 个 Skills",
                        "skills_count": row["skills_count"],
                        "downloads": total_downloads,
                        "rating": rating
                    })
        except Exception as e:
            logger.debug(f"Failed to get vendors: {e}")
        return vendors

    def get_homepage_categories(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Get learning center doc categories for the homepage."""
        categories = []
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT id, name, slug, description, icon, doc_count
                    FROM categories
                    WHERE category_type = 'doc'
                    ORDER BY doc_count DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                for row in rows:
                    categories.append({
                        "icon": row.get("icon") or "📖",
                        "name": row["name"],
                        "desc": row.get("description") or "",
                        "count": row.get("doc_count", 0),
                        "url": f"/docs/{row['slug']}" if row.get("slug") else "/docs"
                    })
        except Exception as e:
            logger.debug(f"Failed to get homepage categories: {e}")
        return categories

    def get_homepage_tutorials(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get featured tutorials for the homepage learning center."""
        tutorials = []
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, slug, category, duration, level,
                           icon, gradient, cover_image, view_count, like_count
                    FROM tutorials
                    WHERE status = 'published'
                    ORDER BY view_count DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                for row in rows:
                    tutorials.append({
                        "title": row["title"],
                        "desc": row.get("description") or "",
                        "category": row.get("category") or "教程",
                        "duration": row.get("duration") or "",
                        "level": row.get("level") or "初级",
                        "icon": row.get("icon") or "📖",
                        "gradient": row.get("gradient") or "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        "url": f"/docs/tutorial/{row['id']}"
                    })
        except Exception as e:
            logger.debug(f"Failed to get homepage tutorials: {e}")
        return tutorials

    def _get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Get article by ID from database or cache."""
        # Try cache first
        if article_id in self._articles:
            return self._articles[article_id]

        # Try database
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
                row = cur.fetchone()
                if row:
                    return row
        except Exception as e:
            logger.debug(f"Database query skipped: {e}")

        return None

    def _get_author_info(self, author_id: int) -> Optional[AuthorInfo]:
        """Get author information by ID."""
        if not author_id:
            return None

        try:
            with get_db_cursor() as cur:
                cur.execute(
                    "SELECT id, username, avatar_url FROM users WHERE id = %s",
                    (author_id,)
                )
                user = cur.fetchone()
                if user:
                    return AuthorInfo(
                        id=user["id"],
                        username=user["username"],
                        avatar_url=user.get("avatar_url"),
                        display_name=user.get("display_name") or user["username"]
                    )
        except Exception as e:
            logger.debug(f"Database query skipped: {e}")

        return None

    def _get_category_name(self, category_id: int) -> Optional[str]:
        """Get category name by ID."""
        if not category_id:
            return None

        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
                row = cur.fetchone()
                if row:
                    return row["name"]
        except Exception as e:
            logger.debug(f"Database query skipped: {e}")

        return None


# ============================================================================
# Category Service
# ============================================================================

class CategoryService:
    """Service for managing categories."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Category Service.

        Args:
            config: Module configuration dictionary
        """
        self._config = config or MODULE_CONFIG
        self._categories: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def create_category(self, data: CategoryCreate) -> CategoryResponse:
        """
        Create a new category.

        Args:
            data: Category creation data

        Returns:
            Created category response
        """
        category_id = self._next_id
        self._next_id += 1

        now = datetime.utcnow()
        category_data = {
            "id": category_id,
            "name": data.name,
            "slug": data.slug,
            "description": data.description,
            "parent_id": data.parent_id,
            "icon": data.icon,
            "color": data.color,
            "article_count": 0,
            "created_at": now,
            "updated_at": now
        }

        # Store in memory for testing
        self._categories[category_id] = category_data

        # Insert into database
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO categories (name, slug, description, parent_id, icon, color, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    category_data["name"],
                    category_data["slug"],
                    category_data["description"],
                    category_data["parent_id"],
                    category_data["icon"],
                    category_data["color"],
                    category_data["created_at"],
                    category_data["updated_at"]
                ))
                result = cur.fetchone()
                if result:
                    category_data["id"] = result["id"]
                    category_id = result["id"]
        except Exception as e:
            logger.debug(f"Database insert skipped: {e}")

        return CategoryResponse(
            id=category_id,
            name=category_data["name"],
            slug=category_data["slug"],
            description=category_data["description"],
            parent_id=category_data["parent_id"],
            icon=category_data["icon"],
            color=category_data["color"],
            article_count=category_data["article_count"],
            created_at=category_data["created_at"],
            updated_at=category_data["updated_at"]
        )

    def update_category(self, category_id: int, data: CategoryUpdate) -> Optional[CategoryResponse]:
        """
        Update an existing category.

        Args:
            category_id: Category ID
            data: Category update data

        Returns:
            Updated category response or None if not found
        """
        # Check if category exists
        if category_id not in self._categories:
            try:
                with get_db_cursor() as cur:
                    cur.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
                    row = cur.fetchone()
                    if not row:
                        return None
                    self._categories[category_id] = row
            except Exception as e:
                logger.debug(f"Database query skipped: {e}")
                return None

        # Build update fields
        update_fields = []
        values = []

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                values.append(value)

        if not update_fields:
            return self.get_category(category_id)

        update_fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        values.append(category_id)

        # Update in database
        try:
            with get_db_cursor() as cur:
                cur.execute(f"""
                    UPDATE categories
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """, values)
        except Exception as e:
            logger.debug(f"Database update skipped: {e}")

        # Update in memory cache
        if category_id in self._categories:
            for field, value in update_data.items():
                self._categories[category_id][field] = value
            self._categories[category_id]["updated_at"] = datetime.utcnow()

        return self.get_category(category_id)

    def delete_category(self, category_id: int) -> bool:
        """
        Delete a category.

        Args:
            category_id: Category ID

        Returns:
            True if deleted, False if not found
        """
        # Check if category exists
        if category_id not in self._categories:
            try:
                with get_db_cursor() as cur:
                    cur.execute("SELECT id FROM categories WHERE id = %s", (category_id,))
                    if not cur.fetchone():
                        return False
            except Exception as e:
                logger.debug(f"Database query skipped: {e}")
                return False

        # Delete from database
        try:
            with get_db_cursor() as cur:
                # Set parent_id to null for child categories
                cur.execute(
                    "UPDATE articles SET category_id = NULL WHERE category_id = %s",
                    (category_id,)
                )
                cur.execute(
                    "UPDATE categories SET parent_id = NULL WHERE parent_id = %s",
                    (category_id,)
                )
                cur.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        except Exception as e:
            logger.debug(f"Database delete skipped: {e}")

        # Delete from memory cache
        if category_id in self._categories:
            del self._categories[category_id]

        return True

    def get_category(self, category_id: int) -> Optional[CategoryResponse]:
        """
        Get a category by ID.

        Args:
            category_id: Category ID

        Returns:
            Category response or None if not found
        """
        # Try cache first
        if category_id in self._categories:
            data = self._categories[category_id]
            return self._build_category_response(data)

        # Try database
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT c.*, COUNT(a.id) as article_count
                    FROM categories c
                    LEFT JOIN articles a ON c.id = a.category_id AND a.status = 'published'
                    WHERE c.id = %s
                    GROUP BY c.id
                """, (category_id,))
                row = cur.fetchone()
                if row:
                    return self._build_category_response(row)
        except Exception as e:
            logger.debug(f"Database query skipped: {e}")

        return None

    def list_categories(
        self,
        parent_id: Optional[int] = None,
        include_count: bool = True
    ) -> CategoryList:
        """
        List all categories.

        Args:
            parent_id: Filter by parent ID (None for root categories)
            include_count: Whether to include article counts

        Returns:
            Category list response
        """
        categories = []

        try:
            with get_db_cursor() as cur:
                if include_count:
                    if parent_id is None:
                        cur.execute("""
                            SELECT c.*, COUNT(a.id) as article_count
                            FROM categories c
                            LEFT JOIN articles a ON c.id = a.category_id AND a.status = 'published'
                            WHERE c.parent_id IS NULL
                            GROUP BY c.id
                            ORDER BY c.name
                        """)
                    else:
                        cur.execute("""
                            SELECT c.*, COUNT(a.id) as article_count
                            FROM categories c
                            LEFT JOIN articles a ON c.id = a.category_id AND a.status = 'published'
                            WHERE c.parent_id = %s
                            GROUP BY c.id
                            ORDER BY c.name
                        """, (parent_id,))
                else:
                    if parent_id is None:
                        cur.execute("SELECT * FROM categories WHERE parent_id IS NULL ORDER BY name")
                    else:
                        cur.execute(
                            "SELECT * FROM categories WHERE parent_id = %s ORDER BY name",
                            (parent_id,)
                        )

                rows = cur.fetchall()
                for row in rows:
                    categories.append(self._build_category_response(row))

        except Exception as e:
            logger.debug(f"Database query skipped: {e}")
            # Fall back to in-memory cache
            for cat in self._categories.values():
                if cat.get("parent_id") == parent_id:
                    categories.append(self._build_category_response(cat))

        return CategoryList(
            items=categories,
            total=len(categories)
        )

    def get_category_with_articles(
        self,
        category_id: int,
        page: int = 1,
        limit: int = 20
    ) -> Optional[CategoryWithArticles]:
        """
        Get category with its articles.

        Args:
            category_id: Category ID
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Category with articles or None if not found
        """
        category = self.get_category(category_id)
        if not category:
            return None

        article_service = ArticleService(self._config)
        articles, total = article_service.list_articles(
            category_id=category_id,
            page=page,
            limit=limit
        )

        pages = math.ceil(total / limit) if total > 0 else 1

        return CategoryWithArticles(
            category=category,
            articles=ArticleList(
                items=articles,
                total=total,
                page=page,
                limit=limit,
                pages=pages
            )
        )

    def _build_category_response(self, data: Dict[str, Any]) -> CategoryResponse:
        """Build category response from data."""
        return CategoryResponse(
            id=data["id"],
            name=data["name"],
            slug=data["slug"],
            description=data.get("description"),
            parent_id=data.get("parent_id"),
            icon=data.get("icon"),
            color=data.get("color"),
            article_count=data.get("article_count", 0),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )


# ============================================================================
# Service Instances
# ============================================================================

article_service = ArticleService()
category_service = CategoryService()
