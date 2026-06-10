# ============================================================
# 用户模型
# 作用：定义 users 表的结构
# ============================================================

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """
    用户表
    - 存储注册用户的基本信息
    - 和 Link 表是一对多关系：一个用户可以创建多个短链接
    """
    __tablename__ = "users"

    # 主键，自增
    id = Column(Integer, primary_key=True, index=True)

    # 用户名，唯一，加索引加速查询
    username = Column(String(50), unique=True, index=True, nullable=False)

    # 邮箱，唯一
    email = Column(String(100), unique=True, index=True, nullable=False)

    # 密码哈希值（不是明文密码！用 bcrypt 加密后存的）
    hash_password = Column(String(128), nullable=False)

    # 注册时间，默认当前时间
    created_at = Column(DateTime, default=datetime.now)

    # 关系：一个用户拥有多个短链接
    # back_populates="owner" 表示 Link 模型里有个 owner 字段指向 User
    links = relationship("Link", back_populates="owner")
