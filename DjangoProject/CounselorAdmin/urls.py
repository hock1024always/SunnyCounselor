from django.urls import path
from CounselorAdmin.views.auth import RegisterSendCodeView, RegisterView, LoginView, CaptchaView
from CounselorAdmin.views.user import AdminUserInfoView

# 函数式视图导入
from CounselorAdmin.views.intervention import (
    # 访谈评估
    interview_list_create,
    interview_delete,
    interview_upload,
    interview_files_list,
    interview_files_upload,
    interview_files_download,
    # 负面事件
    negative_events_list_create,
    negative_events_delete,
    # 转介单位
    referral_organization_list_create,
    referral_organization_delete,
    referral_organization_name_list,
    # 转介管理
    referral_management_list_create_update,
    referral_management_delete,
)

from CounselorAdmin.views.education import (
    # 栏目管理
    categories_list_create_update,
    categories_delete,
    categories_name_list,
    # 宣教管理
    articles_list_create_update,
    articles_delete,
    # 通知管理
    notification_list_create_update,
    notification_delete,
    # Banner管理
    banner_list_create_update,
    banner_delete,
)

from CounselorAdmin.views.counseling import (
    # 咨询统计
    order_list_create,
    # 咨询师管理
    consultants_list_create_update,
    consultants_delete,
    consultants_status_update,
    # 排班管理
    schedule_work_list_create,
    schedule_files_upload,
    schedule_stop_list_update,
)

urlpatterns = [
    # ==================== 用户认证 ====================
    path('auth/register/send_code', RegisterSendCodeView.as_view()),
    path('auth/register', RegisterView.as_view()),
    path('auth/login', LoginView.as_view()),
    path('auth/captcha', CaptchaView.as_view()),
    path('user/<int:id>', AdminUserInfoView.as_view()),
    
    # ==================== 干预管理 ====================
    # 访谈评估
    path('api/admin/interview', interview_list_create),  # GET/POST
    path('api/admin/interview/<int:id>', interview_delete),  # DELETE
    path('api/admin/interview/upload', interview_upload),  # POST
    path('api/interview/files', interview_files_list),  # GET
    path('api/admin/interview/files', interview_files_upload),  # POST
    path('api/admin/interview/files/download', interview_files_download),  # GET - 使用download避免冲突
    
    # 负面事件
    path('api/admin/negative_events', negative_events_list_create),  # GET/POST
    path('api/admin/negative_events/<int:id>', negative_events_delete),  # DELETE
    
    # 转介单位
    path('api/admin/referral/organization', referral_organization_list_create),  # GET/POST
    path('api/admin/referral/organization/<int:id>', referral_organization_delete),  # DELETE
    path('api/admin/referral/organization/name', referral_organization_name_list),  # GET
    
    # 转介管理
    path('api/admin/referral/management', referral_management_list_create_update),  # GET/POST/PUT
    path('api/admin/referral/management/<int:id>', referral_management_delete),  # DELETE
    
    # ==================== 健康宣教 ====================
    # 栏目管理
    path('api/admin/categories', categories_list_create_update),  # GET/POST/PUT
    path('api/admin/categories/<int:id>', categories_delete),  # DELETE
    path('api/admin/categories/name', categories_name_list),  # GET
    
    # 宣教管理
    path('api/admin/articles', articles_list_create_update),  # GET/POST/PUT
    path('api/admin/articles/<int:id>', articles_delete),  # DELETE
    
    # 通知管理
    path('api/admin/notification', notification_list_create_update),  # GET/POST/PUT
    path('api/admin/notification/<int:id>', notification_delete),  # DELETE
    
    # Banner管理
    path('api/admin/banner', banner_list_create_update),  # GET/POST/PUT
    path('api/admin/banner/<int:id>', banner_delete),  # DELETE
    
    # ==================== 心理咨询 ====================
    # 咨询统计
    path('api/admin/order', order_list_create),  # GET/POST
    
    # 咨询师管理
    path('api/admin/consultants', consultants_list_create_update),  # GET/POST/PUT
    path('api/admin/consultants/<int:id>', consultants_delete),  # DELETE
    path('api/admin/consults/status', consultants_status_update),  # PUT
    
    # 排班管理
    path('api/admin/schedule/work', schedule_work_list_create),  # GET/POST
    path('api/admin/schedule/files', schedule_files_upload),  # POST
    path('api/admin/schedule/stop', schedule_stop_list_update),  # GET/PUT
]
