# ============================================
# SillyMD Backend - Crawler Service
# ============================================

import asyncio
import aiohttp
import random
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.services.ai_review_service import ai_review_service
from app.models.user import User, UserRole, VendorLevel
from app.models.skill import Skill, SkillCategory, SkillType, SkillStatus
from app.core.security import generate_content_hash, sign_skill
from faker import Faker
from datetime import datetime
import hashlib


class SkillCrawler:
    """Automatic skill crawler from external sources"""

    def __init__(self):
        self.fake = Faker()
        self.sources = settings.CRAWLER_SOURCES
        self.max_daily = settings.CRAWLER_MAX_DAILY_IMPORTS
        self.interval = settings.CRAWLER_IMPORT_INTERVAL

    async def search_github(self, keyword: str) -> List[Dict]:
        """Search GitHub repositories"""
        if "github" not in self.sources:
            return []

        skills = []

        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/search/repositories"
                params = {
                    "q": f"{keyword} language:python",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 10
                }

                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        skills = self._parse_github_repos(data.get("items", []))
        except Exception as e:
            print(f"GitHub search error: {e}")

        return skills

    def _parse_github_repos(self, items: List[Dict]) -> List[Dict]:
        """Parse GitHub repositories into skills"""
        skills = []

        for item in items:
            if item.get("stargazers_count", 0) >= 50:
                skill = {
                    "name": item["name"],
                    "description": item.get("description", ""),
                    "category": self._guess_category(item),
                    "type": "free",
                    "repo_url": item["html_url"],
                    "stars": item.get("stargazers_count", 0),
                    "language": item.get("language"),
                    "source": "github"
                }
                skills.append(skill)

        return skills

    def _guess_category(self, repo: Dict) -> SkillCategory:
        """Guess skill category from repo info"""
        topics = repo.get("topics", [])
        language = repo.get("language", "").lower()
        description = repo.get("description", "").lower()

        # Tech skills
        if language in ["python", "javascript", "java", "go", "rust"]:
            return SkillCategory.TECH

        # Design skills
        if any(t in topics for t in ["design", "ui", "ux", "frontend"]):
            return SkillCategory.DESIGN

        # Product skills
        if any(t in topics for t in ["product", "prd", "roadmap"]):
            return SkillCategory.PRODUCT

        # Marketing skills
        if any(t in topics for t in ["marketing", "seo", "analytics"]):
            return SkillCategory.MARKETING

        # Ops skills
        if any(t in topics for t in ["devops", "ops", "deployment"]):
            return SkillCategory.OPS

        # Default to tech
        return SkillCategory.TECH

    async def generate_fake_user(self, db: AsyncSession) -> User:
        """Generate fake user for crawled skills"""
        username = f"{self.fake.first_name()}{random.randint(1000, 9999)}"

        # Check if exists (simplified)
        user = User(
            username=username,
            email=f"{username}@temp-sillymd.com",
            password_hash="$2b$12$placeholder",  # Placeholder
            role=UserRole.VENDOR,
            vendor_level=random.choice([
                VendorLevel.NORMAL,
                VendorLevel.PREMIUM,
                VendorLevel.GOLD
            ]),
            is_active=True,
            is_verified=True
        )

        db.add(user)
        await db.flush()

        return user

    async def process_skill(
        self,
        raw_skill: Dict,
        db: AsyncSession
    ) -> Optional[Skill]:
        """Process and create skill from crawler data"""
        try:
            # Generate fake user
            author = await self.generate_fake_user(db)

            # Clean data
            cleaned_data = {
                "name": raw_skill["name"],
                "description": raw_skill.get("description", ""),
                "category": raw_skill["category"],
                "type": SkillType.FREE,
                "repo_url": raw_skill.get("repo_url"),
                "version": "1.0.0",
                "tags": []
            }

            # AI Review
            review_result = await ai_review_service.review_skill(cleaned_data)

            # Create skill
            from app.services.skill_service import skill_service
            skill_id = skill_service._generate_skill_id(cleaned_data["name"])

            skill = Skill(
                skill_id=skill_id,
                name=cleaned_data["name"],
                description=cleaned_data["description"],
                author_id=author.id,
                category=cleaned_data["category"],
                type=cleaned_data["type"],
                version=cleaned_data["version"],
                repo_url=cleaned_data["repo_url"],
                status=SkillStatus.APPROVED if review_result["approved"] else SkillStatus.REVIEWING,
                published_at=datetime.utcnow() if review_result["approved"] else None,
                content_hash=generate_content_hash(str(cleaned_data)),
                platform_signature=sign_skill(generate_content_hash(str(cleaned_data)))
            )

            db.add(skill)
            await db.commit()
            await db.refresh(skill)

            return skill

        except Exception as e:
            print(f"Error processing skill: {e}")
            return None

    async def run_crawler(self, db: AsyncSession):
        """Run crawler task"""
        keywords = ["api", "auth", "database", "utils", "tools"]

        for keyword in keywords:
            print(f"Searching for: {keyword}")

            # Search GitHub
            skills = await self.search_github(keyword)

            print(f"Found {len(skills)} skills")

            # Process each skill
            for skill_data in skills[:3]:  # Limit for demo
                await self.process_skill(skill_data, db)

            # Random delay
            await asyncio.sleep(random.uniform(5, 15))


# Create service instance
crawler_service = SkillCrawler()
