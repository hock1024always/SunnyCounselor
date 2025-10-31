from rest_framework import serializers
from CounselorAdmin.models import StudentReferral


class StudentReferralSerializer(serializers.ModelSerializer):
    """
    学生转介序列化器
    数据库表: student_referrals
    外键: referral_unit_id -> referral_units.id (可空)
    """
    class Meta:
        model = StudentReferral
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


