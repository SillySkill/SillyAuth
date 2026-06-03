"""
Import scrapling-skill and taste-skill skills into the SillyMD platform.

Usage:
    cd /opt/sillymd-new
    python src/_import_skill2_skills.py

This script sends API requests to the local server on port 8001.
"""

import os
import sys
import json
import re
import time
import urllib.request
import urllib.error

API_BASE = "http://127.0.0.1:8001/api/v1/skills"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

SKILL_DIRS = [
    # Scrapling-Skill
    {
        "path": "/opt/sillymd-new/skill2/Scrapling-Skill",
        "category": "tech",
        "tags": ["web-scraping", "python", "crawler", "anti-bot", "automation"],
    },
    # Taste-skill collection (direct subdirs of taste-skill/)
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/taste-skill",
        "category": "design",
        "tags": ["frontend", "design-system", "ui", "landing-page"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/taste-skill-v1",
        "category": "design",
        "tags": ["frontend", "design-system", "ui"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/gpt-tasteskill",
        "category": "design",
        "tags": ["frontend", "gsap", "motion", "awwwards"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/stitch-skill",
        "category": "design",
        "tags": ["design-system", "ui", "semantic-design"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/minimalist-skill",
        "category": "design",
        "tags": ["minimalist", "ui", "editorial"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/brutalist-skill",
        "category": "design",
        "tags": ["brutalist", "ui", "typography"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/soft-skill",
        "category": "design",
        "tags": ["ui", "glassmorphism", "premium-design"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/imagegen-frontend-web",
        "category": "design",
        "tags": ["image-generation", "frontend", "design-reference"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/imagegen-frontend-mobile",
        "category": "design",
        "tags": ["image-generation", "mobile", "ui-design"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/brandkit",
        "category": "design",
        "tags": ["branding", "identity", "logo", "image-generation"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/image-to-code-skill",
        "category": "design",
        "tags": ["image-to-code", "frontend", "design-implementation"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/redesign-skill",
        "category": "design",
        "tags": ["redesign", "audit", "frontend-optimization"],
    },
    {
        "path": "/opt/sillymd-new/skill2/taste-skill/output-skill",
        "category": "ops",
        "tags": ["code-quality", "output-enforcement", "llm-prompt"],
    },
]


def parse_frontmatter(text):
    """Parse YAML frontmatter from SKILL.md"""
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    front = m.group(1)
    data = {}
    for line in front.split('\n'):
        line = line.strip()
        if ':' in line:
            key, val = line.split(':', 1)
            data[key.strip()] = val.strip()
    return data


def read_skill_md(path):
    """Read SKILL.md and return (frontmatter, full_content)"""
    md_path = os.path.join(path, "SKILL.md")
    if not os.path.exists(md_path):
        print(f"  WARNING: SKILL.md not found at {md_path}")
        return None, None
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    front = parse_frontmatter(content)
    return front, content


def api_post(data):
    """Make POST request to API (URL is API_BASE without trailing slash)"""
    url = API_BASE
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"  API error {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"  Request failed: {e}")
        return None


def import_skill(skill_def):
    """Import a single skill via API"""
    path = skill_def["path"]
    dirname = os.path.basename(path)
    print(f"\n{'='*60}")
    print(f"Importing: {dirname}")
    print(f"  Path: {path}")

    if not os.path.exists(path):
        print(f"  SKIP: directory does not exist")
        return False

    front, content = read_skill_md(path)
    if content is None:
        print(f"  SKIP: no SKILL.md found")
        return False

    name = front.get("name", dirname)
    description = front.get("description", "")
    version = front.get("version", "1.0.0")

    print(f"  Name: {name}")
    print(f"  Description: {description[:80]}...")
    print(f"  Version: {version}")
    print(f"  Category: {skill_def['category']}")

    payload = {
        "skill_id": name,
        "name": name,
        "description": description[:500] if description else "",
        "category": skill_def["category"],
        "tags": skill_def["tags"],
        "type": "free",
        "version": version,
        "code_content": content,
        "price": 0,
    }

    print(f"  Creating skill via API...")
    result = api_post(payload)

    if result and result.get("success"):
        skill_id = result.get("data", {}).get("id") or result.get("id")
        print(f"  Created! ID: {skill_id}")

        # Approve the skill
        if skill_id:
            print(f"  Approving skill...")
            try:
                url = API_BASE + "/" + str(skill_id) + "/approve"
                areq = urllib.request.Request(url, method="POST",
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=b"{}")
                with urllib.request.urlopen(areq, timeout=30) as ar:
                    json.loads(ar.read().decode("utf-8"))
                    print("  Approved!")
            except urllib.error.HTTPError as e:
                print(f"  Approve API error {e.code}: {e.read().decode('utf-8')[:200]}")
            except Exception as e:
                print(f"  Approve failed: {e}")

        return True
    else:
        err = result.get("detail") or result.get("message") or "unknown error" if result else "API returned None"
        print(f"  FAILED: {err}")
        return False


def main():
    print("=" * 60)
    print("SillyMD Skill2 Import Script")
    print(f"API: {API_BASE}")
    print("=" * 60)

    # Check server connectivity
    try:
        req = urllib.request.Request(f"{API_BASE}?limit=1")
        with urllib.request.urlopen(req, timeout=10) as resp:
            existing = json.loads(resp.read().decode('utf-8'))
            print(f"Server reachable. Existing skills count: {len(existing) if isinstance(existing, list) else '?'}")
    except Exception as e:
        print(f"Cannot reach API: {e}")
        print("Make sure the server is running on port 8001.")
        sys.exit(1)

    success_count = 0
    fail_count = 0

    for skill_def in SKILL_DIRS:
        try:
            ok = import_skill(skill_def)
            if ok:
                success_count += 1
            else:
                fail_count += 1
            time.sleep(0.5)  # Rate limit
        except Exception as e:
            print(f"  ERROR: {e}")
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"Import complete: {success_count} success, {fail_count} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
