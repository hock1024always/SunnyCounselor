"""
咨询师端URL配置
"""
from django.urls import path
from Consultant.views.auth import (
    LoginView,
    RegisterView,
    SendEmailCodeView,
    SendPhoneCodeView,
    ResetPasswordView,
    DeactivateView
)
from Consultant.views.dashboard import (
    today_transactions,
    category_data,
    yearly_consultations,
    time_slot_data,
    gender_data,
    age_data
)
from Consultant.views.order import (
    order_list,
    order_create
)
from Consultant.views.record import (
    record_list,
    record_create,
    record_delete,
    record_profile,
    session_create,
    session_update,
    personal_profile,
    upload_records,
    upload_template,
    download_template,
    template_list
)
from Consultant.views.schedule import (
    schedule_work,
    schedule_work_update,
    schedule_upload,
    schedule_stop,
    schedule_stop_create,
    schedule_stop_update,
    schedule_stop_delete,
    schedule_stop_conflict
)
from Consultant.views.user import (
    comments,
    user_profile,
    update_profile,
    update_avatar
)

urlpatterns = [
    # ==================== 认证相关 ====================
    path('api/consultant/auth/login', LoginView.as_view(), name='consultant_login'),
    path('api/consultant/auth/register', RegisterView.as_view(), name='consultant_register'),
    path('api/consultant/auth/email', SendEmailCodeView.as_view(), name='consultant_send_email_code'),
    path('api/consult/auth/phone', SendPhoneCodeView.as_view(), name='consultant_send_phone_code'),
    path('api/consultant/auth/reset-password', ResetPasswordView.as_view(), name='consultant_reset_password'),
    path('api/consultant/auth/deactivate', DeactivateView.as_view(), name='consultant_deactivate'),
    
    # ==================== 仪表盘 ====================
    path('api/consultant/dashboard/today-transactions', today_transactions, name='today_transactions'),
    path('api/consultant/dashboard/category-data', category_data, name='category_data'),
    path('api/consultant/dashboard/yearly-consultations', yearly_consultations, name='yearly_consultations'),
    path('api/consultant/dashboard/time-slot-data', time_slot_data, name='time_slot_data'),
    path('api/consultant/dashboard/gender-data', gender_data, name='gender_data'),
    path('api/consultant/dashboard/age-data', age_data, name='age_data'),
    
    # ==================== 咨询列表 ====================
    path('api/consultant/orders', order_list, name='order_list'),
    path('api/consultant/orders/create', order_create, name='order_create'),
    
    # ==================== 咨询档案 ====================
    path('api/consultant/interview/records', record_list, name='record_list'),
    path('api/consultant/interview/records/create', record_create, name='record_create'),
    path('api/consultant/interview/records/delete', record_delete, name='record_delete'),
    path('api/consultant/interview/records/profile', record_profile, name='record_profile'),
    path('api/consultant/interview/records/profile/create', session_create, name='session_create'),
    path('api/consultant/interview/records/profile/update', session_update, name='session_update'),
    path('api/consultant/interview/records/personal-profile', personal_profile, name='personal_profile'),
    path('api/consultant/interview/upload/records', upload_records, name='upload_records'),
    path('api/consultant/interview/upload/template', upload_template, name='upload_template'),
    path('api/consultant/interview/download', download_template, name='download_template'),
    path('api/consultant/interview/template/list', template_list, name='template_list'),
    
    # ==================== 排班管理 ====================
    path('api/consultant/schedule/work', schedule_work, name='schedule_work'),
    path('api/consultant/schedule/work/update', schedule_work_update, name='schedule_work_update'),
    path('api/consultant/schedule/upload', schedule_upload, name='schedule_upload'),
    path('api/consultant/schedule/stop', schedule_stop, name='schedule_stop'),
    path('api/consultant/schedule/stop/create', schedule_stop_create, name='schedule_stop_create'),
    path('api/consultant/schedule/stop/update', schedule_stop_update, name='schedule_stop_update'),
    path('api/consultant/schedule/stop/delete', schedule_stop_delete, name='schedule_stop_delete'),
    path('api/consultant/schedule/stop/conflict', schedule_stop_conflict, name='schedule_stop_conflict'),
    
    # ==================== 个人中心 ====================
    path('api/consuntant/user/comments', comments, name='user_comments'),
    path('api/consultant/user/profile', user_profile, name='user_profile'),
    path('api/consultant/user/updateProfile', update_profile, name='update_profile'),
    path('api/consultant/updateAvatar', update_avatar, name='update_avatar'),
]

