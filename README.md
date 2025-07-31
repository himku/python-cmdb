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
  - MySQL 数据库
  - Redis 缓存
  - SQLAlchemy ORM
  - Pydantic 数据验证
- 📚 API 文档
  - 自动生成的 Swagger UI
  - ReDoc 文档
- 🐳 Docker 支持
  - 容器化部署
  - 环境隔离

## 技术栈

- Python 3.9+
- FastAPI
- MySQL
- Redis
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- Docker

## 快速开始

### 环境要求

- Python 3.9 或更高版本
- MySQL 数据库
- Redis 服务器
- Docker (可选)

### 安装与初始化

1. 克隆仓库：

```bash
git clone https://github.com/himku/python-cmdb.git
cd python-cmdb
```

2. 安装依赖（推荐用 uv，或用 pip）：

```bash
# 安装 uv（如果还没有安装）
pip install uv

# 安装项目依赖
uv sync
# 或用 pip
pip install -r requirements.txt
```

3. 配置环境变量：

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量：
# - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
# - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB
# - SECRET_KEY
```

4. 准备数据库和 Redis：

```bash
# 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE cmdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 确保 Redis 服务正在运行
redis-server
```

5. 初始化数据库结构（Alembic 迁移）：

```bash
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

### API 接口权限说明

#### 🔓 公开接口 (无需token)
- `/health` - 健康检查
- `/docs`, `/redoc`, `/openapi.json` - API文档
- `/auth/login` - 用户登录
- `/auth/logout` - 用户登出
- `/auth/register` - 用户注册
- `/auth/jwt-cookie/*` - Cookie认证相关接口

#### 🔐 受保护接口 (需要Bearer Token)
- `/api/v1/users/*` - 用户管理接口
  - `GET /api/v1/users/` - 获取用户列表 (仅超级用户)
  - `POST /api/v1/users/` - 创建用户 (仅超级用户)
  - `GET /api/v1/users/{user_id}` - 获取用户详情 (超级用户或本人)
  - `PUT /api/v1/users/{user_id}` - 更新用户信息 (超级用户或本人)
  - `DELETE /api/v1/users/{user_id}` - 删除用户 (仅超级用户)
- 未来的资产管理接口等

#### 使用方式
1. 首先调用登录接口获取token
2. 在后续请求的Header中添加: `Authorization: Bearer <your_token>`

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
│   │   ├── session.py           # 数据库会话管理
│   │   ├── redis.py             # Redis 连接管理
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

## 🏗️ 代码库架构深度解析

### 📋 项目概述
这是一个基于 **FastAPI** 构建的现代化**配置管理数据库（CMDB）**系统，主要用于IT资产管理、用户认证和权限控制。

### 🔧 完整技术栈
- **后端框架**: FastAPI 
- **数据库**: MySQL (使用 aiomysql 异步驱动)
- **缓存**: Redis
- **ORM**: SQLAlchemy (异步)
- **认证**: FastAPI-Users + JWT

- **数据库迁移**: Alembic
- **数据验证**: Pydantic
- **容器化**: Docker

### 📁 详细目录结构分析

#### 核心应用模块 (`app/`)
```
app/
├── main.py                 # 🚀 应用入口，配置FastAPI应用和路由
├── core/                   # 🔧 核心功能模块
│   ├── config.py          # ⚙️ 配置管理（数据库、Redis、JWT等）
│   ├── security.py        # 🔐 JWT令牌和密码加密处理
│   └── logging.py         # 📝 日志配置
├── api/                    # 🌐 API路由层
│   ├── deps.py            # 💉 依赖注入（数据库连接、用户认证）
│   └── v1/                # 📋 API版本控制
│       ├── api.py         # 🔗 API路由聚合器
│       └── endpoints/     # 🎯 具体API端点
│           ├── users.py   # 👤 用户管理API（CRUD操作）
│           └── test.py    # 🧪 测试端点
├── models/                 # 🏛️ 数据模型层
│   └── （用户、角色、权限模型在users/models.py中）
├── schemas/               # 📐 Pydantic数据验证模式
│   ├── user.py           # 👤 用户数据模式
│   ├── auth.py           # 🔐 认证数据模式
│   ├── role.py           # 👥 角色权限模式
│   └── asset.py          # 💻 资产管理模式
├── services/              # 🔧 业务逻辑层
│   └── user.py           # 👤 用户业务逻辑
├── users/                 # 👥 用户管理模块
│   ├── models.py         # 🏛️ 用户、角色、权限数据模型
│   └── manager.py        # 👤 FastAPI-Users用户管理器
├── database/              # 🗄️ 数据库层
│   ├── session.py        # 🔗 数据库连接会话
│   ├── redis.py          # 🔴 Redis连接管理
│   ├── init_db.py        # 🚀 数据库初始化
│   └── migrations/       # 📈 Alembic数据库迁移
└── crud/                  # 📝 数据访问层
    └── crud.py           # 🔧 通用CRUD操作
```

