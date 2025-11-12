"""
咨询师端通用工具函数
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from Consultant.models import ConsultantAuthToken
import json


def _verify_id_token(user_id, token):
    """
    验证咨询师用户ID和Token是否匹配
    
    参数:
        user_id: 用户ID（字符串或整数）
        token: Token字符串
    
    返回:
        (is_valid, token_obj): (是否有效, Token对象或None)
    """
    if not user_id or not token:
        return False, None
    
    try:
        # 查找该咨询师的活跃token
        token_obj = ConsultantAuthToken.objects.filter(
            counselor_id=int(user_id),
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


def _get_request_data(request):
    """
    安全地获取请求数据
    支持DRF的request.data和原生Django request
    """
    # 首先尝试使用DRF的request.data（这是最可靠的方式）
    try:
        if hasattr(request, 'data'):
            data = request.data
            # 如果data是QueryDict，转换为普通字典
            if hasattr(data, 'dict'):
                return data.dict()
            # 如果data是列表或其他类型，直接返回
            if data is not None:
                return dict(data) if isinstance(data, (list, tuple)) else data
    except (AttributeError, TypeError, Exception) as e:
        # 如果访问request.data失败，继续尝试其他方法
        pass
    
    # 如果request.data不可用，尝试手动解析JSON
    try:
        content_type = ''
        if hasattr(request, 'content_type'):
            content_type = request.content_type or ''
        elif hasattr(request, 'META'):
            content_type = request.META.get('CONTENT_TYPE', '')
        
        if 'application/json' in content_type.lower():
            if hasattr(request, 'body'):
                body = request.body
                if isinstance(body, bytes):
                    body_str = body.decode('utf-8')
                else:
                    body_str = str(body)
                
                if body_str:
                    parsed_data = json.loads(body_str)
                    return parsed_data if isinstance(parsed_data, dict) else {}
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, ValueError) as e:
        # JSON解析失败，继续尝试其他方法
        pass
    
    # 尝试从POST数据获取（form-data格式）
    try:
        if hasattr(request, 'POST') and request.POST:
            return dict(request.POST)
    except Exception:
        pass
    
    # 尝试从GET数据获取（虽然不太可能，但作为后备）
    try:
        if hasattr(request, 'GET') and request.GET:
            return dict(request.GET)
    except Exception:
        pass
    
    # 如果都不可用，返回空字典
    return {}


def require_body_auth(view_func):
    """
    从请求体中验证user_id和token的装饰器
    支持JSON和multipart/form-data格式
    所有参数都在body中，包括user_id和token
    注意：这个装饰器必须在@api_view之后应用，并且需要在视图中设置permission_classes=[]
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 获取请求数据 - 优先使用DRF的request.data
        user_id = None
        token = None
        
        # 方法1: 尝试使用DRF的request.data（最可靠）
        try:
            # 在DRF的APIView中，request.data是一个属性，会自动解析请求体
            if hasattr(request, 'data'):
                data = request.data
                # 支持QueryDict和普通字典
                if hasattr(data, 'get'):
                    user_id = data.get('userID') or data.get('user_id') or data.get('userId') or data.get('id')
                    token = data.get('token')
                # 如果是字典类型
                elif isinstance(data, dict):
                    user_id = data.get('userID') or data.get('user_id') or data.get('userId') or data.get('id')
                    token = data.get('token')
        except (AttributeError, TypeError, Exception):
            # 如果访问request.data失败，继续尝试其他方法
            pass
        
        # 方法2: 如果request.data不可用，手动解析JSON请求体
        if not user_id or not token:
            try:
                # 获取Content-Type
                content_type = ''
                if hasattr(request, 'content_type'):
                    content_type = request.content_type or ''
                elif hasattr(request, 'META'):
                    content_type = request.META.get('CONTENT_TYPE', '')
                
                # 如果是JSON请求，手动解析
                if 'application/json' in content_type.lower():
                    if hasattr(request, 'body'):
                        body = request.body
                        if isinstance(body, bytes):
                            body_str = body.decode('utf-8')
                        else:
                            body_str = str(body)
                        
                        if body_str:
                            parsed_data = json.loads(body_str)
                            if isinstance(parsed_data, dict):
                                if not user_id:
                                    user_id = parsed_data.get('userID') or parsed_data.get('user_id') or parsed_data.get('userId') or parsed_data.get('id')
                                if not token:
                                    token = parsed_data.get('token')
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, ValueError, Exception):
                pass
        
        # 方法3: 尝试从POST数据获取（form-data格式）
        if not user_id or not token:
            try:
                if hasattr(request, 'POST') and request.POST:
                    if not user_id:
                        user_id = request.POST.get('userID') or request.POST.get('user_id') or request.POST.get('userId') or request.POST.get('id')
                    if not token:
                        token = request.POST.get('token')
            except Exception:
                pass
        
        # 验证是否获取到userID和token
        if not user_id or not token:
            # 添加调试信息，帮助排查问题
            debug_info = {
                'has_request_data': hasattr(request, 'data'),
                'request_type': str(type(request)),
            }
            try:
                if hasattr(request, 'data'):
                    debug_info['data_type'] = str(type(request.data))
                    if hasattr(request.data, 'keys'):
                        debug_info['data_keys'] = list(request.data.keys())
                    elif isinstance(request.data, dict):
                        debug_info['data_keys'] = list(request.data.keys())
            except:
                pass
            
            return Response({
                'code': 401,
                'message': '认证失败：请求体中缺少 userID 或 token（支持字段：userID, user_id, userId, id）',
                'debug': debug_info
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 验证user_id和token
        is_valid, token_obj = _verify_id_token(user_id, token)
        
        if not is_valid:
            return Response({
                'code': 401,
                'message': '认证失败：用户ID与Token不匹配或Token已过期'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 将用户信息附加到request上，供视图函数使用
        request.counselor = token_obj.counselor
        request.verified_user_id = int(user_id)
        
        return view_func(request, *args, **kwargs)
    return wrapper

