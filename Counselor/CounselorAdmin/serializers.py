from rest_framework import serializers
from .models import (
    Student, Interview, NegativeEvent, ReferralUnit, ReferralHistory,
    EducationCategory, EducationContent, Notification, Banner,
    CounselorSchedule, ConsultationOrder
)
from CounselorApp.models import Counselor, Consultation, Client


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class InterviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    counselor_name = serializers.CharField(source='counselor.name', read_only=True)
    
    class Meta:
        model = Interview
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class NegativeEventSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    
    class Meta:
        model = NegativeEvent
        fields = '__all__'
        read_only_fields = ['created_at']


class ReferralUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralUnit
        fields = '__all__'
        read_only_fields = ['created_at']


class ReferralHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_school = serializers.CharField(source='student.school', read_only=True)
    student_grade = serializers.CharField(source='student.grade', read_only=True)
    student_class = serializers.CharField(source='student.class_name', read_only=True)
    referral_unit_name = serializers.CharField(source='referral_unit.name', read_only=True)
    
    class Meta:
        model = ReferralHistory
        fields = '__all__'
        read_only_fields = ['created_at']


class EducationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationCategory
        fields = '__all__'
        read_only_fields = ['created_at']


class EducationContentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = EducationContent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'view_count']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'
        read_only_fields = ['created_at']


class CounselorScheduleSerializer(serializers.ModelSerializer):
    counselor_name = serializers.CharField(source='counselor.name', read_only=True)
    
    class Meta:
        model = CounselorSchedule
        fields = '__all__'
        read_only_fields = ['created_at']


class ConsultationOrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='consultation.client.name', read_only=True)
    counselor_name = serializers.CharField(source='consultation.counselor.name', read_only=True)
    consultation_type = serializers.CharField(source='consultation.type', read_only=True)
    consultation_status = serializers.CharField(source='consultation.status', read_only=True)
    scheduled_at = serializers.DateTimeField(source='consultation.scheduled_at', read_only=True)
    
    class Meta:
        model = ConsultationOrder
        fields = '__all__'
        read_only_fields = ['created_at']


# 导入导出相关的序列化器
class StudentImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class InterviewTemplateSerializer(serializers.Serializer):
    template_type = serializers.ChoiceField(choices=[
        ('student_list', '学生名单模板'),
        ('interview_record', '访谈记录模板')
    ])


# 统计相关的序列化器
class InterviewStatisticsSerializer(serializers.Serializer):
    total_interviews = serializers.IntegerField()
    completed_interviews = serializers.IntegerField()
    pending_interviews = serializers.IntegerField()
    high_risk_count = serializers.IntegerField()
    referral_count = serializers.IntegerField()


class EducationStatisticsSerializer(serializers.Serializer):
    total_contents = serializers.IntegerField()
    published_contents = serializers.IntegerField()
    total_views = serializers.IntegerField()
    active_categories = serializers.IntegerField()