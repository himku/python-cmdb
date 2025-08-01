# CMDB (Configuration Management Database)

一个基于 FastAPI 构建的现代化配置管理数据库系统，提供完整的资产管理、用户认证和**企业级菜单权限控制**功能。

## ✨ 核心功能特点

### 🔐 企业级认证与权限系统
- **JWT Token 认证** - 安全的无状态认证
- **完整的RBAC权限控制** - 用户↔角色↔权限的多对多关系
- **层级菜单权限管理** - 支持无限级菜单嵌套和权限控制
- **细粒度权限控制** - 页面级+按钮级双重权限验证
- **动态路由生成** - 根据用户权限自动生成前端路由

### 🗂️ 智能菜单管理系统
- **三种菜单类型** - 目录(1)、菜单(2)、按钮(3)
- **层级结构支持** - 无限级菜单嵌套，自动层级计算
- **权限映射** - 菜单与权限代码的精确关联
- **循环引用检测** - 防止菜单层级形成循环
- **可视化管理** - 树形结构的菜单管理界面

### 💻 资产管理能力
- 资产信息管理
- 资产状态追踪  
- 资产关系管理

### 🚀 现代化技术栈
- **FastAPI** - 高性能异步Web框架
- **MySQL** - 关系型数据库
- **Redis** - 高性能缓存
- **SQLAlchemy (异步)** - 现代化ORM
- **Pydantic** - 数据验证和序列化
- **Alembic** - 数据库迁移管理

### 📚 完整的API文档
- 自动生成的 Swagger UI
- ReDoc 文档
- 清晰的权限分级说明

### 🐳 生产就绪
- Docker 容器化支持
- 环境隔离
- 健康检查
- 日志管理

## 🛡️ 权限控制架构

### API接口权限分级

#### 🔓 公开接口 (无需认证)
```bash
/health                    # 健康检查
/docs, /redoc             # API文档
/auth/login               # 用户登录
/auth/register            # 用户注册
/auth/logout              # 用户登出
```

#### 🔐 登录用户接口 (需要Bearer Token)
```bash
# 用户管理
/api/v1/users/*           # 用户CRUD操作

# 用户菜单获取 
/api/v1/menus/user        # 获取用户菜单和路由配置
/api/v1/menus/tree        # 获取用户菜单树
```

#### 🛡️ 系统管理接口 (需要admin角色)
```bash
# 角色权限管理
/api/v1/admin/roles/*           # 角色管理
/api/v1/admin/permissions/*     # 权限管理
/api/v1/admin/roles/{id}/permissions/{id}    # 角色权限关联
/api/v1/admin/users/{id}/roles/{id}          # 用户角色关联

# 菜单管理
/api/v1/admin/menus            # 获取所有菜单列表
/api/v1/admin/menus/tree       # 获取菜单树结构
/api/v1/admin/menus/*          # 菜单CRUD操作
```

### 权限控制特性
- **401 Unauthorized** - 未登录或token无效
- **403 Forbidden** - 权限不足（友好错误提示）
- **404 Not Found** - 资源不存在
- **400 Bad Request** - 数据验证失败

## 技术栈

### 后端核心
- **Python 3.11+** - 现代Python版本
- **FastAPI** - 高性能异步Web框架
- **FastAPI-Users** - 企业级用户认证管理
- **SQLAlchemy 2.0** - 现代异步ORM
- **Alembic** - 数据库迁移工具
- **Pydantic** - 数据验证和序列化

### 数据存储
- **MySQL** - 主数据库 (支持异步aiomysql)
- **Redis** - 缓存和会话存储

### 安全认证
- **JWT** - JSON Web Token认证
- **Argon2/Bcrypt** - 密码哈希算法
- **CORS** - 跨域资源共享

### 部署运维
- **Docker** - 容器化部署
- **uvicorn** - ASGI服务器

## 快速开始

### 环境要求

- Python 3.11 或更高版本
- MySQL 数据库
- Redis 服务器
- Docker (可选)

### 安装与初始化

1. **克隆仓库**：

```bash
git clone https://github.com/himku/python-cmdb.git
cd python-cmdb
```

2. **安装依赖**（推荐用 uv）：

```bash
# 安装 uv（如果还没有安装）
pip install uv

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .\.venv\Scripts\activate  # Windows

uv sync
# 或使用 pip
# pip install -r requirements.txt
```

3. **配置环境变量**：

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量：
# - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
# - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB  
# - SECRET_KEY
```

4. **准备数据库和 Redis**：

```bash
# 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE cmdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 确保 Redis 服务正在运行
redis-server
```

5. **初始化数据库结构**：

```bash
# 运行数据库迁移
alembic upgrade head

# 初始化角色权限数据
python app/database/init_roles_permissions.py

