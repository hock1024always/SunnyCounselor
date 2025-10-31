from math import ceil

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now

from CounselorAdmin.models import Category, AdminAuthToken
from CounselorAdmin.Serilizers.category import (
    CategoryListItemSerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer,
)


def _get_token_from_header(request):
    auth = request.headers.get('Authorization') or ''
    if auth.lower().startswith('token '):
        return auth.split(' ', 1)[1].strip()
    return ''


def _require_token(request):
    token = _get_token_from_header(request)
    if not token:
        return None, Response({'message': '未授权'}, status=status.HTTP_401_UNAUTHORIZED)

    # 添加测试逻辑：如果 token 是 "2025"，则返回 id 为 1 的用户
    if token == "2025":
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=1)
            return user, None
        except User.DoesNotExist:
            return None, Response({'message': '测试用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    token_obj = AdminAuthToken.objects.filter(token=token, is_active=True).first()
    if not token_obj or (token_obj.expires_at and token_obj.expires_at < now()):
        return None, Response({'message': 'Token无效或已过期'}, status=status.HTTP_401_UNAUTHORIZED)
    return token_obj.user, None


class CategoryListCreateView(APIView):
    def get(self, request):
        user, error = _require_token(request)
        if error:
            return error
        try:
            page = int(request.query_params.get('page'))
            page_size = int(request.query_params.get('page_size'))
        except Exception:
            return Response({'message': '缺少或非法的分页参数'}, status=status.HTTP_400_BAD_REQUEST)

        name = request.query_params.get('name')
        qs = Category.objects.all().order_by('sort_order', 'created_time')
        if name:
            qs = qs.filter(category_name__icontains=name)

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        data = CategoryListItemSerializer(items, many=True).data
        return Response({'total': total, 'data': data})

    def post(self, request):
        user, error = _require_token(request)
        if error:
            return error
        payload = request.data.copy()
        serializer = CategoryCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response({'id': obj.id, 'message': '创建成功'})


class CategoryUpdateDeleteView(APIView):
    def delete(self, request, id):
        user, error = _require_token(request)
        if error:
            return error
        deleted = Category.objects.filter(id=id).delete()[0]
        return Response({'success': bool(deleted)})

    def put(self, request):
        user, error = _require_token(request)
        if error:
            return error
        serializer = CategoryUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cid = serializer.validated_data.get('id')
        try:
            obj = Category.objects.get(id=cid)
        except Category.DoesNotExist:
            return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 部分字段更新
        for src, field in [('category_name', 'category_name'), ('sort_order', 'sort_order'), ('created_by', 'created_by')]:
            if src in serializer.validated_data:
                setattr(obj, field, serializer.validated_data[src])
        obj.save()
        return Response({'success': True})


class CategoryNameListView(APIView):
    def get(self, request):
        user, error = _require_token(request)
        if error:
            return error
        names = list(Category.objects.values_list('category_name', flat=True))
        return Response({'data': names})


