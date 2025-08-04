# Casbin 权限系统使用指南

## 🎯 概述

本项目已成功集成 [fastapi-authz](https://github.com/pycasbin/fastapi-authz) 权限控制系统，基于强大的 Casbin 库实现 RBAC (基于角色的访问控制)。

## 📖 API 文档访问

**重要**: API 文档现在可以正常访问！我们已经配置了匿名用户权限：

- ✅ **Swagger UI**: http://localhost:8000/docs
- ✅ **ReDoc**: http://localhost:8000/redoc  
- ✅ **OpenAPI JSON**: http://localhost:8000/openapi.json
- ✅ **健康检查**: http://localhost:8000/health
- ✅ **认证接口**: http://localhost:8000/auth/*

### 启动服务器

```bash
# 使用测试脚本启动
python test_server.py

# 或者直接使用 uvicorn
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 🚀 功能特性

- ✅ **RBAC 权限模型**: 支持用户-角色-权限的三层架构
- ✅ **通配符匹配**: 支持路径通配符 (`/api/v1/admin/*`) 和操作通配符 (`*`)
- ✅ **动态策略管理**: 可以在运行时添加、删除权限策略
- ✅ **用户角色管理**: 支持为用户分配/移除角色
- ✅ **中间件集成**: 自动拦截所有API请求进行权限检查
- ✅ **API管理界面**: 提供完整的权限管理API接口
- ✅ **匿名访问支持**: API文档和登录接口对匿名用户开放

## 📁 文件结构

```
app/
├── core/
│   ├── rbac_model.conf        # Casbin RBAC 模型配置
│   └── rbac_policy.csv        # 权限策略数据
├── services/
│   └── casbin_service.py      # Casbin 服务封装
├── api/
│   ├── middleware.py          # 认证中间件
│   └── v1/endpoints/
│       └── casbin.py          # 权限管理API
└── main.py                    # 中间件集成
```

## 🔧 配置说明

### 1. RBAC 模型 (`app/core/rbac_model.conf`)

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && keyMatch2(r.obj, p.obj) && (r.act == p.act || p.act == "*")
```

### 2. 权限策略 (`app/core/rbac_policy.csv`)

```csv
p, admin, /api/v1/admin/*, *
p, admin, /api/v1/users/*, *
p, user_manager, /api/v1/users/*, GET
p, user_manager, /api/v1/users/*, POST
p, user_manager, /api/v1/users/*, PUT
p, viewer, /api/v1/users/*, GET

# 匿名用户权限（用于访问文档和登录）
p, anonymous, /docs, GET
p, anonymous, /redoc, GET
p, anonymous, /openapi.json, GET
p, anonymous, /health, GET
p, anonymous, /auth/*, *

g, alice, admin
g, bob, user_manager
g, charlie, viewer
```

## 🎮 API 接口

### 策略管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/admin/casbin/policies/` | 获取所有策略 |
| POST | `/api/v1/admin/casbin/policies/` | 添加策略 |
| DELETE | `/api/v1/admin/casbin/policies/` | 删除策略 |

### 角色管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/admin/casbin/roles/` | 获取所有角色 |
| POST | `/api/v1/admin/casbin/users/roles/` | 为用户分配角色 |
| DELETE | `/api/v1/admin/casbin/users/roles/` | 移除用户角色 |
| GET | `/api/v1/admin/casbin/users/{username}/roles/` | 获取用户角色 |
| GET | `/api/v1/admin/casbin/roles/{role}/users/` | 获取角色用户 |

### 权限检查

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/admin/casbin/check/` | 检查用户权限 |
| GET | `/api/v1/admin/casbin/users/{username}/permissions/` | 获取用户权限 |

### 同步管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/admin/casbin/sync/` | 从数据库同步用户角色 |

## 📝 使用示例

### 1. 添加新策略

```bash
curl -X POST "http://localhost:8000/api/v1/admin/casbin/policies/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "editor",
    "obj": "/api/v1/content/*",
    "act": "GET"
  }'
```

### 2. 为用户分配角色

```bash
curl -X POST "http://localhost:8000/api/v1/admin/casbin/users/roles/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "role": "editor"
  }'
```

### 3. 检查用户权限

```bash
curl -X POST "http://localhost:8000/api/v1/admin/casbin/check/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "obj": "/api/v1/content/articles",
    "act": "GET"
  }'
```

## 🔐 权限层级

### 预定义角色

1. **admin**: 超级管理员
   - 拥有所有 `/api/v1/admin/*` 和 `/api/v1/users/*` 权限
   - 可以执行任何操作 (`*`)

2. **user_manager**: 用户管理员
   - 可以查看、创建、修改用户 (`GET`, `POST`, `PUT`)
   - 无法删除用户或访问系统管理功能

3. **viewer**: 查看者
   - 只能查看用户信息 (`GET`)
   - 无法进行任何修改操作

4. **anonymous**: 匿名用户
   - 可以访问API文档和健康检查
   - 可以访问所有认证相关接口

### 权限匹配规则

- **精确匹配**: `/api/v1/users/123` 匹配策略 `/api/v1/users/123`
- **通配符匹配**: `/api/v1/users/123` 匹配策略 `/api/v1/users/*`
- **操作通配符**: 任何操作匹配策略中的 `*`

## 🛠️ 开发集成

### 在代码中检查权限

```python
from app.services.casbin_service import CasbinService

# 检查用户权限
has_permission = CasbinService.check_permission(
    user="alice", 
    obj="/api/v1/admin/users", 
    act="GET"
)

if has_permission:
    # 执行操作
    pass
else:
    # 权限不足
    raise HTTPException(status_code=403, detail="权限不足")
```

### 同步数据库角色

```python
from app.services.casbin_service import CasbinService

# 从数据库同步用户角色到 Casbin
await CasbinService.sync_user_roles_from_db(db)
```

## 🚨 注意事项

1. **策略持久化**: 动态添加的策略会保存到 `rbac_policy.csv` 文件
2. **数据库同步**: 在用户角色变更后，建议调用同步API确保一致性
3. **权限缓存**: Casbin 会缓存权限策略，重启应用后会重新加载
4. **超级用户**: `is_superuser=True` 的用户可能需要特殊处理
5. **认证中间件**: 确保认证中间件正确提取用户身份
6. **匿名访问**: 所有用户（包括未认证）都会被分配 `anonymous` 身份

## 🎉 测试验证

权限系统已通过完整测试，包括：

- ✅ 基本权限检查 (用户访问不同资源的权限验证)
- ✅ 动态策略管理 (运行时添加/删除策略)
- ✅ 通配符匹配 (路径和操作的灵活匹配)
- ✅ 角色分配管理 (用户角色的动态分配)
- ✅ 中间件集成 (自动权限拦截)
- ✅ 匿名访问支持 (API文档和登录接口开放)

系统已准备好在生产环境中使用！ 