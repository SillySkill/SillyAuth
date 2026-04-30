"""
Credential Encryption Utility
凭证加密工具

使用 Fernet 对称加密保护敏感凭证信息
"""
import base64
import os
import json
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

logger = logging.getLogger(__name__)

# 从环境变量获取加密密钥
# 如果未设置，将生成一个警告（生产环境必须设置）
ENCRYPTION_KEY = os.getenv("CREDENTIAL_ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    logger.warning(
        "CREDENTIAL_ENCRYPTION_KEY 环境变量未设置！"
        "敏感凭证将以明文存储。生产环境必须设置此密钥。"
    )
    _ENCRYPTION_ENABLED = False
else:
    _ENCRYPTION_ENABLED = True
    # 确保密钥长度正确（Fernet 需要 32 字节 base64 编码）
    if len(ENCRYPTION_KEY) != 44:
        # 如果不是标准长度，派生出一个固定长度的密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'sillymd_credential_salt',  # 固定 salt 用于密钥派生
            iterations=100000,
        )
        key_bytes = kdf.derive(ENCRYPTION_KEY.encode())
        _CIPHER = Fernet(base64.urlsafe_b64encode(key_bytes))
    else:
        _CIPHER = Fernet(ENCRYPTION_KEY.encode())


def encrypt_credentials(credentials: Dict[str, Any]) -> str:
    """
    加密凭证信息

    Args:
        credentials: 凭证字典

    Returns:
        加密后的 JSON 字符串（如果是 base64 编码的加密数据）
        或未加密的 JSON 字符串（如果加密未启用）
    """
    if not _ENCRYPTION_ENABLED:
        logger.warning("加密未启用，凭证将以明文存储")
        return json.dumps(credentials)

    try:
        # 转换为 JSON
        json_data = json.dumps(credentials)

        # 加密
        encrypted_bytes = _CIPHER.encrypt(json_data.encode('utf-8'))

        # 返回 base64 编码的加密数据
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

    except Exception as e:
        logger.error(f"凭证加密失败: {e}", exc_info=True)
        # 加密失败时返回明文（记录错误但不中断服务）
        return json.dumps(credentials)


def decrypt_credentials(encrypted_data: str) -> Dict[str, Any]:
    """
    解密凭证信息

    Args:
        encrypted_data: 加密的数据字符串

    Returns:
        解密后的凭证字典
    """
    if not _ENCRYPTION_ENABLED:
        # 尝试直接解析 JSON（兼容未加密的数据）
        try:
            return json.loads(encrypted_data)
        except json.JSONDecodeError:
            logger.error("解密未启用且数据不是有效的 JSON")
            return {}

    try:
        # 检查是否为加密数据（base64 编码）
        try:
            # 尝试解密
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = _CIPHER.decrypt(encrypted_bytes)
            return json.loads(decrypted_bytes.decode('utf-8'))
        except Exception:
            # 如果解密失败，可能是旧数据（未加密），尝试直接解析
            logger.warning("解密失败，尝试解析为明文 JSON（可能是旧数据）")
            return json.loads(encrypted_data)

    except Exception as e:
        logger.error(f"凭证解密失败: {e}", exc_info=True)
        return {}


def mask_sensitive_data(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """
    屏蔽敏感字段用于日志或显示

    Args:
        credentials: 原始凭证

    Returns:
        屏蔽后的凭证
    """
    masked = {}
    sensitive_keywords = ['secret', 'key', 'password', 'token', 'api_key', 'private_key']

    for key, value in credentials.items():
        if any(keyword in key.lower() for keyword in sensitive_keywords):
            # 只显示前 4 个字符和后 4 个字符
            value_str = str(value)
            if len(value_str) > 8:
                masked[key] = f"{value_str[:4]}...{value_str[-4:]}"
            else:
                masked[key] = "***"
        else:
            masked[key] = value

    return masked


def validate_credentials_fields(
    credentials: Dict[str, Any],
    required_fields: list
) -> tuple[bool, Optional[str]]:
    """
    验证凭证字段

    Args:
        credentials: 凭证字典
        required_fields: 必需字段列表

    Returns:
        (是否有效, 错误消息)
    """
    if not isinstance(credentials, dict):
        return False, "凭证必须是字典类型"

    for field in required_fields:
        if field not in credentials:
            return False, f"缺少必需字段: {field}"

        if not credentials[field]:
            return False, f"字段 {field} 不能为空"

    return True, None


# 导出
__all__ = [
    "encrypt_credentials",
    "decrypt_credentials",
    "mask_sensitive_data",
    "validate_credentials_fields",
    "_ENCRYPTION_ENABLED"
]
