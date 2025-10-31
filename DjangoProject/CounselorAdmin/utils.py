"""
通用工具函数
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from CounselorAdmin.models import AdminAuthToken


def _get_token_from_header(request):
    """从请求头获取token，支持 Bearer 格式和 token 格式"""
    auth = request.headers.get('Authorization') or request.headers.get('token') or ''
    if not auth:
        return ''
    
    auth_lower = auth.lower().strip()
    # 支持 Bearer <token> 格式
    if auth_lower.startswith('bearer '):
        return auth.split(' ', 1)[1].strip()
    # 支持 token <token> 格式
    elif auth_lower.startswith('token '):
        return auth.split(' ', 1)[1].strip()
    # 直接是token值
    return auth.strip()


def require_auth(view_func):
    """Token鉴权装饰器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = _get_token_from_header(request)
        if not token:
            return Response({'detail': '身份认证信息未提供。'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token_obj = AdminAuthToken.objects.filter(token=token, is_active=True).first()
        if not token_obj or (token_obj.expires_at and token_obj.expires_at < now()):
            return Response({'detail': '身份认证信息未提供。'}, status=status.HTTP_401_UNAUTHORIZED)
        
        request.admin_user = token_obj.user
        return view_func(request, *args, **kwargs)
    return wrapper

