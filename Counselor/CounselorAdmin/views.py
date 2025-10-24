# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
from .serializers import *
from .models import AdminUser
import json


# 基础视图类
class BaseViewSet(viewsets.ModelViewSet):
    def get_paginated_response(self, queryset, serializer_class, page, page_size):
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        serializer = serializer_class(page_obj, many=True)
        return Response({
            'total': paginator.count,
            'data': serializer.data
        })


# 访谈评估视图
class InterviewAssessmentViewSet(BaseViewSet):
    queryset = InterviewAssessment.objects.all()

    def list(self, request):
        query_serializer = InterviewQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = query_serializer.validated_data
        queryset = InterviewAssessment.objects.all()

        # 构建查询条件
        filters = Q()
        if data.get('std_name'):
            filters &= Q(student_name__icontains=data['std_name'])
        if data.get('std_grade'):
            filters &= Q(grade__icontains=data['std_grade'])
        if data.get('std_class'):
            filters &= Q(class_name__icontains=data['std_class'])
        if data.get('std_school'):
            filters &= Q(organization__icontains=data['std_school'])
        if data.get('interview_status'):
            filters &= Q(interview_status=data['interview_status'])
        if data.get('interview_type'):
            filters &= Q(interview_type__icontains=data['interview_type'])
        if data.get('doctor_evaluation'):
            filters &= Q(doctor_assessment__icontains=data['doctor_evaluation'])
        if data.get('follow_up_plan'):
            filters &= Q(follow_up_plan__icontains=data['follow_up_plan'])

        queryset = queryset.filter(filters)

        page = data.get('page', 1)
        page_size = data.get('page_size', 20)

        return self.get_paginated_response(queryset, InterviewAssessmentSerializer, page, page_size)

    def create(self, request):
        serializer = InterviewAssessmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                'code': '1',
                'id': instance.id,
                'message': '新建成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({})
        except InterviewAssessment.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        # 文件上传逻辑（待实现）
        return Response({})

    @action(detail=False, methods=['get'])
    def files(self, request):
        # 模板文件列表（待实现）
        return Response({
            'files': {
                'file_name': '访谈记录模板.xlsx',
                'file_size': '20KB'
            }
        })


# 负面事件视图
class NegativeEventViewSet(BaseViewSet):
    queryset = NegativeEvent.objects.all()

    def list(self, request):
        query_serializer = NegativeEventQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = query_serializer.validated_data
        queryset = NegativeEvent.objects.all()

        # 构建查询条件
        filters = Q()
        if data.get('std_name'):
            filters &= Q(student_name__icontains=data['std_name'])
        if data.get('date_start') and data.get('date_end'):
            filters &= Q(event_date__range=[data['date_start'], data['date_end']])

        queryset = queryset.filter(filters)

        page = data.get('page', 1)
        page_size = data.get('page_size', 20)

        return self.get_paginated_response(queryset, NegativeEventSerializer, page, page_size)

    def create(self, request):
        serializer = NegativeEventCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                'code': '1',
                'id': instance.id,
                'message': '新建成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.disabled = True  # 软删除
            instance.save()
            return Response({})
        except NegativeEvent.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)


# 转介单位视图
class ReferralUnitViewSet(BaseViewSet):
    queryset = ReferralUnit.objects.all()

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        org_name = request.query_params.get('org_name')

        queryset = ReferralUnit.objects.all()
        if org_name:
            queryset = queryset.filter(unit_name__icontains=org_name)

        return self.get_paginated_response(queryset, ReferralUnitSerializer, page, page_size)

    def create(self, request):
        serializer = ReferralUnitCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                'code': '1',
                'id': instance.id,
                'message': '新建成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({})
        except ReferralUnit.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def name(self, request):
        units = ReferralUnit.objects.all()
        serializer = ReferralUnitNameSerializer(units, many=True)
        names = [item['unit_name'] for item in serializer.data]
        return Response({'data': names})


# 学生转介视图
class StudentReferralViewSet(BaseViewSet):
    queryset = StudentReferral.objects.all()

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        std_name = request.query_params.get('std_name')

        queryset = StudentReferral.objects.all()
        if std_name:
            queryset = queryset.filter(student_name__icontains=std_name)

        return self.get_paginated_response(queryset, StudentReferralSerializer, page, page_size)

    def create(self, request):
        serializer = StudentReferralCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                'id': instance.id,
                'message': '新建成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = StudentReferralCreateSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentReferral.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({})
        except StudentReferral.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)


# 栏目视图
class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        name = request.query_params.get('name')

        queryset = Category.objects.all()
        if name:
            queryset = queryset.filter(category_name__icontains=name)

        return self.get_paginated_response(queryset, CategorySerializer, page, page_size)

    def create(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                'id': instance.id,
                'message': '新建成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = CategoryCreateSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({})
        except Category.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)


