# CounselorAdmin API接口文档

## 概述
CounselorAdmin提供系统管理端的完整RESTful API接口，支持学生信息管理、访谈记录、负面事件、转介管理、宣教内容、通知管理等系统级功能。

## 基础信息

- **基础URL**: `http://127.0.0.1:8000/admin/`
- **认证方式**: JWT Token认证
- **权限要求**: 管理员权限

## 接口列表

### 1. 学生信息管理

#### GET /admin/api/students/
**描述**: 获取学生列表

**查询参数**:
- `school`: 按学校筛选
- `grade`: 按年级筛选
- `class_name`: 按班级筛选
- `search`: 按姓名或学号搜索

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "张三",
    "gender": "male",
    "age": 18,
    "student_id": "20230001",
    "school": "阳光中学",
    "grade": "高三",
    "class_name": "1班",
    "phone": "13800138000",
    "emergency_contact": "张父",
    "emergency_phone": "13800138001",
    "created_at": "2025-09-01T00:00:00Z",
    "updated_at": "2025-10-20T10:00:00Z"
  }
]
```

#### POST /admin/api/students/
**描述**: 创建学生信息

**请求体**:
```json
{
  "name": "李四",
  "gender": "female",
  "age": 17,
  "student_id": "20230002",
  "school": "阳光中学",
  "grade": "高二",
  "class_name": "2班",
  "phone": "13800138002",
  "emergency_contact": "李母",
  "emergency_phone": "13800138003"
}
```

**响应示例**:
```json
{
  "id": 2,
  "name": "李四",
  "gender": "female",
  "age": 17,
  "student_id": "20230002",
  "school": "阳光中学",
  "grade": "高二",
  "class_name": "2班",
  "phone": "13800138002",
  "emergency_contact": "李母",
  "emergency_phone": "13800138003",
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-20T10:00:00Z"
}
```

#### GET /admin/api/students/{id}/
**描述**: 获取学生详情

**响应示例**:
```json
{
  "id": 1,
  "name": "张三",
  "gender": "male",
  "age": 18,
  "student_id": "20230001",
  "school": "阳光中学",
  "grade": "高三",
  "class_name": "1班",
  "phone": "13800138000",
  "emergency_contact": "张父",
  "emergency_phone": "13800138001",
  "created_at": "2025-09-01T00:00:00Z",
  "updated_at": "2025-10-20T10:00:00Z",
  "interviews": [
    {
      "id": 1,
      "counselor_name": "王咨询师",
      "interview_date": "2025-10-15T14:00:00Z",
      "status": "completed",
      "assessment_level": "medium"
    }
  ],
  "negative_events": [
    {
      "id": 1,
      "event_type": "academic",
      "severity": "mild",
      "occurred_at": "2025-10-10T09:00:00Z",
      "is_resolved": true
    }
  ]
}
```

### 2. 访谈记录管理

#### GET /admin/api/interviews/
**描述**: 获取访谈记录列表

**查询参数**:
- `student_id`: 按学生ID筛选
- `counselor_id`: 按咨询师ID筛选
- `status`: 按状态筛选
- `date_from`: 开始日期
- `date_to`: 结束日期

**响应示例**:
```json
[
  {
    "id": 1,
    "student_name": "张三",
    "counselor_name": "王咨询师",
    "interview_date": "2025-10-15T14:00:00Z",
    "status": "completed",
    "assessment_level": "medium",
    "interview_notes": "学生表现出学业压力，建议定期跟进",
    "follow_up_plan": "每周一次心理辅导",
    "ended_at": "2025-10-15T15:00:00Z",
    "created_at": "2025-10-10T09:00:00Z"
  }
]
```

#### POST /admin/api/interviews/
**描述**: 创建访谈记录

**请求体**:
```json
{
  "student": 1,
  "counselor": 1,
  "interview_date": "2025-10-25T10:00:00Z",
  "assessment_level": "low",
  "interview_notes": "初次访谈，了解基本情况",
  "follow_up_plan": "观察两周后再次评估"
}
```

### 3. 负面事件管理

#### GET /admin/api/negative-events/
**描述**: 获取负面事件列表

**查询参数**:
- `student_id`: 按学生ID筛选
- `event_type`: 按事件类型筛选
- `severity`: 按严重程度筛选
- `date_from`: 开始日期
- `date_to`: 结束日期

**响应示例**:
```json
[
  {
    "id": 1,
    "student_name": "张三",
    "event_type": "academic",
    "severity": "mild",
    "description": "期中考试成绩不理想，情绪低落",
    "occurred_at": "2025-10-10T09:00:00Z",
    "reported_by": "班主任",
    "follow_up_actions": "已安排心理辅导",
    "is_resolved": true,
    "created_at": "2025-10-10T10:00:00Z"
  }
]
```

#### POST /admin/api/negative-events/
**描述**: 创建负面事件记录

**请求体**:
```json
{
  "student": 1,
  "event_type": "emotional",
  "severity": "moderate",
  "description": "学生近期情绪波动较大，上课注意力不集中",
  "occurred_at": "2025-10-20T14:00:00Z",
  "reported_by": "心理老师",
  "follow_up_actions": "安排专业心理咨询"
}
```

### 4. 转介管理

#### GET /admin/api/referral-units/
**描述**: 获取转介单位列表

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "阳光心理咨询中心",
    "unit_type": "psychology_center",
    "contact_person": "李主任",
    "phone": "010-12345678",
    "address": "北京市朝阳区某某路123号",
    "description": "专业心理咨询机构",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### GET /admin/api/referral-history/
**描述**: 获取转介历史记录

**查询参数**:
- `student_id`: 按学生ID筛选
- `referral_unit_id`: 按转介单位ID筛选

**响应示例**:
```json
[
  {
    "id": 1,
    "student_name": "张三",
    "referral_unit_name": "阳光心理咨询中心",
    "reason": "需要专业心理治疗",
    "referral_date": "2025-10-15T10:00:00Z",
    "follow_up_notes": "已安排初次评估",
    "created_at": "2025-10-15T10:00:00Z"
  }
]
```

### 5. 宣教内容管理

#### GET /admin/api/education-categories/
**描述**: 获取宣教栏目列表

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "心理健康",
    "description": "心理健康相关知识",
    "order": 1,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "contents_count": 15
  }
]
```