# 初始化菜单数据  
python app/database/init_menus.py
```

### 运行应用

#### 开发环境

```bash
python run.py
# 或
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

## 🗂️ 菜单权限管理系统

### 菜单类型说明

```json
{
  "menu_type": 1,  // 目录 - 用于分组，无具体页面
  "menu_type": 2,  // 菜单 - 实际页面，有路由路径
  "menu_type": 3   // 按钮 - 页面内操作权限
}
```

### 菜单层级结构示例

```
工作台 (菜单)
├── path: /dashboard
└── permission_code: dashboard:view

系统管理 (目录)
├── path: /system
├── permission_code: system:manage
├── 用户管理 (菜单)
│   ├── path: /system/user
│   ├── permission_code: user:manage  
│   ├── 新增用户 (按钮)
│   │   └── permission_code: user:add
│   ├── 编辑用户 (按钮)
│   │   └── permission_code: user:edit
│   └── 删除用户 (按钮)
│       └── permission_code: user:delete
├── 角色管理 (菜单)
├── 权限管理 (菜单)
└── 菜单管理 (菜单)
```

### 菜单API使用示例

#### 普通用户获取菜单
```bash
curl -X GET 'http://localhost:8000/api/v1/menus/user' \
  -H 'Authorization: Bearer {user_token}'
```

**响应示例：**
```json
{
  "menus": [
    {
      "id": 1,
      "name": "dashboard",
      "title": "工作台",
      "path": "/dashboard",
      "icon": "mdi:monitor-dashboard",
      "menu_type": 2,
      "children": []
    }
  ],
  "routes": [
    {
      "name": "dashboard",
      "path": "/dashboard", 
      "component": "views/dashboard/index.vue",
      "meta": {
        "title": "工作台",
        "icon": "mdi:monitor-dashboard",
        "keepAlive": true
      }
    }
  ],
  "permissions": ["dashboard:view", "user:manage"]
}
```

#### 管理员创建菜单
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/menus' \
  -H 'Authorization: Bearer {admin_token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "reports",
    "title": "报表管理",
    "path": "/reports",
    "component": "views/reports/index.vue",
    "menu_type": 2,
    "icon": "mdi:chart-line",
    "permission_code": "reports:view",
    "sort": 10
  }'
```

## 📁 项目结构

```
python-cmdb/
├── app/                           # 应用主目录
│   ├── main.py                   # 🚀 FastAPI应用入口
│   ├── core/                     # 🔧 核心功能模块
│   │   ├── config.py            # ⚙️ 配置管理
│   │   ├── security.py          # 🔐 JWT和密码加密
│   │   └── logging.py           # 📝 日志配置
│   ├── api/                      # 🌐 API路由层
│   │   ├── deps.py              # 💉 依赖注入
│   │   └── v1/                  # 📋 API版本控制
│   │       ├── api.py           # 🔗 路由聚合器
│   │       └── endpoints/       # 🎯 具体API端点
│   │           ├── users.py     # 👤 用户管理API
│   │           ├── roles.py     # 🛡️ 角色权限管理API
│   │           └── menus.py     # 🗂️ 菜单管理API
│   ├── schemas/                  # 📐 Pydantic数据模式
│   │   ├── user.py              # 👤 用户数据模式
│   │   ├── auth.py              # 🔐 认证数据模式
│   │   ├── role.py              # 👥 角色权限模式
│   │   ├── menu.py              # 🗂️ 菜单数据模式
│   │   └── asset.py             # 💻 资产管理模式
│   ├── services/                 # 🔧 业务逻辑层
│   │   ├── user.py              # 👤 用户业务逻辑
│   │   ├── role.py              # 🛡️ 角色业务逻辑
│   │   ├── permission.py        # 🔑 权限业务逻辑
│   │   └── menu.py              # 🗂️ 菜单业务逻辑
│   ├── users/                    # 👥 用户认证模块
│   │   ├── models.py            # 🏛️ 用户、角色、权限、菜单模型
│   │   └── manager.py           # 👤 FastAPI-Users管理器
│   ├── database/                 # 🗄️ 数据库层
│   │   ├── session.py           # 🔗 数据库会话管理
│   │   ├── redis.py             # 🔴 Redis连接管理
│   │   ├── init_db.py           # 🚀 数据库初始化
│   │   ├── init_roles_permissions.py  # 🛡️ 角色权限初始化
│   │   ├── init_menus.py        # 🗂️ 菜单数据初始化
│   │   └── migrations/          # 📈 Alembic数据库迁移
│   └── crud/                     # 📝 数据访问层
│       └── crud.py              # 🔧 通用CRUD操作
├── alembic.ini                   # 🔄 数据库迁移配置
├── pyproject.toml               # 📦 项目依赖和配置
├── uv.lock                      # 🔒 依赖锁定文件
├── Dockerfile                   # 🐳 容器化配置
├── run.py                       # 🏃 应用启动脚本
└── README.md                    # 📖 项目文档
```

## 🏗️ 系统架构深度解析

### 🔐 RBAC权限控制架构

#### 数据模型关系
```
Users ←→ user_role ←→ Roles ←→ role_permission ←→ Permissions
                                       ↓
                                    Menus (permission_code)
