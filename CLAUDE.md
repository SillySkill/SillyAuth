# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

# SillyMD Project Context

## Architecture
- **Framework**: FastAPI modular (PluginManager + BaseModule)
- **Templating**: Jinja2 with SafeChainableUndefined, custom i18n `_()` function in `template_helpers.py`
- **Database**: PostgreSQL on Alibaba Cloud RDS (pgm-bp17g13e3k5y08y1wo.pg.rds.aliyuncs.com:5432/sillymd)
- **Storage**: Volcengine TOS (对象存储) - custom domain `resource.sillymd.com`
- **Auth**: JWT-based, optional `current_user` dependency

## Key Directories
- `apps/platform/md/src/` - Main Python source (main.py, production.py)
- `apps/platform/md/src/modules/` - Feature modules (skills, cms, vendor, auth, etc.)
- `apps/platform/md/src/core/` - Framework core (plugin_manager, db_adapter, template_helpers)
- `apps/platform/md/src/templates/` - Jinja2 templates
- `apps/platform/md/examples/css/` - Frontend CSS (sillymd.css etc.)
- `apps/platform/md/examples/js/` - Frontend JS
- `apps/platform/md/examples/img/` - Images
- `apps/platform/md/server/` - Deployment scripts, nginx configs, migrations

## Database
- **skills table**: skill_id, name, author_id, category, status, download_count, favorite_count, package_url, etc.
- **users table**: username, email, password_hash, avatar_url, bio, role
- **skill_favorites**: user_id, skill_id (join table for favorites)
- Skill categories enum: tech, product, design, marketing, ops
- Skill statuses enum: draft, reviewing, approved, rejected
- 228 total skills (all source='awesome-complete'), 6 distinct authors

## Key Features Built
- Skills marketplace with pagination (20 per page), card layout with CSS line-clamp
- Skills download via TOS `package_url` (fallback: demo_url → package_url → source_path)
- Favorite toggle API (POST /api/v1/skills/{id}/favorite) backed by `skill_favorites` table
- Homepage hero carousel with video support
- Homepage vendor carousel (query: skills JOIN users GROUP BY author, top 8 by download count)
- Admin-v2 SPA at /admin
- LLM proxy at /llm

## Vendors (首页供应商)
Derived from `skills JOIN users` query - authors with approved skills. Currently 6:
- sillymd (212 skills), 码农小飞 (4), 糖糖AI (3), 北风科技 (3), 小熊猫工坊 (3), 星光码社 (3)

## Deployment
- **Server**: 47.96.133.238 (Alibaba Cloud)
- **SSH Key**: ~/.ssh/silly.pem (root)
- **App Dir**: /opt/sillymd-new/
- **Service**: systemd `sillymd-api` (port 8000, uvicorn production.py)
- **Nginx**: Reverse proxy sillymd.com/www.sillymd.com → 127.0.0.1:8000 (SSL via Let's Encrypt)
- **Web Root**: /var/www/sillymd (static admin SPA at /admin)
- **Deploy**: tar + scp to /opt/sillymd-new/, then systemctl restart sillymd-api
