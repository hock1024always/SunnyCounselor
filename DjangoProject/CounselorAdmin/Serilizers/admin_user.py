from rest_framework import serializers
from CounselorAdmin.models import AdminUser


class AdminUserSerializer(serializers.ModelSerializer):
    """
    管理员用户序列化器
    数据库表: admin_users
    """
    class Meta:
        model = AdminUser
        fields = '__all__'
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }


