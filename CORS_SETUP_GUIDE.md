# 🌐 CMDB CORS 配置指南

## ✅ 已完成的CORS配置

### 1. 🔧 服务器端配置

**配置文件**: `app/core/config.py`

```python
# CORS 配置 - 跨域资源共享设置
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:3000",     # React 开发服务器
    "http://localhost:8080",     # Vue 开发服务器  
    "http://localhost:5173",     # Vite 开发服务器
    "http://localhost:4200",     # Angular 开发服务器
    "http://localhost:8000",     # Django/其他框架
    "http://localhost:9000",     # 其他常用端口
    "http://localhost:9527",     # Vue Admin Template
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080", 
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:9000",
    "http://127.0.0.1:9527",
]

# 开发环境自动添加通配符支持
if ENVIRONMENT == "development":
    BACKEND_CORS_ORIGINS.append("*")
```

**CORS高级配置**:
- ✅ `allow_credentials: true` - 支持携带认证信息
- ✅ `allow_methods: GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH` - 支持所有HTTP方法
- ✅ `allow_headers` - 包含认证头和自定义头
- ✅ `max_age: 86400` - 预检请求缓存24小时

### 2. 🛡️ 中间件配置

**文件**: `app/main.py`

```python
# 中间件顺序（重要！）
# 1. CORS中间件（最后执行）
app.add_middleware(CORSMiddleware, ...)

# 2. Casbin权限中间件（倒数第二执行）
app.add_middleware(CasbinMiddleware, ...)

# 3. 认证中间件（倒数第三执行）
app.add_middleware(AuthenticationMiddleware, ...)

# 4. 日志中间件（最先执行）
app.add_middleware(LoggingMiddleware)
```

### 3. 📊 CORS调试端点

**端点**: `GET /api/v1/users/cors-debug`

返回当前CORS配置和请求信息，用于调试跨域问题。

## 🧪 CORS测试工具

### 方法1: 使用测试页面

1. **启动CMDB API服务器**:
   ```bash
   source .venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

2. **启动CORS测试服务器**:
   ```bash
   python3 start_cors_test.py [端口] [测试文件]
   ```
   
   示例:
   ```bash
   python3 start_cors_test.py 3001          # 默认端口3001
   python3 start_cors_test.py 5000          # 使用端口5000
   ```

3. **自动打开浏览器**测试页面，进行各种CORS测试

### 方法2: 使用curl命令

1. **测试OPTIONS预检请求**:
   ```bash
   curl -v \
     -H "Origin: http://localhost:3001" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8080/health
   ```

2. **测试实际跨域请求**:
   ```bash
   curl -v \
     -H "Origin: http://localhost:3001" \
     -H "Content-Type: application/json" \
     http://localhost:8080/health
   ```

3. **测试带认证的跨域请求**:
   ```bash
   # 先获取token
   TOKEN=$(curl -s -X POST \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=admin123" \
     http://localhost:8080/auth/login | \
     python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
   
   # 使用token访问受保护的API
   curl -v \
     -H "Origin: http://localhost:3001" \
     -H "Authorization: Bearer $TOKEN" \
     http://localhost:8080/users/me
   ```

## 🔍 CORS响应头说明

成功的CORS响应应包含以下头部:

```
access-control-allow-origin: http://localhost:3001
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH
access-control-allow-headers: Accept, Accept-Language, ...
access-control-allow-credentials: true
access-control-max-age: 86400
```

## 🚨 常见CORS问题和解决方案

### 问题1: "CORS policy has blocked the request"

**原因**: 请求的源不在允许列表中

**解决方案**:
1. 检查前端应用运行的端口
2. 将端口添加到 `BACKEND_CORS_ORIGINS` 列表
3. 开发环境确保包含 `"*"` 通配符

### 问题2: "Preflight request doesn't pass"

**原因**: OPTIONS预检请求失败

**解决方案**:
1. 确保 `allow_methods` 包含请求的HTTP方法
2. 确保 `allow_headers` 包含请求的自定义头部
3. 检查中间件顺序

### 问题3: "Credentials include but CORS doesn't allow"

**原因**: 凭据模式配置错误

**解决方案**:
1. 设置 `allow_credentials: true`
2. 不能同时使用 `"*"` 通配符和 credentials
3. 为生产环境配置具体的域名

### 问题4: 认证失败但CORS正常

**原因**: 中间件执行顺序错误

**解决方案**:
```python
# 正确的顺序（后添加的先执行）
app.add_middleware(CORSMiddleware, ...)        # 最后执行
app.add_middleware(CasbinMiddleware, ...)      # 倒数第二
app.add_middleware(AuthenticationMiddleware, ...) # 倒数第三
app.add_middleware(LoggingMiddleware)          # 最先执行
```

## 📈 性能优化

1. **预检缓存**: `max_age: 86400` (24小时)
2. **生产环境**: 移除 `"*"` 通配符，使用具体域名
3. **压缩响应**: 启用gzip压缩
4. **CDN**: 使用CDN分发静态资源

## 🛠️ 开发环境 vs 生产环境

### 开发环境
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173", 
    # ... 其他开发端口
    "*"  # 开发环境通配符
]
```

### 生产环境
```python
BACKEND_CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://admin.yourdomain.com",
    # 只允许具体的生产域名
]
```

## 📝 日志监控

使用日志系统监控CORS请求:

```bash
# 查看CORS相关日志
python3 view_logs.py filter "CORS"
python3 view_logs.py filter "Origin"

# 实时监控
python3 view_logs.py follow
```

## 🎯 测试检查清单

- [ ] OPTIONS预检请求返回正确头部
- [ ] 简单GET/POST请求正常工作  
- [ ] 带认证的请求正常工作
- [ ] 不同端口的请求都能访问
- [ ] 错误响应也包含CORS头部
- [ ] 生产环境配置了具体域名

---

✅ **CORS配置完成！你的前端应用现在可以正常访问CMDB API了。** 