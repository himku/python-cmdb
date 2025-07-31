# 🔗 API 接口结构说明

## 📋 总体设计原则

1. **权限分离**：管理员API与普通用户API分开
2. **路径清晰**：通过路径前缀区分不同权限级别
3. **功能分组**：相关功能归类到同一模块

## 🛣️ API 路由结构

### 🔐 认证相关 (`/auth/`)
```
POST /auth/login          # 用户登录
POST /auth/register       # 用户注册  
POST /auth/logout         # 用户登出
```

### 👤 用户管理 (`/api/v1/users/`)
**权限要求：登录用户**
```
GET    /users              # 获取用户列表
POST   /users              # 创建用户
GET    /users/{user_id}    # 获取用户详情
PUT    /users/{user_id}    # 更新用户
DELETE /users/{user_id}    # 删除用户
```

### 🛡️ 系统管理 (`/api/v1/admin/`)
**权限要求：admin角色**

#### 角色权限管理
```
# 角色管理
GET    /admin/roles        # 获取角色列表
POST   /admin/roles        # 创建角色
GET    /admin/roles/{id}   # 获取角色详情
PUT    /admin/roles/{id}   # 更新角色
DELETE /admin/roles/{id}   # 删除角色

# 权限管理
GET    /admin/permissions  # 获取权限列表
POST   /admin/permissions  # 创建权限
DELETE /admin/permissions/{id}  # 删除权限

# 角色权限关联
POST   /admin/roles/{role_id}/permissions/{permission_id}     # 分配权限给角色
DELETE /admin/roles/{role_id}/permissions/{permission_id}     # 移除角色权限

# 用户角色关联  
POST   /admin/users/{user_id}/roles/{role_id}                # 分配角色给用户
DELETE /admin/users/{user_id}/roles/{role_id}                # 移除用户角色
```

#### 菜单管理
```
GET    /admin/menus        # 获取所有菜单列表
GET    /admin/menus/tree   # 获取菜单树结构
POST   /admin/menus        # 创建菜单
GET    /admin/menus/{id}   # 获取菜单详情
PUT    /admin/menus/{id}   # 更新菜单
DELETE /admin/menus/{id}   # 删除菜单
```

### 🗂️ 用户菜单 (`/api/v1/menus/`)
**权限要求：登录用户**
```
GET /menus/user            # 获取当前用户的菜单和路由配置
GET /menus/tree            # 获取当前用户的菜单树
```

## 🎯 权限控制说明

### 1. **公开接口（无需认证）**
- `POST /auth/login` - 登录
- `POST /auth/register` - 注册
- `GET /docs` - API文档
- `GET /health` - 健康检查

### 2. **登录用户接口**
- `/api/v1/users/*` - 用户基本操作
- `/api/v1/menus/*` - 获取用户菜单

### 3. **管理员接口**
- `/api/v1/admin/*` - 所有系统管理功能
- 需要用户具有 `admin` 角色或 `is_superuser=True`

## 🔧 接口使用示例

### 普通用户获取菜单
```bash
curl -X GET 'http://localhost:8000/api/v1/menus/user' \
  -H 'Authorization: Bearer {user_token}'
```

### 管理员管理菜单
```bash
# 获取所有菜单
curl -X GET 'http://localhost:8000/api/v1/admin/menus' \
  -H 'Authorization: Bearer {admin_token}'

# 创建菜单
curl -X POST 'http://localhost:8000/api/v1/admin/menus' \
  -H 'Authorization: Bearer {admin_token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "reports",
    "title": "报表管理", 
    "path": "/reports",
    "menu_type": 2
  }'
```

## ⚠️ 错误响应规范

### 权限不足 (403)
```json
{
  "detail": "只有admin角色可以执行此操作"
}
```

### 资源不存在 (404)
```json
{
  "detail": "菜单不存在"
}
```

### 数据验证失败 (400)
```json
{
  "detail": "菜单名称已存在"
}
```

## 📊 API分组总结

| 模块 | 路径前缀 | 权限要求 | 功能 |
|------|----------|----------|------|
| 认证 | `/auth/` | 无 | 登录注册 |
| 用户 | `/api/v1/users/` | 登录用户 | 用户CRUD |
| 菜单 | `/api/v1/menus/` | 登录用户 | 获取用户菜单 |
| 系统管理 | `/api/v1/admin/` | admin角色 | 角色权限菜单管理 |

这样的结构清晰地区分了不同权限级别的接口，避免了路径重合和权限混乱的问题。 