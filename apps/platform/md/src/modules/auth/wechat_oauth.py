"""
WeChat Open Platform OAuth Client
微信开放平台扫码登录

流程:
1. 前端请求 /api/v1/auth/wechat/qrcode 获取 OAuth URL
2. 前端生成 QR 码展示给用户
3. 用户微信扫码，确认登录
4. 微信重定向浏览器到 /wechat/callback?code=xxx&state=yyy
5. 后端用 code 换取 access_token，获取用户信息
6. 查 OauthMemberBind 表，已有绑定则登录，否则创建用户
7. 生成 JWT，设置 cookie，重定向到原始页面
"""
import os
import json
import ssl
import hashlib
import secrets
import logging
import time
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

WECHAT_OPEN_APPID = os.getenv("WECHAT_OPEN_APPID", "")
WECHAT_OPEN_SECRET = os.getenv("WECHAT_OPEN_SECRET", "")
WECHAT_OAUTH_STATE = os.getenv("WECHAT_OAUTH_STATE", "sillymd-oauth-state")
DOMAIN = os.getenv("FRONTEND_DOMAIN", "https://sillymd.com")

# Generate a Fernet key from the state secret for encrypting state
def _make_fernet_key(secret: str) -> bytes:
    return hashlib.sha256(secret.encode()).digest()
_fernet = Fernet(Fernet.generate_key())  # placeholder; replaced at first use
_fernet_initialized = False

def _get_fernet() -> Fernet:
    global _fernet, _fernet_initialized
    if not _fernet_initialized:
        import base64
        key = base64.urlsafe_b64encode(_make_fernet_key(WECHAT_OAUTH_STATE))
        _fernet = Fernet(key)
        _fernet_initialized = True
    return _fernet


# WeChat API endpoints
WECHAT_OAUTH_BASE = "https://open.weixin.qq.com"
WECHAT_API_BASE = "https://api.weixin.qq.com"


class WeChatOAuthClient:
    """微信开放平台 OAuth 客户端"""

    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or WECHAT_OPEN_APPID
        self.app_secret = app_secret or WECHAT_OPEN_SECRET
        self.callback_url = f"{DOMAIN}/api/v1/auth/wechat/callback"
        # Shared httpx client: bypass system proxy + permissive SSL for Python 3.8/Win
        _ssl_ctx = ssl.create_default_context()
        _ssl_ctx.check_hostname = False
        _ssl_ctx.verify_mode = ssl.CERT_NONE
        self._http = httpx.Client(verify=_ssl_ctx, trust_env=False, timeout=10.0)

    def get_oauth_url(self, redirect_url: str = "/", ticket: str = None) -> str:
        """
        获取微信扫码登录 URL

        Args:
            redirect_url: 登录成功后的跳转地址
            ticket: 二维码会话 ticket（用于内嵌 QR 码轮询）

        Returns:
            微信 OAuth 扫码 URL
        """
        # Encrypt state: redirect_url + timestamp + random nonce
        nonce = secrets.token_hex(8)
        state_data = {"redirect": redirect_url, "nonce": nonce, "ts": int(time.time())}
        if ticket:
            state_data["ticket"] = ticket
        state_data = json.dumps(state_data)
        state = _get_fernet().encrypt(state_data.encode()).decode()

        params = {
            "appid": self.app_id,
            "redirect_uri": self.callback_url,
            "response_type": "code",
            "scope": "snsapi_login",
            "state": state,
            "self_redirect": "false",
        }
        oauth_url = f"{WECHAT_OAUTH_BASE}/connect/qrconnect?{urlencode(params)}#wechat_redirect"
        logger.info(f"Generated OAuth URL for redirect to: {redirect_url}")
        return oauth_url

    def decrypt_state(self, state: str) -> Optional[Dict[str, Any]]:
        """解密 state 参数，返回 redirect_url, nonce, ts"""
        try:
            data = _get_fernet().decrypt(state.encode()).decode()
            return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to decrypt state: {e}")
            return None

    def get_access_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        用 code 换取 access_token

        Returns:
            {"access_token": "...", "expires_in": 7200, "refresh_token": "...",
             "openid": "...", "scope": "...", "unionid": "..."} or None
        """
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code",
        }
        url = f"{WECHAT_API_BASE}/sns/oauth2/access_token?{urlencode(params)}"

        try:
            resp = self._http.get(url)
            data = resp.json()
            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat access_token error: {data}")
                return None
            logger.info(f"Got access_token for openid={data.get('openid')}")
            return data
        except Exception as e:
            logger.error(f"Failed to get access_token: {e}")
            return None

    def get_user_info(self, access_token: str, openid: str) -> Optional[Dict[str, Any]]:
        """
        获取微信用户信息

        Returns:
            {"openid": "...", "nickname": "...", "sex": 1,
             "headimgurl": "...", "unionid": "...", ...} or None
        """
        params = {
            "access_token": access_token,
            "openid": openid,
        }
        url = f"{WECHAT_API_BASE}/sns/userinfo?{urlencode(params)}"

        try:
            resp = self._http.get(url)
            data = resp.json()
            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat userinfo error: {data}")
                return None
            logger.info(f"Got user info for openid={openid}, nickname={data.get('nickname')}")
            return data
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None


# Singleton
wechat_oauth = WeChatOAuthClient()
