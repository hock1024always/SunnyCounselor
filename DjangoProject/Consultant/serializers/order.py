"""
订单相关序列化器
"""
from rest_framework import serializers
from Consultant.models import ConsultationOrder, ConsultationRecord
from CounselorAdmin.models import Counselor


class ConsultationOrderListSerializer(serializers.ModelSerializer):
    """咨询订单列表序列化器"""
    id = serializers.IntegerField(read_only=True)
    order_id = serializers.CharField(source='order_no', read_only=True)
    gender = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    key_word = serializers.SerializerMethodField()
    date = serializers.DateField(source='appointment_date', read_only=True)
    time = serializers.CharField(source='time_slot', read_only=True)
    commit_time = serializers.DateTimeField(source='submit_time', read_only=True)
    finish_time = serializers.DateTimeField(source='end_time', read_only=True)
    status = serializers.CharField(read_only=True)
    contact = serializers.CharField(source='contact_info', read_only=True)
    
    class Meta:
        model = ConsultationOrder
        fields = [
            'id', 'order_id', 'gender', 'age', 'type', 'key_word',
            'date', 'time', 'commit_time', 'finish_time', 'status', 'contact'
        ]
    
    def get_gender(self, obj):
        """获取性别"""
        if obj.record:
            return obj.record.gender
        return ''
    
    def get_age(self, obj):
        """获取年龄"""
        if obj.record:
            age = obj.record.age
            return str(age) if age else ''
        return ''
    
    def get_type(self, obj):
        """获取服务类型"""
        type_map = {
            'online': '在线咨询',
            'offline': '线下咨询'
        }
        return type_map.get(obj.service_type, obj.service_type)
    
    def get_key_word(self, obj):
        """获取关键词"""
        if obj.counseling_keywords:
            if isinstance(obj.counseling_keywords, list):
                return ','.join(obj.counseling_keywords)
            return str(obj.counseling_keywords)
        return ''


class ConsultationOrderCreateSerializer(serializers.Serializer):
    """创建咨询订单序列化器"""
    name = serializers.CharField(required=True, help_text='姓名')
    age = serializers.CharField(required=True, help_text='年龄')
    gender = serializers.CharField(required=True, help_text='性别')
    type = serializers.CharField(required=True, help_text='服务类型')
    date = serializers.DateField(required=True, help_text='预约日期')
    time = serializers.CharField(required=True, help_text='预约时段')
    contact = serializers.CharField(required=True, help_text='联系方式')
    key_word = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text='关键字数组'
    )