# 宣教资讯视图
class ArticleViewSet(BaseViewSet):
    queryset = Article.objects.all()

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        title = request.query_params.get('title')

        queryset = Article.objects.all()
        if title:
            queryset = queryset.filter(title__icontains=title)

        return self.get_paginated_response(queryset, ArticleSerializer, page, page_size)

    def create(self, request):
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                'id': instance.id,
                'message': '新建成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = ArticleCreateSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Article.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({})
        except Article.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)


# 通知视图
class NotificationViewSet(BaseViewSet):
    queryset = Notification.objects.all()

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        title = request.query_params.get('title')

        queryset = Notification.objects.all()
        if title:
            queryset = queryset.filter(title__icontains=title)

        return self.get_paginated_response(queryset, NotificationSerializer, page, page_size)

    def create(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                'id': instance.id,
                'message': '新建成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = NotificationCreateSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Notification.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({})
        except Notification.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)


# Banner视图
class BannerModuleViewSet(BaseViewSet):
    queryset = BannerModule.objects.all()

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        module = request.query_params.get('module')

        queryset = BannerModule.objects.all()
        if module:
            queryset = queryset.filter(module_name__icontains=module)

        return self.get_paginated_response(queryset, BannerModuleSerializer, page, page_size)

    def create(self, request):
        serializer = BannerModuleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = BannerModuleCreateSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BannerModule.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({})
        except BannerModule.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)


# 预约订单视图
class AppointmentViewSet(BaseViewSet):
    queryset = Appointment.objects.all()

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        name = request.query_params.get('name')
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')
        service_type = request.query_params.get('type')
        status = request.query_params.get('status')

        queryset = Appointment.objects.all()

        filters = Q()
        if name:
            filters &= Q(client_name__icontains=name)
        if date_start and date_end:
            filters &= Q(appointment_date__range=[date_start, date_end])
        if service_type:
            filters &= Q(service_type=service_type)
        if status:
            filters &= Q(status=status)

        queryset = queryset.filter(filters)

        return self.get_paginated_response(queryset, AppointmentSerializer, page, page_size)

    def create(self, request):
        serializer = AppointmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 咨询师视图
class CounselorViewSet(BaseViewSet):
    queryset = Counselor.objects.all()

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        name = request.query_params.get('name')
        phone = request.query_params.get('phone')
        status = request.query_params.get('status')

        queryset = Counselor.objects.all()

        filters = Q()
        if name:
            filters &= Q(name__icontains=name)
        if phone:
            filters &= Q(phone__icontains=phone)
        if status:
            filters &= Q(status=status)

        queryset = queryset.filter(filters)

        return self.get_paginated_response(queryset, CounselorSerializer, page, page_size)

    def create(self, request):
        serializer = CounselorCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = CounselorCreateSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Counselor.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({})
        except Counselor.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['put'])
    def status(self, request):
        counselor_id = request.data.get('id')
        new_status = request.data.get('status')

        try:
            counselor = Counselor.objects.get(id=counselor_id)
            counselor.status = new_status
            counselor.save()
            return Response({})
        except Counselor.DoesNotExist:
            return Response({'error': '咨询师不存在'}, status=status.HTTP_404_NOT_FOUND)


# 认证视图（简化版）
from rest_framework.decorators import api_view


@api_view(['POST'])
def login(request):
    # 登录逻辑（待实现）
    return Response({})


@api_view(['POST'])
def register(request):
    # 注册逻辑（待实现）
    return Response({})


@api_view(['GET'])
def captcha(request):
    # 验证码逻辑（待实现）
    return Response({})



# 文件上传下载相关视图
# 在views.py中补充以下视图类

# 文件上传下载相关视图
class FileViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], url_path='interview/files')
    def upload_interview_template(self, request):
        """上传访谈记录模板文件 - POST /admin/api/admin/files/interview/files/"""
        return Response({})

    @action(detail=False, methods=['get'], url_path='interview/files')
    def download_interview_template(self, request):
        """下载访谈记录模板文件 - GET /admin/api/admin/files/interview/files/"""
        files = request.query_params.getlist('files')
        return Response({})

    @action(detail=False, methods=['post'], url_path='schedule/files')
    def upload_schedule_file(self, request):
        """上传排班文件 - POST /admin/api/admin/files/schedule/files/"""
        return Response({})


# 排班管理视图
class ScheduleViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def work(self, request):
        """按年月份获取排班信息 - GET /admin/api/admin/schedule/work/"""
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        return Response({})

    @action(detail=False, methods=['post'])
    def work(self, request):
        """给单个日期添加排班 - POST /admin/api/admin/schedule/work/"""
        return Response({})

    @action(detail=False, methods=['get'])
    def stop(self, request):
        """按年份查询停诊信息 - GET /admin/api/admin/schedule/stop/"""
        year = request.query_params.get('year')
        return Response({})

    @action(detail=False, methods=['put'])
    def stop(self, request):
        """添加/修改停诊安排 - PUT /admin/api/admin/schedule/stop/"""
        return Response({})


# 栏目名称查询视图函数
@api_view(['GET'])
def get_category_names(request):
    """只查询栏目名称 - GET /admin/api/admin/categories/name"""
    categories = Category.objects.all().values_list('category_name', flat=True)
    return Response({'data': list(categories)})