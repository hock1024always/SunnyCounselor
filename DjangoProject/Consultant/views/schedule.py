"""
排班管理相关视图 - 函数式视图
所有接口使用POST方法，参数和鉴权都在请求体JSON中
"""
import os
import json
import time
from datetime import datetime, timedelta
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from Consultant.models import CounselorSchedule, CounselorAbsence
from Consultant.utils import require_body_auth


# ==================== 排班管理 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_work(request):
    """POST 按年月份获取排班管理信息"""
    counselor = request.counselor
    data = request.data
    year = data.get('year')
    month = data.get('month')
    organization = data.get('organization', '')
    
    if not year or not month:
        return Response({
            'code': 400,
            'message': '年份和月份必填'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 查询该月的排班
    schedules = CounselorSchedule.objects.filter(
        counselor=counselor,
        schedule_date__year=int(year),
        schedule_date__month=int(month)
    ).order_by('schedule_date')
    
    # 按日期组织数据
    result = []
    for schedule in schedules:
        date = schedule.schedule_date.day
        schedule_list = [{
            'id': schedule.id,
            'name': counselor.name,
            'work_time': ', '.join(schedule.time_slots) if isinstance(schedule.time_slots, list) else str(schedule.time_slots)
        }]
        
        result.append({
            'date': date,
            'schedules': schedule_list
        })
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': result
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_work_update(request):
    """
    POST 全覆盖更新排班
    1. 根据上传用户的id进行逻辑鉴权
    2. 删除该id下的所有排班数据库记录
    3. 然后将前端传入的数据库记录全部写入数据库（全覆盖操作）
    """
    counselor = request.counselor
    data = request.data
    user_id = data.get('user_id') or data.get('userID')
    
    # 1. 根据上传用户的id进行逻辑鉴权
    if not user_id:
        return Response({
            'code': 400,
            'message': '缺少用户ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return Response({
            'code': 400,
            'message': '用户ID格式错误'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证user_id是否匹配当前登录的咨询师
    if user_id != counselor.id:
        return Response({
            'code': 403,
            'message': '无权修改其他咨询师的排班'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # 2. 删除该id下的所有排班数据库记录
    deleted_count = CounselorSchedule.objects.filter(counselor=counselor).delete()[0]
    
    # 3. 将前端传入的数据库记录全部写入数据库（全覆盖操作）
    # 支持两种格式：
    # 1. schedules数组格式：多个排班记录
    # 2. 单个记录格式：year, month, date, work_schedules
    schedules_data = data.get('schedules', [])
    
    # 如果没有schedules数组，检查是否是单个记录格式
    if not schedules_data:
        # 检查是否是单个记录格式
        year = data.get('year')
        month = data.get('month')
        date = data.get('date')
        work_schedules = data.get('work_schedules', [])
        
        if year and month and date:
            # 单个记录格式，转换为数组格式
            schedules_data = [{
                'year': year,
                'month': month,
                'date': date,
                'work_schedules': work_schedules
            }]
    
    if not schedules_data:
        return Response({
            'code': 0,
            'message': '更新成功，已清空所有排班记录',
            'data': {
                'deleted_count': deleted_count,
                'created_count': 0
            }
        })
    
    # 批量创建排班记录
    schedules_to_create = []
    for schedule_item in schedules_data:
        try:
            # 解析日期信息
            year = schedule_item.get('year')
            month = schedule_item.get('month')
            date = schedule_item.get('date')
            work_schedules = schedule_item.get('work_schedules', [])
            
            if not year or not month or not date:
                continue  # 跳过无效记录
            
            # 构建日期
            schedule_date = datetime(int(year), int(month), int(date)).date()
            
            # 计算最大预约数和剩余可预约数
            max_appointments = len(work_schedules) * 5 if isinstance(work_schedules, list) else 5
            available_slots = max_appointments
            
            schedules_to_create.append(
                CounselorSchedule(
                    counselor=counselor,
                    schedule_date=schedule_date,
                    time_slots=work_schedules if isinstance(work_schedules, list) else [],
                    max_appointments=max_appointments,
                    available_slots=available_slots
                )
            )
        except Exception as e:
            # 跳过有错误的记录，继续处理其他记录
            continue
    
    # 批量创建
    if schedules_to_create:
        CounselorSchedule.objects.bulk_create(schedules_to_create, batch_size=100)
    
    return Response({
        'code': 0,
        'message': f'更新成功，已删除{deleted_count}条记录，新增{len(schedules_to_create)}条记录',
        'data': {
            'deleted_count': deleted_count,
            'created_count': len(schedules_to_create)
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_upload(request):
    """POST 上传Excel文件批量排班"""
    import pandas as pd
    
    counselor = request.counselor
    
    # 检查是否有文件上传
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
            return Response({
                'code': 400,
                'message': f'Excel文件读取失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 定义Excel列名映射（可能的列名变体）
        column_mapping = {
            '日期': 'schedule_date',
            '排班日期': 'schedule_date',
            'date': 'schedule_date',
            'schedule_date': 'schedule_date',
            '时间段': 'time_slots',
            '排班时间段': 'time_slots',
            'time_slots': 'time_slots',
            'work_schedules': 'time_slots',
            '时间段数组': 'time_slots',
            '最大预约数': 'max_appointments',
            'max_appointments': 'max_appointments',
            '剩余可预约数': 'available_slots',
            'available_slots': 'available_slots',
        }
        
        # 标准化列名
        df.columns = [column_mapping.get(str(col).strip(), str(col).strip()) for col in df.columns]
        
        # 检查必要的列是否存在
        if 'schedule_date' not in df.columns:
            # 尝试查找可能的日期列
            date_cols = [col for col in df.columns if '日期' in col or 'date' in col.lower()]
            if not date_cols:
                return Response({
                    'code': 400,
                    'message': 'Excel文件中必须包含"日期"或"排班日期"列'
                }, status=status.HTTP_400_BAD_REQUEST)
            df = df.rename(columns={date_cols[0]: 'schedule_date'})
        
        # 批量创建记录
        success_count = 0
        error_rows = []
        to_create = []
        
        for index, row in df.iterrows():
            try:
                # 获取日期
                schedule_date_str = str(row.get('schedule_date', '')).strip()
                if not schedule_date_str or schedule_date_str == 'nan':
                    error_rows.append({'row': index + 2, 'error': '排班日期不能为空'})
                    continue
                
                # 解析日期（支持多种格式）
                try:
                    if isinstance(row.get('schedule_date'), pd.Timestamp):
                        schedule_date = row.get('schedule_date').date()
                    elif isinstance(row.get('schedule_date'), datetime):
                        schedule_date = row.get('schedule_date').date()
                    else:
                        # 尝试解析字符串日期
                        schedule_date = pd.to_datetime(schedule_date_str).date()
                except:
                    error_rows.append({'row': index + 2, 'error': f'日期格式错误: {schedule_date_str}'})
                    continue
                
                # 获取时间段
                time_slots = row.get('time_slots', [])
                if pd.notna(time_slots):
                    if isinstance(time_slots, str):
                        # 如果是字符串，尝试解析（可能是逗号分隔或JSON格式）
                        try:
                            time_slots = json.loads(time_slots)
                        except:
                            # 如果不是JSON，按逗号分隔
                            time_slots = [t.strip() for t in time_slots.split(',') if t.strip()]
                    elif not isinstance(time_slots, list):
                        time_slots = []
                else:
                    time_slots = []
                
                if not time_slots:
                    error_rows.append({'row': index + 2, 'error': '时间段不能为空'})
                    continue
                
                # 获取最大预约数和剩余可预约数
                max_appointments = len(time_slots) * 5  # 默认每个时段5个预约
                if pd.notna(row.get('max_appointments')):
                    try:
                        max_appointments = int(float(row.get('max_appointments')))
                    except:
                        pass
                
                available_slots = max_appointments
                if pd.notna(row.get('available_slots')):
                    try:
                        available_slots = int(float(row.get('available_slots')))
                    except:
                        pass
                
                # 检查是否已存在该日期的排班
                if CounselorSchedule.objects.filter(counselor=counselor, schedule_date=schedule_date).exists():
                    # 如果已存在，跳过或更新（这里选择跳过，避免重复）
                    continue
                
                to_create.append(
                    CounselorSchedule(
                        counselor=counselor,
                        schedule_date=schedule_date,
                        time_slots=time_slots,
                        max_appointments=max_appointments,
                        available_slots=available_slots
                    )
                )
            except Exception as e:
                error_rows.append({'row': index + 2, 'error': f'第{index + 2}行数据错误: {str(e)}'})
        
        # 批量入库
        if to_create:
            CounselorSchedule.objects.bulk_create(to_create, batch_size=100, ignore_conflicts=True)
            success_count = len(to_create)
        
        # 返回结果
        result = {
            'code': 0,
            'message': f'成功导入{success_count}条记录',
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
def schedule_stop(request):
    """POST 获取停诊信息 - 用户只能查看自己所属机构下所有咨询师的停诊信息"""
    from CounselorAdmin.models import Cancellation
    from datetime import datetime
    
    counselor = request.counselor
    data = request.data
    
    try:
        page = int(data.get('page', 1)) if data.get('page') else 1
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({
            'code': 400,
            'message': '分页参数错误'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取当前咨询师的所属机构
    current_organization = counselor.organization
    
    # 查询同一机构下所有咨询师的停诊信息
    queryset = Cancellation.objects.filter(
        counselor__organization=current_organization
    ).order_by('-created_time')
    
    # 可选过滤条件
    if data.get('name'):
        queryset = queryset.filter(counselor__name__icontains=data.get('name'))
    if data.get('start_time') and data.get('end_time'):
        try:
            start_time = datetime.strptime(data.get('start_time').strip(), '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(data.get('end_time').strip(), '%Y-%m-%d %H:%M:%S')
            queryset = queryset.filter(
                cancel_start__gte=start_time,
                cancel_end__lte=end_time
            )
        except:
            pass
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        result_data.append({
            'name': item.counselor.name,
            'start_time': item.cancel_start.strftime('%Y-%m-%d %H:%M') if item.cancel_start else '',
            'end_time': item.cancel_end.strftime('%Y-%m-%d %H:%M') if item.cancel_end else '',
        })
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': result_data
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_create(request):
    """POST 新建停诊数据 - 咨询师只能新建自己的停诊信息"""
    from CounselorAdmin.models import Cancellation
    from datetime import datetime
    
    counselor = request.counselor
    data = request.data
    
    try:
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        reason = data.get('reason', '')
        
        if not start_time_str or not end_time_str:
            return Response({
                'code': 400,
                'message': 'start_time和end_time参数不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 解析时间格式
        try:
            start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M')
            except ValueError:
                return Response({
                    'code': 400,
                    'message': 'start_time格式错误'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M')
            except ValueError:
                return Response({
                    'code': 400,
                    'message': 'end_time格式错误'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if start_time >= end_time:
            return Response({
                'code': 400,
                'message': '开始时间必须早于结束时间'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建停诊记录（只能创建自己的）
        Cancellation.objects.create(
            counselor=counselor,
            cancel_start=start_time,
            cancel_end=end_time,
            reason=reason,
            created_by=counselor.username,
        )
        
        return Response({
            'code': 0,
            'message': '创建成功'
        })
    except Exception as e:
        return Response({
            'code': 400,
            'message': f'创建失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_update(request):
    """POST 修改停诊数据 - 咨询师只能修改自己的停诊信息"""
    from CounselorAdmin.models import Cancellation
    from datetime import datetime
    
    counselor = request.counselor
    data = request.data
    
    try:
        cancellation_id = data.get('id')
        if not cancellation_id:
            return Response({
                'code': 400,
                'message': 'id参数不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cancellation = Cancellation.objects.get(id=int(cancellation_id))
        except (Cancellation.DoesNotExist, ValueError):
            return Response({
                'code': 404,
                'message': '停诊记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证权限：只能修改自己的停诊记录
        if cancellation.counselor.id != counselor.id:
            return Response({
                'code': 403,
                'message': '无权修改其他咨询师的停诊记录'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 更新字段
        if 'start_time' in data:
            start_time_str = data.get('start_time')
            try:
                start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M')
                except ValueError:
                    return Response({
                        'code': 400,
                        'message': 'start_time格式错误'
                    }, status=status.HTTP_400_BAD_REQUEST)
            cancellation.cancel_start = start_time
        
        if 'end_time' in data:
            end_time_str = data.get('end_time')
            try:
                end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M')
                except ValueError:
                    return Response({
                        'code': 400,
                        'message': 'end_time格式错误'
                    }, status=status.HTTP_400_BAD_REQUEST)
            cancellation.cancel_end = end_time
        
        if 'reason' in data:
            cancellation.reason = data.get('reason', '')
        
        # 验证时间逻辑
        if cancellation.cancel_start >= cancellation.cancel_end:
            return Response({
                'code': 400,
                'message': '开始时间必须早于结束时间'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cancellation.save()
        return Response({
            'code': 0,
            'message': '更新成功'
        })
    except Exception as e:
        return Response({
            'code': 400,
            'message': f'更新失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_delete(request):
    """POST 删除停诊数据 - 咨询师只能删除自己的停诊信息"""
    from CounselorAdmin.models import Cancellation
    
    counselor = request.counselor
    data = request.data
    
    try:
        cancellation_id = data.get('id')
        if not cancellation_id:
            return Response({
                'code': 400,
                'message': 'id参数不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cancellation = Cancellation.objects.get(id=int(cancellation_id))
        except (Cancellation.DoesNotExist, ValueError):
            return Response({
                'code': 404,
                'message': '停诊记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证权限：只能删除自己的停诊记录
        if cancellation.counselor.id != counselor.id:
            return Response({
                'code': 403,
                'message': '无权删除其他咨询师的停诊记录'
            }, status=status.HTTP_403_FORBIDDEN)
        
        cancellation.delete()
        return Response({
            'code': 0,
            'message': '删除成功'
        })
    except Exception as e:
        return Response({
            'code': 400,
            'message': f'删除失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def schedule_stop_conflict(request):
    """POST 查询咨询师在某时间段是否停诊 - 查询自己的排班时间与停诊时间冲突"""
    from CounselorAdmin.models import Cancellation
    from datetime import datetime
    
    counselor = request.counselor
    data = request.data
    
    try:
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        if not start_time_str or not end_time_str:
            return Response({
                'code': 400,
                'message': 'start_time和end_time参数不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 解析时间格式
        try:
            query_start = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                query_start = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M')
            except ValueError:
                return Response({
                    'code': 400,
                    'message': 'start_time格式错误'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            query_end = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                query_end = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M')
            except ValueError:
                return Response({
                    'code': 400,
                    'message': 'end_time格式错误'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if query_start >= query_end:
            return Response({
                'code': 400,
                'message': '开始时间必须早于结束时间'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 查询是否有时间冲突的停诊记录（只查询自己的）
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
            'code': 0,
            'has_conflict': has_conflict,
            'conflicts': conflict_data
        })
    except Exception as e:
        return Response({
            'code': 400,
            'message': f'查询失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

