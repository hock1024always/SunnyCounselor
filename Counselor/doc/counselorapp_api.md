# CounselorApp API接口文档

## 概述
CounselorApp提供咨询师工作台的完整RESTful API接口，支持数据统计、咨询管理、排班管理、评论查看等功能。

## 基础信息

- **基础URL**: `http://127.0.0.1:8000/counselor/`
- **认证方式**: JWT Token认证
- **权限要求**: 咨询师权限（CounselorPermission）

## 接口列表

### 1. 首页和数据看板

#### GET /counselor/
**描述**: 咨询师工作台首页

**响应示例**:
```json
{
  "message": "欢迎访问咨询师工作台",
  "user": "counselor_username",
  "counselor": "咨询师姓名"
}
```

#### GET /counselor/dashboard/stats/
**描述**: 数据看板统计信息

**响应示例**:
```json
{
  "today_stats": {
    "total": 15,
    "pending": 3,
    "in_progress": 5,
    "completed": 7
  },
  "yearly_total": 245,
  "type_distribution": [
    {"type": "academic", "count": 120},
    {"type": "emotional", "count": 80},
    {"type": "relationship", "count": 30},
    {"type": "career", "count": 15}
  ],
  "gender_distribution": [
    {"client__gender": "male", "count": 130},
    {"client__gender": "female", "count": 115}
  ],
  "age_distribution": [
    {"client__age": 18, "count": 45},
    {"client__age": 19, "count": 52},
    {"client__age": 20, "count": 48}
  ],
  "time_slot_distribution": [
    {"hour": "09:00-10:00", "count": 2},
    {"hour": "10:00-11:00", "count": 3},
    {"hour": "11:00-12:00", "count": 1},
    {"hour": "14:00-15:00", "count": 4},
    {"hour": "15:00-16:00", "count": 3},
    {"hour": "16:00-17:00", "count": 2}
  ],
  "average_rating": 4.8
}
```

### 2. 咨询管理

#### GET /counselor/consultations/pending/
**描述**: 待接单咨询列表

**响应示例**:
```json
[
  {
    "id": 1,
    "client": 101,
    "client_name": "张三",
    "client_gender": "male",
    "client_age": 20,
    "type": "academic",
    "status": "pending",
    "scheduled_at": "2025-10-21T14:00:00Z",
    "started_at": null,
    "ended_at": null,
    "description": "学业压力大，需要心理疏导",
    "notes": "",
    "created_at": "2025-10-20T10:00:00Z"
  }
]
```

#### GET /counselor/consultations/in-progress/
**描述**: 咨询中列表

**响应示例**:
```json
[
  {
    "id": 2,
    "client": 102,
    "client_name": "李四",
    "client_gender": "female",
    "client_age": 19,
    "type": "emotional",
    "status": "in_progress",
    "scheduled_at": "2025-10-20T15:00:00Z",
    "started_at": "2025-10-20T15:05:00Z",
    "ended_at": null,
    "description": "情感问题咨询",
    "notes": "正在进行中...",
    "created_at": "2025-10-19T09:00:00Z"
  }
]
```

#### GET /counselor/consultations/completed/
**描述**: 已结束咨询列表

**响应示例**:
```json
[
  {
    "id": 3,
    "client": 103,
    "client_name": "王五",
    "client_gender": "male",
    "client_age": 21,
    "type": "career",
    "status": "completed",
    "scheduled_at": "2025-10-19T10:00:00Z",
    "started_at": "2025-10-19T10:00:00Z",
    "ended_at": "2025-10-19T10:45:00Z",
    "description": "职业规划咨询",
    "notes": "咨询顺利完成，提供了职业建议",
    "created_at": "2025-10-18T14:00:00Z"
  }
]
```

#### GET /counselor/consultations/rejected/
**描述**: 已拒绝咨询列表

**响应示例**:
```json
[
  {
    "id": 4,
    "client": 104,
    "client_name": "赵六",
    "client_gender": "female",
    "client_age": 22,
    "type": "relationship",
    "status": "rejected",
    "scheduled_at": "2025-10-18T16:00:00Z",
    "started_at": null,
    "ended_at": null,
    "description": "人际关系问题",
    "notes": "",
    "created_at": "2025-10-17T11:00:00Z"
  }
]
```

#### POST /counselor/api/consultations/{id}/accept/
**描述**: 接受咨询

**请求体**: 无

**响应示例**:
```json
{
  "message": "咨询已接受"
}
```

#### POST /counselor/api/consultations/{id}/reject/
**描述**: 拒绝咨询

**请求体**: 无

**响应示例**:
```json
{
  "message": "咨询已拒绝"
}
```

#### POST /counselor/api/consultations/{id}/complete/
**描述**: 完成咨询

**请求体**: 无

**响应示例**:
```json
{
  "message": "咨询已完成"
}
```

### 3. 排班管理

#### GET /counselor/api/schedules/
**描述**: 获取排班列表

