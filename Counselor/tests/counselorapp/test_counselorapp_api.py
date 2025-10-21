import pytest
import json
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from CounselorApp.models import Counselor, Consultation, Schedule, Review, Client
from django.contrib.auth.models import User
from datetime import datetime, timedelta


@pytest.mark.django_db
class TestCounselorAppAPI:
    """CounselorApp API测试类"""

    @pytest.fixture
    def api_client(self):
        """API客户端fixture"""
        return APIClient()

    @pytest.fixture
    def test_counselor(self):
        """测试咨询师fixture"""
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
            email='counselor@test.com',
            service_types=['academic', 'emotional'],
            years_of_experience=5,
            is_active=True
        )
        return counselor

    @pytest.fixture
    def test_client(self):
        """测试客户fixture"""
        user = User.objects.create_user(
            username='test_client',
            password='testpassword123',
            email='client@test.com'
        )
        client = Client.objects.create(
            user=user,
            name='测试客户',
            gender='male',
            age=18,
            phone='13800138001',
            student_id='20230001'
        )
        return client

    @pytest.fixture
    def test_consultations(self, test_counselor, test_client):
        """测试咨询会话fixture"""
        consultations = []
        # 创建不同状态的咨询会话
        statuses = ['pending', 'in_progress', 'completed', 'rejected']
        for i, status_val in enumerate(statuses):
            consultation = Consultation.objects.create(
                client=test_client,
                counselor=test_counselor,
                type='academic',
                status=status_val,
                scheduled_at=datetime.now() + timedelta(days=i),
                description=f'测试咨询问题{i+1}'
            )
            consultations.append(consultation)
        return consultations

    @pytest.fixture
    def test_schedules(self, test_counselor):
        """测试排班fixture"""
        schedules = []
        for i in range(3):
            schedule = Schedule.objects.create(
                counselor=test_counselor,
                date=datetime.now().date() + timedelta(days=i),
                start_time='09:00:00',
                end_time='12:00:00',
                is_available=True,
                max_appointments=5
            )
            schedules.append(schedule)
        return schedules

    @pytest.fixture
    def test_reviews(self, test_counselor, test_consultations):
        """测试评论fixture"""
        reviews = []
        for i, consultation in enumerate(test_consultations[:2]):
            review = Review.objects.create(
                consultation=consultation,
                counselor=test_counselor,
                rating=4 + i,
                comment=f'测试评论内容{i+1}',
                is_anonymous=False if i == 0 else True
            )
            reviews.append(review)
        return reviews

    def test_dashboard_stats(self, api_client, test_counselor, test_consultations):
        """测试数据看板统计接口"""
        # 认证用户
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('counselor:dashboard-stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 验证响应结构
        assert 'today_stats' in data
        assert 'yearly_total' in data
        assert 'time_slot_distribution' in data
        assert 'type_distribution' in data
        assert 'gender_distribution' in data
        assert 'age_distribution' in data
        assert 'average_rating' in data
        
        # 验证今日统计
        today_stats = data['today_stats']
        assert 'total' in today_stats
        assert 'pending' in today_stats
        assert 'in_progress' in today_stats
        assert 'completed' in today_stats
        
        # 验证时段分布
        time_distribution = data['time_slot_distribution']
        assert isinstance(time_distribution, list)
        for time_slot in time_distribution:
            assert 'hour' in time_slot
            assert 'count' in time_slot

    def test_pending_consultations(self, api_client, test_counselor, test_consultations):
        """测试待接单列表接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('pending-consultations')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 验证只返回待接单状态的咨询
        for consultation in data:
            assert consultation['status'] == 'pending'

    def test_in_progress_consultations(self, api_client, test_counselor, test_consultations):
        """测试咨询中列表接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('in-progress-consultations')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for consultation in data:
            assert consultation['status'] == 'in_progress'

    def test_completed_consultations(self, api_client, test_counselor, test_consultations):
        """测试已结束列表接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('completed-consultations')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for consultation in data:
            assert consultation['status'] == 'completed'

    def test_rejected_consultations(self, api_client, test_counselor, test_consultations):
        """测试已拒绝列表接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('rejected-consultations')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for consultation in data:
            assert consultation['status'] == 'rejected'

    def test_bulk_create_schedules(self, api_client, test_counselor):
        """测试批量排班接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('bulk-create-schedules')
        schedule_data = {
            'schedules': [
                {
                    'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'start_time': '09:00:00',
                    'end_time': '12:00:00',
                    'max_appointments': 5
                },
                {
                    'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'start_time': '14:00:00',
                    'end_time': '17:00:00',
                    'max_appointments': 3
                }
            ]
        }
        
        response = api_client.post(
            url, 
            data=json.dumps(schedule_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert 'created_count' in data
        assert data['created_count'] == 2

    def test_stop_service(self, api_client, test_counselor, test_schedules):
        """测试停诊安排接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('stop-service')
        stop_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        stop_data = {
            'date': stop_date,
            'reason': '临时有事'
        }
        
        response = api_client.post(
            url,
            data=json.dumps(stop_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'message' in data
        
        # 验证排班状态已更新
        schedule = Schedule.objects.get(
            counselor=test_counselor,
            date=stop_date
        )
        assert not schedule.is_available

    def test_review_list(self, api_client, test_counselor, test_reviews):
        """测试评论列表接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('review-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 验证返回评论数量
        assert len(data) == len(test_reviews)
        
        # 验证评论结构
        for review in data:
            assert 'id' in review
            assert 'rating' in review
            assert 'comment' in review
            assert 'created_at' in review
            assert 'student_name' in review

    def test_update_profile(self, api_client, test_counselor):
        """测试更新个人资料接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('update-profile')
        update_data = {
            'name': '更新后的咨询师',
            'phone': '13800138001',
            'specialization': '学业压力,情感咨询,职业规划'
        }
        
        response = api_client.patch(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 验证资料已更新
        assert data['name'] == '更新后的咨询师'
        assert data['phone'] == '13800138001'
        
        # 验证数据库已更新
        test_counselor.refresh_from_db()
        assert test_counselor.name == '更新后的咨询师'

    def test_update_service_types(self, api_client, test_counselor):
        """测试更新服务类型配置接口"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('update-service-types')
        service_data = {
            'service_types': ['academic', 'emotional', 'career']
        }
        
        response = api_client.patch(
            url,
            data=json.dumps(service_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'service_types' in data

    def test_unauthorized_access(self, api_client):
        """测试未授权访问"""
        url = reverse('dashboard-stats')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_consultation_status_transition(self, api_client, test_counselor, test_consultations):
        """测试咨询状态转换"""
        api_client.force_authenticate(user=test_counselor.user)
        
        # 获取一个待接单的咨询
        pending_consultation = test_consultations[0]  # pending状态
        
        # 更新为咨询中状态
        url = reverse('consultation-detail', kwargs={'pk': pending_consultation.id})
        update_data = {'status': 'in_progress'}
        
        response = api_client.patch(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'in_progress'

    def test_schedule_conflict(self, api_client, test_counselor):
        """测试排班冲突"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('bulk-create-schedules')
        schedule_data = {
            'schedules': [
                {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'start_time': '09:00:00',
                    'end_time': '12:00:00',
                    'max_appointments': 5
                }
            ]
        }
        
        # 第一次创建
        response1 = api_client.post(
            url, 
            data=json.dumps(schedule_data),
            content_type='application/json'
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # 第二次创建相同日期的排班（应该冲突）
        response2 = api_client.post(
            url, 
            data=json.dumps(schedule_data),
            content_type='application/json'
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_review_creation(self, api_client, test_counselor, test_consultations):
        """测试创建评论（模拟学生端操作）"""
        # 注意：实际中评论应由学生创建，这里模拟测试
        completed_consultation = test_consultations[2]  # completed状态
        
        url = reverse('review-list')
        review_data = {
            'consultation': completed_consultation.id,
            'rating': 5,
            'comment': '非常好的咨询体验',
            'is_anonymous': False
        }
        
        response = api_client.post(
            url,
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        # 咨询师不能为自己创建评论，应该返回403
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCounselorAppIntegration:
    """CounselorApp集成测试"""

    def test_consultation_workflow(self, api_client, test_counselor):
        """测试完整的咨询工作流"""
        # 1. 创建咨询会话（模拟学生预约）
        consultation_data = {
            'counselor': test_counselor.id,
            'student_name': '集成测试学生',
            'student_age': 20,
            'student_gender': 'female',
            'consultation_type': 'academic',
            'scheduled_time': (datetime.now() + timedelta(days=1)).isoformat(),
            'keywords': ['学业压力', '时间管理']
        }
        
        # 注意：实际中咨询创建应由学生端完成
        # 这里直接测试咨询师端的操作
        
        # 2. 咨询师查看待接单列表
        api_client.force_authenticate(user=test_counselor.user)
        url = reverse('pending-consultations')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # 3. 咨询师接受咨询（更新状态）
        if response.json():
            consultation_id = response.json()[0]['id']
            update_url = reverse('consultation-detail', kwargs={'pk': consultation_id})
            update_data = {'status': 'in_progress'}
            
            update_response = api_client.patch(
                update_url,
                data=json.dumps(update_data),
                content_type='application/json'
            )
            assert update_response.status_code == status.HTTP_200_OK
            
            # 4. 完成咨询
            complete_data = {'status': 'completed'}
            complete_response = api_client.patch(
                update_url,
                data=json.dumps(complete_data),
                content_type='application/json'
            )
            assert complete_response.status_code == status.HTTP_200_OK

    def test_dashboard_data_consistency(self, api_client, test_counselor, test_consultations):
        """测试看板数据一致性"""
        api_client.force_authenticate(user=test_counselor.user)
        
        url = reverse('dashboard-stats')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # 验证今日统计与数据库一致
        today = datetime.now().date()
        today_consultations = Consultation.objects.filter(
            counselor=test_counselor,
            scheduled_time__date=today
        )
        
        today_stats = data['today_stats']
        assert today_stats['total'] == today_consultations.count()
        
        # 验证年度统计
        current_year = datetime.now().year
        yearly_consultations = Consultation.objects.filter(
            counselor=test_counselor,
            scheduled_time__year=current_year
        )
        assert data['yearly_stats']['total_consultations'] == yearly_consultations.count()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])