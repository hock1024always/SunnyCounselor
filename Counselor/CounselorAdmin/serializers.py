# serializers.py
from rest_framework import serializers
from .models import *


# 访谈评估序列化器（根据接口文档调整）
class InterviewAssessmentSerializer(serializers.ModelSerializer):
    std_name = serializers.CharField(source='student_name')
    std_grade = serializers.CharField(source='grade')
    std_class = serializers.CharField(source='class_name')
    std_school = serializers.CharField(source='organization')
    doctor_evaluation = serializers.CharField(source='doctor_assessment')
    create_time = serializers.DateTimeField(source='created_time', format='%Y-%m-%d')

    class Meta:
        model = InterviewAssessment
        fields = [
            'id', 'std_name', 'std_grade', 'std_class', 'std_school',
            'interview_count', 'interview_status', 'interview_type',
            'doctor_evaluation', 'follow_up_plan', 'create_time'
        ]


class InterviewAssessmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewAssessment
        fields = '__all__'


# 负面事件序列化器
class NegativeEventSerializer(serializers.ModelSerializer):
    std_name = serializers.CharField(source='student_name')
    std_grade = serializers.CharField(source='grade')
    std_class = serializers.CharField(source='class_name')
    std_school = serializers.CharField(source='organization')
    event_content = serializers.CharField(source='event_details')
    creator = serializers.CharField(source='created_by')
    create_time = serializers.DateTimeField(source='created_time', format='%Y-%m-%d %H:%M')

    class Meta:
        model = NegativeEvent
        fields = [
            'id', 'std_name', 'std_grade', 'std_class', 'std_school',
            'event_content', 'event_date', 'creator', 'create_time'
        ]


class NegativeEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegativeEvent
        fields = '__all__'


# 转介单位序列化器
class ReferralUnitSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField(source='unit_name')
    org_address = serializers.CharField(source='address')
    phone = serializers.CharField(source='contact_phone')
    creator = serializers.CharField(source='created_by')
    creat_time = serializers.DateTimeField(source='created_time', format='%Y-%m-%d %H:%M')

    class Meta:
        model = ReferralUnit
        fields = ['id', 'org_name', 'org_address', 'phone', 'creator', 'creat_time']


class ReferralUnitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralUnit
        fields = '__all__'


class ReferralUnitNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralUnit
        fields = ['unit_name']


# 学生转介序列化器
class StudentReferralSerializer(serializers.ModelSerializer):
    std_name = serializers.CharField(source='student_name')
    std_grade = serializers.CharField(source='grade')
    std_class = serializers.CharField(source='class_name')
    std_school = serializers.CharField(source='school')
    std_gender = serializers.CharField(source='gender')
    org_name = serializers.CharField(source='referral_unit.unit_name')
    reason = serializers.CharField(source='referral_reason')
    time = serializers.DateField(source='referral_date')

    class Meta:
        model = StudentReferral
        fields = [
            'id', 'std_name', 'std_grade', 'std_class', 'std_school',
            'std_gender', 'org_name', 'reason', 'time'
        ]


class StudentReferralCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentReferral
        fields = '__all__'


# 栏目序列化器
class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='category_name')
    order = serializers.IntegerField(source='sort_order')
    create_time = serializers.DateTimeField(source='created_time')
    creator = serializers.CharField(source='created_by')

    class Meta:
        model = Category
        fields = ['id', 'name', 'order', 'create_time', 'creator']


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# 宣教资讯序列化器
class ArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name')

    class Meta:
        model = Article
        fields = '__all__'


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


# 通知序列化器
class NotificationSerializer(serializers.ModelSerializer):
    isPublished = serializers.BooleanField(source='is_published')
    create_time = serializers.DateTimeField(source='created_time')
    creator = serializers.CharField(source='created_by')

    class Meta:
        model = Notification
        fields = ['id', 'title', 'isPublished', 'creator', 'create_time']


class NotificationDetailSerializer(serializers.ModelSerializer):
    isPublished = serializers.BooleanField(source='is_published')

    class Meta:
        model = Notification
        fields = ['id', 'title', 'isPublished', 'content']


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


# Banner序列化器
class BannerModuleSerializer(serializers.ModelSerializer):
    module = serializers.CharField(source='module_name')
    count = serializers.IntegerField(source='carousel_count')
    create_time = serializers.DateTimeField(source='created_time')
    creator = serializers.CharField(source='created_by')

    class Meta:
        model = BannerModule
        fields = ['id', 'module', 'count', 'creator', 'create_time']


class BannerModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerModule
        fields = '__all__'


# 预约订单序列化器
class AppointmentSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order_no')
    name = serializers.CharField(source='client_name')
    gender = serializers.CharField(source='client_gender')
    age = serializers.CharField(source='client_age')
    type = serializers.CharField(source='service_type')
    key_word = serializers.CharField(source='counseling_keywords')
    date = serializers.DateField(source='appointment_date')
    time = serializers.CharField(source='time_slot')
    commit_time = serializers.DateTimeField(source='submit_time')
    finish_time = serializers.DateTimeField(source='end_time')
    status = serializers.CharField(source='status')

    class Meta:
        model = Appointment
        fields = [
            'id', 'order_id', 'name', 'gender', 'age', 'type', 'key_word',
            'date', 'time', 'commit_time', 'finish_time', 'status'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


# 咨询师序列化器
class CounselorSerializer(serializers.ModelSerializer):
    skills = serializers.JSONField(source='expertise_tags')

    class Meta:
        model = Counselor
        fields = ['id', 'name', 'gender', 'phone', 'organization', 'skills', 'status']


class CounselorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counselor
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


# 排班序列化器
class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


# 停诊序列化器
class CancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancellation
        fields = '__all__'


# 查询参数序列化器
class InterviewQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=20)
    std_name = serializers.CharField(required=False)
    std_grade = serializers.CharField(required=False)
    std_class = serializers.CharField(required=False)
    std_school = serializers.CharField(required=False)
    interview_count = serializers.CharField(required=False)
    interview_status = serializers.CharField(required=False)
    interview_type = serializers.CharField(required=False)
    doctor_evaluation = serializers.CharField(required=False)
    follow_up_plan = serializers.CharField(required=False)


class NegativeEventQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=20)
    std_name = serializers.CharField(required=False)
    date_start = serializers.DateField(required=False)
    date_end = serializers.DateField(required=False)