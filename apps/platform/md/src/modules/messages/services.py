"""
Messages Module Services
Business logic for messaging operations

Provides message sending, retrieval, thread management, and notification services
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from .schemas import (
    MessageCreate,
    MessageResponse,
    NotificationCreate,
    NotificationResponse,
    CreateConversationRequest,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "sillymd"),
    "user": os.getenv("DB_USER", "sillyAdmin"),
    "password": os.getenv("DB_PASSWORD", "")
}

# Module configuration defaults
MAX_MESSAGE_LENGTH = 5000
MAX_ATTACHMENT_SIZE_MB = 10
RETENTION_DAYS = 90


def get_db_cursor():
    """Get database cursor"""
    from server.api.database import get_db_cursor
    return get_db_cursor(DB_CONFIG)


# ============================================================================
# Message Service
# ============================================================================

class MessageService:
    """Service class for message operations"""

    @staticmethod
    def _build_message_response(row: dict, current_user_id: Optional[int] = None) -> MessageResponse:
        """
        Build MessageResponse from database row

        Args:
            row: Database row dictionary
            current_user_id: Current user ID for checking ownership

        Returns:
            MessageResponse object
        """
        is_own = current_user_id is not None and row.get('sender_id') == current_user_id

        return MessageResponse(
            id=row['id'],
            sender_id=row.get('sender_id'),
            sender_username=row.get('sender_username'),
            sender_avatar=row.get('sender_avatar'),
            recipient_id=row.get('recipient_id'),
            recipient_username=row.get('recipient_username'),
            content=row['content'],
            type=row.get('type', 'user'),
            read=row.get('read', False),
            read_at=row.get('read_at'),
            attachments=json.loads(row['attachments']) if row.get('attachments') else None,
            created_at=row['created_at'],
            is_own=is_own
        )

    def send_message(
        self,
        sender_id: int,
        recipient_id: int,
        content: str,
        msg_type: str = "user",
        attachments: Optional[List[dict]] = None
    ) -> Optional[MessageResponse]:
        """
        Send a message from one user to another

        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            content: Message content
            msg_type: Message type (system, user, admin)
            attachments: Optional list of attachments

        Returns:
            MessageResponse or None if failed
        """
        # Validate content length
        if len(content) > MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long from user {sender_id}: {len(content)} chars")
            return None

        # Validate recipient exists
        with get_db_cursor() as cur:
            cur.execute("SELECT id, username FROM users WHERE id = %s", (recipient_id,))
            recipient = cur.fetchone()
            if not recipient:
                logger.warning(f"Recipient {recipient_id} not found")
                return None

            # Validate sender exists
            cur.execute("SELECT id, username FROM users WHERE id = %s", (sender_id,))
            sender = cur.fetchone()
            if not sender:
                logger.warning(f"Sender {sender_id} not found")
                return None

            # Convert attachments to JSON
            attachments_json = json.dumps(attachments) if attachments else None

            # Insert message
            cur.execute("""
                INSERT INTO messages (sender_id, recipient_id, content, type, attachments, read, created_at)
                VALUES (%s, %s, %s, %s, %s, FALSE, CURRENT_TIMESTAMP)
                RETURNING id, sender_id, recipient_id, content, type, attachments, read, created_at
            """, (sender_id, recipient_id, content, msg_type, attachments_json))

            row = cur.fetchone()

            # Create response with sender info
            row['sender_username'] = sender['username']
            row['recipient_username'] = recipient['username']

            return self._build_message_response(row, sender_id)

    def get_conversation(
        self,
        user_id: int,
        other_user_id: int,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[MessageResponse], int]:
        """
        Get conversation between two users

        Args:
            user_id: Current user ID
            other_user_id: Other user ID
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (messages list, total count)
        """
        offset = (page - 1) * limit

        with get_db_cursor() as cur:
            # Get total count
            cur.execute("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE (sender_id = %s AND recipient_id = %s)
                   OR (sender_id = %s AND recipient_id = %s)
            """, (user_id, other_user_id, other_user_id, user_id))

            total = cur.fetchone()['count']

            # Get messages
            cur.execute("""
                SELECT
                    m.id,
                    m.sender_id,
                    m.recipient_id,
                    m.content,
                    m.type,
                    m.attachments,
                    m.read,
                    m.read_at,
                    m.created_at,
                    sender.username as sender_username,
                    sender.avatar_url as sender_avatar,
                    recipient.username as recipient_username
                FROM messages m
                JOIN users sender ON m.sender_id = sender.id
                JOIN users recipient ON m.recipient_id = recipient.id
                WHERE (m.sender_id = %s AND m.recipient_id = %s)
                   OR (m.sender_id = %s AND m.recipient_id = %s)
                ORDER BY m.created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, other_user_id, other_user_id, user_id, limit, offset))

            rows = cur.fetchall()

            # Mark messages as read if recipient is current user
            message_ids = [row['id'] for row in rows]
            if message_ids:
                cur.execute("""
                    UPDATE messages
                    SET read = TRUE, read_at = CURRENT_TIMESTAMP
                    WHERE id = ANY(%s) AND recipient_id = %s AND read = FALSE
                """, (message_ids, user_id))

            messages = [self._build_message_response(row, user_id) for row in rows]

            return messages, total

    def get_threads(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get message threads for a user

        Args:
            user_id: User ID
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (threads list, total count)
        """
        offset = (page - 1) * limit

        with get_db_cursor() as cur:
            # Get total count
            cur.execute("""
                SELECT COUNT(DISTINCT conversation_id) as count
                FROM messages
                WHERE sender_id = %s OR recipient_id = %s
            """, (user_id, user_id))

            total = cur.fetchone()['count']

            # Get threads with last message and unread count
            cur.execute("""
                WITH conversation_stats AS (
                    SELECT
                        CASE
                            WHEN sender_id = %s THEN recipient_id
                            ELSE sender_id
                        END as other_user_id,
                        MAX(created_at) as last_message_at,
                        COUNT(*) FILTER (WHERE read = FALSE AND recipient_id = %s) as unread_count
                    FROM messages
                    WHERE sender_id = %s OR recipient_id = %s
                    GROUP BY other_user_id
                )
                SELECT
                    cs.other_user_id,
                    cs.last_message_at,
                    cs.unread_count,
                    u.id as user_id,
                    u.username,
                    u.avatar_url,
                    (
                        SELECT json_build_object(
                            'id', m.id,
                            'content', m.content,
                            'type', m.type,
                            'sender_id', m.sender_id,
                            'sender_username', sender.username,
                            'created_at', m.created_at,
                            'is_own', m.sender_id = %s
                        )
                        FROM messages m
                        JOIN users sender ON m.sender_id = sender.id
                        WHERE (m.sender_id = %s AND m.recipient_id = cs.other_user_id)
                           OR (m.sender_id = cs.other_user_id AND m.recipient_id = %s)
                        ORDER BY m.created_at DESC
                        LIMIT 1
                    ) as last_message
                FROM conversation_stats cs
                JOIN users u ON cs.other_user_id = u.id
                ORDER BY cs.last_message_at DESC NULLS LAST
                LIMIT %s OFFSET %s
            """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, limit, offset))

            rows = cur.fetchall()

            threads = []
            for row in rows:
                thread = {
                    'participant_id': row['user_id'],
                    'participant_username': row['username'],
                    'participant_avatar': row.get('avatar_url'),
                    'last_message': row['last_message'],
                    'unread_count': row['unread_count'],
                    'last_message_at': row['last_message_at']
                }
                threads.append(thread)

            return threads, total

    def mark_as_read(self, message_id: int, user_id: int) -> bool:
        """
        Mark a message as read

        Args:
            message_id: Message ID
            user_id: Current user ID (must be recipient)

        Returns:
            True if successful
        """
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE messages
                SET read = TRUE, read_at = CURRENT_TIMESTAMP
                WHERE id = %s AND recipient_id = %s
                RETURNING id
            """, (message_id, user_id))

            result = cur.fetchone()
            return result is not None

    def mark_conversation_read(self, user_id: int, other_user_id: int) -> int:
        """
        Mark all messages in a conversation as read

        Args:
            user_id: Current user ID
            other_user_id: Other user ID

        Returns:
            Number of messages marked as read
        """
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE messages
                SET read = TRUE, read_at = CURRENT_TIMESTAMP
                WHERE sender_id = %s AND recipient_id = %s AND read = FALSE
                RETURNING id
            """, (other_user_id, user_id))

            rows = cur.fetchall()
            return len(rows)

    def delete_message(self, message_id: int, user_id: int) -> bool:
        """
        Delete a message (soft delete)

        Args:
            message_id: Message ID
            user_id: Current user ID (must be sender)

        Returns:
            True if successful
        """
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE messages
                SET is_deleted = TRUE
                WHERE id = %s AND sender_id = %s
                RETURNING id
            """, (message_id, user_id))

            result = cur.fetchone()
            return result is not None

    def get_unread_count(self, user_id: int) -> int:
        """
        Get total unread message count for user

        Args:
            user_id: User ID

        Returns:
            Unread message count
        """
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE recipient_id = %s AND read = FALSE
            """, (user_id,))

            return cur.fetchone()['count']

    # ========================================================================
    # Conversation Management (conversation-based messaging)
    # ========================================================================

    def create_conversation(
        self,
        created_by: int,
        request: CreateConversationRequest
    ) -> dict:
        """
        Create a new conversation.

        Supports both direct (1-on-1) and group conversations.
        Checks for existing direct conversations before creating.

        Args:
            created_by: User ID creating the conversation
            request: CreateConversationRequest with conversation details

        Returns:
            Dict with conversation_id and created status

        Raises:
            ValueError: If participants not found or invalid
            Exception: If database operation fails
        """
        # Build full participant list including creator
        participant_ids = list(set(request.participant_ids + [created_by]))
        if len(participant_ids) < 2:
            raise ValueError("At least 2 participants required")

        with get_db_cursor() as cur:
            # Validate all participants exist
            cur.execute(
                "SELECT id, username FROM users WHERE id = ANY(%s)",
                (participant_ids,)
            )
            found_users = cur.fetchall()
            if len(found_users) != len(participant_ids):
                raise ValueError("Some participants not found")

            # Check for existing direct conversation
            if request.conversation_type == "direct" and len(participant_ids) == 2:
                cur.execute("""
                    SELECT c.id
                    FROM conversations c
                    WHERE c.conversation_type = 'direct'
                      AND c.is_group = FALSE
                      AND c.id IN (
                          SELECT cp1.conversation_id
                          FROM conversation_participants cp1
                          WHERE cp1.user_id = %s
                          AND cp1.conversation_id IN (
                              SELECT cp2.conversation_id
                              FROM conversation_participants cp2
                              WHERE cp2.user_id = %s
                          )
                      )
                """, (participant_ids[0], participant_ids[1]))

                existing = cur.fetchone()
                if existing:
                    return {
                        "conversation_id": existing['id'],
                        "created": False,
                        "message": "Conversation already exists"
                    }

            # Create the conversation
            is_group = request.conversation_type == "group"
            cur.execute("""
                INSERT INTO conversations (conversation_type, title, created_by, is_group, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
                RETURNING id
            """, (request.conversation_type, request.title, created_by, is_group))

            conversation_id = cur.fetchone()['id']

            # Add all participants
            for pid in participant_ids:
                role = 'owner' if pid == created_by else 'member'
                cur.execute("""
                    INSERT INTO conversation_participants (conversation_id, user_id, role)
                    VALUES (%s, %s, %s)
                """, (conversation_id, pid, role))

            # Send initial message if provided
            if request.initial_message:
                cur.execute("""
                    INSERT INTO messages (sender_id, recipient_id, content, type, created_at)
                    VALUES (%s, %s, %s, 'user', CURRENT_TIMESTAMP)
                """, (created_by, participant_ids[0], request.initial_message))

                cur.execute("""
                    UPDATE conversations
                    SET last_message_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (conversation_id,))

            return {
                "conversation_id": conversation_id,
                "created": True,
                "message": "Conversation created successfully"
            }

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Delete a conversation (soft delete - removes user from participants).

        Only removes the current user from the conversation.
        The conversation remains for other participants.

        Args:
            conversation_id: Conversation ID to delete
            user_id: Current user ID

        Returns:
            True if successful

        Raises:
            Exception: If database operation fails
        """
        with get_db_cursor() as cur:
            cur.execute("""
                DELETE FROM conversation_participants
                WHERE conversation_id = %s AND user_id = %s
                RETURNING conversation_id
            """, (conversation_id, user_id))

            result = cur.fetchone()
            return result is not None

    def initialize_database(self) -> None:
        """
        Initialize the database tables for conversations.

        Creates conversations and conversation_participants tables
        if they don't already exist.

        Raises:
            Exception: If table creation fails
        """
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            conversation_type VARCHAR(20) NOT NULL DEFAULT 'direct',
            title VARCHAR(255),
            created_by INTEGER NOT NULL,
            is_group BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            last_message_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS conversation_participants (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL DEFAULT 'member',
            last_read_at TIMESTAMP,
            has_unread BOOLEAN DEFAULT FALSE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(conversation_id, user_id)
        );

        CREATE INDEX IF NOT EXISTS idx_conversations_created_by
        ON conversations(created_by);

        CREATE INDEX IF NOT EXISTS idx_conversation_participants_user
        ON conversation_participants(user_id);

        CREATE INDEX IF NOT EXISTS idx_conversation_participants_conv
        ON conversation_participants(conversation_id);
        """

        with get_db_cursor() as cur:
            cur.execute(create_tables_sql)
            logger.info("Conversations database tables initialized successfully")


# ============================================================================
# Notification Service
# ============================================================================

class NotificationService:
    """Service class for notification operations"""

    @staticmethod
    def _build_notification_response(row: dict) -> NotificationResponse:
        """Build NotificationResponse from database row"""
        return NotificationResponse(
            id=row['id'],
            user_id=row['user_id'],
            title=row['title'],
            content=row['content'],
            type=row.get('type', 'info'),
            read=row.get('read', False),
            read_at=row.get('read_at'),
            action_url=row.get('action_url'),
            metadata=json.loads(row['metadata']) if row.get('metadata') else None,
            created_at=row['created_at']
        )

    def send_notification(
        self,
        user_id: int,
        title: str,
        content: str,
        notif_type: str = "info",
        action_url: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[NotificationResponse]:
        """
        Send a notification to a user

        Args:
            user_id: Target user ID
            title: Notification title
            content: Notification content
            notif_type: Notification type (info, warning, error, success, system)
            action_url: Optional URL to navigate to
            metadata: Optional additional metadata

        Returns:
            NotificationResponse or None if failed
        """
        # Validate user exists
        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cur.fetchone():
                logger.warning(f"User {user_id} not found for notification")
                return None

            # Convert metadata to JSON
            metadata_json = json.dumps(metadata) if metadata else None

            # Insert notification
            cur.execute("""
                INSERT INTO notifications (user_id, title, content, type, action_url, metadata, read, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, FALSE, CURRENT_TIMESTAMP)
                RETURNING id, user_id, title, content, type, action_url, metadata, read, read_at, created_at
            """, (user_id, title, content, notif_type, action_url, metadata_json))

            row = cur.fetchone()
            return self._build_notification_response(row)

    def get_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[NotificationResponse], int, int]:
        """
        Get notifications for a user

        Args:
            user_id: User ID
            unread_only: Filter to unread only
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (notifications list, total count, unread count)
        """
        offset = (page - 1) * limit

        with get_db_cursor() as cur:
            # Get unread count
            cur.execute("""
                SELECT COUNT(*) as count
                FROM notifications
                WHERE user_id = %s AND read = FALSE
            """, (user_id,))

            unread_count = cur.fetchone()['count']

            # Get total count
            if unread_only:
                total = unread_count
            else:
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM notifications
                    WHERE user_id = %s
                """, (user_id,))
                total = cur.fetchone()['count']

            # Get notifications
            if unread_only:
                cur.execute("""
                    SELECT id, user_id, title, content, type, action_url, metadata, read, read_at, created_at
                    FROM notifications
                    WHERE user_id = %s AND read = FALSE
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (user_id, limit, offset))
            else:
                cur.execute("""
                    SELECT id, user_id, title, content, type, action_url, metadata, read, read_at, created_at
                    FROM notifications
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (user_id, limit, offset))

            rows = cur.fetchall()
            notifications = [self._build_notification_response(row) for row in rows]

            return notifications, total, unread_count

    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """
        Mark a notification as read

        Args:
            notification_id: Notification ID
            user_id: Current user ID (must be owner)

        Returns:
            True if successful
        """
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE notifications
                SET read = TRUE, read_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (notification_id, user_id))

            result = cur.fetchone()
            return result is not None

    def mark_all_read(self, user_id: int) -> int:
        """
        Mark all notifications as read for a user

        Args:
            user_id: User ID

        Returns:
            Number of notifications marked as read
        """
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE notifications
                SET read = TRUE, read_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND read = FALSE
                RETURNING id
            """, (user_id,))

            rows = cur.fetchall()
            return len(rows)

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """
        Delete a notification

        Args:
            notification_id: Notification ID
            user_id: Current user ID (must be owner)

        Returns:
            True if successful
        """
        with get_db_cursor() as cur:
            cur.execute("""
                DELETE FROM notifications
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (notification_id, user_id))

            result = cur.fetchone()
            return result is not None

    def cleanup_old_notifications(self, days: int = RETENTION_DAYS) -> int:
        """
        Delete notifications older than specified days

        Args:
            days: Number of days to retain

        Returns:
            Number of deleted notifications
        """
        with get_db_cursor() as cur:
            cur.execute("""
                DELETE FROM notifications
                WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
                RETURNING id
            """, (days,))

            rows = cur.fetchall()
            count = len(rows)

            if count > 0:
                logger.info(f"Cleaned up {count} old notifications")

            return count

    def get_unread_count(self, user_id: int) -> int:
        """
        Get unread notification count for user

        Args:
            user_id: User ID

        Returns:
            Unread notification count
        """
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as count
                FROM notifications
                WHERE user_id = %s AND read = FALSE
            """, (user_id,))

            return cur.fetchone()['count']


# ============================================================================
# Singleton Instances
# ============================================================================

message_service = MessageService()
notification_service = NotificationService()
