"""
干预管理接口 - 函数式视图
所有接口使用POST方法，参数和鉴权都在请求体JSON中
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from datetime import datetime

from CounselorAdmin.models import InterviewAssessment, NegativeEvent, ReferralUnit, StudentReferral
from CounselorAdmin.utils import require_body_auth
from django.conf import settings
from django.http import FileResponse, HttpResponse
import os
import mimetypes
import io
import zipfile


# ==================== 访谈评估 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def interview_list(request):
    """POST 分页查询访谈记录列表"""
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = InterviewAssessment.objects.all()
    
    # 过滤条件（从body中获取）
    if data.get('std_name'):
        queryset = queryset.filter(student_name__icontains=data.get('std_name'))
    if data.get('std_grade'):
        queryset = queryset.filter(grade=data.get('std_grade'))
    if data.get('std_class'):
        queryset = queryset.filter(class_name=data.get('std_class'))
    if data.get('std_school'):
        queryset = queryset.filter(organization=data.get('std_school'))
    if data.get('interview_cout'):
        queryset = queryset.filter(interview_count=int(data.get('interview_cout')))
    if data.get('interview_status'):
        queryset = queryset.filter(interview_status=data.get('interview_status'))
    if data.get('interview_type'):
        queryset = queryset.filter(interview_type=data.get('interview_type'))
    if data.get('doctor_evaluation'):
        queryset = queryset.filter(doctor_assessment=data.get('doctor_evaluation'))
    if data.get('follow_up_plan'):
        queryset = queryset.filter(follow_up_plan=data.get('follow_up_plan'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        result_data.append({
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
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def interview_create(request):
    """POST 新建一条访谈记录"""
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


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def interview_delete(request):
    """POST 删除一条访谈记录"""
    data = request.data
    record_id = data.get('id')
    
    if not record_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        InterviewAssessment.objects.filter(id=record_id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def interview_upload(request):
    """POST 批量导入访谈记录"""
    import os
    import pandas as pd
    from django.conf import settings
    
    # 检查是否有文件上传
    if 'file' not in request.FILES:
        return Response({'code': '0', 'message': '请上传Excel文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    
    # 检查文件扩展名
    file_name = uploaded_file.name
    if not (file_name.endswith('.xls') or file_name.endswith('.xlsx')):
        return Response({'code': '0', 'message': '只支持.xls或.xlsx格式的Excel文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 确保interview_form目录存在
        interview_form_dir = os.path.join(settings.BASE_DIR, 'static', 'interview_form')
        os.makedirs(interview_form_dir, exist_ok=True)
        
        # 生成唯一文件名（使用时间戳）
        import time
        timestamp = int(time.time() * 1000)
        file_ext = os.path.splitext(file_name)[1]
        unique_filename = f"{timestamp}_{file_name}"
        file_path = os.path.join(interview_form_dir, unique_filename)
        
        # 保存文件到static/interview_form目录
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # 读取Excel文件
        try:
            # 尝试读取Excel文件
            df = pd.read_excel(file_path, engine='openpyxl' if file_ext == '.xlsx' else None)
        except Exception as e:
            return Response({'code': '0', 'message': f'Excel文件读取失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查必要的列是否存在（根据数据库模型，student_name是必填的）
        # 定义Excel列名映射（可能的列名变体）
        column_mapping = {
            '学生姓名': 'student_name',
            '姓名': 'student_name',
            '所属机构': 'organization',
            '机构': 'organization',
            'std_school': 'organization',
            '年级': 'grade',
            'std_grade': 'grade',
            '班级': 'class_name',
            'std_class': 'class_name',
            '访谈次数': 'interview_count',
            'interview_count': 'interview_count',
            '访谈状态': 'interview_status',
            'interview_status': 'interview_status',
            '访谈类型': 'interview_type',
            'interview_type': 'interview_type',
            '类型': 'interview_type',
            '医生评定': 'doctor_assessment',
            'doctor_evaluation': 'doctor_assessment',
            '后续计划': 'follow_up_plan',
            'follow_up_plan': 'follow_up_plan',
        }
        
        # 标准化列名
        df.columns = [column_mapping.get(str(col).strip(), str(col).strip()) for col in df.columns]
        
        # 检查是否有student_name列
        if 'student_name' not in df.columns:
            # 尝试查找可能的姓名列
            name_cols = [col for col in df.columns if '姓名' in col or 'name' in col.lower()]
            if not name_cols:
                return Response({'code': '0', 'message': 'Excel文件中必须包含"学生姓名"或"姓名"列'}, status=status.HTTP_400_BAD_REQUEST)
            df = df.rename(columns={name_cols[0]: 'student_name'})
        
        # 批量创建记录
        success_count = 0
        error_rows = []
        to_create = []
        
        for index, row in df.iterrows():
            try:
                # 获取字段值，处理空值和NaN
                student_name = str(row.get('student_name', '')).strip()
                if not student_name or student_name == 'nan':
                    error_rows.append({'row': index + 2, 'error': '学生姓名不能为空'})
                    continue
                
                organization = str(row.get('organization', '')).strip() if pd.notna(row.get('organization')) else ''
                grade = str(row.get('grade', '')).strip() if pd.notna(row.get('grade')) else ''
                class_name = str(row.get('class_name', '')).strip() if pd.notna(row.get('class_name')) else ''
                
                # 处理访谈次数
                interview_count = 1
                if pd.notna(row.get('interview_count')):
                    try:
                        interview_count = int(float(row.get('interview_count')))
                    except:
                        interview_count = 1
                
                # 处理访谈状态
                interview_status = '待处理'
                status_val = row.get('interview_status')
                if pd.notna(status_val):
                    status_str = str(status_val).strip()
                    if status_str in ['待处理', '进行中', '已完成']:
                        interview_status = status_str
                
                interview_type = str(row.get('interview_type', '')).strip() if pd.notna(row.get('interview_type')) else ''
                doctor_assessment = str(row.get('doctor_assessment', '')).strip() if pd.notna(row.get('doctor_assessment')) else ''
                follow_up_plan = str(row.get('follow_up_plan', '')).strip() if pd.notna(row.get('follow_up_plan')) else ''
                
                to_create.append(InterviewAssessment(
                    student_name=student_name,
                    organization=organization,
                    grade=grade,
                    class_name=class_name,
                    interview_count=interview_count,
                    interview_status=interview_status,
                    interview_type=interview_type,
                    doctor_assessment=doctor_assessment,
                    follow_up_plan=follow_up_plan,
                ))
            except Exception as e:
                error_rows.append({'row': index + 2, 'error': f'第{index + 2}行数据错误: {str(e)}'})
        
        # 批量入库
        if to_create:
            InterviewAssessment.objects.bulk_create(to_create, batch_size=500)
            success_count = len(to_create)
        
        # 返回结果
        result = {
            'code': '1',
            'message': f'成功导入{success_count}条记录',
            'success_count': success_count,
            'total_rows': len(df),
            'error_count': len(error_rows),
        }
        
        if error_rows:
            result['errors'] = error_rows[:10]  # 最多返回10个错误
        
        return Response(result)
        
    except Exception as e:
        return Response({'code': '0', 'message': f'导入失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@require_body_auth
def interview_files_list(request):
    """POST 查询模板文件列表（返回文件名与大小）"""
    templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    if not os.path.isdir(templates_dir):
        return Response({'files': []})
    result = []
    for name in os.listdir(templates_dir):
        path = os.path.join(templates_dir, name)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            result.append({'file_name': name, 'file_size': size})
    return Response({'files': result})


@api_view(['POST'])
@permission_classes([AllowAny])
@require_body_auth
def interview_files_upload(request):
    """POST 上传模板文件到templates目录（支持多个文件）"""
    templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    # 支持多个文件上传，可以是'file'或'files'字段
    uploaded_files = []
    if 'files' in request.FILES:
        # 如果是files字段（多个文件）
        files_list = request.FILES.getlist('files')
        uploaded_files.extend(files_list)
    elif 'file' in request.FILES:
        # 如果是file字段（单个文件，也支持）
        uploaded_files.append(request.FILES['file'])
    
    if not uploaded_files:
        return Response({'message': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    saved_files = []
    for uploaded_file in uploaded_files:
        filename = os.path.basename(uploaded_file.name)
        save_path = os.path.join(templates_dir, filename)
        
        with open(save_path, 'wb+') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
        
        saved_files.append(filename)
    
    if len(saved_files) == 1:
        return Response({'message': '上传成功', 'file': saved_files[0]})
    else:
        return Response({'message': '上传成功', 'files': saved_files, 'count': len(saved_files)})


@api_view(['POST'])
@permission_classes([AllowAny])
@require_body_auth
def interview_files_download(request):
    """POST 下载模板文件（单个直接返回，多个打包zip返回）"""
    templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    
    filenames = request.data.get('filenames') or request.data.get('files')
    if not filenames:
        return Response({'message': '请提供要下载的文件名数组'}, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(filenames, str):
        # 逗号分隔或单字符串
        filenames = [x.strip() for x in filenames.split(',') if x.strip()]
    if not isinstance(filenames, (list, tuple)):
        return Response({'message': 'filenames格式错误，应为数组或逗号分隔字符串'}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'message': '文件不存在', 'missing': missing}, status=status.HTTP_404_NOT_FOUND)

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


# ==================== 负面事件 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def negative_events_list(request):
    """POST 分页查询负面事件记录列表"""
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = NegativeEvent.objects.filter(disabled=False)
    
    if data.get('std_name'):
        queryset = queryset.filter(student_name__icontains=data.get('std_name'))
    if data.get('date_start'):
        try:
            date_start = datetime.strptime(data.get('date_start'), '%Y-%m-%d').date()
            queryset = queryset.filter(event_date__gte=date_start)
        except:
            pass
    if data.get('date_end'):
        try:
            date_end = datetime.strptime(data.get('date_end'), '%Y-%m-%d').date()
            queryset = queryset.filter(event_date__lte=date_end)
        except:
            pass
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        result_data.append({
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
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def negative_events_create(request):
    """POST 新建一条负面事件记录"""
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


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def negative_events_delete(request):
    """POST 删除一条负面事件记录（软删除）"""
    data = request.data
    record_id = data.get('id')
    
    if not record_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        NegativeEvent.objects.filter(id=record_id).update(disabled=True)
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


# ==================== 转介单位 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def referral_organization_list(request):
    """POST 查询转介单位列表"""
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = ReferralUnit.objects.all()
    
    if data.get('org_name'):
        queryset = queryset.filter(unit_name__icontains=data.get('org_name'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        result_data.append({
            'id': str(item.id),
            'org_name': item.unit_name,
            'org_address': item.address or '',
            'phone': item.contact_phone or '',
            'creator': item.created_by or '',
            'creat_time': item.created_time.strftime('%Y-%m-%d %H:%M') if item.created_time else '',
        })
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def referral_organization_create(request):
    """POST 新建一条转介单位记录"""
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


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def referral_organization_delete(request):
    """POST 删除一条转介单位记录"""
    data = request.data
    record_id = data.get('id')
    
    if not record_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        ReferralUnit.objects.filter(id=record_id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def referral_organization_name_list(request):
    """POST 查询转介单位名称列表"""
    names = list(ReferralUnit.objects.values_list('unit_name', flat=True))
    return Response({'data': names})


# ==================== 转介管理 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def referral_management_list(request):
    """POST 查询转介记录列表"""
    from django.conf import settings
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = StudentReferral.objects.select_related('referral_unit').all()
    
    if data.get('std_name'):
        queryset = queryset.filter(student_name__icontains=data.get('std_name'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        # 构建图片URL（如果存在图片路径）
        image_url = ''
        if item.image_path:
            # 返回可以访问的URL路径
            image_url = f"/static/{item.image_path}"
        
        result_data.append({
            'id': str(item.id),
            'std_name': item.student_name,
            'std_grade': item.grade or '',
            'std_class': item.class_name or '',
            'std_school': item.school or '',
            'std_gender': item.gender,
            'org_name': item.referral_unit.unit_name if item.referral_unit else '',
            'reason': item.referral_reason or '',
            'time': item.referral_date.strftime('%Y-%m-%d') if item.referral_date else '',
            'image': image_url,
        })
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def referral_management_create(request):
    """POST 新建一条转介记录（支持图片上传）"""
    import os
    import time
    from django.conf import settings
    
    data = request.data
    
    try:
        # 处理图片上传
        image_path = ''
        if 'image' in request.FILES:
            uploaded_image = request.FILES['image']
            # 检查文件类型（图片格式）
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = os.path.splitext(uploaded_image.name)[1].lower()
            if file_ext not in allowed_extensions:
                return Response({'message': '不支持的图片格式，请上传jpg、png、gif、bmp或webp格式的图片'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 确保目录存在
            referral_image_dir = os.path.join(settings.BASE_DIR, 'static', 'referral_image')
            os.makedirs(referral_image_dir, exist_ok=True)
            
            # 生成文件名：name_time_序号.扩展名
            student_name = data.get('name', 'student').replace(' ', '_')
            timestamp = int(time.time() * 1000)
            # 使用序号（可以是记录ID，但这里先用时间戳确保唯一性）
            file_name = f"{student_name}_{timestamp}{file_ext}"
            
            # 保存文件
            file_path = os.path.join(referral_image_dir, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)
            
            # 保存相对路径到数据库（相对于static目录）
            image_path = f"referral_image/{file_name}"
        
        # 查找或创建转介单位
        org_name = data.get('organization', '')
        referral_unit = None
        if org_name:
            referral_unit, _ = ReferralUnit.objects.get_or_create(
                unit_name=org_name,
                defaults={'created_by': request.admin_user.username if hasattr(request, 'admin_user') else ''}
            )
        
        obj = StudentReferral.objects.create(
            student_name=data.get('name', ''),
            gender=data.get('std_gender', '男'),  # 如果没有提供，默认值
            school=data.get('std_school', ''),
            grade=data.get('std_grade', ''),
            class_name=data.get('std_class', ''),
            referral_unit=referral_unit,
            referral_reason=data.get('reason', ''),
            referral_date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else None,
            image_path=image_path,
            created_by=request.admin_user.username if hasattr(request, 'admin_user') else '',
        )
        return Response({'code': '1', 'id': str(obj.id), 'message': '创建成功'})
    except Exception as e:
        return Response({'code': '0', 'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def referral_management_update(request):
    """POST 更改一条转介记录（支持图片更新）"""
    import os
    import time
    from django.conf import settings
    
    data = request.data
    record_id = data.get('id')
    
    if not record_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = StudentReferral.objects.get(id=record_id)
        
        # 处理图片更新（如果上传了新图片）
        if 'image' in request.FILES:
            # 删除旧图片（如果存在）
            if obj.image_path:
                old_image_path = os.path.join(settings.BASE_DIR, 'static', obj.image_path)
                if os.path.exists(old_image_path):
                    try:
                        os.remove(old_image_path)
                    except Exception:
                        pass  # 如果删除失败，继续处理新图片
            
            # 处理新图片上传
            uploaded_image = request.FILES['image']
            # 检查文件类型
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = os.path.splitext(uploaded_image.name)[1].lower()
            if file_ext not in allowed_extensions:
                return Response({'message': '不支持的图片格式，请上传jpg、png、gif、bmp或webp格式的图片'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 确保目录存在
            referral_image_dir = os.path.join(settings.BASE_DIR, 'static', 'referral_image')
            os.makedirs(referral_image_dir, exist_ok=True)
            
            # 生成新文件名
            student_name = data.get('name', obj.student_name).replace(' ', '_')
            timestamp = int(time.time() * 1000)
            file_name = f"{student_name}_{timestamp}{file_ext}"
            
            # 保存新文件
            file_path = os.path.join(referral_image_dir, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)
            
            # 更新图片路径
            obj.image_path = f"referral_image/{file_name}"
        
        # 查找或创建转介单位
        org_name = data.get('organization', '')
        if org_name:
            referral_unit, _ = ReferralUnit.objects.get_or_create(
                unit_name=org_name,
                defaults={'created_by': request.admin_user.username if hasattr(request, 'admin_user') else ''}
            )
            obj.referral_unit = referral_unit
        
        # 更新其他字段
        if 'name' in data:
            obj.student_name = data.get('name')
        if 'std_gender' in data:
            obj.gender = data.get('std_gender')
        if 'std_school' in data:
            obj.school = data.get('std_school')
        if 'std_grade' in data:
            obj.grade = data.get('std_grade')
        if 'std_class' in data:
            obj.class_name = data.get('std_class')
        if 'reason' in data:
            obj.referral_reason = data.get('reason')
        if 'date' in data:
            obj.referral_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else None
        
        obj.save()
        return Response({'code': '1', 'message': '更新成功'})
    except StudentReferral.DoesNotExist:
        return Response({'code': '0', 'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'code': '0', 'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def referral_management_delete(request):
    """POST 删除一条转介记录（同时删除对应的图片文件）"""
    import os
    from django.conf import settings
    
    data = request.data
    record_id = data.get('id')
    
    if not record_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = StudentReferral.objects.filter(id=record_id).first()
        if not obj:
            return Response({'code': '0', 'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 删除对应的图片文件（如果存在）
        if obj.image_path:
            image_path = os.path.join(settings.BASE_DIR, 'static', obj.image_path)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception:
                    pass  # 如果删除失败，继续删除数据库记录
        
        # 删除数据库记录
        obj.delete()
        return Response({'code': '1', 'message': '删除成功'})
    except Exception as e:
        return Response({'code': '0', 'message': f'删除失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def interview_grade_list(request):
    """POST 获取访谈评估表中所有年级名字（不重复）"""
    # 查询所有非空的年级，去重并排序
    grades = InterviewAssessment.objects.exclude(grade__isnull=True).exclude(grade='').values_list('grade', flat=True).distinct().order_by('grade')
    grade_list = list(grades)
    return Response({'data': grade_list})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def interview_class_list(request):
    """POST 获取访谈评估表中所有班级名字（不重复）"""
    # 查询所有非空的班级，去重并排序
    classes = InterviewAssessment.objects.exclude(class_name__isnull=True).exclude(class_name='').values_list('class_name', flat=True).distinct().order_by('class_name')
    class_list = list(classes)
    return Response({'data': class_list})