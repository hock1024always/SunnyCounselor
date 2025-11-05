from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User  # 导入Django的User


# 咨询师管理器
class CounselorManager(BaseUserManager):
    """
    咨询师管理类，继承自BaseUserManager，用于管理咨询师用户的创建和认证
    """

    def create_user(self, username, password=None, **extra_fields):
        """
        创建普通用户方法
        参数:
            username (str): 用户名
            password (str, optional): 用户密码，默认为None
            **extra_fields: 其他额外字段
        返回:
            User: 创建的普通用户实例
        异常:
            ValueError: 当用户名为空时抛出
        """
        if not username:
            raise ValueError('用户名必须设置')
        user = self.model(username=username, **extra_fields)  # 创建用户模型实例
        user.set_password(password)  # 设置用户密码
        user.save(using=self._db)
        return user  # 保存用户到数据库

    # 返回创建的用户实例
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)

        """
        创建超级用户方法

        参数:
            username (str): 用户名
            password (str, optional): 用户密码，默认为None
            **extra_fields: 其他额外字段

        返回:
            User: 创建的超级用户实例
        """
        extra_fields.setdefault('is_superuser', True)  # 设置用户为管理员
        return self.create_user(username, password, **extra_fields)  # 设置用户为超级用户


# 调用create_user方法创建用户

# 咨询师表
class Counselor(AbstractBaseUser):
    """
    咨询师模型类，继承自AbstractBaseUser，用于存储咨询师的基本信息
    """
    # 性别选项
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    # 状态选项
    STATUS_CHOICES = [
        ('启用', '启用'),
        ('停用', '停用'),
    ]

    # 咨询师ID，自增主键
    id = models.AutoField(primary_key=True)
    # 咨询师姓名 (NOT NULL)
    name = models.CharField(max_length=50, null=False, blank=False, verbose_name='咨询师姓名')
    # 系统用户昵称，必须唯一 (NOT NULL)
    username = models.CharField(max_length=50, unique=True, null=False, blank=False, verbose_name='系统用户昵称')
    # 性别，从GENDER_CHOICES中选择 (NOT NULL)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, null=False, blank=False, verbose_name='性别')
    # 联系电话 (NOT NULL)
    phone = models.CharField(max_length=20, null=False, blank=False, verbose_name='联系电话')
    # 邮箱地址，可以为空
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='邮箱地址')
    # 所属机构，可以为空
    organization = models.CharField(max_length=100, blank=True, verbose_name='所属机构')
    # 擅长标签，使用JSON格式存储，可以为空
    expertise_tags = models.JSONField(blank=True, null=True, verbose_name='擅长标签')
    # 状态，默认为'启用'
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='启用', verbose_name='状态')

    # 使用自定义的CounselorManager
    objects = CounselorManager()

    # 指定用户名字段为username
    USERNAME_FIELD = 'username'
    # 指定创建用户时必须填写的字段
    REQUIRED_FIELDS = ['name', 'gender', 'phone']

    class Meta:
        # 指定数据库表名
        db_table = 'counselors'
        # 指定模型的中文单数形式
        verbose_name = '咨询师'
        # 指定模型的中文复数形式
        verbose_name_plural = '咨询师'

    def __str__(self):
        # 返回咨询师的姓名作为字符串表示
        return self.name


