from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.database import engine, Base
from app.routers import auth, link, stats

# 创建所有数据库表（如果表不存在的话）
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(title="短链接服务", version="1.0.0")

# 注册路由
app.include_router(auth.router)
app.include_router(link.router)
app.include_router(stats.router)


# 前端页面
@app.get("/", response_class=HTMLResponse)
def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
