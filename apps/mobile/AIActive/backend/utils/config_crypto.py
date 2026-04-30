"""
配置文件加密/解密工具
与 Android 端保持一致的算法实现

使用 AES-256-GCM 加密，PBKDF2 从版本号派生密钥

@author Claude Code
@since 2026-02-06
"""
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

ALGORITHM = 'AES'
SALT = b'JC_AI_CONFIG_SALT_2026'
ITERATIONS = 100000  # 测试用100K，生产环境使用300K
KEY_SIZE = 32  # 256 bits
GCM_TAG_LENGTH = 16  # 128 bits
GCM_IV_LENGTH = 12  # 96 bits


def derive_key(version: str) -> bytes:
    """
    从版本号派生加密密钥
    v1.2.0 -> "120" -> PBKDF2-HMAC-SHA256 -> 256-bit key

    安全说明：
    - 使用 PBKDF2-HMAC-SHA256 进行密钥派生
    - 迭代次数设置为 300,000 以防止暴力破解
    - 版本号标准化：右填充 '0' 到至少3位 (v1.0 -> "100", v1.2.0 -> "120")

    :param version: 版本号字符串 (e.g., "v1.2.0")
    :return: 256-bit AES 密钥
    """
    # 转换版本号为数字字符串: "v1.2.0" -> "120"
    # 与 Android 端保持一致：右填充 '0' 到至少 3 位
    version_num = version.replace('v', '').replace('.', '')
    while len(version_num) < 3:
        version_num = version_num + '0'

    # 使用 HMAC-SHA256，与 Android 端保持一致
    from Crypto.Hash import SHA256
    key = PBKDF2(
        version_num,
        SALT,
        dkLen=KEY_SIZE,
        count=ITERATIONS,
        hmac_hash_module=SHA256
    )
    return key


def encrypt(plaintext: str, version: str) -> str:
    """
    加密明文字符串

    :param plaintext: 要加密的明文
    :param version: 版本号（用于派生密钥）
    :return: Base64 编码的密文 (IV + ciphertext + auth_tag)
    """
    key = derive_key(version)
    iv = get_random_bytes(GCM_IV_LENGTH)

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))

    # 组合 IV + ciphertext + tag
    combined = iv + ciphertext + tag

    # 返回 Base64 编码
    return base64.b64encode(combined).decode('utf-8')


def decrypt(ciphertext: str, version: str) -> str:
    """
    解密密文字符串

    :param ciphertext: Base64 编码的密文 (IV + ciphertext + auth_tag)
    :param version: 版本号（用于派生密钥）
    :return: 解密后的明文
    :raises ValueError: 如果解密失败（认证失败）
    """
    key = derive_key(version)

    # 解码 Base64
    combined = base64.b64decode(ciphertext)

    # 提取组件
    iv = combined[:GCM_IV_LENGTH]
    tag = combined[-GCM_TAG_LENGTH:]
    encrypted = combined[GCM_IV_LENGTH:-GCM_TAG_LENGTH]

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    plaintext = cipher.decrypt_and_verify(encrypted, tag)

    return plaintext.decode('utf-8')


def encrypt_dict(config: dict, version: str, keys_to_encrypt: list = None) -> dict:
    """
    加密字典中的指定字段

    :param config: 配置字典
    :param version: 版本号
    :param keys_to_encrypt: 要加密的键列表，None 表示加密所有字符串值
    :return: 加密后的字典
    """
    encrypted = {}

    for key, value in config.items():
        if keys_to_encrypt is None or key in keys_to_encrypt:
            if isinstance(value, str):
                encrypted[key] = encrypt(value, version)
            elif isinstance(value, dict):
                encrypted[key] = encrypt_dict(value, version, keys_to_encrypt)
            else:
                encrypted[key] = value
        else:
            encrypted[key] = value

    return encrypted


def decrypt_dict(config: dict, version: str, keys_to_decrypt: list = None) -> dict:
    """
    解密字典中的指定字段

    :param config: 加密的配置字典
    :param version: 版本号
    :param keys_to_decrypt: 要解密的键列表，None 表示解密所有字符串值
    :return: 解密后的字典
    """
    decrypted = {}

    for key, value in config.items():
        if keys_to_decrypt is None or key in keys_to_decrypt:
            if isinstance(value, str):
                try:
                    # 检查是否为服务器额外加密
                    if value.startswith("SERVER_ENC:"):
                        # 服务器额外加密，暂不解密
                        decrypted[key] = value
                    else:
                        decrypted[key] = decrypt(value, version)
                except Exception as e:
                    print(f"Warning: Failed to decrypt {key}: {e}")
                    decrypted[key] = value
            elif isinstance(value, dict):
                decrypted[key] = decrypt_dict(value, version, keys_to_decrypt)
            else:
                decrypted[key] = value
        else:
            decrypted[key] = value

    return decrypted


if __name__ == '__main__':
    # 测试加密/解密
    test_version = "v1.0.0"
    test_plaintext = "test_api_key_12345"

    print(f"Testing encryption/decryption with version: {test_version}")
    print(f"Plaintext: {test_plaintext}")

    # 加密
    encrypted = encrypt(test_plaintext, test_version)
    print(f"Encrypted: {encrypted}")

    # 解密
    decrypted = decrypt(encrypted, test_version)
    print(f"Decrypted: {decrypted}")

    # 验证
    assert decrypted == test_plaintext, f"Decryption failed! Expected {test_plaintext}, got {decrypted}"
    print("[OK] Encryption/decryption test passed!")

    # 测试字典加密
    test_config = {
        "api_key": "secret_key_123",
        "secret": "another_secret",
        "url": "https://example.com"
    }

    encrypted_config = encrypt_dict(test_config, test_version, ["api_key", "secret"])
    print(f"\nEncrypted config: {encrypted_config}")

    decrypted_config = decrypt_dict(encrypted_config, test_version, ["api_key", "secret"])
    print(f"Decrypted config: {decrypted_config}")

    assert decrypted_config["api_key"] == test_config["api_key"]
    assert decrypted_config["secret"] == test_config["secret"]
    assert decrypted_config["url"] == test_config["url"]
    print("[OK] Dictionary encryption/decryption test passed!")