# 预约订单表
class Appointment(models.Model):
    """
    预约订单模型类，用于存储和管理心理咨询预约相关信息
    """
    # 服务类型选项，包含个体咨询、团体咨询、家庭咨询和危机干预
    SERVICE_TYPE_CHOICES = [
        ('个体咨询', '个体咨询'),
        ('团体咨询', '团体咨询'),
        ('家庭咨询', '家庭咨询'),
        ('危机干预', '危机干预'),
    ]

    # 预约状态选项，包含未开始、进行中和已完成
    STATUS_CHOICES = [
        ('未开始', '未开始'),
        ('进行中', '进行中'),
        ('已完成', '已完成'),
    ]

    # 性别选项，包含男和女
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    # 主键ID，自增
    id = models.AutoField(primary_key=True)
    # 订单编号，唯一标识符 (UNIQUE NOT NULL)
    order_no = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name='订单编号')
    # 预约人员姓名 (NOT NULL)
    client_name = models.CharField(max_length=50, null=False, blank=False, verbose_name='预约人员姓名')
    # 性别，使用GENDER_CHOICES选项 (NOT NULL)
    client_gender = models.CharField(max_length=2, choices=GENDER_CHOICES, null=False, blank=False, verbose_name='性别')
    # 年龄，允许为空
    client_age = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    # 服务类型，使用SERVICE_TYPE_CHOICES选项，允许为空
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, blank=True, verbose_name='服务类型')
    # 咨询关键字，描述咨询内容的关键词，允许为空
    counseling_keywords = models.CharField(max_length=200, blank=True, verbose_name='咨询关键字')
    # 预约日期，允许为空
    appointment_date = models.DateField(blank=True, null=True, verbose_name='预约日期')
    # 预约时段，如上午、下午等，允许为空
    time_slot = models.CharField(max_length=50, blank=True, verbose_name='预约时段')
    # 提交时间，自动记录创建时间
    submit_time = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    # 结束时间，允许为空
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    # 预约状态，使用STATUS_CHOICES选项，默认为'未开始'
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='未开始', verbose_name='状态')
    # 关联的咨询师，使用外键关联，允许为空
    counselor = models.ForeignKey(Counselor, on_delete=models.SET_NULL, blank=True, null=True,
                                  verbose_name='关联咨询师')

    class Meta:
        # 指定数据库表名为'appointments'
        db_table = 'appointments'
        # 设置模型的可读名称为'预约订单'
        verbose_name = '预约订单'
        # 设置复数形式的可读名称为'预约订单'
        verbose_name_plural = '预约订单'

    def __str__(self):
        """
        返回预约订单的字符串表示，格式为"订单编号 - 预约人员姓名"
        """
        return f"{self.order_no} - {self.client_name}"


# 轮播图模块表
# 数据库文档中的 module_name 在接口中简化为 module
# carousel_count 在接口中简化为 count
# pictures 字段在接口中对应 images
class BannerModule(models.Model):
    """
    轮播图模块模型类
    用于存储和管理网站轮播图模块的相关信息
    """
    id = models.AutoField(primary_key=True)  # 自增主键ID
    module_name = models.CharField(max_length=50, null=False, blank=False, verbose_name='模块名称')  # 模块名称，最大长度50字符 (NOT NULL)
    carousel_count = models.IntegerField(default=0, verbose_name='轮播数量')  # 轮播图数量，默认为0
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 创建人，允许为空
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间，自动设置为记录创建时的时间
    pictures = models.JSONField(blank=True, null=True, verbose_name='轮播图片URL数组')  # 轮播图片URL数组，使用JSON格式存储，允许为空

    class Meta:
        db_table = 'banner_modules'  # 指定数据库表名为'banner_modules'
        verbose_name = '轮播图模块'  # 在Django admin中显示的名称
        verbose_name_plural = '轮播图模块'  # 复数形式的名称，与单数相同

    def __str__(self):
        """
        返回对象的字符串表示形式
        :return: 模块名称
        """
        return self.module_name


