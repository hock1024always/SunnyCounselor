"""
心理咨询接口 - 函数式视图
所有接口使用POST方法，参数和鉴权都在请求体JSON中
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date
from collections import defaultdict
from django.db.models import Max
from django.utils import timezone

from CounselorAdmin.models import Appointment, Counselor, Schedule, Cancellation
from CounselorAdmin.utils import require_body_auth
from Consultant.models import CounselorProfile, ConsultationRecord, ConsultationSession, ConsultantAuthToken
from Consultant.serializers.record import ConsultationSessionDetailSerializer
import json


# ==================== 辅助函数 ====================

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


# ==================== 咨询统计 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def order_list(request):
    """POST 分页查询咨询订单记录"""
    data = request.data
    
    try:
        page = int(data.get('page', 1)) if data.get('page') else 1
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Appointment.objects.all()
    
    if data.get('name'):
        queryset = queryset.filter(client_name__icontains=data.get('name'))
    if data.get('date_start'):
        try:
            date_start = datetime.strptime(data.get('date_start'), '%Y-%m-%d').date()
            queryset = queryset.filter(appointment_date__gte=date_start)
        except:
            pass
    if data.get('date_end'):
        try:
            date_end = datetime.strptime(data.get('date_end'), '%Y-%m-%d').date()
            queryset = queryset.filter(appointment_date__lte=date_end)
        except:
            pass
    if data.get('type'):
        queryset = queryset.filter(service_type=data.get('type'))
    if data.get('status'):
        queryset = queryset.filter(status=data.get('status'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        result_data.append({
            'id': str(item.id),
            'order_id': item.order_no,
            'name': item.client_name,
            'gender': item.client_gender or '',
            'age': str(item.client_age) if item.client_age else '',
            'type': item.service_type or '',
            'key_word': item.counseling_keywords or '',
            'date': item.appointment_date.strftime('%Y-%m-%d') if item.appointment_date else '',
            'time': item.time_slot or '',
            'commit_time': item.submit_time.strftime('%Y-%m-%d %H:%M:%S') if item.submit_time else '',
            'finish_time': item.end_time.strftime('%Y-%m-%d %H:%M:%S') if item.end_time else '',
            'status': item.status or '未开始',  # 状态：未开始、进行中、已完成
            'contact': item.contact or '',  # 联系方式字段
        })
    
    return Response({'message': '查询成功', 'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def order_create(request):
    """POST 创建一条咨询订单"""
    data = request.data
    
    try:
        import uuid
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8]}"
        
        obj = Appointment.objects.create(
            order_no=order_no,
            client_name=data.get('name'),
            client_gender=data.get('gender'),
            client_age=int(data.get('age', 0)) if data.get('age') else None,
            service_type=data.get('type', ''),
            counseling_keywords=data.get('key_word', ''),
            appointment_date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else None,
            time_slot=data.get('time', ''),
            status='未开始',
        )
        return Response({'id': str(obj.id), 'message': '创建成功'})
    except Exception as e:
        return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 咨询师管理 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def consultants_list(request):
    """POST 分页查询咨询师信息表"""
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Counselor.objects.all()
    
    if data.get('name'):
        queryset = queryset.filter(name__icontains=data.get('name'))
    if data.get('phone'):
        queryset = queryset.filter(phone__icontains=data.get('phone'))
    if data.get('status'):
        queryset = queryset.filter(status=data.get('status'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        # 获取咨询师详情
        try:
            profile = item.profile
        except CounselorProfile.DoesNotExist:
            profile = None
        
        # 构建返回数据
        result_item = {
            'id': str(item.id),
            'name': profile.name if profile else item.name,
            'graduated_school': profile.graduated_school if profile else '',
            'address': profile.address if profile else '',
            'organization': profile.organization if profile else (item.organization or ''),
            'profession': profile.profession if profile else '',
            'expertise': profile.expertise if profile and profile.expertise else [],
            'introduction': profile.introduction if profile else '',
            'education': profile.education if profile else '',
            'skilled_filed': profile.skilled_filed if profile else '',
            'consultation_count': profile.consultation_count if profile else 0,
            'created_time': profile.created_time.strftime('%Y-%m-%d %H:%M:%S') if profile and profile.created_time else '',
            'serve_type': item.serve_type if item.serve_type else [],
            'status': item.status or '启用',
        }
        result_data.append(result_item)
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def consultants_list_profile(request):
    """POST 获取咨询师的账户信息和详细信息"""
    data = request.data
    counselor_id = data.get('id')
    
    if not counselor_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        counselor = Counselor.objects.get(id=counselor_id)
        
        # 获取咨询师的活跃token
        active_token = ConsultantAuthToken.objects.filter(
            counselor=counselor,
            is_active=True
        ).order_by('-created_time').first()
        
        token_value = active_token.token if active_token else ''
        
        # 获取咨询师详情
        try:
            profile = counselor.profile
        except CounselorProfile.DoesNotExist:
            profile = None
        
        # 构建返回数据
        result = {
            'user_id': str(counselor.id),
            'token': token_value,
            'id': str(counselor.id),
            'data': {
                'avatar': profile.avatar if profile and profile.avatar else '',
                'graduated_school': profile.graduated_school if profile else '',
                'address': profile.address if profile else '',
                'profession': profile.profession if profile else '',
                'introduction': profile.introduction if profile else '',
                'education': profile.education if profile else '',
                'skilled_filed': profile.skilled_filed if profile else '',
                'serve_type': counselor.serve_type if counselor.serve_type else [],
                'email': counselor.email if counselor.email else ''
            }
        }
        
        return Response(result)
    except Counselor.DoesNotExist:
        return Response({'message': '咨询师不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': f'获取失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def consultants_create(request):
    """POST 新建一条咨询师的信息"""
    data = request.data
    
    try:
        import uuid
        username = f"counselor_{uuid.uuid4().hex[:8]}"
        
        # 创建咨询师基本信息
        obj = Counselor.objects.create(
            username=username,
            name=data.get('name', ''),
            gender=data.get('gender', '男'),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            organization=data.get('organization', ''),
            expertise_tags=data.get('expertise', []),
            serve_type=data.get('serve_type', []),
            status=data.get('status', '启用'),
        )
        
        # 创建咨询师详情
        CounselorProfile.objects.create(
            counselor=obj,
            name=data.get('name', ''),
            graduated_school=data.get('graduated_school', ''),
            address=data.get('address', ''),
            organization=data.get('organization', ''),
            profession=data.get('profession', ''),
            expertise=data.get('expertise', []),
            introduction=data.get('introduction', ''),
            education=data.get('education', ''),
            skilled_filed=data.get('skilled_filed', ''),
            consultation_count=data.get('consultation_count', 0),
        )
        
        return Response({'id': str(obj.id), 'message': '创建成功'})
    except Exception as e:
        return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def consultants_update(request):
    """POST 修改一条咨询师的信息"""
    data = request.data
    counselor_id = data.get('id')
    
    if not counselor_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = Counselor.objects.get(id=counselor_id)
        
        # 更新咨询师基本信息
        if 'name' in data:
            obj.name = data.get('name')
        if 'phone' in data:
            obj.phone = data.get('phone')
        if 'email' in data:
            obj.email = data.get('email')
        if 'organization' in data:
            obj.organization = data.get('organization')
        if 'expertise' in data:
            obj.expertise_tags = data.get('expertise', [])
        if 'serve_type' in data:
            obj.serve_type = data.get('serve_type', [])
        if 'status' in data:
            obj.status = data.get('status')
        
        obj.save()
        
        # 更新或创建咨询师详情
        profile, created = CounselorProfile.objects.get_or_create(
            counselor=obj,
            defaults={'name': obj.name}
        )
        
        if 'name' in data:
            profile.name = data.get('name')
        if 'graduated_school' in data:
            profile.graduated_school = data.get('graduated_school', '')
        if 'address' in data:
            profile.address = data.get('address', '')
        if 'organization' in data:
            profile.organization = data.get('organization', '')
        if 'profession' in data:
            profile.profession = data.get('profession', '')
        if 'expertise' in data:
            profile.expertise = data.get('expertise', [])
        if 'introduction' in data:
            profile.introduction = data.get('introduction', '')
        if 'education' in data:
            profile.education = data.get('education', '')
        if 'skilled_filed' in data:
            profile.skilled_filed = data.get('skilled_filed', '')
        if 'consultation_count' in data:
            profile.consultation_count = data.get('consultation_count', 0)
        
        profile.save()
        
        return Response({})
    except Counselor.DoesNotExist:
        return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def consultants_id_name_list(request):
    """POST 查询所有咨询师的id和名字"""
    counselors = Counselor.objects.all().order_by('id')
    result_data = []
    for counselor in counselors:
        result_data.append({
            'id': str(counselor.id),
            'name': counselor.name,
        })
    return Response({'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def consultants_delete(request):
    """POST 删除一条咨询师的信息"""
    data = request.data
    counselor_id = data.get('id')
    
    if not counselor_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        Counselor.objects.filter(id=counselor_id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def consultants_status_update(request):
    """POST 启用/禁用一个咨询师"""
    data = request.data
    counselor_id = data.get('id')
    new_status = data.get('status')
    
    if not counselor_id or not new_status:
        return Response({'message': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        Counselor.objects.filter(id=counselor_id).update(status=new_status)
        return Response({})
    except Exception as e:
        return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 排班管理 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_work_list(request):
    """POST 按年月份获取排班管理信息"""
    data = request.data
    
    try:
        year = int(data.get('year'))
        month = int(data.get('month'))
    except (ValueError, TypeError):
        return Response({'message': '年份或月份参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取该月的所有日期
    from calendar import monthrange
    _, last_day = monthrange(year, month)
    
    result_data = []
    
    for day in range(1, last_day + 1):
        work_date = date(year, month, day)
        schedules = Schedule.objects.filter(work_date=work_date)
        
        schedules_dict = {}
        for schedule in schedules:
            counselor_id = str(schedule.counselor.id)
            counselor_name = schedule.counselor.name
            
            if counselor_id not in schedules_dict:
                schedules_dict[counselor_id] = {
                    'id': counselor_id,
                    'name': counselor_name,
                    'work_time': []
                }
            
            time_str = f"{schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}"
            if time_str not in schedules_dict[counselor_id]['work_time']:
                schedules_dict[counselor_id]['work_time'].append(time_str)
        
        result_data.append({
            'date': work_date.strftime('%Y-%m-%d'),
            'schedules': list(schedules_dict.values())
        })
    
    return Response({'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_work_create(request):
    """POST 给单个日期添加/修改排班（覆盖修改）"""
    data = request.data
    
    try:
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('date'))
        work_date = date(year, month, day)
        
        schedules_list = data.get('schedules', [])
        
        # 先删除该日期的所有排班记录（覆盖修改）
        # 如果 schedules 为空数组，则只删除不创建，相当于清空该日期的排班信息
        Schedule.objects.filter(work_date=work_date).delete()
        
        # 如果 schedules 为空，直接返回（清空操作完成）
        if not schedules_list:
            return Response({})
        
        # 创建新的排班记录
        created_by = request.admin_user.username if hasattr(request, 'admin_user') else ''
        
        for schedule_item in schedules_list:
            counselor_id = schedule_item.get('id')
            counselor_name = schedule_item.get('name')
            work_time_list = schedule_item.get('work_time', [])
            
            # 优先使用ID查找咨询师，如果没有ID则使用姓名
            if counselor_id:
                try:
                    counselor = Counselor.objects.get(id=int(counselor_id))
                except (Counselor.DoesNotExist, ValueError):
                    continue
            elif counselor_name:
                counselor = Counselor.objects.filter(name=counselor_name).first()
                if not counselor:
                    continue
            else:
                continue
            
            # 为每个工作时间段创建排班记录
            for work_time_str in work_time_list:
                try:
                    # 解析时间格式 "09:00-17:00"
                    if '-' in work_time_str:
                        start_str, end_str = work_time_str.split('-')
                        start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                        end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                        
                        Schedule.objects.create(
                            counselor=counselor,
                            work_date=work_date,
                            start_time=start_time,
                            end_time=end_time,
                            created_by=created_by,
                        )
                except (ValueError, AttributeError):
                    continue
        
        return Response({})
    except Exception as e:
        return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_files_upload(request):
    """POST 上传文件批量排班"""
    import os
    import pandas as pd
    import time
    from django.conf import settings
    
    # 检查是否有文件上传
    if 'file' not in request.FILES:
        return Response({'message': '请上传Excel文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    
    # 检查文件扩展名
    file_name = uploaded_file.name
    if not (file_name.endswith('.xls') or file_name.endswith('.xlsx')):
        return Response({'message': '只支持.xls或.xlsx格式的Excel文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 确保schedule_upload目录存在
        schedule_upload_dir = os.path.join(settings.BASE_DIR, 'static', 'schedule_upload')
        os.makedirs(schedule_upload_dir, exist_ok=True)
        
        # 生成唯一文件名（使用时间戳）
        timestamp = int(time.time() * 1000)
        file_ext = os.path.splitext(file_name)[1]
        unique_filename = f"{timestamp}_{file_name}"
        file_path = os.path.join(schedule_upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # 读取Excel文件
        try:
            df = pd.read_excel(file_path, engine='openpyxl' if file_ext == '.xlsx' else None)
        except Exception as e:
            return Response({'message': f'Excel文件读取失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 定义Excel列名映射（可能的列名变体）
        column_mapping = {
            '咨询师ID': 'counselor_id',
            '咨询师id': 'counselor_id',
            'counselor_id': 'counselor_id',
            'id': 'counselor_id',
            '咨询师姓名': 'counselor_name',
            '咨询师': 'counselor_name',
            '姓名': 'counselor_name',
            'name': 'counselor_name',
            '日期': 'work_date',
            '排班日期': 'work_date',
            'date': 'work_date',
            'work_date': 'work_date',
            '开始时间': 'start_time',
            'start_time': 'start_time',
            '结束时间': 'end_time',
            'end_time': 'end_time',
        }
        
        # 标准化列名
        df.columns = [column_mapping.get(str(col).strip(), str(col).strip()) for col in df.columns]
        
        # 检查必要的列是否存在
        has_counselor_id = 'counselor_id' in df.columns
        has_counselor_name = 'counselor_name' in df.columns
        
        if not has_counselor_id and not has_counselor_name:
            return Response({'message': 'Excel文件中必须包含"咨询师ID"或"咨询师姓名"列'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'work_date' not in df.columns:
            date_cols = [col for col in df.columns if '日期' in col or 'date' in col.lower()]
            if not date_cols:
                return Response({'message': 'Excel文件中必须包含"日期"或"排班日期"列'}, status=status.HTTP_400_BAD_REQUEST)
            df = df.rename(columns={date_cols[0]: 'work_date'})
        
        if 'start_time' not in df.columns:
            start_cols = [col for col in df.columns if '开始' in col or 'start' in col.lower()]
            if not start_cols:
                return Response({'message': 'Excel文件中必须包含"开始时间"列'}, status=status.HTTP_400_BAD_REQUEST)
            df = df.rename(columns={start_cols[0]: 'start_time'})
        
        if 'end_time' not in df.columns:
            end_cols = [col for col in df.columns if '结束' in col or 'end' in col.lower()]
            if not end_cols:
                return Response({'message': 'Excel文件中必须包含"结束时间"列'}, status=status.HTTP_400_BAD_REQUEST)
            df = df.rename(columns={end_cols[0]: 'end_time'})
        
        # 批量创建记录
        success_count = 0
        error_rows = []
        to_create = []
        created_by = request.admin_user.username if hasattr(request, 'admin_user') else ''
        
        for index, row in df.iterrows():
            try:
                # 获取咨询师信息
                counselor = None
                if has_counselor_id and pd.notna(row.get('counselor_id')):
                    try:
                        counselor_id = int(float(row.get('counselor_id')))
                        counselor = Counselor.objects.get(id=counselor_id)
                    except (Counselor.DoesNotExist, ValueError):
                        error_rows.append({'row': index + 2, 'error': f'咨询师ID {row.get("counselor_id")} 不存在'})
                        continue
                elif has_counselor_name:
                    counselor_name = str(row.get('counselor_name', '')).strip()
                    if not counselor_name or counselor_name == 'nan':
                        error_rows.append({'row': index + 2, 'error': '咨询师姓名不能为空'})
                        continue
                    counselor = Counselor.objects.filter(name=counselor_name).first()
                    if not counselor:
                        error_rows.append({'row': index + 2, 'error': f'咨询师"{counselor_name}"不存在'})
                        continue
                else:
                    error_rows.append({'row': index + 2, 'error': '缺少咨询师信息'})
                    continue
                
                # 获取日期
                work_date_str = str(row.get('work_date', '')).strip()
                if not work_date_str or work_date_str == 'nan':
                    error_rows.append({'row': index + 2, 'error': '排班日期不能为空'})
                    continue
                
                try:
                    if isinstance(row.get('work_date'), pd.Timestamp):
                        work_date = row.get('work_date').date()
                    elif isinstance(row.get('work_date'), datetime):
                        work_date = row.get('work_date').date()
                    else:
                        work_date = pd.to_datetime(work_date_str).date()
                except:
                    error_rows.append({'row': index + 2, 'error': f'日期格式错误: {work_date_str}'})
                    continue
                
                # 获取开始时间
                start_time_str = str(row.get('start_time', '')).strip()
                if not start_time_str or start_time_str == 'nan':
                    error_rows.append({'row': index + 2, 'error': '开始时间不能为空'})
                    continue
                
                try:
                    if isinstance(row.get('start_time'), pd.Timestamp):
                        start_time = row.get('start_time').time()
                    elif isinstance(row.get('start_time'), datetime):
                        start_time = row.get('start_time').time()
                    else:
                        # 尝试解析时间字符串（支持 HH:MM 或 HH:MM:SS 格式）
                        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
                except:
                    try:
                        start_time = datetime.strptime(start_time_str, '%H:%M').time()
                    except:
                        error_rows.append({'row': index + 2, 'error': f'开始时间格式错误: {start_time_str}'})
                        continue
                
                # 获取结束时间
                end_time_str = str(row.get('end_time', '')).strip()
                if not end_time_str or end_time_str == 'nan':
                    error_rows.append({'row': index + 2, 'error': '结束时间不能为空'})
                    continue
                
                try:
                    if isinstance(row.get('end_time'), pd.Timestamp):
                        end_time = row.get('end_time').time()
                    elif isinstance(row.get('end_time'), datetime):
                        end_time = row.get('end_time').time()
                    else:
                        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
                except:
                    try:
                        end_time = datetime.strptime(end_time_str, '%H:%M').time()
                    except:
                        error_rows.append({'row': index + 2, 'error': f'结束时间格式错误: {end_time_str}'})
                        continue
                
                if start_time >= end_time:
                    error_rows.append({'row': index + 2, 'error': '开始时间必须早于结束时间'})
                    continue
                
                to_create.append(Schedule(
                    counselor=counselor,
                    work_date=work_date,
                    start_time=start_time,
                    end_time=end_time,
                    created_by=created_by,
                ))
            except Exception as e:
                error_rows.append({'row': index + 2, 'error': f'第{index + 2}行数据错误: {str(e)}'})
        
        # 批量入库
        if to_create:
            Schedule.objects.bulk_create(to_create, batch_size=500, ignore_conflicts=True)
            success_count = len(to_create)
        
        # 返回结果
        result = {
            'message': f'成功导入{success_count}条记录',
            'success_count': success_count,
            'total_rows': len(df),
            'error_count': len(error_rows),
        }
        
        if error_rows:
            result['errors'] = error_rows[:10]  # 最多返回10个错误
        
        return Response(result)
        
    except Exception as e:
        return Response({'message': f'导入失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_list(request):
    """POST 分页查询停诊信息"""
    data = request.data
    
    try:
        page = int(data.get('page', 1)) if data.get('page') else 1
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Cancellation.objects.all().order_by('-created_time')
    
    # 可选过滤条件
    if data.get('name'):
        queryset = queryset.filter(counselor__name__icontains=data.get('name'))
    if data.get('start_time'):
        try:
            start_time = datetime.strptime(data.get('start_time'), '%Y-%m-%d %H:%M')
            queryset = queryset.filter(cancel_start__gte=start_time)
        except:
            pass
    if data.get('end_time'):
        try:
            end_time = datetime.strptime(data.get('end_time'), '%Y-%m-%d %H:%M')
            queryset = queryset.filter(cancel_end__lte=end_time)
        except:
            pass
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        result_data.append({
            'id': str(item.id),
            'name': item.counselor.name,
            'start_time': item.cancel_start.strftime('%Y-%m-%d %H:%M') if item.cancel_start else '',
            'end_time': item.cancel_end.strftime('%Y-%m-%d %H:%M') if item.cancel_end else '',
            'reason': item.reason or '',
            'create_time': item.created_time.strftime('%Y-%m-%d %H:%M') if item.created_time else '',
        })
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_create(request):
    """POST 新建单个咨询师的停诊数据"""
    data = request.data
    
    try:
        # 获取咨询师信息（优先使用consultant_id，如果没有则使用name）
        counselor = None
        consultant_id = data.get('consultant_id')
        name = data.get('name')
        
        if consultant_id:
            try:
                counselor = Counselor.objects.get(id=int(consultant_id))
            except (Counselor.DoesNotExist, ValueError):
                return Response({'message': '咨询师不存在'}, status=status.HTTP_400_BAD_REQUEST)
        elif name:
            counselor = Counselor.objects.filter(name=name).first()
            if not counselor:
                return Response({'message': '咨询师不存在'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'consultant_id或name参数至少需要一个'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取时间参数
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        reason = data.get('reason', '')
        
        if not start_time_str or not end_time_str:
            return Response({'message': 'start_time和end_time参数不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 解析时间格式，支持多种格式
        try:
            # 尝试解析 "2025-12-03 05:11:10" 格式
            start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # 尝试解析 "2025-12-03 05:11" 格式
                start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M')
            except ValueError:
                return Response({'message': 'start_time格式错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M')
            except ValueError:
                return Response({'message': 'end_time格式错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        if start_time >= end_time:
            return Response({'message': '开始时间必须早于结束时间'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建停诊记录
        created_by = request.admin_user.username if hasattr(request, 'admin_user') else ''
        Cancellation.objects.create(
            counselor=counselor,
            cancel_start=start_time,
            cancel_end=end_time,
            reason=reason,
            created_by=created_by,
        )
        
        return Response({'message': '创建成功'})
    except Exception as e:
        return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_update(request):
    """POST 修改单个咨询师的停诊数据"""
    data = request.data
    
    try:
        cancellation_id = data.get('id')
        if not cancellation_id:
            return Response({'message': 'id参数不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cancellation = Cancellation.objects.get(id=int(cancellation_id))
        except (Cancellation.DoesNotExist, ValueError):
            return Response({'message': '停诊记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 如果提供了name，验证是否匹配
        if 'name' in data:
            if cancellation.counselor.name != data.get('name'):
                return Response({'message': '咨询师姓名不匹配'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新字段
        if 'start_time' in data:
            start_time_str = data.get('start_time')
            try:
                start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M')
                except ValueError:
                    return Response({'message': 'start_time格式错误'}, status=status.HTTP_400_BAD_REQUEST)
            cancellation.cancel_start = start_time
        
        if 'end_time' in data:
            end_time_str = data.get('end_time')
            try:
                end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M')
                except ValueError:
                    return Response({'message': 'end_time格式错误'}, status=status.HTTP_400_BAD_REQUEST)
            cancellation.cancel_end = end_time
        
        if 'reason' in data:
            cancellation.reason = data.get('reason', '')
        
        # 验证时间逻辑
        if cancellation.cancel_start >= cancellation.cancel_end:
            return Response({'message': '开始时间必须早于结束时间'}, status=status.HTTP_400_BAD_REQUEST)
        
        cancellation.save()
        return Response({'message': '更新成功'})
    except Exception as e:
        return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_delete(request):
    """POST 删除单个咨询师的停诊数据"""
    data = request.data
    
    try:
        cancellation_id = data.get('id')
        if not cancellation_id:
            return Response({'message': 'id参数不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cancellation = Cancellation.objects.get(id=int(cancellation_id))
            cancellation.delete()
            return Response({'message': '删除成功'})
        except (Cancellation.DoesNotExist, ValueError):
            return Response({'message': '停诊记录不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': f'删除失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_list_conflict(request):
    """POST 查询咨询师在某时间段中是否停诊"""
    data = request.data
    
    try:
        counselor_id = data.get('id')
        if not counselor_id:
            return Response({'message': 'id参数不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            counselor = Counselor.objects.get(id=int(counselor_id))
        except (Counselor.DoesNotExist, ValueError):
            return Response({'message': '咨询师不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        if not start_time_str or not end_time_str:
            return Response({'message': 'start_time和end_time参数不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 解析时间格式
        try:
            query_start = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                query_start = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M')
            except ValueError:
                return Response({'message': 'start_time格式错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            query_end = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                query_end = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M')
            except ValueError:
                return Response({'message': 'end_time格式错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        if query_start >= query_end:
            return Response({'message': '开始时间必须早于结束时间'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查询是否有时间冲突的停诊记录
        # 冲突条件：停诊时间段与查询时间段有重叠
        # 即：停诊开始时间 < 查询结束时间 且 停诊结束时间 > 查询开始时间
        conflicts = Cancellation.objects.filter(
            counselor=counselor,
            cancel_start__lt=query_end,
            cancel_end__gt=query_start
        )
        
        has_conflict = conflicts.exists()
        conflict_data = []
        
        if has_conflict:
            for conflict in conflicts:
                conflict_data.append({
                    'id': str(conflict.id),
                    'start_time': conflict.cancel_start.strftime('%Y-%m-%d %H:%M') if conflict.cancel_start else '',
                    'end_time': conflict.cancel_end.strftime('%Y-%m-%d %H:%M') if conflict.cancel_end else '',
                    'reason': conflict.reason or '',
                })
        
        return Response({
            'has_conflict': has_conflict,
            'conflicts': conflict_data
        })
    except Exception as e:
        return Response({'message': f'查询失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 咨询档案 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def record_profile(request):
    """
    POST 获取咨询档案的详细咨询记录（管理员端）
    管理员可以查看所有档案的详细记录
    """
    record_id = request.data.get('id')
    
    if not record_id:
        return Response({
            'code': 400,
            'message': '缺少档案ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 管理员可以查看所有档案
        record = ConsultationRecord.objects.get(id=record_id)
        sessions = record.sessions.all().order_by('session_number')
        
        serializer = ConsultationSessionDetailSerializer(sessions, many=True)
        
        return Response({
            'code': 0,
            'message': '获取成功',
            'data': serializer.data
        })
    except ConsultationRecord.DoesNotExist:
        return Response({
            'code': 404,
            'message': '档案不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def session_create(request):
    """
    POST 新建一条咨询记录（管理员端）
    管理员可以为任何档案创建会话
    支持 JSON 和 form-data 两种格式
    """
    import os
    import time
    from django.conf import settings
    
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
    
    # 文档中要求传入id作为咨询档案的id
    record_id = data.get('id')
    
    if not record_id:
        return Response({
            'code': 400,
            'message': '缺少档案ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        record = ConsultationRecord.objects.get(id=record_id)
        
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
        elif 'attachImages' in data:
            # 如果只是数组路径，直接使用
            attach_images = data.get('attachImages', [])
            if not isinstance(attach_images, list):
                attach_images = []
        
        # 处理日期字段
        interview_date = timezone.now().date()
        if data.get('date'):
            try:
                if isinstance(data.get('date'), str):
                    interview_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
                elif hasattr(data.get('date'), 'date'):
                    interview_date = data.get('date').date()
            except (ValueError, TypeError):
                interview_date = timezone.now().date()
        
        # 处理 duration 字段
        duration = None
        if data.get('duration'):
            try:
                duration_value = data.get('duration')
                if isinstance(duration_value, str) and duration_value.isdigit():
                    duration = int(duration_value)
                elif isinstance(duration_value, (int, float)):
                    duration = int(duration_value)
            except (ValueError, TypeError):
                duration = None
        
        # 处理 isThirdPartyEvaluation 字段
        is_third_party = False
        if 'isThirdPartyEvaluation' in data:
            is_third_party_value = data.get('isThirdPartyEvaluation')
            if isinstance(is_third_party_value, bool):
                is_third_party = is_third_party_value
            elif isinstance(is_third_party_value, str):
                is_third_party = is_third_party_value.lower() in ('true', '1', 'yes')
            else:
                is_third_party = bool(is_third_party_value)
        
        # 创建会话
        session = ConsultationSession.objects.create(
            record=record,
            session_number=next_number,
            interview_date=interview_date,
            interview_time=data.get('time', ''),
            duration=duration,
            visit_status=data.get('visitStatus', 'scheduled'),
            objective_description=data.get('description', ''),
            doctor_evaluation=data.get('doctorEvaluation', ''),
            follow_up_plan=data.get('followUpPlan', ''),
            next_visit_plan=data.get('nextVisitPlan', ''),
            crisis_status=_convert_crisis_status_to_string(data.get('crisisStatus', [])),
            consultant_name=data.get('consultantName', ''),
            is_third_party_evaluation=is_third_party,
            signature_image=signature_image or data.get('signatureImage', ''),
            attach_images=attach_images,
            created_by=record.counselor  # 使用档案的咨询师作为创建人
        )
        
        # 更新档案的访谈次数
        record.interview_count = next_number
        record.save(update_fields=['interview_count'])
        
        return Response({
            'code': '0',
            'message': '创建成功'
        })
    except ConsultationRecord.DoesNotExist:
        return Response({
            'code': 404,
            'message': '档案不存在'
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
    POST 更新一条咨询记录（管理员端）
    管理员可以更新任何会话
    支持 form-data 和 JSON 两种格式
    必选参数：user_id（用于鉴权）、token（用于鉴权）、id（记录id）
    """
    # 支持 form-data 和 JSON 两种格式
    data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
    
    # 检查必选参数：user_id 和 id
    user_id = data.get('user_id') or data.get('userID')
    session_id = data.get('id')
    
    if not user_id:
        return Response({
            'code': 400,
            'message': '缺少user_id参数'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not session_id:
        return Response({
            'code': 400,
            'message': '缺少id参数（记录id）'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        import os
        import time
        import json
        from django.conf import settings
        
        session = ConsultationSession.objects.get(id=session_id)
        
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
            is_third_party = data.get('isThirdPartyEvaluation')
            if isinstance(is_third_party, bool):
                session.is_third_party_evaluation = is_third_party
            else:
                session.is_third_party_evaluation = str(is_third_party).lower() == 'true'
        
        # 处理签名图片文件上传（如果上传了新文件）
        if 'signatureImage' in request.FILES:
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
        
        # 处理附加图片文件上传（如果上传了新文件，支持多个文件）
        if 'attachImages' in request.FILES:
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
        
        session.save()
        
        return Response({})
    except ConsultationSession.DoesNotExist:
        return Response({
            'code': 404,
            'message': '会话不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def personal_profile(request):
    """
    POST 获取个人档案（管理员端）
    管理员可以查看所有档案的个人信息
    """
    record_id = request.data.get('id')
    
    if not record_id:
        return Response({
            'code': 400,
            'message': '缺少档案ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        record = ConsultationRecord.objects.get(id=record_id)
        
        # 构建紧急联系人信息
        emergency_contact = {}
        if record.emergency_contact_name:
            emergency_contact = {
                'name': record.emergency_contact_name,
                'relationship': '',  # 关系字段在模型中不存在，返回空
                'phone': record.emergency_contact_phone or ''
            }
        
        return Response({
            'code': 'string',
            'message': 'string',
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
        return Response({
            'code': 404,
            'message': '档案不存在'
        }, status=status.HTTP_404_NOT_FOUND)
