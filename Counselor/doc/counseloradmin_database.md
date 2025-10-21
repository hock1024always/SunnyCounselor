# CounselorAdmin 数据库表字段文档

## 概述
CounselorAdmin是系统管理端应用，包含学生信息管理、访谈记录、负面事件、转介管理、宣教内容、通知管理等系统级功能。

## 数据表结构

### 1. Student（学生信息表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| name | CharField(100) | 姓名 | max_length=100 | - |
| gender | CharField(10) | 性别 | choices=GENDER_CHOICES | - |
| age | PositiveSmallIntegerField | 年龄 | validators=[6,25] | - |
| student_id | CharField(20) | 学号 | unique=True, max_length=20 | - |
| school | CharField(200) | 学校 | max_length=200 | - |
| grade | CharField(50) | 年级 | max_length=50 | - |
| class_name | CharField(50) | 班级 | max_length=50 | - |
| phone | CharField(20) | 联系电话 | blank=True | '' |
| emergency_contact | CharField(100) | 紧急联系人 | blank=True | '' |
| emergency_phone | CharField(20) | 紧急联系电话 | blank=True | '' |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |
| updated_at | DateTimeField | 更新时间 | auto_now=True | 当前时间 |

**性别选项 (GENDER_CHOICES):**
- male: 男
- female: 女  
- other: 其他

### 2. Interview（访谈记录表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| student | ForeignKey(Student) | 学生 | CASCADE, related_name='interviews' | - |
| counselor | ForeignKey(Counselor) | 咨询师 | CASCADE, related_name='interviews' | - |
| interview_date | DateTimeField | 访谈时间 | - | - |
| status | CharField(20) | 状态 | choices=INTERVIEW_STATUS_CHOICES | 'pending' |
| assessment_level | CharField(20) | 评估等级 | choices=ASSESSMENT_LEVEL_CHOICES, blank=True | '' |
| interview_notes | TextField | 访谈记录 | blank=True | '' |
| follow_up_plan | TextField | 后续计划 | blank=True | '' |
| is_manual_end | BooleanField | 手动结束 | default=False | False |
| ended_at | DateTimeField | 结束时间 | null=True, blank=True | null |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |
| updated_at | DateTimeField | 更新时间 | auto_now=True | 当前时间 |

**访谈状态选项 (INTERVIEW_STATUS_CHOICES):**
- pending: 待开始
- in_progress: 进行中  
- completed: 已完成
- cancelled: 已取消

**评估等级选项 (ASSESSMENT_LEVEL_CHOICES):**
- low: 低风险
- medium: 中风险
- high: 高风险
- critical: 危急

### 3. NegativeEvent（负面事件记录表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| student | ForeignKey(Student) | 学生 | CASCADE, related_name='negative_events' | - |
| event_type | CharField(20) | 事件类型 | choices=EVENT_TYPE_CHOICES | - |
| severity | CharField(20) | 严重程度 | choices=SEVERITY_CHOICES | - |
| description | TextField | 事件描述 | - | - |
| occurred_at | DateTimeField | 发生时间 | - | - |
| reported_by | CharField(100) | 报告人 | max_length=100 | - |
| follow_up_actions | TextField | 跟进措施 | blank=True | '' |
| is_resolved | BooleanField | 是否解决 | default=False | False |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |

**事件类型选项 (EVENT_TYPE_CHOICES):**
- academic: 学业问题
- emotional: 情绪问题
- behavioral: 行为问题
- social: 社交问题
- family: 家庭问题
- other: 其他

**严重程度选项 (SEVERITY_CHOICES):**
- mild: 轻度
- moderate: 中度
- severe: 重度

### 4. ReferralUnit（转介单位表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| name | CharField(200) | 单位名称 | max_length=200 | - |
| unit_type | CharField(20) | 单位类型 | choices=UNIT_TYPE_CHOICES | - |
| contact_person | CharField(100) | 联系人 | max_length=100 | - |
| phone | CharField(20) | 联系电话 | max_length=20 | - |
| address | TextField | 地址 | - | - |
| description | TextField | 单位描述 | blank=True | '' |
| is_active | BooleanField | 是否有效 | default=True | True |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |

**单位类型选项 (UNIT_TYPE_CHOICES):**
- hospital: 医院
- psychology_center: 心理咨询中心
- social_service: 社会服务机构
- school: 学校相关部门
- other: 其他

