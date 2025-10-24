from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CounselorAdmin(admin.ModelAdmin):  # 改为继承admin.ModelAdmin而不是UserAdmin
    list_display = ('username', 'name', 'gender', 'phone', 'email', 'organization', 'status')
    list_filter = ('gender', 'status')
    search_fields = ('name', 'phone', 'username')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('name', 'gender', 'phone', 'email', 'organization')}),
        ('专业信息', {'fields': ('expertise_tags', 'status')}),
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'client_name', 'service_type', 'appointment_date', 'status', 'counselor')
    list_filter = ('service_type', 'status', 'appointment_date')
    search_fields = ('client_name', 'order_no')

@admin.register(BannerModule)
class BannerModuleAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'carousel_count', 'created_by', 'created_time')
    search_fields = ('module_name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_by', 'created_time')
    list_filter = ('is_published',)
    search_fields = ('title',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'sort_order', 'created_by', 'created_time')
    search_fields = ('category_name',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'read_count', 'like_count', 'created_time')
    list_filter = ('category',)
    search_fields = ('title',)

@admin.register(ReferralUnit)
class ReferralUnitAdmin(admin.ModelAdmin):
    list_display = ('unit_name', 'contact_phone', 'address', 'created_by')
    search_fields = ('unit_name',)

@admin.register(StudentReferral)
class StudentReferralAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'gender', 'school', 'referral_unit', 'referral_date')
    list_filter = ('gender', 'referral_date')
    search_fields = ('student_name',)

@admin.register(NegativeEvent)
class NegativeEventAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'organization', 'event_date', 'disabled', 'created_time')
    list_filter = ('disabled', 'event_date')
    search_fields = ('student_name',)

@admin.register(InterviewAssessment)
class InterviewAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'organization', 'interview_status', 'interview_count', 'created_time')
    list_filter = ('interview_status', 'organization')
    search_fields = ('student_name',)

@admin.register(AdminUser)  # 修改为AdminUser
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'gender', 'email', 'phone')
    list_filter = ('gender',)
    search_fields = ('username',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('counselor', 'work_date', 'start_time', 'end_time', 'created_by')
    list_filter = ('work_date', 'counselor')
    search_fields = ('counselor__name',)

@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ('counselor', 'cancel_start', 'cancel_end', 'created_by')
    list_filter = ('cancel_start', 'counselor')
    search_fields = ('counselor__name',)

# 注册咨询师模型
admin.site.register(Counselor, CounselorAdmin)