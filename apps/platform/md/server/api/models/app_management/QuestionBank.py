# -*- coding: utf-8 -*-
from application import db
from common.models.model.PageDataProperty import PageDataProperty
from datetime import datetime


class QuestionBank(db.Model, PageDataProperty):
    __tablename__ = 'question_banks'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='题库ID')
    bank_name = db.Column(db.String(200), nullable=False, comment='题库名称')
    bank_category = db.Column(db.String(100), comment='题库分类')
    difficulty_level = db.Column(db.String(50), comment='难度等级: easy/medium/hard')
    total_questions = db.Column(db.Integer, default=0, comment='总题数')
    choice_count = db.Column(db.Integer, default=0, comment='选择题数量')
    judgement_count = db.Column(db.Integer, default=0, comment='判断题数量')
    time_limit = db.Column(db.Integer, comment='时间限制(秒)')
    pass_score = db.Column(db.Integer, comment='及格分数')
    total_score = db.Column(db.Integer, comment='总分')
    tags = db.Column(db.String(500), comment='标签(逗号分隔)')
    cover_image = db.Column(db.String(500), comment='封面图片URL')
    description = db.Column(db.Text, comment='题库描述')
    question_data = db.Column(db.Text, comment='题目数据(JSON)')
    prize_config = db.Column(db.Text, comment='奖品配置(JSON)')
    is_public = db.Column(db.Integer, nullable=False, default=1, comment='是否公开: 0-私有 1-公开')
    sort_order = db.Column(db.Integer, default=0, comment='排序顺序')
    status = db.Column(db.Integer, nullable=False, default=1, comment='状态: 1-正常 2-禁用 3-删除')
    created_by = db.Column(db.Integer, comment='创建人ID')
    updated_by = db.Column(db.Integer, comment='更新人ID')
    created_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'bank_id': self.bank_id,
            'bank_name': self.bank_name,
            'bank_category': self.bank_category,
            'difficulty_level': self.difficulty_level,
            'total_questions': self.total_questions,
            'choice_count': self.choice_count,
            'judgement_count': self.judgement_count,
            'time_limit': self.time_limit,
            'pass_score': self.pass_score,
            'total_score': self.total_score,
            'tags': self.tags,
            'cover_image': self.cover_image,
            'description': self.description,
            'question_data': self.question_data,
            'prize_config': self.prize_config,
            'is_public': self.is_public,
            'sort_order': self.sort_order,
            'status': self.status,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None,
            'updated_time': self.updated_time.strftime('%Y-%m-%d %H:%M:%S') if self.updated_time else None
        }
