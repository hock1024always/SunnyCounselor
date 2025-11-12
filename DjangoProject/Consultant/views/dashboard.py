"""
仪表盘相关视图 - 函数式视图
所有接口使用POST方法，参数和鉴权都在请求体JSON中
"""
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from Consultant.models import ConsultationOrder, ConsultationRecord
from Consultant.utils import require_body_auth


# ==================== 仪表盘 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def today_transactions(request):
    """POST 获取今日咨询交易情况"""
    counselor = request.counselor
    today = timezone.now().date()
    
    # 查询今日订单
    orders = ConsultationOrder.objects.filter(
        counselor=counselor,
        appointment_date=today,
        status__in=['accepted', 'completed']
    )
    
    count = orders.count()
    # 假设每个订单金额为固定值，这里可以根据实际业务逻辑调整
    amount = count * 100  # 假设每个订单100元
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': {
            'count': count,
            'amount': amount
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def category_data(request):
    """POST 获取咨询类别占比数据"""
    counselor = request.counselor
    
    # 统计在线和线下咨询数量
    online_count = ConsultationOrder.objects.filter(
        counselor=counselor,
        service_type='online'
    ).count()
    
    offline_count = ConsultationOrder.objects.filter(
        counselor=counselor,
        service_type='offline'
    ).count()
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': {
            'online': online_count,
            'outline': offline_count
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def yearly_consultations(request):
    """POST 获取年度咨询量数据"""
    counselor = request.counselor
    current_year = timezone.now().year
    
    # 统计年度总咨询量（按人数计算）
    total = ConsultationRecord.objects.filter(
        counselor=counselor,
        created_time__year=current_year
    ).count()
    
    # 统计每月咨询量
    monthly_data = [0] * 12
    for month in range(1, 13):
        count = ConsultationRecord.objects.filter(
            counselor=counselor,
            created_time__year=current_year,
            created_time__month=month
        ).count()
        monthly_data[month - 1] = count
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': {
            'total': total,
            'data': monthly_data
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def time_slot_data(request):
    """POST 获取时段预约趋势数据"""
    counselor = request.counselor
    
    # 获取最近30天的数据
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    orders = ConsultationOrder.objects.filter(
        counselor=counselor,
        appointment_date__gte=start_date,
        appointment_date__lte=end_date
    )
    
    # 统计各时段的预约数量
    # 这里简化处理，实际应该根据time_slot字段进行分组统计
    time_slots = []
    appointments = []
    
    # 假设时间段为8:00-20:00，每小时一个时段
    for hour in range(8, 21):
        time_slots.append(hour)
        count = orders.filter(time_slot__contains=str(hour)).count()
        appointments.append(count)
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': {
            'timeSlots': time_slots,
            'appointments': appointments
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def gender_data(request):
    """POST 获取用户性别分布数据"""
    counselor = request.counselor
    
    # 统计性别分布
    male_count = ConsultationRecord.objects.filter(
        counselor=counselor,
        gender='男'
    ).count()
    
    female_count = ConsultationRecord.objects.filter(
        counselor=counselor,
        gender='女'
    ).count()
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': {
            'male': male_count,
            'female': female_count
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def age_data(request):
    """POST 获取用户年龄分布数据"""
    counselor = request.counselor
    
    records = ConsultationRecord.objects.filter(counselor=counselor).exclude(age__isnull=True)
    
    # 年龄段划分：["1-17", "18-25", "26-35", "36-45", "46-55", "55+"]
    age_ranges = [
        (1, 17),
        (18, 25),
        (26, 35),
        (36, 45),
        (46, 55),
        (56, 200)  # 55+
    ]
    
    values = []
    for min_age, max_age in age_ranges:
        if max_age == 200:
            count = records.filter(age__gte=min_age).count()
        else:
            count = records.filter(age__gte=min_age, age__lte=max_age).count()
        values.append(count)
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': {
            'values': values
        }
    })

