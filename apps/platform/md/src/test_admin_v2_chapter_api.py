"""
Admin-v2 章节管理 API 端到端测试

向运行中的服务器 (localhost:8000) 发送 HTTP 请求,
测试教程章节的 CRUD 接口。

用法:
  1. 先启动服务器: python main.py
  2. 再运行测试:   python test_admin_v2_chapter_api.py
"""

import json
import os
import sys
import traceback
import urllib.request
import urllib.error
import ssl
from typing import Optional, Dict, Any, List

BASE_URL = "http://localhost:8000"

# ============================================================
# 测试数据
# ============================================================
TEST_TUTORIAL = {
    "title": "[Test] SillyFu Tutorial",
    "description": "Test tutorial for chapter API verification",
    "category": "Testing",
    "level": "beginner",
    "status": "draft",
}

TEST_CHAPTER_1 = {
    "title": "Chapter 1: Environment Setup",
    "title_en": "Chapter 1: Environment Setup",
    "content": "Before starting, prepare the dev environment.\n1. Install Python 3.8+\n2. Configure DB\n3. Install deps",
    "content_en": "Before starting, prepare the dev environment.",
    "order": 1,
}

TEST_CHAPTER_2 = {
    "title": "Chapter 2: Basic Config",
    "title_en": "Chapter 2: Basic Configuration",
    "content": "This chapter covers basic configuration items.",
    "content_en": "This chapter covers basic configuration items.",
    "order": 2,
    "video_url": "https://example.com/video/ch2.mp4",
}

TEST_CHAPTER_3 = {
    "title": "Chapter 3: Advanced Features",
    "title_en": "Chapter 3: Advanced Features",
    "content": "Detailed advanced features.",
    "content_en": "Detailed advanced features.",
    "order": 3,
}

TEST_CHAPTER_UPDATE = {
    "title": "[Updated] Chapter 1: Setup & Installation",
    "title_en": "[Updated] Chapter 1: Setup & Installation",
    "content": "Updated content for chapter 1.",
    "is_free": True,
    "order": 1,
}


# ============================================================
# HTTP Helper
# ============================================================

def api(method, path, body=None):
    """Make an API call and return (status_code, parsed_json)."""
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(
            req, context=ssl._create_unverified_context(), timeout=15
        ) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.read() else ""
        try:
            return e.code, json.loads(body_text) if body_text else {"error": str(e)}
        except json.JSONDecodeError:
            return e.code, {"error": body_text, "status": e.code}
    except Exception as e:
        return 0, {"error": str(e)}


# ============================================================
# 测试结果收集
# ============================================================
class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.detail = ""

    def succeed(self, detail: str = ""):
        self.passed = True
        self.detail = detail

    def fail(self, detail: str):
        self.passed = False
        self.detail = detail


test_results: List[TestResult] = []
_created_tutorial_id: Optional[int] = None
_created_chapter_ids: List[int] = []


