# -*- coding: utf-8 -*-
"""
配置推送服务
管理推送任务、批量推送、进度跟踪和失败重试
"""

import json
import uuid
from datetime import datetime, timedelta
from threading import Thread, Lock
import logging

logger = logging.getLogger(__name__)


class PushService:
    """配置推送服务"""

    def __init__(self, db):
        """
        初始化推送服务

        Args:
            db: SQLAlchemy 数据库实例
        """
        self.db = db
        self.tasks = {}  # 内存中的任务缓存: {task_id: task_info}
        self.lock = Lock()

        # 加载未完成的任务
        self._load_pending_tasks()

        logger.info("推送服务初始化完成")

    def _load_pending_tasks(self):
        """从数据库加载未完成的任务"""
        # TODO: 从数据库加载状态为 pending/in_progress 的任务
        # 这里简化为空实现
        pass

    def create_push_task(self, config_version, target_devices=None, target_groups=None):
        """
        创建推送任务

        Args:
            config_version: 配置版本信息
                {
                    'version': 'v1.2.0',
                    'version_code': 120,
                    'force_update': False,
                    'release_notes': '更新说明',
                    'files': [
                        {
                            'path': 'config.json',
                            'size': 1024,
                            'md5': 'abc123...',
                            'url': '/api/config/file?path=config.json',
                            'compressed': False,
                            'essential': True
                        }
                    ]
                }
            target_devices: 目标设备ID列表，如果为None则推送到所有设备
            target_groups: 目标设备组列表

        Returns:
            task_id: 任务ID
        """
        task_id = str(uuid.uuid4())

        task_info = {
            'task_id': task_id,
            'version': config_version.get('version'),
            'version_code': config_version.get('version_code'),
            'force_update': config_version.get('force_update', False),
            'release_notes': config_version.get('release_notes', ''),
            'files': config_version.get('files', []),
            'target_devices': target_devices or [],
            'target_groups': target_groups or [],
            'status': 'pending',
            'total_devices': 0,
            'success_devices': 0,
            'failed_devices': 0,
            'pending_devices': [],
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'error_message': None
        }

        with self.lock:
            self.tasks[task_id] = task_info

        # TODO: 保存任务到数据库

        logger.info(f"推送任务已创建: task_id={task_id}, version={task_info['version']}")
        return task_id

    def start_push_task(self, task_id):
        """
        启动推送任务

        Args:
            task_id: 任务ID

        Returns:
            (success, message)
        """
        with self.lock:
            task_info = self.tasks.get(task_id)
            if not task_info:
                return False, "任务不存在"

            if task_info['status'] != 'pending':
                return False, f"任务状态为 {task_info['status']}，无法启动"

        # 获取目标设备列表
        target_devices = self._get_target_devices(task_info)

        if not target_devices:
            with self.lock:
                task_info['status'] = 'completed'
                task_info['completed_at'] = datetime.now().isoformat()
            return False, "没有可推送的设备"

        # 更新任务状态
        with self.lock:
            task_info['status'] = 'in_progress'
            task_info['total_devices'] = len(target_devices)
            task_info['pending_devices'] = target_devices
            task_info['started_at'] = datetime.now().isoformat()

        # 异步执行推送
        thread = Thread(target=self._execute_push_task, args=(task_id,))
        thread.daemon = True
        thread.start()

        logger.info(f"推送任务已启动: task_id={task_id}, target_count={len(target_devices)}")
        return True, f"任务已启动，目标设备数: {len(target_devices)}"

    def _get_target_devices(self, task_info):
        """获取目标设备列表"""
        # 如果指定了设备，直接返回
        if task_info['target_devices']:
            return task_info['target_devices']

        # TODO: 根据设备组获取设备列表
        if task_info['target_groups']:
            # 这里需要从数据库查询设备组对应的设备
            pass

        # TODO: 获取所有活跃设备
        # 这里需要从数据库查询所有活跃设备
        return []

    def _execute_push_task(self, task_id):
        """执行推送任务（在独立线程中运行）"""
        from websocket.push_server import send_to_device, is_device_connected

        task_info = self.tasks.get(task_id)
        if not task_info:
            logger.error(f"任务不存在，无法执行: task_id={task_id}")
            return

        target_devices = task_info['pending_devices'][:]
        push_data = {
            'push_id': task_id,
            'version': task_info['version'],
            'version_code': task_info['version_code'],
            'force_update': task_info['force_update'],
            'release_notes': task_info['release_notes'],
            'files': task_info['files']
        }

        for device_id in target_devices:
            try:
                # 检查任务是否被取消
                with self.lock:
                    if self.tasks[task_id]['status'] == 'cancelled':
                        logger.info(f"任务已取消，停止推送: task_id={task_id}")
                        break

                # 检查设备是否在线
                if is_device_connected(device_id):
                    # 发送推送通知
                    send_to_device(device_id, 'config_update', push_data)
                    logger.info(f"配置推送已发送: device_id={device_id}, task_id={task_id}")
                else:
                    # 设备离线，等待连接后推送
                    logger.info(f"设备离线，等待连接: device_id={device_id}, task_id={task_id}")

                    # TODO: 保存待推送信息到数据库
                    # 这样设备连接时会自动获取

                # 避免推送过快
                import time
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"推送到设备失败: device_id={device_id}, error={e}")

                with self.lock:
                    task_info['failed_devices'] += 1

        # 更新任务状态
        with self.lock:
            task_info['status'] = 'completed'
            task_info['completed_at'] = datetime.now().isoformat()

        logger.info(f"推送任务完成: task_id={task_id}, "
                   f"total={task_info['total_devices']}, "
                   f"success={task_info['success_devices']}, "
                   f"failed={task_info['failed_devices']}")

    def cancel_push_task(self, task_id):
        """
        取消推送任务

        Args:
            task_id: 任务ID

        Returns:
            (success, message)
        """
        with self.lock:
            task_info = self.tasks.get(task_id)
            if not task_info:
                return False, "任务不存在"

            if task_info['status'] in ['completed', 'cancelled']:
                return False, f"任务已{task_info['status']}，无法取消"

            task_info['status'] = 'cancelled'

        # TODO: 更新数据库

        logger.info(f"推送任务已取消: task_id={task_id}")
        return True, "任务已取消"

    def get_task_status(self, task_id):
        """
        获取推送任务状态

        Args:
            task_id: 任务ID

        Returns:
            task_info: 任务信息字典
        """
        with self.lock:
            return self.tasks.get(task_id)

    def get_pending_push(self, device_id):
        """
        获取设备的待推送配置（设备连接时调用）

        Args:
            device_id: 设备ID

        Returns:
            push_info: 推送信息，如果没有则返回None
        """
        # TODO: 从数据库查询该设备的待推送配置
        # 这里简化为查找内存中的任务

        with self.lock:
            for task_id, task_info in self.tasks.items():
                if task_info['status'] == 'in_progress':
                    if device_id in task_info['target_devices'] or not task_info['target_devices']:
                        return {
                            'push_id': task_id,
                            'version': task_info['version'],
                            'version_code': task_info['version_code'],
                            'force_update': task_info['force_update'],
                            'release_notes': task_info['release_notes'],
                            'files': task_info['files']
                        }

        return None

    def on_config_ack(self, device_id, push_id, status, message, received_files, failed_files):
        """
        处理配置确认回调

        Args:
            device_id: 设备ID
            push_id: 推送任务ID
            status: 确认状态 (success/failed)
            message: 消息
            received_files: 已接收的文件列表
            failed_files: 失败的文件列表
        """
        logger.info(f"配置确认: device_id={device_id}, push_id={push_id}, status={status}")

        with self.lock:
            task_info = self.tasks.get(push_id)
            if task_info and task_info['status'] == 'in_progress':
                if status == 'success':
                    task_info['success_devices'] += 1
                else:
                    task_info['failed_devices'] += 1

                # 从待推送列表中移除
                if device_id in task_info['pending_devices']:
                    task_info['pending_devices'].remove(device_id)

        # TODO: 更新数据库记录
        # 记录设备的推送结果

    def on_device_disconnected(self, device_id):
        """设备断开连接时的回调"""
        logger.info(f"设备断开连接: device_id={device_id}")
        # TODO: 更新设备在线状态

    def on_device_status(self, device_id, status_info):
        """设备状态上报回调"""
        logger.debug(f"设备状态: device_id={device_id}, status={status_info}")
        # TODO: 保存设备状态到数据库

    def on_device_error(self, device_id, error_msg):
        """设备错误回调"""
        logger.error(f"设备错误: device_id={device_id}, error={error_msg}")
        # TODO: 记录错误到数据库

    def get_all_tasks(self):
        """获取所有任务列表"""
        with self.lock:
            return list(self.tasks.values())

    def cleanup_old_tasks(self, days=7):
        """清理旧任务（保留最近N天的任务）"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self.lock:
            to_delete = []
            for task_id, task_info in self.tasks.items():
                created_at = datetime.fromisoformat(task_info['created_at'])
                if created_at < cutoff_time and task_info['status'] == 'completed':
                    to_delete.append(task_id)

            for task_id in to_delete:
                del self.tasks[task_id]

        logger.info(f"清理了 {len(to_delete)} 个旧任务")
        return len(to_delete)
