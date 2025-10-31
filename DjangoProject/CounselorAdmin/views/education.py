"""
健康宣教接口 - 函数式视图
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from CounselorAdmin.models import Category, Article, Notification, BannerModule
from CounselorAdmin.utils import require_auth


# ==================== 栏目管理（已部分实现，补充函数式版本） ====================

@api_view(['GET', 'POST', 'PUT'])
@require_auth
def categories_list_create_update(request):
    """GET 分页查询栏目列表 / POST 新建一条栏目信息 / PUT 修改一条栏目信息"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Category.objects.all().order_by('sort_order', 'created_time')
        
        if request.query_params.get('name'):
            queryset = queryset.filter(category_name__icontains=request.query_params.get('name'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'name': item.category_name,
                'order': str(item.sort_order),
                'create_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S') if item.created_time else '',
                'creator': item.created_by or '',
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
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
    
    elif request.method == 'PUT':
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


@api_view(['DELETE'])
@require_auth
def categories_delete(request, id):
    """DELETE 删除栏目"""
    try:
        Category.objects.filter(id=id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@require_auth
def categories_name_list(request):
    """GET 只查询栏目的名称"""
    names = list(Category.objects.values_list('category_name', flat=True))
    return Response({'data': names})


# ==================== 宣教管理 ====================

@api_view(['GET', 'POST', 'PUT'])
@require_auth
def articles_list_create_update(request):
    """GET 分页查询宣教资讯列表 / POST 创建一条新的资讯 / PUT 修改一条宣教资讯信息"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1)) if request.query_params.get('page') else 1
            page_size = int(request.query_params.get('page_size', 10)) if request.query_params.get('page_size') else 10
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Article.objects.all()
        
        if request.query_params.get('title'):
            queryset = queryset.filter(title__icontains=request.query_params.get('title'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'title': item.title,
                'category_name': item.category.category_name if item.category else '',
                'content': item.content or '',
                'collect_count': item.collect_count,
                'like_count': item.like_count,
                'read_count': item.read_count,
                'created_by': item.created_by or '',
                'created_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S') if item.created_time else '',
                'video': item.video or '',
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
        data = request.data
        
        try:
            # 根据栏目名称查找栏目
            category_name = data.get('category_name')
            category = Category.objects.filter(category_name=category_name).first()
            if not category:
                return Response({'id': None, 'message': '栏目不存在'}, status=status.HTTP_400_BAD_REQUEST)
            
            obj = Article.objects.create(
                category=category,
                title=data.get('title'),
                content=data.get('content', ''),
                created_by=data.get('author', ''),
                video=data.get('video', ''),
            )
            return Response({'id': str(obj.id), 'message': '创建成功'})
        except Exception as e:
            return Response({'id': None, 'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        data = request.data
        article_id = data.get('id')
        
        if not article_id:
            return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            obj = Article.objects.get(id=article_id)
            
            if 'title' in data:
                obj.title = data.get('title')
            if 'content' in data:
                obj.content = data.get('content')
            if 'author' in data:
                obj.created_by = data.get('author')
            if 'resource' in data:
                # resource字段在模型中可能需要映射
                pass
            if 'video' in data:
                obj.video = data.get('video')
            
            obj.save()
            return Response({})
        except Article.DoesNotExist:
            return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@require_auth
def articles_delete(request, id):
    """DELETE 删除一条资讯"""
    try:
        Article.objects.filter(id=id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


# ==================== 通知管理 ====================

@api_view(['GET', 'POST', 'PUT'])
@require_auth
def notification_list_create_update(request):
    """GET 分页查询通知列表 / POST 新建一条通知 / PUT 修改一条通知"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Notification.objects.all()
        
        if request.query_params.get('title'):
            queryset = queryset.filter(title__icontains=request.query_params.get('title'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'title': item.title,
                'isPublished': item.is_published,
                'creator': item.created_by or '',
                'create_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S') if item.created_time else '',
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
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
    
    elif request.method == 'PUT':
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


@api_view(['DELETE'])
@require_auth
def notification_delete(request, id):
    """DELETE 删除一条通知"""
    try:
        Notification.objects.filter(id=id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)


# ==================== Banner管理 ====================

@api_view(['GET', 'POST', 'PUT'])
@require_auth
def banner_list_create_update(request):
    """GET 分页查询banner列表 / POST 新建一条banner / PUT 修改一条banner数据"""
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except (ValueError, TypeError):
            return Response({'message': '分页参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = BannerModule.objects.all()
        
        if request.query_params.get('module'):
            queryset = queryset.filter(module_name__icontains=request.query_params.get('module'))
        
        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        
        data = []
        for item in items:
            data.append({
                'id': str(item.id),
                'module': item.module_name,
                'count': str(item.carousel_count),
                'creator': item.created_by or '',
                'create_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S') if item.created_time else '',
            })
        
        return Response({'total': str(total), 'data': data})
    
    elif request.method == 'POST':
        data = request.data
        
        try:
            # 处理图片上传（简化处理，实际可能需要文件存储）
            images = data.get('images', [])
            if isinstance(images, str):
                images = [images] if images else []
            
            obj = BannerModule.objects.create(
                module_name=data.get('module', ''),
                carousel_count=len(images) if images else int(data.get('count', 0)),
                pictures=images if images else [],
                created_by=request.admin_user.username if hasattr(request, 'admin_user') else '',
            )
            return Response({'id': str(obj.id), 'message': '创建成功'})
        except Exception as e:
            return Response({'message': f'创建失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        data = request.data
        banner_id = data.get('id')
        
        if not banner_id:
            return Response({'message': '缺少id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            obj = BannerModule.objects.get(id=banner_id)
            
            if 'module' in data:
                obj.module_name = data.get('module')
            
            images = data.get('images', [])
            if images:
                if isinstance(images, str):
                    images = [images]
                obj.pictures = images
                obj.carousel_count = len(images)
            elif 'count' in data:
                obj.carousel_count = int(data.get('count'))
            
            obj.save()
            return Response({})
        except BannerModule.DoesNotExist:
            return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'更新失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@require_auth
def banner_delete(request, id):
    """DELETE 删除一条banner数据"""
    try:
        BannerModule.objects.filter(id=id).delete()
        return Response({})
    except Exception:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

