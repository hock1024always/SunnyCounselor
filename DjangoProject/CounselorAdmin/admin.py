from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Counselor,
    Appointment,
    BannerModule,
    Notification,
    Category,
    Article,
    ReferralUnit,
    StudentReferral,
    NegativeEvent,
    InterviewAssessment,
    AdminUser,
    Schedule,
    Cancellation,
    VerificationCode,
    Captcha,
    AdminAuthToken,
)


@admin.register(Counselor)
class CounselorAdmin(BaseUserAdmin):
    """咨询师管理"""
    list_display = ['id', 'username', 'name', 'gender', 'phone', 'email', 'organization', 'status']
    list_filter = ['gender', 'status']
    search_fields = ['username', 'name', 'phone', 'email']
    
    # 重写 fieldsets，因为 Counselor 继承自 AbstractBaseUser，没有 groups 和 user_permissions
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('name', 'gender', 'phone', 'email')}),
        ('咨询师信息', {'fields': ('organization', 'expertise_tags', 'status')}),
        ('重要日期', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('个人信息', {'fields': ('name', 'gender', 'phone', 'email')}),
        ('咨询师信息', {'fields': ('organization', 'expertise_tags', 'status')}),
    )
    
    # 移除 BaseUserAdmin 默认的 filter_horizontal，因为 Counselor 没有这些字段
    filter_horizontal = []


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """预约订单管理"""
    list_display = ['id', 'order_no', 'client_name', 'client_gender', 'client_age', 'service_type', 'appointment_date', 'status', 'counselor']
    list_filter = ['service_type', 'status', 'client_gender', 'appointment_date']
    search_fields = ['order_no', 'client_name', 'counseling_keywords']
    readonly_fields = ['submit_time']
    autocomplete_fields = ['counselor']


@admin.register(BannerModule)
class BannerModuleAdmin(admin.ModelAdmin):
    """轮播图模块管理"""
    list_display = ['id', 'module_name', 'carousel_count', 'created_by', 'created_time']
    list_filter = ['created_time']
    search_fields = ['module_name', 'created_by']
    readonly_fields = ['created_time']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """通知管理"""
    list_display = ['id', 'title', 'is_published', 'created_by', 'created_time']
    list_filter = ['is_published', 'created_time']
    search_fields = ['title', 'content', 'created_by']
    readonly_fields = ['created_time']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """宣教栏目管理"""
    list_display = ['id', 'category_name', 'sort_order', 'created_by', 'created_time']
    list_filter = ['created_time']
    search_fields = ['category_name', 'created_by']
    readonly_fields = ['created_time']
    ordering = ['sort_order', 'created_time']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """宣教资讯管理"""
    list_display = ['id', 'title', 'category', 'collect_count', 'like_count', 'read_count', 'created_by', 'created_time']
    list_filter = ['category', 'created_time']
    search_fields = ['title', 'content', 'created_by']
    readonly_fields = ['created_time']
    autocomplete_fields = ['category']


@admin.register(ReferralUnit)
class ReferralUnitAdmin(admin.ModelAdmin):
    """转介单位管理"""
    list_display = ['id', 'unit_name', 'address', 'contact_phone', 'created_by', 'created_time']
    list_filter = ['created_time']
    search_fields = ['unit_name', 'address', 'contact_phone', 'created_by']
    readonly_fields = ['created_time']


@admin.register(StudentReferral)
class StudentReferralAdmin(admin.ModelAdmin):
    """学生转介管理"""
    list_display = ['id', 'student_name', 'gender', 'school', 'grade', 'class_name', 'referral_unit', 'referral_date', 'created_by', 'created_time']
    list_filter = ['gender', 'referral_date', 'created_time']
    search_fields = ['student_name', 'school', 'grade', 'class_name']
    readonly_fields = ['created_time']
    autocomplete_fields = ['referral_unit']


@admin.register(NegativeEvent)
class NegativeEventAdmin(admin.ModelAdmin):
    """负面事件管理"""
    list_display = ['id', 'student_name', 'organization', 'grade', 'class_name', 'event_date', 'disabled', 'created_by', 'created_time']
    list_filter = ['disabled', 'event_date', 'created_time']
    search_fields = ['student_name', 'organization', 'grade', 'class_name']
    readonly_fields = ['created_time']


@admin.register(InterviewAssessment)
class InterviewAssessmentAdmin(admin.ModelAdmin):
    """访谈评估管理"""
    list_display = ['id', 'student_name', 'organization', 'grade', 'class_name', 'interview_count', 'interview_status', 'interview_type', 'created_time']
    list_filter = ['interview_status', 'interview_type', 'created_time']
    search_fields = ['student_name', 'organization', 'grade', 'class_name', 'doctor_assessment', 'follow_up_plan']
    readonly_fields = ['created_time']


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    """管理员用户管理"""
    list_display = ['id', 'username', 'gender', 'email', 'phone']
    list_filter = ['gender']
    search_fields = ['username', 'email', 'phone']
    readonly_fields = []


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """排班管理"""
    list_display = ['id', 'counselor', 'work_date', 'start_time', 'end_time', 'created_by', 'created_time']
    list_filter = ['work_date', 'created_time']
    search_fields = ['created_by']
    readonly_fields = ['created_time']
    autocomplete_fields = ['counselor']


@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    """停诊管理"""
    list_display = ['id', 'counselor', 'cancel_start', 'cancel_end', 'created_by', 'created_time']
    list_filter = ['cancel_start', 'cancel_end', 'created_time']
    search_fields = ['created_by']
    readonly_fields = ['created_time']
    autocomplete_fields = ['counselor']


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """验证码管理"""
    list_display = ['id', 'username', 'email', 'phone', 'code', 'purpose', 'is_verified', 'created_time', 'expires_at']
    list_filter = ['purpose', 'is_verified', 'created_time']
    search_fields = ['username', 'email', 'phone', 'code']
    readonly_fields = ['created_time']


@admin.register(Captcha)
class CaptchaAdmin(admin.ModelAdmin):
    """图形验证码管理"""
    list_display = ['id', 'key', 'text', 'is_used', 'created_time', 'expires_at']
    list_filter = ['is_used', 'created_time']
    search_fields = ['key', 'text']
    readonly_fields = ['created_time']


@admin.register(AdminAuthToken)
class AdminAuthTokenAdmin(admin.ModelAdmin):
    """管理员Token管理"""
    list_display = ['id', 'user', 'token', 'is_active', 'created_time', 'expires_at']
    list_filter = ['is_active', 'created_time']
    search_fields = ['token', 'user__username']
    readonly_fields = ['created_time']
    autocomplete_fields = ['user']