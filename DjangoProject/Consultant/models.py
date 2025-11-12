from django.db import models
from django.contrib.auth.hashers import make_password
from CounselorAdmin.models import Counselor  # 复用现有的Counselor模型


# 咨询师用户表（复用CounselorAdmin的Counselor模型，但添加额外字段）
# 注意：这里我们使用CounselorAdmin的Counselor作为基础用户模型


# 咨询师详情表 (counselor_profiles)
class CounselorProfile(models.Model):
    """
    咨询师详情表
    关联到CounselorAdmin的Counselor模型
    """
    id = models.BigAutoField(primary_key=True, verbose_name='主键ID')
    counselor = models.OneToOneField(
        Counselor,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='咨询师'
    )
    name = models.CharField(max_length=50, null=False, blank=False, verbose_name='真实姓名')
    graduated_school = models.CharField(max_length=100, blank=True, null=True, verbose_name='毕业学校')
    address = models.CharField(max_length=100, blank=True, null=True, verbose_name='所在地区')
    organization = models.CharField(max_length=100, blank=True, null=True, verbose_name='所属机构')
    profession = models.CharField(max_length=50, blank=True, null=True, verbose_name='心理职称')
    expertise = models.JSONField(blank=True, null=True, verbose_name='擅长标签数组')
    introduction = models.TextField(blank=True, null=True, verbose_name='个人介绍')
    experience = models.TextField(blank=True, null=True, verbose_name='从业经验')
    education = models.TextField(blank=True, null=True, verbose_name='教育背景')
    skilled_filed = models.TextField(blank=True, null=True, verbose_name='擅长领域')
    certifications = models.TextField(blank=True, null=True, verbose_name='资质证书')
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name='头像路径')
    consultation_count = models.IntegerField(default=0, verbose_name='咨询次数')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'counselor_profiles'
        verbose_name = '咨询师详情'
        verbose_name_plural = '咨询师详情'

    def __str__(self):
        return self.name


# 咨询师认证Token表
class ConsultantAuthToken(models.Model):
    """
    咨询师登录Token
    """
    id = models.AutoField(primary_key=True)
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name='tokens', verbose_name='咨询师')
    token = models.CharField(max_length=128, unique=True, verbose_name='Token')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')

    class Meta:
        db_table = 'consultant_auth_tokens'
        indexes = [
            models.Index(fields=['token']),
        ]