**响应示例**:
```json
[
  {
    "id": 1,
    "date": "2025-10-21",
    "start_time": "09:00:00",
    "end_time": "12:00:00",
    "is_available": true,
    "reason": ""
  },
  {
    "id": 2,
    "date": "2025-10-21",
    "start_time": "14:00:00",
    "end_time": "17:00:00",
    "is_available": true,
    "reason": ""
  }
]
```

#### POST /counselor/api/schedules/
**描述**: 创建单个排班

**请求体**:
```json
{
  "date": "2025-10-22",
  "start_time": "09:00:00",
  "end_time": "12:00:00",
  "is_available": true,
  "reason": ""
}
```

**响应示例**:
```json
{
  "id": 3,
  "date": "2025-10-22",
  "start_time": "09:00:00",
  "end_time": "12:00:00",
  "is_available": true,
  "reason": ""
}
```

#### POST /counselor/schedules/bulk-create/
**描述**: 批量创建排班

**请求体**:
```json
{
  "dates": ["2025-10-23", "2025-10-24", "2025-10-25"],
  "start_time": "09:00:00",
  "end_time": "12:00:00"
}
```

**响应示例**:
```json
{
  "message": "成功创建 3 个排班",
  "schedules": [
    {
      "id": 4,
      "date": "2025-10-23",
      "start_time": "09:00:00",
      "end_time": "12:00:00",
      "is_available": true,
      "reason": ""
    },
    {
      "id": 5,
      "date": "2025-10-24",
      "start_time": "09:00:00",
      "end_time": "12:00:00",
      "is_available": true,
      "reason": ""
    },
    {
      "id": 6,
      "date": "2025-10-25",
      "start_time": "09:00:00",
      "end_time": "12:00:00",
      "is_available": true,
      "reason": ""
    }
  ]
}
```

#### POST /counselor/schedules/stop-service/
**描述**: 添加停诊安排

**请求体**:
```json
{
  "date": "2025-10-26",
  "reason": "参加培训会议"
}
```

**响应示例**:
```json
{
  "message": "已停诊 2 个排班",
  "date": "2025-10-26",
  "reason": "参加培训会议"
}
```

### 4. 评论管理

#### GET /counselor/api/reviews/
**描述**: 获取评论列表

**响应示例**:
```json
[
  {
    "id": 1,
    "client_name": "张三",
    "rating": 5,
    "comment": "咨询师非常专业，解答了我的困惑",
    "is_anonymous": false,
    "created_at": "2025-10-19T11:00:00Z"
  },
  {
    "id": 2,
    "client_name": "匿名用户",
    "rating": 4,
    "comment": "服务态度很好",
    "is_anonymous": true,
    "created_at": "2025-10-18T15:30:00Z"
  }
]
```

### 5. 个人资料管理

#### GET /counselor/profile/
**描述**: 获取个人资料

**响应示例**:
```json
{
  "id": 1,
  "name": "王咨询师",
  "gender": "male",
  "age": 35,
  "phone": "13800138000",
  "email": "counselor@example.com",
  "avatar": "/media/counselor_avatars/avatar.jpg",
  "service_types": ["academic", "emotional"],
  "introduction": "资深心理咨询师，擅长学业压力和情感咨询",
  "years_of_experience": 10
}
```

#### PUT /counselor/profile/update/
**描述**: 更新个人资料

**请求体**:
```json
{
  "name": "王咨询师",
  "gender": "male",
  "age": 36,
  "phone": "13800138001",
  "email": "counselor_updated@example.com",
  "introduction": "资深心理咨询师，10年从业经验",
  "years_of_experience": 11
}
```

**响应示例**:
```json
{
  "id": 1,
  "name": "王咨询师",
  "gender": "male",
  "age": 36,
  "phone": "13800138001",
  "email": "counselor_updated@example.com",
  "avatar": "/media/counselor_avatars/avatar.jpg",
  "service_types": ["academic", "emotional"],
  "introduction": "资深心理咨询师，10年从业经验",
  "years_of_experience": 11
}
```

#### PUT /counselor/profile/service-types/
**描述**: 更新服务类型配置

**请求体**:
```json
{
  "service_types": ["academic", "emotional", "career"]
}
```

**响应示例**:
```json
{
  "service_types": ["academic", "emotional", "career"]
}
```

## 错误响应

### 通用错误格式
```json
{
  "error": "错误描述信息",
  "code": "错误代码（可选）"
}
```

### 常见错误码

- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足（非咨询师用户）
- `404`: 资源不存在
- `500`: 服务器内部错误

## 权限说明

1. **咨询师权限**: 所有接口都需要咨询师权限
2. **数据隔离**: 每个咨询师只能访问自己的数据
3. **操作限制**: 只能操作自己相关的咨询、排班、评论等

## API版本控制

支持API版本控制，可通过以下路径访问：
- `/counselor/api/v1/` - v1版本API