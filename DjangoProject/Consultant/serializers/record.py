"""
咨询档案相关序列化器
"""
import json
from rest_framework import serializers
from Consultant.models import ConsultationRecord, ConsultationSession


class ConsultationRecordListSerializer(serializers.ModelSerializer):
    """咨询档案列表序列化器"""
    id = serializers.IntegerField(read_only=True)
    std_name = serializers.CharField(source='client_name', read_only=True)
    std_grade = serializers.CharField(source='grade', read_only=True)
    std_class = serializers.CharField(source='class_name', read_only=True)
    std_school = serializers.CharField(source='school', read_only=True)
    interview_count = serializers.IntegerField(read_only=True)
    interview_status = serializers.SerializerMethodField()
    interview_type = serializers.SerializerMethodField()
    doctor_evaluation = serializers.SerializerMethodField()
    follow_up_plan = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(source='created_time', read_only=True)
    
    class Meta:
        model = ConsultationRecord
        fields = [
            'id', 'std_name', 'std_grade', 'std_class', 'std_school',
            'interview_count', 'interview_status', 'interview_type',
            'doctor_evaluation', 'follow_up_plan', 'create_time'
        ]
    
    def get_interview_status(self, obj):
        """获取访谈状态"""
        status_map = {
            'active': '进行中',
            'completed': '已完成',
            'closed': '已关闭'
        }
        return status_map.get(obj.current_status, obj.current_status)
    
    def get_doctor_evaluation(self, obj):
        """获取医生评定（从最新会话中获取）"""
        latest_session = obj.sessions.order_by('-session_number').first()
        if latest_session:
            return latest_session.doctor_evaluation or ''
        return ''
    
    def get_follow_up_plan(self, obj):
        """获取后续计划（从最新会话中获取）"""
        latest_session = obj.sessions.order_by('-session_number').first()
        if latest_session:
            return latest_session.follow_up_plan or ''
        return ''
    
    def get_interview_type(self, obj):
        """获取访谈类型"""
        return obj.interview_type or ''


class ConsultationRecordCreateSerializer(serializers.Serializer):
    """创建咨询档案序列化器"""
    std_name = serializers.CharField(required=True, help_text='学生姓名')
    std_grade = serializers.CharField(required=True, help_text='年级')
    std_class = serializers.CharField(required=True, help_text='班级')
    std_school = serializers.CharField(required=True, help_text='学校')
    interview_count = serializers.CharField(required=True, help_text='访谈次数')
    interview_status = serializers.CharField(required=True, help_text='访谈状态')
    interview_type = serializers.CharField(required=True, help_text='访谈类型')
    doctor_evaluation = serializers.CharField(required=True, help_text='医生评定')
    follow_up_plan = serializers.CharField(required=True, help_text='后续计划')


class ConsultationSessionDetailSerializer(serializers.ModelSerializer):
    """咨询会话详情序列化器"""
    id = serializers.IntegerField(read_only=True)
    count = serializers.CharField(source='session_number', read_only=True)
    name = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    studentId = serializers.CharField(source='record.student_id', read_only=True)
    school = serializers.CharField(source='record.school', read_only=True)
    grade = serializers.CharField(source='record.grade', read_only=True)
    class_field = serializers.CharField(source='record.class_name', read_only=True)
    date = serializers.DateField(source='interview_date', read_only=True)
    time = serializers.CharField(source='interview_time', read_only=True)
    duration = serializers.CharField(read_only=True)
    visitStatus = serializers.CharField(source='visit_status', read_only=True)
    description = serializers.CharField(source='objective_description', read_only=True)
    doctorEvaluation = serializers.CharField(source='doctor_evaluation', read_only=True)
    followUpPlan = serializers.CharField(source='follow_up_plan', read_only=True)
    nextVisitPlan = serializers.CharField(source='next_visit_plan', read_only=True)
    crisisStatus = serializers.SerializerMethodField()
    consultantName = serializers.CharField(source='consultant_name', read_only=True)
    signatureImage = serializers.CharField(source='signature_image', read_only=True)
    attachImage = serializers.SerializerMethodField()
    isThirdPartyEvaluation = serializers.BooleanField(source='is_third_party_evaluation', read_only=True)
    
    class Meta:
        model = ConsultationSession
        fields = [
            'id', 'count', 'name', 'gender', 'studentId', 'school', 'grade',
            'class_field', 'date', 'time', 'duration', 'visitStatus',
            'description', 'doctorEvaluation', 'followUpPlan', 'nextVisitPlan',
            'crisisStatus', 'consultantName', 'signatureImage', 'attachImage',
            'isThirdPartyEvaluation'
        ]
    
    def get_name(self, obj):
        """获取来访者姓名"""
        return obj.record.client_name if obj.record else ''
    
    def get_gender(self, obj):
        """获取性别"""
        return obj.record.gender if obj.record else ''
    
    def get_attachImage(self, obj):
        """获取附加图片（取第一张）"""
        if obj.attach_images and isinstance(obj.attach_images, list) and len(obj.attach_images) > 0:
            return obj.attach_images[0]
        return ''
    
    def get_duration(self, obj):
        """获取访谈时长"""
        if obj.duration:
            return f"{obj.duration}分钟"
        return ''
    
    def get_crisisStatus(self, obj):
        """获取危机状态（转换为数组）"""
        if obj.crisis_status:
            # 如果是字符串，尝试解析为数组
            if isinstance(obj.crisis_status, str):
                # 尝试按逗号分隔
                if ',' in obj.crisis_status:
                    return [s.strip() for s in obj.crisis_status.split(',') if s.strip()]
                # 如果是JSON字符串，尝试解析
                try:
                    parsed = json.loads(obj.crisis_status)
                    if isinstance(parsed, list):
                        return parsed
                    return [parsed] if parsed else []
                except:
                    # 如果不是JSON，返回单个元素的数组
                    return [obj.crisis_status] if obj.crisis_status else []
            # 如果已经是数组，直接返回
            if isinstance(obj.crisis_status, list):
                return obj.crisis_status
        return []


class ConsultationSessionCreateSerializer(serializers.Serializer):
    """创建咨询会话序列化器"""
    record_id = serializers.IntegerField(required=True, help_text='档案ID')
    count = serializers.CharField(required=True, help_text='第几次访谈')
    name = serializers.CharField(required=False, help_text='姓名')
    gender = serializers.CharField(required=False, help_text='性别')
    studentId = serializers.CharField(required=False, help_text='学籍号')
    school = serializers.CharField(required=False, help_text='学校')
    grade = serializers.CharField(required=False, help_text='年级')
    class_field = serializers.CharField(required=False, help_text='班级')
    date = serializers.DateField(required=False, help_text='访谈日期')
    time = serializers.CharField(required=False, help_text='访谈时间')
    duration = serializers.CharField(required=False, help_text='访谈时长')
    visitStatus = serializers.CharField(required=False, help_text='访谈状态')
    description = serializers.CharField(required=False, help_text='客观描述')
    doctorEvaluation = serializers.CharField(required=False, help_text='医生评定')
    followUpPlan = serializers.CharField(required=False, help_text='后续计划')
    nextVisitPlan = serializers.CharField(required=False, help_text='下次访谈计划')
    crisisStatus = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='危机状态数组'
    )
    consultantName = serializers.CharField(required=False, help_text='咨询师姓名')
    isThirdPartyEvaluation = serializers.BooleanField(required=False, help_text='是否为他评')
    signatureImage = serializers.CharField(required=False, help_text='签名图片')
    attachImages = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='附加图片数组'
    )

