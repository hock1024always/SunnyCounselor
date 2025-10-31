from rest_framework import serializers
from CounselorAdmin.models import InterviewAssessment


class InterviewAssessmentSerializer(serializers.ModelSerializer):
    """
    访谈评估序列化器
    数据库表: interview_assessments
    """
    class Meta:
        model = InterviewAssessment
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


