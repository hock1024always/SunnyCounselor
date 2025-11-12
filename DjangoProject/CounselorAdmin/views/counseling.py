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

from CounselorAdmin.models import Appointment, Counselor, Schedule, Cancellation
from CounselorAdmin.utils import require_body_auth
from Consultant.models import CounselorProfile


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
