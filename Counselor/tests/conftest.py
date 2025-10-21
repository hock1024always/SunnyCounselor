import pytest
import os
import django
from django.conf import settings

# 配置Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Counselor.settings')

# 确保Django已配置
if not settings.configured:
    django.setup()

# 使用pytest-django的内置fixture，不再自定义session级别的数据库设置


@pytest.fixture
def test_settings():
    """测试设置fixture"""
    return {
        'TEST_DATABASE_NAME': 'test_counselor_db',
        'TEST_RUNNER': 'django.test.runner.DiscoverRunner'
    }


@pytest.fixture
def api_client():
    """API客户端fixture"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def admin_user():
    """管理员用户fixture"""
    from django.contrib.auth.models import User
    user = User.objects.create_user(
        username='test_admin',
        password='testpassword123',
        email='admin@test.com',
        is_staff=True,
        is_superuser=True
    )
    return user


@pytest.fixture
def counselor_user():
    """咨询师用户fixture"""
    from django.contrib.auth.models import User
    from CounselorApp.models import Counselor
    
    user = User.objects.create_user(
        username='test_counselor',
        password='testpassword123',
        email='counselor@test.com'
    )
    counselor = Counselor.objects.create(
        user=user,
        name='测试咨询师',
        gender='male',
        age=35,
        phone='13800138000',
        specialization='学业压力,情感咨询',
        experience_years=5,
        hourly_rate=200.00,
        is_available=True
    )
    return counselor


@pytest.fixture
def sample_student_data():
    """样本学生数据fixture"""
    return {
        'name': '测试学生',
        'gender': 'male',
        'age': 18,
        'student_id': '20230001',
        'school': '阳光中学',
        'grade': '高三',
        'class_name': '1班',
        'phone': '13800138000',
        'emergency_contact': '测试联系人',
        'emergency_phone': '13800138001'
    }


@pytest.fixture
def sample_consultation_data(counselor_user):
    """样本咨询数据fixture"""
    return {
        'counselor': counselor_user.id,
        'student_name': '测试咨询学生',
        'student_age': 19,
        'student_gender': 'female',
        'consultation_type': 'academic',
        'scheduled_time': '2025-10-25T10:00:00Z',
        'keywords': ['学业压力', '时间管理']
    }


@pytest.fixture
def sample_interview_data(counselor_user):
    """样本访谈数据fixture"""
    return {
        'counselor': counselor_user.id,
        'interview_date': '2025-10-26T14:00:00Z',
        'status': 'scheduled',
        'assessment_level': 'medium',
        'interview_notes': '测试访谈记录',
        'follow_up_plan': '测试跟进计划'
    }


@pytest.fixture
def mock_excel_file():
    """模拟Excel文件fixture"""
    import tempfile
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    # 创建模拟Excel文件内容
    excel_content = b'\x50\x4b\x03\x04'  # 简化的Excel文件头
    return SimpleUploadedFile(
        'test_students.xlsx',
        excel_content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@pytest.fixture
def test_datetime():
    """测试日期时间fixture"""
    from datetime import datetime
    return datetime(2025, 10, 20, 10, 0, 0)


class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_student(**kwargs):
        """创建学生测试数据"""
        from CounselorAdmin.models import Student
        
        default_data = {
            'name': '工厂测试学生',
            'gender': 'male',
            'age': 17,
            'student_id': '20230099',
            'school': '测试学校',
            'grade': '高二',
            'class_name': '2班',
            'phone': '13800138999',
            'emergency_contact': '工厂测试联系人',
            'emergency_phone': '13800138998'
        }
        default_data.update(kwargs)
        
        return Student.objects.create(**default_data)
    
    @staticmethod
    def create_consultation(counselor, **kwargs):
        """创建咨询测试数据"""
        from CounselorApp.models import Consultation
        
        default_data = {
            'counselor': counselor,
            'student_name': '工厂咨询学生',
            'student_age': 18,
            'student_gender': 'female',
            'consultation_type': 'academic',
            'scheduled_time': '2025-10-25T10:00:00Z',
            'status': 'pending',
            'payment_amount': 200.00,
            'payment_status': 'pending'
        }
        default_data.update(kwargs)
        
        return Consultation.objects.create(**default_data)
    
    @staticmethod
    def create_interview(student, counselor, **kwargs):
        """创建访谈测试数据"""
        from CounselorAdmin.models import Interview
        
        default_data = {
            'student': student,
            'counselor': counselor,
            'interview_date': '2025-10-25T14:00:00Z',
            'status': 'scheduled',
            'assessment_level': 'medium',
            'interview_notes': '工厂测试访谈记录'
        }
        default_data.update(kwargs)
        
        return Interview.objects.create(**default_data)


# 测试装饰器
def skip_if_no_database(func):
    """如果没有数据库则跳过测试的装饰器"""
    return pytest.mark.skipif(
        not hasattr(settings, 'DATABASES') or not settings.DATABASES.get('default'),
        reason="需要配置数据库"
    )(func)


def requires_admin(func):
    """需要管理员权限的装饰器"""
    return pytest.mark.admin_access(func)


def requires_counselor(func):
    """需要咨询师权限的装饰器"""
    return pytest.mark.counselor_access(func)


# 测试配置
def pytest_configure():
    """pytest配置"""
    pytest.TEST_MODE = True


def pytest_unconfigure():
    """pytest清理配置"""
    pytest.TEST_MODE = False