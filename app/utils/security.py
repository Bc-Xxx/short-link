# ============================================================
# 安全工具文件
# 作用：JWT token 的创建和验证、密码加密和校验
# ============================================================

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db

settings = get_settings()

# ---- 密码加密 ----

# 创建密码加密上下文
# bcrypt 是一种单向哈希算法，把密码变成不可逆的哈希值
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """把明文密码加密成哈希值"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码：把用户输入的密码加密后，和数据库里存的哈希值对比"""
    return pwd_context.verify(plain_password, hashed_password)


# ---- JWT Token ----

# OAuth2PasswordBearer 告诉 FastAPI：token 从哪个接口获取
# 当你用 Depends(get_current_user) 时，FastAPI 会自动从
# 请求头的 Authorization 字段里提取 Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict) -> str:
    """
    创建 JWT token

    参数 data 的格式一般是 {"sub": "用户ID"}
    - to_encode：复制一份数据，加上过期时间
    - jwt.encode：用密钥签名，生成 token 字符串

    生成的 token 长这样：
    eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzE4MDAwMDAwfQ.abc123签名
    """
    to_encode = data.copy()
    # 设置过期时间：当前时间 + 配置的分钟数
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 用密钥和算法签名
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    从请求中提取当前登录用户（FastAPI 依赖注入）

    流程：
    1. FastAPI 从请求头 Authorization: Bearer xxx 里提取 token
    2. jwt.decode 解码 token，拿到 payload（包含用户ID）
    3. 根据用户ID去数据库查用户
    4. 返回用户对象

    如果 token 无效或用户不存在，返回 401 未授权
    """
    from app.models.user import User  # 延迟导入，避免循环引用

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解码 token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        # 从 payload 中取出用户ID（创建时放在 "sub" 字段里）
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 根据用户ID查数据库
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user
