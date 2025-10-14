from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Counselor, Client, Consultation, Schedule, Review


# 在Django管理界面中注册Counselor模型，并自定义管理界面配置
@admin.register(Counselor)
class CounselorAdmin(admin.ModelAdmin):
    # 在列表中显示的字段
    list_display = ['name', 'gender', 'age', 'phone', 'is_active', 'created_at']
    # 用于过滤的字段
    list_filter = ['gender', 'is_active', 'created_at']
    # 用于搜索的字段
    search_fields = ['name', 'phone', 'email']
    # 只读字段，不可编辑
    readonly_fields = ['created_at', 'updated_at']
    # 空的filter_horizontal配置，表示不使用多选过滤器
    filter_horizontal = []

    # 定义管理界面的字段分组
    fieldsets = (
        # 基本信息
        ('基本信息', {
            'fields': ('user', 'name', 'gender', 'age', 'phone', 'email', 'avatar')
        }),
        # 专业信息
        ('专业信息', {
            'fields': ('service_types', 'introduction', 'years_of_experience')
        }),
        # 状态信息
        ('状态信息', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    # 优化查询性能，预加载关联的user对象
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'age', 'phone', 'student_id', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['name', 'phone', 'student_id']
    readonly_fields = ['created_at']


@admin.register(Consultation)  # 使用装饰器注册Consultation模型到Django admin站点
class ConsultationAdmin(admin.ModelAdmin):
    # 定义在列表页显示的字段
    list_display = ['client', 'counselor', 'type', 'status', 'scheduled_at', 'duration_display']
    # 定义用于过滤器的字段
    list_filter = ['type', 'status', 'scheduled_at', 'created_at']
    # 定义搜索字段，支持跨外键搜索
    search_fields = ['client__name', 'counselor__name', 'description']
    # 定义只读字段，不可编辑
    readonly_fields = ['created_at']
    # 定义日期层次结构字段
    date_hierarchy = 'scheduled_at'

    def duration_display(self, obj):
        # 自定义方法，用于显示咨询时长
        duration = obj.duration
        if duration > 0:
            return f"{duration} 分钟"
        return "未开始"

    # 设置duration_display方法在列表页的列标题
    duration_display.short_description = '咨询时长'

    def get_queryset(self, request):
        # 优化查询，使用select_related减少数据库查询次数
        return super().get_queryset(request).select_related('client', 'counselor')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['counselor', 'date', 'start_time', 'end_time', 'is_available_display', 'reason']
    list_filter = ['date', 'is_available', 'counselor']
    search_fields = ['counselor__name', 'reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'

    def is_available_display(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">● 可用</span>')
        else:
            return format_html('<span style="color: red;">● 停诊</span>')

    is_available_display.short_description = '状态'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('counselor')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['counselor', 'client_display', 'rating_stars', 'created_at']
    list_filter = ['rating', 'is_anonymous', 'created_at']
    search_fields = ['counselor__name', 'client__name', 'comment']
    readonly_fields = ['created_at']

    def client_display(self, obj):
        if obj.is_anonymous:
            return "匿名用户"
        return obj.client.name

    client_display.short_description = '客户'

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(f'<span style="color: gold;">{stars}</span>')

    rating_stars.short_description = '评分'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('counselor', 'client', 'consultation')


# 自定义Admin站点标题
admin.site.site_header = '学生心理服务云平台 - 咨询师管理系统'
admin.site.site_title = '心理服务平台'
admin.site.index_title = '数据管理'