from rest_framework import serializers
from CounselorAdmin.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    数据库表: notifications
    """
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


