#!/usr/bin/env python3
"""
生成加密的配置文件
从现有的明文配置生成加密后的配置文件

用法:
    python generate_encrypted_config.py <input.json> <output.json> <version>

示例:
    python generate_encrypted_config.py config.plain.json config.encrypted.json v1.0.0

@author Claude Code
@since 2026-02-06
"""
import json
import sys
import os
import hashlib

# 添加父目录到路径以便导入 utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_crypto import encrypt


def calculate_md5(file_path: str) -> str:
    """计算文件的 MD5 哈希"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def generate_encrypted_config(input_file: str, output_file: str, version: str) -> dict:
    """
    生成加密配置

    :param input_file: 输入的明文配置文件路径
    :param output_file: 输出的加密配置文件路径
    :param version: 配置版本号 (e.g., "v1.0.0")
    :return: 加密后的配置字典
    """
    # 读取明文配置
    with open(input_file, 'r', encoding='utf-8') as f:
        plain_config = json.load(f)

    # 构建加密配置结构
    encrypted_config = {
        '_meta': {
            'version': version,
            'version_code': int(version.replace('v', '').replace('.', '')) * 10,
            'format_version': '1.0',
            'released_at': plain_config.get('_meta', {}).get('released_at', '2026-02-06T00:00:00Z'),
            'min_compatible_version': plain_config.get('_meta', {}).get('min_compatible_version', version)
        },
        'app': plain_config.get('app', {
            'name': 'AI活动秀',
            'debug': False,
            'log_level': 'info'
        }),
        'features': plain_config.get('features', {}),
        '_encrypted': {
            'api_keys': {},
            'admin': {},
            'llm': {}
        },
        'services': plain_config.get('services', {})
    }

    # 加密 API 密钥
    if 'api_keys' in plain_config:
        for service, keys in plain_config['api_keys'].items():
            encrypted_config['_encrypted']['api_keys'][service] = {}

            for key, value in keys.items():
                if not isinstance(value, str):
                    encrypted_config['_encrypted']['api_keys'][service][key] = value
                    continue

                # 注意：服务器额外加密（SERVER_ENC:）功能尚未实现
                # 当前所有字段都使用常规的版本号派生密钥加密
                # 未来高度敏感字段（api_key, secret_key）将使用服务器额外加密
                encrypted_value = encrypt(value, version)
                encrypted_config['_encrypted']['api_keys'][service][key] = encrypted_value

    # 加密管理员密码
    if 'admin' in plain_config:
        admin_config = plain_config['admin']
        if 'password' in admin_config:
            encrypted_config['_encrypted']['admin']['password'] = encrypt(
                admin_config['password'], version
            )

    # 加密 LLM 配置
    if 'llm' in plain_config:
        llm_config = plain_config['llm']
        if 'api_key' in llm_config:
            encrypted_config['_encrypted']['llm']['api_key'] = encrypt(
                llm_config['api_key'], version
            )
        if 'model_id' in llm_config:
            encrypted_config['_encrypted']['llm']['model_id'] = encrypt(
                llm_config['model_id'], version
            )

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(encrypted_config, f, ensure_ascii=False, indent=2)

    print(f"[OK] Encrypted config generated: {output_file}")

    # 计算 MD5
    md5_hash = calculate_md5(output_file)
    print(f"  MD5: {md5_hash}")
    print(f"  Size: {os.path.getsize(output_file)} bytes")

    return encrypted_config


def main():
    if len(sys.argv) < 4:
        print("Usage: python generate_encrypted_config.py <input.json> <output.json> <version>")
        print("\nExample:")
        print("  python generate_encrypted_config.py config.plain.json config.encrypted.json v1.0.0")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    version = sys.argv[3]

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    print(f"Generating encrypted config...")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print(f"  Version: {version}")
    print()

    try:
        generate_encrypted_config(input_file, output_file, version)
        print("\n[OK] Success!")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
