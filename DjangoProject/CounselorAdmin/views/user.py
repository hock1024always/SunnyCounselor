from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from CounselorAdmin.models import AdminUser
from CounselorAdmin.Serilizers import AdminUserInfoSerializer
from CounselorAdmin.utils import _verify_id_token


class AdminUserInfoView(APIView):
    """
    获取用户信息接口
    使用POST方法，在请求体JSON中传递 user_id 和 token
    不需要在请求头设置任何鉴权信息，不涉及路径参数
    """
    permission_classes = []  # 不使用DRF的权限系统
    
    def post(self, request):
        # 从请求体的JSON中获取user_id和token
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        
        # 如果没有提供id和token
        if not user_id or not token:
            return Response({
                'message': '缺少必要参数',
                'detail': '请在请求体JSON中提供 user_id 和 token 字段'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证user_id和token是否匹配
        is_valid, token_obj = _verify_id_token(user_id, token)
        
        if not is_valid:
            return Response({
                'message': '认证失败',
                'detail': '用户ID与Token不匹配或Token已过期'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 获取用户信息
        user = AdminUser.objects.filter(id=user_id).first()
        if not user:
            return Response({
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        data = AdminUserInfoSerializer(user).data
        return Response({
            'user_info': {
                'user_name': data.get('username'),
                'email': data.get('email'),
                'phone': data.get('phone'),
            }
        })


