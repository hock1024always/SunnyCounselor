from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Counselor(models.Model):
    """
    咨询师信息模型类
    用于存储和管理咨询师的基本信息、服务类型等数据
    """
    # 性别选择选项
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]

    # 服务类型选择选项
    SERVICE_TYPE_CHOICES = [
        ('academic', '学业压力'),
        ('emotional', '情感咨询'),
        ('relationship', '人际关系'),
        ('career', '职业规划'),
        ('other', '其他'),
    ]

    # 关联用户模型，一对一关系
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='counselor')
    # 咨询师姓名
    name = models.CharField('姓名', max_length=100)
    # 性别，使用预定义选项
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES)
    # 年龄，范围限制在18-70岁之间
    age = models.PositiveSmallIntegerField('年龄', validators=[MinValueValidator(18), MaxValueValidator(70)])
    # 手机号码
    phone = models.CharField('手机号', max_length=20)
    # 电子邮箱
    email = models.EmailField('邮箱')
    # 头像图片，允许为空
    avatar = models.ImageField('头像', upload_to='counselor_avatars/', null=True, blank=True)
    # 服务类型配置，使用JSON格式存储
    service_types = models.JSONField('服务类型配置', default=list)
    # 个人介绍，允许为空
    introduction = models.TextField('个人介绍', blank=True)
    # 从业年限，默认为0
    years_of_experience = models.PositiveSmallIntegerField('从业年限', default=0)
    # 是否激活状态，默认为激活
    is_active = models.BooleanField('是否激活', default=True)
    # 创建时间，自动记录创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间，自动记录最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        # 模型显示名称
        verbose_name = '咨询师'
        verbose_name_plural = '咨询师'
        # 默认排序方式，按创建时间降序
        ordering = ['-created_at']

    def __str__(self):
        # 返回咨询师的字符串表示，格式为"姓名 - 性别"
        return f"{self.name} - {self.get_gender_display()}"


class Client(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    name = models.CharField('姓名', max_length=100)
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveSmallIntegerField('年龄', validators=[MinValueValidator(12), MaxValueValidator(30)])
    phone = models.CharField('手机号', max_length=20)
    student_id = models.CharField('学号', max_length=20, blank=True)
    created_at = models.DateTimeField('注册时间', auto_now_add=True)

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'

    def __str__(self):
        return f"{self.name} - {self.get_gender_display()}"


class Consultation(models.Model):
    CONSULTATION_TYPE_CHOICES = [
        ('academic', '学业压力'),
        ('emotional', '情感咨询'),
        ('relationship', '人际关系'),
        ('career', '职业规划'),
        ('other', '其他'),
    ]

    STATUS_CHOICES = [
        ('pending', '待接单'),
        ('in_progress', '咨询中'),
        ('completed', '已结束'),
        ('rejected', '已拒绝'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='客户', related_name='consultations')
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, verbose_name='咨询师',
                                  related_name='consultations')
    type = models.CharField('咨询类型', max_length=20, choices=CONSULTATION_TYPE_CHOICES)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField('预约时间')
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    ended_at = models.DateTimeField('结束时间', null=True, blank=True)
    description = models.TextField('问题描述', blank=True)
    notes = models.TextField('咨询笔记', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '咨询会话'
        verbose_name_plural = '咨询会话'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.client.name} - {self.counselor.name} - {self.get_status_display()}"

    @property
    def duration(self):
        """计算咨询时长（分钟）"""
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds() // 60
        return 0


class Schedule(models.Model):
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, verbose_name='咨询师', related_name='schedules')
    date = models.DateField('排班日期')
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    is_available = models.BooleanField('是否可用', default=True)
    reason = models.CharField('停诊原因', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '排班'
        verbose_name_plural = '排班'
        ordering = ['date', 'start_time']
        unique_together = ['counselor', 'date', 'start_time']

    def __str__(self):
        status = "可用" if self.is_available else f"停诊 - {self.reason}"
        return f"{self.counselor.name} - {self.date} {self.start_time}-{self.end_time} - {status}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1星'),
        (2, '2星'),
        (3, '3星'),
        (4, '4星'),
        (5, '5星'),
    ]

    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, verbose_name='咨询会话',
                                        related_name='review')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='客户', related_name='reviews')
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, verbose_name='咨询师', related_name='reviews')
    rating = models.PositiveSmallIntegerField('评分', choices=RATING_CHOICES,
                                              validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField('评论内容')
    is_anonymous = models.BooleanField('是否匿名', default=False)
    created_at = models.DateTimeField('评论时间', auto_now_add=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

    def __str__(self):
        anonymous = "匿名" if self.is_anonymous else self.client.name
        return f"{anonymous} - {self.counselor.name} - {self.rating}星"