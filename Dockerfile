# ============================================
# 短链接服务 Dockerfile
# 基于 Python 3.11，使用清华镜像加速安装
# ============================================

# 基础镜像：轻量级 Python 3.11
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 用清华镜像源加速 pip 安装
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 先复制 requirements.txt，利用 Docker 缓存机制
# 只要 requirements.txt 不变，这层缓存就不会失效
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录（SQLite 文件放这里）
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 启动命令（使用 PORT 环境变量，Railway 会自动设置）
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
