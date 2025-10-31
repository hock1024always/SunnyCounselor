"""
干预管理接口 - 函数式视图
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime

from CounselorAdmin.models import InterviewAssessment, NegativeEvent, ReferralUnit, StudentReferral
from CounselorAdmin.utils import require_auth


# ==================== 访谈评估 ====================

@api_view(['GET', 'POST'])
@require_auth
def interview_list_create(request):
    """GET 分页查询访谈记录列表 / POST 新建一条访谈记录"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = InterviewAssessment.objects.all()
        
        # 过滤条件
        if request.query_params.get('std_name'):
            queryset = queryset.filter(student_name__icontains=request.query_params.get('std_name'))
        if request.query_params.get('std_grade'):
            queryset = queryset.filter(grade=request.query_params.get('std_grade'))
        if request.query_params.get('std_class'):
            queryset = queryset.filter(class_name=request.query_params.get('std_class'))
        if request.query_params.get('std_school'):
            queryset = queryset.filter(organization=request.query_params.get('std_school'))
        if request.query_params.get('interview_cout'):
            queryset = queryset.filter(interview_count=int(request.query_params.get('interview_cout')))
        if request.query_params.get('interview_status'):
            queryset = queryset.filter(interview_status=request.query_params.get('interview_status'))
        if request.query_params.get('interview_type'):
            queryset = queryset.filter(interview_type=request.query_params.get('interview_type'))
        if request.query_params.get('doctor_evaluation'):
            queryset = queryset.filter(doctor_assessment=request.query_params.get('doctor_evaluation'))
        if request.query_params.get('follow_up_plan'):
            queryset = queryset.filter(follow_up_plan=request.query_params.get('follow_up_plan'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'std_name': item.student_name,
                'std_grade': item.grade or '',
                'std_class': item.class_name or '',
                'std_school': item.organization or '',
                'interview_count': str(item.interview_count),
                'interview_status': item.interview_status,
                'interview_type': item.interview_type or '',
                'doctor_evaluation': item.doctor_assessment or '',
                'follow_up_plan': item.follow_up_plan or '',
                'create_time': item.created_time.strftime('%Y-%m-%d') if item.created_time else '',
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
        data = request.data
        
        try:
            obj = InterviewAssessment.objects.create(
                student_name=data.get('std_name'),
                grade=data.get('std_grade', ''),
                class_name=data.get('std_class', ''),
                organization=data.get('std_school', ''),
                interview_count=int(data.get('interview_count', 1)),
                interview_status=data.get('interview_status', '待处理'),
                interview_type=data.get('interview_type', ''),
                doctor_assessment=data.get('doctor_evaluation', ''),
                follow_up_plan=data.get('follow_up_plan', ''),
            )
            return Response({'code': '1', 'id': str(obj.id), 'meesage': '新建成功'})
        except Exception as e:
            return Response({'code': '0', 'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@require_auth
def interview_delete(request, id):
    """DELETE 删除一条访谈记录"""
    try:
        InterviewAssessment.objects.filter(id=id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@require_auth
def interview_upload(request):
    """POST 批量导入访谈记录"""
    # TODO: 实现Excel文件解析和批量导入
    return Response({})


@api_view(['GET'])
@require_auth
def interview_files_list(request):
    """GET 查询模板文件列表"""
    # TODO: 实现文件列表查询
    return Response({'files': {'file_name': 'template.xlsx', 'file_size': '20KB'}})


@api_view(['POST'])
@require_auth
def interview_files_upload(request):
    """POST 上传模板文件"""
    # TODO: 实现文件上传
    return Response({})


@api_view(['GET'])
@require_auth
def interview_files_download(request):
    """GET 模板下载"""
    # TODO: 实现文件下载
    return Response({})


# ==================== 负面事件 ====================

@api_view(['GET', 'POST'])
@require_auth
def negative_events_list_create(request):
    """GET 分页查询负面事件记录列表 / POST 新建一条负面事件记录"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = NegativeEvent.objects.filter(disabled=False)
        
        if request.query_params.get('std_name'):
            queryset = queryset.filter(student_name__icontains=request.query_params.get('std_name'))
        if request.query_params.get('date_start'):
            try:
                date_start = datetime.strptime(request.query_params.get('date_start'), '%Y-%m-%d').date()
                queryset = queryset.filter(event_date__gte=date_start)
            except:
                pass
        if request.query_params.get('date_end'):
            try:
                date_end = datetime.strptime(request.query_params.get('date_end'), '%Y-%m-%d').date()
                queryset = queryset.filter(event_date__lte=date_end)
            except:
                pass
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'std_name': item.student_name,
                'std_grade': item.grade or '',
                'std_class': item.class_name or '',
                'std_school': item.organization or '',
                'event_content': item.event_details or '',
                'event_date': item.event_date.strftime('%Y-%m-%d') if item.event_date else '',
                'creator': item.created_by or '',
                'create_time': item.created_time.strftime('%Y-%m-%d %H:%M') if item.created_time else '',
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
        data = request.data
        
        try:
            obj = NegativeEvent.objects.create(
                student_name=data.get('std_name'),
                grade=data.get('std_grade', ''),
                class_name=data.get('std_class', ''),
                organization=data.get('std_school', ''),
                event_date=datetime.strptime(data.get('event_date'), '%Y-%m-%d').date() if data.get('event_date') else None,
                event_details=data.get('event_content', ''),
                created_by=data.get('creator', ''),
                disabled=False,
            )
            return Response({'code': '1', 'id': str(obj.id), 'message': '新建成功'})
        except Exception as e:
            return Response({'code': '0', 'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@require_auth
def negative_events_delete(request, id):
    """DELETE 删除一条负面事件记录（软删除）"""
    try:
        NegativeEvent.objects.filter(id=id).update(disabled=True)
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


# ==================== 转介单位 ====================

@api_view(['GET', 'POST'])
@require_auth
def referral_organization_list_create(request):
    """GET 查询转介单位列表 / POST 新建一条转介单位记录"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = ReferralUnit.objects.all()
        
        if request.query_params.get('org_name'):
            queryset = queryset.filter(unit_name__icontains=request.query_params.get('org_name'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'org_name': item.unit_name,
                'org_address': item.address or '',
                'phone': item.contact_phone or '',
                'creator': item.created_by or '',
                'creat_time': item.created_time.strftime('%Y-%m-%d %H:%M') if item.created_time else '',
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
        data = request.data
        
        try:
            obj = ReferralUnit.objects.create(
                unit_name=data.get('org_name'),
                address=data.get('org_address', ''),
                contact_phone=data.get('phone', ''),
                created_by=data.get('creator', ''),
            )
            return Response({'code': '1', 'id': str(obj.id), 'message': '新建成功'})
        except Exception as e:
            return Response({'code': '0', 'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@require_auth
def referral_organization_delete(request, id):
    """DELETE 删除一条转介单位记录"""
    try:
        ReferralUnit.objects.filter(id=id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@require_auth
def referral_organization_name_list(request):
    """GET 查询转介单位名称列表"""
    names = list(ReferralUnit.objects.values_list('unit_name', flat=True))
    return Response({'data': names})


# ==================== 转介管理 ====================

@api_view(['GET', 'POST', 'PUT'])
@require_auth
def referral_management_list_create_update(request):
    """GET 查询转介记录列表 / POST 新建一条转介记录 / PUT 更改一条转介记录"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = StudentReferral.objects.all()
        
        if request.query_params.get('std_name'):
            queryset = queryset.filter(student_name__icontains=request.query_params.get('std_name'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'std_name': item.student_name,
                'std_grade': item.grade or '',
                'std_class': item.class_name or '',
                'std_school': item.school or '',
                'std_gender': item.gender,
                'org_name': item.referral_unit.unit_name if item.referral_unit else '',
                'reason': item.referral_reason or '',
                'time': item.referral_date.strftime('%Y-%m-%d') if item.referral_date else '',
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
        data = request.data
        
        try:
            # 查找或创建转介单位
            org_name = data.get('org_name', '')
            referral_unit = None
            if org_name:
                referral_unit, _ = ReferralUnit.objects.get_or_create(
                    unit_name=org_name,
                    defaults={'created_by': request.admin_user.username if hasattr(request, 'admin_user') else ''}
                )
            
            obj = StudentReferral.objects.create(
                student_name=data.get('std_name'),
                gender=data.get('std_gender'),
                school=data.get('std_school', ''),
                grade=data.get('std_grade', ''),
                class_name=data.get('std_class', ''),
                referral_unit=referral_unit,
                referral_reason=data.get('reason', ''),
                referral_date=datetime.strptime(data.get('time'), '%Y-%m-%d').date() if data.get('time') else None,
                created_by=request.admin_user.username if hasattr(request, 'admin_user') else '',
            )
            return Response({'id': str(obj.id), 'message': '创建成功'})
        except Exception as e:
            return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        data = request.data
        record_id = data.get('id')
        
        if not record_id:
            return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            obj = StudentReferral.objects.get(id=record_id)
            
            # 查找或创建转介单位
            org_name = data.get('org_name', '')
            if org_name:
                referral_unit, _ = ReferralUnit.objects.get_or_create(
                    unit_name=org_name,
                    defaults={'created_by': request.admin_user.username if hasattr(request, 'admin_user') else ''}
                )
                obj.referral_unit = referral_unit
            
            obj.student_name = data.get('std_name', obj.student_name)
            obj.gender = data.get('std_gender', obj.gender)
            obj.school = data.get('std_school', obj.school)
            obj.grade = data.get('std_grade', obj.grade)
            obj.class_name = data.get('std_class', obj.class_name)
            obj.referral_reason = data.get('reason', obj.referral_reason)
            
            if data.get('time'):
                obj.referral_date = datetime.strptime(data.get('time'), '%Y-%m-%d').date()
            
            obj.save()
            return Response({})
        except StudentReferral.DoesNotExist:
            return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@require_auth
def referral_management_delete(request, id):
    """DELETE 删除一条转介记录"""
    try:
        StudentReferral.objects.filter(id=id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

