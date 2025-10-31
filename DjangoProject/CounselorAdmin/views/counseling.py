"""
心理咨询接口 - 函数式视图
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date
from collections import defaultdict

from CounselorAdmin.models import Appointment, Counselor, Schedule, Cancellation
from CounselorAdmin.utils import require_auth


# ==================== 咨询统计 ====================

@api_view(['GET', 'POST'])
@require_auth
def order_list_create(request):
    """GET 分页查询咨询订单记录 / POST 创建一条咨询订单"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1)) if request.query_params.get('page') else 1
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Appointment.objects.all()
        
        if request.query_params.get('name'):
            queryset = queryset.filter(client_name__icontains=request.query_params.get('name'))
        if request.query_params.get('date_start'):
            try:
                date_start = datetime.strptime(request.query_params.get('date_start'), '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__gte=date_start)
            except:
                pass
        if request.query_params.get('date_end'):
            try:
                date_end = datetime.strptime(request.query_params.get('date_end'), '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__lte=date_end)
            except:
                pass
        if request.query_params.get('type'):
            queryset = queryset.filter(service_type=request.query_params.get('type'))
        if request.query_params.get('status'):
            queryset = queryset.filter(status=request.query_params.get('status'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'order_id': item.order_no,
                'name': item.client_name,
                'gender': item.client_gender,
                'age': str(item.client_age) if item.client_age else '',
                'type': item.service_type or '',
                'key_word': item.counseling_keywords or '',
                'date': item.appointment_date.strftime('%Y-%m-%d') if item.appointment_date else '',
                'time': item.time_slot or '',
                'commit_time': item.submit_time.strftime('%Y-%m-%d %H:%M:%S') if item.submit_time else '',
                'finish_time': item.end_time.strftime('%Y-%m-%d %H:%M:%S') if item.end_time else '',
                'status': item.status,
            })
        
        return Response({'message': '查询成功', 'total': str(total), 'data': data})
    
    elif request.method == 'POST':
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

@api_view(['GET', 'POST', 'PUT'])
@require_auth
def consultants_list_create_update(request):
    """GET 分页查询咨询师信息表 / POST 新建一条咨询师的信息 / PUT 修改一条咨询师的信息"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Counselor.objects.all()
        
        if request.query_params.get('name'):
            queryset = queryset.filter(name__icontains=request.query_params.get('name'))
        if request.query_params.get('phone'):
            queryset = queryset.filter(phone__icontains=request.query_params.get('phone'))
        if request.query_params.get('status'):
            queryset = queryset.filter(status=request.query_params.get('status'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            skills = item.expertise_tags if isinstance(item.expertise_tags, list) else []
            data.append({
                'id': str(item.id),
                'name': item.name,
                'gender': item.gender,
                'phone': item.phone,
                'organization': item.organization or '',
                'skills': skills,
                'status': item.status,
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
        data = request.data
        
        try:
            import uuid
            username = f"counselor_{uuid.uuid4().hex[:8]}"
            
            obj = Counselor.objects.create(
                username=username,
                name=data.get('name'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                organization=data.get('organization', ''),
                expertise_tags=data.get('skills', []),
                status=data.get('status', '启用'),
            )
            return Response({'id': str(obj.id), 'message': '创建成功'})
        except Exception as e:
            return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        data = request.data
        counselor_id = data.get('id')
        
        if not counselor_id:
            return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            obj = Counselor.objects.get(id=counselor_id)
            
            if 'name' in data:
                obj.name = data.get('name')
            if 'phone' in data:
                obj.phone = data.get('phone')
            if 'organization' in data:
                obj.organization = data.get('organization')
            if 'skills' in data:
                obj.expertise_tags = data.get('skills', [])
            if 'status' in data:
                obj.status = data.get('status')
            
            obj.save()
            return Response({})
        except Counselor.DoesNotExist:
            return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@require_auth
def consultants_delete(request, id):
    """DELETE 删除一条咨询师的信息"""
    try:
        Counselor.objects.filter(id=id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@require_auth
def consultants_status_update(request):
    """PUT 启用/禁用一个咨询师"""
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

@api_view(['GET', 'POST'])
@require_auth
def schedule_work_list_create(request):
    """GET 按年月份获取排班管理信息 / POST 给单个日期添加排班"""
    if request.method == 'GET':
        try:
            year = int(request.query_params.get('year'))
            month = int(request.query_params.get('month'))
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
    
    elif request.method == 'POST':
        data = request.data
        schedules_data = data.get('schedules', {})
        
        try:
            year = int(data.get('year'))
            month = int(data.get('month'))
            day = int(data.get('date'))
            work_date = date(year, month, day)
            
            counselor_name = schedules_data.get('name')
            counselor = Counselor.objects.filter(name=counselor_name).first()
            if not counselor:
                return Response({'message': '咨询师不存在'}, status=status.HTTP_400_BAD_REQUEST)
            
            work_time = schedules_data.get('work_time', '')
            stop_work_time = schedules_data.get('stop_work_time', '')
            
            if work_time and stop_work_time:
                start_time = datetime.strptime(work_time, '%H:%M').time()
                end_time = datetime.strptime(stop_work_time, '%H:%M').time()
                
                Schedule.objects.create(
                    counselor=counselor,
                    work_date=work_date,
                    start_time=start_time,
                    end_time=end_time,
                    created_by=request.admin_user.username if hasattr(request, 'admin_user') else '',
                )
            
            return Response({})
        except Exception as e:
            return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@require_auth
def schedule_files_upload(request):
    """POST 上传文件批量排班"""
    # TODO: 实现Excel文件解析和批量排班
    return Response({})


@api_view(['GET', 'PUT'])
@require_auth
def schedule_stop_list_update(request):
    """GET 按年份查询停诊信息 / PUT 添加/修改停诊安排"""
    if request.method == 'GET':
        try:
            year = int(request.query_params.get('year'))
        except (ValueError, TypeError):
            return Response({'message': '年份参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查询该年的所有停诊记录
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        cancellations = Cancellation.objects.filter(
            cancel_start__gte=start_date,
            cancel_start__lte=end_date
        )
        
        # 按咨询师分组
        counselor_dict = defaultdict(lambda: {'stop_schedules': []})
        
        for cancel in cancellations:
            counselor_id = str(cancel.counselor.id)
            counselor_name = cancel.counselor.name
            
            if counselor_id not in counselor_dict:
                counselor_dict[counselor_id] = {
                    'id': counselor_id,
                    'name': counselor_name,
                    'stop_schedules': []
                }
            
            counselor_dict[counselor_id]['stop_schedules'].append({
                'start_time': cancel.cancel_start.strftime('%Y-%m-%d %H:%M'),
                'end_time': cancel.cancel_end.strftime('%Y-%m-%d %H:%M'),
            })
        
        return Response({'data': list(counselor_dict.values())})
    
    elif request.method == 'PUT':
        data_list = request.data.get('data', [])
        
        try:
            for item in data_list:
                counselor_name = item.get('name')
                counselor = Counselor.objects.filter(name=counselor_name).first()
                if not counselor:
                    continue
                
                start_time = datetime.strptime(item.get('start_time'), '%Y-%m-%d %H:%M')
                end_time = datetime.strptime(item.get('end_time'), '%Y-%m-%d %H:%M')
                
                # 查找是否存在相同时间的停诊记录
                existing = Cancellation.objects.filter(
                    counselor=counselor,
                    cancel_start=start_time,
                    cancel_end=end_time
                ).first()
                
                if not existing:
                    Cancellation.objects.create(
                        counselor=counselor,
                        cancel_start=start_time,
                        cancel_end=end_time,
                        created_by=request.admin_user.username if hasattr(request, 'admin_user') else '',
                    )
                else:
                    # 更新现有记录
                    existing.cancel_start = start_time
                    existing.cancel_end = end_time
                    existing.save()
            
            return Response({})
        except Exception as e:
            return Response({'message': f'操作失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

