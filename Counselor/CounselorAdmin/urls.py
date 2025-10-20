from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'counselor_admin'

router = DefaultRouter()

# 干预管理相关路由
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'interviews', views.InterviewViewSet, basename='interview')
router.register(r'negative-events', views.NegativeEventViewSet, basename='negative-event')
router.register(r'referral-units', views.ReferralUnitViewSet, basename='referral-unit')
router.register(r'referral-histories', views.ReferralHistoryViewSet, basename='referral-history')

# 健康宣教相关路由
router.register(r'education-categories', views.EducationCategoryViewSet, basename='education-category')
router.register(r'education-contents', views.EducationContentViewSet, basename='education-content')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'banners', views.BannerViewSet, basename='banner')

# 心理咨询相关路由
router.register(r'counselor-schedules', views.CounselorScheduleViewSet, basename='counselor-schedule')
router.register(r'consultation-orders', views.ConsultationOrderViewSet, basename='consultation-order')

urlpatterns = [
    path('api/admin/', include(router.urls)),
]