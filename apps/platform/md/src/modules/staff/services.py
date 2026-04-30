"""
Staff Module Services
Business logic for staff management operations

Provides services for:
- Staff user authentication
- Staff user CRUD operations
- Role management
- Permission management
- Audit logging
"""

import hashlib
from passlib.hash import bcrypt
import secrets
import json
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


from .schemas import (
    StaffStatus,
    StaffUserResponse,
    StaffUserCreate,
    StaffUserUpdate,
    RoleResponse,
    RoleCreate,
    RoleUpdate,
    PermissionResponse,
    AuditLogEntry,
    AuditLogFilter,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

# Load environment variables from .env file
def _load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

# Load environment on module import
_load_env()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))


def get_db_cursor():
    """Get database cursor"""
    from core.db_adapter import get_db_cursor
    return get_db_cursor()


# ============================================================================
# Permission Definitions
# ============================================================================

# All available permissions with their metadata
ALL_PERMISSIONS = {
    # Orders permissions
    "orders:order:read": {"name": "查看订单", "category": "orders", "description": "查看订单列表和详情"},
    "orders:order:create": {"name": "创建订单", "category": "orders", "description": "创建新订单"},
    "orders:order:update": {"name": "更新订单", "category": "orders", "description": "修改订单信息"},
    "orders:order:delete": {"name": "删除订单", "category": "orders", "description": "删除订单"},
    "orders:order:refund": {"name": "订单退款", "category": "orders", "description": "处理订单退款"},

    # Goods permissions
    "goods:product:read": {"name": "查看商品", "category": "goods", "description": "查看商品列表和详情"},
    "goods:product:create": {"name": "创建商品", "category": "goods", "description": "创建新商品"},
    "goods:product:update": {"name": "更新商品", "category": "goods", "description": "修改商品信息"},
    "goods:product:delete": {"name": "删除商品", "category": "goods", "description": "删除商品"},

    # Promotion permissions
    "promotion:coupon:read": {"name": "查看优惠券", "category": "promotion", "description": "查看优惠券列表"},
    "promotion:coupon:create": {"name": "创建优惠券", "category": "promotion", "description": "创建新优惠券"},
    "promotion:coupon:update": {"name": "更新优惠券", "category": "promotion", "description": "修改优惠券"},
    "promotion:coupon:delete": {"name": "删除优惠券", "category": "promotion", "description": "删除优惠券"},
    "promotion:activity:read": {"name": "查看活动", "category": "promotion", "description": "查看营销活动"},
    "promotion:activity:create": {"name": "创建活动", "category": "promotion", "description": "创建营销活动"},
    "promotion:activity:update": {"name": "更新活动", "category": "promotion", "description": "修改营销活动"},

    # Logistics permissions
    "logistics:ship:read": {"name": "查看物流", "category": "logistics", "description": "查看物流信息"},
    "logistics:ship:update": {"name": "更新物流", "category": "logistics", "description": "更新物流状态"},

    # Staff permissions
    "staff:user:read": {"name": "查看员工", "category": "staff", "description": "查看员工列表和详情"},
    "staff:user:create": {"name": "创建员工", "category": "staff", "description": "创建新员工"},
    "staff:user:update": {"name": "更新员工", "category": "staff", "description": "修改员工信息"},
    "staff:user:delete": {"name": "删除员工", "category": "staff", "description": "删除员工"},
    "staff:role:read": {"name": "查看角色", "category": "staff", "description": "查看角色列表"},
    "staff:role:create": {"name": "创建角色", "category": "staff", "description": "创建新角色"},
    "staff:role:update": {"name": "更新角色", "category": "staff", "description": "修改角色"},
    "staff:role:delete": {"name": "删除角色", "category": "staff", "description": "删除角色"},

    # Storage permissions
    "storage:file:read": {"name": "查看文件", "category": "storage", "description": "查看文件列表"},
    "storage:file:upload": {"name": "上传文件", "category": "storage", "description": "上传文件"},
    "storage:file:delete": {"name": "删除文件", "category": "storage", "description": "删除文件"},

    # Points permissions
    "points:account:read": {"name": "查看积分账户", "category": "points", "description": "查看积分账户"},
    "points:account:update": {"name": "更新积分账户", "category": "points", "description": "修改积分账户"},
    "points:transaction:read": {"name": "查看积分流水", "category": "points", "description": "查看积分交易记录"},
}

