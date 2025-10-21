import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from CounselorAdmin.models import Student, Interview, NegativeEvent
from CounselorApp.models import Counselor, Consultation, Client
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestCounselorAdminAPI:
    """CounselorAdmin API测试类"""

    def test_student_list(self):
        """测试学生列表API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        Student.objects.create(
            name='学生1',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        Student.objects.create(
            name='学生2',
            student_id='20230002',
            gender='female',
            age=19,
            grade='大一',
            class_name='2班',
            school='测试大学'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:student-list')
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
        # 检查结果中包含两个学生，不依赖特定顺序
        student_names = [student['name'] for student in response.data['results']]
        assert '学生1' in student_names
        assert '学生2' in student_names

    def test_student_create(self):
        """测试学生创建API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:student-list')
        data = {
            'name': '新学生',
            'student_id': '20230003',
            'gender': 'male',
            'age': 18,
            'grade': '大一',
            'class_name': '1班',
            'school': '测试大学'
        }
        response = client.post(url, data, format='json')
        
        # 验证响应
        assert response.status_code == 201
        assert response.data['name'] == '新学生'
        assert Student.objects.count() == 1

    def test_student_detail(self):
        """测试学生详情API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:student-detail', args=[student.id])
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert response.data['name'] == '测试学生'
        assert response.data['student_id'] == '20230001'

    def test_interview_list(self):
        """测试访谈记录列表API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        
        # 创建咨询师用于关联
        counselor_user = User.objects.create_user(
            username='counselor_user',
            password='counselorpass123',
            email='counselor@test.com'
        )
        counselor = Counselor.objects.create(
            user=counselor_user,
            name='张老师',
            gender='male',
            age=35,
            phone='13800138000',
            email='counselor@test.com',
            service_types=['academic', 'emotional']
        )
        
        Interview.objects.create(
            student=student,
            counselor=counselor,
            interview_date='2025-10-20T10:00:00Z',
            status='completed',
            assessment_level='low',
            interview_notes='学生反映学习压力大',
            follow_up_plan='建议减轻课业负担'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:interview-list')
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['counselor_name'] == '张老师'

    def test_negative_event_list(self):
        """测试负面事件列表API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        
        NegativeEvent.objects.create(
            student=student,
            event_date='2025-10-19',
            event_type='学业问题',
            description='期中考试不及格',
            severity='中等',
            handling_measures='安排补考和辅导',
            follow_up_status='进行中'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:negativeevent-list')
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['event_type'] == '学业问题'

    def test_student_statistics(self):
        """测试学生统计API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        Student.objects.create(
            name='学生1',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        Student.objects.create(
            name='学生2',
            student_id='20230002',
            gender='female',
            age=19,
            grade='大一',
            class_name='2班',
            school='测试大学'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:student-statistics')
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert 'total_students' in response.data
        assert 'gender_distribution' in response.data
        assert 'grade_distribution' in response.data

    def test_interview_statistics(self):
        """测试访谈统计API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        
        # 创建咨询师用于关联
        counselor_user = User.objects.create_user(
            username='counselor_user2',
            password='counselorpass123',
            email='counselor2@test.com'
        )
        counselor = Counselor.objects.create(
            user=counselor_user,
            name='张老师',
            gender='male',
            age=35,
            phone='13800138000',
            email='counselor2@test.com',
            service_types=['academic', 'emotional']
        )
        
        Interview.objects.create(
            student=student,
            counselor=counselor,
            interview_date='2025-10-20T10:00:00Z',
            status='completed',
            assessment_level='low',
            interview_notes='学生反映学习压力大',
            follow_up_plan='建议减轻课业负担'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:interview-statistics')
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert 'total_interviews' in response.data
        assert 'status_distribution' in response.data

    def test_negative_event_statistics(self):
        """测试负面事件统计API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='M',
            age=20,
            grade='大二',
            major='计算机科学'
        )
        
        NegativeEvent.objects.create(
            student=student,
            event_date='2025-10-19',
            event_type='学业问题',
            description='期中考试不及格',
            severity='中等',
            handling_measures='安排补考和辅导',
            follow_up_status='进行中'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:negativeevent-statistics')
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert 'total_events' in response.data
        assert 'event_type_distribution' in response.data

    def test_student_search(self):
        """测试学生搜索API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        Student.objects.create(
            name='张三',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        Student.objects.create(
            name='李四',
            student_id='20230002',
            gender='female',
            age=19,
            grade='大一',
            class_name='2班',
            school='测试大学'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:student-list') + '?search=张三'
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['name'] == '张三'

    def test_interview_filter(self):
        """测试访谈记录过滤API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        
        # 创建咨询师用于关联
        counselor_user = User.objects.create_user(
            username='counselor_user3',
            password='counselorpass123',
            email='counselor3@test.com'
        )
        counselor = Counselor.objects.create(
            user=counselor_user,
            name='张老师',
            gender='male',
            age=35,
            phone='13800138000',
            email='counselor3@test.com',
            service_types=['academic', 'emotional']
        )
        
        Interview.objects.create(
            student=student,
            counselor=counselor,
            interview_date='2025-10-20T10:00:00Z',
            status='completed',
            assessment_level='low',
            interview_notes='学生反映学习压力大',
            follow_up_plan='建议减轻课业负担'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:interview-list') + '?counselor__name=张老师'
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['counselor_name'] == '张老师'

    def test_negative_event_filter(self):
        """测试负面事件过滤API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='M',
            age=20,
            grade='大二',
            major='计算机科学'
        )
        
        NegativeEvent.objects.create(
            student=student,
            event_date='2025-10-19',
            event_type='学业问题',
            description='期中考试不及格',
            severity='中等',
            handling_measures='安排补考和辅导',
            follow_up_status='进行中'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:negativeevent-list') + '?event_type=学业问题'
        response = client.get(url)
        
        # 验证响应
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['event_type'] == '学业问题'

    def test_student_update(self):
        """测试学生更新API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='原学生',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:student-detail', args=[student.id])
        data = {
            'name': '更新学生',
            'student_id': '20230001',
            'gender': 'male',
            'age': 21,
            'grade': '大三',
            'class_name': '1班',
            'school': '测试大学'
        }
        response = client.put(url, data, format='json')
        
        # 验证响应
        assert response.status_code == 200
        assert response.data['name'] == '更新学生'
        assert response.data['age'] == 21

    def test_student_delete(self):
        """测试学生删除API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='删除学生',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:student-detail', args=[student.id])
        response = client.delete(url)
        
        # 验证响应
        assert response.status_code == 204
        assert Student.objects.count() == 0

    def test_interview_create(self):
        """测试访谈记录创建API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='male',
            age=20,
            grade='大二',
            class_name='1班',
            school='测试大学'
        )
        
        # 创建咨询师用于关联
        counselor_user = User.objects.create_user(
            username='counselor_user4',
            password='counselorpass123',
            email='counselor4@test.com'
        )
        counselor = Counselor.objects.create(
            user=counselor_user,
            name='王老师',
            gender='male',
            age=35,
            phone='13800138000',
            email='counselor4@test.com',
            service_types=['academic', 'emotional']
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:interview-list')
        data = {
            'student': student.id,
            'counselor': counselor.id,
            'interview_date': '2025-10-21T10:00:00Z',
            'status': 'pending',
            'assessment_level': 'low',
            'interview_notes': '学生情绪稳定',
            'follow_up_plan': '定期回访'
        }
        response = client.post(url, data, format='json')
        
        # 验证响应
        assert response.status_code == 201
        assert response.data['counselor_name'] == '王老师'
        assert Interview.objects.count() == 1

    def test_negative_event_create(self):
        """测试负面事件创建API"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建测试数据
        student = Student.objects.create(
            name='测试学生',
            student_id='20230001',
            gender='M',
            age=20,
            grade='大二',
            major='计算机科学'
        )
        
        # 调用API
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('counselor_admin:negativeevent-list')
        data = {
            'student': student.id,
            'event_date': '2025-10-22',
            'event_type': '行为问题',
            'description': '课堂违纪',
            'severity': '轻微',
            'handling_measures': '口头警告',
            'follow_up_status': '已处理'
        }
        response = client.post(url, data, format='json')
        
        # 验证响应
        assert response.status_code == 201
        assert response.data['event_type'] == '行为问题'
        assert NegativeEvent.objects.count() == 1