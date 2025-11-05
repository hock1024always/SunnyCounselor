"""
通用工具函数
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from CounselorAdmin.models import AdminAuthToken


def _verify_id_token(user_id, token):
    """
    验证用户ID和Token是否匹配
    
    参数:
        user_id: 用户ID（字符串或整数）
        token: Token字符串
    
    返回:
        (is_valid, token_obj): (是否有效, Token对象或None)
    """
    if not user_id or not token:
        return False, None
    
    try:
        # 查找该用户的活跃token
        token_obj = AdminAuthToken.objects.filter(
            user_id=int(user_id),
            token=str(token).strip(),
            is_active=True
        ).first()
        
        if not token_obj:
            return False, None
        
        # 检查token是否过期
        if token_obj.expires_at and token_obj.expires_at < now():
            return False, None
        
        return True, token_obj
    except (ValueError, TypeError):
        return False, None


def require_body_auth(view_func):
    """
    从请求体中验证user_id和token的装饰器
    支持JSON和multipart/form-data格式
    所有参数都在body中，包括user_id和token
    注意：这个装饰器必须在@api_view之后应用，并且需要在视图中设置permission_classes=[]
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 从请求体获取user_id和token
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        
        if not user_id or not token:
            return Response({
                'message': '认证失败',
                'detail': '请求体中缺少 user_id 或 token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 验证user_id和token
        is_valid, token_obj = _verify_id_token(user_id, token)
        
        if not is_valid:
            return Response({
                'message': '认证失败',
                'detail': '用户ID与Token不匹配或Token已过期'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 将用户信息附加到request上，供视图函数使用
        request.admin_user = token_obj.user
        request.verified_user_id = int(user_id)
        
        return view_func(request, *args, **kwargs)
    return wrapper

