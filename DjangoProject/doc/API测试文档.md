# API测试文档 - 用户认证模块

## 基础URL
```
http://localhost:8000/counselor_admin
```

## 1. 获取邮箱验证码

**接口**: `POST /auth/register/send_code`

**不需要鉴权**

### 请求示例
```json
{
    "email": "test@example.com",
    "user_name": "testuser",
    "phone": "13800138000"
}
```

### 响应示例（成功）
```json
{
    "message": "验证码已发送"
}
```

### 响应示例（失败）
```json
{
    "message": "email必填"
}
```

**注意**: 验证码会发送到指定邮箱，有效期5分钟。

---

## 2. 用户注册

**接口**: `POST /auth/register`

**不需要鉴权**

### 请求示例
```json
{
    "email": "test@example.com",
    "user_name": "testuser",
    "phone": "13800138000",
    "password": "password123",
    "verify_code": "123456",
    "gender": "男"
}
```

### 响应示例（成功）
```json
{
    "message": "注册成功"
}
```

### 响应示例（失败）
```json
{
    "message": "验证码无效或已过期"
}
```

或

```json
{
    "message": "该邮箱已被注册"
}
```

**说明**:
- `email`: 必填，用于验证码验证
- `user_name`: 必填，用户名
- `password`: 必填，密码
- `verify_code`: 必填，从邮箱获取的验证码
- `phone`: 可选，会存储到数据库但不验证
- `gender`: 可选，默认"男"

---

## 3. 用户登录

**接口**: `POST /auth/login`

**不需要鉴权**

### 请求示例
```json
{
    "email": "test@example.com",
    "password": "password123",
    "captcha": "true"
}
```

### 响应示例（成功）
```json
{
    "token": "2f68dbbf-519d-4f01-9636-e2421b68f379",
    "id": "1"
}
```

### 响应示例（失败）
```json
{
    "message": "用户不存在"
}
```

或

```json
{
    "message": "密码错误"
}
```

**说明**:
- `email`: 必填，用户邮箱
- `password`: 必填，用户密码
- `captcha`: 必填，目前传入 `"true"` 即可

---

## 4. 使用Token鉴权的接口测试

在Apifox中测试需要鉴权的接口时，需要在请求头中添加：

### Header设置
```
Authorization: Bearer <token>
```

例如：
```
Authorization: Bearer 2f68dbbf-519d-4f01-9636-e2421b68f379
```

### 测试示例：获取栏目列表

**接口**: `GET /api/admin/categories`

**需要鉴权**: 是

**Header**:
```
Authorization: Bearer 2f68dbbf-519d-4f01-9636-e2421b68f379
```

**Query参数**:
- `page`: 1
- `page_size`: 10
- `name`: (可选) 栏目名称

### 响应示例（成功）
```json
{
    "total": "10",
    "data": [
        {
            "id": "1",
            "name": "心理健康",
            "order": "1",
            "create_time": "2024-01-01 12:00:00",
            "creator": "admin"
        }
    ]
}
```

### 响应示例（鉴权失败）
```json
{
    "detail": "身份认证信息未提供。"
}
```

---

## 测试流程建议

1. **发送验证码**
   - 使用有效的邮箱地址发送验证码
   - 检查邮箱是否收到验证码（6位数字）

2. **注册用户**
   - 使用刚才收到的验证码进行注册
   - 确保用户名、邮箱、密码都已填写

3. **登录获取Token**
   - 使用注册时的邮箱和密码登录
   - `captcha` 字段填写 `"true"`
   - 保存返回的 `token` 和 `id`

4. **测试需要鉴权的接口**
   - 在Apifox的Header中添加 `Authorization: Bearer <token>`
   - 测试其他接口是否正常工作

---

## 注意事项

1. **验证码有效期**: 5分钟
2. **Token有效期**: 7天
3. **Bearer格式**: 必须严格按照 `Authorization: Bearer <token>` 格式，Bearer和token之间有一个空格
4. **图形验证码**: 目前暂时传入 `"true"` 即可，后续会实现真正的验证码验证