```

#### 权限控制流程
1. **用户登录** → 获取JWT Token
2. **访问接口** → Token验证 → 获取用户角色
3. **权限检查** → 角色权限查询 → 访问控制决策
4. **菜单生成** → 根据权限过滤菜单 → 返回可访问菜单树

### 🗂️ 菜单管理架构

#### 核心表结构
**menus表**:
```sql
CREATE TABLE menus (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT '菜单名称',
  title VARCHAR(100) NOT NULL COMMENT '菜单标题',
  path VARCHAR(255) COMMENT '路由路径',
  component VARCHAR(255) COMMENT '组件路径',
  parent_id INT COMMENT '父菜单ID',
  sort INT DEFAULT 0 COMMENT '排序序号',
  level INT DEFAULT 1 COMMENT '菜单层级',
  menu_type INT DEFAULT 1 COMMENT '菜单类型',
  is_visible BOOLEAN DEFAULT TRUE COMMENT '是否显示',
  is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  icon VARCHAR(100) COMMENT '图标',
  permission_code VARCHAR(100) COMMENT '权限代码',
  meta TEXT COMMENT '元数据配置',
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  FOREIGN KEY (parent_id) REFERENCES menus(id)
);
```

#### 菜单特性
- **层级管理**: 自引用外键实现无限级嵌套
- **权限映射**: permission_code字段关联权限系统
- **元数据支持**: meta字段存储自定义配置
- **排序控制**: sort字段控制菜单显示顺序
- **类型区分**: menu_type区分目录、菜单、按钮

### 🚀 异步架构设计

#### 核心特性
- **全异步I/O**: 数据库、Redis、HTTP请求全异步
- **连接池管理**: 高效的连接复用
- **依赖注入**: FastAPI的依赖注入系统
- **会话管理**: 异步数据库会话生命周期管理

#### 性能优势
- **高并发**: 支持大量并发请求
- **低延迟**: 异步操作避免阻塞
- **资源高效**: 连接池和会话复用

## API 文档

启动应用后，可以通过以下地址访问 API 文档：

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

### 权限测试示例

```bash
# 1. 未认证访问admin接口 → 401
curl http://localhost:8000/api/v1/admin/menus

# 2. 普通用户访问admin接口 → 403 + 友好提示
curl -H "Authorization: Bearer user_token" \
     http://localhost:8000/api/v1/admin/menus
# 响应: {"detail": "只有admin角色可以执行此操作"}

# 3. 普通用户访问用户菜单 → 200
curl -H "Authorization: Bearer user_token" \
     http://localhost:8000/api/v1/menus/user
```

## 🔧 系统亮点

### 技术创新
1. **完整的企业级RBAC** - 用户→角色→权限→菜单的完整链路
2. **动态菜单系统** - 基于权限的菜单动态生成
3. **异步优先架构** - 现代Python异步技术栈
4. **细粒度权限控制** - 页面级+按钮级双重权限
5. **智能权限检查** - 友好的错误提示和权限验证

### 架构优势
- **高性能**: 异步I/O + 连接池 + 缓存
- **高安全**: 多层权限验证 + JWT认证
- **高可维护**: 清晰的分层架构和文档
- **高扩展**: 模块化设计支持功能扩展

### 生产就绪特性
- **完整的初始化脚本** - 一键初始化角色权限和菜单
- **Docker容器化** - 生产环境部署支持
- **健康检查** - 应用状态监控
- **错误处理** - 完善的异常处理和日志
- **API文档** - 自动生成的完整文档

## 📈 项目状态

### 已完成功能
- ✅ 完整的用户认证系统 (FastAPI-Users)
- ✅ 企业级RBAC权限控制
- ✅ 智能菜单权限管理系统
- ✅ 动态路由生成
- ✅ 细粒度权限控制 (页面+按钮)
- ✅ 异步数据库架构
- ✅ Redis缓存集成
- ✅ API文档自动生成
- ✅ 容器化部署支持
- ✅ 完整的初始化脚本

### 开发中功能
- 🔄 资产管理功能
- 🔄 审计日志系统
- 🔄 数据备份恢复

这个CMDB系统采用现代化的企业级架构设计，特别是完整的菜单权限管理系统，适合中大型企业的IT资产管理和权限控制需求，具备优秀的性能、安全性和可扩展性。

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
