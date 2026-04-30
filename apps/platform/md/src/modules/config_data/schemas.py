from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ConfigDataBase(BaseModel):
    """基础配置数据模型"""
    category: str = Field(..., description="分类标识")
    name: str = Field(..., description="数据名称/标识")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="数据内容(JSON格式)")
    position_x: Optional[float] = Field(None, description="X坐标(百分比)")
    position_y: Optional[float] = Field(None, description="Y坐标(百分比)")


class ConfigDataCreate(ConfigDataBase):
    """创建配置数据请求"""
    pass


class ConfigDataUpdate(BaseModel):
    """更新配置数据请求"""
    name: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class ConfigDataResponse(ConfigDataBase):
    """配置数据响应"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigDataListResponse(BaseModel):
    """配置数据列表响应"""
    items: List[ConfigDataResponse]
    total: int
