"""
TOS Client - 火山引擎对象存储客户端封装

提供 TOS 对象存储的基本操作接口
"""

import hashlib
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

import requests
import tos
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tos.exceptions import TosServerError

logger = logging.getLogger(__name__)


def _retry_reconnect(retry_state):
    """Callback to reconnect the TOS client before a retry sleep."""
    instance = retry_state.args[0] if retry_state.args else None
    if instance and hasattr(instance, '_reconnect'):
        logger.warning(
            f"Reconnecting TOS client before retry attempt {retry_state.attempt_number}..."
        )
        instance._reconnect()


class TosClient:
    """
    TOS (Volcengine Object Storage) 客户端封装类

    提供文件上传、下载、删除、签名URL等基本操作
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 TOS 客户端

        Args:
            config: TOS 配置字典，包含:
                - endpoint: TOS 端点地址
                - bucket: 存储桶名称
                - access_key: 访问密钥
                - secret_key: 秘密密钥
                - custom_domain: 自定义域名 (可选)
        """
        self.endpoint = config.get("endpoint", "tos-cn-shanghai.volces.com")
        self.region = config.get("region", "cn-shanghai")
        self.bucket = config.get("bucket", "")
        self.custom_domain = config.get("custom_domain", "")
        self.access_key = config.get("access_key", "")
        self.secret_key = config.get("secret_key", "")

        # 创建 TOS 客户端
        self._client: Optional[tos.TosClientV2] = None
        self._init_client()

    def _init_client(self):
        """初始化 TOS 客户端实例"""
        if not self.access_key or not self.secret_key:
            logger.warning("TOS credentials not configured, client will not be functional")
            return

        try:
            self._client = tos.TosClientV2(
                self.access_key,
                self.secret_key,
                self.endpoint,
                region=self.region
            )
            logger.info(f"TOS client initialized for bucket: {self.bucket}, region: {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize TOS client: {e}")
            raise

    def _reconnect(self):
        """Reinitialize the TOS client instance on connection failure."""
        logger.warning("Attempting to reconnect TOS client...")
        self._init_client()

    def _ensure_client(self) -> tos.TosClientV2:
        """确保客户端已初始化"""
        if self._client is None:
            raise RuntimeError("TOS client not initialized. Check credentials configuration.")
        return self._client

    def _generate_checksum(self, content: bytes) -> str:
        """生成文件 MD5 校验和"""
        return hashlib.md5(content).hexdigest()

    def _build_url(self, key: str) -> str:
        """构建文件访问 URL"""
        if self.custom_domain:
            return f"https://{self.custom_domain}/{key}"
        return f"https://{self.bucket}.{self.endpoint}/{key}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TosServerError, ConnectionError, TimeoutError, requests.exceptions.ConnectionError)),
        before_sleep=_retry_reconnect,
        reraise=True
    )
    def upload_file(
        self,
        key: str,
        content: bytes,
        content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """
        上传文件到 TOS

        Args:
            key: 文件存储的 key (路径)
            content: 文件内容 (bytes)
            content_type: 文件的 MIME 类型

        Returns:
            Dict 包含:
                - url: 文件访问 URL
                - size: 文件大小
                - checksum: 文件 MD5 校验和

        Raises:
            RuntimeError: 客户端未初始化
            TosServerError: TOS 服务端错误（重试后仍失败）
        """
        client = self._ensure_client()
        checksum = self._generate_checksum(content)

        # 上传文件（瞬态错误由 retry 装饰器处理）
        result = client.put_object(
            bucket=self.bucket,
            key=key,
            content=content,
            content_type=content_type
        )

        logger.info(f"File uploaded successfully: {key}, size: {len(content)}")

        return {
            "url": self._build_url(key),
            "key": key,
            "size": len(content),
            "checksum": checksum,
            "etag": result.etag if hasattr(result, 'etag') else None
        }

    def upload_file_from_file(
        self,
        key: str,
        file_path: str,
        content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """
        从本地文件上传到 TOS

        Args:
            key: 文件存储的 key (路径)
            file_path: 本地文件路径
            content_type: 文件的 MIME 类型

        Returns:
            Dict 包含: url, size, checksum
        """
        with open(file_path, 'rb') as f:
            content = f.read()
        return self.upload_file(key, content, content_type)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TosServerError, ConnectionError, TimeoutError, requests.exceptions.ConnectionError)),
        before_sleep=_retry_reconnect,
        reraise=True
    )
    def download_file(self, key: str) -> bytes:
        """
        从 TOS 下载文件

        Args:
            key: 文件的存储 key

        Returns:
            文件内容 (bytes)

        Raises:
            RuntimeError: 客户端未初始化
            TosServerError: TOS 服务端错误（重试后仍失败）或文件不存在
        """
        client = self._ensure_client()

        # 下载文件（瞬态错误由 retry 装饰器处理，404 为业务逻辑错误直接抛出）
        try:
            result = client.get_object(
                bucket=self.bucket,
                key=key
            )
        except TosServerError as e:
            if e.status_code == 404:
                logger.warning(f"File not found: {key}")
                raise TosServerError(404, "Not Found", f"File not found: {key}")
            raise

        # 读取内容
        content = result.read()
        logger.info(f"File downloaded successfully: {key}, size: {len(content)}")
        return content

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((TosServerError, ConnectionError, TimeoutError, requests.exceptions.ConnectionError)),
        before_sleep=_retry_reconnect,
        reraise=True
    )
    def delete_file(self, key: str) -> bool:
        """
        删除 TOS 上的文件

        Args:
            key: 文件的存储 key

        Returns:
            bool: 删除是否成功

        Raises:
            RuntimeError: 客户端未初始化
            TosServerError: TOS 服务端错误（重试后仍失败）
        """
        client = self._ensure_client()

        # 删除文件（瞬态错误由 retry 装饰器处理，404 为业务逻辑直接返回 False）
        try:
            client.delete_object(
                bucket=self.bucket,
                key=key
            )
        except TosServerError as e:
            if e.status_code == 404:
                logger.warning(f"File not found for deletion: {key}")
                return False
            raise
        logger.info(f"File deleted successfully: {key}")
        return True

    def get_signed_url(self, key: str, expires_seconds: int = 3600) -> str:
        """
        获取文件的签名访问 URL

        Args:
            key: 文件的存储 key
            expires_seconds: URL 有效期（秒），默认 1 小时

        Returns:
            str: 签名的访问 URL

        Raises:
            RuntimeError: 客户端未初始化
        """
        client = self._ensure_client()

        try:
            # 生成预签名 URL
            signed_url = client.pre_signed_url(
                bucket=self.bucket,
                key=key,
                expires=expires_seconds
            )
            logger.debug(f"Generated signed URL for {key}, expires in {expires_seconds}s")
            return signed_url

        except Exception as e:
            logger.error(f"Failed to generate signed URL for {key}: {e}")
            raise

    def list_files(self, prefix: str = "", max_keys: int = 100) -> List[str]:
        """
        列出指定前缀下的文件

        Args:
            prefix: 文件前缀/目录路径
            max_keys: 最大返回数量

        Returns:
            List[str]: 文件 key 列表

        Raises:
            RuntimeError: 客户端未初始化
        """
        client = self._ensure_client()
        keys = []

        try:
            # 列出对象
            result = client.list_objects(
                bucket=self.bucket,
                prefix=prefix,
                max_keys=max_keys
            )

            # 提取文件 key
            if hasattr(result, 'contents'):
                for obj in result.contents:
                    keys.append(obj.key)

            logger.info(f"Listed {len(keys)} files with prefix: {prefix}")
            return keys

        except Exception as e:
            logger.error(f"Failed to list files with prefix {prefix}: {e}")
            raise

    def file_exists(self, key: str) -> bool:
        """
        检查文件是否存在

        Args:
            key: 文件的存储 key

        Returns:
            bool: 文件是否存在

        Raises:
            RuntimeError: 客户端未初始化
        """
        client = self._ensure_client()

        try:
            client.head_object(
                bucket=self.bucket,
                key=key
            )
            return True

        except TosServerError as e:
            if e.status_code == 404:
                return False
            logger.error(f"Error checking file existence for {key}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking file existence: {e}")
            raise

    def get_file_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息

        Args:
            key: 文件的存储 key

        Returns:
            Dict 包含文件信息，或 None 如果文件不存在
        """
        client = self._ensure_client()

        try:
            result = client.head_object(
                bucket=self.bucket,
                key=key
            )

            # 转换 datetime 为字符串
            last_modified = result.last_modified
            if hasattr(last_modified, 'isoformat'):
                last_modified = last_modified.isoformat()

            return {
                "key": key,
                "size": result.content_length,
                "content_type": result.content_type,
                "last_modified": last_modified,
                "etag": result.etag
            }

        except TosServerError as e:
            if e.status_code == 404:
                return None
            logger.error(f"Error getting file info for {key}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting file info: {e}")
            raise

    def copy_file(self, source_key: str, dest_key: str) -> bool:
        """
        复制文件

        Args:
            source_key: 源文件 key
            dest_key: 目标文件 key

        Returns:
            bool: 复制是否成功
        """
        client = self._ensure_client()

        try:
            client.copy_object(
                bucket=self.bucket,
                key=dest_key,
                src_bucket=self.bucket,
                src_key=source_key
            )
            logger.info(f"File copied from {source_key} to {dest_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to copy file from {source_key} to {dest_key}: {e}")
            raise


# 全局客户端实例
_global_client: Optional[TosClient] = None


def get_tos_client(config: Optional[Dict[str, Any]] = None) -> TosClient:
    """
    获取全局 TOS 客户端实例

    Args:
        config: TOS 配置，如果为 None 则返回已存在的实例

    Returns:
        TosClient: TOS 客户端实例
    """
    global _global_client

    if config is not None:
        _global_client = TosClient(config)
        return _global_client

    if _global_client is None:
        raise RuntimeError("TOS client not initialized. Call get_tos_client(config) first.")
    return _global_client
