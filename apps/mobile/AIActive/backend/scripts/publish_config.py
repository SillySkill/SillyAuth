#!/usr/bin/env python3
"""
配置发布工具
用于发布新版本的配置文件到服务器

使用方法:
    python publish_config.py --version v1.0.1 --source ../media --notes "修复题库配置错误"

选项:
    --version: 版本号 (格式: v1.0.0)
    --source: 配置文件源目录
    --notes: 发布说明
    --force: 是否强制更新 (默认False)
    --min-version: 最低兼容版本
    --server: 服务器地址 (默认: http://localhost:5000)
"""
import os
import sys
import json
import hashlib
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict

import requests


class ConfigPublisher:
    """配置发布器"""

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.api_base = f"{self.server_url}/api/config"

    def publish(self, version: str, source_dir: str, release_notes: str,
                force_update: bool = False, min_compatible_version: str = None) -> Dict:
        """
        发布新版本配置

        Args:
            version: 版本号 (如 v1.0.1)
            source_dir: 配置文件源目录
            release_notes: 发布说明
            force_update: 是否强制更新
            min_compatible_version: 最低兼容版本

        Returns:
            发布结果
        """
        print(f"开始发布版本 {version}...")

        # 验证版本号格式
        if not version.startswith('v'):
            print("错误: 版本号必须以 'v' 开头 (如 v1.0.0)")
            return {'success': False, 'error': '版本号格式错误'}

        # 验证源目录
        source_path = Path(source_dir)
        if not source_path.exists():
            print(f"错误: 源目录不存在: {source_dir}")
            return {'success': False, 'error': '源目录不存在'}

        # 构建发布数据
        payload = {
            'version': version,
            'release_notes': release_notes,
            'force_update': force_update,
            'source_dir': str(source_path.absolute())
        }

        if min_compatible_version:
            payload['min_compatible_version'] = min_compatible_version

        # 发送发布请求
        try:
            url = f"{self.api_base}/publish"
            print(f"发送发布请求到: {url}")

            response = requests.post(url, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print(f"\n版本 {version} 发布成功！")
                    self._print_manifest(result.get('data', {}))
                    return {'success': True, 'data': result.get('data')}
                else:
                    print(f"发布失败: {result.get('message')}")
                    return {'success': False, 'error': result.get('message')}
            else:
                print(f"HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}

        except requests.exceptions.RequestException as e:
            print(f"网络请求失败: {e}")
            return {'success': False, 'error': str(e)}

    def push_notification(self, version: str, message: str, target_devices: List[str] = None) -> Dict:
        """
        推送更新通知到客户端

        Args:
            version: 版本号
            message: 推送消息
            target_devices: 目标设备列表 (空表示推送到所有设备)

        Returns:
            推送结果
        """
        print(f"推送更新通知: {version}...")

        payload = {
            'version': version,
            'message': message,
            'target_devices': target_devices or []
        }

        try:
            url = f"{self.api_base}/push"
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print("推送通知发送成功！")
                    return {'success': True, 'data': result.get('data')}
                else:
                    print(f"推送失败: {result.get('message')}")
                    return {'success': False, 'error': result.get('message')}
            else:
                print(f"HTTP错误: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}

        except requests.exceptions.RequestException as e:
            print(f"推送通知失败: {e}")
            return {'success': False, 'error': str(e)}

    def get_stats(self) -> Dict:
        """获取更新统计信息"""
        try:
            url = f"{self.api_base}/stats"
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return {'success': True, 'data': result.get('data')}
            return {'success': False, 'error': '获取统计失败'}

        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

    def _print_manifest(self, manifest: Dict):
        """打印版本清单"""
        print("\n" + "=" * 60)
        print("版本清单:")
        print("=" * 60)
        print(f"版本号: {manifest.get('version')}")
        print(f"版本代码: {manifest.get('version_code')}")
        print(f"发布时间: {manifest.get('released_at')}")
        print(f"强制更新: {'是' if manifest.get('force_update') else '否'}")
        print(f"最低兼容版本: {manifest.get('min_compatible_version')}")
        print(f"发布说明: {manifest.get('release_notes')}")
        print(f"文件数量: {len(manifest.get('files', []))}")
        print("=" * 60)


class LocalPublisher:
    """本地配置发布器（不需要服务器）"""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def publish(self, version: str, source_dir: str, release_notes: str,
                force_update: bool = False, min_compatible_version: str = None) -> Dict:
        """
        发布到本地存储

        Args:
            version: 版本号
            source_dir: 配置文件源目录
            release_notes: 发布说明
            force_update: 是否强制更新
            min_compatible_version: 最低兼容版本

        Returns:
            发布结果
        """
        print(f"开始发布版本 {version} 到本地存储...")

        # 验证版本号格式
        if not version.startswith('v'):
            return {'success': False, 'error': '版本号格式错误'}

        # 创建版本目录
        version_path = self.storage_path / version
        if version_path.exists():
            return {'success': False, 'error': f'版本 {version} 已存在'}

        version_path.mkdir(parents=True, exist_ok=True)

        # 复制配置文件
        source_path = Path(source_dir)
        file_count = 0

        for item in source_path.rglob('*'):
            if item.is_file():
                relative_path = item.relative_to(source_path)
                dest_file = version_path / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_file)
                file_count += 1
                print(f"  复制: {relative_path}")

        # 构建版本清单
        manifest = self._build_manifest(version, version_path)
        manifest['release_notes'] = release_notes
        manifest['force_update'] = force_update
        if min_compatible_version:
            manifest['min_compatible_version'] = min_compatible_version

        # 保存清单
        manifest_file = version_path / 'manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # 更新版本数据库
        self._update_version_db(version, manifest)

        print(f"\n版本 {version} 发布成功！共 {file_count} 个文件")
        self._print_manifest(manifest)

        return {'success': True, 'data': manifest}

    def _build_manifest(self, version: str, version_path: Path) -> Dict:
        """构建版本清单"""
        manifest = {
            'version': version,
            'version_code': self._parse_version_code(version),
            'released_at': datetime.utcnow().isoformat() + 'Z',
            'files': [],
            'deleted_files': []
        }

        # 遍历版本目录
        for file_path in version_path.rglob('*'):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(version_path)).replace('\\', '/')
                file_stat = file_path.stat()

                file_info = {
                    'path': relative_path,
                    'size': file_stat.st_size,
                    'md5': self._calculate_md5(file_path),
                    'url': f'/api/config/file?version={version}&path={relative_path}',
                    'compressed': relative_path.endswith(('.gz', '.zip')),
                    'essential': relative_path.endswith('.json')
                }
                manifest['files'].append(file_info)

        return manifest

    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件MD5"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def _parse_version_code(self, version: str) -> int:
        """解析版本代码"""
        version_str = version.replace('v', '').replace('.', '')
        return int(version_str.ljust(3, '0'))

    def _update_version_db(self, version: str, manifest: Dict):
        """更新版本数据库"""
        db_path = self.storage_path / 'versions.json'

        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
        else:
            db = {'versions': {}, 'current': 'v1.0.0'}

        db['versions'][version] = manifest
        db['current'] = version

        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

    def _print_manifest(self, manifest: Dict):
        """打印版本清单"""
        print("\n" + "=" * 60)
        print("版本清单:")
        print("=" * 60)
        print(f"版本号: {manifest.get('version')}")
        print(f"版本代码: {manifest.get('version_code')}")
        print(f"发布时间: {manifest.get('released_at')}")
        print(f"强制更新: {'是' if manifest.get('force_update') else '否'}")
        print(f"最低兼容版本: {manifest.get('min_compatible_version', 'N/A')}")
        print(f"发布说明: {manifest.get('release_notes')}")
        print(f"文件数量: {len(manifest.get('files', []))}")
        print("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='配置发布工具')
    parser.add_argument('--version', required=True, help='版本号 (如 v1.0.0)')
    parser.add_argument('--source', required=True, help='配置文件源目录')
    parser.add_argument('--notes', default='', help='发布说明')
    parser.add_argument('--force', action='store_true', help='是否强制更新')
    parser.add_argument('--min-version', help='最低兼容版本')
    parser.add_argument('--server', default='http://localhost:5000', help='服务器地址')
    parser.add_argument('--local', help='使用本地存储模式，指定存储路径')
    parser.add_argument('--push', action='store_true', help='发布后立即推送通知')
    parser.add_argument('--push-message', default='新版本可用，请更新', help='推送消息')

    args = parser.parse_args()

    # 选择发布模式
    if args.local:
        # 本地存储模式
        publisher = LocalPublisher(args.local)
    else:
        # 服务器模式
        publisher = ConfigPublisher(args.server)

    # 发布配置
    result = publisher.publish(
        version=args.version,
        source_dir=args.source,
        release_notes=args.notes,
        force_update=args.force,
        min_compatible_version=args.min_version
    )

    if result['success']:
        print("\n发布成功！")

        # 如果需要推送通知
        if args.push and isinstance(publisher, ConfigPublisher):
            publisher.push_notification(
                version=args.version,
                message=args.push_message
            )

        return 0
    else:
        print(f"\n发布失败: {result.get('error')}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