# 咨询档案主表 (consultation_records)
class ConsultationRecord(models.Model):
    """
    咨询档案主表
    """
    CLIENT_TYPE_CHOICES = [
        ('student', 'student'),
        ('adult', 'adult'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'active'),
        ('completed', 'completed'),
        ('closed', 'closed'),
    ]
    
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='主键ID')
    record_no = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name='档案编号')
    client_name = models.CharField(max_length=50, null=False, blank=False, verbose_name='来访者姓名')
    client_type = models.CharField(max_length=10, choices=CLIENT_TYPE_CHOICES, default='student', verbose_name='来访者类型')
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, null=False, blank=False, verbose_name='性别')
    age = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    student_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='学籍号(学生类型)')
    school = models.CharField(max_length=100, blank=True, null=True, verbose_name='学校')
    grade = models.CharField(max_length=20, blank=True, null=True, verbose_name='年级')
    class_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='班级')
    education = models.CharField(max_length=50, blank=True, null=True, verbose_name='教育程度(成人类型)')
    occupation = models.CharField(max_length=50, blank=True, null=True, verbose_name='职业(成人类型)')
    contact = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系方式')
    emergency_contact_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='紧急联系人姓名')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='紧急联系人电话')
    referral_source = models.CharField(max_length=200, blank=True, null=True, verbose_name='咨询来源')
    main_complaint = models.TextField(blank=True, null=True, verbose_name='主诉问题')
    consultation_goal = models.TextField(blank=True, null=True, verbose_name='咨询目标')
    counselor = models.ForeignKey(
        Counselor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation_records',
        verbose_name='负责咨询师'
    )
    interview_count = models.IntegerField(default=0, verbose_name='总访谈次数')
    current_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='档案状态')
    created_by = models.ForeignKey(
        Counselor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_consultation_records',
        verbose_name='创建人'
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'consultation_records'
        verbose_name = '咨询档案'
        verbose_name_plural = '咨询档案'

    def __str__(self):
        return f"{self.record_no} - {self.client_name}"


# 咨询访谈详情表 (consultation_sessions)
class ConsultationSession(models.Model):
    """
    咨询访谈详情表
    """
    VISIT_STATUS_CHOICES = [
        ('scheduled', 'scheduled'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='主键ID')
    record = models.ForeignKey(
        ConsultationRecord,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='档案'
    )
    session_number = models.IntegerField(null=False, blank=False, verbose_name='第几次访谈')
    interview_date = models.DateField(null=False, blank=False, verbose_name='访谈日期')
    interview_time = models.CharField(max_length=50, blank=True, null=True, verbose_name='访谈时间')
    duration = models.IntegerField(blank=True, null=True, verbose_name='访谈时长(分钟)')
    visit_status = models.CharField(
        max_length=10,
        choices=VISIT_STATUS_CHOICES,
        default='scheduled',
        verbose_name='访谈状态'
    )
    objective_description = models.TextField(blank=True, null=True, verbose_name='客观描述')
    doctor_evaluation = models.TextField(blank=True, null=True, verbose_name='医生评定')
    follow_up_plan = models.TextField(blank=True, null=True, verbose_name='后续计划')
    next_visit_plan = models.TextField(blank=True, null=True, verbose_name='下次访谈计划')
    crisis_status = models.CharField(max_length=50, blank=True, null=True, verbose_name='危机状态')
    consultant_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='咨询师姓名')
    is_third_party_evaluation = models.BooleanField(default=False, verbose_name='是否为他评')
    signature_image = models.CharField(max_length=500, blank=True, null=True, verbose_name='签名图片URL')
    attach_images = models.JSONField(blank=True, null=True, verbose_name='附加图片URL数组')
    created_by = models.ForeignKey(
        Counselor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_sessions',
        verbose_name='创建人'
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'consultation_sessions'
        verbose_name = '咨询访谈'
        verbose_name_plural = '咨询访谈'
        unique_together = [['record', 'session_number']]  # 确保同一档案的访谈次数唯一

    def __str__(self):
        return f"{self.record.record_no} - 第{self.session_number}次访谈"


# 咨询订单表 (consultation_orders)
class ConsultationOrder(models.Model):
    """
    咨询订单表
    """
    SERVICE_TYPE_CHOICES = [
        ('online', 'online'),
        ('offline', 'offline'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled'),
        ('rejected', 'rejected'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='主键ID')
    order_no = models.CharField(max_length=30, unique=True, null=False, blank=False, verbose_name='订单编号')
    record = models.ForeignKey(
        ConsultationRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='关联档案'
    )
    counselor = models.ForeignKey(
        Counselor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='咨询师'
    )
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES, null=False, blank=False, verbose_name='服务类型')
    counseling_keywords = models.JSONField(blank=True, null=True, verbose_name='咨询关键词数组')
    appointment_date = models.DateField(null=False, blank=False, verbose_name='预约日期')
    time_slot = models.CharField(max_length=50, null=False, blank=False, verbose_name='预约时段')
    contact_info = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系方式')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    submit_time = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    accept_time = models.DateTimeField(blank=True, null=True, verbose_name='接单时间')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'consultation_orders'
        verbose_name = '咨询订单'
        verbose_name_plural = '咨询订单'

    def __str__(self):
        return f"{self.order_no} - {self.status}"


# 咨询评价表 (consultation_reviews)
class ConsultationReview(models.Model):
    """
    咨询评价表
    """
    id = models.BigAutoField(primary_key=True, verbose_name='主键ID')
    order = models.ForeignKey(
        ConsultationOrder,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='订单'
    )
    counselor = models.ForeignKey(
        Counselor,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='咨询师'
    )
    rating = models.IntegerField(null=False, blank=False, verbose_name='评分(1-5)')
    content = models.TextField(blank=True, null=True, verbose_name='评价内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'consultation_reviews'
        verbose_name = '咨询评价'
        verbose_name_plural = '咨询评价'

    def __str__(self):
        return f"{self.counselor.name} - {self.rating}分"


# 咨询师排班表 (counselor_schedules) - 新版本，使用JSON存储时间段
class CounselorSchedule(models.Model):
    """
    咨询师排班表
    """
    id = models.BigAutoField(primary_key=True, verbose_name='主键ID')
    counselor = models.ForeignKey(
        Counselor,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='咨询师'
    )
    schedule_date = models.DateField(null=False, blank=False, verbose_name='排班日期')
    time_slots = models.JSONField(null=False, blank=False, verbose_name='时间段数组')
    max_appointments = models.IntegerField(default=5, verbose_name='最大预约数')
    available_slots = models.IntegerField(default=5, verbose_name='剩余可预约数')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'counselor_schedules'
        verbose_name = '咨询师排班'
        verbose_name_plural = '咨询师排班'
        unique_together = [['counselor', 'schedule_date']]  # 确保咨询师同一天只有一个排班记录

    def __str__(self):
        return f"{self.counselor.name} - {self.schedule_date}"


# 停诊记录表 (counselor_absences)
class CounselorAbsence(models.Model):
    """
    停诊记录表
    """
    ABSENCE_TYPE_CHOICES = [
        ('sick_leave', 'sick_leave'),
        ('personal_leave', 'personal_leave'),
        ('other', 'other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('approved', 'approved'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='主键ID')
    counselor = models.ForeignKey(
        Counselor,
        on_delete=models.CASCADE,
        related_name='absences',
        verbose_name='咨询师'
    )
    absence_type = models.CharField(
        max_length=20,
        choices=ABSENCE_TYPE_CHOICES,
        default='personal_leave',
        verbose_name='停诊类型'
    )
    start_time = models.DateTimeField(null=False, blank=False, verbose_name='开始时间')
    end_time = models.DateTimeField(null=False, blank=False, verbose_name='结束时间')
    reason = models.TextField(blank=True, null=True, verbose_name='停诊原因')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'counselor_absences'
        verbose_name = '停诊记录'
        verbose_name_plural = '停诊记录'

    def __str__(self):
        return f"{self.counselor.name} - {self.start_time}"


# 文件存储表 (file_storage)
class FileStorage(models.Model):
    """
    文件存储表
    """
    id = models.BigAutoField(primary_key=True, verbose_name='主键ID')
    file_name = models.CharField(max_length=255, null=False, blank=False, verbose_name='文件名')
    file_path = models.CharField(max_length=500, null=False, blank=False, verbose_name='文件路径')
    file_size = models.BigIntegerField(null=False, blank=False, verbose_name='文件大小')
    file_type = models.CharField(max_length=100, null=False, blank=False, verbose_name='文件类型')
    module = models.CharField(max_length=50, null=False, blank=False, verbose_name='所属模块')
    associated_id = models.BigIntegerField(blank=True, null=True, verbose_name='关联记录ID')
    uploader = models.ForeignKey(
        Counselor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_files',
        verbose_name='上传者'
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'file_storage'
        verbose_name = '文件存储'
        verbose_name_plural = '文件存储'

    def __str__(self):
        return self.file_name
