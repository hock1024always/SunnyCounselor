from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'counselor'

router = DefaultRouter()
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')
router.register(r'consultations', views.ConsultationViewSet, basename='consultation')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # 首页和数据看板
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),

    # 在线咨询管理 - 使用视图集的action
    path('consultations/pending/', views.PendingConsultationListView.as_view(), name='pending-consultations'),
    path('consultations/in-progress/', views.InProgressConsultationListView.as_view(),
         name='in-progress-consultations'),
    path('consultations/completed/', views.CompletedConsultationListView.as_view(), name='completed-consultations'),
    path('consultations/rejected/', views.RejectedConsultationListView.as_view(), name='rejected-consultations'),

    # 排班管理
    path('schedules/bulk-create/', views.BulkCreateScheduleView.as_view(), name='bulk-create-schedule'),
    path('schedules/stop-service/', views.StopServiceView.as_view(), name='stop-service'),

    # 个人设置
    path('profile/', views.CounselorProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('profile/service-types/', views.UpdateServiceTypesView.as_view(), name='update-service-types'),

    # API路由
    path('api/', include(router.urls)),
]

# 添加API版本控制
urlpatterns += [
    path('api/v1/', include(router.urls)),
]