# 通知表
class Notification(models.Model):
    """
    通知模型类，用于存储和管理系统通知信息
    继承自Django的models.Model，表示这是一个数据库模型
    """
    id = models.AutoField(primary_key=True)  # 自增主键，唯一标识每条通知记录
    title = models.CharField(max_length=200, null=False, blank=False, verbose_name='通知标题')  # 通知标题，最大长度200字符 (NOT NULL)
    content = models.TextField(blank=True, verbose_name='通知内容')  # 通知内容，可为空，使用TextField存储长文本
    is_published = models.BooleanField(default=False, verbose_name='发布状态')  # 发布状态，默认为未发布(False)
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 创建人，最大长度50字符，可为空
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间，自动记录对象创建时的时间

    class Meta:
        db_table = 'notifications'  # 指定数据库表名为'notifications'
        verbose_name = '通知'  # 指定模型在Django admin中的显示名称
        verbose_name_plural = '通知'  # 指定模型的复数形式名称

    def __str__(self):
        """
        返回对象的字符串表示形式
        这里返回通知的标题，方便在Django admin等界面显示
        """
        return self.title


# 宣教栏目表
class Category(models.Model):
    """
    宣教栏目模型类
    用于存储和管理宣教栏目的相关信息
    """
    id = models.AutoField(primary_key=True)  # 自增主键ID
    category_name = models.CharField(max_length=50, verbose_name='栏目名称', null=False,
                                     blank=False)  # 修正：添加 NOT NULL 约束
    sort_order = models.IntegerField(default=0, verbose_name='栏目顺序')  # 栏目顺序，默认值为0
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 创建人，允许为空
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间，自动设置为当前时间

    class Meta:
        db_table = 'categories'  # 指定数据库表名为'categories'
        verbose_name = '宣教栏目'  # 在后台管理界面显示的名称
        verbose_name_plural = '宣教栏目'  # 在后台管理界面显示的复数名称
        ordering = ['sort_order', 'created_time']

    def __str__(self):
        """
        返回栏目的名称字符串表示
        :return: 栏目名称
        """
        return self.category_name


# 宣教资讯表
class Article(models.Model):
    """
    宣教资讯模型类，用于存储和管理宣教相关的资讯信息
    继承自Django的models.Model，表示这是一个数据库模型
    """
    id = models.AutoField(primary_key=True)  # 自增主键ID
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='栏目ID')  # 外键关联栏目，级联删除
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='栏目ID',
        null=False,  # 修正：添加 NOT NULL 约束
        blank=False,  # 修正：添加 NOT NULL 约束
        related_name='articles'  # 新增：添加反向关系名称
    )
    title = models.CharField(max_length=200, verbose_name='资讯标题', null=False, blank=False)  # 修正：添加 NOT NULL 约束
    content = models.TextField(blank=True, verbose_name='资讯内容')  # 文本类型的内容字段，允许为空
    collect_count = models.IntegerField(default=0, verbose_name='收藏人数')  # 整数类型的收藏人数，默认值为0
    like_count = models.IntegerField(default=0, verbose_name='点赞人数')  # 整数类型的点赞人数，默认值为0
    read_count = models.IntegerField(default=0, verbose_name='阅读人数')  # 整数类型的阅读人数，默认值为0
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 字符串类型的创建人字段，允许为空
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 自动记录创建时间
    video = models.URLField(max_length=500, blank=True, verbose_name='视频URL')  # URL类型的视频字段，允许为空（用于外部链接）
    video_path = models.CharField(max_length=255, blank=True, verbose_name='视频文件路径')  # 视频文件路径字段，存储相对路径，允许为空（用于上传的视频文件）
    resource = models.CharField(max_length=200, blank=True, verbose_name='资源')  # 资源字段
    type = models.CharField(max_length=50, blank=True, verbose_name='类型')  # 类型字段

    class Meta:
        """
        元数据类，用于配置模型的数据库表名和显示名称
        """
        db_table = 'articles'  # 指定数据库表名为'articles'
        verbose_name = '宣教资讯'  # 模型的单数形式名称
        verbose_name_plural = '宣教资讯'  # 模型的复数形式名称

    def __str__(self):
        """
        返回模型的字符串表示，通常用于后台显示
        这里返回资讯的标题
        """
        return self.title


