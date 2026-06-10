# ============================================================
# 用户相关的请求/响应格式
# 作用：定义注册、登录请求的数据格式，以及返回给前端的数据格式
# ============================================================

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---- 请求格式（前端发给后端的数据） ----

class UserCreate(BaseModel):
    """注册请求：前端需要提交用户名、邮箱、密码"""
    username: str
    email: str  # 邮箱（先当普通字符串处理）
    password: str


class UserLogin(BaseModel):
    """登录请求：前端需要提交用户名和密码"""
    username: str
    password: str


# ---- 响应格式（后端返回给前端的数据） ----

class UserResponse(BaseModel):
    """用户信息响应：返回给前端的用户数据（不包含密码！）"""
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        # 让 Pydantic 能从 SQLAlchemy 模型对象直接转换
        # 比如 UserResponse.model_validate(user_obj)
        from_attributes = True


class Token(BaseModel):
    """登录成功后返回的 token"""
    access_token: str
    token_type: str = "bearer"
