# ============================================================
# 访问记录模型
# 作用：定义 clicks 表的结构，记录每次短链接被访问的信息
# ============================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Click(Base):
    """
    访问记录表
    - 每次有人点击短链接，就在这里插入一条记录
    - 和 Link 表是多对一关系：一个链接可以被点很多次
    - 单独建表的原因：访问量会很大，方便按时间聚合统计和清理历史数据
    """
    __tablename__ = "clicks"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键：点的是哪个链接
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False)

    # 点击时间
    clicked_at = Column(DateTime, default=datetime.now)

    # 访问者的 IP 地址
    ip_address = Column(String(50), default="")

    # 浏览器/设备信息（User-Agent 字符串）
    # 比如："Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
    user_agent = Column(String(500), default="")

    # 来源页面（从哪个页面跳转来的）
    # 比如从微信打开，referer 可能是 "https://weixin.qq.com"
    referer = Column(String(500), default="")

    # 关系：这条记录属于哪个链接（多对一）
    link = relationship("Link", back_populates="clicks")
