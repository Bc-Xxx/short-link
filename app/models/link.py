# ============================================================
# 短链接模型
# 作用：定义 links 表的结构（核心表）
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Link(Base):
    """
    短链接表
    - 存储短码和原始链接的映射关系
    - short_code 字段加了索引，因为每次跳转都要根据它查数据库
    """
    __tablename__ = "links"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 短码，比如 "aB3xK9"
    # unique=True：不能重复
    # index=True：加索引！这是重点，每次跳转都要根据短码查数据库
    short_code = Column(String(10), unique=True, index=True, nullable=False)

    # 用户提交的原始长链接
    original_url = Column(String(2048), nullable=False)

    # 网页标题（AI 分析时抓取的）
    title = Column(String(500), default="")

    # 是否启用（用户可以禁用短链接而不删除）
    is_active = Column(Boolean, default=True)

    # 过期时间，为空表示永不过期
    expires_at = Column(DateTime, nullable=True)

    # ---- AI 安全分析字段 ----

    # 安全评分：1-10，10分最安全
    safety_score = Column(Integer, nullable=True)

    # 安全等级：安全 / 警告 / 危险
    safety_level = Column(String(10), default="待分析")

    # AI 给出的分析理由
    safety_reason = Column(String(500), default="")

    # ---- 关联字段 ----

    # 外键：这个链接是谁创建的
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 创建时间
    created_at = Column(DateTime, default=datetime.now)

    # 关系：这个链接的创建者（多对一）
    owner = relationship("User", back_populates="links")

    # 关系：这个链接的所有访问记录（一对多，级联删除）
    clicks = relationship("Click", back_populates="link", cascade="all, delete-orphan")