### 5. ReferralHistory（转介历史记录表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| student | ForeignKey(Student) | 学生 | CASCADE, related_name='referrals' | - |
| referral_unit | ForeignKey(ReferralUnit) | 转介单位 | CASCADE | - |
| reason | TextField | 转介原因 | - | - |
| referral_date | DateTimeField | 转介时间 | - | - |
| follow_up_notes | TextField | 跟进记录 | blank=True | '' |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |

### 6. EducationCategory（宣教栏目表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| name | CharField(100) | 栏目名称 | max_length=100 | - |
| description | TextField | 栏目描述 | blank=True | '' |
| order | PositiveIntegerField | 排序 | default=0 | 0 |
| is_active | BooleanField | 是否启用 | default=True | True |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |

### 7. EducationContent（宣教内容表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| category | ForeignKey(EducationCategory) | 栏目 | CASCADE, related_name='contents' | - |
| title | CharField(200) | 标题 | max_length=200 | - |
| content_type | CharField(20) | 内容类型 | choices=CONTENT_TYPE_CHOICES | - |
| content | TextField | 内容 | - | - |
| thumbnail | ImageField | 缩略图 | upload_to='education/thumbnails/' | null=True, blank=True |
| attachment | FileField | 附件 | upload_to='education/attachments/' | null=True, blank=True |
| view_count | PositiveIntegerField | 浏览数 | default=0 | 0 |
| is_published | BooleanField | 是否发布 | default=False | False |
| published_at | DateTimeField | 发布时间 | null=True, blank=True | null |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |
| updated_at | DateTimeField | 更新时间 | auto_now=True | 当前时间 |

**内容类型选项 (CONTENT_TYPE_CHOICES):**
- article: 文章
- video: 视频
- audio: 音频
- image: 图片

### 8. Notification（通知管理表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| title | CharField(200) | 标题 | max_length=200 | - |
| content | TextField | 内容 | - | - |
| notification_type | CharField(20) | 通知类型 | choices=NOTIFICATION_TYPE_CHOICES | - |
| status | CharField(20) | 状态 | choices=STATUS_CHOICES | 'draft' |
| target_audience | JSONField | 目标受众 | default=dict | {} |
| published_at | DateTimeField | 发布时间 | null=True, blank=True | null |
| closed_at | DateTimeField | 关闭时间 | null=True, blank=True | null |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |
| updated_at | DateTimeField | 更新时间 | auto_now=True | 当前时间 |

**通知类型选项 (NOTIFICATION_TYPE_CHOICES):**
- system: 系统通知
- education: 宣教通知
- event: 活动通知
- other: 其他

**状态选项 (STATUS_CHOICES):**
- draft: 草稿
- published: 已发布
- closed: 已关闭

### 9. Banner（轮播图表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| title | CharField(100) | 标题 | max_length=100 | - |
| image | ImageField | 图片 | upload_to='banners/' | - |
| link_url | URLField | 链接地址 | blank=True | '' |
| position | CharField(20) | 位置 | choices=POSITION_CHOICES | 'home' |
| order | PositiveIntegerField | 排序 | default=0 | 0 |
| is_active | BooleanField | 是否启用 | default=True | True |
| start_date | DateTimeField | 开始时间 | - | - |
| end_date | DateTimeField | 结束时间 | - | - |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |

**位置选项 (POSITION_CHOICES):**
- home: 首页
- education: 宣教页
- consultation: 咨询页

### 10. CounselorSchedule（咨询师排班表 - 管理端）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| counselor | ForeignKey(Counselor) | 咨询师 | CASCADE, related_name='admin_schedules' | - |
| date | DateField | 排班日期 | - | - |
| start_time | TimeField | 开始时间 | - | - |
| end_time | TimeField | 结束时间 | - | - |
| is_available | BooleanField | 是否可用 | default=True | True |
| reason | CharField(200) | 停诊原因 | blank=True | '' |
| max_appointments | PositiveIntegerField | 最大预约数 | default=5 | 5 |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |

### 11. ConsultationOrder（心理咨询订单管理表）

| 字段名 | 类型 | 说明 | 约束 | 默认值 |
|--------|------|------|------|--------|
| id | AutoField | 主键ID | PRIMARY KEY | 自动递增 |
| consultation | OneToOneField(Consultation) | 咨询会话 | CASCADE, related_name='order' | - |
| order_number | CharField(50) | 订单号 | unique=True, max_length=50 | - |
| keywords | JSONField | 咨询关键词 | default=list | [] |
| payment_status | CharField(20) | 支付状态 | choices=PAYMENT_STATUS_CHOICES | 'pending' |
| payment_amount | DecimalField | 支付金额 | max_digits=10, decimal_places=2 | 0.00 |
| paid_at | DateTimeField | 支付时间 | null=True, blank=True | null |
| created_at | DateTimeField | 创建时间 | auto_now_add=True | 当前时间 |

