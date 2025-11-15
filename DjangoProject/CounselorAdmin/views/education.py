"""
健康宣教接口 - 函数式视图
所有接口使用POST方法，参数和鉴权都在请求体JSON中
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from CounselorAdmin.models import Category, Article, Notification, BannerModule
from CounselorAdmin.utils import require_body_auth


# ==================== 栏目管理 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def categories_list(request):
    """POST 分页查询栏目列表"""
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Category.objects.all().order_by('sort_order', 'created_time')
    
    if data.get('name'):
        queryset = queryset.filter(category_name__icontains=data.get('name'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        result_data.append({
            'id': str(item.id),
            'name': item.category_name,
            'order': str(item.sort_order),
            'create_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S') if item.created_time else '',
            'creator': item.created_by or '',
        })
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def categories_create(request):
    """POST 新建一条栏目信息"""
    data = request.data
    
    try:
        obj = Category.objects.create(
            category_name=data.get('name'),
            sort_order=int(data.get('order', 0)),
            created_by=data.get('creator', ''),
        )
        return Response({'id': str(obj.id), 'message': '创建成功'})
    except Exception as e:
        return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def categories_update(request):
    """POST 修改一条栏目信息"""
    data = request.data
    category_id = data.get('id')
    
    if not category_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = Category.objects.get(id=category_id)
        if 'name' in data:
            obj.category_name = data.get('name')
        if 'order' in data:
            obj.sort_order = int(data.get('order'))
        obj.save()
        return Response({})
    except Category.DoesNotExist:
        return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def categories_delete(request):
    """POST 删除栏目"""
    data = request.data
    category_id = data.get('id')
    
    if not category_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        Category.objects.filter(id=category_id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def categories_name_list(request):
    """POST 查询所有栏目的id和名称"""
    categories = Category.objects.all().order_by('sort_order', 'created_time')
    result_data = []
    for category in categories:
        result_data.append({
            'id': str(category.id),
            'category_name': category.category_name,
        })
    return Response({'data': result_data})


# ==================== 宣教管理 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def articles_list(request):
    """POST 分页查询宣教资讯列表"""
    data = request.data
    
    try:
        page = int(data.get('page', 1)) if data.get('page') else 1
        page_size = int(data.get('page_size', 10)) if data.get('page_size') else 10
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Article.objects.all()
    
    if data.get('title'):
        queryset = queryset.filter(title__icontains=data.get('title'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        # 构建视频URL（优先使用上传的视频文件，否则使用外部链接）
        video_url = ''
        if item.video_path:
            video_url = f"/static/{item.video_path}"
        elif item.video:
            video_url = item.video
        
        result_data.append({
            'id': str(item.id),
            'title': item.title,
            'category_name': item.category.category_name if item.category else '',
            'content': item.content or '',
            'collect_count': item.collect_count,
            'like_count': item.like_count,
            'read_count': item.read_count,
            'created_by': item.created_by or '',
            'created_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S') if item.created_time else '',
            'video': video_url,
        })
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def articles_create(request):
    """POST 创建一条新的资讯（支持视频文件上传）"""
    import os
    import time
    from django.conf import settings
    from datetime import datetime
    
    data = request.data
    
    try:
        # 检查必填字段
        if not data.get('category_id') and not data.get('category_name'):
            return Response({'code': '0', 'message': '栏目ID或栏目名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('title'):
            return Response({'code': '0', 'message': '标题不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('type'):
            return Response({'code': '0', 'message': '类型不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('author'):
            return Response({'code': '0', 'message': '作者不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('resource'):
            return Response({'code': '0', 'message': '资源不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('content'):
            return Response({'code': '0', 'message': '内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 优先使用 category_id 查找栏目，如果没有则使用 category_name（向后兼容）
        category = None
        if data.get('category_id'):
            try:
                category = Category.objects.get(id=data.get('category_id'))
            except Category.DoesNotExist:
                return Response({'code': '0', 'message': '栏目不存在'}, status=status.HTTP_400_BAD_REQUEST)
        elif data.get('category_name'):
            category = Category.objects.filter(category_name=data.get('category_name')).first()
            if not category:
                return Response({'code': '0', 'message': '栏目不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 处理视频文件上传
        video_path = ''
        if 'video' in request.FILES:
            uploaded_video = request.FILES['video']
            # 检查文件类型（视频格式）
            allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
            file_ext = os.path.splitext(uploaded_video.name)[1].lower()
            if file_ext not in allowed_extensions:
                return Response({'code': '0', 'message': '不支持的视频格式，请上传mp4、avi、mov、wmv、flv、mkv或webm格式的视频'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 确保目录存在
            article_video_dir = os.path.join(settings.BASE_DIR, 'static', 'article_video')
            os.makedirs(article_video_dir, exist_ok=True)
            
            # 生成文件名：时间_创建者_序号.扩展名
            timestamp = int(time.time() * 1000)
            author = data.get('author', 'author').replace(' ', '_')
            # 使用时间戳作为序号确保唯一性
            file_name = f"{timestamp}_{author}{file_ext}"
            
            # 保存文件
            file_path = os.path.join(article_video_dir, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_video.chunks():
                    destination.write(chunk)
            
            # 保存相对路径到数据库（相对于static目录）
            video_path = f"article_video/{file_name}"
        
        # 处理创建时间
        created_time = None
        if data.get('create_time'):
            try:
                created_time = datetime.strptime(data.get('create_time'), '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    created_time = datetime.strptime(data.get('create_time'), '%Y-%m-%d')
                except:
                    pass
        
        obj = Article.objects.create(
            category=category,
            title=data.get('title'),
            content=data.get('content', ''),
            created_by=data.get('author', ''),
            video=data.get('video', ''),  # 外部视频链接（如果有）
            video_path=video_path,  # 上传的视频文件路径
            resource=data.get('resource', ''),
            type=data.get('type', ''),
        )
        
        # 如果指定了创建时间，更新它
        if created_time:
            obj.created_time = created_time
            obj.save()
        
        return Response({'code': '1', 'id': str(obj.id), 'message': '创建成功'})
    except Exception as e:
        return Response({'code': '0', 'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def articles_detail(request):
    """POST 查询一条资讯的详情信息"""
    data = request.data
    article_id = data.get('id')
    
    if not article_id:
        return Response({'code': '0', 'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = Article.objects.select_related('category').get(id=article_id)
        
        # 构建视频URL（优先使用上传的视频文件，否则使用外部链接）
        video_url = ''
        if obj.video_path:
            video_url = f"/static/{obj.video_path}"
        elif obj.video:
            video_url = obj.video
        
        result = {
            'code': '1',
            'data': {
                'id': str(obj.id),
                'title': obj.title,
                'category_name': obj.category.category_name if obj.category else '',
                'content': obj.content or '',
                'collect_count': obj.collect_count,
                'like_count': obj.like_count,
                'read_count': obj.read_count,
                'created_by': obj.created_by or '',
                'created_time': obj.created_time.strftime('%Y-%m-%d %H:%M:%S') if obj.created_time else '',
                'video': video_url,
                'resource': obj.resource or '',
                'type': obj.type or '',
            }
        }
        
        return Response(result)
    except Article.DoesNotExist:
        return Response({'code': '0', 'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'code': '0', 'message': f'查询失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def articles_update(request):
    """POST 修改一条宣教资讯信息（支持视频文件更新）"""
    import os
    import time
    from django.conf import settings
    
    data = request.data
    article_id = data.get('id')
    
    if not article_id:
        return Response({'code': '0', 'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = Article.objects.get(id=article_id)
        
        # 处理视频文件更新（如果上传了新视频）
        if 'video' in request.FILES:
            # 删除旧视频文件（如果存在）
            if obj.video_path:
                old_video_path = os.path.join(settings.BASE_DIR, 'static', obj.video_path)
                if os.path.exists(old_video_path):
                    try:
                        os.remove(old_video_path)
                    except Exception:
                        pass  # 如果删除失败，继续处理新视频
            
            # 处理新视频上传
            uploaded_video = request.FILES['video']
            # 检查文件类型
            allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
            file_ext = os.path.splitext(uploaded_video.name)[1].lower()
            if file_ext not in allowed_extensions:
                return Response({'code': '0', 'message': '不支持的视频格式，请上传mp4、avi、mov、wmv、flv、mkv或webm格式的视频'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 确保目录存在
            article_video_dir = os.path.join(settings.BASE_DIR, 'static', 'article_video')
            os.makedirs(article_video_dir, exist_ok=True)
            
            # 生成新文件名
            timestamp = int(time.time() * 1000)
            author = data.get('author', obj.created_by or 'author').replace(' ', '_')
            file_name = f"{timestamp}_{author}{file_ext}"
            
            # 保存新文件
            file_path = os.path.join(article_video_dir, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_video.chunks():
                    destination.write(chunk)
            
            # 更新视频路径
            obj.video_path = f"article_video/{file_name}"
            obj.video = ''  # 清空外部链接，因为使用上传的文件
        
        # 更新栏目信息（优先使用 category_id，如果没有则使用 category_name）
        if 'category_id' in data or 'category_name' in data:
            category = None
            if data.get('category_id'):
                try:
                    category = Category.objects.get(id=data.get('category_id'))
                except Category.DoesNotExist:
                    return Response({'code': '0', 'message': '栏目不存在'}, status=status.HTTP_400_BAD_REQUEST)
            elif data.get('category_name'):
                category = Category.objects.filter(category_name=data.get('category_name')).first()
                if not category:
                    return Response({'code': '0', 'message': '栏目不存在'}, status=status.HTTP_400_BAD_REQUEST)
            
            if category:
                obj.category = category
        
        if 'title' in data:
            obj.title = data.get('title')
        if 'content' in data:
            obj.content = data.get('content')
        if 'author' in data:
            obj.created_by = data.get('author')
        if 'resource' in data:
            obj.resource = data.get('resource')
        if 'type' in data:
            obj.type = data.get('type')
        if 'video' in data and 'video' not in request.FILES:  # 如果提供的是外部链接而不是文件
            obj.video = data.get('video')
            obj.video_path = ''  # 清空上传的文件路径
        
        obj.save()
        return Response({'code': '1', 'message': '更新成功'})
    except Article.DoesNotExist:
        return Response({'code': '0', 'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'code': '0', 'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def articles_delete(request):
    """POST 删除一条资讯（同时删除对应的视频文件）"""
    import os
    from django.conf import settings
    
    data = request.data
    article_id = data.get('id')
    
    if not article_id:
        return Response({'code': '0', 'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = Article.objects.filter(id=article_id).first()
        if not obj:
            return Response({'code': '0', 'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 删除对应的视频文件（如果存在）
        if obj.video_path:
            video_path = os.path.join(settings.BASE_DIR, 'static', obj.video_path)
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except Exception:
                    pass  # 如果删除失败，继续删除数据库记录
        
        # 删除数据库记录
        obj.delete()
        return Response({'code': '1', 'message': '删除成功'})
    except Exception as e:
        return Response({'code': '0', 'message': f'删除失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 通知管理 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def notification_list(request):
    """POST 分页查询通知列表"""
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Notification.objects.all()
    
    if data.get('title'):
        queryset = queryset.filter(title__icontains=data.get('title'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        result_data.append({
            'id': str(item.id),
            'title': item.title,
            'isPublished': item.is_published,
            'creator': item.created_by or '',
            'create_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S') if item.created_time else '',
        })
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def notification_create(request):
    """POST 新建一条通知"""
    data = request.data
    
    try:
        obj = Notification.objects.create(
            title=data.get('title'),
            content=data.get('content', ''),
            is_published=data.get('isPublished', 'false').lower() == 'true' if isinstance(data.get('isPublished'), str) else bool(data.get('isPublished')),
            created_by=request.admin_user.username if hasattr(request, 'admin_user') else '',
        )
        return Response({'id': str(obj.id), 'message': '创建成功'})
    except Exception as e:
        return Response({'id': None, 'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def notification_update(request):
    """POST 修改一条通知"""
    data = request.data
    notification_id = data.get('id')
    
    if not notification_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = Notification.objects.get(id=notification_id)
        
        if 'title' in data:
            obj.title = data.get('title')
        if 'content' in data:
            obj.content = data.get('content')
        if 'isPublished' in data:
            obj.is_published = data.get('isPublished') if isinstance(data.get('isPublished'), bool) else data.get('isPublished', 'false').lower() == 'true'
        
        obj.save()
        return Response({})
    except Notification.DoesNotExist:
        return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def notification_delete(request):
    """POST 删除一条通知"""
    data = request.data
    notification_id = data.get('id')
    
    if not notification_id:
        return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        Notification.objects.filter(id=notification_id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


# ==================== Banner管理 ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def banner_list(request):
    """POST 分页查询banner列表"""
    data = request.data
    
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
    except (ValueError, TypeError):
        return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = BannerModule.objects.all()
    
    if data.get('module'):
        queryset = queryset.filter(module_name__icontains=data.get('module'))
    
    total = queryset.count()
    start = (page - 1) * page_size
    items = queryset[start:start + page_size]
    
    result_data = []
    for item in items:
        # 构建图片URL数组（如果存在图片路径）
        images = []
        if item.pictures:
            if isinstance(item.pictures, list):
                for pic_path in item.pictures:
                    if pic_path:
                        images.append(f"/static/{pic_path}")
            elif isinstance(item.pictures, str):
                images.append(f"/static/{item.pictures}")
        
        result_data.append({
            'id': str(item.id),
            'module': item.module_name,
            'count': str(item.carousel_count),
            'images': images,
            'creator': item.created_by or '',
            'create_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S') if item.created_time else '',
        })
    
    return Response({'total': str(total), 'data': result_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def banner_create(request):
    """POST 新建一条banner（支持图片文件上传）"""
    import os
    from django.conf import settings
    from datetime import datetime
    
    data = request.data
    
    try:
        # 先创建记录以获取banner_id
        obj = BannerModule.objects.create(
            module_name=data.get('module', ''),
            carousel_count=0,
            pictures=[],
            created_by=request.admin_user.username if hasattr(request, 'admin_user') else '',
        )
        
        banner_id = obj.id
        date_str = datetime.now().strftime('%Y%m%d')
        
        # 处理图片上传
        image_paths = []
        if 'images' in request.FILES:
            # 支持多个图片文件上传
            uploaded_images = request.FILES.getlist('images')
            
            # 确保目录存在
            banner_photo_dir = os.path.join(settings.BASE_DIR, 'static', 'banner_photo')
            os.makedirs(banner_photo_dir, exist_ok=True)
            
            for index, uploaded_image in enumerate(uploaded_images):
                # 检查文件类型（图片格式）
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                file_ext = os.path.splitext(uploaded_image.name)[1].lower()
                if file_ext not in allowed_extensions:
                    # 如果格式不支持，跳过这个文件
                    continue
                
                # 生成文件名：date_banner_id_序号.扩展名
                file_name = f"{date_str}_{banner_id}_{index + 1}{file_ext}"
                
                # 保存文件
                file_path = os.path.join(banner_photo_dir, file_name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_image.chunks():
                        destination.write(chunk)
                
                # 保存相对路径（相对于static目录）
                image_paths.append(f"banner_photo/{file_name}")
        
        # 更新记录，保存图片路径和数量
        obj.pictures = image_paths
        obj.carousel_count = len(image_paths)
        obj.save()
        
        return Response({'code': '1', 'id': str(obj.id), 'message': '创建成功'})
    except Exception as e:
        return Response({'code': '0', 'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def banner_update(request):
    """POST 修改一条banner数据（支持图片文件更新）"""
    import os
    from django.conf import settings
    from datetime import datetime
    
    data = request.data
    banner_id = data.get('id')
    
    if not banner_id:
        return Response({'code': '0', 'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = BannerModule.objects.get(id=banner_id)
        
        # 处理图片更新（如果上传了新图片）
        if 'images' in request.FILES:
            # 删除旧图片文件（如果存在）
            if obj.pictures:
                old_images = obj.pictures if isinstance(obj.pictures, list) else [obj.pictures]
                for pic_path in old_images:
                    if pic_path:
                        old_image_path = os.path.join(settings.BASE_DIR, 'static', pic_path)
                        if os.path.exists(old_image_path):
                            try:
                                os.remove(old_image_path)
                            except Exception:
                                pass  # 如果删除失败，继续处理新图片
            
            # 处理新图片上传
            uploaded_images = request.FILES.getlist('images')
            date_str = datetime.now().strftime('%Y%m%d')
            
            # 确保目录存在
            banner_photo_dir = os.path.join(settings.BASE_DIR, 'static', 'banner_photo')
            os.makedirs(banner_photo_dir, exist_ok=True)
            
            image_paths = []
            for index, uploaded_image in enumerate(uploaded_images):
                # 检查文件类型
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                file_ext = os.path.splitext(uploaded_image.name)[1].lower()
                if file_ext not in allowed_extensions:
                    continue
                
                # 生成新文件名：date_banner_id_序号.扩展名
                file_name = f"{date_str}_{banner_id}_{index + 1}{file_ext}"
                
                # 保存新文件
                file_path = os.path.join(banner_photo_dir, file_name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_image.chunks():
                        destination.write(chunk)
                
                # 保存相对路径
                image_paths.append(f"banner_photo/{file_name}")
            
            # 更新图片路径和数量
            obj.pictures = image_paths
            obj.carousel_count = len(image_paths)
        
        # 更新其他字段
        if 'module' in data:
            obj.module_name = data.get('module')
        
        obj.save()
        return Response({'code': '1', 'message': '更新成功'})
    except BannerModule.DoesNotExist:
        return Response({'code': '0', 'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'code': '0', 'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # 禁用DRF默认权限检查
@require_body_auth  # 业务逻辑中的鉴权
def banner_delete(request):
    """POST 删除一条banner数据（同时删除对应的图片文件）"""
    import os
    from django.conf import settings
    
    data = request.data
    banner_id = data.get('id')
    
    if not banner_id:
        return Response({'code': '0', 'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        obj = BannerModule.objects.filter(id=banner_id).first()
        if not obj:
            return Response({'code': '0', 'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 删除对应的图片文件（如果存在）
        if obj.pictures:
            images = obj.pictures if isinstance(obj.pictures, list) else [obj.pictures]
            for pic_path in images:
                if pic_path:
                    image_path = os.path.join(settings.BASE_DIR, 'static', pic_path)
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                        except Exception:
                            pass  # 如果删除失败，继续删除其他文件
        
        # 删除数据库记录
        obj.delete()
        return Response({'code': '1', 'message': '删除成功'})
    except Exception as e:
        return Response({'code': '0', 'message': f'删除失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