# 转介单位表
class ReferralUnit(models.Model):
    """
    转介单位模型类，用于存储和管理转介单位的信息
    包括单位名称、地址、联系电话、创建人和创建时间等字段
    """
    id = models.AutoField(primary_key=True)  # 自增主键
    unit_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='单位名称')  # 单位名称，最大长度100字符 (NOT NULL)
    address = models.CharField(max_length=200, blank=True, verbose_name='地址')  # 地址，最大长度200字符，可为空
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')  # 联系电话，最大长度20字符，可为空
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 创建人，最大长度50字符，可为空
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间，自动设置为记录创建时的时间

    class Meta:
        db_table = 'referral_units'  # 指定数据库表名为'referral_units'
        verbose_name = '转介单位'  # 指定在管理界面中显示的名称
        verbose_name_plural = '转介单位'  # 指定在管理界面中显示的复数名称

    def __str__(self):
        return self.unit_name  # 返回单位的名称字符串表示


# 学生转介表
class StudentReferral(models.Model):
    """
    学生转介模型类，用于存储和管理学生转介的相关信息。
    包含学生的基本信息、转介单位、转介原因等字段。
    """
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    id = models.AutoField(primary_key=True)  # 主键ID，自增
    student_name = models.CharField(max_length=50, null=False, blank=False, verbose_name='学生姓名')  # 学生姓名字段 (NOT NULL)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, null=False, blank=False, verbose_name='性别')  # 性别字段，使用预定义的性别选项 (NOT NULL)
    school = models.CharField(max_length=100, blank=True, verbose_name='学校')  # 学校字段，允许为空
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')  # 年级字段，允许为空
    class_name = models.CharField(max_length=20, blank=True, verbose_name='班级')  # 班级字段，允许为空
    referral_unit = models.ForeignKey(ReferralUnit, on_delete=models.SET_NULL, blank=True, null=True,
                                      verbose_name='转介单位')  # 转介单位字段，外键关联，允许为空
    referral_reason = models.TextField(blank=True, verbose_name='转介原因')  # 转介原因字段，允许为空
    referral_date = models.DateField(blank=True, null=True, verbose_name='转介时间')  # 转介时间字段，允许为空
    image_path = models.CharField(max_length=255, blank=True, verbose_name='图片路径')  # 图片路径字段，存储相对路径，允许为空
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 创建人字段，允许为空
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间字段，自动记录创建时间

    class Meta:
        db_table = 'student_referrals'  # 指定数据库表名
        verbose_name = '学生转介'  # 指定模型的易读名称
        verbose_name_plural = '学生转介'  # 指定模型的复数形式名称

    def __str__(self):
        return self.student_name  # 返回学生姓名作为对象的字符串表示


# 负面事件表
class NegativeEvent(models.Model):
    """
    负面事件模型类，用于存储和管理学生的负面事件信息。
    包含学生基本信息、事件详情、创建时间等字段。
    """
    id = models.AutoField(primary_key=True)  # 自增主键ID
    student_name = models.CharField(max_length=50, null=False, blank=False, verbose_name='学生姓名')  # 学生姓名字段，最大长度50 (NOT NULL)
    organization = models.CharField(max_length=100, blank=True, verbose_name='机构名称')  # 机构名称字段，最大长度100，可为空
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')  # 年级字段，最大长度20，可为空
    class_name = models.CharField(max_length=20, blank=True, verbose_name='班级')  # 班级字段，最大长度20，可为空
    event_details = models.TextField(blank=True, verbose_name='事件详情')  # 事件详情字段，使用TextField类型，可为空
    event_date = models.DateField(blank=True, null=True, verbose_name='事件日期')  # 事件日期字段，可为空，可为null
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 创建人字段，最大长度50，可为空
    disabled = models.BooleanField(default=False, verbose_name='是否禁用')  # 是否禁用字段，默认为False
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间字段，自动设置为创建时的时间

    class Meta:
        db_table = 'negative_events'  # 指定数据库表名为'negative_events'
        verbose_name = '负面事件'  # 指定模型的单数形式名称
        verbose_name_plural = '负面事件'  # 指定模型的复数形式名称

    def __str__(self):
        return self.student_name  # 返回学生名称作为对象的字符串表示


