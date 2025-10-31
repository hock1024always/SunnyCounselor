from rest_framework import serializers
from CounselorAdmin.models import Cancellation


class CancellationSerializer(serializers.ModelSerializer):
    """
    停诊序列化器
    数据库表: cancellations
    外键: counselor_id -> counselors.id (NOT NULL)
    """
    class Meta:
        model = Cancellation
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


