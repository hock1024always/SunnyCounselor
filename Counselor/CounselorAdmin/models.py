from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from CounselorApp.models import Client, Counselor, Consultation


class Student(models.Model):
    """学生信息模型"""
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]
    
    name = models.CharField('姓名', max_length=100)
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveSmallIntegerField('年龄', validators=[MinValueValidator(6), MaxValueValidator(25)])
    student_id = models.CharField('学号', max_length=20, unique=True)
    school = models.CharField('学校', max_length=200)
    grade = models.CharField('年级', max_length=50)
    class_name = models.CharField('班级', max_length=50)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    emergency_contact = models.CharField('紧急联系人', max_length=100, blank=True)
    emergency_phone = models.CharField('紧急联系电话', max_length=20, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '学生信息'
        verbose_name_plural = '学生信息'
        ordering = ['school', 'grade', 'class_name', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.school} {self.grade}班"


class Interview(models.Model):
    """访谈记录模型"""
    INTERVIEW_STATUS_CHOICES = [
        ('pending', '待开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    ASSESSMENT_LEVEL_CHOICES = [
        ('low', '低风险'),
        ('medium', '中风险'),
        ('high', '高风险'),
        ('critical', '危急'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', related_name='interviews')
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, verbose_name='咨询师', related_name='interviews')
    interview_date = models.DateTimeField('访谈时间')
    status = models.CharField('状态', max_length=20, choices=INTERVIEW_STATUS_CHOICES, default='pending')
    assessment_level = models.CharField('评估等级', max_length=20, choices=ASSESSMENT_LEVEL_CHOICES, blank=True)
    interview_notes = models.TextField('访谈记录', blank=True)
    follow_up_plan = models.TextField('后续计划', blank=True)
    is_manual_end = models.BooleanField('手动结束', default=False)
    ended_at = models.DateTimeField('结束时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '访谈记录'
        verbose_name_plural = '访谈记录'
        ordering = ['-interview_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.interview_date.strftime('%Y-%m-%d %H:%M')}"


class NegativeEvent(models.Model):
    """负面事件记录模型"""
    EVENT_TYPE_CHOICES = [
        ('academic', '学业问题'),
        ('emotional', '情绪问题'),
        ('behavioral', '行为问题'),
        ('social', '社交问题'),
        ('family', '家庭问题'),
        ('other', '其他'),
    ]
    
    SEVERITY_CHOICES = [
        ('mild', '轻度'),
        ('moderate', '中度'),
        ('severe', '重度'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', related_name='negative_events')
    event_type = models.CharField('事件类型', max_length=20, choices=EVENT_TYPE_CHOICES)
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField('事件描述')
    occurred_at = models.DateTimeField('发生时间')
    reported_by = models.CharField('报告人', max_length=100)
    follow_up_actions = models.TextField('跟进措施', blank=True)
    is_resolved = models.BooleanField('是否解决', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '负面事件'
        verbose_name_plural = '负面事件'
        ordering = ['-occurred_at']
    
    def __str__(self):
        return f"{self.student.name} - {self.get_event_type_display()}"


class ReferralUnit(models.Model):
    """转介单位模型"""
    UNIT_TYPE_CHOICES = [
        ('hospital', '医院'),
        ('psychology_center', '心理咨询中心'),
        ('social_service', '社会服务机构'),
        ('school', '学校相关部门'),
        ('other', '其他'),
    ]
    
    name = models.CharField('单位名称', max_length=200)
    unit_type = models.CharField('单位类型', max_length=20, choices=UNIT_TYPE_CHOICES)
    contact_person = models.CharField('联系人', max_length=100)
    phone = models.CharField('联系电话', max_length=20)
    address = models.TextField('地址')
    description = models.TextField('单位描述', blank=True)
    is_active = models.BooleanField('是否有效', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '转介单位'
        verbose_name_plural = '转介单位'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReferralHistory(models.Model):
    """转介历史记录模型"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', related_name='referrals')
    referral_unit = models.ForeignKey(ReferralUnit, on_delete=models.CASCADE, verbose_name='转介单位')
    reason = models.TextField('转介原因')
    referral_date = models.DateTimeField('转介时间')
    follow_up_notes = models.TextField('跟进记录', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '转介记录'
        verbose_name_plural = '转介记录'
        ordering = ['-referral_date']
    
    def __str__(self):
        return f"{self.student.name} -> {self.referral_unit.name}"


class EducationCategory(models.Model):
    """宣教栏目模型"""
    name = models.CharField('栏目名称', max_length=100)
    description = models.TextField('栏目描述', blank=True)
    order = models.PositiveIntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '宣教栏目'
        verbose_name_plural = '宣教栏目'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class EducationContent(models.Model):
    """宣教内容模型"""
    CONTENT_TYPE_CHOICES = [
        ('article', '文章'),
        ('video', '视频'),
        ('audio', '音频'),
        ('image', '图片'),
    ]
    
    category = models.ForeignKey(EducationCategory, on_delete=models.CASCADE, verbose_name='栏目', related_name='contents')
    title = models.CharField('标题', max_length=200)
    content_type = models.CharField('内容类型', max_length=20, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField('内容')
    thumbnail = models.ImageField('缩略图', upload_to='education/thumbnails/', null=True, blank=True)
    attachment = models.FileField('附件', upload_to='education/attachments/', null=True, blank=True)
    view_count = models.PositiveIntegerField('浏览数', default=0)
    is_published = models.BooleanField('是否发布', default=False)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '宣教内容'
        verbose_name_plural = '宣教内容'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title


class Notification(models.Model):
    """通知管理模型"""
    NOTIFICATION_TYPE_CHOICES = [
        ('system', '系统通知'),
        ('education', '宣教通知'),
        ('event', '活动通知'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('closed', '已关闭'),
    ]
    
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    notification_type = models.CharField('通知类型', max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    target_audience = models.JSONField('目标受众', default=dict)  # 存储受众条件
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    closed_at = models.DateTimeField('关闭时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '通知管理'
        verbose_name_plural = '通知管理'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title


class Banner(models.Model):
    """轮播图管理模型"""
    POSITION_CHOICES = [
        ('home', '首页'),
        ('education', '宣教页'),
        ('consultation', '咨询页'),
    ]
    
    title = models.CharField('标题', max_length=100)
    image = models.ImageField('图片', upload_to='banners/')
    link_url = models.URLField('链接地址', blank=True)
    position = models.CharField('位置', max_length=20, choices=POSITION_CHOICES, default='home')
    order = models.PositiveIntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    start_date = models.DateTimeField('开始时间')
    end_date = models.DateTimeField('结束时间')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = '轮播图'
        ordering = ['position', 'order']
    
    def __str__(self):
        return self.title


class CounselorSchedule(models.Model):
    """咨询师排班模型"""
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, verbose_name='咨询师', related_name='admin_schedules')
    date = models.DateField('排班日期')
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    is_available = models.BooleanField('是否可用', default=True)
    reason = models.CharField('停诊原因', max_length=200, blank=True)
    max_appointments = models.PositiveIntegerField('最大预约数', default=5)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '咨询师排班'
        verbose_name_plural = '咨询师排班'
        ordering = ['date', 'start_time']
        unique_together = ['counselor', 'date', 'start_time']
    
    def __str__(self):
        status = "可用" if self.is_available else f"停诊 - {self.reason}"
        return f"{self.counselor.name} - {self.date} {self.start_time}-{self.end_time} - {status}"


class ConsultationOrder(models.Model):
    """心理咨询订单管理模型"""
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, verbose_name='咨询会话', related_name='order')
    order_number = models.CharField('订单号', max_length=50, unique=True)
    keywords = models.JSONField('咨询关键词', default=list)
    payment_status = models.CharField('支付状态', max_length=20, choices=[
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('refunded', '已退款'),
    ], default='pending')
    payment_amount = models.DecimalField('支付金额', max_digits=10, decimal_places=2, default=0)
    paid_at = models.DateTimeField('支付时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '咨询订单'
        verbose_name_plural = '咨询订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.consultation.client.name}"