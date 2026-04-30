"""
OpenClaw WebSocket 客户端 - 连接到 webhook-hub 服务器
用于接收企业微信消息的实时推送
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket 服务器配置
WS_URL = "wss://webhook.sillymd.com/ws"
# 使用用户ID=33的JWT token（傻小福和傻小黑的用户）
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMyIsImVtYWlsIjoiYWRtaW5Ac2lsbHltZC5jb20iLCJleHAiOjE4MDMzMDg0NjIsImlhdCI6MTc3MTc3MjQ2Mn0.ful0iaidNY5OGbf0rOUEvxSum_9Q7Jr7ZLd-jVVjuZU"

# 设备配置
DEVICE_NAME = "sillyHei"  # 与服务器推送目标设备名称一致
TENANT_ID = "51ae5b72-279c-4e39-88c0-a42c9f2b5be1"  # 傻小黑
# 或者使用傻小福的租户ID: "8101f5a6-cf39-4ddf-8f1e-875a9f53eeb4"


class OpenClawClient:
    """OpenClaw WebSocket 客户端"""

    def __init__(self, ws_url: str, token: str, device_name: str, tenant_id: str):
        self.ws_url = f"{ws_url}?token={token}"
        self.device_name = device_name
        self.tenant_id = tenant_id
        self.is_connected = False
        self.is_bound = False
        self.message_count = 0

    async def connect(self):
        """连接到 WebSocket 服务器"""
        try:
            logger.info(f"[客户端] 正在连接到 {self.ws_url}")

            async with websockets.connect(
                self.ws_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=5
            ) as websocket:
                self.is_connected = True
                logger.info("[客户端] ✅ WebSocket 连接成功")

                # 接收连接确认消息
                try:
                    init_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    logger.info(f"[客户端] 📨 收到初始化消息: {init_msg}")
                    self._print_json(init_msg)
                except asyncio.TimeoutError:
                    logger.warning("[客户端] ⚠️  未收到初始化消息")

                # 发送设备绑定消息
                # 注意: 当前服务器实现推送时不包含 tenant_id
                # 因此绑定时不传 tenant_id，使用格式: user_id:device_name
                bind_message = {
                    "type": "bind",
                    "device_name": self.device_name
                    # tenant_id 暂不传入，等待服务器端修复
                    # "tenant_id": self.tenant_id
                }
                await websocket.send(json.dumps(bind_message))
                logger.info(f"[客户端] 📤 发送绑定消息: {bind_message}")
                logger.info(f"[客户端] ℹ️  使用简化绑定格式 (不含 tenant_id) 以匹配服务器推送格式")

                # 接收绑定确认
                try:
                    bound_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    logger.info(f"[客户端] 📨 收到绑定确认: {bound_msg}")
                    self._print_json(bound_msg)

                    bound_data = json.loads(bound_msg)
                    if bound_data.get("type") == "bound":
                        self.is_bound = True
                        logger.info("[客户端] ✅ 设备绑定成功")
                except asyncio.TimeoutError:
                    logger.error("[客户端] ❌ 绑定超时")
                    return

                # 查询状态
                status_msg = {"type": "status"}
                await websocket.send(json.dumps(status_msg))

                # 进入消息循环
                logger.info("[客户端] 🎧 开始监听消息...")
                logger.info("[客户端] " + "="*60)

                message_count = 0
                while True:
                    try:
                        # 接收消息（带超时）
                        message = await asyncio.wait_for(websocket.recv(), timeout=300)
                        message_count += 1
                        self.message_count += 1

                        # 解析并打印消息
                        try:
                            msg_data = json.loads(message)
                            self._handle_message(msg_data)
                        except json.JSONDecodeError:
                            logger.info(f"[客户端] 📨 收到文本消息: {message}")

                    except asyncio.TimeoutError:
                        # 发送心跳ping
                        ping_msg = {"type": "ping"}
                        await websocket.send(json.dumps(ping_msg))
                        logger.debug("[客户端] 💓 发送心跳 ping")

        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"[客户端] ❌ 连接已关闭: {e.code} - {e.reason}")
        except Exception as e:
            logger.error(f"[客户端] ❌ 连接异常: {e}")
        finally:
            self.is_connected = False
            self.is_bound = False

    def _handle_message(self, msg_data: dict):
        """处理收到的消息"""
        msg_type = msg_data.get("type", "unknown")

        # 打印消息头
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info("")
        logger.info("="*80)
        logger.info(f"[客户端] 📨 [{timestamp}] 收到消息 #{self.message_count}")
        logger.info("="*80)

        if msg_type == "pong":
            logger.info("[客户端] 💓 心跳响应")

        elif msg_type == "status":
            logger.info(f"[客户端] 📊 状态响应")
            self._print_json(msg_data)

        elif msg_type == "webhook":
            logger.info(f"[客户端] 🎯 Webhook 推送消息")
            logger.info(f"  来源: {msg_data.get('source', 'unknown')}")
            logger.info(f"  目标设备: {msg_data.get('target_device', 'unknown')}")

            # 打印 webhook 数据
            webhook_data = msg_data.get('data', {})
            if isinstance(webhook_data, dict):
                logger.info(f"  租户ID: {webhook_data.get('tenant_id', 'unknown')}")
                logger.info(f"  路径: {webhook_data.get('path', 'unknown')}")
                logger.info(f"  方法: {webhook_data.get('method', 'unknown')}")
                logger.info(f"  来源IP: {webhook_data.get('source_ip', 'unknown')}")

                # 打印消息体
                body = webhook_data.get('body')
                if body:
                    logger.info(f"  消息内容:")
                    if body.startswith('<xml>'):
                        # 企业微信 XML 消息
                        logger.info(f"    {body[:200]}...")
                        self._parse_wechat_xml(body)
                    else:
                        logger.info(f"    {body[:200]}...")

        elif msg_type == "error":
            logger.error(f"[客户端] ❌ 错误消息: {msg_data}")

        else:
            logger.info(f"[客户端] 📦 未知类型消息: {msg_type}")
            self._print_json(msg_data)

        logger.info("")

    def _parse_wechat_xml(self, xml_content: str):
        """解析企业微信 XML 消息"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)

            # 提取关键信息
            from_user = root.find('FromUserName')
            msg_type = root.find('MsgType')
            content = root.find('Content')

            if from_user is not None:
                logger.info(f"    发送者: {from_user.text}")
            if msg_type is not None:
                logger.info(f"    消息类型: {msg_type.text}")
            if content is not None:
                logger.info(f"    内容: {content.text}")

        except Exception as e:
            logger.debug(f"[客户端] XML 解析跳过: {e}")

    def _print_json(self, data):
        """美化打印 JSON"""
        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            for line in json_str.split('\n'):
                logger.info(f"  {line}")
        except:
            logger.info(f"  {data}")


async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         OpenClaw WebSocket 客户端 - 企业微信消息接收           ║
║                                                                    ║
║  连接到: webhook.sillymd.com                                       ║
║  租户: 傻小黑 (51ae5b72)                                            ║
║  设备: openclaw_client_windows                                     ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # 创建客户端
    client = OpenClawClient(
        ws_url=WS_URL,
        token=JWT_TOKEN,
        device_name=DEVICE_NAME,
        tenant_id=TENANT_ID
    )

    # 连接并监听（带自动重连）
    retry_count = 0
    max_retries = 10

    while retry_count < max_retries:
        try:
            await client.connect()
            # 如果连接断开，等待后重连
            retry_count += 1
            if retry_count < max_retries:
                wait_time = min(60, 2 ** retry_count)
                logger.warning(f"[客户端] 🔄 {wait_time}秒后重连 (第{retry_count}次)...")
                await asyncio.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info("\n[客户端] 👋 用户中断，退出")
            break
        except Exception as e:
            logger.error(f"[客户端] ❌ 异常: {e}")
            retry_count += 1
            await asyncio.sleep(5)

    logger.info("[客户端] 🛑 客户端已停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