# 访谈评估表
class InterviewAssessment(models.Model):
    """
    访谈评估模型类，用于存储和管理学生访谈评估的相关信息。
    包含学生的基本信息、访谈状态、医生评定等内容。
    """
    # 访谈状态选项，包含待处理、进行中和已完成三种状态
    INTERVIEW_STATUS_CHOICES = [
        ('待处理', '待处理'),
        ('进行中', '进行中'),
        ('已完成', '已完成'),
    ]

    # 主键ID，自增
    id = models.AutoField(primary_key=True)
    # 所属机构，字符串类型，允许为空
    organization = models.CharField(max_length=100, blank=True, verbose_name='所属机构')
    # 年级，字符串类型，允许为空
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')
    # 班级，字符串类型，允许为空
    class_name = models.CharField(max_length=20, blank=True, verbose_name='班级')
    # 学生姓名，字符串类型，必填字段 (NOT NULL)
    student_name = models.CharField(max_length=50, null=False, blank=False, verbose_name='姓名')
    # 访谈次数，整数类型，默认值为1
    interview_count = models.IntegerField(default=1, verbose_name='访谈次数')
    # 访谈状态，字符串类型，从预定义选项中选择，默认为'待处理'
    interview_status = models.CharField(max_length=10, choices=INTERVIEW_STATUS_CHOICES, default='待处理',
                                        verbose_name='访谈状态')
    # 访谈类型，字符串类型，允许为空
    interview_type = models.CharField(max_length=50, blank=True, verbose_name='类型')
    # 医生评定，字符串类型，允许为空
    doctor_assessment = models.CharField(max_length=50, blank=True, verbose_name='医生评定')
    # 后续计划，字符串类型，允许为空
    follow_up_plan = models.CharField(max_length=50, blank=True, verbose_name='后续计划')
    # 创建时间，自动设置为记录创建时的时间
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        # 指定数据库表名为'interview_assessments'
        db_table = 'interview_assessments'
        # 设置模型的中文单数形式名称
        verbose_name = '访谈评估'
        # 设置模型的中文复数形式名称
        verbose_name_plural = '访谈评估'

    def __str__(self):
        # 返回学生姓名和访谈状态的字符串表示，用于模型的字符串显示
        return f"{self.student_name} - {self.interview_status}"


class AdminUser(models.Model):
    """
    管理员信息表 - 独立模型版本
    数据库表: admin_users
    主键类型: BIGINT (Django的AutoField会根据数据库自动处理)
    """
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    # 严格按照数据库设计定义字段
    id = models.BigAutoField(primary_key=True, verbose_name='用户唯一ID')  # BIGINT AUTO_INCREMENT
    username = models.CharField(max_length=50, unique=True, null=False, blank=False, verbose_name='用户名')  # 用户名，唯一 (NOT NULL)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, null=False, blank=False, verbose_name='性别')  # 性别 (NOT NULL)
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='邮箱地址')  # 邮箱地址 (NULL)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')  # 手机号 (NULL)
    password = models.CharField(max_length=128, null=False, blank=False, verbose_name='加密密码')  # 加密密码 (NOT NULL，密码必须设置)

    class Meta:
        db_table = 'admin_users'
        verbose_name = '管理员'
        verbose_name_plural = '管理员'

    def __str__(self):
        return self.username


class VerificationCode(models.Model):
    """
    通用验证码（用于邮箱/手机注册验证）
    """
    PURPOSE_CHOICES = [
        ('register', 'register'),
        ('login', 'login'),
        ('captcha', 'captcha'),
    ]
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, blank=True, verbose_name='用户名')
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='邮箱地址')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    code = models.CharField(max_length=12, verbose_name='验证码')
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='register', verbose_name='用途')
    is_verified = models.BooleanField(default=False, verbose_name='是否已验证')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')

    class Meta:
        db_table = 'verification_codes'
        indexes = [
            models.Index(fields=['email', 'phone', 'username', 'purpose']),
        ]


