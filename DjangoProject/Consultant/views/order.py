"""
订单相关视图 - 函数式视图
所有接口使用POST方法，参数和鉴权都在请求体JSON中
"""
import uuid
from datetime import datetime
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from Consultant.models import ConsultationOrder, ConsultationRecord
from Consultant.serializers.order import ConsultationOrderListSerializer, ConsultationOrderCreateSerializer
from Consultant.utils import require_body_auth


# ==================== 咨询列表 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def order_list(request):
    """POST 获取咨询列表"""
    counselor = request.counselor
    data = request.data
    
    page = int(data.get('page', 1))
    page_size = int(data.get('pageSize', 10))
    name = data.get('name', '')
    date_start = data.get('date_start', '')
    date_end = data.get('date_end', '')
    service_type = data.get('type', '')
    order_status = data.get('status', '')
    
    # 构建查询
    queryset = ConsultationOrder.objects.filter(counselor=counselor)
    
    # 姓名筛选（通过关联的档案）
    if name:
        queryset = queryset.filter(record__client_name__icontains=name)
    
    # 日期范围筛选
    if date_start:
        queryset = queryset.filter(appointment_date__gte=date_start)
    if date_end:
        queryset = queryset.filter(appointment_date__lte=date_end)
    
    # 服务类型筛选
    if service_type:
        if service_type == '在线咨询':
            queryset = queryset.filter(service_type='online')
        elif service_type == '线下咨询':
            queryset = queryset.filter(service_type='offline')
    
    # 状态筛选
    if order_status:
        status_map = {
            '已结束': 'completed',
            '咨询中': 'accepted',
            '等待中': 'pending',
            '待接单': 'pending',
            '已拒绝': 'rejected'
        }
        mapped_status = status_map.get(order_status, order_status)
        queryset = queryset.filter(status=mapped_status)
    
    # 排序
    queryset = queryset.order_by('-created_time')
    
    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    orders = queryset[start:end]
    
    serializer = ConsultationOrderListSerializer(orders, many=True)
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': {
            'total': total,
            'data': serializer.data
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def order_create(request):
    """POST 新增来访/创建咨询订单"""
    counselor = request.counselor
    serializer = ConsultationOrderCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'code': 400,
            'message': '参数错误',
            'detail': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # 创建或获取咨询档案
    record, created = ConsultationRecord.objects.get_or_create(
        client_name=data.get('name'),
        counselor=counselor,
        defaults={
            'record_no': f'RC{uuid.uuid4().hex[:12].upper()}',
            'gender': data.get('gender', '男'),
            'age': int(data.get('age')) if data.get('age').isdigit() else None,
            'client_type': 'adult',  # 默认成人
            'current_status': 'active'
        }
    )
    
    # 创建订单
    order_no = f'ORD{uuid.uuid4().hex[:12].upper()}'
    order = ConsultationOrder.objects.create(
        order_no=order_no,
        record=record,
        counselor=counselor,
        service_type='online' if data.get('type') == '在线咨询' else 'offline',
        counseling_keywords=data.get('key_word', []),
        appointment_date=data.get('date'),
        time_slot=data.get('time'),
        contact_info=data.get('contact'),
        status='pending'
    )
    
    return Response({
        'code': 0,
        'message': '创建成功',
        'id': order.id
    })

