"""
认证相关视图
"""
import uuid
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password

from CounselorAdmin.models import Counselor, VerificationCode
from Consultant.models import ConsultantAuthToken, CounselorProfile
from Consultant.serializers.auth import (
    CounselorLoginSerializer,
    CounselorRegisterSerializer,
    CounselorUserInfoSerializer
)


def _generate_code(length: int = 6) -> str:
    """生成验证码"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def _send_email_code(email: str, code: str) -> bool:
    """
    使用163邮箱SMTP发送验证码
    """
    try:
        smtp_server = "smtp.163.com"
        smtp_port = 465
        sender_email = "hock2022@163.com"
        sender_password = "CER9J5e7FrVscZKZ"
        smtp_user = "hock2022@163.com"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = '【咨询师注册验证码】'
        
        body = f'您的验证码是：{code}，5分钟内有效。'
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


class LoginView(APIView):
    """
    登录接口
    POST /api/consultant/auth/login
    """
    permission_classes = []
    
    def post(self, request):
        serializer = CounselorLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'detail': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        login_type = data.get('loginType')
        account_type = data.get('accountType')
        account = data.get('account')
        credential = data.get('credential')
        
        # 根据账户类型查找用户
        if account_type == 'email':
            counselor = Counselor.objects.filter(email=account).first()
        elif account_type == 'phone':
            counselor = Counselor.objects.filter(phone=account).first()
        else:
            return Response({
                'code': 400,
                'message': '账户类型错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not counselor:
            return Response({
                'code': 404,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证登录方式
        if login_type == 'password':
            # 密码登录
            if not check_password(credential, counselor.password):
                return Response({
                    'code': 401,
                    'message': '密码错误'
                }, status=status.HTTP_401_UNAUTHORIZED)
        elif login_type == 'code':
            # 验证码登录
            # 支持查询login和register两种用途的验证码（兼容性处理）
            vc = VerificationCode.objects.filter(
                email=account if account_type == 'email' else None,
                phone=account if account_type == 'phone' else None,
                purpose__in=['login', 'register']  # 支持两种用途
            ).order_by('-created_time').first()
            
            if not vc:
                return Response({
                    'code': 401,
                    'message': '验证码不存在，请先获取验证码'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证验证码
            if vc.code != str(credential).strip():
                return Response({
                    'code': 401,
                    'message': '验证码错误'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 检查是否过期
            if vc.expires_at and vc.expires_at < now():
                return Response({
                    'code': 401,
                    'message': '验证码已过期'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            vc.is_verified = True
            vc.save(update_fields=['is_verified'])
        else:
            return Response({
                'code': 400,
                'message': '登录类型错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成token
        token = str(uuid.uuid4())
        
        # 禁用旧的token，创建新token
        ConsultantAuthToken.objects.filter(counselor=counselor, is_active=True).update(is_active=False)
        ConsultantAuthToken.objects.create(
            counselor=counselor,
            token=token,
            expires_at=now() + timedelta(days=7)
        )
        
        # 获取用户信息
        user_info = CounselorUserInfoSerializer(counselor).data
        
        return Response({
            'code': 0,
            'message': '登录成功',
            'data': {
                'token': token,
                'userInfo': user_info
            }
        })


class RegisterView(APIView):
    """
    注册接口
    POST /api/consultant/auth/register
    """
    permission_classes = []
    
    def post(self, request):
        serializer = CounselorRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'detail': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        username = data.get('userName')
        account = data.get('account')
        account_type = data.get('accountType')
        password = data.get('password')
        verification_code = data.get('verificationCode')
        
        # 验证验证码
        if account_type == 'email':
            vc = VerificationCode.objects.filter(
                email=account,
                purpose='register'
            ).order_by('-created_time').first()
        elif account_type == 'phone':
            vc = VerificationCode.objects.filter(
                phone=account,
                purpose='register'
            ).order_by('-created_time').first()
        else:
            return Response({
                'code': 400,
                'message': '账户类型错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not vc or vc.code != str(verification_code).strip() or (vc.expires_at and vc.expires_at < now()):
            return Response({
                'code': 400,
                'message': '验证码无效或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户名是否已存在
        if Counselor.objects.filter(username=username).exists():
            return Response({
                'code': 400,
                'message': '用户名已存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查邮箱或手机号是否已注册
        if account_type == 'email' and Counselor.objects.filter(email=account).exists():
            return Response({
                'code': 400,
                'message': '该邮箱已被注册'
            }, status=status.HTTP_400_BAD_REQUEST)
        elif account_type == 'phone' and Counselor.objects.filter(phone=account).exists():
            return Response({
                'code': 400,
                'message': '该手机号已被注册'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建咨询师用户
        counselor = Counselor.objects.create(
            username=username,
            name=username,  # 默认使用用户名作为姓名
            email=account if account_type == 'email' else '',
            phone=account if account_type == 'phone' else '',
            password=make_password(password),
            gender='男',  # 默认值
            status='启用'
        )
        
        # 创建咨询师详情
        CounselorProfile.objects.create(
            counselor=counselor,
            name=username
        )
        
        # 标记验证码为已验证
        vc.is_verified = True
        vc.save(update_fields=['is_verified'])
        
        return Response({
            'code': 0,
            'message': '注册成功'
        })


class SendEmailCodeView(APIView):
    """
    发送邮箱验证码
    POST /api/consultant/auth/email
    支持注册和登录两种用途
    """
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        purpose = request.data.get('purpose', 'register')  # 默认为register，支持login
        
        if not email:
            return Response({
                'code': 400,
                'message': '邮箱必填'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证purpose参数
        if purpose not in ['register', 'login']:
            purpose = 'register'  # 默认使用register
        
        code = _generate_code()
        expires = now() + timedelta(minutes=5)
        
        VerificationCode.objects.create(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=expires,
        )
        
        sent = _send_email_code(email, code)
        if not sent:
            return Response({
                'code': 500,
                'message': '验证码发送失败，请检查邮件配置'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'code': 0,
            'message': '验证码已发送'
        })


class SendPhoneCodeView(APIView):
    """
    发送短信验证码
    POST /api/consult/auth/phone
    支持注册和登录两种用途
    """
    permission_classes = []
    
    def post(self, request):
        phone = request.data.get('phone')
        purpose = request.data.get('purpose', 'register')  # 默认为register，支持login
        
        if not phone:
            return Response({
                'code': 400,
                'message': '手机号必填'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证purpose参数
        if purpose not in ['register', 'login']:
            purpose = 'register'  # 默认使用register
        
        code = _generate_code()
        expires = now() + timedelta(minutes=5)
        
        VerificationCode.objects.create(
            phone=phone,
            code=code,
            purpose=purpose,
            expires_at=expires,
        )
        
        # TODO: 实现短信发送功能
        # 这里暂时返回成功，实际需要接入短信服务
        
        return Response({
            'code': 0,
            'message': '验证码已发送'
        })


class ResetPasswordView(APIView):
    """
    重置密码
    POST /api/consultant/auth/reset-password
    """
    permission_classes = []
    
    def post(self, request):
        account_type = request.data.get('accountType')
        account = request.data.get('account')
        verification_code = request.data.get('verificationCode')
        new_password = request.data.get('newPassword')
        
        if not account_type or not account or not verification_code or not new_password:
            return Response({
                'code': 400,
                'message': '参数不完整'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证验证码
        if account_type == 'email':
            vc = VerificationCode.objects.filter(
                email=account,
                purpose='register'  # 复用register用途
            ).order_by('-created_time').first()
        elif account_type == 'phone':
            vc = VerificationCode.objects.filter(
                phone=account,
                purpose='register'
            ).order_by('-created_time').first()
        else:
            return Response({
                'code': 400,
                'message': '账户类型错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not vc or vc.code != str(verification_code).strip() or (vc.expires_at and vc.expires_at < now()):
            return Response({
                'code': 400,
                'message': '验证码无效或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找用户
        if account_type == 'email':
            counselor = Counselor.objects.filter(email=account).first()
        else:
            counselor = Counselor.objects.filter(phone=account).first()
        
        if not counselor:
            return Response({
                'code': 404,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 更新密码
        counselor.password = make_password(new_password)
        counselor.save(update_fields=['password'])
        
        # 标记验证码为已验证
        vc.is_verified = True
        vc.save(update_fields=['is_verified'])
        
        return Response({
            'code': 0,
            'message': '密码重置成功'
        })


class DeactivateView(APIView):
    """
    注销账号
    POST /api/consultant/auth/deactivate
    """
    permission_classes = []
    
    def post(self, request):
        token = request.data.get('token')
        account_type = request.data.get('accountType')
        account = request.data.get('account')
        verification_code = request.data.get('verificationCode')
        
        if not token or not account_type or not account or not verification_code:
            return Response({
                'code': 400,
                'message': '参数不完整'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证token
        token_obj = ConsultantAuthToken.objects.filter(token=token, is_active=True).first()
        if not token_obj or (token_obj.expires_at and token_obj.expires_at < now()):
            return Response({
                'code': 401,
                'message': 'Token无效或已过期'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        counselor = token_obj.counselor
        
        # 验证验证码
        if account_type == 'email':
            if counselor.email != account:
                return Response({
                    'code': 400,
                    'message': '账户信息不匹配'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            vc = VerificationCode.objects.filter(
                email=account,
                purpose='register'
            ).order_by('-created_time').first()
        elif account_type == 'phone':
            if counselor.phone != account:
                return Response({
                    'code': 400,
                    'message': '账户信息不匹配'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            vc = VerificationCode.objects.filter(
                phone=account,
                purpose='register'
            ).order_by('-created_time').first()
        else:
            return Response({
                'code': 400,
                'message': '账户类型错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not vc or vc.code != str(verification_code).strip() or (vc.expires_at and vc.expires_at < now()):
            return Response({
                'code': 400,
                'message': '验证码无效或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 注销账号（软删除：将状态设为停用）
        counselor.status = '停用'
        counselor.save(update_fields=['status'])
        
        # 禁用所有token
        ConsultantAuthToken.objects.filter(counselor=counselor).update(is_active=False)
        
        return Response({
            'code': 0,
            'message': '账号注销成功'
        })