#### GET /admin/api/education-contents/
**描述**: 获取宣教内容列表

**查询参数**:
- `category_id`: 按栏目ID筛选
- `content_type`: 按内容类型筛选
- `is_published`: 按发布状态筛选

**响应示例**:
```json
[
  {
    "id": 1,
    "category_name": "心理健康",
    "title": "如何应对学业压力",
    "content_type": "article",
    "content": "学业压力是学生常见的问题...",
    "thumbnail": "/media/education/thumbnails/压力管理.jpg",
    "view_count": 256,
    "is_published": true,
    "published_at": "2025-10-01T09:00:00Z",
    "created_at": "2025-09-28T14:00:00Z"
  }
]
```

#### POST /admin/api/education-contents/
**描述**: 创建宣教内容

**请求体**:
```json
{
  "category": 1,
  "title": "情绪管理技巧",
  "content_type": "article",
  "content": "情绪管理是心理健康的重要部分...",
  "is_published": true,
  "published_at": "2025-10-25T09:00:00Z"
}
```

### 6. 通知管理

#### GET /admin/api/notifications/
**描述**: 获取通知列表

**查询参数**:
- `notification_type`: 按通知类型筛选
- `status`: 按状态筛选

**响应示例**:
```json
[
  {
    "id": 1,
    "title": "系统维护通知",
    "content": "系统将于本周六进行维护...",
    "notification_type": "system",
    "status": "published",
    "target_audience": {"schools": ["阳光中学"]},
    "published_at": "2025-10-18T09:00:00Z",
    "created_at": "2025-10-17T14:00:00Z"
  }
]
```

#### POST /admin/api/notifications/
**描述**: 创建通知

**请求体**:
```json
{
  "title": "心理健康讲座通知",
  "content": "本周五下午举办心理健康讲座...",
  "notification_type": "event",
  "target_audience": {
    "grades": ["高一", "高二", "高三"],
    "schools": ["阳光中学"]
  },
  "status": "draft"
}
```

### 7. 轮播图管理

#### GET /admin/api/banners/
**描述**: 获取轮播图列表

**查询参数**:
- `position`: 按位置筛选
- `is_active`: 按启用状态筛选

