"""
认证相关序列化器
"""
from rest_framework import serializers
from CounselorAdmin.models import Counselor, VerificationCode
from Consultant.models import ConsultantAuthToken, CounselorProfile


class CounselorLoginSerializer(serializers.Serializer):
    """登录序列化器"""
    loginType = serializers.CharField(required=True, help_text='登录类型: password 或 code')
    accountType = serializers.CharField(required=True, help_text='账户类型: email 或 phone')
    account = serializers.CharField(required=True, help_text='账号')
    credential = serializers.CharField(required=True, help_text='密码或验证码')


class CounselorRegisterSerializer(serializers.Serializer):
    """注册序列化器"""
    userName = serializers.CharField(required=True, help_text='用户名')
    account = serializers.CharField(required=True, help_text='账号')
    accountType = serializers.CharField(required=True, help_text='账户类型: email 或 phone')
    password = serializers.CharField(required=True, help_text='密码')
    verificationCode = serializers.CharField(required=True, help_text='验证码')


class CounselorUserInfoSerializer(serializers.ModelSerializer):
    """咨询师用户信息序列化器"""
    userID = serializers.IntegerField(source='id', read_only=True)
    userName = serializers.CharField(source='username', read_only=True)
    name = serializers.SerializerMethodField()
    phone = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    organization = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Counselor
        fields = ['userID', 'userName', 'name', 'phone', 'email', 'organization', 'avatar']
    
    def get_name(self, obj):
        """获取真实姓名"""
        try:
            profile = obj.profile
            return profile.name if profile else obj.name
        except CounselorProfile.DoesNotExist:
            return obj.name
    
    def get_organization(self, obj):
        """获取所属机构"""
        try:
            profile = obj.profile
            return profile.organization if profile else ''
        except CounselorProfile.DoesNotExist:
            return ''
    
    def get_avatar(self, obj):
        """获取头像URL"""
        try:
            profile = obj.profile
            if profile and profile.avatar:
                return profile.avatar
        except CounselorProfile.DoesNotExist:
            pass
        return ''


class CounselorProfileSerializer(serializers.ModelSerializer):
    """咨询师详情序列化器"""
    class Meta:
        model = CounselorProfile
        fields = [
            'name', 'organization', 'introduction', 'experience',
            'expertise', 'education', 'certifications', 'consultation_count'
        ]

