from django.urls import path
from CounselorAdmin.views.auth import RegisterSendCodeView, RegisterView, LoginView, CaptchaView
from CounselorAdmin.views.user import AdminUserInfoView

# 函数式视图导入
from CounselorAdmin.views.intervention import (
    # 访谈评估
    interview_list,
    interview_create,
    interview_delete,
    interview_upload,
    interview_files_list,
    interview_files_upload,
    interview_files_download,
    # 负面事件
    negative_events_list,
    negative_events_create,
    negative_events_delete,
    # 转介单位
    referral_organization_list,
    referral_organization_create,
    referral_organization_delete,
    referral_organization_name_list,
    # 转介管理
    referral_management_list,
    referral_management_create,
    referral_management_update,
    referral_management_delete,
)

from CounselorAdmin.views.education import (
    # 栏目管理
    categories_list,
    categories_create,
    categories_update,
    categories_delete,
    categories_name_list,
    # 宣教管理
    articles_list,
    articles_create,
    articles_detail,
    articles_update,
    articles_delete,
    # 通知管理
    notification_list,
    notification_create,
    notification_update,
    notification_delete,
    # Banner管理
    banner_list,
    banner_create,
    banner_update,
    banner_delete,
)

from CounselorAdmin.views.counseling import (
    # 咨询统计
    order_list,
    order_create,
    # 咨询师管理
    consultants_list,
    consultants_create,
    consultants_update,
    consultants_delete,
    consultants_status_update,
    # 排班管理
    schedule_work_list,
    schedule_work_create,
    schedule_files_upload,
    schedule_stop_list,
    schedule_stop_update,
)

urlpatterns = [
    # ==================== 用户认证 ====================
    path('auth/register/send_code', RegisterSendCodeView.as_view()),
    path('auth/register', RegisterView.as_view()),
    path('auth/login', LoginView.as_view()),
    path('auth/captcha', CaptchaView.as_view()),
    path('user/info', AdminUserInfoView.as_view()),
    
    # ==================== 干预管理 ====================
    # 访谈评估
    path('api/admin/interview/list', interview_list),  # POST
    path('api/admin/interview/create', interview_create),  # POST
    path('api/admin/interview/delete', interview_delete),  # POST
    path('api/admin/interview/upload', interview_upload),  # POST
    path('api/interview/files', interview_files_list),  # POST 模板列表
    path('api/admin/interview/files/upload', interview_files_upload),  # POST 模板上传
    path('api/admin/interview/files/download', interview_files_download),  # POST 模板下载
    
    # 负面事件
    path('api/admin/negative_events/list', negative_events_list),  # POST
    path('api/admin/negative_events/create', negative_events_create),  # POST
    path('api/admin/negative_events/delete', negative_events_delete),  # POST
    
    # 转介单位
    path('api/admin/referral/organization/list', referral_organization_list),  # POST
    path('api/admin/referral/organization/create', referral_organization_create),  # POST
    path('api/admin/referral/organization/delete', referral_organization_delete),  # POST
    path('api/admin/referral/organization/name', referral_organization_name_list),  # POST
    
    # 转介管理
    path('api/admin/referral/management/list', referral_management_list),  # POST
    path('api/admin/referral/management/create', referral_management_create),  # POST
    path('api/admin/referral/management/update', referral_management_update),  # POST
    path('api/admin/referral/management/delete', referral_management_delete),  # POST
    
    # ==================== 健康宣教 ====================
    # 栏目管理
    path('api/admin/categories/list', categories_list),  # POST
    path('api/admin/categories/create', categories_create),  # POST
    path('api/admin/categories/update', categories_update),  # POST
    path('api/admin/categories/delete', categories_delete),  # POST
    path('api/admin/categories/name', categories_name_list),  # POST
    
    # 宣教管理
    path('api/admin/articles/list', articles_list),  # POST
    path('api/admin/articles/create', articles_create),  # POST
    path('api/admin/articles/detail', articles_detail),  # POST
    path('api/admin/articles/update', articles_update),  # POST
    path('api/admin/articles/delete', articles_delete),  # POST
    
    # 通知管理
    path('api/admin/notification/list', notification_list),  # POST
    path('api/admin/notification/create', notification_create),  # POST
    path('api/admin/notification/update', notification_update),  # POST
    path('api/admin/notification/delete', notification_delete),  # POST
    
    # Banner管理
    path('api/admin/banner/list', banner_list),  # POST
    path('api/admin/banner/create', banner_create),  # POST
    path('api/admin/banner/update', banner_update),  # POST
    path('api/admin/banner/delete', banner_delete),  # POST
    
    # ==================== 心理咨询 ====================
    # 咨询统计
    path('api/admin/order/list', order_list),  # POST
    path('api/admin/order/create', order_create),  # POST
    
    # 咨询师管理
    path('api/admin/consultants/list', consultants_list),  # POST
    path('api/admin/consultants/create', consultants_create),  # POST
    path('api/admin/consultants/update', consultants_update),  # POST
    path('api/admin/consultants/delete', consultants_delete),  # POST
    path('api/admin/consults/status', consultants_status_update),  # POST
    
    # 排班管理
    path('api/admin/schedule/work/list', schedule_work_list),  # POST
    path('api/admin/schedule/work/create', schedule_work_create),  # POST
    path('api/admin/schedule/files', schedule_files_upload),  # POST
    path('api/admin/schedule/stop/list', schedule_stop_list),  # POST
    path('api/admin/schedule/stop/update', schedule_stop_update),  # POST
]
