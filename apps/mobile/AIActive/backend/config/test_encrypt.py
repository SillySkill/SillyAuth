#!/usr/bin/env python3
"""
测试MiniMax凭证的加密/解密
"""
import base64
import hashlib
import os
import struct
import hmac
from Crypto.Cipher import AES

# 配置常量（与Android端保持一致）
SALT = b"JC_AI_CONFIG_SALT_2026"
ITERATIONS = 100000
KEY_SIZE = 32
GCM_IV_LENGTH = 12

def derive_key(version="v1.0.0"):
    version_num = version.replace("v", "").replace(".", "")
    while len(version_num) < 3:
        version_num = version_num + "0"

    password = version_num.encode('utf-8')

    def prf(p, s):
        return hmac.new(p, s, hashlib.sha256).digest()

    dk = b''
    block_index = 1
    while len(dk) < KEY_SIZE:
        salt_with_index = SALT + struct.pack('>I', block_index)
        u = prf(password, salt_with_index)
        result = u
        for _ in range(1, ITERATIONS):
            u = prf(password, u)
            result = bytes(x ^ y for x, y in zip(result, u))
        dk += result
        block_index += 1

    return dk[:KEY_SIZE]

def decrypt(ciphertext, version="v1.0.0"):
    """解密测试"""
    key = derive_key(version)

    # 解码Base64
    combined = base64.b64decode(ciphertext)

    # 提取IV和密文
    iv = combined[:GCM_IV_LENGTH]
    encrypted = combined[GCM_IV_LENGTH:]

    # 解密
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    plaintext = cipher.decrypt(encrypted)
    # 去除tag
    plaintext = plaintext[:-16]  # GCM tag是16字节

    return plaintext.decode('utf-8')

if __name__ == "__main__":
    # 读取加密后的值
    encrypted_api_key = "lmKkWEEK9Ui+0PPlkIAwM7KW6MZWku7t4WGXRbjxAiAYLPM9OI+NJg+xFVYjkiAuHYfPEw8KDmGGjuEPeZJ7SH3E2kbKiaBenFnraeCpw+h6iY3ThF4C8hgD+tEgcxqK7YLPDPq36eM/uJBEt45VxrRwc5RKwT2jlNCz7UaO6RfajPUu0TWpiHTi0W7bWxnIhTvCloite6HUVA=="
    encrypted_group_id = "WhvFPjPUPUZaQgrD/Ib0zw8IDKdp+Md6P6avoNwx/m6/bJG/tWZ7fKQgHhskKTY="

    print("测试解密:")
    try:
        decrypted_api = decrypt(encrypted_api_key)
        print(f"API Key: {decrypted_api}")
    except Exception as e:
        print(f"API Key解密失败: {e}")

    try:
        decrypted_group = decrypt(encrypted_group_id)
        print(f"Group ID: {decrypted_group}")
    except Exception as e:
        print(f"Group ID解密失败: {e}")
