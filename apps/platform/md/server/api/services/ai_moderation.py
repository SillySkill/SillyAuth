"""
AI Content Moderation Service
AI 内容审核服务

使用 AI 对用户提交的内容进行自动审核
"""
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict, Any
import httpx
import json
import re
from datetime import datetime

from ..database import get_db
from ..models.user_submissions import UserSubmission
from ..models.ai_review import AIContentReview
from ..config import settings


class AIModerationService:
    """AI 审核服务"""

    def __init__(self):
        self.ai_api_url = settings.AI_API_URL
        self.ai_api_key = settings.AI_API_KEY

    async def review_submission(
        self,
        submission_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        审核用户提交的内容

        1. 获取提交内容
        2. 调用 AI API 进行审核
        3. 更新审核状态
        4. 返回审核结果
        """
        # 获取提交记录
        submission = await db.get(UserSubmission, submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="提交记录不存在")

        # 更新状态为审核中
        submission.status = "reviewing"
        submission.ai_review_status = "pending"
        await db.commit()

        # 准备审核数据
        review_data = {
            "content_type": submission.content_type,
            "title": submission.title_zh_CN,
            "description": submission.description_zh_CN,
            "content": submission.content_zh_CN,
            "category": submission.category,
            "check_items": [
                "quality_score",      # 内容质量评分
                "originality_check",   # 原创性检查
                "safety_check",        # 安全性检查
                "spam_check",          # 垃圾内容检查
                "technical_accuracy",  # 技术准确性
                "completeness"         # 完整性检查
            ]
        }

        # 调用 AI 审核 API
        try:
            ai_result = await self._call_ai_moderation_api(review_data)
        except Exception as e:
            # AI 调用失败，转为人工审核
            submission.ai_review_status = "failed"
            submission.ai_review_feedback = f"AI 审核失败: {str(e)}"
            await db.commit()
            return {
                "success": False,
                "status": "ai_failed",
                "message": "AI 审核失败，已转为人工审核"
            }

        # 处理审核结果
        review_result = self._process_ai_result(ai_result)

        # 更新审核状态
        submission.ai_review_status = review_result["status"]
        submission.ai_review_score = review_result["score"]
        submission.ai_review_feedback = review_result["feedback"]

        # 如果 AI 审核通过，自动发布
        if review_result["status"] == "passed" and review_result["score"] >= 70:
            await self._auto_publish_submission(submission, db)
        elif review_result["status"] == "failed":
            submission.status = "rejected"
            submission.rejection_reason = "AI 审核未通过: " + review_result["feedback"]

        await db.commit()

        # 记录审核历史
        await self._create_review_record(
            submission_id=submission_id,
            ai_result=ai_result,
            review_result=review_result,
            db=db
        )

        return {
            "success": True,
            "submission_id": submission_id,
            "status": review_result["status"],
            "score": review_result["score"],
            "feedback": review_result["feedback"],
            "auto_published": review_result["status"] == "passed" and review_result["score"] >= 70
        }

    async def _call_ai_moderation_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用 AI 审核 API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.ai_api_url}/moderation/check",
                headers={
                    "Authorization": f"Bearer {self.ai_api_key}",
                    "Content-Type": "application/json"
                },
                json=data
            )
            response.raise_for_status()
            return response.json()

    def _process_ai_result(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """处理 AI 返回的审核结果"""
        # 提取各项评分
        scores = ai_result.get("scores", {})

        # 计算总分（加权平均）
        weights = {
            "quality_score": 0.3,
            "originality_check": 0.25,
            "safety_check": 0.2,
            "technical_accuracy": 0.15,
            "completeness": 0.1
        }

        total_score = sum(
            scores.get(item, 0) * weight
            for item, weight in weights.items()
        )

        # 检查是否有一票否决项
        safety = scores.get("safety_check", 100)
        spam = scores.get("spam_check", 100)

        # 安全性或垃圾内容检查低于 50 分，直接拒绝
        if safety < 50 or spam < 50:
            return {
                "status": "failed",
                "score": total_score,
                "feedback": self._generate_rejection_reason(scores)
            }

        # 总分低于 60 分，拒绝
        if total_score < 60:
            return {
                "status": "failed",
                "score": total_score,
                "feedback": self._generate_rejection_reason(scores)
            }

        # 总分 60-70 分，需要人工审核
        if total_score < 70:
            return {
                "status": "manual_review",
                "score": total_score,
                "feedback": self._generate_improvement_suggestions(scores)
            }

        # 总分 >= 70 分，自动通过
        return {
            "status": "passed",
            "score": total_score,
            "feedback": "内容质量良好，自动发布"
        }

    def _generate_rejection_reason(self, scores: Dict[str, float]) -> str:
        """生成拒绝原因"""
        reasons = []

        if scores.get("quality_score", 100) < 60:
            reasons.append("内容质量不足")
        if scores.get("originality_check", 100) < 60:
            reasons.append("原创性不足，可能存在抄袭")
        if scores.get("safety_check", 100) < 50:
            reasons.append("内容存在安全风险")
        if scores.get("spam_check", 100) < 50:
            reasons.append("疑似垃圾或广告内容")
        if scores.get("technical_accuracy", 100) < 60:
            reasons.append("技术准确性有待提高")
        if scores.get("completeness", 100) < 60:
            reasons.append("内容不完整")

        return "；".join(reasons) if reasons else "综合评分未达标"

    def _generate_improvement_suggestions(self, scores: Dict[str, float]) -> str:
        """生成改进建议"""
        suggestions = []

        if scores.get("quality_score", 100) < 70:
            suggestions.append("建议提高内容质量，增加详细说明和示例")
        if scores.get("originality_check", 100) < 70:
            suggestions.append("建议增加原创内容，减少对现有资料的引用")
        if scores.get("technical_accuracy", 100) < 70:
            suggestions.append("建议检查技术准确性，确保代码和命令正确")
        if scores.get("completeness", 100) < 70:
            suggestions.append("建议补充完整的内容，包括必要的步骤和说明")

        return "；".join(suggestions) if suggestions else "内容整体良好，稍作优化即可"

    async def _auto_publish_submission(
        self,
        submission: UserSubmission,
        db: AsyncSession
    ):
        """自动发布审核通过的内容"""
        from ..models.tutorials import Tutorial
        from ..models.downloads import Download

        if submission.content_type == "tutorial":
            # 创建教程
            published = Tutorial(
                tutorial_key=re.sub(r'\s+', '-', submission.title_zh_CN.lower()),
                slug=re.sub(r'\s+', '-', submission.title_zh_CN.lower()),
                title_zh_CN=submission.title_zh_CN,
                title_en=submission.title_en,
                description_zh_CN=submission.description_zh_CN,
                description_en=submission.description_en,
                content_zh_CN=submission.content_zh_CN,
                content_en=submission.content_en,
                category=submission.category,
                subcategory=submission.subcategory,
                difficulty=submission.difficulty,
                thumbnail=submission.thumbnail,
                video_url=submission.video_url,
                video_type=submission.video_type,
                video_duration=submission.video_duration,
                github_url=submission.github_url,
                is_paid=submission.is_paid,
                price=float(submission.price) if submission.price else 0,
                creator_id=submission.user_id,
                is_published=True,
                published_at=datetime.utcnow()
            )
            db.add(published)
            await db.flush()

            # 更新提交记录
            submission.published_content_id = published.id
            submission.status = "approved"
            submission.published_at = datetime.utcnow()

        elif submission.content_type == "download":
            # 创建下载资源
            published = Download(
                download_key=re.sub(r'\s+', '-', submission.title_zh_CN.lower()),
                slug=re.sub(r'\s+', '-', submission.title_zh_CN.lower()),
                title_zh_CN=submission.title_zh_CN,
                title_en=submission.title_en,
                description_zh_CN=submission.description_zh_CN,
                description_en=submission.description_en,
                category=submission.category,
                subcategory=submission.subcategory,
                version=submission.version,
                platform=submission.platform,
                file_name=submission.file_name,
                file_url=submission.file_url,
                file_size=submission.file_size,
                file_type=submission.file_type,
                file_checksum=submission.file_checksum,
                github_url=submission.github_url,
                thumbnail=submission.thumbnail,
                is_paid=submission.is_paid,
                price=float(submission.price) if submission.price else 0,
                creator_id=submission.user_id,
                is_published=True,
                published_at=datetime.utcnow()
            )
            db.add(published)
            await db.flush()

            # 更新提交记录
            submission.published_content_id = published.id
            submission.status = "approved"
            submission.published_at = datetime.utcnow()

        # 创建付费产品记录
        if submission.is_paid and submission.price > 0:
            from ..models.paid_products import PaidProduct

            product = PaidProduct(
                content_type=submission.content_type,
                content_id=published.id,
                product_name=submission.title_zh_CN,
                is_free=False,
                price=float(submission.price),
                creator_id=submission.user_id,
                creator_share_percentage=70.0,
                platform_share_percentage=30.0
            )
            db.add(product)

    async def _create_review_record(
        self,
        submission_id: int,
        ai_result: Dict[str, Any],
        review_result: Dict[str, Any],
        db: AsyncSession
    ):
        """创建审核记录"""
        review = AIContentReview(
            content_type="user_submission",
            content_id=submission_id,
            review_type="automated",
            review_model="gpt-4",
            review_result=review_result["status"],
            review_score=review_result["score"],
            review_feedback=review_result["feedback"],
            review_data=ai_result,
            reviewed_at=datetime.utcnow()
        )
        db.add(review)


# 全局实例
ai_moderation_service = AIModerationService()
