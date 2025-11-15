"""
个人中心相关视图 - 函数式视图
所有接口使用POST方法，参数和鉴权都在请求体JSON中
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from Consultant.models import ConsultationReview, ConsultationOrder
from Consultant.serializers.auth import CounselorUserInfoSerializer
from Consultant.models import CounselorProfile
from Consultant.utils import require_body_auth


# ==================== 个人中心 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def comments(request):
    """POST 获取客户对咨询师的评论"""
    counselor = request.counselor
    data = request.data
    
    # 支持两种参数名：pageSize 和 page_size
    page = int(data.get('page', 1))
    page_size = int(data.get('page_size', data.get('pageSize', 10)))
    
    reviews = ConsultationReview.objects.filter(
        counselor=counselor
    ).order_by('-created_time')
    
    # 分页
    total = reviews.count()
    start = (page - 1) * page_size
    end = start + page_size
    reviews = reviews[start:end]
    
    result_data = []
    for review in reviews:
        # 获取订单信息
        order = review.order
        client_name = order.record.client_name if order and order.record else ''
        
        result_data.append({
            'id': str(review.id),
            'avatar': '',
            'username': client_name,
            'name': client_name,
            'organization': '',
            'time': review.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'content': review.content or '',
            'rating': review.rating
        })
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'total': total,
        'data': result_data
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def user_profile(request):
    """POST 获取用户详情信息"""
    counselor = request.counselor
    
    # 获取咨询师详情
    try:
        profile = counselor.profile
    except CounselorProfile.DoesNotExist:
        profile = None
    
    return Response({
        'code': 0,
        'message': '获取成功',
        'data': {
            'avatar': profile.avatar if profile and profile.avatar else '',
            'username': counselor.username,
            'name': profile.name if profile else counselor.name,
            'phone': counselor.phone,
            'email': counselor.email,
            'graduated_school': profile.graduated_school if profile else '',
            'address': profile.address if profile else '',
            'organization': profile.organization if profile else '',
            'profession': profile.profession if profile else '',
            'expertise': profile.expertise if profile and profile.expertise else [],
            'introduction': profile.introduction if profile else '',
            'education': profile.education if profile else '',
            'skilled_filed': profile.skilled_filed if profile else '',
            'certifications': profile.certifications if profile else '',
            'consultation_count': profile.consultation_count if profile else 0,
            'created_time': profile.created_time.strftime('%Y-%m-%d %H:%M:%S') if profile and profile.created_time else '',
            'serve_type': counselor.serve_type if counselor.serve_type else []
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def update_profile(request):
    """POST 更新用户信息"""
    counselor = request.counselor
    profile_data = request.data.get('profile', {})
    
    if not profile_data:
        return Response({
            'code': 400,
            'message': '缺少profile数据'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 更新咨询师基本信息
    counselor.username = profile_data.get('username', counselor.username)
    counselor.name = profile_data.get('name', counselor.name)
    counselor.phone = profile_data.get('phone', counselor.phone)
    counselor.email = profile_data.get('email', counselor.email)
    counselor.save()
    
    # 更新或创建咨询师详情
    profile, created = CounselorProfile.objects.get_or_create(
        counselor=counselor,
        defaults={'name': counselor.name}
    )
    
    profile.name = profile_data.get('name', profile.name)
    profile.graduated_school = profile_data.get('graduated_school', '')
    profile.address = profile_data.get('address', '')
    profile.organization = profile_data.get('organization', '')
    profile.profession = profile_data.get('profession', '')
    profile.introduction = profile_data.get('introduction', '')
    profile.experience = profile_data.get('experience', '')
    # expertise 可以是数组或字符串
    expertise_data = profile_data.get('expertise', [])
    if isinstance(expertise_data, str):
        profile.expertise = expertise_data.split(',') if expertise_data else []
    else:
        profile.expertise = expertise_data if expertise_data else []
    profile.education = profile_data.get('education', '')
    profile.skilled_filed = profile_data.get('skilled_filed', '')
    profile.certifications = profile_data.get('certifications', '')
    if 'consultation_count' in profile_data:
        profile.consultation_count = profile_data.get('consultation_count', 0)
    profile.save()
    
    # 更新咨询师基本信息的 serve_type
    if 'serve_type' in profile_data:
        counselor.serve_type = profile_data.get('serve_type', [])
        counselor.save()
    
    return Response({
        'code': 0,
        'message': '更新成功'
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def update_avatar(request):
    """POST 更新用户头像"""
    import os
    import uuid
    from django.conf import settings
    
    counselor = request.counselor
    avatar_file = request.FILES.get('avatar')
    
    if not avatar_file:
        return Response({
            'code': 400,
            'message': '缺少头像文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查文件类型（只允许图片）
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    file_name = avatar_file.name.lower()
    file_ext = os.path.splitext(file_name)[1]
    
    if file_ext not in allowed_extensions:
        return Response({
            'code': 400,
            'message': f'不支持的文件格式，只支持：{", ".join(allowed_extensions)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 确保头像存储目录存在
        avatar_dir = os.path.join(settings.BASE_DIR, 'static', 'counselor_avatar')
        os.makedirs(avatar_dir, exist_ok=True)
        
        # 生成唯一文件名（使用UUID + 原始扩展名）
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(avatar_dir, unique_filename)
        
        # 如果咨询师已有头像，删除旧头像
        try:
            profile = counselor.profile
            if profile and profile.avatar:
                old_avatar_path = os.path.join(settings.BASE_DIR, profile.avatar.lstrip('/'))
                if os.path.exists(old_avatar_path):
                    try:
                        os.remove(old_avatar_path)
                    except:
                        pass  # 如果删除失败，继续执行
        except CounselorProfile.DoesNotExist:
            pass
        
        # 保存新头像文件
        with open(file_path, 'wb+') as destination:
            for chunk in avatar_file.chunks():
                destination.write(chunk)
        
        # 生成相对路径（用于存储到数据库）
        # 路径格式：/static/counselor_avatar/filename.jpg
        relative_path = f'/static/counselor_avatar/{unique_filename}'
        
        # 更新或创建咨询师详情记录
        profile, created = CounselorProfile.objects.get_or_create(
            counselor=counselor,
            defaults={'name': counselor.name}
        )
        
        # 更新头像路径
        profile.avatar = relative_path
        profile.save(update_fields=['avatar'])
        
        return Response({
            'code': 0,
            'message': '头像更新成功',
            'data': {
                'avatar': relative_path  # 返回头像相对路径
            }
        })
        
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'头像上传失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

