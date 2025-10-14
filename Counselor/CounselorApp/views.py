from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Avg
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, UpdateAPIView
from .models import Counselor, Consultation, Schedule, Review
from .serializers import (
    CounselorSerializer, ConsultationSerializer, ScheduleSerializer,
    ReviewSerializer, DashboardStatsSerializer, BulkScheduleSerializer,
    ServiceTypesSerializer
)


class CounselorPermission(permissions.BasePermission):
    """确保只有咨询师可以访问这些视图"""

    def has_permission(self, request, view):
        return hasattr(request.user, 'counselor') and request.user.counselor.is_active


class DashboardView(APIView):
    """首页视图"""
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get(self, request):
        # 这里可以返回HTML模板或重定向到前端页面
        return Response({
            "message": "欢迎访问咨询师工作台",
            "user": request.user.username,
            "counselor": request.user.counselor.name
        })


class DashboardStatsView(APIView):
    """数据看板统计接口"""
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get(self, request):
        counselor = request.user.counselor
        today = timezone.now().date()

        # 今日咨询统计
        today_consultations = Consultation.objects.filter(
            counselor=counselor,
            scheduled_at__date=today
        )

        # 年度咨询统计
        current_year = timezone.now().year
        yearly_consultations = Consultation.objects.filter(
            counselor=counselor,
            scheduled_at__year=current_year
        )

        # 咨询类型占比
        type_stats = yearly_consultations.values('type').annotate(
            count=Count('id')
        ).order_by('-count')

        # 客户性别占比
        gender_stats = yearly_consultations.values('client__gender').annotate(
            count=Count('id')
        )

        # 客户年龄分布
        age_stats = yearly_consultations.values('client__age').annotate(
            count=Count('id')
        ).order_by('client__age')

        stats_data = {
            "today_stats": {
                "total": today_consultations.count(),
                "pending": today_consultations.filter(status='pending').count(),
                "in_progress": today_consultations.filter(status='in_progress').count(),
                "completed": today_consultations.filter(status='completed').count(),
            },
            "yearly_total": yearly_consultations.count(),
            "type_distribution": list(type_stats),
            "gender_distribution": list(gender_stats),
            "age_distribution": list(age_stats),
            "average_rating": counselor.reviews.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
        }

        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data)


class ConsultationViewSet(viewsets.ModelViewSet):
    """咨询会话视图集"""
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_queryset(self):
        counselor = self.request.user.counselor
        return Consultation.objects.filter(counselor=counselor).select_related('client')

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """接受咨询"""
        consultation = self.get_object()
        if consultation.status != 'pending':
            return Response(
                {"error": "只能接受待接单的咨询"},
                status=status.HTTP_400_BAD_REQUEST
            )

        consultation.status = 'in_progress'
        consultation.started_at = timezone.now()
        consultation.save()

        return Response({"message": "咨询已接受"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝咨询"""
        consultation = self.get_object()
        if consultation.status != 'pending':
            return Response(
                {"error": "只能拒绝待接单的咨询"},
                status=status.HTTP_400_BAD_REQUEST
            )

        consultation.status = 'rejected'
        consultation.save()

        return Response({"message": "咨询已拒绝"})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成咨询"""
        consultation = self.get_object()
        if consultation.status != 'in_progress':
            return Response(
                {"error": "只能完成进行中的咨询"},
                status=status.HTTP_400_BAD_REQUEST
            )

        consultation.status = 'completed'
        consultation.ended_at = timezone.now()
        consultation.save()

        return Response({"message": "咨询已完成"})


class PendingConsultationListView(ListAPIView):
    """待接单咨询列表"""
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_queryset(self):
        counselor = self.request.user.counselor
        return Consultation.objects.filter(
            counselor=counselor,
            status='pending'
        ).select_related('client').order_by('scheduled_at')


class InProgressConsultationListView(ListAPIView):
    """咨询中列表"""
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_queryset(self):
        counselor = self.request.user.counselor
        return Consultation.objects.filter(
            counselor=counselor,
            status='in_progress'
        ).select_related('client').order_by('scheduled_at')


class CompletedConsultationListView(ListAPIView):
    """已结束咨询列表"""
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_queryset(self):
        counselor = self.request.user.counselor
        return Consultation.objects.filter(
            counselor=counselor,
            status='completed'
        ).select_related('client').order_by('-ended_at')


class RejectedConsultationListView(ListAPIView):
    """已拒绝咨询列表"""
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_queryset(self):
        counselor = self.request.user.counselor
        return Consultation.objects.filter(
            counselor=counselor,
            status='rejected'
        ).select_related('client').order_by('-scheduled_at')


class ScheduleViewSet(viewsets.ModelViewSet):
    """排班管理视图集"""
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_queryset(self):
        counselor = self.request.user.counselor
        return Schedule.objects.filter(counselor=counselor).order_by('date', 'start_time')

    def perform_create(self, serializer):
        serializer.save(counselor=self.request.user.counselor)


class BulkCreateScheduleView(APIView):
    """批量创建排班"""
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def post(self, request):
        serializer = BulkScheduleSerializer(data=request.data)
        if serializer.is_valid():
            schedules = serializer.save(counselor=request.user.counselor)
            return Response({
                "message": f"成功创建 {len(schedules)} 个排班",
                "schedules": ScheduleSerializer(schedules, many=True).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StopServiceView(APIView):
    """添加停诊安排"""
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def post(self, request):
        counselor = request.user.counselor
        date = request.data.get('date')
        reason = request.data.get('reason', '')

        if not date:
            return Response(
                {"error": "请提供停诊日期"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 停诊当天的所有排班
        schedules = Schedule.objects.filter(
            counselor=counselor,
            date=date,
            is_available=True
        )

        updated_count = schedules.update(is_available=False, reason=reason)

        return Response({
            "message": f"已停诊 {updated_count} 个排班",
            "date": date,
            "reason": reason
        })


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """评论管理视图集（只读）"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_queryset(self):
        counselor = self.request.user.counselor
        return Review.objects.filter(counselor=counselor).select_related('client')


class CounselorProfileView(RetrieveUpdateAPIView):
    """咨询师个人资料"""
    serializer_class = CounselorSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_object(self):
        return self.request.user.counselor


from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, UpdateAPIView


# ... 其他已有的代码 ...

class UpdateProfileView(RetrieveUpdateAPIView):
    """更新个人资料"""
    serializer_class = CounselorSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_object(self):
        return self.request.user.counselor


class UpdateServiceTypesView(UpdateAPIView):
    """更新服务类型配置"""
    serializer_class = ServiceTypesSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_object(self):
        return self.request.user.counselor


# 如果还缺少其他视图类，也一并添加：

class UpdateProfileView(RetrieveUpdateAPIView):
    """更新个人资料"""
    serializer_class = CounselorSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_object(self):
        return self.request.user.counselor


class UpdateServiceTypesView(UpdateAPIView):
    """更新服务类型配置"""
    serializer_class = ServiceTypesSerializer
    permission_classes = [permissions.IsAuthenticated, CounselorPermission]

    def get_object(self):
        return self.request.user.counselor