# System roles with default permissions
SYSTEM_ROLES = [
    {
        "code": "super_admin",
        "name": "超级管理员",
        "description": "拥有系统所有权限",
        "permissions": ["*"],  # Wildcard means all permissions
        "is_system": True
    },
    {
        "code": "admin",
        "name": "管理员",
        "description": "拥有大部分管理权限",
        "permissions": [
            "orders:order:*",
            "goods:product:*",
            "promotion:coupon:*",
            "promotion:activity:*",
            "logistics:ship:*",
            "staff:user:*",
            "staff:role:read",
            "storage:*",
            "points:*",
        ],
        "is_system": True
    },
    {
        "code": "operator",
        "name": "运营人员",
        "description": "负责日常运营工作",
        "permissions": [
            "orders:order:read",
            "orders:order:update",
            "goods:product:read",
            "goods:product:create",
            "goods:product:update",
            "promotion:coupon:*",
            "promotion:activity:*",
        ],
        "is_system": True
    },
    {
        "code": "customer_service",
        "name": "客服人员",
        "description": "负责客户服务和售后",
        "permissions": [
            "orders:order:read",
            "orders:order:update",
            "orders:order:refund",
            "goods:product:read",
        ],
        "is_system": True
    },
    {
        "code": "warehouse",
        "name": "仓库人员",
        "description": "负责仓库管理和发货",
        "permissions": [
            "orders:order:read",
            "logistics:ship:read",
            "logistics:ship:update",
            "goods:product:read",
        ],
        "is_system": True
    },
    {
        "code": "finance",
        "name": "财务人员",
        "description": "负责财务和对账",
        "permissions": [
            "orders:order:read",
            "orders:order:refund",
            "points:account:read",
            "points:transaction:read",
            "logistics:ship:read",
        ],
        "is_system": True
    },
]