class Captcha(models.Model):
    """
    图形验证码存储（文本+Base64图片，可扩展为其他表现形式）
    """
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=64, unique=True, verbose_name='验证码键')
    text = models.CharField(max_length=8, verbose_name='验证码文本')
    image_base64 = models.TextField(blank=True, verbose_name='图片Base64')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')

    class Meta:
        db_table = 'captchas'
        indexes = [
            models.Index(fields=['key']),
        ]


class AdminAuthToken(models.Model):
    """
    管理员登录Token（自定义加盐token）
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name='tokens', verbose_name='管理员')
    token = models.CharField(max_length=128, unique=True, verbose_name='Token')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')

    class Meta:
        db_table = 'admin_auth_tokens'
        indexes = [
            models.Index(fields=['token']),
        ]


# 排班表
class Schedule(models.Model):
    """
    排班模型类，用于存储和管理咨询师的工作排班信息。

    属性:
        id: 自增主键，唯一标识每条排班记录
        counselor: 外键，关联到咨询师模型，表示该排班的咨询师
        work_date: 日期类型，表示咨询师的工作日期
        start_time: 时间类型，表示当天的开始工作时间
        end_time: 时间类型，表示当天的结束工作时间
        created_by: 字符串类型，记录创建人信息
        created_time: 日期时间类型，记录记录创建时间，自动设置为创建时的时间戳
    """
    id = models.AutoField(primary_key=True)  # 自增主键，唯一标识每条排班记录
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, null=False, blank=False, verbose_name='咨询师')  # 关联到咨询师模型，级联删除 (NOT NULL)
    work_date = models.DateField(null=False, blank=False, verbose_name='工作日期')  # 咨询师的工作日期 (NOT NULL)
    start_time = models.TimeField(null=False, blank=False, verbose_name='开始时间')  # 当天的开始工作时间 (NOT NULL)
    end_time = models.TimeField(null=False, blank=False, verbose_name='结束时间')  # 当天的结束工作时间 (NOT NULL)
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 创建人信息，允许为空
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间，自动设置为记录创建时的时间戳

    class Meta:
        db_table = 'schedules'  # 指定数据库表名为'schedules'
        verbose_name = '排班'  # 指定模型在管理界面中的显示名称
        verbose_name_plural = '排班'  # 指定模型在管理界面中的复数显示名称

    def __str__(self):
        """
        返回模型的字符串表示形式，用于在管理界面等地方显示。
        返回格式:
            咨询师姓名 - 工作日期
        """
        return f"{self.counselor.name} - {self.work_date}"


# 停诊表
class Cancellation(models.Model):
    """
    停诊模型类
    用于记录咨询师的停诊信息
    """
    id = models.AutoField(primary_key=True)  # 主键ID，自增
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, null=False, blank=False, verbose_name='咨询师')  # 关联咨询师，外键 (NOT NULL)
    cancel_start = models.DateTimeField(null=False, blank=False, verbose_name='停诊开始时间')  # 停诊开始时间 (NOT NULL)
    cancel_end = models.DateTimeField(null=False, blank=False, verbose_name='停诊结束时间')  # 停诊结束时间 (NOT NULL)
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')  # 创建人，可为空
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间，自动记录

    class Meta:
        db_table = 'cancellations'  # 指定数据库表名
        verbose_name = '停诊'  # 模型的可读名称
        verbose_name_plural = '停诊'  # 模型的复数可读名称

    def __str__(self):
        """
        返回模型的字符串表示
        格式为：咨询师姓名 - 停诊开始时间
        """
        return f"{self.counselor.name} - {self.cancel_start}"
# Create your models here.
