"""
OpenClaw WebSocket 接收服务
将企业微信 WebSocket 消息存储到 OpenClaw 内存文件
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket 配置
WS_URL = "wss://webhook.sillymd.com/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20ifQ.SXPJEwegy41JcsUOCPbzMpfk7SriZB8G34G-tDm5Jlg"

# OpenClaw 目录配置
OPENCLAW_DIR = Path("d:/openclaw")
MEMORY_DIR = OPENCLAW_DIR / "memory"
WECHAT_LOG_FILE = MEMORY_DIR / f"wechat_{datetime.now().strftime('%Y-%m-%d')}.md"

# 设备配置
DEVICE_NAME = "openclaw_client_windows"


class OpenClawWebSocketClient:
    """OpenClaw WebSocket 客户端 - 接收企业微信消息并存储"""

    def __init__(self, ws_url: str, device_name: str):
        self.ws_url = f"{ws_url}"
        self.device_name = device_name
        self.is_connected = False
        self.message_count = 0

        # 确保 memory 目录存在
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

        # 初始化今日日志文件
        self._init_wechat_log()

    def _init_wechat_log(self):
        """初始化企业微信日志文件"""
        if not WECHAT_LOG_FILE.exists():
            content = f"""# 企业微信消息记录 - {datetime.now().strftime('%Y-%m-%d')}

> 本文件由 WebSocket 服务自动生成，记录从企业微信接收的消息

## 消息列表

"""
            WECHAT_LOG_FILE.write_text(content, encoding='utf-8')
            logger.info(f"[OpenClaw] 创建企业微信日志: {WECHAT_LOG_FILE}")

    async def connect(self):
        """连接到 WebSocket 服务器"""
        try:
            logger.info(f"[OpenClaw] 正在连接到 {self.ws_url}")

            async with websockets.connect(
                self.ws_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=5
            ) as websocket:
                self.is_connected = True
                logger.info("[OpenClaw] ✅ WebSocket 连接成功")

                # 接收连接确认消息
                try:
                    init_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    logger.info(f"[OpenClaw] 📨 收到初始化消息: {init_msg}")
                except asyncio.TimeoutError:
                    logger.warning("[OpenClaw] ⚠️  未收到初始化消息")

                # 发送设备绑定消息
                bind_message = {
                    "type": "bind",
                    "device_name": self.device_name
                }
                await websocket.send(json.dumps(bind_message))
                logger.info(f"[OpenClaw] 📤 发送绑定消息: {bind_message}")

                # 接收绑定确认
                try:
                    bound_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    logger.info(f"[OpenClaw] 📨 收到绑定确认: {bound_msg}")
                except asyncio.TimeoutError:
                    logger.error("[OpenClaw] ❌ 绑定超时")
                    return

                # 进入消息循环
                logger.info("[OpenClaw] 🎧 开始监听企业微信消息...")

                while True:
                    try:
                        # 接收消息
                        message = await asyncio.wait_for(websocket.recv(), timeout=300)
                        self.message_count += 1

                        # 解析并处理消息
                        try:
                            msg_data = json.loads(message)
                            await self._handle_message(msg_data)
                        except json.JSONDecodeError:
                            logger.debug(f"[OpenClaw] 收到非 JSON 消息: {message}")

                    except asyncio.TimeoutError:
                        # 发送心跳 ping
                        ping_msg = {"type": "ping"}
                        await websocket.send(json.dumps(ping_msg))
                        logger.debug("[OpenClaw] 💓 发送心跳 ping")

        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"[OpenClaw] ❌ 连接已关闭: {e.code} - {e.reason}")
        except Exception as e:
            logger.error(f"[OpenClaw] ❌ 连接异常: {e}")
        finally:
            self.is_connected = False

    async def _handle_message(self, msg_data: dict):
        """处理收到的消息"""
        msg_type = msg_data.get("type", "unknown")

        if msg_type == "wechat":
            # 企业微信消息 - 保存到 OpenClaw 内存
            await self._save_wechat_message(msg_data)

        elif msg_type == "ping":
            logger.debug("[OpenClaw] 💓 收到心跳 ping")

        elif msg_type == "status":
            logger.info(f"[OpenClaw] 📊 状态响应")

        elif msg_type == "error":
            logger.error(f"[OpenClaw] ❌ 错误消息: {msg_data}")

    async def _save_wechat_message(self, msg_data: dict):
        """保存企业微信消息到 OpenClaw 内存"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            data = msg_data.get("data", {})

            # 提取消息信息
            from_user = data.get("from_user", "未知")
            msg_type = data.get("msg_type", "unknown")
            content = self._extract_content(data)
            tenant_name = msg_data.get("tenant_name", "未知租户")

            # 构建日志条目
            log_entry = f"""

### [{timestamp}] 来自 {from_user} ({tenant_name})

**类型:** {msg_type}
**发送者:** {from_user}
**时间:** {msg_data.get('timestamp', '')}

**内容:**
{content}

---

"""

            # 追加到今日日志文件
            with open(WECHAT_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            self.message_count += 1
            logger.info(f"[OpenClaw] 💾 企业微信消息已保存: #{self.message_count} | 发送者: {from_user} | 类型: {msg_type}")

        except Exception as e:
            logger.error(f"[OpenClaw] ❌ 保存消息失败: {e}")

    def _extract_content(self, data: dict) -> str:
        """提取消息内容"""
        msg_type = data.get("msg_type", "unknown")

        if msg_type == "text":
            # 从 XML 中提取文本内容
            xml_content = data.get("xml_content", "")
            if "Content" in xml_content:
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(xml_content)
                    content_elem = root.find('Content')
                    if content_elem is not None:
                        return content_elem.text or "（空消息）"
                except:
                    pass
            return "（无法解析文本内容）"

        elif msg_type == "event":
            event = data.get("event", "未知事件")
            return f"事件: {event}"

        elif msg_type == "image":
            return "📷 [图片消息]"

        elif msg_type == "voice":
            return "🎤 [语音消息]"

        elif msg_type == "video":
            return "🎬 [视频消息]"

        else:
            return f"[{msg_type} 类型消息]"


async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         OpenClaw - 企业微信 WebSocket 接收服务                   ║
║                                                                    ║
║  功能: 接收企业微信消息并保存到 OpenClaw 内存文件                 ║
║  设备: openclaw_client_windows                                     ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    client = OpenClawWebSocketClient(
        ws_url=WS_URL,
        device_name=DEVICE_NAME
    )

    # 连接并监听（带自动重连）
    retry_count = 0
    max_retries = 100  # 持续运行

    while retry_count < max_retries:
        try:
            await client.connect()
            # 如果连接断开，等待后重连
            retry_count += 1
            if retry_count < max_retries:
                wait_time = min(60, 2 ** retry_count)
                logger.warning(f"[OpenClaw] 🔄 {wait_time}秒后重连 (第{retry_count}次)...")
                await asyncio.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info("\n[OpenClaw] 👋 用户中断，退出")
            break
        except Exception as e:
            logger.error(f"[OpenClaw] ❌ 异常: {e}")
            retry_count += 1
            await asyncio.sleep(5)

    logger.info("[OpenClaw] 🛑 服务已停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
