from django.test import TestCase
from django.contrib.auth.models import User
from .models import (
    Student, Interview, NegativeEvent, ReferralUnit, ReferralHistory,
    EducationCategory, EducationContent, Notification, Banner,
    CounselorSchedule, ConsultationOrder
)
from CounselorApp.models import Counselor, Consultation, Client
from datetime import datetime, timedelta


class StudentModelTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name='测试学生',
            gender='male',
            age=15,
            student_id='2023001',
            school='测试学校',
            grade='高一',
            class_name='1班'
        )
    
    def test_student_creation(self):
        self.assertEqual(self.student.name, '测试学生')
        self.assertEqual(self.student.gender, 'male')
        self.assertEqual(self.student.school, '测试学校')


class InterviewModelTest(TestCase):
    def setUp(self):
        # 创建用户和咨询师
        self.user = User.objects.create_user(username='testcounselor', password='testpass')
        self.counselor = Counselor.objects.create(
            user=self.user,
            name='测试咨询师',
            gender='male',
            age=30,
            phone='13800138000',
            email='test@example.com'
        )
        
        # 创建学生
        self.student = Student.objects.create(
            name='测试学生',
            gender='male',
            age=15,
            student_id='2023001',
            school='测试学校',
            grade='高一',
            class_name='1班'
        )
        
        self.interview = Interview.objects.create(
            student=self.student,
            counselor=self.counselor,
            interview_date=datetime.now(),
            status='pending'
        )
    
    def test_interview_creation(self):
        self.assertEqual(self.interview.student.name, '测试学生')
        self.assertEqual(self.interview.counselor.name, '测试咨询师')
        self.assertEqual(self.interview.status, 'pending')


class EducationContentModelTest(TestCase):
    def setUp(self):
        self.category = EducationCategory.objects.create(
            name='测试栏目',
            description='测试描述'
        )
        
        self.content = EducationContent.objects.create(
            category=self.category,
            title='测试内容',
            content_type='article',
            content='测试内容正文'
        )
    
    def test_education_content_creation(self):
        self.assertEqual(self.content.title, '测试内容')
        self.assertEqual(self.content.category.name, '测试栏目')
        self.assertEqual(self.content.content_type, 'article')


class NotificationModelTest(TestCase):
    def setUp(self):
        self.notification = Notification.objects.create(
            title='测试通知',
            content='测试通知内容',
            notification_type='system'
        )
    
    def test_notification_creation(self):
        self.assertEqual(self.notification.title, '测试通知')
        self.assertEqual(self.notification.status, 'draft')
        self.assertEqual(self.notification.notification_type, 'system')


class BannerModelTest(TestCase):
    def setUp(self):
        self.banner = Banner.objects.create(
            title='测试Banner',
            image='banners/test.jpg',
            position='home',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
    
    def test_banner_creation(self):
        self.assertEqual(self.banner.title, '测试Banner')
        self.assertEqual(self.banner.position, 'home')
        self.assertTrue(self.banner.is_active)