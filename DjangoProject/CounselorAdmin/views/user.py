from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now

from CounselorAdmin.models import AdminUser, AdminAuthToken
from CounselorAdmin.Serilizers import AdminUserInfoSerializer


def _get_token_from_auth_header(request):
    auth = request.headers.get('Authorization') or ''
    if auth.lower().startswith('token '):
        return auth.split(' ', 1)[1].strip()
    return ''


class AdminUserInfoView(APIView):
    def get(self, request, id):
        token = _get_token_from_auth_header(request)
        if not token:
            return Response({'message': '未授权'}, status=status.HTTP_401_UNAUTHORIZED)

        token_obj = AdminAuthToken.objects.filter(token=token, is_active=True).first()
        if not token_obj or (token_obj.expires_at and token_obj.expires_at < now()):
            return Response({'message': 'Token无效或已过期'}, status=status.HTTP_401_UNAUTHORIZED)

        if str(token_obj.user_id) != str(id):
            return Response({'message': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

        user = AdminUser.objects.filter(id=id).first()
        if not user:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        data = AdminUserInfoSerializer(user).data
        return Response({'user_info': {
            'user_name': data.get('username'),
            'email': data.get('email'),
            'phone': data.get('phone'),
        }})