**支付状态选项:**
- pending: 待支付
- paid: 已支付
- refunded: 已退款

## 表关系图

```mermaid
erDiagram
    Student ||--o{ Interview : "一对多"
    Counselor ||--o{ Interview : "一对多"
    Student ||--o{ NegativeEvent : "一对多"
    Student ||--o{ ReferralHistory : "一对多"
    ReferralUnit ||--o{ ReferralHistory : "一对多"
    EducationCategory ||--o{ EducationContent : "一对多"
    Counselor ||--o{ CounselorSchedule : "一对多"
    Consultation ||--|| ConsultationOrder : "一对一"
    
    Student {
        int id PK
        varchar name
        varchar gender
        int age
        varchar student_id UK
        varchar school
        varchar grade
        varchar class_name
        varchar phone
        varchar emergency_contact
        varchar emergency_phone
        datetime created_at
        datetime updated_at
    }
    
    Interview {
        int id PK
        int student_id FK
        int counselor_id FK
        datetime interview_date
        varchar status
        varchar assessment_level
        text interview_notes
        text follow_up_plan
        boolean is_manual_end
        datetime ended_at
        datetime created_at
        datetime updated_at
    }
    
    NegativeEvent {
        int id PK
        int student_id FK
        varchar event_type
        varchar severity
        text description
        datetime occurred_at
        varchar reported_by
        text follow_up_actions
        boolean is_resolved
        datetime created_at
    }
    
    ReferralUnit {
        int id PK
        varchar name
        varchar unit_type
        varchar contact_person
        varchar phone
        text address
        text description
        boolean is_active
        datetime created_at
    }
    
    ReferralHistory {
        int id PK
        int student_id FK
        int referral_unit_id FK
        text reason
        datetime referral_date
        text follow_up_notes
        datetime created_at
    }
    
    EducationCategory {
        int id PK
        varchar name
        text description
        int order
        boolean is_active
        datetime created_at
    }
    
    EducationContent {
        int id PK
        int category_id FK
        varchar title
        varchar content_type
        text content
        varchar thumbnail
        varchar attachment
        int view_count
        boolean is_published
        datetime published_at
        datetime created_at
        datetime updated_at
    }
    
    Notification {
        int id PK
        varchar title
        text content
        varchar notification_type
        varchar status
        json target_audience
        datetime published_at
        datetime closed_at
        datetime created_at
        datetime updated_at
    }
    
    Banner {
        int id PK
        varchar title
        varchar image
        varchar link_url
        varchar position
        int order
        boolean is_active
        datetime start_date
        datetime end_date
        datetime created_at
    }
    
    CounselorSchedule {
        int id PK
        int counselor_id FK
        date date
        time start_time
        time end_time
        boolean is_available
        varchar reason
        int max_appointments
        datetime created_at
    }
    
    ConsultationOrder {
        int id PK
        int consultation_id FK UK
        varchar order_number UK
        json keywords
        varchar payment_status
        decimal payment_amount
        datetime paid_at
        datetime created_at
    }
```

## 索引和排序

**Student表:**
- 默认排序: `school`, `grade`, `class_name`, `name`
- 唯一索引: `student_id`

**Interview表:**
- 默认排序: `-interview_date`

**NegativeEvent表:**
- 默认排序: `-occurred_at`

**ReferralHistory表:**
- 默认排序: `-referral_date`

**EducationCategory表:**
- 默认排序: `order`, `name`

**EducationContent表:**
- 默认排序: `-published_at`, `-created_at`

**Notification表:**
- 默认排序: `-published_at`, `-created_at`

**Banner表:**
- 默认排序: `position`, `order`

**CounselorSchedule表:**
- 默认排序: `date`, `start_time`
- 唯一约束: `counselor`, `date`, `start_time`

**ConsultationOrder表:**
- 默认排序: `-created_at`
- 唯一索引: `order_number`, `consultation_id`

## 数据验证规则

1. **年龄验证:**
   - Student: 6-25岁

2. **排班唯一性:**
   - 同一咨询师在同一日期同一时间只能有一个排班

3. **订单唯一性:**
   - 每个咨询会话只能对应一个订单
   - 订单号必须唯一

4. **时间有效性:**
   - Banner的开始时间必须早于结束时间