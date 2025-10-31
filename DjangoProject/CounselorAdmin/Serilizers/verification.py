from rest_framework import serializers
from CounselorAdmin.models import VerificationCode, Captcha, AdminUser, AdminAuthToken
from django.contrib.auth.hashers import make_password, check_password


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = '__all__'


class CaptchaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Captcha
        fields = '__all__'


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'gender', 'email', 'phone', 'password']

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        validated_data['password'] = make_password(raw_password)
        return AdminUser.objects.create(**validated_data)


class AdminUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'phone']


class AdminAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuthToken
        fields = ['id', 'user', 'token', 'is_active', 'created_time', 'expires_at']