#### 配置和部署文件
```
├── pyproject.toml         # 📦 项目依赖和配置
├── alembic.ini           # 🔄 数据库迁移配置
├── Dockerfile            # 🐳 容器化配置

└── scripts/              # 📜 数据库初始化脚本
```

### 🔐 认证与权限系统

#### 1. 认证层次
- **多重认证后端**: 支持Cookie和Bearer Token两种认证方式
- **JWT策略**: 使用FastAPI-Users进行JWT令牌管理
- **用户管理**: 基于FastAPI-Users的用户注册、登录、验证

#### 2. 权限控制架构
- **RBAC模型**: 用户 ↔ 角色 ↔ 权限的多对多关系
- **基于角色的权限控制**: 精细化权限管理
  - 支持多层级权限控制
  - 基于资源和操作的细粒度控制

#### 3. 数据模型关系
```
Users ←→ user_role ←→ Roles ←→ role_permission ←→ Permissions
```

### 🗄️ 数据库架构

#### 核心表结构
1. **users**: 用户基础信息
   - UUID主键、邮箱、用户名、密码哈希
   - 激活状态、超级用户标记、验证状态
   - 创建时间、更新时间

2. **roles**: 角色定义
   - UUID主键、角色名称、描述

3. **permissions**: 权限定义  
   - UUID主键、权限名称、权限代码、描述



#### 数据库连接特性
- **异步MySQL**: 使用aiomysql驱动实现异步数据库操作
- **连接池**: 通过SQLAlchemy管理数据库连接
- **会话管理**: 异步会话和依赖注入模式

### 🔴 缓存系统 (Redis)
- **连接池管理**: 提供高效的Redis连接复用
- **配置灵活**: 支持密码认证和多数据库
- **健康检查**: 提供连接状态检测功能

### 🛠️ 开发和部署架构

#### API设计模式
- **RESTful风格**: 标准的CRUD操作
- **版本控制**: `/api/v1`前缀进行版本管理  
- **权限控制**: 基于用户角色的接口访问控制
- **自动文档**: Swagger UI和ReDoc文档生成

#### 测试框架
- **单元测试**: 使用pytest进行API测试
- **测试客户端**: FastAPI TestClient集成

#### 容器化部署
- **多阶段构建**: Python 3.9-slim基础镜像
- **安全配置**: 非root用户运行
- **环境变量**: 通过.env文件管理配置

### 🔧 系统关键特性

1. **异步架构**: 全异步的数据库和Redis操作
2. **模块化设计**: 清晰的分层架构（API-Service-Model）
3. **权限精细化**: RBAC角色权限控制
4. **配置管理**: 基于环境变量的配置系统
5. **数据验证**: Pydantic模式验证
6. **迁移管理**: Alembic数据库版本控制
7. **CORS支持**: 跨域资源共享配置
8. **健康检查**: 应用健康状态监控

### 🚀 系统亮点

#### 架构优势
- **高性能**: 异步I/O操作，支持高并发
- **可扩展**: 微服务友好的模块化设计
- **安全**: 多层次的认证和权限控制
- **可维护**: 清晰的代码分层和文档

#### 技术创新
- **FastAPI + SQLAlchemy异步**: 现代Python异步框架组合
- **RBAC权限模型**: 灵活强大的权限管理
- **FastAPI-Users集成**: 开箱即用的用户管理系统

### 📈 项目状态
根据当前开发状态，系统具备：
- ✅ 完整的用户认证系统
- ✅ RBAC权限控制框架
- ✅ RBAC权限控制系统
- ✅ 异步数据库架构
- ✅ Redis缓存集成
- ✅ API文档自动生成
- ✅ 容器化部署支持
- 🔄 资产管理功能开发中

这个CMDB系统采用现代化的微服务架构设计，适合企业级的IT资产管理需求，具备优秀的性能、安全性和可扩展性。

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
