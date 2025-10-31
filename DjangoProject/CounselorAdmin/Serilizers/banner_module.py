from rest_framework import serializers
from CounselorAdmin.models import BannerModule


class BannerModuleSerializer(serializers.ModelSerializer):
    """
    轮播图模块序列化器
    数据库表: banner_modules
    """
    class Meta:
        model = BannerModule
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


