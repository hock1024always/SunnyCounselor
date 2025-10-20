from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
try:
    import pandas as pd
except ImportError:
    pd = None
import json
from datetime import datetime

from .models import (
    Student, Interview, NegativeEvent, ReferralUnit, ReferralHistory,
    EducationCategory, EducationContent, Notification, Banner,
    CounselorSchedule, ConsultationOrder
)
from .serializers import (
    StudentSerializer, InterviewSerializer, NegativeEventSerializer,
    ReferralUnitSerializer, ReferralHistorySerializer, EducationCategorySerializer,
    EducationContentSerializer, NotificationSerializer, BannerSerializer,
    CounselorScheduleSerializer, ConsultationOrderSerializer,
    StudentImportSerializer, InterviewTemplateSerializer,
    InterviewStatisticsSerializer, EducationStatisticsSerializer
)
from django.db.models import Sum


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['school', 'grade', 'class_name', 'gender']
    search_fields = ['name', 'student_id', 'school']
    ordering_fields = ['created_at', 'updated_at', 'name']
    
    @action(detail=False, methods=['post'], serializer_class=StudentImportSerializer)
    def import_students(self, request):
        """导入学生名单"""
        if pd is None:
            return Response({'error': 'pandas库未安装，无法处理Excel文件'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = StudentImportSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            try:
                # 读取Excel文件
                df = pd.read_excel(file)
                created_count = 0
                errors = []
                
                for index, row in df.iterrows():
                    try:
                        student, created = Student.objects.get_or_create(
                            student_id=row['学号'],
                            defaults={
                                'name': row['姓名'],
                                'gender': row.get('性别', 'other'),
                                'age': row.get('年龄', 0),
                                'school': row['学校'],
                                'grade': row['年级'],
                                'class_name': row['班级'],
                                'phone': row.get('联系电话', ''),
                                'emergency_contact': row.get('紧急联系人', ''),
                                'emergency_phone': row.get('紧急联系电话', ''),
                            }
                        )
                        if created:
                            created_count += 1
                    except Exception as e:
                        errors.append(f"第{index+1}行错误: {str(e)}")
                
                return Response({
                    'message': f'成功导入{created_count}名学生',
                    'errors': errors
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({'error': f'文件处理错误: {str(e)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], serializer_class=InterviewTemplateSerializer)
    def download_template(self, request):
        """下载导入模板"""
        if pd is None:
            return Response({'error': 'pandas库未安装，无法生成Excel模板'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        template_type = request.query_params.get('template_type', 'student_list')
        
        if template_type == 'student_list':
            # 创建学生名单模板
            df = pd.DataFrame(columns=['姓名', '学号', '性别', '年龄', '学校', '年级', '班级', '联系电话', '紧急联系人', '紧急联系电话'])
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="student_import_template.xlsx"'
            df.to_excel(response, index=False)
            return response
        
        return Response({'error': '无效的模板类型'}, status=status.HTTP_400_BAD_REQUEST)


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'assessment_level', 'counselor', 'student']
    search_fields = ['student__name', 'counselor__name', 'interview_notes']
    ordering_fields = ['interview_date', 'created_at', 'updated_at']
    
    @action(detail=True, methods=['post'])
    def end_interview(self, request, pk=None):
        """手动结束访谈"""
        interview = self.get_object()
        if interview.status == 'completed':
            return Response({'error': '访谈已结束'}, status=status.HTTP_400_BAD_REQUEST)
        
        interview.status = 'completed'
        interview.is_manual_end = True
        interview.ended_at = datetime.now()
        interview.save()
        
        return Response({'message': '访谈已结束'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取访谈统计信息"""
        total = Interview.objects.count()
        completed = Interview.objects.filter(status='completed').count()
        pending = Interview.objects.filter(status='pending').count()
        high_risk = Interview.objects.filter(assessment_level='high').count()
        referral_count = ReferralHistory.objects.count()
        
        serializer = InterviewStatisticsSerializer({
            'total_interviews': total,
            'completed_interviews': completed,
            'pending_interviews': pending,
            'high_risk_count': high_risk,
            'referral_count': referral_count
        })
        
        return Response(serializer.data)


class NegativeEventViewSet(viewsets.ModelViewSet):
    queryset = NegativeEvent.objects.all()
    serializer_class = NegativeEventSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'severity', 'is_resolved']
    search_fields = ['student__name', 'description']
    ordering_fields = ['occurred_at', 'created_at']


class ReferralUnitViewSet(viewsets.ModelViewSet):
    queryset = ReferralUnit.objects.filter(is_active=True)
    serializer_class = ReferralUnitSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['unit_type', 'is_active']
    search_fields = ['name', 'contact_person']
    ordering_fields = ['name', 'created_at']


class ReferralHistoryViewSet(viewsets.ModelViewSet):
    queryset = ReferralHistory.objects.all()
    serializer_class = ReferralHistorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['referral_unit']
    search_fields = ['student__name', 'referral_unit__name', 'reason']
    ordering_fields = ['referral_date', 'created_at']


class EducationCategoryViewSet(viewsets.ModelViewSet):
    queryset = EducationCategory.objects.filter(is_active=True)
    serializer_class = EducationCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']


class EducationContentViewSet(viewsets.ModelViewSet):
    queryset = EducationContent.objects.all()
    serializer_class = EducationContentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'content_type', 'is_published']
    search_fields = ['title', 'content']
    ordering_fields = ['published_at', 'created_at', 'view_count']
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布宣教内容"""
        content = self.get_object()
        content.is_published = True
        content.published_at = datetime.now()
        content.save()
        return Response({'message': '内容已发布'})
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """取消发布宣教内容"""
        content = self.get_object()
        content.is_published = False
        content.save()
        return Response({'message': '内容已取消发布'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取宣教统计信息"""
        total = EducationContent.objects.count()
        published = EducationContent.objects.filter(is_published=True).count()
        total_views = EducationContent.objects.aggregate(total_views=models.Sum('view_count'))['total_views'] or 0
        active_categories = EducationCategory.objects.filter(is_active=True).count()
        
        serializer = EducationStatisticsSerializer({
            'total_contents': total,
            'published_contents': published,
            'total_views': total_views,
            'active_categories': active_categories
        })
        
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['published_at', 'created_at']
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布通知"""
        notification = self.get_object()
        notification.status = 'published'
        notification.published_at = datetime.now()
        notification.save()
        return Response({'message': '通知已发布'})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """关闭通知"""
        notification = self.get_object()
        notification.status = 'closed'
        notification.closed_at = datetime.now()
        notification.save()
        return Response({'message': '通知已关闭'})


class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['position', 'is_active']
    search_fields = ['title']
    ordering_fields = ['order', 'start_date']


class CounselorScheduleViewSet(viewsets.ModelViewSet):
    queryset = CounselorSchedule.objects.all()
    serializer_class = CounselorScheduleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['counselor', 'date', 'is_available']
    search_fields = ['counselor__name']
    ordering_fields = ['date', 'start_time']


class ConsultationOrderViewSet(viewsets.ModelViewSet):
    queryset = ConsultationOrder.objects.all()
    serializer_class = ConsultationOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['payment_status']
    search_fields = ['order_number', 'consultation__client__name']
    ordering_fields = ['created_at', 'paid_at']