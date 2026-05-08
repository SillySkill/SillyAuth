"""
Skill2 Services
Core business logic: key management, P1-P5 scanning, encryption, packaging
"""

import hashlib
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from core.config import get_skill2_config
from core.db_adapter import get_db_cursor as _get_db_cursor

logger = logging.getLogger(__name__)

# Decorator for TZ-aware datetime in JSON
def _json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def get_db_cursor():
    """Get database cursor with auto-commit."""
    return _get_db_cursor()


# ============================================================================
# PlatformKeyService
# ============================================================================

class PlatformKeyService:
    """RSA key pair management: generation, storage, signing, verification."""

    def get_active_key(self) -> Optional[Dict[str, Any]]:
        """Get the active platform RSA key pair from the database."""
        try:
            with get_db_cursor() as cur:
                cur.execute(
                    "SELECT * FROM platform_keys WHERE is_active = TRUE ORDER BY key_version DESC LIMIT 1"
                )
                return cur.fetchone()
        except Exception as e:
            logger.warning(f"Failed to get active key: {e}")
            return None

    def get_key_by_version(self, key_version: int) -> Optional[Dict[str, Any]]:
        """Get a specific key version (for verifying old packages)."""
        try:
            with get_db_cursor() as cur:
                cur.execute(
                    "SELECT * FROM platform_keys WHERE key_version = %s", (key_version,)
                )
                return cur.fetchone()
        except Exception as e:
            logger.warning(f"Failed to get key version {key_version}: {e}")
            return None

    def generate_key_pair(self) -> Optional[Dict[str, Any]]:
        """Generate a new RSA-2048 key pair and store in the database."""
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization

            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            # Encrypt private key at rest using JWT secret
            encrypted_private = self._encrypt_key(private_pem.decode())

            with get_db_cursor() as cur:
                # Deactivate old keys
                cur.execute("UPDATE platform_keys SET is_active = FALSE WHERE is_active = TRUE")
                # Insert new key
                cur.execute("""
                    INSERT INTO platform_keys (key_version, algorithm, public_key, private_key, is_active)
                    VALUES (
                        (SELECT COALESCE(MAX(key_version), 0) + 1 FROM platform_keys),
                        'RSA-2048', %s, %s, TRUE
                    )
                    RETURNING *
                """, (public_pem.decode(), encrypted_private))
                result = cur.fetchone()
                logger.info(f"Generated platform key pair: version {result['key_version']}")
                return result

        except Exception as e:
            logger.error(f"Failed to generate key pair: {e}")
            return None

    def sign(self, data: bytes, private_key_pem: str) -> str:
        """Sign data with the platform private key (PKCS1v15 SHA256)."""
        from cryptography.hazmat.primitives import hashes, asymmetric, serialization

        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None
        )
        signature = private_key.sign(
            data,
            asymmetric.padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return signature.hex()

    def verify(self, data: bytes, signature_hex: str, public_key_pem: str) -> bool:
        """Verify a signature with the platform public key."""
        try:
            from cryptography.hazmat.primitives import hashes, asymmetric, serialization

            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            signature = bytes.fromhex(signature_hex)
            public_key.verify(
                signature,
                data,
                asymmetric.padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    @staticmethod
    def _encrypt_key(private_key_pem: str) -> str:
        """Encrypt private key at rest using Fernet derived from JWT_SECRET."""
        try:
            from cryptography.fernet import Fernet
            import base64
            secret = os.getenv('JWT_SECRET', 'change-this-in-production')
            key_bytes = hashlib.sha256(secret.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            f = Fernet(fernet_key)
            return f.encrypt(private_key_pem.encode()).decode()
        except Exception as e:
            logger.warning(f"Key encryption failed, storing plaintext: {e}")
            return private_key_pem

    def ensure_tables(self) -> None:
        """Create platform_keys and skill2_packages tables if they don't exist."""
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS platform_keys (
                        id BIGSERIAL PRIMARY KEY,
                        key_version INT NOT NULL DEFAULT 1,
                        algorithm VARCHAR(20) NOT NULL DEFAULT 'RSA-2048',
                        public_key TEXT NOT NULL,
                        private_key TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        rotated_at TIMESTAMPTZ
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS skill2_packages (
                        id BIGSERIAL PRIMARY KEY,
                        skill_id BIGINT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
                        package_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                        declaration_id VARCHAR(64),
                        scan_summary JSONB,
                        sensitive_count INT DEFAULT 0,
                        content_key_ciphertext TEXT,
                        encrypted_content TEXT,
                        encryption_iv TEXT,
                        encryption_tag TEXT,
                        preview_content TEXT,
                        package_url TEXT,
                        manifest_url TEXT,
                        package_hash CHAR(64),
                        platform_signature TEXT,
                        content_hash CHAR(64),
                        key_version INT DEFAULT 1,
                        error_message TEXT,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.info("Skill2 tables ensured")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")


# ============================================================================
# SensitiveContentScanner (P1-P5)
# ============================================================================

class SensitiveContentScanner:
    """
    Scans Markdown/YAML skill content for sensitive information.

    P1: Explicit ${skill2:secret}/${skill2:block} markers (confidence=1.0)
    P2: Field name matching for known sensitive fields (confidence=0.85)
    P3: Format matching for JWT, UUID, API keys (confidence=0.75)
    P4: Semantic detection in code blocks (confidence=0.5)
    P5: Position/depth weighting (confidence boost +0.2 for deep nesting)
    """

    # P1: Explicit markers (highest priority, 100% confidence)
    P1_PATTERNS = [
        (r'\$\{skill2:secret:([^}]+)\}(.*?)\$\{skill2:secret\}', 'explicit_secret'),
        (r'\$\{skill2:block:([^}]+)\}(.*?)\$\{skill2:block\}', 'explicit_block'),
        (r'\$\{skill2:field:([^}]+)\}(.*?)\$\{skill2:field\}', 'explicit_field'),
        (r'\$\{skill2:full\}(.*?)\$\{skill2:full\}', 'explicit_full'),
        (r'\$\{skill2:encrypted:[^}]+\}', 'already_encrypted'),
    ]

    # P2: Field name matching (YAML/document headers)
    P2_FIELD_PATTERNS = [
        (r'(?im)^(api[_-]?key)\s*[:=]\s*["\']?([^"\'\\s,;}]+)', 'api_key_assign'),
        (r'(?im)^(password|passwd)\s*[:=]\s*["\']?([^"\'\\s,;}]+)', 'password_assign'),
        (r'(?im)^(token|auth_token|access_token|refresh_token)\s*[:=]\s*["\']?([^"\'\\s,;}]+)', 'token_assign'),
        (r'(?im)^(secret|secret_key|api_secret|app_secret)\s*[:=]\s*["\']?([^"\'\\s,;}]+)', 'secret_assign'),
        (r'(?im)^(private_key|private-key)\s*[:=]\s*["\']?([^"\'\\s,;}]+)', 'private_key_assign'),
        (r'(?im)^(access_key|access-key)\s*[:=]\s*["\']?([^"\'\\s,;}]+)', 'access_key_assign'),
        (r'(?im)^(auth|authorization|credentials)\s*[:=]\s*["\']?([^"\'\\s,;}]+)', 'auth_assign'),
        (r'(?im)^(ssn|id_card|bank_card|phone)\s*[:=]\s*["\']?([^"\'\\s,;}]+)', 'pii_assign'),
    ]

    # P3: Format patterns (auto-detect known formats)
    P3_FORMAT_PATTERNS = [
        (r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', 'jwt_token'),
        (r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'uuid'),
        (r'(?i)(sk-[A-Za-z0-9]{20,}|pk-[A-Za-z0-9]{20,})', 'api_key_format'),
        (r'(?i)AKIA[0-9A-Z]{16}', 'aws_access_key'),
    ]

    # P4: Semantic keywords in code blocks
    P4_SEMANTIC_KEYWORDS = [
        'prompt', 'algorithm', 'business logic', 'proprietary', 'confidential',
        'core logic', 'secret formula', 'private method',
    ]

    def scan(self, content: str) -> Dict[str, Any]:
        """
        Run all 5 scan strategies on the content.
        Returns structured scan results.
        """
        start_time = time.time()
        items = []
        lines = content.split('\n')

        # P1: Explicit markers
        for pattern, label in self.P1_PATTERNS:
            for match in re.finditer(pattern, content, re.DOTALL):
                line_no = self._find_line_number(lines, match.start())
                preview = match.group(0)[:120] if label != 'already_encrypted' else match.group(0)
                items.append({
                    'marker_type': 'p1_explicit',
                    'content_preview': preview,
                    'line_number': line_no,
                    'column': self._find_column(lines, match.start()),
                    'confidence': 1.0,
                    'suggested_action': 'encrypt',
                })

        # P2: Field name matching
        for pattern, label in self.P2_FIELD_PATTERNS:
            for match in re.finditer(pattern, content):
                items.append({
                    'marker_type': 'p2_field_name',
                    'content_preview': match.group(0)[:120],
                    'line_number': self._find_line_number(lines, match.start()),
                    'column': self._find_column(lines, match.start()),
                    'confidence': 0.85,
                    'suggested_action': 'encrypt',
                })

        # P3: Format matching
        for pattern, label in self.P3_FORMAT_PATTERNS:
            for match in re.finditer(pattern, content):
                items.append({
                    'marker_type': 'p3_format',
                    'content_preview': match.group(0)[:120],
                    'line_number': self._find_line_number(lines, match.start()),
                    'column': self._find_column(lines, match.start()),
                    'confidence': 0.75,
                    'suggested_action': 'review',
                })

        # P4: Semantic recognition in code blocks
        code_blocks = list(re.finditer(r'```(\w*)\n(.*?)```', content, re.DOTALL))
        for block in code_blocks:
            block_content = block.group(2)
            has_semantic = any(kw in block_content.lower() for kw in self.P4_SEMANTIC_KEYWORDS)
            if has_semantic:
                items.append({
                    'marker_type': 'p4_semantic',
                    'content_preview': block_content[:120],
                    'line_number': self._find_line_number(lines, block.start()),
                    'column': self._find_column(lines, block.start()),
                    'confidence': 0.5,
                    'suggested_action': 'review',
                })

        # P5: Position weight (boost confidence for deep nesting)
        items = self._apply_p5_weighting(items, content)

        # Deduplicate: merge overlapping matches, keep highest confidence
        items = self._deduplicate(items)

        elapsed = int((time.time() - start_time) * 1000)

        return {
            'items': items,
            'total_sensitive': len(items),
            'content_hash': hashlib.sha256(content.encode('utf-8')).hexdigest(),
            'scan_time_ms': elapsed,
        }

    def _apply_p5_weighting(self, items: List[Dict], content: str) -> List[Dict]:
        """P5: Boost confidence for content in deeply nested code blocks."""
        # Count nesting depth at each position
        depth_map = {}
        depth = 0
        for i, line in enumerate(content.split('\n')):
            if line.strip().startswith('```'):
                depth += 1
            depth_map[i + 1] = depth

        for item in items:
            item_depth = depth_map.get(item['line_number'], 0)
            if item_depth >= 3:
                item['confidence'] = min(1.0, item['confidence'] + 0.2)

        return items

    def _find_line_number(self, lines: List[str], position: int) -> int:
        char_count = 0
        for i, line in enumerate(lines, 1):
            char_count += len(line) + 1
            if char_count > position:
                return i
        return len(lines)

    def _find_column(self, lines: List[str], position: int) -> int:
        char_count = 0
        for line in lines:
            if char_count + len(line) + 1 > position:
                return position - char_count + 1
            char_count += len(line) + 1
        return 1

    def _deduplicate(self, items: List[Dict]) -> List[Dict]:
        """Deduplicate by position, keeping highest confidence."""
        seen = {}
        for item in items:
            key = (item['line_number'], item['content_preview'][:40])
            if key not in seen or item['confidence'] > seen[key]['confidence']:
                seen[key] = item
        # Also deduplicate by exact content match
        content_seen = set()
        result = []
        for item in seen.values():
            content_key = item['content_preview']
            if content_key not in content_seen:
                content_seen.add(content_key)
                result.append(item)
        # Sort by line number
        result.sort(key=lambda x: (x['line_number'], -x['confidence']))
        return result


# ============================================================================
# ContentEncryptor
# ============================================================================

class ContentEncryptor:
    """
    Encrypts skill content with AES-256-GCM.
    The content_key itself is encrypted with the platform RSA public key.
    """

    def encrypt_content(self, content: str, public_key_pem: str) -> Dict[str, Any]:
        """
        Encrypt full skill content with AES-256-GCM.
        Returns encrypted data + RSA-encrypted content key.
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives import serialization, hashes
            from cryptography.hazmat.primitives.asymmetric import padding

            # Generate content key (256-bit)
            content_key = AESGCM.generate_key(bit_length=256)
            aesgcm = AESGCM(content_key)

            # Generate random 96-bit IV (12 bytes - GCM standard)
            iv = os.urandom(12)

            # Encrypt content
            plaintext = content.encode('utf-8')
            ciphertext = aesgcm.encrypt(iv, plaintext, None)

            # Split ciphertext and tag (GCM appends tag to ciphertext)
            # AES-GCM: ciphertext + tag (16 bytes)
            actual_ciphertext = ciphertext[:-16]
            tag = ciphertext[-16:]

            # Encrypt content_key with RSA public key (OAEP)
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            key_ciphertext = public_key.encrypt(
                content_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            return {
                'content_key_ciphertext': key_ciphertext.hex(),
                'encrypted_content': actual_ciphertext.hex(),
                'iv_hex': iv.hex(),
                'tag_hex': tag.hex(),
                'algorithm': 'AES-256-GCM',
            }

        except ImportError:
            logger.error("cryptography library not available")
            raise
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def encryption_params(self) -> Dict[str, Any]:
        """Return encryption parameter metadata."""
        return {
            'algorithm': 'AES-256-GCM',
            'key_length': 256,
            'iv_length': 12,
            'tag_length': 16,
        }


# ============================================================================
# Skill2PackageBuilder
# ============================================================================

class Skill2PackageBuilder:
    """Builds and uploads the .skill2 package structure."""

    def build_manifest(
        self,
        skill_id: int,
        skill_name: str,
        declaration_id: str,
        content_hash: str,
        author_id: int,
        author_name: str,
        version: str,
        price: int = 0,
    ) -> Dict[str, Any]:
        """Build the manifest.json content."""
        return {
            'skill2_version': '1.0.0',
            'identity': {
                'skill_id': f"skill_{skill_id}",
                'declaration_id': declaration_id,
                'name': skill_name,
                'version': version or '1.0.0',
            },
            'author': {
                'author_id': f"author_{author_id}",
                'name': author_name,
            },
            'fee': {
                'type': 'one-time' if price > 0 else 'free',
                'amount': price,
                'currency': 'CNY',
            },
            'content': {
                'encrypted': True,
                'checksum': f"sha256:{content_hash}",
            },
        }

    def build_preview(self, skill_description: str, theme_description: Optional[str] = None) -> str:
        """Build a preview markdown (unencrypted overview)."""
        parts = []
        if theme_description:
            parts.append(f"## 主题\n\n{theme_description}\n")
        if skill_description:
            parts.append(f"## 简介\n\n{skill_description}\n")
        parts.append(
            "---\n\n"
            "此技能已通过 Skill2 加密保护。\n"
            "需要有效的 License Token 才能解密运行。\n"
        )
        return '\n'.join(parts)

    def upload_package(
        self,
        skill_id: int,
        declaration_id: str,
        manifest: Dict[str, Any],
        encrypted_content: str,
        signature: str,
        preview_content: str,
        iv_hex: str,
        tag_hex: str,
    ) -> Dict[str, Any]:
        """Upload all .skill2 package files to TOS."""
        try:
            from core.config import get_tos_config
            from modules.storage.tos_client import get_tos_client

            tos_config = get_tos_config()
            client = get_tos_client({
                'endpoint': tos_config.endpoint,
                'region': 'cn-shanghai',
                'bucket': tos_config.bucket,
                'access_key': tos_config.access_key,
                'secret_key': tos_config.secret_key,
                'custom_domain': tos_config.custom_domain,
            })

            cfg = get_skill2_config()
            base_key = f"{cfg.tos_prefix}{skill_id}/{declaration_id[:8]}/"

            # Upload manifest.json
            manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2, default=_json_serial)
            manifest_result = client.upload_file(
                f"{base_key}manifest.json",
                manifest_json.encode('utf-8'),
                'application/json',
            )

            # Upload skill.md.enc (hex-encoded ciphertext)
            enc_result = client.upload_file(
                f"{base_key}skill.md.enc",
                encrypted_content.encode('utf-8'),
                'application/octet-stream',
            )

            # Upload signature
            sig_result = client.upload_file(
                f"{base_key}signature",
                signature.encode('utf-8'),
                'application/octet-stream',
            )

            # Upload _internal/preview.md
            internal_prefix = f"{base_key}_internal/"
            client.upload_file(
                f"{internal_prefix}preview.md",
                preview_content.encode('utf-8'),
                'text/markdown',
            )

            logger.info(f"Skill2 package uploaded: {base_key}")

            return {
                'package_url': f"{base_key}",
                'manifest_url': manifest_result.get('url', ''),
                'enc_url': enc_result.get('url', ''),
                'sig_url': sig_result.get('url', ''),
            }

        except Exception as e:
            logger.error(f"Failed to upload skill2 package: {e}")
            raise


# ============================================================================
# Skill2Service (Orchestrator)
# ============================================================================

class Skill2Service:
    """
    Orchestrates the full Skill2 pipeline:
    scan -> encrypt -> sign -> package -> upload -> store
    """

    def __init__(self):
        self.key_service = PlatformKeyService()
        self.scanner = SensitiveContentScanner()
        self.encryptor = ContentEncryptor()
        self.builder = Skill2PackageBuilder()

    def ensure_tables(self):
        """Create required database tables."""
        self.key_service.ensure_tables()

    def get_active_key(self) -> Optional[Dict[str, Any]]:
        return self.key_service.get_active_key()

    def generate_key_pair(self) -> Optional[Dict[str, Any]]:
        return self.key_service.generate_key_pair()

    # ----------------------------------------------------------------
    # Scan
    # ----------------------------------------------------------------

    def scan_skill_content(self, skill_id: int) -> Optional[Dict[str, Any]]:
        """
        Run P1-P5 scan on a skill's code_content.
        Stores scan results in skill2_packages table.
        """
        from modules.skills.services import skill_service

        skill = skill_service.get_skill_by_id(skill_id)
        if not skill:
            logger.warning(f"Skill {skill_id} not found for scanning")
            return None

        content = skill.get('code_content', '')
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Check if already scanned with same content
        existing = self.get_processing_status(skill_id)
        if existing and existing.get('status') in ('scanned', 'packaged'):
            if existing.get('content_hash') == content_hash:
                logger.info(f"Skill {skill_id} already scanned (content unchanged)")
                return existing

        # Run scan
        scan_result = self.scanner.scan(content)

        # Store in DB
        with get_db_cursor() as cur:
            # Check for existing record
            cur.execute(
                "SELECT id FROM skill2_packages WHERE skill_id = %s ORDER BY created_at DESC LIMIT 1",
                (skill_id,)
            )
            existing_record = cur.fetchone()

            if existing_record:
                cur.execute("""
                    UPDATE skill2_packages
                    SET status = 'scanned',
                        scan_summary = %s,
                        sensitive_count = %s,
                        content_hash = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    json.dumps(scan_result, default=_json_serial),
                    scan_result['total_sensitive'],
                    scan_result['content_hash'],
                    existing_record['id'],
                ))
            else:
                cur.execute("""
                    INSERT INTO skill2_packages
                        (skill_id, status, scan_summary, sensitive_count, content_hash)
                    VALUES (%s, 'scanned', %s, %s, %s)
                """, (
                    skill_id,
                    json.dumps(scan_result, default=_json_serial),
                    scan_result['total_sensitive'],
                    scan_result['content_hash'],
                ))

        return {
            'skill_id': skill_id,
            'status': 'scanned',
            'total_sensitive': scan_result['total_sensitive'],
            'items': scan_result['items'],
            'scan_time_ms': scan_result['scan_time_ms'],
            'content_hash': scan_result['content_hash'],
        }

    # ----------------------------------------------------------------
    # Full Pipeline (background task)
    # ----------------------------------------------------------------

    def process_full_pipeline(self, skill_id: int) -> Optional[Dict[str, Any]]:
        """
        Full pipeline: scan -> encrypt -> sign -> package -> upload -> store.
        Runs in caller's thread (should be called as background task).
        """
        from modules.skills.services import skill_service

        try:
            # Update status to scanning
            with get_db_cursor() as cur:
                cur.execute(
                    "UPDATE skill2_packages SET status = 'scanning', updated_at = CURRENT_TIMESTAMP "
                    "WHERE skill_id = %s AND status IN ('pending', 'scanned')",
                    (skill_id,)
                )

            skill = skill_service.get_skill_by_id(skill_id)
            if not skill:
                raise ValueError(f"Skill {skill_id} not found")

            content = skill.get('code_content', '')
            skill_name = skill.get('name', 'Unknown')
            skill_desc = skill.get('description', '')
            theme_desc = skill.get('theme_description', '')
            author_id = skill.get('author_id', 0)
            author_name = skill.get('author_username', 'unknown')
            version = skill.get('version', '1.0.0')
            price = skill.get('price', 0)

            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            declaration_id = f"decl_{uuid.uuid4()}"

            # Step 1: Scan
            scan_result = self.scanner.scan(content)

            # Step 2: Get platform key
            platform_key = self.key_service.get_active_key()
            if not platform_key:
                raise RuntimeError("No active platform key. Generate one first.")

            # Step 3: Encrypt content
            enc_result = self.encryptor.encrypt_content(content, platform_key['public_key'])

            # Step 4: Build manifest
            manifest = self.builder.build_manifest(
                skill_id=skill_id,
                skill_name=skill_name,
                declaration_id=declaration_id,
                content_hash=content_hash,
                author_id=author_id,
                author_name=author_name,
                version=version,
                price=price,
            )

            # Step 5: Sign manifest
            manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2, default=_json_serial)
            signature = self.key_service.sign(
                manifest_json.encode('utf-8'),
                platform_key['private_key'],
            )

            # Step 6: Build preview
            preview = self.builder.build_preview(skill_desc, theme_desc)

            # Step 7: Upload to TOS
            urls = self.builder.upload_package(
                skill_id=skill_id,
                declaration_id=declaration_id,
                manifest=manifest,
                encrypted_content=enc_result['encrypted_content'],
                signature=signature,
                preview_content=preview,
                iv_hex=enc_result['iv_hex'],
                tag_hex=enc_result['tag_hex'],
            )

            # Step 8: Update database records
            package_hash = hashlib.sha256(manifest_json.encode('utf-8')).hexdigest()

            with get_db_cursor() as cur:
                # Update skill2_packages
                cur.execute("""
                    UPDATE skill2_packages
                    SET status = 'packaged',
                        declaration_id = %s,
                        scan_summary = %s,
                        sensitive_count = %s,
                        content_key_ciphertext = %s,
                        encrypted_content = %s,
                        encryption_iv = %s,
                        encryption_tag = %s,
                        preview_content = %s,
                        package_url = %s,
                        manifest_url = %s,
                        package_hash = %s,
                        platform_signature = %s,
                        content_hash = %s,
                        key_version = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE skill_id = %s
                """, (
                    declaration_id,
                    json.dumps(scan_result, default=_json_serial),
                    scan_result['total_sensitive'],
                    enc_result['content_key_ciphertext'],
                    enc_result['encrypted_content'],
                    enc_result['iv_hex'],
                    enc_result['tag_hex'],
                    preview,
                    urls['package_url'],
                    urls['manifest_url'],
                    package_hash,
                    signature,
                    content_hash,
                    platform_key['key_version'],
                    skill_id,
                ))

                # Update skills.platform_signature
                cur.execute(
                    "UPDATE skills SET platform_signature = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (signature, skill_id)
                )

            logger.info(f"Skill2 pipeline complete for skill {skill_id}: {urls['manifest_url']}")

            return {
                'skill_id': skill_id,
                'status': 'packaged',
                'declaration_id': declaration_id,
                'content_hash': content_hash,
                'key_version': platform_key['key_version'],
                'platform_signature': signature,
                'package_url': urls['package_url'],
                'manifest_url': urls['manifest_url'],
            }

        except Exception as e:
            logger.error(f"Skill2 pipeline failed for skill {skill_id}: {e}")
            with get_db_cursor() as cur:
                cur.execute(
                    "UPDATE skill2_packages SET status = 'failed', error_message = %s, updated_at = CURRENT_TIMESTAMP "
                    "WHERE skill_id = %s",
                    (str(e), skill_id)
                )
            return None

    # ----------------------------------------------------------------
    # Status / Query
    # ----------------------------------------------------------------

    def get_processing_status(self, skill_id: int) -> Optional[Dict[str, Any]]:
        """Get the current processing status for a skill."""
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT * FROM skill2_packages
                    WHERE skill_id = %s
                    ORDER BY created_at DESC LIMIT 1
                """, (skill_id,))
                return cur.fetchone()
        except Exception as e:
            logger.warning(f"Failed to get processing status for {skill_id}: {e}")
            return None

    # ----------------------------------------------------------------
    # License & Usage (API stubs for Agent integration)
    # ----------------------------------------------------------------

    def verify_license(
        self,
        declaration_id: str,
        license_token: str,
        device_fingerprint: str,
    ) -> Dict[str, Any]:
        """
        Verify a license token for a skill.
        Returns session key if valid.
        """
        # Placeholder: actual implementation will validate License Token
        # against platform_keys and content_key_ciphertext
        logger.info(f"License verify requested: decl={declaration_id[:16]}...")
        return {
            'status': 'success',
            'session_key': f"sk_{uuid.uuid4().hex[:16]}",
            'author_id': None,
            'expires_in': 3600,
        }

    def log_usage(self, data: Dict[str, Any]) -> bool:
        """Log skill usage for tracking/analytics."""
        logger.info(f"Usage logged: skill={data.get('skill_id')}, type={data.get('usage_type')}")
        return True

    def get_developer_stats(self, author_id: int) -> Dict[str, Any]:
        """Get usage and revenue stats for a developer."""
        # Placeholder: will aggregate from usage logs
        return {
            'total_uses': 0,
            'total_revenue': 0.0,
            'skills': [],
        }


# Singleton
skill2_service = Skill2Service()
