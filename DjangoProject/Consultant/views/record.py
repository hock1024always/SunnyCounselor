"""
咨询档案相关视图 - 函数式视图
所有接口使用POST方法，参数和鉴权都在请求体JSON中
"""
import uuid
import os
import time
import io
import zipfile
import mimetypes
import pandas as pd
from datetime import datetime
from django.db.models import Q, Max
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import FileResponse, HttpResponse

from Consultant.models import ConsultationRecord, ConsultationSession, FileStorage
from Consultant.serializers.record import (
    ConsultationRecordListSerializer,
    ConsultationRecordCreateSerializer,
    ConsultationSessionDetailSerializer,
    ConsultationSessionCreateSerializer
)
from Consultant.utils import require_body_auth
import json


# ==================== 咨询档案 ====================

def _convert_crisis_status_to_string(crisis_status):
    """将危机状态数组转换为字符串存储"""
    if not crisis_status:
        return ''
    if isinstance(crisis_status, list):
        # 过滤空值并转换为字符串
        filtered = [str(s).strip() for s in crisis_status if s and str(s).strip()]
        if filtered:
            # 使用JSON格式存储，便于后续解析
            return json.dumps(filtered, ensure_ascii=False)
        return ''
    # 如果已经是字符串，直接返回
    return str(crisis_status) if crisis_status else ''

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def record_list(request):
    """POST 获取咨询档案列表"""
    counselor = request.counselor
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({
            'code': 400,
            'message': '分页参数错误'
        }, status=status.HTTP_400_BAD_REQUEST)
    std_name = data.get('std_name', '')
    std_grade = data.get('std_grade', '')
    std_class = data.get('std_class', '')
    std_school = data.get('std_school', '')
    interview_count = data.get('interview_count', '')
    interview_status = data.get('interview_status', '')
    interview_type = data.get('interview_type', '')
    doctor_evaluation = data.get('doctor_evaluation', '')
    follow_up_plan = data.get('follow_up_plan', '')
    
    # 构建查询
    queryset = ConsultationRecord.objects.filter(counselor=counselor)
    
    # 筛选条件
    if std_name:
        queryset = queryset.filter(client_name__icontains=std_name)
    if std_grade:
        queryset = queryset.filter(grade__icontains=std_grade)
    if std_class:
        queryset = queryset.filter(class_name__icontains=std_class)
    if std_school:
        queryset = queryset.filter(school__icontains=std_school)
    if interview_count:
        queryset = queryset.filter(interview_count=int(interview_count))
    if interview_status:
        status_map = {
            '进行中': 'active',
            '已完成': 'completed',
            '已关闭': 'closed'
        }
        mapped_status = status_map.get(interview_status, interview_status)
        queryset = queryset.filter(current_status=mapped_status)
    
    # 排序
    queryset = queryset.order_by('-created_time')
    
    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    records = queryset[start:end]
    
    serializer = ConsultationRecordListSerializer(records, many=True)
    
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
def record_create(request):
    """POST 创建一条访谈/档案记录"""
    counselor = request.counselor
    serializer = ConsultationRecordCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'code': 400,
            'message': '参数错误',
            'detail': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # 创建档案
    record = ConsultationRecord.objects.create(
        record_no=f'RC{uuid.uuid4().hex[:12].upper()}',
        client_name=data.get('std_name'),
        grade=data.get('std_grade', ''),
        class_name=data.get('std_class', ''),
        school=data.get('std_school', ''),
        counselor=counselor,
        created_by=counselor,
        interview_count=int(data.get('interview_count', 0)),
        interview_type=data.get('interview_type', ''),
        current_status='active' if data.get('interview_status') == '进行中' else 'completed',
        client_type='student',
        gender='男'  # 默认值
    )
    
    # 如果传入了 doctor_evaluation 或 follow_up_plan，创建第一条会话记录
    doctor_evaluation = data.get('doctor_evaluation', '')
    follow_up_plan = data.get('follow_up_plan', '')
    
    if doctor_evaluation or follow_up_plan:
        ConsultationSession.objects.create(
            record=record,
            session_number=1,
            interview_date=timezone.now().date(),
            interview_time='',
            visit_status='completed',
            doctor_evaluation=doctor_evaluation,
            follow_up_plan=follow_up_plan,
            consultant_name=counselor.name,
            created_by=counselor
        )
    
    return Response({
        'code': 0,
        'message': '创建成功'
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def record_delete(request):
    """POST 删除一条访谈/档案记录"""
    counselor = request.counselor
    record_id = request.data.get('id')
    
    if not record_id:
        return Response({
            'code': 400,
            'message': '缺少档案ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        record = ConsultationRecord.objects.get(id=record_id, counselor=counselor)
        # 删除档案会级联删除所有会话
        record.delete()
        
        return Response({
            'code': 0,
            'message': '删除成功'
        })
    except ConsultationRecord.DoesNotExist:
        return Response({
            'code': 404,
            'message': '档案不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def record_profile(request):
    """
    POST 获取咨询档案的详细咨询记录
    业务逻辑鉴权：确保只能访问自己的档案
    """
    counselor = request.counselor
    record_id = request.data.get('id')
    
    if not record_id:
        return Response({
            'code': 400,
            'message': '缺少档案ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 业务逻辑鉴权：确保档案属于当前咨询师
        record = ConsultationRecord.objects.get(id=record_id, counselor=counselor)
        sessions = record.sessions.all().order_by('session_number')
        
        serializer = ConsultationSessionDetailSerializer(sessions, many=True)
        
        return Response({
            'code': 0,
            'message': '获取成功',
            'data': serializer.data
        })
    except ConsultationRecord.DoesNotExist:
        # 可能是档案不存在，也可能是无权访问（返回相同错误避免信息泄露）
        return Response({
            'code': 404,
            'message': '档案不存在或无权访问'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def session_create(request):
    """
    POST 新建一条咨询记录
    业务逻辑鉴权：确保只能为自己的档案创建会话
    支持 JSON 和 form-data 两种格式
    """
    import os
    import time
    from django.conf import settings
    
    counselor = request.counselor
    
    # 支持 form-data 和 JSON 两种格式
    # 如果是 form-data，需要从 request.data 中获取文本字段，从 request.FILES 中获取文件
    data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
    
    # 处理 form-data 中的数组字段（如 crisisStatus）
    # 在 form-data 中，数组可能以 JSON 字符串形式传递
    if 'crisisStatus' in data:
        crisis_status_value = data.get('crisisStatus')
        if isinstance(crisis_status_value, str):
            try:
                # 尝试解析 JSON 字符串
                crisis_status_value = json.loads(crisis_status_value)
            except (json.JSONDecodeError, TypeError):
                # 如果不是 JSON，尝试按逗号分隔
                if ',' in crisis_status_value:
                    crisis_status_value = [s.strip() for s in crisis_status_value.split(',') if s.strip()]
                else:
                    crisis_status_value = [crisis_status_value] if crisis_status_value else []
        data['crisisStatus'] = crisis_status_value if isinstance(crisis_status_value, list) else []
    
    # 处理 attachImages（如果是 JSON 字符串）
    if 'attachImages' in data and isinstance(data.get('attachImages'), str):
        try:
            data['attachImages'] = json.loads(data.get('attachImages'))
        except (json.JSONDecodeError, TypeError):
            data['attachImages'] = []
    
    # 验证数据（使用序列化器验证非文件字段）
    serializer = ConsultationSessionCreateSerializer(data=data)
    
    if not serializer.is_valid():
        return Response({
            'code': 400,
            'message': '参数错误',
            'detail': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    record_id = validated_data.get('record_id')
    
    if not record_id:
        return Response({
            'code': 400,
            'message': '缺少档案ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 业务逻辑鉴权：确保档案属于当前咨询师
        record = ConsultationRecord.objects.get(id=record_id, counselor=counselor)
        
        # 获取下一个会话编号
        max_session = record.sessions.aggregate(Max('session_number'))
        next_number = (max_session['session_number__max'] or 0) + 1
        
        # 处理签名图片文件上传
        signature_image = ''
        if 'signatureImage' in request.FILES:
            uploaded_file = request.FILES['signatureImage']
            # 检查文件类型（图片格式）
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in allowed_extensions:
                return Response({
                    'code': 400,
                    'message': '签名图片格式不支持，请上传jpg、png、gif、bmp或webp格式的图片'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 确保目录存在
            signature_dir = os.path.join(settings.BASE_DIR, 'static', 'session_signature')
            os.makedirs(signature_dir, exist_ok=True)
            
            # 生成唯一文件名
            timestamp = int(time.time() * 1000)
            file_name = f"signature_{record_id}_{timestamp}{file_ext}"
            
            # 保存文件
            file_path = os.path.join(signature_dir, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # 保存相对路径到数据库（相对于static目录）
            signature_image = f"session_signature/{file_name}"
        elif 'signatureImage' in validated_data:
            signature_image = validated_data.get('signatureImage', '')
        
        # 处理附加图片文件上传（支持多个文件）
        attach_images = []
        if 'attachImages' in request.FILES:
            uploaded_files = request.FILES.getlist('attachImages')
            
            # 确保目录存在
            attach_dir = os.path.join(settings.BASE_DIR, 'static', 'session_attach')
            os.makedirs(attach_dir, exist_ok=True)
            
            for index, uploaded_file in enumerate(uploaded_files):
                # 检查文件类型（图片格式）
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                if file_ext not in allowed_extensions:
                    # 如果格式不支持，跳过这个文件
                    continue
                
                # 生成唯一文件名
                timestamp = int(time.time() * 1000)
                file_name = f"attach_{record_id}_{timestamp}_{index + 1}{file_ext}"
                
                # 保存文件
                file_path = os.path.join(attach_dir, file_name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # 保存相对路径（相对于static目录）
                attach_images.append(f"session_attach/{file_name}")
        elif 'attachImages' in validated_data:
            attach_images = validated_data.get('attachImages', [])
        
        # 创建会话
        session = ConsultationSession.objects.create(
            record=record,
            session_number=next_number,
            interview_date=validated_data.get('date') or timezone.now().date(),
            interview_time=validated_data.get('time', ''),
            duration=int(validated_data.get('duration', 0)) if validated_data.get('duration') and str(validated_data.get('duration')).isdigit() else None,
            visit_status=validated_data.get('visitStatus', 'scheduled'),
            objective_description=validated_data.get('description', ''),
            doctor_evaluation=validated_data.get('doctorEvaluation', ''),
            follow_up_plan=validated_data.get('followUpPlan', ''),
            next_visit_plan=validated_data.get('nextVisitPlan', ''),
            crisis_status=_convert_crisis_status_to_string(validated_data.get('crisisStatus', [])),
            consultant_name=validated_data.get('consultantName', counselor.name),
            is_third_party_evaluation=validated_data.get('isThirdPartyEvaluation', False),
            signature_image=signature_image,
            attach_images=attach_images,
            created_by=counselor
        )
        
        # 更新档案的访谈次数
        record.interview_count = next_number
        record.save(update_fields=['interview_count'])
        
        return Response({
            'code': 0,
            'message': '创建成功'
        })
    except ConsultationRecord.DoesNotExist:
        # 可能是档案不存在，也可能是无权访问（返回相同错误避免信息泄露）
        return Response({
            'code': 404,
            'message': '档案不存在或无权访问'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'创建失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def session_update(request):
    """
    POST 更新一条咨询记录
    业务逻辑鉴权：确保只能更新自己创建的会话，且会话所属的档案也属于当前咨询师
    """
    counselor = request.counselor
    session_id = request.data.get('id')
    
    if not session_id:
        return Response({
            'code': 400,
            'message': '缺少会话ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 业务逻辑鉴权：确保会话是由当前咨询师创建的，且所属档案也属于当前咨询师
        session = ConsultationSession.objects.select_related('record').get(
            id=session_id,
            created_by=counselor,
            record__counselor=counselor  # 双重验证：确保档案也属于当前咨询师
        )
        
        # 支持 form-data 和 JSON 两种格式
        # 如果是 form-data，需要从 request.data 中获取文本字段，从 request.FILES 中获取文件
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # 处理 form-data 中的数组字段（如 crisisStatus）
        # 在 form-data 中，数组可能以 JSON 字符串形式传递
        if 'crisisStatus' in data:
            crisis_status_value = data.get('crisisStatus')
            if isinstance(crisis_status_value, str):
                try:
                    # 尝试解析 JSON 字符串
                    crisis_status_value = json.loads(crisis_status_value)
                except (json.JSONDecodeError, TypeError):
                    # 如果不是 JSON，尝试按逗号分隔
                    if ',' in crisis_status_value:
                        crisis_status_value = [s.strip() for s in crisis_status_value.split(',') if s.strip()]
                    else:
                        crisis_status_value = [crisis_status_value] if crisis_status_value else []
            data['crisisStatus'] = crisis_status_value if isinstance(crisis_status_value, list) else []
        
        # 更新字段
        if 'visitStatus' in data:
            session.visit_status = data.get('visitStatus')
        if 'description' in data:
            session.objective_description = data.get('description')
        if 'doctorEvaluation' in data:
            session.doctor_evaluation = data.get('doctorEvaluation')
        if 'followUpPlan' in data:
            session.follow_up_plan = data.get('followUpPlan')
        if 'nextVisitPlan' in data:
            session.next_visit_plan = data.get('nextVisitPlan')
        if 'crisisStatus' in data:
            session.crisis_status = _convert_crisis_status_to_string(data.get('crisisStatus', []))
        if 'consultantName' in data:
            session.consultant_name = data.get('consultantName')
        if 'isThirdPartyEvaluation' in data:
            session.is_third_party_evaluation = data.get('isThirdPartyEvaluation')
        # 处理签名图片文件上传（如果上传了新文件）
        if 'signatureImage' in request.FILES:
            import os
            import time
            from django.conf import settings
            
            # 删除旧文件（如果存在）
            if session.signature_image:
                old_file_path = os.path.join(settings.BASE_DIR, 'static', session.signature_image)
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except Exception:
                        pass  # 如果删除失败，继续处理新文件
            
            # 处理新文件上传
            uploaded_file = request.FILES['signatureImage']
            # 检查文件类型（图片格式）
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in allowed_extensions:
                return Response({
                    'code': 400,
                    'message': '签名图片格式不支持，请上传jpg、png、gif、bmp或webp格式的图片'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 确保目录存在
            signature_dir = os.path.join(settings.BASE_DIR, 'static', 'session_signature')
            os.makedirs(signature_dir, exist_ok=True)
            
            # 生成唯一文件名
            timestamp = int(time.time() * 1000)
            record_id = session.record.id
            file_name = f"signature_{record_id}_{timestamp}{file_ext}"
            
            # 保存文件
            file_path = os.path.join(signature_dir, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # 更新相对路径到数据库（相对于static目录）
            session.signature_image = f"session_signature/{file_name}"
        elif 'signatureImage' in data:
            # 如果只是字符串路径，直接更新
            session.signature_image = data.get('signatureImage')
        
        # 处理附加图片文件上传（如果上传了新文件，支持多个文件）
        if 'attachImages' in request.FILES:
            import os
            import time
            from django.conf import settings
            
            # 删除旧文件（如果存在）
            if session.attach_images and isinstance(session.attach_images, list):
                for old_image_path in session.attach_images:
                    if old_image_path:
                        old_file_path = os.path.join(settings.BASE_DIR, 'static', old_image_path)
                        if os.path.exists(old_file_path):
                            try:
                                os.remove(old_file_path)
                            except Exception:
                                pass  # 如果删除失败，继续处理新文件
            
            # 处理新文件上传
            uploaded_files = request.FILES.getlist('attachImages')
            
            # 确保目录存在
            attach_dir = os.path.join(settings.BASE_DIR, 'static', 'session_attach')
            os.makedirs(attach_dir, exist_ok=True)
            
            attach_images = []
            for index, uploaded_file in enumerate(uploaded_files):
                # 检查文件类型（图片格式）
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                if file_ext not in allowed_extensions:
                    # 如果格式不支持，跳过这个文件
                    continue
                
                # 生成唯一文件名
                timestamp = int(time.time() * 1000)
                record_id = session.record.id
                file_name = f"attach_{record_id}_{timestamp}_{index + 1}{file_ext}"
                
                # 保存文件
                file_path = os.path.join(attach_dir, file_name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # 保存相对路径（相对于static目录）
                attach_images.append(f"session_attach/{file_name}")
            
            # 更新附加图片路径数组
            if attach_images:
                session.attach_images = attach_images
        elif 'attachImages' in data:
            # 如果只是数组路径，直接更新
            session.attach_images = data.get('attachImages', [])
        
        session.save()
        
        return Response({
            'code': 0,
            'message': '更新成功'
        })
    except ConsultationSession.DoesNotExist:
        # 可能是会话不存在，也可能是无权访问（返回相同错误避免信息泄露）
        return Response({
            'code': 404,
            'message': '会话不存在或无权访问'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def personal_profile(request):
    """
    POST 获取个人档案
    业务逻辑鉴权：确保只能访问自己的档案
    """
    counselor = request.counselor
    record_id = request.data.get('id')
    
    if not record_id:
        return Response({
            'code': 400,
            'message': '缺少档案ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 业务逻辑鉴权：确保档案属于当前咨询师
        record = ConsultationRecord.objects.get(id=record_id, counselor=counselor)
        
        # 构建紧急联系人信息
        emergency_contact = {}
        if record.emergency_contact_name:
            emergency_contact = {
                'name': record.emergency_contact_name,
                'relationship': '',  # 关系字段在模型中不存在，返回空
                'phone': record.emergency_contact_phone or ''
            }
        
        return Response({
            'code': 0,
            'message': '获取成功',
            'data': {
                'name': record.client_name,
                'id': str(record.id),
                'gender': record.gender,
                'age': str(record.age) if record.age else '',
                'education': record.education or '',
                'occupation': record.occupation or '',
                'maritalStatus': '',  # 模型中不存在，返回空
                'contact': record.contact or '',
                'emergencyContact': emergency_contact,
                'referral': record.referral_source or '',
                'complaint': record.main_complaint or '',
                'goal': record.consultation_goal or ''
            }
        })
    except ConsultationRecord.DoesNotExist:
        # 可能是档案不存在，也可能是无权访问（返回相同错误避免信息泄露）
        return Response({
            'code': 404,
            'message': '档案不存在或无权访问'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def upload_records(request):
    """
    POST 上传访谈记录文件
    解析Excel文件并导入ConsultationRecord和ConsultationSession数据
    """
    counselor = request.counselor
    uploaded_file = request.FILES.get('files') or request.FILES.get('file')
    
    if not uploaded_file:
        return Response({
            'code': 400,
            'message': '请上传Excel文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查文件扩展名
    file_name = uploaded_file.name
    if not (file_name.endswith('.xls') or file_name.endswith('.xlsx')):
        return Response({
            'code': 400,
            'message': '只支持.xls或.xlsx格式的Excel文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 确保upload目录存在
        upload_dir = os.path.join(settings.BASE_DIR, 'static', 'interview_upload')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = int(time.time() * 1000)
        file_ext = os.path.splitext(file_name)[1]
        unique_filename = f"{timestamp}_{file_name}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # 读取Excel文件
        try:
            df = pd.read_excel(file_path, engine='openpyxl' if file_ext == '.xlsx' else None)
        except Exception as e:
            return Response({
                'code': 400,
                'message': f'Excel文件读取失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 定义Excel列名映射（支持中英文列名）
        column_mapping = {
            # 档案基本信息
            '来访者姓名': 'client_name',
            '姓名': 'client_name',
            'client_name': 'client_name',
            '来访者类型': 'client_type',
            'client_type': 'client_type',
            '性别': 'gender',
            'gender': 'gender',
            '年龄': 'age',
            'age': 'age',
            '学籍号': 'student_id',
            'student_id': 'student_id',
            '学校': 'school',
            'school': 'school',
            '年级': 'grade',
            'grade': 'grade',
            '班级': 'class_name',
            'class_name': 'class_name',
            '教育程度': 'education',
            'education': 'education',
            '职业': 'occupation',
            'occupation': 'occupation',
            '联系方式': 'contact',
            'contact': 'contact',
            '紧急联系人姓名': 'emergency_contact_name',
            'emergency_contact_name': 'emergency_contact_name',
            '紧急联系人电话': 'emergency_contact_phone',
            'emergency_contact_phone': 'emergency_contact_phone',
            '咨询来源': 'referral_source',
            'referral_source': 'referral_source',
            '主诉问题': 'main_complaint',
            'main_complaint': 'main_complaint',
            '咨询目标': 'consultation_goal',
            'consultation_goal': 'consultation_goal',
            '访谈次数': 'interview_count',
            'interview_count': 'interview_count',
            '档案状态': 'current_status',
            'current_status': 'current_status',
            # 访谈详情
            '访谈日期': 'interview_date',
            'interview_date': 'interview_date',
            '访谈时间': 'interview_time',
            'interview_time': 'interview_time',
            '访谈时长': 'duration',
            'duration': 'duration',
            '访谈状态': 'visit_status',
            'visit_status': 'visit_status',
            '客观描述': 'objective_description',
            'objective_description': 'objective_description',
            '医生评定': 'doctor_evaluation',
            'doctor_evaluation': 'doctor_evaluation',
            '后续计划': 'follow_up_plan',
            'follow_up_plan': 'follow_up_plan',
            '下次访谈计划': 'next_visit_plan',
            'next_visit_plan': 'next_visit_plan',
            '危机状态': 'crisis_status',
            'crisis_status': 'crisis_status',
            '咨询师姓名': 'consultant_name',
            'consultant_name': 'consultant_name',
        }
        
        # 标准化列名
        df.columns = [column_mapping.get(str(col).strip(), str(col).strip()) for col in df.columns]
        
        # 检查必要的列是否存在
        if 'client_name' not in df.columns:
            name_cols = [col for col in df.columns if '姓名' in col or 'name' in col.lower()]
            if not name_cols:
                return Response({
                    'code': 400,
                    'message': 'Excel文件中必须包含"来访者姓名"或"姓名"列'
                }, status=status.HTTP_400_BAD_REQUEST)
            df = df.rename(columns={name_cols[0]: 'client_name'})
        
        # 批量创建记录
        success_count = 0
        error_rows = []
        records_to_create = []
        sessions_to_create = []
        
        for index, row in df.iterrows():
            try:
                # 获取来访者姓名（必填）
                client_name = str(row.get('client_name', '')).strip()
                if not client_name or client_name == 'nan':
                    error_rows.append({'row': index + 2, 'error': '来访者姓名不能为空'})
                    continue
                
                # 获取其他字段
                client_type = 'student'  # 默认学生
                if pd.notna(row.get('client_type')):
                    client_type_str = str(row.get('client_type')).strip().lower()
                    if 'adult' in client_type_str or '成人' in client_type_str:
                        client_type = 'adult'
                
                gender = '男'  # 默认值
                if pd.notna(row.get('gender')):
                    gender_str = str(row.get('gender')).strip()
                    if gender_str in ['男', '女', 'male', 'female']:
                        gender = '男' if gender_str in ['男', 'male'] else '女'
                
                age = None
                if pd.notna(row.get('age')):
                    try:
                        age = int(float(row.get('age')))
                    except:
                        pass
                
                # 创建或获取档案记录
                record, created = ConsultationRecord.objects.get_or_create(
                    client_name=client_name,
                    counselor=counselor,
                    defaults={
                        'record_no': f'RC{uuid.uuid4().hex[:12].upper()}',
                        'client_type': client_type,
                        'gender': gender,
                        'age': age,
                        'student_id': str(row.get('student_id', '')).strip() if pd.notna(row.get('student_id')) else '',
                        'school': str(row.get('school', '')).strip() if pd.notna(row.get('school')) else '',
                        'grade': str(row.get('grade', '')).strip() if pd.notna(row.get('grade')) else '',
                        'class_name': str(row.get('class_name', '')).strip() if pd.notna(row.get('class_name')) else '',
                        'education': str(row.get('education', '')).strip() if pd.notna(row.get('education')) else '',
                        'occupation': str(row.get('occupation', '')).strip() if pd.notna(row.get('occupation')) else '',
                        'contact': str(row.get('contact', '')).strip() if pd.notna(row.get('contact')) else '',
                        'emergency_contact_name': str(row.get('emergency_contact_name', '')).strip() if pd.notna(row.get('emergency_contact_name')) else '',
                        'emergency_contact_phone': str(row.get('emergency_contact_phone', '')).strip() if pd.notna(row.get('emergency_contact_phone')) else '',
                        'referral_source': str(row.get('referral_source', '')).strip() if pd.notna(row.get('referral_source')) else '',
                        'main_complaint': str(row.get('main_complaint', '')).strip() if pd.notna(row.get('main_complaint')) else '',
                        'consultation_goal': str(row.get('consultation_goal', '')).strip() if pd.notna(row.get('consultation_goal')) else '',
                        'interview_count': int(float(row.get('interview_count', 0))) if pd.notna(row.get('interview_count')) else 0,
                        'current_status': 'active',
                        'created_by': counselor
                    }
                )
                
                # 如果有访谈详情信息，创建访谈记录
                if pd.notna(row.get('interview_date')):
                    try:
                        # 解析访谈日期
                        if isinstance(row.get('interview_date'), pd.Timestamp):
                            interview_date = row.get('interview_date').date()
                        elif isinstance(row.get('interview_date'), datetime):
                            interview_date = row.get('interview_date').date()
                        else:
                            interview_date = pd.to_datetime(str(row.get('interview_date'))).date()
                        
                        # 获取下一个会话编号
                        max_session = record.sessions.aggregate(Max('session_number'))
                        next_number = (max_session['session_number__max'] or 0) + 1
                        
                        # 解析访谈时长
                        duration = None
                        if pd.notna(row.get('duration')):
                            try:
                                duration = int(float(row.get('duration')))
                            except:
                                pass
                        
                        sessions_to_create.append(
                            ConsultationSession(
                                record=record,
                                session_number=next_number,
                                interview_date=interview_date,
                                interview_time=str(row.get('interview_time', '')).strip() if pd.notna(row.get('interview_time')) else '',
                                duration=duration,
                                visit_status='completed' if pd.notna(row.get('visit_status')) else 'scheduled',
                                objective_description=str(row.get('objective_description', '')).strip() if pd.notna(row.get('objective_description')) else '',
                                doctor_evaluation=str(row.get('doctor_evaluation', '')).strip() if pd.notna(row.get('doctor_evaluation')) else '',
                                follow_up_plan=str(row.get('follow_up_plan', '')).strip() if pd.notna(row.get('follow_up_plan')) else '',
                                next_visit_plan=str(row.get('next_visit_plan', '')).strip() if pd.notna(row.get('next_visit_plan')) else '',
                                crisis_status=str(row.get('crisis_status', '')).strip() if pd.notna(row.get('crisis_status')) else '',
                                consultant_name=str(row.get('consultant_name', counselor.name)).strip() if pd.notna(row.get('consultant_name')) else counselor.name,
                                created_by=counselor
                            )
                        )
                        
                        # 更新档案的访谈次数
                        record.interview_count = next_number
                        record.save(update_fields=['interview_count'])
                    except Exception as e:
                        error_rows.append({'row': index + 2, 'error': f'访谈详情解析失败: {str(e)}'})
                
            except Exception as e:
                error_rows.append({'row': index + 2, 'error': f'第{index + 2}行数据错误: {str(e)}'})
        
        # 批量创建访谈记录
        if sessions_to_create:
            ConsultationSession.objects.bulk_create(sessions_to_create, batch_size=100, ignore_conflicts=True)
            success_count = len(sessions_to_create)
        
        # 返回结果
        result = {
            'code': 0,
            'message': f'成功导入{success_count}条访谈记录',
            'success_count': success_count,
            'total_rows': len(df),
            'error_count': len(error_rows),
        }
        
        if error_rows:
            result['errors'] = error_rows[:10]  # 最多返回10个错误
        
        return Response(result)
        
    except Exception as e:
        return Response({
            'code': 400,
            'message': f'导入失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def upload_template(request):
    """POST 上传模板文件到templates文件夹"""
    counselor = request.counselor
    templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # 支持多个文件上传，可以是'file'或'files'字段
    uploaded_files = []
    if 'files' in request.FILES:
        files_list = request.FILES.getlist('files')
        uploaded_files.extend(files_list)
    elif 'file' in request.FILES:
        uploaded_files.append(request.FILES['file'])
    
    if not uploaded_files:
        return Response({
            'code': 400,
            'message': '请上传文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    saved_files = []
    for uploaded_file in uploaded_files:
        filename = os.path.basename(uploaded_file.name)
        save_path = os.path.join(templates_dir, filename)
        
        with open(save_path, 'wb+') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
        
        saved_files.append(filename)
    
    if len(saved_files) == 1:
        return Response({
            'code': 0,
            'message': '上传成功',
            'data': {
                'file': saved_files[0]
            }
        })
    else:
        return Response({
            'code': 0,
            'message': '上传成功',
            'data': {
                'files': saved_files,
                'count': len(saved_files)
            }
        })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def download_template(request):
    """POST 下载模板文件（单个直接返回，多个打包zip返回）"""
    counselor = request.counselor
    templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    
    filenames = request.data.get('fileNames') or request.data.get('filenames') or request.data.get('files')
    if not filenames:
        return Response({
            'code': 400,
            'message': '请提供要下载的文件名数组'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(filenames, str):
        # 逗号分隔或单字符串
        filenames = [x.strip() for x in filenames.split(',') if x.strip()]
    if not isinstance(filenames, (list, tuple)):
        return Response({
            'code': 400,
            'message': 'filenames格式错误，应为数组或逗号分隔字符串'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 过滤与规范化
    safe_names = [os.path.basename(n) for n in filenames]
    file_paths = []
    missing = []
    for name in safe_names:
        path = os.path.join(templates_dir, name)
        if os.path.isfile(path):
            file_paths.append(path)
        else:
            missing.append(name)
    
    if not file_paths:
        return Response({
            'code': 404,
            'message': '文件不存在',
            'data': {
                'missing': missing
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 单文件直接返回
    if len(file_paths) == 1:
        file_path = file_paths[0]
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        response['Content-Type'] = content_type
        return response
    
    # 多文件zip打包
    memfile = io.BytesIO()
    with zipfile.ZipFile(memfile, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in file_paths:
            zf.write(p, arcname=os.path.basename(p))
    memfile.seek(0)
    zip_name = 'templates_bundle.zip'
    resp = HttpResponse(memfile.read(), content_type='application/zip')
    resp['Content-Disposition'] = f'attachment; filename="{zip_name}"'
    if missing:
        resp['X-Missing-Files'] = ','.join(missing)
    return resp


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def template_list(request):
    """POST 查询模板文件列表（返回templates文件夹下的文件列表）"""
    counselor = request.counselor
    templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    
    if not os.path.isdir(templates_dir):
        return Response({
            'code': 0,
            'message': '获取成功',
            'data': []
        })
    
    result = []
    for name in os.listdir(templates_dir):
        path = os.path.join(templates_dir, name)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            result.append({
                'fileName': name,
                'fileSize': str(size)
            })
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': result
    })
