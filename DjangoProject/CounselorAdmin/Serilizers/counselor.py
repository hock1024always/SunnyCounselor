from rest_framework import serializers
from CounselorAdmin.models import Counselor


class CounselorSerializer(serializers.ModelSerializer):
    """
    咨询师序列化器
    数据库表: counselors
    """
    class Meta:
        model = Counselor
        fields = '__all__'
        read_only_fields = ['id']


