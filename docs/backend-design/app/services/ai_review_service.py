# ============================================
# SillyMD Backend - AI Review Service
# ============================================

import asyncio
import random
from typing import Dict, Optional
from app.core.config import settings
from openai import AsyncOpenAI
import httpx


class AIReviewService:
    """AI-based skill review service"""

    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def review_skill(
        self,
        skill_data: Dict
    ) -> Dict:
        """
        Review skill using AI
        Returns dict with: {approved: bool, confidence: float, scores: dict, suggestions: list}
        """
        # Get review difficulty settings
        difficulty_config = self._get_difficulty_config(settings.REVIEW_DIFFICULTY)

        # Check format
        format_score = self._check_format(skill_data)
        safety_score = await self._check_safety(skill_data)
        quality_score = self._assess_quality(skill_data)

        # Calculate final score
        final_score = (
            format_score * 0.2 +
            safety_score * 0.3 +
            quality_score * 0.5
        )

        # Determine approval based on difficulty
        approved = final_score >= difficulty_config["autoApprovalThreshold"]

        # Add randomness for realism
        if approved and random.random() > difficulty_config["randomApprovalRate"]:
            approved = False

        return {
            "approved": approved,
            "confidence": final_score,
            "scores": {
                "format": format_score,
                "safety": safety_score,
                "quality": quality_score
            },
            "suggestions": self._generate_suggestions(skill_data, final_score),
            "review_difficulty": settings.REVIEW_DIFFICULTY
        }

    def _get_difficulty_config(self, difficulty: str) -> Dict:
        """Get review difficulty configuration"""
        configs = {
            "easy": {
                "autoApprovalThreshold": 0.7,
                "randomApprovalRate": 0.9
            },
            "medium": {
                "autoApprovalThreshold": 0.3,
                "randomApprovalRate": 0.5
            },
            "hard": {
                "autoApprovalThreshold": 0.0,
                "randomApprovalRate": 0.1
            }
        }
        return configs.get(difficulty, configs["medium"])

    def _check_format(self, skill_data: Dict) -> float:
        """Check skill format (0-1)"""
        score = 1.0

        # Check required fields
        if not skill_data.get("name"):
            score -= 0.3
        if not skill_data.get("description"):
            score -= 0.2
        if not skill_data.get("category"):
            score -= 0.2

        # Check description length
        desc = skill_data.get("description", "")
        if len(desc) < 50:
            score -= 0.1
        elif len(desc) >= 200:
            score += 0.1

        return max(0.0, min(1.0, score))

    async def _check_safety(self, skill_data: Dict) -> float:
        """Check content safety (0-1)"""
        # Basic safety checks
        score = 1.0
        text = f"{skill_data.get('name', '')} {skill_data.get('description', '')}"

        # Check for suspicious patterns
        suspicious_patterns = [
            "password",
            "secret",
            "api_key",
            "token",
            "hack",
            "crack",
            "bypass"
        ]

        text_lower = text.lower()
        for pattern in suspicious_patterns:
            if pattern in text_lower:
                score -= 0.1

        return max(0.0, min(1.0, score))

    def _assess_quality(self, skill_data: Dict) -> float:
        """Assess skill quality (0-1)"""
        score = 0.5  # Base score

        # Description quality
        desc = skill_data.get("description", "")
        if len(desc) > 100:
            score += 0.1
        if len(desc) > 300:
            score += 0.1

        # Has repo URL
        if skill_data.get("repo_url"):
            score += 0.1

        # Has dependencies
        if skill_data.get("dependencies"):
            score += 0.1

        # Has tags
        tags = skill_data.get("tags", [])
        if len(tags) > 0:
            score += 0.1

        return min(1.0, score)

    def _generate_suggestions(self, skill_data: Dict, score: float) -> list:
        """Generate improvement suggestions"""
        suggestions = []

        if score < 0.7:
            if not skill_data.get("description"):
                suggestions.append("添加详细描述")
            if len(skill_data.get("description", "")) < 100:
                suggestions.append("扩展描述内容，至少100字")
            if not skill_data.get("repo_url"):
                suggestions.append("添加代码仓库链接")
            if not skill_data.get("tags"):
                suggestions.append("添加相关标签便于搜索")

        return suggestions


# Create service instance
ai_review_service = AIReviewService()
