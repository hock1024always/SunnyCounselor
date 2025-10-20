from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from CounselorApp.models import Counselor, Client
from CounselorAdmin.models import (
    EducationCategory, EducationContent, Notification, Banner,
    ReferralUnit, Student
)
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Initialize sample data for CounselorAdmin'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化CounselorAdmin示例数据...')
        
        # 创建示例宣教栏目
        categories = [
            {'name': '心理健康', 'description': '心理健康相关知识'},
            {'name': '学业指导', 'description': '学习方法和技巧'},
            {'name': '情绪管理', 'description': '情绪调节和管理'},
            {'name': '人际关系', 'description': '社交技巧和沟通'},
        ]
        
        for cat_data in categories:
            category, created = EducationCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'创建宣教栏目: {category.name}')
        
        # 创建示例宣教内容
        contents = [
            {
                'title': '如何应对考试焦虑',
                'category': '心理健康',
                'content_type': 'article',
                'content': '考试焦虑是学生常见的心理问题...',
                'is_published': True
            },
            {
                'title': '高效学习方法分享',
                'category': '学业指导', 
                'content_type': 'article',
                'content': '掌握正确的学习方法可以提高学习效率...',
                'is_published': True
            }
        ]
        
        for content_data in contents:
            category = EducationCategory.objects.get(name=content_data.pop('category'))
            content, created = EducationContent.objects.get_or_create(
                title=content_data['title'],
                category=category,
                defaults=content_data
            )
            if created:
                self.stdout.write(f'创建宣教内容: {content.title}')
        
        # 创建示例通知
        notifications = [
            {
                'title': '系统维护通知',
                'content': '系统将于本周六进行维护，期间可能无法访问。',
                'notification_type': 'system',
                'status': 'published'
            },
            {
                'title': '心理健康讲座通知',
                'content': '本周五下午将举办心理健康讲座，欢迎参加。',
                'notification_type': 'event',
                'status': 'published'
            }
        ]
        
        for notif_data in notifications:
            notification, created = Notification.objects.get_or_create(
                title=notif_data['title'],
                defaults=notif_data
            )
            if created:
                self.stdout.write(f'创建通知: {notification.title}')
        
        # 创建示例转介单位
        referral_units = [
            {
                'name': '市心理卫生中心',
                'unit_type': 'hospital',
                'contact_person': '张医生',
                'phone': '13800138000',
                'address': '北京市朝阳区心理卫生路123号'
            },
            {
                'name': '青少年心理咨询中心',
                'unit_type': 'psychology_center',
                'contact_person': '李老师',
                'phone': '13900139000',
                'address': '北京市海淀区学院路456号'
            }
        ]
        
        for unit_data in referral_units:
            unit, created = ReferralUnit.objects.get_or_create(
                name=unit_data['name'],
                defaults=unit_data
            )
            if created:
                self.stdout.write(f'创建转介单位: {unit.name}')
        
        # 创建示例学生
        students = [
            {
                'name': '张三',
                'gender': 'male',
                'age': 15,
                'student_id': '2023001',
                'school': '北京市第一中学',
                'grade': '高一',
                'class_name': '1班'
            },
            {
                'name': '李四',
                'gender': 'female', 
                'age': 16,
                'student_id': '2023002',
                'school': '北京市第一中学',
                'grade': '高一',
                'class_name': '2班'
            }
        ]
        
        for student_data in students:
            student, created = Student.objects.get_or_create(
                student_id=student_data['student_id'],
                defaults=student_data
            )
            if created:
                self.stdout.write(f'创建学生: {student.name}')
        
        self.stdout.write(
            self.style.SUCCESS('CounselorAdmin示例数据初始化完成！')
        )