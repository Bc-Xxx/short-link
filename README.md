# 🔗 短链接服务 (Short Link)

一个基于 **FastAPI** 的短链接服务，支持用户注册登录、短链接生成与管理、访问统计、AI 安全分析。

## ✨ 功能特性

- **🔐 用户系统** — 注册 / 登录（JWT 认证，密码 bcrypt 加密）
- **🔗 短链接管理** — 创建、查看、删除自己的短链接
- **📱 二维码识别** — 上传二维码图片自动识别URL并创建短链接
- **🔄 302 重定向** — 访问短码自动跳转到原始链接
- **📊 访问统计** — 总访问量、今日访问量、近 7 天每日趋势
- **🤖 AI 安全分析** — 创建链接时自动调用通义千问大模型，分析目标 URL 安全性（评分 + 等级 + 理由）
- **🐳 Docker 支持** — 一键容器化部署
- **☁️ 生产就绪** — 支持 PostgreSQL、环境变量配置

## 🏗️ 项目结构

```
short-link/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理（环境变量）
│   ├── database.py          # 数据库引擎与会话
│   ├── models/
│   │   ├── user.py          # 用户模型
│   │   ├── link.py          # 短链接模型
│   │   └── click.py         # 访问记录模型
│   ├── schemas/
│   │   ├── user.py          # 用户请求/响应格式
│   │   └── link.py          # 链接请求/响应/统计格式
│   ├── routers/
│   │   ├── auth.py          # 注册 & 登录接口
│   │   ├── link.py          # 短链接 CRUD & 跳转
│   │   └── stats.py         # 访问统计接口
│   └── utils/
│       ├── security.py      # JWT & 密码加密
│       ├── short_code.py    # 随机短码生成
│       └── ai_analyzer.py   # 通义千问 AI 安全分析
├── templates/
│   └── index.html           # 前端页面（单页应用）
├── tests/                   # 测试目录
├── Dockerfile               # Docker 构建文件
└── .env.example             # 环境变量配置示例
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- （可选）Docker

### 1️⃣ 克隆并安装

```bash
git clone <repo-url>
cd short-link

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入配置
```

### 2️⃣ 配置环境变量

编辑 `.env` 文件：

```ini
DATABASE_URL=sqlite:///./shortlink.db
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
DASHSCOPE_API_KEY=your-api-key    # AI 分析（可选）
BASE_URL=http://localhost:8000
```

### 3️⃣ 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

打开 http://localhost:8000 即可使用。

## 📖 API 接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/auth/register` | 用户注册 | ❌ |
| POST | `/auth/login` | 用户登录，返回 Token | ❌ |
| POST | `/links` | 创建短链接 | ✅ |
| POST | `/links/from-qrcode` | 从二维码图片创建短链接 | ✅ |
| GET | `/links` | 查看我的链接列表 | ✅ |
| GET | `/links/{id}` | 查看链接详情 | ✅ |
| DELETE | `/links/{id}` | 删除链接 | ✅ |
| GET | `/links/{id}/stats` | 查看访问统计 | ✅ |
| GET | `/{short_code}` | 短链接跳转（302） | ❌ |
| GET | `/` | 前端页面 | ❌ |

### 接口示例

**注册用户**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "123456"}'
```

**登录获取 Token**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "123456"}'
```

**创建短链接（需 Token）**

```bash
curl -X POST http://localhost:8000/links \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"original_url": "https://example.com/long-url"}'
```

**从二维码图片创建短链接（需 Token）**

```bash
curl -X POST http://localhost:8000/links/from-qrcode \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@qrcode.png"
```

**查看统计数据**

```bash
curl http://localhost:8000/links/{id}/stats \
  -H "Authorization: Bearer <your-token>"
```

## 🤖 AI 安全分析

创建短链接后，系统自动在后台调用**通义千问大模型**分析目标 URL：

- **安全评分** — 1~10 分（10 分最安全）
- **安全等级** — `安全` / `警告` / `危险`
- **分析理由** — AI 给出的判断依据

> 需要配置 `DASHSCOPE_API_KEY`，前往[阿里云模型服务灵积](https://help.aliyun.com/zh/model-studio/) 申请。

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t short-link .

# 运行容器
docker run -d \
  --name short-link \
  -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e DASHSCOPE_API_KEY="your-api-key" \
  -e BASE_URL="http://localhost:8000" \
  -v $(pwd)/data:/app/data \
  short-link
```

## ☁️ 生产部署（Railway 平台）

1. **Fork / 推送代码到 GitHub**
2. **在 [Railway](https://railway.app) 新建项目，关联 GitHub 仓库**
3. **添加 PostgreSQL 插件** — Railway 会自动设置 `DATABASE_URL` 环境变量
4. **设置环境变量：**

   | 变量 | 说明 |
   |------|------|
   | `SECRET_KEY` | JWT 密钥（随机长字符串） |
   | `DASHSCOPE_API_KEY` | 通义千问 API Key（可选） |
   | `BASE_URL` | `https://你的域名.railway.app` |
   | `ALGORITHM` | `HS256` |

5. 部署完成 ✅

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | FastAPI 0.111 |
| 数据库 | SQLAlchemy 2.0 + SQLite / PostgreSQL |
| 认证 | JWT (python-jose) + bcrypt |
| AI | 通义千问 (DashScope API) |
| 部署 | Docker / Railway |

## 📝 License

MIT
