from rest_framework import serializers
from CounselorAdmin.models import ReferralUnit


class ReferralUnitSerializer(serializers.ModelSerializer):
    """
    转介单位序列化器
    数据库表: referral_units
    """
    class Meta:
        model = ReferralUnit
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


