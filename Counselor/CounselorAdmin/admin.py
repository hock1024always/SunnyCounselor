from django.contrib import admin
from .models import (
    Student, Interview, NegativeEvent, ReferralUnit, ReferralHistory,
    EducationCategory, EducationContent, Notification, Banner,
    CounselorSchedule, ConsultationOrder
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'age', 'school', 'grade', 'class_name', 'created_at']
    list_filter = ['gender', 'school', 'grade', 'class_name']
    search_fields = ['name', 'student_id', 'school']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'counselor', 'interview_date', 'status', 'assessment_level', 'is_manual_end']
    list_filter = ['status', 'assessment_level', 'interview_date', 'counselor']
    search_fields = ['student__name', 'counselor__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'interview_date'
    list_per_page = 20


@admin.register(NegativeEvent)
class NegativeEventAdmin(admin.ModelAdmin):
    list_display = ['student', 'event_type', 'severity', 'occurred_at', 'is_resolved']
    list_filter = ['event_type', 'severity', 'is_resolved', 'occurred_at']
    search_fields = ['student__name', 'reported_by']
    readonly_fields = ['created_at']
    date_hierarchy = 'occurred_at'
    list_per_page = 20


@admin.register(ReferralUnit)
class ReferralUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit_type', 'contact_person', 'phone', 'is_active']
    list_filter = ['unit_type', 'is_active']
    search_fields = ['name', 'contact_person']
    readonly_fields = ['created_at']
    list_per_page = 20


@admin.register(ReferralHistory)
class ReferralHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'referral_unit', 'referral_date']
    list_filter = ['referral_date', 'referral_unit']
    search_fields = ['student__name', 'referral_unit__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'referral_date'
    list_per_page = 20


@admin.register(EducationCategory)
class EducationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    readonly_fields = ['created_at']
    list_per_page = 20


@admin.register(EducationContent)
class EducationContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'view_count', 'is_published', 'published_at']
    list_filter = ['category', 'content_type', 'is_published']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at', 'view_count']
    date_hierarchy = 'published_at'
    list_per_page = 20


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'status', 'published_at']
    list_filter = ['notification_type', 'status']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'published_at'
    list_per_page = 20


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'order', 'is_active', 'start_date', 'end_date']
    list_filter = ['position', 'is_active']
    search_fields = ['title']
    readonly_fields = ['created_at']
    list_per_page = 20


@admin.register(CounselorSchedule)
class CounselorScheduleAdmin(admin.ModelAdmin):
    list_display = ['counselor', 'date', 'start_time', 'end_time', 'is_available', 'max_appointments']
    list_filter = ['date', 'is_available', 'counselor']
    search_fields = ['counselor__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    list_per_page = 20


@admin.register(ConsultationOrder)
class ConsultationOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'consultation', 'payment_status', 'payment_amount', 'paid_at']
    list_filter = ['payment_status', 'paid_at']
    search_fields = ['order_number', 'consultation__client__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'paid_at'
    list_per_page = 20