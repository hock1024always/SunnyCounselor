from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


# 咨询师管理器
class CounselorManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名必须设置')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


# 咨询师表
class Counselor(AbstractBaseUser):
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    STATUS_CHOICES = [
        ('启用', '启用'),
        ('停用', '停用'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='咨询师姓名')
    username = models.CharField(max_length=50, unique=True, verbose_name='系统用户昵称')
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name='性别')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='邮箱地址')
    organization = models.CharField(max_length=100, blank=True, verbose_name='所属机构')
    expertise_tags = models.JSONField(blank=True, null=True, verbose_name='擅长标签')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='启用', verbose_name='状态')

    objects = CounselorManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'gender', 'phone']

    class Meta:
        db_table = 'counselors'
        verbose_name = '咨询师'
        verbose_name_plural = '咨询师'

    def __str__(self):
        return self.name


# 预约订单表
class Appointment(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('个体咨询', '个体咨询'),
        ('团体咨询', '团体咨询'),
        ('家庭咨询', '家庭咨询'),
        ('危机干预', '危机干预'),
    ]

    STATUS_CHOICES = [
        ('未开始', '未开始'),
        ('进行中', '进行中'),
        ('已结束', '已结束'),
    ]

    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    id = models.AutoField(primary_key=True)
    order_no = models.CharField(max_length=20, unique=True, verbose_name='订单编号')
    client_name = models.CharField(max_length=50, verbose_name='预约人员姓名')
    client_gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name='性别')
    client_age = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, blank=True, verbose_name='服务类型')
    counseling_keywords = models.CharField(max_length=200, blank=True, verbose_name='咨询关键字')
    appointment_date = models.DateField(blank=True, null=True, verbose_name='预约日期')
    time_slot = models.CharField(max_length=50, blank=True, verbose_name='预约时段')
    submit_time = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='未开始', verbose_name='状态')
    counselor = models.ForeignKey(Counselor, on_delete=models.SET_NULL, blank=True, null=True,
                                  verbose_name='关联咨询师')

    class Meta:
        db_table = 'appointments'
        verbose_name = '预约订单'
        verbose_name_plural = '预约订单'

    def __str__(self):
        return f"{self.order_no} - {self.client_name}"


# 轮播图模块表
class BannerModule(models.Model):
    id = models.AutoField(primary_key=True)
    module_name = models.CharField(max_length=50, verbose_name='模块名称')
    carousel_count = models.IntegerField(default=0, verbose_name='轮播数量')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    pictures = models.JSONField(blank=True, null=True, verbose_name='轮播图片URL数组')

    class Meta:
        db_table = 'banner_modules'
        verbose_name = '轮播图模块'
        verbose_name_plural = '轮播图模块'

    def __str__(self):
        return self.module_name


# 通知表
class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='通知标题')
    content = models.TextField(blank=True, verbose_name='通知内容')
    is_published = models.BooleanField(default=False, verbose_name='发布状态')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知'

    def __str__(self):
        return self.title


# 宣教栏目表
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, verbose_name='栏目名称')
    sort_order = models.IntegerField(default=0, verbose_name='栏目顺序')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'categories'
        verbose_name = '宣教栏目'
        verbose_name_plural = '宣教栏目'

    def __str__(self):
        return self.category_name


# 宣教资讯表
class Article(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='栏目ID')
    title = models.CharField(max_length=200, verbose_name='资讯标题')
    content = models.TextField(blank=True, verbose_name='资讯内容')
    collect_count = models.IntegerField(default=0, verbose_name='收藏人数')
    like_count = models.IntegerField(default=0, verbose_name='点赞人数')
    read_count = models.IntegerField(default=0, verbose_name='阅读人数')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    video = models.URLField(max_length=500, blank=True, verbose_name='视频URL')

    class Meta:
        db_table = 'articles'
        verbose_name = '宣教资讯'
        verbose_name_plural = '宣教资讯'

    def __str__(self):
        return self.title


