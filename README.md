# Tutoring Website

全栈家教平台，支持家长/老师/学生/管理员四种角色。

## 技术栈

- 后端：FastAPI + SQLAlchemy + MySQL
- 前端：Vue3 + TypeScript + Vite5 + Naive UI
- 基础设施：Docker Compose (MySQL, Redis, MinIO)

## 快速启动

### 1. 启动基础设施
```bash
docker-compose up -d
```

### 2. 配置后端环境
```bash
cp backend/.env.example backend/.env
```

### 3. 安装后端依赖并初始化数据库
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python seed.py
```

### 4. 启动后端
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. 安装前端依赖并启动
```bash
cd frontend
npm install
npm run dev
```

## 测试账号

| 角色 | 手机号 | 密码 |
|------|--------|------|
| 管理员 | 13800000001 | admin123 |
| 老师 | 13800000002 | teacher123 |
| 家长 | 13800000003 | parent123 |
| 学生 | 13800000004 | student123 |

## API 文档

启动后端后访问: http://localhost:8000/docs

## 项目结构

```
Tutoring_Website/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 配置、数据库、安全
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic schemas
│   │   └── main.py       # FastAPI 入口
│   ├── alembic/          # 数据库迁移
│   └── seed.py           # 种子数据
├── frontend/
│   └── src/
│       ├── views/        # 页面组件
│       ├── components/   # 通用组件
│       ├── composables/  # 组合式函数
│       ├── stores/       # Pinia store
│       ├── api/          # API 请求
│       └── router/       # 路由配置
├── docker-compose.yml    # 基础设施
└── init-db.sql           # 数据库初始化脚本
```
