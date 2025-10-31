import base64
import io
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from django.utils.timezone import now
# 引入Django自带的Token模型
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from CounselorAdmin.models import VerificationCode, Captcha, AdminUser, AdminAuthToken
from CounselorAdmin.Serilizers import (
    VerificationCodeSerializer,
    CaptchaSerializer,
    AdminUserCreateSerializer,
)

# import coreapi
# print(coreapi.__version__)  # 检查 coreapi 是否可用
#
# # 使用信号机制创建Token
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)  # Django的信号机制
# def generate_token(sender, instance=None, created=False, **kwargs):
#     """
#     创建用户时自动生成Token
#     :param sender:
#     :param instance:
#     :param created:
#     :param kwargs:
#     :return:
#     """
#     if created:
#         Token.objects.create(user=instance)


def _generate_code(length: int = 6) -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def _generate_captcha_text(length: int = 4) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _generate_captcha_image_base64(text: str) -> str:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return ''
    img = Image.new('RGB', (120, 40), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 24)
    except Exception:
        font = ImageFont.load_default()
    draw.text((10, 8), text, fill=(0, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def _send_email_code(email: str, code: str) -> bool:
    """
    使用163邮箱SMTP发送验证码
    """
    try:
        # 163邮箱SMTP配置
        smtp_server = "smtp.163.com"
        smtp_port = 465
        sender_email = "hock2022@163.com"
        sender_password = "CER9J5e7FrVscZKZ"  # 授权码
        smtp_user = "hock2022@163.com"  # SMTP用户名
        
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = '【管理员注册验证码】'
        
        # 邮件正文
        body = f'您的验证码是：{code}，5分钟内有效。'
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


class RegisterSendCodeView(APIView):
    """
    发送邮箱验证码接口 - 不需要鉴权
    """
    permission_classes = []  # 不需要任何权限
    
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('user_name') or ''
        phone = request.data.get('phone') or ''
        
        if not email:
            return Response({'message': 'email必填'}, status=status.HTTP_400_BAD_REQUEST)

        code = _generate_code()
        expires = now() + timedelta(minutes=5)
        VerificationCode.objects.create(
            username=username,
            email=email,
            phone=phone,
            code=code,
            purpose='register',
            expires_at=expires,
        )
        sent = _send_email_code(email, code)
        if not sent:
            return Response({'message': '验证码发送失败，请检查邮件配置'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'message': '验证码已发送'})


# class RegisterView(APIView):
#     def post(self, request):
#         verify_code = request.data.get('verify_code')
#         email = request.data.get('email')
#         phone = request.data.get('phone')
#         username = request.data.get('user_name')
#         password = request.data.get('password')

#         if not username or not password:
#             return Response({'message': '用户名与密码必填'}, status=status.HTTP_400_BAD_REQUEST)

#         if email:
#             vc = VerificationCode.objects.filter(email=email, purpose='register').order_by('-created_time').first()
#         else:
#             vc = VerificationCode.objects.filter(phone=phone, purpose='register').order_by('-created_time').first()

#         if not vc or vc.code != verify_code or (vc.expires_at and vc.expires_at < now()):
#             return Response({'message': '验证码无效或已过期'}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = AdminUserCreateSerializer(data={
#             'username': username,
#             'gender': request.data.get('gender', '男'),
#             'email': email,
#             'phone': phone,
#             'password': password,
#         })
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         vc.is_verified = True
#         vc.save(update_fields=['is_verified'])
#         return Response({'message': '注册成功'})

class RegisterView(APIView):
    """
    注册接口 - 只需要邮箱验证码，手机号可选存储，不需要鉴权
    """
    permission_classes = []  # 不需要任何权限
    
    def post(self, request):
        # 从请求中获取验证码、邮箱、手机号、用户名和密码
        verify_code = request.data.get('verify_code')
        email = request.data.get('email')
        phone = request.data.get('phone', '')  # 手机号可选，但要存储
        username = request.data.get('user_name')
        password = request.data.get('password')

        # 检查必填字段
        if not email:
            return Response({'message': '邮箱必填'}, status=status.HTTP_400_BAD_REQUEST)
        if not username or not password:
            return Response({'message': '用户名与密码必填'}, status=status.HTTP_400_BAD_REQUEST)
        if not verify_code:
            return Response({'message': '验证码必填'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证邮箱验证码
        vc = VerificationCode.objects.filter(email=email, purpose='register').order_by('-created_time').first()
        if not vc or vc.code != str(verify_code).strip() or (vc.expires_at and vc.expires_at < now()):
            return Response({'message': '验证码无效或已过期'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查邮箱是否已注册
        if AdminUser.objects.filter(email=email).exists():
            return Response({'message': '该邮箱已被注册'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建管理员用户序列化器并验证数据
        serializer = AdminUserCreateSerializer(data={
            'username': username,
            'gender': request.data.get('gender', '男'),
            'email': email,
            'phone': phone,  # 手机号存储但不验证
            'password': password,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 标记验证码为已验证
        vc.is_verified = True
        vc.save(update_fields=['is_verified'])
            
        # 返回注册成功响应
        return Response({'message': '注册成功'})

# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         phone = request.data.get('phone')
#         password = request.data.get('password')
#         captcha_text = request.data.get('captcha')

#         if not captcha_text:
#             return Response({'message': '缺少图形验证码'}, status=status.HTTP_400_BAD_REQUEST)
#         latest_captcha = Captcha.objects.filter(is_used=False).order_by('-created_time').first()
#         if not latest_captcha or latest_captcha.text.lower() != str(captcha_text).strip().lower() or (
#             latest_captcha.expires_at and latest_captcha.expires_at < now()
#         ):
#             return Response({'message': '图形验证码错误或过期'}, status=status.HTTP_400_BAD_REQUEST)
#         latest_captcha.is_used = True
#         latest_captcha.save(update_fields=['is_used'])

#         user_qs = AdminUser.objects.all()
#         if email:
#             user_qs = user_qs.filter(email=email)
#         if phone:
#             user_qs = user_qs.filter(phone=phone)
#         user = user_qs.first()
#         if not user:
#             return Response({'message': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

#         from django.contrib.auth.hashers import check_password
#         if not check_password(password, user.password):
#             return Response({'message': '密码错误'}, status=status.HTTP_400_BAD_REQUEST)

#         # 生成自定义加盐token
#         salt = getattr(settings, 'ADMIN_TOKEN_SALT', 'admin_salt')
#         raw = f"{user.id}:{secrets.token_urlsafe(24)}:{salt}"
#         token = base64.urlsafe_b64encode(raw.encode('utf-8')).decode('utf-8')

#         AdminAuthToken.objects.filter(user=user, is_active=True).update(is_active=False)
#         AdminAuthToken.objects.create(user=user, token=token, expires_at=now() + timedelta(days=7))
#         return Response({'token': token, 'id': str(user.id)})


class LoginView(APIView):
    """
    登录接口 - 只需要邮箱和密码，图形验证码接收true即可，不需要鉴权
    """
    permission_classes = []  # 不需要任何权限
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        captcha_text = request.data.get('captcha')

        # 检查必填字段
        if not email:
            return Response({'message': '邮箱必填'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'message': '密码必填'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 图形验证码检查 - 如果传入true或"true"则通过
        if captcha_text:
            captcha_str = str(captcha_text).strip().lower()
            if captcha_str not in ['true', '1', 'yes']:
                return Response({'message': '图形验证码无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': '缺少图形验证码'}, status=status.HTTP_400_BAD_REQUEST)

        # 根据邮箱查找用户
        user = AdminUser.objects.filter(email=email).first()
        if not user:
            return Response({'message': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证密码
        from django.contrib.auth.hashers import check_password
        if not check_password(password, user.password):
            return Response({'message': '密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成UUID格式的token（类似示例中的格式）
        import uuid
        token = str(uuid.uuid4())

        # 禁用旧的token，创建新token
        AdminAuthToken.objects.filter(user=user, is_active=True).update(is_active=False)
        AdminAuthToken.objects.create(user=user, token=token, expires_at=now() + timedelta(days=7))
        
        return Response({'token': token, 'id': str(user.id)})

class CaptchaView(APIView):
    permission_classes = []  # 空列表表示不需要任何权限
    
    def get(self, request):
        text = _generate_captcha_text()
        image_b64 = _generate_captcha_image_base64(text)
        key = secrets.token_urlsafe(16)
        Captcha.objects.create(
            key=key,
            text=text,
            image_base64=image_b64,
            expires_at=now() + timedelta(minutes=3),
        )
        return Response({
            'captcha_key': key,
            'captcha_image_base64': image_b64,
        })


