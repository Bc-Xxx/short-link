# ============================================================
# 数据库连接文件
# 作用：创建数据库引擎、会话工厂，提供 get_db 依赖注入
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

# 获取配置
settings = get_settings()

# 创建数据库引擎
# SQLite 需要 check_same_thread=False 来允许多线程访问
# PostgreSQL 不需要这个参数，所以根据连接字符串自动选择
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# 会话工厂
# - 每次调用 SessionLocal() 就创建一个新的数据库会话
# - autocommit=False：不会自动提交事务，需要手动 commit
# - autoflush=False：不会自动刷新，需要手动 flush 或 commit
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
# 所有的数据库模型都要继承这个 Base，SQLAlchemy 才能识别它们
Base = declarative_base()


def get_db():
    """
    数据库会话依赖（FastAPI 依赖注入用法）

    这是一个生成器函数：
    - yield 之前：创建会话
    - yield：把会话交给接口函数使用
    - yield 之后（finally）：关闭会话，释放资源

    在接口函数中这样用：
        def create_link(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
