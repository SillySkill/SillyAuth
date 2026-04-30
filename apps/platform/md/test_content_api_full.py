"""
完整的教程和下载资源API测试脚本
作为QA测试工程师执行的全面测试
"""
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import sys
import io

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class APItester:
    def __init__(self, base_url: str = "http://47.96.133.238:8000"):
        self.base_url = base_url
        self.test_results = []
        self.performance_data = []

    def time_request(self, method: str, url: str, **kwargs) -> tuple:
        """执行请求并计时"""
        start_time = time.time()
        response = requests.request(method, url, **kwargs)
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000

        return response, elapsed_ms

    def log_test(self, test_name: str, passed: bool, details: str, response_time: float, status_code: int = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "response_time_ms": response_time,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

        # 性能评级
        if response_time < 200:
            performance = "✅ 优秀"
        elif response_time < 500:
            performance = "⚠️ 良好"
        else:
            performance = "❌ 需要优化"

        status_icon = "✅" if passed else "❌"
        print(f"{status_icon} {test_name}")
        print(f"   状态码: {status_code}")
        print(f"   响应时间: {response_time:.2f}ms {performance}")
        print(f"   详情: {details}")
        print()

    def test_1_tutorials_list(self):
        """测试教程列表API"""
        print("=" * 80)
        print("测试 1: 教程列表 API")
        print("=" * 80)

        # 基础列表测试
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?limit=5")
        passed = response.status_code == 200

        if passed:
            data = response.json()
            details = f"返回 {len(data.get('data', {}).get('items', []))} 条教程，总数: {data.get('data', {}).get('total', 0)}"
        else:
            details = f"返回错误: {response.text[:100]}"

        self.log_test("教程列表 - 基础查询", passed, details, elapsed, response.status_code)

    def test_2_tutorials_filtering(self):
        """测试教程筛选功能"""
        print("=" * 80)
        print("测试 2: 教程筛选功能")
        print("=" * 80)

        # 按分类筛选
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?category=claude-code&limit=5")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"分类筛选结果: {len(data.get('data', {}).get('items', []))} 条"
        else:
            details = f"分类筛选失败: {response.text[:100]}"
        self.log_test("教程列表 - 分类筛选", passed, details, elapsed, response.status_code)

        # 按难度筛选
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?difficulty=beginner&limit=5")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"难度筛选结果: {len(data.get('data', {}).get('items', []))} 条"
        else:
            details = f"难度筛选失败: {response.text[:100]}"
        self.log_test("教程列表 - 难度筛选", passed, details, elapsed, response.status_code)

        # 关键词搜索
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?search=Claude&limit=5")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"搜索结果: {len(data.get('data', {}).get('items', []))} 条"
        else:
            details = f"搜索失败: {response.text[:100]}"
        self.log_test("教程列表 - 关键词搜索", passed, details, elapsed, response.status_code)

        # 组合筛选
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?category=claude-code&difficulty=beginner&limit=5")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"组合筛选结果: {len(data.get('data', {}).get('items', []))} 条"
        else:
            details = f"组合筛选失败: {response.text[:100]}"
        self.log_test("教程列表 - 组合筛选", passed, details, elapsed, response.status_code)

    def test_3_tutorials_detail(self):
        """测试教程详情API"""
        print("=" * 80)
        print("测试 3: 教程详情 API")
        print("=" * 80)

        # 先获取一个教程ID
        response, _ = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?limit=1")
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('items', [])
            if items:
                tutorial_id = items[0]['id']
                tutorial_slug = items[0]['slug']

                # 测试通过ID获取详情
                response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/{tutorial_id}")
                passed = response.status_code == 200
                if passed:
                    detail_data = response.json()
                    chapters_count = len(detail_data.get('data', {}).get('chapters', []))
                    details = f"教程标题: {detail_data.get('data', {}).get('title')}, 章节数: {chapters_count}"
                else:
                    details = f"获取详情失败: {response.text[:100]}"
                self.log_test(f"教程详情 - ID查询 (ID={tutorial_id})", passed, details, elapsed, response.status_code)

                # 测试通过slug获取详情
                response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/{tutorial_slug}")
                passed = response.status_code == 200
                if passed:
                    detail_data = response.json()
                    details = f"通过slug获取详情成功: {detail_data.get('data', {}).get('title')}"
                else:
                    details = f"通过slug获取详情失败: {response.text[:100]}"
                self.log_test(f"教程详情 - Slug查询 (slug={tutorial_slug})", passed, details, elapsed, response.status_code)
            else:
                self.log_test("教程详情", False, "没有可用的教程数据", 0, 404)
        else:
            self.log_test("教程详情", False, "无法获取教程列表", 0, response.status_code)

    def test_4_downloads_list(self):
        """测试下载资源列表API"""
        print("=" * 80)
        print("测试 4: 下载资源列表 API")
        print("=" * 80)

        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/downloads/?limit=5")
        passed = response.status_code == 200

        if passed:
            data = response.json()
            details = f"返回 {len(data.get('data', {}).get('items', []))} 条资源，总数: {data.get('data', {}).get('total', 0)}"
        else:
            details = f"返回错误: {response.text[:100]}"

        self.log_test("下载资源列表 - 基础查询", passed, details, elapsed, response.status_code)

    def test_5_downloads_detail(self):
        """测试下载资源详情API"""
        print("=" * 80)
        print("测试 5: 下载资源详情 API")
        print("=" * 80)

        # 先获取一个资源ID
        response, _ = self.time_request("GET", f"{self.base_url}/api/content/downloads/?limit=1")
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('items', [])
            if items:
                download_id = items[0]['id']
                download_slug = items[0]['slug']

                # 测试通过ID获取详情
                response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/downloads/{download_id}")
                passed = response.status_code == 200
                if passed:
                    detail_data = response.json()
                    versions_count = len(detail_data.get('data', {}).get('versions', []))
                    details = f"资源标题: {detail_data.get('data', {}).get('title')}, 版本数: {versions_count}"
                else:
                    details = f"获取详情失败: {response.text[:100]}"
                self.log_test(f"下载资源详情 - ID查询 (ID={download_id})", passed, details, elapsed, response.status_code)

                # 测试通过slug获取详情
                response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/downloads/{download_slug}")
                passed = response.status_code == 200
                if passed:
                    detail_data = response.json()
                    details = f"通过slug获取详情成功: {detail_data.get('data', {}).get('title')}"
                else:
                    details = f"通过slug获取详情失败: {response.text[:100]}"
                self.log_test(f"下载资源详情 - Slug查询 (slug={download_slug})", passed, details, elapsed, response.status_code)
            else:
                self.log_test("下载资源详情", False, "没有可用的资源数据", 0, 404)
        else:
            self.log_test("下载资源详情", False, "无法获取资源列表", 0, response.status_code)

    def test_6_statistics(self):
        """测试统计API"""
        print("=" * 80)
        print("测试 6: 统计 API")
        print("=" * 80)

        # 教程分类统计
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/categories")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            categories = data.get('data', {})
            details = f"分类数: {len(categories)}, 有数据的分类: {sum(1 for c in categories.values() if c['count'] > 0)}"
        else:
            details = f"获取分类统计失败: {response.text[:100]}"
        self.log_test("教程分类统计", passed, details, elapsed, response.status_code)

        # 下载资源分类统计
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/downloads/categories")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            categories = data.get('data', {})
            details = f"分类数: {len(categories)}, 有数据的分类: {sum(1 for c in categories.values() if c['count'] > 0)}"
        else:
            details = f"获取分类统计失败: {response.text[:100]}"
        self.log_test("下载资源分类统计", passed, details, elapsed, response.status_code)

        # 精选教程
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/featured?limit=6")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            items = data.get('data', {}).get('items', [])
            details = f"精选教程数: {len(items)}"
        else:
            details = f"获取精选教程失败: {response.text[:100]}"
        self.log_test("精选教程列表", passed, details, elapsed, response.status_code)

    def test_7_interactions(self):
        """测试交互功能"""
        print("=" * 80)
        print("测试 7: 交互功能 API")
        print("=" * 80)

        # 先获取一个教程ID
        response, _ = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?limit=1")
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('items', [])
            if items:
                tutorial_id = items[0]['id']

                # 记录浏览
                response, elapsed = self.time_request("POST", f"{self.base_url}/api/content/tutorials/{tutorial_id}/view")
                passed = response.status_code == 200
                if passed:
                    view_data = response.json()
                    details = f"浏览次数: {view_data.get('data', {}).get('view_count')}"
                else:
                    details = f"记录浏览失败: {response.text[:100]}"
                self.log_test("交互 - 记录浏览", passed, details, elapsed, response.status_code)

                # 点赞
                response, elapsed = self.time_request("POST", f"{self.base_url}/api/content/tutorials/{tutorial_id}/like")
                passed = response.status_code == 200
                if passed:
                    like_data = response.json()
                    details = f"点赞数: {like_data.get('data', {}).get('like_count')}"
                else:
                    details = f"点赞失败: {response.text[:100]}"
                self.log_test("交互 - 点赞", passed, details, elapsed, response.status_code)
            else:
                self.log_test("交互功能", False, "没有可用的教程数据", 0, 404)
        else:
            self.log_test("交互功能", False, "无法获取教程列表", 0, response.status_code)

        # 测试下载记录
        response, _ = self.time_request("GET", f"{self.base_url}/api/content/downloads/?limit=1")
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('items', [])
            if items:
                download_id = items[0]['id']

                response, elapsed = self.time_request("POST", f"{self.base_url}/api/content/downloads/{download_id}/download")
                passed = response.status_code == 200
                if passed:
                    details = "下载记录成功"
                else:
                    details = f"记录下载失败: {response.text[:100]}"
                self.log_test("交互 - 记录下载", passed, details, elapsed, response.status_code)

    def test_8_pagination(self):
        """测试分页功能"""
        print("=" * 80)
        print("测试 8: 分页功能")
        print("=" * 80)

        # 测试分页参数
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?page=1&page_size=5")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            page_info = data.get('data', {})
            details = f"当前页: {page_info.get('page')}, 页大小: {page_info.get('page_size')}, 总页数: {page_info.get('total_pages')}"
        else:
            details = f"分页测试失败: {response.text[:100]}"
        self.log_test("分页功能 - 基础分页", passed, details, elapsed, response.status_code)

    def test_9_data_integrity(self):
        """测试数据完整性"""
        print("=" * 80)
        print("测试 9: 数据完整性验证")
        print("=" * 80)

        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?limit=1")
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('items', [])
            if items:
                tutorial = items[0]

                # 检查必需字段
                required_fields = ['id', 'tutorial_key', 'slug', 'title', 'description', 'category', 'difficulty']
                missing_fields = [f for f in required_fields if f not in tutorial]

                if not missing_fields:
                    details = f"所有必需字段存在，数据结构完整"
                    passed = True
                else:
                    details = f"缺少字段: {', '.join(missing_fields)}"
                    passed = False

                self.log_test("数据完整性 - 教程列表字段", passed, details, elapsed, response.status_code)

                # 测试详情数据完整性
                tutorial_id = tutorial['id']
                response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/{tutorial_id}")
                if response.status_code == 200:
                    detail_data = response.json()
                    tutorial_detail = detail_data.get('data', {})

                    # 检查详情字段
                    detail_fields = ['id', 'tutorial_key', 'slug', 'title', 'description', 'content', 'chapters']
                    missing_detail_fields = [f for f in detail_fields if f not in tutorial_detail]

                    if not missing_detail_fields:
                        details = f"详情数据完整，章节数: {len(tutorial_detail.get('chapters', []))}"
                        passed = True
                    else:
                        details = f"详情缺少字段: {', '.join(missing_detail_fields)}"
                        passed = False

                    self.log_test("数据完整性 - 教程详情字段", passed, details, elapsed, response.status_code)

    def test_10_error_handling(self):
        """测试错误处理"""
        print("=" * 80)
        print("测试 10: 错误处理")
        print("=" * 80)

        # 测试不存在的教程
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/999999")
        passed = response.status_code == 404
        details = f"预期的404错误: {response.text[:100] if passed else '未返回404'}"
        self.log_test("错误处理 - 不存在的教程", passed, details, elapsed, response.status_code)

        # 测试无效的分页参数
        response, elapsed = self.time_request("GET", f"{self.base_url}/api/content/tutorials/?page=0")
        passed = response.status_code == 422  # Validation error
        details = f"验证错误处理: {response.text[:100] if passed else '未处理无效参数'}"
        self.log_test("错误处理 - 无效分页参数", passed, details, elapsed, response.status_code)

    def generate_report(self):
        """生成测试报告"""
        print("=" * 80)
        print("测试报告摘要")
        print("=" * 80)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # 计算平均响应时间
        avg_response_time = sum(r['response_time_ms'] for r in self.test_results) / total_tests if total_tests > 0 else 0

        # 性能统计
        excellent_count = sum(1 for r in self.test_results if r['response_time_ms'] < 200)
        good_count = sum(1 for r in self.test_results if 200 <= r['response_time_ms'] < 500)
        poor_count = sum(1 for r in self.test_results if r['response_time_ms'] >= 500)

        print(f"\n总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"通过率: {pass_rate:.1f}%")
        print(f"\n平均响应时间: {avg_response_time:.2f}ms")
        print(f"性能评级:")
        print(f"  ✅ 优秀 (<200ms): {excellent_count}")
        print(f"  ⚠️ 良好 (200-500ms): {good_count}")
        print(f"  ❌ 需要优化 (>500ms): {poor_count}")

        # 失败的测试
        if failed_tests > 0:
            print(f"\n失败的测试:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ❌ {result['test_name']}: {result['details']}")

        print("\n" + "=" * 80)

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
            "avg_response_time_ms": avg_response_time,
            "excellent_count": excellent_count,
            "good_count": good_count,
            "poor_count": poor_count,
            "test_results": self.test_results
        }

    def save_report(self, report_data: dict, filename: str):
        """保存测试报告到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 教程和下载资源API测试报告\n\n")
            f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 测试摘要\n\n")
            f.write(f"- **总测试数**: {report_data['total_tests']}\n")
            f.write(f"- **通过**: {report_data['passed_tests']} ✅\n")
            f.write(f"- **失败**: {report_data['failed_tests']} ❌\n")
            f.write(f"- **通过率**: {report_data['pass_rate']:.1f}%\n")
            f.write(f"- **平均响应时间**: {report_data['avg_response_time_ms']:.2f}ms\n\n")

            f.write("## 性能统计\n\n")
            f.write(f"- ✅ **优秀** (<200ms): {report_data['excellent_count']}\n")
            f.write(f"- ⚠️ **良好** (200-500ms): {report_data['good_count']}\n")
            f.write(f"- ❌ **需要优化** (>500ms): {report_data['poor_count']}\n\n")

            f.write("## 测试详情\n\n")

            for result in report_data['test_results']:
                status_icon = "✅" if result['passed'] else "❌"
                f.write(f"### {status_icon} {result['test_name']}\n\n")
                f.write(f"- **状态码**: {result['status_code']}\n")
                f.write(f"- **响应时间**: {result['response_time_ms']:.2f}ms\n")
                f.write(f"- **详情**: {result['details']}\n")
                f.write(f"- **时间**: {result['timestamp']}\n\n")

            f.write("## 发现的问题\n\n")

            issues = [r for r in report_data['test_results'] if not r['passed']]
            if issues:
                for issue in issues:
                    f.write(f"### ❌ {issue['test_name']}\n\n")
                    f.write(f"{issue['details']}\n\n")
            else:
                f.write("没有发现问题 ✅\n\n")

            f.write("## 修复建议\n\n")

            if report_data['poor_count'] > 0:
                f.write("### 性能优化\n\n")
                f.write("- 检查数据库查询优化\n")
                f.write("- 考虑添加数据库索引\n")
                f.write("- 实施API响应缓存\n\n")

            if report_data['pass_rate'] < 100:
                f.write("### 功能修复\n\n")
                for issue in issues:
                    f.write(f"- 修复 {issue['test_name']}: {issue['details']}\n")
                f.write("\n")

        print(f"\n测试报告已保存到: {filename}")


def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("教程和下载资源API - 完整测试套件")
    print("=" * 80)
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {sys.argv[1] if len(sys.argv) > 1 else 'http://47.96.133.238:8000'}")
    print("=" * 80 + "\n")

    # 初始化测试器
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://47.96.133.238:8000"
    tester = APItester(base_url)

    # 执行所有测试
    try:
        tester.test_1_tutorials_list()
        tester.test_2_tutorials_filtering()
        tester.test_3_tutorials_detail()
        tester.test_4_downloads_list()
        tester.test_5_downloads_detail()
        tester.test_6_statistics()
        tester.test_7_interactions()
        tester.test_8_pagination()
        tester.test_9_data_integrity()
        tester.test_10_error_handling()
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    # 生成报告
    report_data = tester.generate_report()

    # 保存报告
    report_file = "E:/silly/md/docs/verification/content-api-test-report.md"
    import os
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    tester.save_report(report_data, report_file)

    print(f"\n测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 返回退出码
    sys.exit(0 if report_data['pass_rate'] >= 80 else 1)


if __name__ == "__main__":
    main()
