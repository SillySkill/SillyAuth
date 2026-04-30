"""
应用配置管理API测试脚本
"""
import asyncio
import aiohttp
import json
from typing import Optional


# 配置
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


class ApplicationConfigAPITest:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _headers(self):
        """获取请求头"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    async def login(self, username: str, password: str):
        """管理员登录"""
        print("\n=== 测试登录 ===")
        url = f"{self.base_url}/api/admin/auth/login"
        data = {"username": username, "password": password}

        async with self.session.post(url, json=data) as response:
            result = await response.json()
            if result.get("code") == 200:
                self.token = result["data"]["token"]
                print(f"✓ 登录成功")
                print(f"  Token: {self.token[:50]}...")
                return True
            else:
                print(f"✗ 登录失败: {result}")
                return False

    async def test_get_config_list(self):
        """测试获取配置列表"""
        print("\n=== 测试获取配置列表 ===")
        url = f"{self.base_url}/api/admin/application/config"

        async with self.session.get(url, headers=self._headers()) as response:
            result = await response.json()
            if result.get("code") == 200:
                total = result["data"]["total"]
                print(f"✓ 获取列表成功，共 {total} 条记录")
                if total > 0:
                    first_config = result["data"]["list"][0]
                    print(f"  第一条: {first_config['app_name']} ({first_config['app_id']})")
                return result["data"]["list"]
            else:
                print(f"✗ 获取列表失败: {result}")
                return []

    async def test_get_config_by_app_id(self, app_id: str):
        """测试获取单个配置"""
        print(f"\n=== 测试获取配置: {app_id} ===")
        url = f"{self.base_url}/api/admin/application/config/{app_id}"

        async with self.session.get(url, headers=self._headers()) as response:
            result = await response.json()
            if result.get("code") == 200:
                config = result["data"]
                print(f"✓ 获取配置成功")
                print(f"  应用名称: {config['app_name']}")
                print(f"  版本: {config['version']}")
                print(f"  状态: {config['status']}")
                return config
            else:
                print(f"✗ 获取配置失败: {result}")
                return None

    async def test_get_config_schema(self, app_id: str):
        """测试获取配置结构"""
        print(f"\n=== 测试获取配置Schema: {app_id} ===")
        url = f"{self.base_url}/api/admin/application/config/{app_id}/schema"

        async with self.session.get(url, headers=self._headers()) as response:
            result = await response.json()
            if result.get("code") == 200:
                print(f"✓ 获取Schema成功")
                print(f"  包含字段: schema, default_config, ui_schema, current_config")
                return result["data"]
            else:
                print(f"✗ 获取Schema失败: {result}")
                return None

    async def test_validate_config(self, app_id: str, config: dict):
        """测试验证配置"""
        print(f"\n=== 测试验证配置: {app_id} ===")
        url = f"{self.base_url}/api/admin/application/config/{app_id}/validate"

        async with self.session.post(url, headers=self._headers(), json=config) as response:
            result = await response.json()
            if result.get("code") == 200:
                valid = result["data"]["valid"]
                errors = result["data"]["errors"]
                if valid:
                    print(f"✓ 配置验证通过")
                else:
                    print(f"✗ 配置验证失败:")
                    for error in errors:
                        print(f"  - {error}")
                return valid
            else:
                print(f"✗ 验证请求失败: {result}")
                return False

    async def test_partial_update_config(self, app_id: str, update_data: dict):
        """测试部分更新配置"""
        print(f"\n=== 测试部分更新配置: {app_id} ===")
        url = f"{self.base_url}/api/admin/application/config/{app_id}"

        print(f"  更新内容: {json.dumps(update_data, ensure_ascii=False)}")

        async with self.session.patch(url, headers=self._headers(), json=update_data) as response:
            result = await response.json()
            if result.get("code") == 200:
                print(f"✓ 更新成功")
                return result["data"]
            else:
                print(f"✗ 更新失败: {result}")
                return None

    async def test_reset_config(self, app_id: str):
        """测试重置配置"""
        print(f"\n=== 测试重置配置: {app_id} ===")
        url = f"{self.base_url}/api/admin/application/config/{app_id}/reset"

        async with self.session.post(url, headers=self._headers()) as response:
            result = await response.json()
            if result.get("code") == 200:
                print(f"✓ 重置成功")
                return result["data"]["config"]
            else:
                print(f"✗ 重置失败: {result}")
                return None

    async def test_get_config_history(self, app_id: str):
        """测试获取配置历史"""
        print(f"\n=== 测试获取配置历史: {app_id} ===")
        url = f"{self.base_url}/api/admin/application/config/{app_id}/history"

        async with self.session.get(url, headers=self._headers()) as response:
            result = await response.json()
            if result.get("code") == 200:
                total = result["data"]["total"]
                print(f"✓ 获取历史成功，共 {total} 条记录")
                if total > 0:
                    for log in result["data"]["list"][:3]:
                        print(f"  - {log['operation']}: {log['operation_desc']} ({log['created_at']})")
                return result["data"]["list"]
            else:
                print(f"✗ 获取历史失败: {result}")
                return []

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("应用配置管理API测试")
        print("=" * 60)

        # 1. 登录
        if not await self.login(ADMIN_USERNAME, ADMIN_PASSWORD):
            print("登录失败，终止测试")
            return

        # 2. 获取配置列表
        configs = await self.test_get_config_list()
        if not configs:
            print("没有配置数据，后续测试跳过")
            return

        app_id = configs[0]["app_id"]

        # 3. 获取单个配置
        await self.test_get_config_by_app_id(app_id)

        # 4. 获取配置Schema
        await self.test_get_config_schema(app_id)

        # 5. 验证配置
        test_config = {
            "app": {
                "name": "AI活动秀",
                "version": "1.0.0",
                "debug": True
            },
            "features": {
                "ai_show": {
                    "enabled": True,
                    "invite_code_mode": True,
                    "payment_mode": True,
                    "employee_mode": True,
                    "auto_close_time": 20
                },
                "quiz": {
                    "enabled": True,
                    "voice_input": False,
                    "push_prize": True
                },
                "lottery": {
                    "enabled": True,
                    "voice_trigger": False,
                    "push_winner": True
                },
                "inner_show": {
                    "enabled": True,
                    "digital_human_announce": True
                }
            }
        }
        await self.test_validate_config(app_id, test_config)

        # 6. 部分更新配置
        update_data = {
            "config": {
                "features": {
                    "quiz": {
                        "voice_input": True
                    }
                }
            }
        }
        await self.test_partial_update_config(app_id, update_data)

        # 7. 获取配置历史
        await self.test_get_config_history(app_id)

        # 8. 重置配置
        # await self.test_reset_config(app_id)  # 可选测试

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


async def main():
    """主函数"""
    async with ApplicationConfigAPITest(BASE_URL) as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
