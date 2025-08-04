# 数据库 Casbin 策略系统使用指南

## 🎯 概述

系统已成功升级为基于数据库的 Casbin 策略管理系统。现在所有权限策略都存储在数据库中，**只有超级管理员**可以管理这些策略。

## 🔄 主要变更

### 之前 (文件模式)
- ❌ 策略存储在 CSV 文件中
- ❌ 任何 admin 角色都可以管理策略
- ❌ 需要手动编辑文件

### 现在 (数据库模式)
- ✅ 策略存储在数据库表 `casbin_rule` 中
- ✅ **只有超级管理员** (`is_superuser=True`) 可以管理策略
- ✅ 通过 API 动态管理策略
- ✅ 自动持久化和同步

## 🗄️ 数据库结构

### CasbinRule 表结构
```sql
CREATE TABLE casbin_rule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ptype VARCHAR(255) NOT NULL,     -- 策略类型 (p/g)
    v0 VARCHAR(255),                 -- 主体/角色
    v1 VARCHAR(255),                 -- 对象/资源  
    v2 VARCHAR(255),                 -- 动作/操作
    v3 VARCHAR(255),                 -- 扩展字段
    v4 VARCHAR(255),                 -- 扩展字段
    v5 VARCHAR(255),                 -- 扩展字段
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### 索引
- `idx_casbin_rule_ptype` - 策略类型索引
- `idx_casbin_rule_v0` - 主体/角色索引  
- `idx_casbin_rule_v1` - 对象/资源索引

## 🚀 部署步骤

### 1. 执行数据库迁移
```bash
# 创建 casbin_rule 表
alembic upgrade head
```

### 2. 初始化默认策略
```bash
# 运行初始化脚本
python app/database/init_casbin_policies.py

# 或者通过 API 初始化
curl -X POST "http://localhost:8000/api/v1/admin/casbin/initialize/" \
  -H "Authorization: Bearer SUPERUSER_TOKEN"
```

## 🔐 权限级别

### 策略管理权限
- **超级管理员** (`is_superuser=True`): 可以管理所有策略
- **普通管理员** (`admin` 角色): 只能使用策略，不能管理
- **其他用户**: 根据分配的角色使用相应权限

### 默认策略
```
# 角色权限策略
admin -> /api/v1/admin/* [*]
admin -> /api/v1/users/* [*]
user_manager -> /api/v1/users/* [GET/POST/PUT]
viewer -> /api/v1/users/* [GET]
anonymous -> /docs, /redoc, /openapi.json, /health [GET]
anonymous -> /auth/* [*]

# 用户角色分配
alice -> admin
bob -> user_manager  
charlie -> viewer
```

## 🎮 API 接口 (仅超级管理员)

### 策略管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/v1/admin/casbin/policies/` | 获取所有策略 | 超级管理员 |
| POST | `/api/v1/admin/casbin/policies/` | 添加策略 | 超级管理员 |
| DELETE | `/api/v1/admin/casbin/policies/` | 删除策略 | 超级管理员 |

### 角色管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/v1/admin/casbin/roles/` | 获取所有角色 | 超级管理员 |
| POST | `/api/v1/admin/casbin/users/roles/` | 为用户分配角色 | 超级管理员 |
| DELETE | `/api/v1/admin/casbin/users/roles/` | 移除用户角色 | 超级管理员 |
| GET | `/api/v1/admin/casbin/users/{username}/roles/` | 获取用户角色 | 超级管理员 |
| GET | `/api/v1/admin/casbin/roles/{role}/users/` | 获取角色用户 | 超级管理员 |

### 权限检查

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/v1/admin/casbin/check/` | 检查用户权限 | 超级管理员 |
| GET | `/api/v1/admin/casbin/users/{username}/permissions/` | 获取用户权限 | 超级管理员 |

### 系统管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/v1/admin/casbin/sync/` | 同步数据库角色 | 超级管理员 |
| POST | `/api/v1/admin/casbin/initialize/` | 初始化默认策略 | 超级管理员 |
| POST | `/api/v1/admin/casbin/reload/` | 重新加载策略 | 超级管理员 |

## 📝 使用示例

### 1. 添加新策略 (仅超级管理员)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/casbin/policies/" \
  -H "Authorization: Bearer SUPERUSER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "editor",
    "obj": "/api/v1/content/*",
    "act": "GET"
  }'
```

### 2. 为用户分配角色 (仅超级管理员)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/casbin/users/roles/" \
  -H "Authorization: Bearer SUPERUSER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "role": "editor"
  }'
```

### 3. 检查用户权限 (仅超级管理员)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/casbin/check/" \
  -H "Authorization: Bearer SUPERUSER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "obj": "/api/v1/content/articles",
    "act": "GET"
  }'
```

### 4. 获取所有策略 (仅超级管理员)
```bash
curl -X GET "http://localhost:8000/api/v1/admin/casbin/policies/" \
  -H "Authorization: Bearer SUPERUSER_TOKEN"
```

## 🛠️ 开发集成

### 代码中检查权限
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

### 管理策略 (仅在代码中，需要超级管理员权限)
```python
from app.services.casbin_service import CasbinService

# 添加策略
success = CasbinService.add_policy("editor", "/api/v1/content/*", "GET")

# 为用户分配角色
success = CasbinService.add_role_for_user("john", "editor")

# 保存到数据库 (自动完成)
```

## 🚨 安全注意事项

### 1. 超级管理员权限
- **严格控制**: 只有真正的系统管理员才应该拥有 `is_superuser=True`
- **最小权限原则**: 不要轻易给用户分配超级管理员权限
- **审计日志**: 记录所有策略变更操作

### 2. 策略管理
- **谨慎操作**: 策略变更会立即生效，影响所有用户
- **备份重要**: 定期备份 `casbin_rule` 表
- **测试验证**: 在测试环境验证策略变更

### 3. 角色分配
- **定期审查**: 定期检查用户角色分配的合理性
- **最小权限**: 给用户分配满足需求的最小权限
- **及时回收**: 员工离职或角色变更时及时回收权限

## 🔄 迁移指南

### 从文件模式迁移到数据库模式

1. **备份现有配置**
   ```bash
   cp app/core/rbac_policy.csv app/core/rbac_policy.csv.backup
   ```

2. **执行数据库迁移**
   ```bash
   alembic upgrade head
   ```

3. **初始化策略**
   ```bash
   python app/database/init_casbin_policies.py
   ```

4. **验证迁移**
   - 测试 API 访问权限
   - 验证用户角色分配
   - 检查策略生效情况

## 🎉 优势总结

### 数据库模式的优势
- ✅ **动态管理**: 无需重启应用即可变更策略
- ✅ **安全控制**: 只有超级管理员可以管理策略
- ✅ **持久化**: 策略自动保存到数据库
- ✅ **可扩展**: 支持复杂的权限模型
- ✅ **审计追踪**: 可以记录策略变更历史
- ✅ **高性能**: 数据库索引优化查询性能

### 适用场景
- 🎯 **企业级应用**: 需要严格的权限控制
- 🎯 **多租户系统**: 复杂的角色权限管理
- 🎯 **合规要求**: 需要权限审计和追踪
- 🎯 **动态权限**: 需要运行时调整权限

您的权限系统现在已经升级为企业级的数据库策略管理系统！🔐 