# ============================================================
# 短链接相关的请求/响应格式
# 作用：定义创建、查询短链接的数据格式
# ============================================================

from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


# ---- 请求格式 ----

class LinkCreate(BaseModel):
    """创建短链接请求：前端提交一个长链接"""
    original_url: str  # 原始长链接
    custom_code: Optional[str] = None  # 自定义短码（可选）


# ---- 响应格式 ----

class LinkResponse(BaseModel):
    """短链接响应：创建成功后返回的数据"""
    id: int
    short_code: str
    original_url: str
    short_url: str  # 完整的短链接地址
    title: Optional[str] = ""
    safety_level: str = "待分析"
    safety_score: Optional[int] = None
    safety_reason: Optional[str] = ""
    click_count: int = 0  # 总访问次数
    created_at: datetime

    class Config:
        from_attributes = True


class LinkListResponse(BaseModel):
    """链接列表响应（分页）"""
    total: int  # 总数
    links: list[LinkResponse]  # 链接列表


class ClickStats(BaseModel):
    """单条访问记录"""
    clicked_at: datetime
    ip_address: str
    user_agent: str
    referer: str

    class Config:
        from_attributes = True


class DailyStat(BaseModel):
    """按天统计"""
    date: str
    count: int


class LinkStats(BaseModel):
    """链接统计信息"""
    total_clicks: int  # 总访问量
    today_clicks: int  # 今日访问量
    daily_stats: list[DailyStat]  # 最近7天每天的访问量
