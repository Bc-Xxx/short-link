# ============================================================
# 配置管理文件
# 作用：集中管理所有配置项，从 .env 文件中读取环境变量
# ============================================================

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    应用配置类
    - 继承 BaseSettings，自动从 .env 文件或环境变量中读取值
    - 字段名必须和 .env 里的变量名一致（大小写不敏感）
    """

    # 数据库连接地址（SQLite 文件）
    DATABASE_URL: str = "sqlite:///./shortlink.db"

    # JWT 密钥，用来签名和验证 token（生产环境要换成随机长字符串）
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # JWT 签名算法
    ALGORITHM: str = "HS256"

    # Token 过期时间（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 通义千问 API Key（AI 安全分析用）
    DASHSCOPE_API_KEY: str = ""

    # ---- Redis 缓存配置 ----
    # Railway 会自动注入 REDIS_URL，本地开发用 REDIS_HOST/PORT/DB
    REDIS_URL: str = ""

    # ---- 部署相关配置 ----

    # 短链接完整地址的前缀（部署上线后改成你的域名）
    # 本地开发：http://localhost:8000
    # 生产环境：https://你的域名.com
    BASE_URL: str = "http://localhost:8000"

    # 服务监听地址（Railway 会自动注入 PORT 环境变量）
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        # 指定 .env 文件路径
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    - @lru_cache 保证只创建一次 Settings 对象，避免每次都读 .env 文件
    - 其他地方通过 Depends(get_settings) 注入配置
    """
    return Settings()