# 转介单位表
class ReferralUnit(models.Model):
    id = models.AutoField(primary_key=True)
    unit_name = models.CharField(max_length=100, verbose_name='单位名称')
    address = models.CharField(max_length=200, blank=True, verbose_name='地址')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'referral_units'
        verbose_name = '转介单位'
        verbose_name_plural = '转介单位'

    def __str__(self):
        return self.unit_name


# 学生转介表
class StudentReferral(models.Model):
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=50, verbose_name='学生姓名')
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name='性别')
    school = models.CharField(max_length=100, blank=True, verbose_name='学校')
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')
    class_name = models.CharField(max_length=20, blank=True, verbose_name='班级')
    referral_unit = models.ForeignKey(ReferralUnit, on_delete=models.SET_NULL, blank=True, null=True,
                                      verbose_name='转介单位')
    referral_reason = models.TextField(blank=True, verbose_name='转介原因')
    referral_date = models.DateField(blank=True, null=True, verbose_name='转介时间')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'student_referrals'
        verbose_name = '学生转介'
        verbose_name_plural = '学生转介'

    def __str__(self):
        return self.student_name


# 负面事件表
class NegativeEvent(models.Model):
    id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=50, verbose_name='学生姓名')
    organization = models.CharField(max_length=100, blank=True, verbose_name='机构名称')
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')
    class_name = models.CharField(max_length=20, blank=True, verbose_name='班级')
    event_details = models.TextField(blank=True, verbose_name='事件详情')
    event_date = models.DateField(blank=True, null=True, verbose_name='事件日期')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    disabled = models.BooleanField(default=False, verbose_name='是否禁用')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'negative_events'
        verbose_name = '负面事件'
        verbose_name_plural = '负面事件'

    def __str__(self):
        return self.student_name


# 访谈评估表
class InterviewAssessment(models.Model):
    INTERVIEW_STATUS_CHOICES = [
        ('待处理', '待处理'),
        ('进行中', '进行中'),
        ('已完成', '已完成'),
    ]

    id = models.AutoField(primary_key=True)
    organization = models.CharField(max_length=100, blank=True, verbose_name='所属机构')
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')
    class_name = models.CharField(max_length=20, blank=True, verbose_name='班级')
    student_name = models.CharField(max_length=50, verbose_name='姓名')
    interview_count = models.IntegerField(default=1, verbose_name='访谈次数')
    interview_status = models.CharField(max_length=10, choices=INTERVIEW_STATUS_CHOICES, default='待处理',
                                        verbose_name='访谈状态')
    interview_type = models.CharField(max_length=50, blank=True, verbose_name='类型')
    doctor_assessment = models.CharField(max_length=50, blank=True, verbose_name='医生评定')
    follow_up_plan = models.CharField(max_length=50, blank=True, verbose_name='后续计划')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        db_table = 'interview_assessments'
        verbose_name = '访谈评估'
        verbose_name_plural = '访谈评估'

    def __str__(self):
        return f"{self.student_name} - {self.interview_status}"


# 管理员信息表
class AdminUser(models.Model):
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name='性别')
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='邮箱地址')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    password = models.CharField(max_length=128, verbose_name='加密密码')

    class Meta:
        db_table = 'admin_users'  # 修改表名避免冲突
        verbose_name = '管理员'
        verbose_name_plural = '管理员'

    def __str__(self):
        return self.username


# 排班表
class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, verbose_name='咨询师')
    work_date = models.DateField(verbose_name='工作日期')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'schedules'
        verbose_name = '排班'
        verbose_name_plural = '排班'

    def __str__(self):
        return f"{self.counselor.name} - {self.work_date}"


# 停诊表
class Cancellation(models.Model):
    id = models.AutoField(primary_key=True)
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, verbose_name='咨询师')
    cancel_start = models.DateTimeField(verbose_name='停诊开始时间')
    cancel_end = models.DateTimeField(verbose_name='停诊结束时间')
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'cancellations'
        verbose_name = '停诊'
        verbose_name_plural = '停诊'

    def __str__(self):
        return f"{self.counselor.name} - {self.cancel_start}"