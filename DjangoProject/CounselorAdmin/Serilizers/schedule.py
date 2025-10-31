from rest_framework import serializers
from CounselorAdmin.models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    """
    排班序列化器
    数据库表: schedules
    外键: counselor_id -> counselors.id (NOT NULL)
    """
    class Meta:
        model = Schedule
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


