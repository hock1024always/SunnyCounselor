from rest_framework import serializers
from CounselorAdmin.models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """
    预约订单序列化器
    数据库表: appointments
    外键: counselor_id -> counselors.id (可空)
    """
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['id', 'submit_time']


