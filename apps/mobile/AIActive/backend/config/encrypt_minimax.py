#!/usr/bin/env python3
"""
MiniMax凭证加密工具
使用与Android端相同的加密算法
"""
import base64
import hashlib
import os
import struct
import hmac
from Crypto.Cipher import AES

# 配置常量（与Android端保持一致）
SALT = b"JC_AI_CONFIG_SALT_2026"
ITERATIONS = 100000  # 测试用100K
KEY_SIZE = 32  # 256 bits
GCM_IV_LENGTH = 12  # 96 bits for GCM

def derive_key(version="v1.0.0"):
    """
    从版本号派生密钥（与Android端一致）
    v1.0.0 -> "100" -> PBKDF2 -> 256-bit key
    """
    # 转换版本号为数字字符串: "v1.0.0" -> "100"
    version_num = version.replace("v", "").replace(".", "")
    while len(version_num) < 3:
        version_num = version_num + "0"

    # 手动实现PBKDF2-HMAC-SHA256
    password = version_num.encode('utf-8')

    # 使用PRF计算密钥
    def prf(p, s):
        return hmac.new(p, s, hashlib.sha256).digest()

    # PBKDF2关键派生
    dk = b''
    block_index = 1
    while len(dk) < KEY_SIZE:
        # U1 = PRF(password, salt || INT_32_BE(i))
        # salt + i (big-endian 4 bytes)
        salt_with_index = SALT + struct.pack('>I', block_index)
        u = prf(password, salt_with_index)

        result = u
        # U2 ... Uc = PRF(password, U1) ... PRF(password, Uc-1)
        for _ in range(1, ITERATIONS):
            u = prf(password, u)
            result = bytes(x ^ y for x, y in zip(result, u))

        dk += result
        block_index += 1

    return dk[:KEY_SIZE]

def encrypt(plaintext, version="v1.0.0"):
    """
    加密明文字符串（与Android端一致）
    返回Base64编码的密文 (IV + ciphertext + auth_tag)
    """
    key = derive_key(version)

    # 生成随机IV
    iv = os.urandom(GCM_IV_LENGTH)

    # 创建AES-GCM加密器
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

    # 加密
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))

    # 组合 IV + ciphertext + tag
    combined = iv + ciphertext + tag

    # 返回Base64编码（无换行）
    return base64.b64encode(combined).decode('utf-8')

if __name__ == "__main__":
    # MiniMax凭证
    api_key = "REDACTED_MINIMAX_API_KEY_2"
    group_id = "REDACTED_MINIMAX_GROUP_ID_2"

    # 加密
    encrypted_api_key = encrypt(api_key, "v1.0.0")
    encrypted_group_id = encrypt(group_id, "v1.0.0")

    print("加密后的MiniMax凭证:")
    print(f'  "api_key": "{encrypted_api_key}",')
    print(f'  "group_id": "{encrypted_group_id}"')