def record(name: str):
    """Decorator to record test result."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = TestResult(name)
            try:
                func(result, *args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                result.fail(f"{type(e).__name__}: {e}\n{tb}")
            test_results.append(result)
            status = "PASS" if result.passed else "FAIL"
            print(f"  [{status}] {name}")
            if not result.passed:
                # 只打印前几行错误
                lines = result.detail.strip().split("\n")
                for line in lines[:6]:
                    print(f"         {line}")
                if len(lines) > 6:
                    print(f"         ... ({len(lines) - 6} more lines)")
        return wrapper
    return decorator


def print_summary():
    """Print test summary and cleanup."""
    total = len(test_results)
    passed = sum(1 for r in test_results if r.passed)
    failed = total - passed

    print()
    print("=" * 60)
    print(f"  Tests: {passed}/{total} passed")
    if failed > 0:
        print(f"  Failed: {failed}")
        for r in test_results:
            if not r.passed:
                print(f"    FAIL {r.name}: {r.detail[:120]}")
    print("=" * 60)

    cleanup()

    if failed > 0:
        sys.exit(1)


def cleanup():
    """Cleanup test data from server."""
    global _created_tutorial_id, _created_chapter_ids
    for ch_id in reversed(_created_chapter_ids):
        if _created_tutorial_id:
            status, _ = api("DELETE", f"/api/v1/tutorials/{_created_tutorial_id}/chapters/{ch_id}")
            if status == 200:
                print(f"  [Cleanup] Deleted chapter #{ch_id}")
            else:
                print(f"  [Cleanup] Delete chapter #{ch_id} failed: {status}")
    if _created_tutorial_id:
        status, _ = api("DELETE", f"/api/v1/tutorials/{_created_tutorial_id}")
        if status == 200:
            print(f"  [Cleanup] Deleted tutorial #{_created_tutorial_id}")
        else:
            print(f"  [Cleanup] Delete tutorial #{_created_tutorial_id} failed: {status}")


# ============================================================
# 测试用例
# ============================================================

@record("Setup: Create tutorial")
def test_create_tutorial(result: TestResult):
    """Create a tutorial for chapter testing."""
    global _created_tutorial_id
    status, body = api("POST", "/api/v1/tutorials/", TEST_TUTORIAL)
    assert status == 200, f"HTTP {status}: {body}"
    assert body.get("success") is True, f"success=False: {body}"
    _created_tutorial_id = body.get("data", {}).get("id")
    assert _created_tutorial_id is not None and _created_tutorial_id > 0, f"invalid id: {body}"
    result.succeed(f"tutorial_id={_created_tutorial_id}")


@record("GET chapters: empty list")
def test_get_chapters_empty(result: TestResult):
    """Newly created tutorial should have 0 chapters."""
    status, body = api("GET", f"/api/v1/tutorials/{_created_tutorial_id}/chapters")
    assert status == 200, f"HTTP {status}: {body}"
    assert body.get("success") is True
    items = body.get("data", {}).get("items", [])
    assert isinstance(items, list), f"items not list: {items}"
    assert len(items) == 0, f"expected 0, got {len(items)}"
    result.succeed("0 chapters")


@record("POST chapter: create ch1")
def test_create_chapter_1(result: TestResult):
    """Create chapter 1."""
    global _created_chapter_ids
    status, body = api("POST", f"/api/v1/tutorials/{_created_tutorial_id}/chapters", TEST_CHAPTER_1)
    assert status == 200, f"HTTP {status}: {body}"
    assert body.get("success") is True
    ch_id = body.get("data", {}).get("id")
    assert ch_id is not None and ch_id > 0
    _created_chapter_ids.append(ch_id)
    result.succeed(f"chapter_id={ch_id}")


@record("POST chapter: create ch2 (with video)")
def test_create_chapter_2(result: TestResult):
    """Create chapter 2 with video_url."""
    global _created_chapter_ids
    status, body = api("POST", f"/api/v1/tutorials/{_created_tutorial_id}/chapters", TEST_CHAPTER_2)
    assert status == 200
    ch_id = body.get("data", {}).get("id")
    assert ch_id is not None
    _created_chapter_ids.append(ch_id)
    result.succeed(f"chapter_id={ch_id}")


@record("POST chapter: create ch3")
def test_create_chapter_3(result: TestResult):
    """Create chapter 3."""
    global _created_chapter_ids
    status, body = api("POST", f"/api/v1/tutorials/{_created_tutorial_id}/chapters", TEST_CHAPTER_3)
    assert status == 200
    ch_id = body.get("data", {}).get("id")
    assert ch_id is not None
    _created_chapter_ids.append(ch_id)
    result.succeed(f"chapter_id={ch_id}")


@record("GET chapters: 3 items sorted by order")
def test_get_chapters_3_items(result: TestResult):
    """Verify 3 chapters returned, sorted by order."""
    status, body = api("GET", f"/api/v1/tutorials/{_created_tutorial_id}/chapters")
    assert status == 200
    assert body.get("success") is True
    items = body.get("data", {}).get("items", [])
    assert len(items) == 3, f"expected 3, got {len(items)}"

    # Verify all expected fields
    ch = items[0]
    expected = [
        "id", "tutorial_id", "order", "chapter_order", "chapter_key",
        "title", "title_zh_CN", "title_en",
        "content", "content_zh_CN", "content_en",
        "video_url", "video_start_time", "video_end_time",
        "is_free", "created_at", "updated_at",
    ]
    for field in expected:
        assert field in ch, f"missing field '{field}'"

    # Verify sorting
    for i in range(1, len(items)):
        assert items[i]["order"] >= items[i-1]["order"], "not sorted"

    # Verify ch2 has video_url
    ch2 = items[1]
    assert ch2["video_url"] == TEST_CHAPTER_2["video_url"], f"video mismatch: {ch2['video_url']}"

    result.succeed("3 chapters, sorted by order, full fields")


@record("PUT chapter: update title/content/is_free")
def test_update_chapter(result: TestResult):
    """Update chapter 1."""
    ch_id = _created_chapter_ids[0]
    status, body = api("PUT", f"/api/v1/tutorials/{_created_tutorial_id}/chapters/{ch_id}", TEST_CHAPTER_UPDATE)
    assert status == 200, f"HTTP {status}: {body}"
    assert body.get("success") is True

    # Verify persisted
    _, get_body = api("GET", f"/api/v1/tutorials/{_created_tutorial_id}/chapters")
    items = get_body.get("data", {}).get("items", [])
    updated = next((ch for ch in items if ch["id"] == ch_id), None)
    assert updated is not None, "chapter not found after update"
    assert updated["title"] == TEST_CHAPTER_UPDATE["title"], f"title not updated: {updated['title']}"
    assert updated["content"] == TEST_CHAPTER_UPDATE["content"], "content not updated"
    assert updated["is_free"] is True, "is_free not updated"
    result.succeed("title, content, is_free updated and persisted")


@record("PUT chapter: partial update (order only)")
def test_update_chapter_partial(result: TestResult):
    """Partial update: change order only."""
    ch_id = _created_chapter_ids[2]
    status, _ = api("PUT", f"/api/v1/tutorials/{_created_tutorial_id}/chapters/{ch_id}", {"order": 99})
    assert status == 200, f"HTTP {status}"

    _, get_body = api("GET", f"/api/v1/tutorials/{_created_tutorial_id}/chapters")
    items = get_body.get("data", {}).get("items", [])
    updated = next((ch for ch in items if ch["id"] == ch_id), None)
    assert updated is not None
    assert updated["order"] == 99, f"order not updated: {updated['order']}"

    # Restore
    api("PUT", f"/api/v1/tutorials/{_created_tutorial_id}/chapters/{ch_id}", {"order": 3})
    result.succeed("order partial update OK")


@record("GET /tutorials/{id}: detail contains chapters")
def test_tutorial_detail_contains_chapters(result: TestResult):
    """Verify tutorial detail endpoint includes chapters."""
    status, body = api("GET", f"/api/v1/tutorials/{_created_tutorial_id}?lang=zh-CN")
    assert status == 200
    assert body.get("success") is True
    chapters = body.get("data", {}).get("chapters", [])
    assert len(chapters) == 3, f"expected 3, got {len(chapters)}"
    ch = chapters[0]
    assert "title_zh_CN" in ch, "missing title_zh_CN"
    assert "title_en" in ch, "missing title_en"
    result.succeed(f"{len(chapters)} chapters with i18n fields")


@record("DELETE chapter: remove ch3")
def test_delete_chapter(result: TestResult):
    """Delete chapter 3, verify count goes from 3 to 2."""
    ch_id = _created_chapter_ids.pop()
    status, body = api("DELETE", f"/api/v1/tutorials/{_created_tutorial_id}/chapters/{ch_id}")
    assert status == 200, f"HTTP {status}: {body}"
    assert body.get("success") is True

    _, get_body = api("GET", f"/api/v1/tutorials/{_created_tutorial_id}/chapters")
    items = get_body.get("data", {}).get("items", [])
    assert len(items) == 2, f"expected 2 after delete, got {len(items)}"
    assert all(ch["id"] != ch_id for ch in items), "deleted chapter still in list"
    result.succeed(f"deleted ch#{ch_id}, 2 remaining")


@record("DELETE chapter: repeat delete -> 404")
def test_delete_chapter_not_found(result: TestResult):
    """Re-deleting should return 404."""
    status, _ = api("DELETE", f"/api/v1/tutorials/{_created_tutorial_id}/chapters/99999")
    assert status == 404, f"expected 404, got {status}"
    result.succeed("correctly returned 404")


@record("POST chapter: non-existent tutorial -> 404")
def test_create_chapter_invalid_tutorial(result: TestResult):
    """Creating chapter under non-existent tutorial should 404."""
    status, _ = api("POST", "/api/v1/tutorials/99999/chapters", {"title": "x", "content": "x", "order": 1})
    assert status == 404, f"expected 404, got {status}"
    result.succeed("correctly returned 404")


@record("POST chapter: minimal fields (empty title/content)")
def test_create_chapter_minimal(result: TestResult):
    """Create with only order set."""
    global _created_chapter_ids
    status, body = api("POST", f"/api/v1/tutorials/{_created_tutorial_id}/chapters",
                       {"order": 100, "title": "", "content": ""})
    assert status == 200
    ch_id = body.get("data", {}).get("id")
    assert ch_id is not None
    _created_chapter_ids.append(ch_id)

    _, get_body = api("GET", f"/api/v1/tutorials/{_created_tutorial_id}/chapters")
    items = get_body.get("data", {}).get("items", [])
    minimal_ch = next((ch for ch in items if ch["id"] == ch_id), None)
    assert minimal_ch is not None
    assert minimal_ch["title"] == "", f"expected empty title: {minimal_ch['title']}"
    assert minimal_ch["is_free"] is False, "default is_free should be False"
    result.succeed(f"chapter #{ch_id} with empty title OK")


@record("Field mapping: verify field consistency")
def test_chapter_field_mapping(result: TestResult):
    """
    Verify field mapping:
      order -> chapter_order / order
      title -> title_zh_CN / title
      content -> content_zh_CN / content
    """
    global _created_chapter_ids
    status, body = api("POST", f"/api/v1/tutorials/{_created_tutorial_id}/chapters", {
        "title": "Mapping Test CN",
        "title_en": "Mapping Test EN",
        "content": "Chinese content",
        "content_en": "English content",
        "order": 50,
    })
    assert status == 200
    ch_id = body.get("data", {}).get("id")
    _created_chapter_ids.append(ch_id)

    _, get_body = api("GET", f"/api/v1/tutorials/{_created_tutorial_id}/chapters")
    items = get_body.get("data", {}).get("items", [])
    ch = next((c for c in items if c["id"] == ch_id), None)
    assert ch is not None

    assert ch["order"] == 50, f"order: {ch['order']}"
    assert ch["chapter_order"] == 50, f"chapter_order: {ch['chapter_order']}"
    assert ch["title"] == "Mapping Test CN", f"title: {ch['title']}"
    assert ch["title_zh_CN"] == "Mapping Test CN", f"title_zh_CN: {ch['title_zh_CN']}"
    assert ch["title_en"] == "Mapping Test EN", f"title_en: {ch['title_en']}"
    assert ch["content"] == "Chinese content", f"content: {ch['content']}"
    assert ch["content_zh_CN"] == "Chinese content", f"content_zh_CN: {ch['content_zh_CN']}"
    assert ch["content_en"] == "English content", f"content_en: {ch['content_en']}"
    result.succeed("field mapping verified")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Admin-v2 Chapter Management API Test")
    print("  Server: " + BASE_URL)
    print("=" * 60)
    print()

    # Health check first
    status, _ = api("GET", "/api/health")
    if status != 200:
        print(f"ERROR: Server not responding (HTTP {status})")
        print(f"  Start the server first: cd src && python main.py")
        sys.exit(1)
    print(f"  Server OK (HTTP {status})")
    print()

    # Run tests in order
    test_create_tutorial()
    test_get_chapters_empty()
    test_create_chapter_1()
    test_create_chapter_2()
    test_create_chapter_3()
    test_get_chapters_3_items()
    test_update_chapter()
    test_update_chapter_partial()
    test_tutorial_detail_contains_chapters()
    test_delete_chapter()
    test_delete_chapter_not_found()
    test_create_chapter_invalid_tutorial()
    test_create_chapter_minimal()
    test_chapter_field_mapping()

    print_summary()
