#!/usr/bin/env python3
"""
配置发布工具 - 快速发布新配置到服务器
使用方法: python quick_publish.py --version v1.0.1 --notes "新增国风动漫风格"
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# 配置
API_BASE_URL = "https://www.jcoding.chat/application/com.jcoding.aiactivity"
LOCAL_ASSETS_PATH = "../android/app/src/main/assets"


def calculate_md5(file_path):
    """计算文件MD5"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def build_file_list(version_path):
    """构建文件列表"""
    files = []
    for root, dirs, filenames in os.walk(version_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, version_path)

            file_stat = os.stat(file_path)
            file_info = {
                'path': rel_path.replace('\\', '/'),
                'size': file_stat.st_size,
                'md5': calculate_md5(file_path),
                'url': f'/api/config/file?version={os.path.basename(version_path)}&path={rel_path.replace(os.sep, "/")}',
                'compressed': filename.endswith('.gz') or filename.endswith('.zip'),
                'essential': filename.endswith('.json')
            }
            files.append(file_info)

    return files


def prepare_version(version, assets_path, output_path):
    """准备版本文件"""
    version_dir = os.path.join(output_path, version)

    print(f"准备版本 {version}...")

    # 创建版本目录
    os.makedirs(version_dir, exist_ok=True)

    # 复制配置文件
    config_types = ['style', 'question', 'lottery', 'aibeing']
    for config_type in config_types:
        src_dir = os.path.join(assets_path, config_type)
        if os.path.exists(src_dir):
            dst_dir = os.path.join(version_dir, config_type)
            os.makedirs(dst_dir, exist_ok=True)

            # 复制所有文件
            for item in os.listdir(src_dir):
                src = os.path.join(src_dir, item)
                dst = os.path.join(dst_dir, item)
                if os.path.isdir(src):
                    os.system(f'cp -r "{src}" "{dst}"')
                else:
                    os.system(f'cp "{src}" "{dst}"')
            print(f"  ✓ {config_type}/")

    # 构建版本清单
    version_code = int(version.replace('v', '').replace('.', '').ljust(3, '0'))
    manifest = {
        'version': version,
        'version_code': version_code,
        'released_at': datetime.utcnow().isoformat() + 'Z',
        'force_update': False,
        'min_compatible_version': version,
        'release_notes': '',
        'files': build_file_list(version_dir),
        'deleted_files': []
    }

    # 保存清单
    manifest_path = os.path.join(version_dir, 'manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"  ✓ manifest.json ({len(manifest['files'])} 个文件)")

    return version_dir


def publish_to_server(version_dir, version, notes, force_update=False):
    """发布到服务器"""
    import requests

    print(f"\n发布到服务器 {API_BASE_URL}...")

    # 读取清单
    manifest_path = os.path.join(version_dir, 'manifest.json')
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # 更新发布信息
    manifest['release_notes'] = notes
    manifest['force_update'] = force_update

    # 发布请求
    url = f"{API_BASE_URL}/api/config/publish"
    payload = {
        'version': version,
        'release_notes': notes,
        'force_update': force_update,
        'min_compatible_version': version,
        'source_dir': os.path.abspath(version_dir)
    }

    print(f"POST {url}")
    print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result.get('code') == 200:
            print(f"\n✓ 发布成功!")
            print(f"  版本: {version}")
            print(f"  文件数: {len(manifest['files'])}")
            print(f"  说明: {notes}")
            return True
        else:
            print(f"\n✗ 发布失败: {result.get('message')}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n✗ 网络错误: {e}")
        print("\n请手动上传文件并发布:")
        print(f"1. 上传 {version_dir} 到服务器")
        print(f"2. 调用 API: POST {url}")
        print(f"   数据: {json.dumps(payload, indent=2)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='配置发布工具')
    parser.add_argument('--version', required=True, help='版本号 (如: v1.0.1)')
    parser.add_argument('--notes', default='', help='更新说明')
    parser.add_argument('--force', action='store_true', help='强制更新')
    parser.add_argument('--assets', default=LOCAL_ASSETS_PATH, help='Assets路径')
    parser.add_argument('--output', default='./config_publish', help='输出目录')
    parser.add_argument('--publish', action='store_true', help='自动发布到服务器')

    args = parser.parse_args()

    # 准备版本文件
    version_dir = prepare_version(args.version, args.assets, args.output)

    print(f"\n版本文件已准备: {version_dir}")
    print(f"\n下一步:")
    print(f"1. 上传整个 {version_dir} 目录到服务器")
    print(f"2. 调用发布API")

    if args.publish:
        publish_to_server(version_dir, args.version, args.notes, args.force)
    else:
        print(f"\n或使用此命令发布:")
        print(f"python quick_publish.py --version {args.version} --notes '{args.notes}' --publish")


if __name__ == '__main__':
    main()