**响应示例**:
```json
[
  {
    "id": 1,
    "title": "心理健康月活动",
    "image": "/media/banners/心理健康月.jpg",
    "link_url": "https://example.com/activity",
    "position": "home",
    "order": 1,
    "is_active": true,
    "start_date": "2025-10-01T00:00:00Z",
    "end_date": "2025-10-31T23:59:59Z",
    "created_at": "2025-09-28T10:00:00Z"
  }
]
```

### 8. 咨询师排班管理（管理端）

#### GET /admin/api/counselor-schedules/
**描述**: 获取咨询师排班列表

**查询参数**:
- `counselor_id`: 按咨询师ID筛选
- `date`: 按日期筛选
- `is_available`: 按可用状态筛选

**响应示例**:
```json
[
  {
    "id": 1,
    "counselor_name": "王咨询师",
    "date": "2025-10-25",
    "start_time": "09:00:00",
    "end_time": "12:00:00",
    "is_available": true,
    "max_appointments": 5,
    "created_at": "2025-10-20T09:00:00Z"
  }
]
```

### 9. 咨询订单管理

#### GET /admin/api/consultation-orders/
**描述**: 获取咨询订单列表

**查询参数**:
- `payment_status`: 按支付状态筛选
- `date_from`: 开始日期
- `date_to`: 结束日期

**响应示例**:
```json
[
  {
    "id": 1,
    "order_number": "ORDER202510200001",
    "student_name": "张三",
    "counselor_name": "王咨询师",
    "consultation_type": "academic",
    "payment_status": "paid",
    "payment_amount": "200.00",
    "paid_at": "2025-10-20T10:30:00Z",
    "keywords": ["学业压力", "心理疏导"],
    "created_at": "2025-10-20T10:00:00Z"
  }
]
```

## 统计报表接口

### GET /admin/api/dashboard/stats/
**描述**: 管理端数据看板统计

**响应示例**:
```json
{
  "student_stats": {
    "total_students": 1560,
    "new_students_today": 12,
    "students_by_school": {
      "阳光中学": 800,
      "希望中学": 560,
      "未来中学": 200
    }
  },
  "consultation_stats": {
    "total_consultations": 2450,
    "today_consultations": 25,
    "consultations_by_type": {
      "academic": 1200,
      "emotional": 800,
      "relationship": 300,
      "career": 150
    }
  },
  "interview_stats": {
    "total_interviews": 890,
    "completed_interviews": 750,
    "pending_interviews": 140,
    "assessment_distribution": {
      "low": 400,
      "medium": 350,
      "high": 120,
      "critical": 20
    }
  },
  "revenue_stats": {
    "total_revenue": 245000.00,
    "today_revenue": 2500.00,
    "monthly_revenue": 45000.00
  }
}
```

## 错误响应

### 通用错误格式
```json
{
  "error": "错误描述信息",
  "code": "错误代码",
  "details": "详细错误信息（可选）"
}
```

### 常见错误码

- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足（非管理员用户）
- `404`: 资源不存在
- `409`: 资源冲突（如学号重复）
- `500`: 服务器内部错误

## 权限说明

1. **管理员权限**: 所有接口都需要管理员权限
2. **数据访问**: 管理员可以访问所有数据
3. **操作权限**: 支持完整的CRUD操作

## 批量操作接口

### POST /admin/api/students/bulk-import/
**描述**: 批量导入学生信息

**请求体** (multipart/form-data):
- `file`: Excel文件（支持.xlsx格式）

**响应示例**:
```json
{
  "message": "成功导入 50 条学生记录",
  "success_count": 50,
  "error_count": 2,
  "errors": [
    {
      "row": 3,
      "error": "学号已存在"
    },
    {
      "row": 25,
      "error": "年龄格式错误"
    }
  ]
}
```

### POST /admin/api/education-contents/bulk-publish/
**描述**: 批量发布宣教内容

**请求体**:
```json
{
  "content_ids": [1, 2, 3, 4, 5],
  "publish_date": "2025-10-25T09:00:00Z"
}
```

**响应示例**:
```json
{
  "message": "成功发布 5 条宣教内容",
  "published_count": 5,
  "failed_count": 0
}
```

## API版本控制

支持API版本控制，可通过以下路径访问：
- `/admin/api/v1/` - v1版本API