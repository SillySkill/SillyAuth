"""
Admin Module Services
Business logic for admin operations

Provides services for user management, content moderation,
system statistics, and audit logging
"""

import hashlib
import secrets
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple

from .schemas import (
    UserStatus,
    ContentType,
    ContentAction,
    UserListItem,
    UserDetailsResponse,
    ContentModerationItem,
    SystemStats,
    DashboardData,
    AuditLogEntry,
    AuditLogFilter,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

from src.core.db_adapter import get_db_cursor


# ============================================================================
# User Management Service
# ============================================================================

class UserManagementService:
    """Service for user management operations"""

    @staticmethod
    def _build_user_list_item(row: Dict[str, Any]) -> UserListItem:
        """Convert database row to UserListItem"""
        return UserListItem(
            id=row.get('id', 0),
            username=row.get('username', ''),
            email=row.get('email', ''),
            first_name=row.get('first_name'),
            last_name=row.get('last_name'),
            role=row.get('role', 'user'),
            is_active=row.get('is_active', True),
            is_verified=row.get('is_verified', False),
            created_at=row.get('created_at', datetime.now()),
            last_login_at=row.get('last_login_at')
        )

    def get_users(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[UserListItem], int]:
        """
        Get paginated list of users with optional filters

        Args:
            filters: Optional filter parameters (role, status, search)
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (user list, total count)
        """
        filters = filters or {}
        offset = (page - 1) * limit

        # Build WHERE clause
        conditions = []
        values = []

        if 'role' in filters:
            conditions.append("role = %s")
            values.append(filters['role'])

        if 'status' in filters:
            status = filters['status']
            if status == 'active':
                conditions.append("is_active = TRUE")
            elif status == 'inactive':
                conditions.append("is_active = FALSE")

        if 'search' in filters:
            search_term = f"%{filters['search']}%"
            conditions.append("(username ILIKE %s OR email ILIKE %s)")
            values.append(search_term)

        if 'verified' in filters:
            conditions.append("is_verified = %s")
            values.append(filters['verified'])

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM users {where_clause}"
        with get_db_cursor() as cur:
            cur.execute(count_query, values)
            total = cur.fetchone()['total']

        # Get paginated results
        query = f"""
            SELECT id, username, email, first_name, last_name, role,
                   is_active, is_verified, created_at, last_login_at
            FROM users
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        values.extend([limit, offset])

        with get_db_cursor() as cur:
            cur.execute(query, values)
            rows = cur.fetchall()

        users = [self._build_user_list_item(dict(row)) for row in rows]
        return users, total

    def update_user_status(
        self,
        user_id: int,
        status: UserStatus,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update user account status

        Args:
            user_id: User ID to update
            status: New status
            reason: Optional reason for status change

        Returns:
            True if successful, False otherwise
        """
        # Map status to database values
        is_active = status in [UserStatus.ACTIVE, UserStatus.INACTIVE]

        with get_db_cursor() as cur:
            # Update user status
            cur.execute(
                """
                UPDATE users
                SET is_active = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (is_active, user_id)
            )

            # Log the action in audit log
            cur.execute(
                """
                INSERT INTO audit_logs (admin_id, action, target_type, target_id, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (
                    0,  # Will be updated with actual admin ID in routes
                    f"update_user_status:{status.value}",
                    'user',
                    user_id,
                    str({'reason': reason})
                )
            )

        logger.info(f"User {user_id} status updated to {status.value}")
        return True

    def reset_user_password(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Reset user password to a temporary password

        Args:
            user_id: User ID to reset password for

        Returns:
            Tuple of (success, temporary_password)
        """
        # Generate temporary password
        temp_password = secrets.token_urlsafe(12)
        password_hash = hashlib.sha256(temp_password.encode()).hexdigest()

        with get_db_cursor() as cur:
            # Update password
            cur.execute(
                """
                UPDATE users
                SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (password_hash, user_id)
            )

            # Log the action
            cur.execute(
                """
                INSERT INTO audit_logs (admin_id, action, target_type, target_id, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (
                    0,  # Will be updated with actual admin ID in routes
                    'reset_user_password',
                    'user',
                    user_id,
                    '{"action": "password_reset"}'
                )
            )

        logger.info(f"Password reset for user {user_id}")
        return True, temp_password

    def get_user_details(self, user_id: int) -> Optional[UserDetailsResponse]:
        """
        Get detailed user information

        Args:
            user_id: User ID to get details for

        Returns:
            UserDetailsResponse or None if not found
        """
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT id, username, email, first_name, last_name, role,
                       is_active, is_verified, created_at, last_login_at, avatar_url,
                       metadata
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )
            row = cur.fetchone()

        if not row:
            return None

        return UserDetailsResponse(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            first_name=row.get('first_name'),
            last_name=row.get('last_name'),
            role=row.get('role', 'user'),
            is_active=row.get('is_active', True),
            is_verified=row.get('is_verified', False),
            created_at=row.get('created_at', datetime.now()),
            last_login_at=row.get('last_login_at'),
            avatar_url=row.get('avatar_url'),
            metadata=row.get('metadata')
        )


# ============================================================================
# Content Moderation Service
# ============================================================================

class ContentModerationService:
    """Service for content moderation operations"""

    @staticmethod
    def _build_content_item(row: Dict[str, Any], content_type: str = 'article') -> ContentModerationItem:
        """Convert database row to ContentModerationItem"""
        return ContentModerationItem(
            id=row.get('id', 0),
            type=ContentType(content_type),
            title=row.get('title'),
            content=row.get('content', '')[:200] if row.get('content') else None,
            author_id=row.get('author_id', 0),
            author_username=row.get('author_username', 'unknown'),
            created_at=row.get('created_at', datetime.now()),
            status=row.get('status', 'pending'),
            flags=row.get('flags', 0)
        )

    def get_pending_content(
        self,
        content_type: Optional[ContentType] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ContentModerationItem], int]:
        """
        Get paginated list of pending content for moderation

        Args:
            content_type: Optional filter by content type
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (content list, total count)
        """
        offset = (page - 1) * limit
        items = []

        # For now, we'll use a unified approach
        # In a real implementation, you might have separate tables for different content types
        content_type_value = content_type.value if content_type else None

        with get_db_cursor() as cur:
            if content_type_value == 'article' or content_type_value is None:
                # Get pending articles
                count_query = "SELECT COUNT(*) as total FROM articles WHERE status = 'pending'"
                cur.execute(count_query)
                total = cur.fetchone()['total']

                if total > 0:
                    query = """
                        SELECT a.id, a.title, a.content, a.author_id, u.username as author_username,
                               a.created_at, a.status, COALESCE(a.flags, 0) as flags
                        FROM articles a
                        LEFT JOIN users u ON a.author_id = u.id
                        WHERE a.status = 'pending'
                        ORDER BY a.created_at DESC
                        LIMIT %s OFFSET %s
                    """
                    cur.execute(query, (limit, offset))
                    for row in cur.fetchall():
                        items.append(self._build_content_item(dict(row), 'article'))

            # Add more content types as needed...

        return items, total

    def approve_content(self, content_id: int, content_type: str = 'article') -> bool:
        """
        Approve content

        Args:
            content_id: Content ID to approve
            content_type: Type of content

        Returns:
            True if successful
        """
        with get_db_cursor() as cur:
            if content_type == 'article':
                cur.execute(
                    """
                    UPDATE articles
                    SET status = 'approved', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (content_id,)
                )
            # Add more content types as needed...

            # Log the action
            cur.execute(
                """
                INSERT INTO audit_logs (admin_id, action, target_type, target_id, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (
                    0,
                    'approve_content',
                    content_type,
                    content_id,
                    '{"action": "approved"}'
                )
            )

        logger.info(f"Content {content_id} (type: {content_type}) approved")
        return True

    def reject_content(
        self,
        content_id: int,
        reason: str,
        content_type: str = 'article'
    ) -> bool:
        """
        Reject content

        Args:
            content_id: Content ID to reject
            reason: Rejection reason
            content_type: Type of content

        Returns:
            True if successful
        """
        with get_db_cursor() as cur:
            if content_type == 'article':
                cur.execute(
                    """
                    UPDATE articles
                    SET status = 'rejected', rejection_reason = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (reason, content_id)
                )
            # Add more content types as needed...

            # Log the action
            cur.execute(
                """
                INSERT INTO audit_logs (admin_id, action, target_type, target_id, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (
                    0,
                    'reject_content',
                    content_type,
                    content_id,
                    str({'reason': reason})
                )
            )

        logger.info(f"Content {content_id} (type: {content_type}) rejected: {reason}")
        return True


# ============================================================================
# System Service
# ============================================================================

class SystemService:
    """Service for system statistics and dashboard data"""

    def get_system_stats(self) -> SystemStats:
        """
        Get comprehensive system statistics

        Returns:
            SystemStats object
        """
        stats = SystemStats()

        with get_db_cursor() as cur:
            # User statistics
            cur.execute("SELECT COUNT(*) as total FROM users")
            stats.total_users = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) as active FROM users WHERE is_active = TRUE")
            stats.active_users = cur.fetchone()['active']

            cur.execute(
                "SELECT COUNT(*) as new_users FROM users WHERE created_at >= CURRENT_DATE"
            )
            stats.new_users_today = cur.fetchone()['new_users']

            cur.execute(
                "SELECT COUNT(*) as new_users FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'"
            )
            stats.new_users_this_week = cur.fetchone()['new_users']

            cur.execute(
                "SELECT COUNT(*) as new_users FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'"
            )
            stats.new_users_this_month = cur.fetchone()['new_users']

            # Content statistics
            cur.execute("SELECT COUNT(*) as total FROM articles")
            stats.total_content = cur.fetchone()['total']

            cur.execute(
                "SELECT COUNT(*) as pending FROM articles WHERE status = 'pending'"
            )
            stats.pending_moderation = cur.fetchone()['pending']

            # Storage and bandwidth (these would typically come from a monitoring system)
            stats.storage_used_gb = 0.0
            stats.bandwidth_gb = 0.0

            # API calls (would come from a metrics system)
            stats.api_calls_today = 0

            # Error rate (would come from monitoring)
            stats.error_rate = 0.0

            # Uptime (would come from monitoring)
            stats.uptime_hours = 0.0

        return stats

    def get_dashboard_data(self) -> DashboardData:
        """
        Get comprehensive dashboard data including charts and metrics

        Returns:
            DashboardData object
        """
        stats = self.get_system_stats()

        user_growth = []
        content_growth = []
        revenue_history = []
        recent_activity = []
        top_content = []

        with get_db_cursor() as cur:
            # Get user growth over last 30 days
            cur.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users
                WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            for row in cur.fetchall():
                user_growth.append({
                    'date': row['date'].isoformat(),
                    'count': row['count']
                })

            # Get recent activity
            cur.execute("""
                SELECT action, target_type, target_id, details, timestamp
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            for row in cur.fetchall():
                recent_activity.append({
                    'action': row['action'],
                    'target_type': row['target_type'],
                    'target_id': row['target_id'],
                    'details': row['details'],
                    'timestamp': row['timestamp'].isoformat()
                })

            # Get top performing content
            cur.execute("""
                SELECT id, title, 'article' as type
                FROM articles
                WHERE status = 'approved'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            for row in cur.fetchall():
                top_content.append({
                    'id': row['id'],
                    'title': row['title'],
                    'type': row['type']
                })

        # Get active modules from plugin manager
        active_modules = []
        try:
            from src.core.plugin_manager import PluginManager
            # Note: This would need proper integration with the app
        except ImportError:
            pass

        return DashboardData(
            stats=stats,
            user_growth=user_growth,
            content_growth=content_growth,
            revenue_history=revenue_history,
            recent_activity=recent_activity,
            top_content=top_content,
            active_modules=active_modules
        )


# ============================================================================
# Audit Log Service
# ============================================================================

class AuditLogService:
    """Service for audit logging operations"""

    def __init__(self, enabled: bool = True):
        """
        Initialize audit log service

        Args:
            enabled: Whether audit logging is enabled
        """
        self.enabled = enabled

    def log_action(
        self,
        admin_id: int,
        action: str,
        target: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Log an admin action to the audit log

        Args:
            admin_id: Admin user ID
            action: Action performed
            target: Target description
            details: Additional details as dict
            ip_address: Admin IP address
            user_agent: Admin user agent string

        Returns:
            True if logged successfully
        """
        if not self.enabled:
            return True

        # Parse target to extract type and id
        target_type = None
        target_id = None
        if target:
            parts = target.split(':')
            if len(parts) >= 2:
                target_type = parts[0]
                try:
                    target_id = int(parts[1])
                except ValueError:
                    pass

        try:
            with get_db_cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_logs (admin_id, action, target_type, target_id, target, details, ip_address, user_agent, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """,
                    (
                        admin_id,
                        action,
                        target_type,
                        target_id,
                        target,
                        str(details) if details else None,
                        ip_address,
                        user_agent
                    )
                )
            return True
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")
            return False

    def get_audit_logs(
        self,
        filters: Optional[AuditLogFilter] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[AuditLogEntry], int]:
        """
        Get paginated audit logs with optional filters

        Args:
            filters: Optional filter parameters
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (log list, total count)
        """
        filters = filters or AuditLogFilter()
        offset = (page - 1) * limit

        # Build WHERE clause
        conditions = []
        values = []

        if filters.admin_id:
            conditions.append("al.admin_id = %s")
            values.append(filters.admin_id)

        if filters.action:
            conditions.append("al.action LIKE %s")
            values.append(f"%{filters.action}%")

        if filters.target_type:
            conditions.append("al.target_type = %s")
            values.append(filters.target_type)

        if filters.start_date:
            conditions.append("al.timestamp >= %s")
            values.append(filters.start_date)

        if filters.end_date:
            conditions.append("al.timestamp <= %s")
            values.append(filters.end_date)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM audit_logs al
            {where_clause}
        """
        with get_db_cursor() as cur:
            cur.execute(count_query, values)
            total = cur.fetchone()['total']

        # Get paginated results
        query = f"""
            SELECT al.id, al.admin_id, u.username as admin_username, al.action,
                   al.target_type, al.target_id, al.target, al.details,
                   al.ip_address, al.user_agent, al.timestamp
            FROM audit_logs al
            LEFT JOIN users u ON al.admin_id = u.id
            {where_clause}
            ORDER BY al.timestamp DESC
            LIMIT %s OFFSET %s
        """
        values.extend([limit, offset])

        with get_db_cursor() as cur:
            cur.execute(query, values)
            rows = cur.fetchall()

        logs = []
        for row in rows:
            logs.append(AuditLogEntry(
                id=row['id'],
                admin_id=row['admin_id'],
                admin_username=row.get('admin_username', 'unknown'),
                action=row['action'],
                target_type=row['target_type'],
                target_id=row['target_id'],
                target=row['target'],
                details=eval(row['details']) if row['details'] else None,
                ip_address=row['ip_address'],
                user_agent=row['user_agent'],
                timestamp=row['timestamp']
            ))

        return logs, total


# ============================================================================
# Singleton Instances
# ============================================================================

user_management_service = UserManagementService()
content_moderation_service = ContentModerationService()
system_service = SystemService()
audit_log_service = AuditLogService(enabled=True)
