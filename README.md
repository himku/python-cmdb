# CMDB (Configuration Management Database)

一个基于 FastAPI 构建的现代化配置管理数据库系统，提供完整的资产管理、用户认证和权限控制功能。

## 功能特点

- 🔐 用户认证和授权
  - JWT token 认证
  - 基于角色的访问控制 (RBAC)
  - 细粒度的权限管理
- 💻 资产管理
  - 资产信息管理
  - 资产状态追踪
  - 资产关系管理
- 🚀 现代化技术栈
  - FastAPI 框架
  - PostgreSQL 数据库
  - SQLAlchemy ORM
  - Pydantic 数据验证
- 📚 API 文档
  - 自动生成的 Swagger UI
  - ReDoc 文档
- 🐳 Docker 支持
  - 容器化部署
  - 环境隔离

## 技术栈

- Python 3.13+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- Docker

## 快速开始

### 环境要求

- Python 3.13 或更高版本
- PostgreSQL 数据库
- Docker (可选)

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/python-cmdb.git
cd python-cmdb
```

2. 创建并激活虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置环境变量：

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

5. 初始化数据库：

```bash
# 创建数据库
createdb cmdb

# 运行数据库迁移
alembic upgrade head
```

### 运行应用

#### 开发环境

```bash
uvicorn app.main:app --reload
```

#### 生产环境

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Docker 部署

```bash
# 构建镜像
docker build -t cmdb .

# 运行容器
docker run -p 8000:8000 cmdb
```

## API 文档

启动应用后，可以通过以下地址访问 API 文档：

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## 项目结构

```
cmdb/
├── app/                           # 应用主目录
│   ├── core/                     # 核心功能模块
│   │   ├── config.py            # 配置管理
│   │   ├── logging.py           # 日志配置
│   │   └── security.py          # 安全相关
│   ├── api/                      # API 路由
│   │   ├── deps.py              # 依赖注入
│   │   ├── asset.py             # 资产管理 API
│   │   ├── user.py              # 用户管理 API
│   │   └── auth.py              # 认证 API
│   ├── models/                   # 数据模型
│   │   ├── asset.py             # 资产模型
│   │   ├── user.py              # 用户模型
│   │   └── role.py              # 角色模型
│   ├── schemas/                  # Pydantic 模型
│   │   ├── asset.py             # 资产模式
│   │   ├── user.py              # 用户模式
│   │   └── auth.py              # 认证模式
│   ├── crud/                     # CRUD 操作
│   │   ├── asset.py             # 资产 CRUD
│   │   ├── user.py              # 用户 CRUD
│   │   └── role.py              # 角色 CRUD
│   ├── database/                 # 数据库配置
│   │   ├── session.py           # 会话管理
│   │   └── init_db.py           # 数据库初始化
│   ├── services/                 # 业务逻辑
│   │   ├── asset_service.py     # 资产服务
│   │   ├── user_service.py      # 用户服务
│   │   └── auth_service.py      # 认证服务
│   └── main.py                  # 应用入口
├── alembic/                      # 数据库迁移
├── tests/                        # 测试文件
├── requirements.txt              # 项目依赖
├── Dockerfile                    # Docker 配置
└── README.md                     # 项目文档
```

## 开发指南

### 代码风格

- 遵循 PEP 8 规范
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序

### 提交规范

提交信息格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型（type）：

- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建

### 分支管理

- main: 主分支
- develop: 开发分支
- feature/*: 功能分支
- bugfix/*: 修复分支
- release/*: 发布分支

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目维护者：[himku](https://github.com/himku)
- 邮箱：[baemawu@gmail.com](mailto:baemawu@gmail.com)
- 项目链接：[https://github.com/himku/python-cmdb](https://github.com/himku/python-cmdb)