# ============================================================================
# Helper Functions
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash. Supports both bcrypt and legacy SHA-256."""
    # bcrypt hashes start with $2b$ or $2a$
    if password_hash.startswith("$2"):
        return bcrypt.verify(password, password_hash)
    # Legacy SHA-256 hash (64 hex characters)
    if len(password_hash) == 64 and all(c in "0123456789abcdef" for c in password_hash.lower()):
        return hashlib.sha256(password.encode()).hexdigest() == password_hash
    return False


def generate_temp_password(length: int = 12) -> str:
    """Generate temporary password"""
    return secrets.token_urlsafe(length)


def expand_permissions(permissions: List[str]) -> set:
    """
    Expand permission patterns to individual permissions

    Args:
        permissions: List of permission strings, may include wildcards

    Returns:
        Set of expanded permission codes
    """
    expanded = set()

    for perm in permissions:
        if perm == "*":
            # All permissions
            expanded.update(ALL_PERMISSIONS.keys())
        elif perm.endswith(":*"):
            # Category wildcard (e.g., "orders:*")
            prefix = perm[:-2]
            for p in ALL_PERMISSIONS.keys():
                if p.startswith(prefix + ":"):
                    expanded.add(p)
        else:
            # Specific permission
            expanded.add(perm)

    return expanded


def check_permission(user_permissions: set, required_permission: str) -> bool:
    """Check if user has the required permission"""
    # Check for wildcard permission
    if "*" in user_permissions:
        return True

    # Check for category wildcard
    category = required_permission.split(":")[0]
    if f"{category}:*" in user_permissions:
        return True

    # Check for specific permission
    return required_permission in user_permissions


# ============================================================================
# Database Initialization
# ============================================================================

def init_staff_tables():
    """Initialize staff-related database tables"""
    with get_db_cursor() as cur:
        # Create staff_users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS staff_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100),
                password_hash VARCHAR(64) NOT NULL,
                phone VARCHAR(20),
                role_id INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                last_login TIMESTAMP,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create staff_roles table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS staff_roles (
                id SERIAL PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                description VARCHAR(500),
                permissions_json TEXT DEFAULT '[]',
                is_system BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create staff_permissions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS staff_permissions (
                id SERIAL PRIMARY KEY,
                code VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description VARCHAR(500)
            )
        """)

        # Create staff_audit_log table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS staff_audit_log (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                action VARCHAR(100) NOT NULL,
                resource VARCHAR(100) NOT NULL,
                resource_id INTEGER,
                details_json TEXT,
                ip VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_staff_users_username
            ON staff_users (username)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_staff_users_status
            ON staff_users (status)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_staff_roles_code
            ON staff_roles (code)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_staff_audit_log_user_id
            ON staff_audit_log (user_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_staff_audit_log_created_at
            ON staff_audit_log (created_at DESC)
        """)

        logger.info("Staff tables initialized successfully")


def init_system_roles():
    """Initialize system roles if they don't exist"""
    with get_db_cursor() as cur:
        for role_data in SYSTEM_ROLES:
            # Check if role exists
            cur.execute(
                "SELECT id FROM staff_roles WHERE code = %s",
                (role_data["code"],)
            )
            existing = cur.fetchone()

            if not existing:
                # Insert system role
                cur.execute("""
                    INSERT INTO staff_roles (code, name, description, permissions_json, is_system)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    role_data["code"],
                    role_data["name"],
                    role_data["description"],
                    json.dumps(role_data["permissions"]),
                    role_data["is_system"]
                ))
                logger.info(f"Created system role: {role_data['code']}")


def init_permissions():
    """Initialize permissions table if empty"""
    with get_db_cursor() as cur:
        # Check if permissions table is empty
        cur.execute("SELECT COUNT(*) as cnt FROM staff_permissions")
        count = cur.fetchone()['cnt']

        if count == 0:
            # Insert all permissions
            for code, meta in ALL_PERMISSIONS.items():
                cur.execute("""
                    INSERT INTO staff_permissions (code, name, category, description)
                    VALUES (%s, %s, %s, %s)
                """, (
                    code,
                    meta["name"],
                    meta["category"],
                    meta.get("description", "")
                ))
            logger.info(f"Initialized {len(ALL_PERMISSIONS)} permissions")


# ============================================================================
# Authentication Service
# ============================================================================

class AuthService:
    """Service for staff authentication"""

    def __init__(self):
        self.jwt_secret = JWT_SECRET
        self.jwt_algorithm = JWT_ALGORITHM
        self.jwt_expire_minutes = JWT_EXPIRE_MINUTES

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate staff user

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT u.*, r.name as role_name, r.permissions_json
                    FROM staff_users u
                    LEFT JOIN staff_roles r ON u.role_id = r.id
                    WHERE u.username = %s
                """, (username,))
                user = cur.fetchone()

            if not user:
                return False, None, "用户名或密码错误"

            # Check status
            if user['status'] != 'active':
                return False, None, f"账户已被禁用 (状态: {user['status']})"

            # Verify password
            if not verify_password(password, user['password_hash']):
                return False, None, "用户名或密码错误"

            # Update last login
            with get_db_cursor() as cur:
                cur.execute(
                    "UPDATE staff_users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                    (user['id'],)
                )

            # Build user data (exclude password hash)
            user_data = {
                "id": user['id'],
                "username": user['username'],
                "email": user.get('email'),
                "phone": user.get('phone'),
                "role_id": user['role_id'],
                "role_name": user.get('role_name'),
                "status": user['status'],
                "permissions": json.loads(user.get('permissions_json', '[]')) if user.get('permissions_json') else []
            }

            return True, user_data, None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None, f"认证失败: {str(e)}"

    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        from jose import jwt

        expire = datetime.utcnow() + timedelta(minutes=self.jwt_expire_minutes)
        payload = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "role_id": user_data["role_id"],
            "role_name": user_data.get("role_name"),
            "permissions": user_data.get("permissions", []),
            "exp": expire,
            "type": "staff_access"
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify JWT token"""
        from jose import jwt, JWTError

        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            if payload.get("type") != "staff_access":
                return False, None
            return True, payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return False, None


auth_service = AuthService()


# ============================================================================
# Staff User Service
# ============================================================================

class StaffUserService:
    """Service for staff user management"""

    @staticmethod
    def _build_user_response(row: Dict[str, Any]) -> StaffUserResponse:
        """Build StaffUserResponse from database row"""
        return StaffUserResponse(
            id=row.get('id', 0),
            username=row.get('username', ''),
            email=row.get('email'),
            phone=row.get('phone'),
            role_id=row.get('role_id', 0),
            role_name=row.get('role_name'),
            status=row.get('status', 'active'),
            last_login=row.get('last_login'),
            created_by=row.get('created_by'),
            created_at=row.get('created_at', datetime.now()),
            updated_at=row.get('updated_at')
        )

    def get_users(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[StaffUserResponse], int]:
        """
        Get paginated list of staff users

        Args:
            filters: Optional filter parameters
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
        param_index = 1

        if 'status' in filters:
            conditions.append(f"u.status = ${param_index}")
            values.append(filters['status'])
            param_index += 1

        if 'role_id' in filters:
            conditions.append(f"u.role_id = ${param_index}")
            values.append(filters['role_id'])
            param_index += 1

        if 'search' in filters:
            search_term = f"%{filters['search']}%"
            conditions.append(f"(u.username ILIKE ${param_index} OR u.email ILIKE ${param_index} OR u.phone ILIKE ${param_index})")
            values.append(search_term)
            param_index += 1

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM staff_users u
            {where_clause}
        """
        with get_db_cursor() as cur:
            cur.execute(count_query, values)
            total = cur.fetchone()['total']

        # Build pagination values
        # Use %s placeholders for pagination since they come after filter params
        query = f"""
            SELECT u.*, r.name as role_name
            FROM staff_users u
            LEFT JOIN staff_roles r ON u.role_id = r.id
            {where_clause}
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        """
        # Append pagination values to filter values
        pagination_values = values.copy()
        pagination_values.extend([limit, offset])

        with get_db_cursor() as cur:
            cur.execute(query, pagination_values)
            rows = cur.fetchall()

        users = [self._build_user_response(dict(row)) for row in rows]
        return users, total

    def get_user_by_id(self, user_id: int) -> Optional[StaffUserResponse]:
        """Get staff user by ID"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT u.*, r.name as role_name
                FROM staff_users u
                LEFT JOIN staff_roles r ON u.role_id = r.id
                WHERE u.id = %s
            """, (user_id,))
            row = cur.fetchone()

        if not row:
            return None

        return self._build_user_response(dict(row))

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get user permissions based on role"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT r.permissions_json
                FROM staff_users u
                JOIN staff_roles r ON u.role_id = r.id
                WHERE u.id = %s
            """, (user_id,))
            row = cur.fetchone()

        if not row or not row.get('permissions_json'):
            return []

        return json.loads(row['permissions_json'])

    def create_user(self, user_data: StaffUserCreate, created_by: int) -> Tuple[bool, Optional[StaffUserResponse], str]:
        """Create a new staff user"""
        try:
            # Validate username format
            if not re.match(r'^[a-zA-Z0-9_]{2,50}$', user_data.username):
                return False, None, "用户名只能包含字母、数字和下划线，长度2-50位"

            # Check if username exists
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM staff_users WHERE username = %s", (user_data.username,))
                if cur.fetchone():
                    return False, None, "用户名已存在"

                # Verify role exists
                cur.execute("SELECT id FROM staff_roles WHERE id = %s", (user_data.role_id,))
                if not cur.fetchone():
                    return False, None, "指定的角色不存在"

            # Hash password and create user
            password_hash = hash_password(user_data.password)

            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO staff_users
                    (username, email, password_hash, phone, role_id, status, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    user_data.username,
                    user_data.email,
                    password_hash,
                    user_data.phone,
                    user_data.role_id,
                    str(user_data.status.value),
                    created_by
                ))
                user_id = cur.fetchone()['id']

            # Return created user
            return True, self.get_user_by_id(user_id), ""

        except Exception as e:
            logger.error(f"Error creating staff user: {e}")
            return False, None, f"创建员工失败: {str(e)}"

    def update_user(
        self,
        user_id: int,
        user_data: StaffUserUpdate
    ) -> Tuple[bool, Optional[StaffUserResponse], str]:
        """Update staff user"""
        try:
            # Build update query dynamically
            updates = []
            values = []
            param_index = 1

            if user_data.email is not None:
                updates.append(f"email = ${param_index}")
                values.append(user_data.email)
                param_index += 1

            if user_data.phone is not None:
                updates.append(f"phone = ${param_index}")
                values.append(user_data.phone)
                param_index += 1

            if user_data.role_id is not None:
                # Verify role exists
                with get_db_cursor() as cur:
                    cur.execute("SELECT id FROM staff_roles WHERE id = %s", (user_data.role_id,))
                    if not cur.fetchone():
                        return False, None, "指定的角色不存在"
                updates.append(f"role_id = ${param_index}")
                values.append(user_data.role_id)
                param_index += 1

            if user_data.status is not None:
                updates.append(f"status = ${param_index}")
                values.append(str(user_data.status.value))
                param_index += 1

            if not updates:
                return True, self.get_user_by_id(user_id), ""

            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)

            with get_db_cursor() as cur:
                query = f"""
                    UPDATE staff_users
                    SET {', '.join(updates)}
                    WHERE id = ${param_index}
                """
                cur.execute(query, values)

            return True, self.get_user_by_id(user_id), ""

        except Exception as e:
            logger.error(f"Error updating staff user: {e}")
            return False, None, f"更新员工失败: {str(e)}"

    def update_password(self, user_id: int, new_password: str, admin_id: Optional[int] = None) -> Tuple[bool, str]:
        """Update staff user password"""
        try:
            password_hash = hash_password(new_password)

            with get_db_cursor() as cur:
                cur.execute(
                    "UPDATE staff_users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (password_hash, user_id)
                )

            # Log action
            if admin_id:
                audit_service.log_action(
                    user_id=admin_id,
                    action="reset_password",
                    resource="staff_user",
                    resource_id=user_id,
                    details={"action": "admin_reset_password"}
                )

            return True, "密码更新成功"

        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False, f"密码更新失败: {str(e)}"

    def update_status(self, user_id: int, status: StaffStatus, admin_id: int) -> Tuple[bool, str]:
        """Update staff user status"""
        try:
            with get_db_cursor() as cur:
                cur.execute(
                    "UPDATE staff_users SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (str(status.value), user_id)
                )

            # Log action
            audit_service.log_action(
                user_id=admin_id,
                action="change_status",
                resource="staff_user",
                resource_id=user_id,
                details={"new_status": str(status.value)}
            )

            return True, "状态更新成功"

        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False, f"状态更新失败: {str(e)}"

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Delete staff user"""
        try:
            with get_db_cursor() as cur:
                cur.execute("DELETE FROM staff_users WHERE id = %s AND is_system = FALSE", (user_id,))

            return True, "删除成功"

        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False, f"删除失败: {str(e)}"


staff_user_service = StaffUserService()


# ============================================================================
# Role Service
# ============================================================================

class RoleService:
    """Service for role management"""

    @staticmethod
    def _build_role_response(row: Dict[str, Any]) -> RoleResponse:
        """Build RoleResponse from database row"""
        permissions_json = row.get('permissions_json', '[]')
        if isinstance(permissions_json, str):
            permissions = json.loads(permissions_json)
        else:
            permissions = permissions_json

        return RoleResponse(
            id=row.get('id', 0),
            code=row.get('code', ''),
            name=row.get('name', ''),
            description=row.get('description'),
            permissions=permissions,
            is_system=row.get('is_system', False),
            created_at=row.get('created_at', datetime.now()),
            updated_at=row.get('updated_at')
        )

    def get_roles(self) -> List[RoleResponse]:
        """Get all roles"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM staff_roles
                ORDER BY is_system DESC, id ASC
            """)
            rows = cur.fetchall()

        return [self._build_role_response(dict(row)) for row in rows]

    def get_role_by_id(self, role_id: int) -> Optional[RoleResponse]:
        """Get role by ID"""
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM staff_roles WHERE id = %s", (role_id,))
            row = cur.fetchone()

        if not row:
            return None

        return self._build_role_response(dict(row))

    def get_role_by_code(self, code: str) -> Optional[RoleResponse]:
        """Get role by code"""
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM staff_roles WHERE code = %s", (code,))
            row = cur.fetchone()

        if not row:
            return None

        return self._build_role_response(dict(row))

    def create_role(self, role_data: RoleCreate) -> Tuple[bool, Optional[RoleResponse], str]:
        """Create a new role"""
        try:
            # Validate code format
            if not re.match(r'^[a-z][a-z0-9_]*$', role_data.code):
                return False, None, "角色代码只能包含小写字母、数字和下划线，以小写字母开头"

            # Check if code exists
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM staff_roles WHERE code = %s", (role_data.code,))
                if cur.fetchone():
                    return False, None, "角色代码已存在"

            # Validate permissions
            user_perms = set(role_data.permissions)
            all_perms = set(ALL_PERMISSIONS.keys())
            expanded = expand_permissions(role_data.permissions)
            invalid_perms = expanded - all_perms

            if invalid_perms:
                return False, None, f"无效的权限代码: {', '.join(list(invalid_perms)[:5])}"

            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO staff_roles (code, name, description, permissions_json, is_system)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    role_data.code,
                    role_data.name,
                    role_data.description,
                    json.dumps(role_data.permissions),
                    role_data.is_system
                ))
                role_id = cur.fetchone()['id']

            return True, self.get_role_by_id(role_id), ""

        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return False, None, f"创建角色失败: {str(e)}"

    def update_role(
        self,
        role_id: int,
        role_data: RoleUpdate
    ) -> Tuple[bool, Optional[RoleResponse], str]:
        """Update role"""
        try:
            # Check if role is system role
            role = self.get_role_by_id(role_id)
            if not role:
                return False, None, "角色不存在"
            if role.is_system:
                return False, None, "系统角色不能修改"

            # Build update query
            updates = []
            values = []
            param_index = 1

            if role_data.name is not None:
                updates.append(f"name = ${param_index}")
                values.append(role_data.name)
                param_index += 1

            if role_data.description is not None:
                updates.append(f"description = ${param_index}")
                values.append(role_data.description)
                param_index += 1

            if role_data.permissions is not None:
                # Validate permissions
                expanded = expand_permissions(role_data.permissions)
                invalid_perms = expanded - set(ALL_PERMISSIONS.keys())

                if invalid_perms:
                    return False, None, f"无效的权限代码: {', '.join(list(invalid_perms)[:5])}"

                updates.append(f"permissions_json = ${param_index}")
                values.append(json.dumps(role_data.permissions))
                param_index += 1

            if not updates:
                return True, role, ""

            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(role_id)

            with get_db_cursor() as cur:
                query = f"""
                    UPDATE staff_roles
                    SET {', '.join(updates)}
                    WHERE id = ${param_index}
                """
                cur.execute(query, values)

            return True, self.get_role_by_id(role_id), ""

        except Exception as e:
            logger.error(f"Error updating role: {e}")
            return False, None, f"更新角色失败: {str(e)}"

    def delete_role(self, role_id: int) -> Tuple[bool, str]:
        """Delete role"""
        try:
            # Check if role is system role
            role = self.get_role_by_id(role_id)
            if not role:
                return False, "角色不存在"
            if role.is_system:
                return False, "系统角色不能删除"

            # Check if role is in use
            with get_db_cursor() as cur:
                cur.execute("SELECT COUNT(*) as cnt FROM staff_users WHERE role_id = %s", (role_id,))
                count = cur.fetchone()['cnt']
                if count > 0:
                    return False, f"该角色已被 {count} 个员工使用，无法删除"

                cur.execute("DELETE FROM staff_roles WHERE id = %s", (role_id,))

            return True, "删除成功"

        except Exception as e:
            logger.error(f"Error deleting role: {e}")
            return False, f"删除失败: {str(e)}"


role_service = RoleService()


# ============================================================================
# Permission Service
# ============================================================================

class PermissionService:
    """Service for permission management"""

    def get_permissions(self) -> List[PermissionResponse]:
        """Get all permissions"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM staff_permissions
                ORDER BY category, code
            """)
            rows = cur.fetchall()

        return [PermissionResponse(
            id=row['id'],
            code=row['code'],
            name=row['name'],
            category=row['category'],
            description=row.get('description')
        ) for row in rows]

    def get_permission_tree(self) -> List[Dict[str, Any]]:
        """Get permissions as a tree structure"""
        from .schemas import PermissionTreeNode

        permissions = self.get_permissions()

        # Group by category
        categories = {}
        for perm in permissions:
            cat = perm.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "key": perm.code,
                "label": perm.name,
                "category": perm.category,
                "description": perm.description,
                "children": []
            })

        # Category display names
        category_names = {
            "orders": "订单管理",
            "goods": "商品管理",
            "promotion": "营销推广",
            "logistics": "物流管理",
            "staff": "员工管理",
            "storage": "文件存储",
            "points": "积分管理",
            "finance": "财务管理"
        }

        # Build tree
        tree = []
        for cat_code, perms in sorted(categories.items()):
            tree.append({
                "key": cat_code,
                "label": category_names.get(cat_code, cat_code),
                "category": cat_code,
                "description": None,
                "children": perms
            })

        return tree

    def check_user_permission(self, user_id: int, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = staff_user_service.get_user_permissions(user_id)
        expanded = expand_permissions(permissions)
        return check_permission(expanded, permission)


permission_service = PermissionService()


# ============================================================================
# Audit Log Service
# ============================================================================

class StaffAuditLogService:
    """Service for staff audit logging"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def log_action(
        self,
        user_id: int,
        action: str,
        resource: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Log an action to audit log"""
        if not self.enabled:
            return True

        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO staff_audit_log
                    (user_id, action, resource, resource_id, details_json, ip, user_agent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    action,
                    resource,
                    resource_id,
                    json.dumps(details) if details else None,
                    ip,
                    user_agent
                ))
            return True
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")
            return False

    def get_logs(
        self,
        filters: Optional[AuditLogFilter] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[AuditLogEntry], int]:
        """Get paginated audit logs"""
        filters = filters or AuditLogFilter()
        offset = (page - 1) * limit

        # Build WHERE clause
        conditions = []
        values = []
        param_index = 1

        if filters.user_id:
            conditions.append(f"a.user_id = ${param_index}")
            values.append(filters.user_id)
            param_index += 1

        if filters.action:
            conditions.append(f"a.action = ${param_index}")
            values.append(filters.action)
            param_index += 1

        if filters.resource:
            conditions.append(f"a.resource = ${param_index}")
            values.append(filters.resource)
            param_index += 1

        if filters.start_date:
            conditions.append(f"a.created_at >= ${param_index}")
            values.append(filters.start_date)
            param_index += 1

        if filters.end_date:
            conditions.append(f"a.created_at <= ${param_index}")
            values.append(filters.end_date)
            param_index += 1

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM staff_audit_log a
            {where_clause}
        """
        with get_db_cursor() as cur:
            cur.execute(count_query, values)
            total = cur.fetchone()['total']

        # Get paginated results
        query = f"""
            SELECT a.*, u.username
            FROM staff_audit_log a
            LEFT JOIN staff_users u ON a.user_id = u.id
            {where_clause}
            ORDER BY a.created_at DESC
            LIMIT %s OFFSET %s
        """
        # Append pagination values to filter values
        pagination_values = values.copy()
        pagination_values.extend([limit, offset])

        with get_db_cursor() as cur:
            cur.execute(query, pagination_values)
            rows = cur.fetchall()

        logs = []
        for row in rows:
            details_json = row.get('details_json')
            details = None
            if details_json:
                try:
                    details = json.loads(details_json)
                except Exception:
                    details = {"raw": details_json}

            logs.append(AuditLogEntry(
                id=row['id'],
                user_id=row['user_id'],
                username=row.get('username'),
                action=row['action'],
                resource=row['resource'],
                resource_id=row.get('resource_id'),
                details=details,
                ip=row.get('ip'),
                user_agent=row.get('user_agent'),
                created_at=row['created_at']
            ))

        return logs, total


audit_service = StaffAuditLogService(enabled=True)


# ============================================================================
# Singleton Instances
# ============================================================================

__all__ = [
    "AuthService",
    "StaffUserService",
    "RoleService",
    "PermissionService",
    "StaffAuditLogService",
    "auth_service",
    "staff_user_service",
    "role_service",
    "permission_service",
    "audit_service",
    "init_staff_tables",
    "init_system_roles",
    "init_permissions",
    "ALL_PERMISSIONS",
    "SYSTEM_ROLES",
    "expand_permissions",
    "check_permission",
    "hash_password",
    "verify_password",
]
