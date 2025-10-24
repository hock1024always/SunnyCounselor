from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'CounselorAdmin'

router = DefaultRouter()

# 干预管理
router.register('interview', views.InterviewAssessmentViewSet, basename='interview')
router.register('negative_events', views.NegativeEventViewSet, basename='negative_events')
router.register('referral/organization', views.ReferralUnitViewSet, basename='referral-organization')
router.register('referral/management', views.StudentReferralViewSet, basename='referral-management')

# 健康宣教
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('articles', views.ArticleViewSet, basename='articles')
router.register('notification', views.NotificationViewSet, basename='notification')
router.register('banner', views.BannerModuleViewSet, basename='banner')

# 心理咨询
router.register('order', views.AppointmentViewSet, basename='order')
router.register('consultants', views.CounselorViewSet, basename='consultants')

# 文件管理和排班管理
router.register('files', views.FileViewSet, basename='files')
router.register('schedule', views.ScheduleViewSet, basename='schedule')

urlpatterns = [
    # 认证相关
    path('auth/login', views.login, name='login'),
    path('auth/register', views.register, name='register'),
    path('auth/captcha', views.captcha, name='captcha'),

    # 补充的独立接口
    path('categories/name', views.get_category_names, name='categories-name'),

    # 包含所有router生成的路由
    path('', include(router.urls)),
]