from rest_framework import serializers
from CounselorAdmin.models import NegativeEvent


class NegativeEventSerializer(serializers.ModelSerializer):
    """
    负面事件序列化器
    数据库表: negative_events
    """
    class Meta:
        model = NegativeEvent
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


