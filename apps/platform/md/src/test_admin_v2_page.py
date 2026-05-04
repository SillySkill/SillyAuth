"""
Admin-v2 章节管理页面完整测试

模拟前端操作流程：
  1. 登录 -> 获取 token
  2. 创建教程
  3. 章节 CRUD (创建/查询/更新/删除)
  4. 异常场景
  5. 清理数据

运行: python test_admin_v2_page.py
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
    "title": "[Admin Test] Chapter Management Tutorial",
    "description": "Created by admin-v2 chapter management test",
    "category": "Testing",
    "level": "beginner",
    "status": "draft",
}

CHAPTERS_DATA = [
    {"title": "Getting Started", "title_en": "Getting Started",
     "content": "Welcome to this tutorial.", "content_en": "Welcome.",
     "order": 1},
    {"title": "Installation Guide", "title_en": "Installation Guide",
     "content": "Step-by-step installation.", "content_en": "Install steps.",
     "order": 2, "video_url": "https://example.com/install.mp4"},
    {"title": "Configuration", "title_en": "Configuration",
     "content": "Configure your settings.", "content_en": "Config guide.",
     "order": 3, "is_free": True},
]

UPDATE_DATA = {
    "title": "[Updated] Getting Started Guide",
    "content": "Updated: Welcome to the updated tutorial.",
    "is_free": True,
    "order": 1,
}

# ============================================================
# HTTP helper
# ============================================================
_token: Optional[str] = None

def set_token(t: str):
    global _token
    _token = t

def api(method: str, path: str, body: dict = None, use_auth: bool = False):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if use_auth and _token:
        headers["Authorization"] = f"Bearer {_token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        b = e.read().decode() if e.read() else ""
        try:
            return e.code, json.loads(b) if b else {"error": str(e)}
        except json.JSONDecodeError:
            return e.code, {"error": b}
    except Exception as e:
        return 0, {"error": str(e)}


# ============================================================
# Test framework
# ============================================================
class Case:
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

test_cases: List[Case] = []
_tutorial_id: Optional[int] = None
_chapter_ids: List[int] = []

def test(name: str):
    def deco(fn):
        def wrapper():
            c = Case(name)
            try:
                fn(c)
            except Exception as e:
                c.fail(f"{type(e).__name__}: {e}")
            test_cases.append(c)
            tag = "PASS" if c.passed else "FAIL"
            print(f"  [{tag}] {name}")
            if not c.passed:
                for line in c.detail.strip().split("\n")[:4]:
                    print(f"         {line}")
        return wrapper
    return deco


# ============================================================
# Tests
# ============================================================

@test("Dev login")
def t_login(c: Case):
    status, body = api("POST", "/api/v1/auth/dev-login",
                       {"email": "admin@sillymd.com", "password": "admin123456"})
    assert status == 200, f"HTTP {status}"
    token = body.get("access_token", "")
    assert token, "no access_token in response"
    set_token(token)
    assert body.get("user", {}).get("role") == "super_admin", "not super_admin"
    c.succeed(f"token={token[:30]}... role=super_admin")


@test("Create tutorial")
def t_create_tutorial(c: Case):
    global _tutorial_id
    status, body = api("POST", "/api/v1/tutorials/", TEST_TUTORIAL)
    assert status == 200, f"HTTP {status}: {body}"
    assert body.get("success") is True
    _tutorial_id = body["data"]["id"]
    c.succeed(f"tutorial_id={_tutorial_id}")


@test("List tutorials (verify created)")
def t_list_tutorials(c: Case):
    status, body = api("GET", "/api/v1/tutorials/?status=draft")
    assert status == 200
    items = body.get("data", {}).get("items", [])
    found = any(t["id"] == _tutorial_id for t in items)
    assert found, f"tutorial #{_tutorial_id} not in list"
    c.succeed(f"found in list ({len(items)} total)")


@test("GET chapters: empty")
def t_chapters_empty(c: Case):
    status, body = api("GET", f"/api/v1/tutorials/{_tutorial_id}/chapters")
    assert status == 200
    assert body["data"]["items"] == [], "not empty"
    c.succeed("OK")


@test("POST 3 chapters one by one")
def t_create_3_chapters(c: Case):
    global _chapter_ids
    for i, ch_data in enumerate(CHAPTERS_DATA):
        status, body = api("POST", f"/api/v1/tutorials/{_tutorial_id}/chapters", ch_data)
        assert status == 200, f"ch{i} HTTP {status}: {body}"
        ch_id = body["data"]["id"]
        _chapter_ids.append(ch_id)
    c.succeed(f"created {len(_chapter_ids)} chapters: {_chapter_ids}")


@test("GET chapters: verify all fields and sorting")
def t_verify_chapters(c: Case):
    status, body = api("GET", f"/api/v1/tutorials/{_tutorial_id}/chapters")
    assert status == 200
    items = body["data"]["items"]
    assert len(items) == 3, f"expected 3, got {len(items)}"

    # Verify full field set
    ch = items[0]
    for f in ["id", "tutorial_id", "order", "chapter_order", "chapter_key",
              "title", "title_zh_CN", "title_en",
              "content", "content_zh_CN", "content_en",
              "video_url", "is_free", "created_at", "updated_at"]:
        assert f in ch, f"missing field: {f}"

    # Sort check
    for i in range(1, len(items)):
        assert items[i]["order"] >= items[i-1]["order"], "not sorted"

    # Ch2 video_url
    if len(items) > 1:
        assert items[1]["video_url"] == CHAPTERS_DATA[1]["video_url"]

    c.succeed(f"3 chapters OK, fields complete, sorted")


@test("Update chapter 1")
def t_update_chapter(c: Case):
    ch_id = _chapter_ids[0]
    status, body = api("PUT", f"/api/v1/tutorials/{_tutorial_id}/chapters/{ch_id}", UPDATE_DATA)
    assert status == 200, f"HTTP {status}: {body}"
    assert body.get("success") is True

    # Verify
    _, r = api("GET", f"/api/v1/tutorials/{_tutorial_id}/chapters")
    items = r["data"]["items"]
    updated = next(ch for ch in items if ch["id"] == ch_id)
    assert updated["title"] == UPDATE_DATA["title"], f"title: {updated['title']}"
    assert updated["content"] == UPDATE_DATA["content"], "content wrong"
    assert updated["is_free"] == UPDATE_DATA["is_free"], "is_free wrong"
    c.succeed("title/content/is_free updated")


@test("Partial update: order only")
def t_partial_update(c: Case):
    ch_id = _chapter_ids[2]
    s, _ = api("PUT", f"/api/v1/tutorials/{_tutorial_id}/chapters/{ch_id}", {"order": 99})
    assert s == 200
    _, r = api("GET", f"/api/v1/tutorials/{_tutorial_id}/chapters")
    updated = next(ch for ch in r["data"]["items"] if ch["id"] == ch_id)
    assert updated["order"] == 99, f"order={updated['order']}"
    # Restore
    api("PUT", f"/api/v1/tutorials/{_tutorial_id}/chapters/{ch_id}", {"order": 3})
    c.succeed("partial update OK")


@test("Tutorial detail includes chapters")
def t_detail_includes_chapters(c: Case):
    status, body = api("GET", f"/api/v1/tutorials/{_tutorial_id}?lang=zh-CN")
    assert status == 200
    chs = body["data"]["chapters"]
    assert len(chs) == 3, f"got {len(chs)} chapters"
    ch = chs[0]
    assert "title_zh_CN" in ch, "no title_zh_CN"
    assert "title_en" in ch, "no title_en"
    assert "content_zh_CN" in ch, "no content_zh_CN"
    assert "content_en" in ch, "no content_en"
    assert "is_free" in ch, "no is_free"
    assert "video_url" in ch, "no video_url"
    c.succeed(f"{len(chs)} chapters with i18n fields")


@test("Delete chapter 3")
def t_delete_chapter(c: Case):
    ch_id = _chapter_ids.pop()
    status, body = api("DELETE", f"/api/v1/tutorials/{_tutorial_id}/chapters/{ch_id}")
    assert status == 200
    assert body["success"] is True
    _, r = api("GET", f"/api/v1/tutorials/{_tutorial_id}/chapters")
    assert len(r["data"]["items"]) == 2, "count not 2 after delete"
    assert all(ch["id"] != ch_id for ch in r["data"]["items"])
    c.succeed(f"deleted ch#{ch_id}, 2 left")


@test("Repeat delete -> 404")
def t_double_delete(c: Case):
    status, _ = api("DELETE", f"/api/v1/tutorials/{_tutorial_id}/chapters/99999")
    assert status == 404, f"expected 404, got {status}"
    c.succeed("404 OK")


@test("Create chapter on invalid tutorial -> 404")
def t_invalid_tutorial(c: Case):
    status, _ = api("POST", "/api/v1/tutorials/99999/chapters",
                    {"title": "x", "content": "x", "order": 1})
    assert status == 404, f"expected 404, got {status}"
    c.succeed("404 OK")


@test("Minimal chapter (empty title/content)")
def t_minimal_chapter(c: Case):
    global _chapter_ids
    status, body = api("POST", f"/api/v1/tutorials/{_tutorial_id}/chapters",
                       {"order": 100, "title": "", "content": ""})
    assert status == 200
    ch_id = body["data"]["id"]
    _chapter_ids.append(ch_id)
    _, r = api("GET", f"/api/v1/tutorials/{_tutorial_id}/chapters")
    ch = next(c for c in r["data"]["items"] if c["id"] == ch_id)
    assert ch["title"] == "", f"title not empty: {ch['title']}"
    assert ch["is_free"] is False, "is_free should be False"
    c.succeed(f"ch#{ch_id} empty title OK")


@test("Field mapping consistency")
def t_field_mapping(c: Case):
    global _chapter_ids
    status, body = api("POST", f"/api/v1/tutorials/{_tutorial_id}/chapters", {
        "title": "字段映射测试",
        "title_en": "Field Mapping Test",
        "content": "中文内容 content",
        "content_en": "English content",
        "order": 50,
    })
    assert status == 200
    ch_id = body["data"]["id"]
    _chapter_ids.append(ch_id)

    _, r = api("GET", f"/api/v1/tutorials/{_tutorial_id}/chapters")
    ch = next(c for c in r["data"]["items"] if c["id"] == ch_id)

    # Verify mapping: request -> response
    assert ch["order"] == 50, f"order={ch['order']}"
    assert ch["chapter_order"] == 50
    assert ch["title"] == "字段映射测试"
    assert ch["title_zh_CN"] == "字段映射测试"
    assert ch["title_en"] == "Field Mapping Test"
    assert ch["content"] == "中文内容 content"
    assert ch["content_zh_CN"] == "中文内容 content"
    assert ch["content_en"] == "English content"
    c.succeed("mapping verified")


@test("Auth: chapters CRUD without token still works")
def t_auth_check(c: Case):
    """Note: chapter endpoints currently have no auth decorator."""
    status, body = api("GET", f"/api/v1/tutorials/{_tutorial_id}/chapters")
    assert status == 200, f"public access blocked: {status}"
    c.succeed("public access OK (no auth on chapter endpoints)")


# ============================================================
# Main
# ============================================================
def cleanup():
    global _tutorial_id, _chapter_ids
    for ch_id in reversed(_chapter_ids):
        if _tutorial_id:
            s, _ = api("DELETE", f"/api/v1/tutorials/{_tutorial_id}/chapters/{ch_id}")
            if s == 200:
                print(f"  [Cleanup] chapter #{ch_id}")
    if _tutorial_id:
        s, _ = api("DELETE", f"/api/v1/tutorials/{_tutorial_id}")
        if s == 200:
            print(f"  [Cleanup] tutorial #{_tutorial_id}")

def summary():
    total = len(test_cases)
    passed = sum(1 for c in test_cases if c.passed)
    failed = total - passed
    print()
    print("=" * 60)
    print(f"  Admin-v2 Chapter Page Test: {passed}/{total} passed")
    if failed > 0:
        for c in test_cases:
            if not c.passed:
                print(f"    FAIL {c.name}: {c.detail[:100]}")
    print("=" * 60)
    cleanup()
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    import time
    print("=" * 60)
    print("  Admin-v2 Chapter Management Page E2E Test")
    print(f"  Server: {BASE_URL}")
    print("=" * 60)
    print()

    # Health check
    s, _ = api("GET", "/api/health")
    if s != 200:
        print(f"ERROR: Server not running (HTTP {s})")
        print("  Start: cd src && python main.py")
        sys.exit(1)
    print(f"  Server OK\n")

    tests = [
        t_login, t_create_tutorial, t_list_tutorials,
        t_chapters_empty, t_create_3_chapters, t_verify_chapters,
        t_update_chapter, t_partial_update,
        t_detail_includes_chapters,
        t_delete_chapter, t_double_delete, t_invalid_tutorial,
        t_minimal_chapter, t_field_mapping, t_auth_check,
    ]
    for t in tests:
        t()
        time.sleep(0.1)

    summary()
