"""
Django管理命令：生成测试数据
为每个表（除管理员表和咨询师表外）插入100条测试数据
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
import json

# Consultant app models
from Consultant.models import (
    CounselorProfile, ConsultationRecord, ConsultationSession,
    ConsultationOrder, ConsultationReview, CounselorSchedule,
    CounselorAbsence, FileStorage
)

# CounselorAdmin app models
from CounselorAdmin.models import (
    Appointment, BannerModule, Notification, Category, Article,
    ReferralUnit, StudentReferral, NegativeEvent, InterviewAssessment,
    Schedule, Cancellation, Counselor
)


class Command(BaseCommand):
    help = '为每个表生成100条测试数据（排除管理员表和咨询师表）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--counselor-id',
            type=int,
            default=2,
            help='咨询师ID（默认：2）'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='每个表生成的数据条数（默认：100）'
        )

    def handle(self, *args, **options):
        counselor_id = options['counselor_id']
        count = options['count']

        # 验证咨询师是否存在
        try:
            counselor = Counselor.objects.get(id=counselor_id)
            self.stdout.write(self.style.SUCCESS(f'使用咨询师ID: {counselor_id} ({counselor.name})'))
        except Counselor.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'咨询师ID {counselor_id} 不存在！'))
            return

        self.stdout.write(self.style.SUCCESS(f'开始生成测试数据，每个表 {count} 条...'))

        # 生成测试数据
        try:
            # 1. 咨询师详情表 (CounselorProfile) - 注意：OneToOne关系，只能有一个
            self.generate_counselor_profiles(counselor, count)

            # 2. 咨询档案主表 (ConsultationRecord) - 需要先创建
            records = self.generate_consultation_records(counselor, count)

            # 3. 咨询访谈详情表 (ConsultationSession) - 需要ConsultationRecord
            self.generate_consultation_sessions(counselor, records, count)

            # 4. 咨询订单表 (ConsultationOrder) - 需要ConsultationRecord
            orders = self.generate_consultation_orders(counselor, records, count)

            # 5. 咨询评价表 (ConsultationReview) - 需要ConsultationOrder
            self.generate_consultation_reviews(counselor, orders, count)

            # 6. 咨询师排班表 (CounselorSchedule)
            self.generate_counselor_schedules(counselor, count)

            # 7. 停诊记录表 (CounselorAbsence)
            self.generate_counselor_absences(counselor, count)

            # 8. 文件存储表 (FileStorage)
            self.generate_file_storage(counselor, count)

            # 9. 预约订单表 (Appointment)
            self.generate_appointments(counselor, count)

            # 10. 轮播图模块表 (BannerModule)
            self.generate_banner_modules(count)

            # 11. 通知表 (Notification)
            self.generate_notifications(count)

            # 12. 宣教栏目表 (Category) - 需要先创建
            categories = self.generate_categories(count)

            # 13. 宣教资讯表 (Article) - 需要Category
            self.generate_articles(categories, count)

            # 14. 转介单位表 (ReferralUnit) - 需要先创建
            referral_units = self.generate_referral_units(count)

            # 15. 学生转介表 (StudentReferral) - 需要ReferralUnit（可选）
            self.generate_student_referrals(referral_units, count)

            # 16. 负面事件表 (NegativeEvent)
            self.generate_negative_events(count)

            # 17. 访谈评估表 (InterviewAssessment)
            self.generate_interview_assessments(count)

            # 18. 排班表 (Schedule) - 管理员端
            self.generate_schedules(counselor, count)

            # 19. 停诊表 (Cancellation) - 管理员端
            self.generate_cancellations(counselor, count)

            self.stdout.write(self.style.SUCCESS(f'\n成功生成所有测试数据！每个表 {count} 条。'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'生成测试数据时出错: {str(e)}'))
            import traceback
            traceback.print_exc()

    def generate_counselor_profiles(self, counselor, count):
        """生成咨询师详情表数据"""
        self.stdout.write('生成咨询师详情表数据...')
        # OneToOne关系，检查是否已存在
        if CounselorProfile.objects.filter(counselor=counselor).exists():
            self.stdout.write(self.style.WARNING('咨询师详情已存在，跳过...'))
            return

        CounselorProfile.objects.create(
            counselor=counselor,
            name=counselor.name,
            organization='测试心理咨询机构',
            introduction='资深心理咨询师，拥有丰富的咨询经验',
            experience='从事心理咨询工作10年，擅长青少年心理问题',
            expertise=['焦虑症', '抑郁症', '人际关系'],
            education='心理学硕士',
            certifications='国家二级心理咨询师',
            consultation_count=random.randint(0, 500)
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ 咨询师详情表: 1条'))

    def generate_consultation_records(self, counselor, count):
        """生成咨询档案主表数据"""
        self.stdout.write('生成咨询档案主表数据...')
        records = []
        genders = ['男', '女']
        client_types = ['student', 'adult']
        statuses = ['active', 'completed', 'closed']
        schools = ['第一中学', '第二中学', '实验中学', '外国语学校', '师范大学附属中学']
        grades = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '初一', '初二', '初三', '高一', '高二', '高三']

        for i in range(count):
            client_type = random.choice(client_types)
            gender = random.choice(genders)
            record_no = f'REC{timezone.now().strftime("%Y%m%d")}{str(i+1).zfill(6)}'

            if client_type == 'student':
                record = ConsultationRecord.objects.create(
                    record_no=record_no,
                    client_name=f'学生{random.randint(1, 1000)}',
                    client_type=client_type,
                    gender=gender,
                    age=random.randint(10, 18),
                    student_id=f'STU{random.randint(100000, 999999)}',
                    school=random.choice(schools),
                    grade=random.choice(grades),
                    class_name=f'{random.randint(1, 20)}班',
                    contact=f'138{random.randint(10000000, 99999999)}',
                    emergency_contact_name=f'联系人{random.randint(1, 100)}',
                    emergency_contact_phone=f'139{random.randint(10000000, 99999999)}',
                    referral_source=random.choice(['学校推荐', '家长推荐', '自主咨询', '其他']),
                    main_complaint='学习压力大，情绪低落',
                    consultation_goal='缓解学习压力，改善情绪状态',
                    counselor=counselor,
                    interview_count=random.randint(0, 10),
                    current_status=random.choice(statuses),
                    created_by=counselor
                )
            else:
                record = ConsultationRecord.objects.create(
                    record_no=record_no,
                    client_name=f'成人{random.randint(1, 1000)}',
                    client_type=client_type,
                    gender=gender,
                    age=random.randint(20, 60),
                    education=random.choice(['高中', '大专', '本科', '硕士', '博士']),
                    occupation=random.choice(['教师', '医生', '工程师', '销售', '自由职业']),
                    contact=f'138{random.randint(10000000, 99999999)}',
                    emergency_contact_name=f'联系人{random.randint(1, 100)}',
                    emergency_contact_phone=f'139{random.randint(10000000, 99999999)}',
                    referral_source=random.choice(['朋友推荐', '网络搜索', '自主咨询', '其他']),
                    main_complaint='工作压力大，人际关系困扰',
                    consultation_goal='改善工作状态，提升人际交往能力',
                    counselor=counselor,
                    interview_count=random.randint(0, 10),
                    current_status=random.choice(statuses),
                    created_by=counselor
                )
            records.append(record)

        self.stdout.write(self.style.SUCCESS(f'  ✓ 咨询档案主表: {count}条'))
        return records

    def generate_consultation_sessions(self, counselor, records, count):
        """生成咨询访谈详情表数据"""
        self.stdout.write('生成咨询访谈详情表数据...')
        visit_statuses = ['scheduled', 'completed', 'cancelled']
        created = 0

        for record in records:
            # 为每个档案生成1-5次访谈
            session_count = random.randint(1, 5)
            for session_num in range(1, session_count + 1):
                if created >= count:
                    break
                ConsultationSession.objects.create(
                    record=record,
                    session_number=session_num,
                    interview_date=timezone.now().date() - timedelta(days=random.randint(0, 365)),
                    interview_time=f'{random.randint(9, 17)}:00-{random.randint(10, 18)}:00',
                    duration=random.randint(30, 120),
                    visit_status=random.choice(visit_statuses),
                    objective_description='来访者表现正常，情绪稳定',
                    doctor_evaluation='情况良好，建议继续咨询',
                    follow_up_plan='定期回访，关注情绪变化',
                    next_visit_plan='下周同一时间继续咨询',
                    crisis_status=random.choice(['无', '低风险', '中风险']),
                    consultant_name=counselor.name,
                    is_third_party_evaluation=random.choice([True, False]),
                    created_by=counselor
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 咨询访谈详情表: {created}条'))

    def generate_consultation_orders(self, counselor, records, count):
        """生成咨询订单表数据"""
        self.stdout.write('生成咨询订单表数据...')
        orders = []
        service_types = ['online', 'offline']
        statuses = ['pending', 'accepted', 'completed', 'cancelled', 'rejected']
        keywords_list = [
            ['焦虑', '压力'],
            ['抑郁', '情绪'],
            ['人际关系', '沟通'],
            ['学习', '考试'],
            ['家庭', '亲子']
        ]

        for i in range(count):
            record = random.choice(records) if records else None
            order_no = f'ORD{timezone.now().strftime("%Y%m%d")}{str(i+1).zfill(6)}'
            appointment_date = timezone.now().date() + timedelta(days=random.randint(1, 30))

            order = ConsultationOrder.objects.create(
                order_no=order_no,
                record=record,
                counselor=counselor,
                service_type=random.choice(service_types),
                counseling_keywords=random.choice(keywords_list),
                appointment_date=appointment_date,
                time_slot=f'{random.randint(9, 17)}:00-{random.randint(10, 18)}:00',
                contact_info=f'138{random.randint(10000000, 99999999)}',
                status=random.choice(statuses),
                accept_time=timezone.now() - timedelta(days=random.randint(0, 10)) if random.choice([True, False]) else None,
                end_time=timezone.now() - timedelta(days=random.randint(0, 5)) if random.choice([True, False]) else None
            )
            orders.append(order)

        self.stdout.write(self.style.SUCCESS(f'  ✓ 咨询订单表: {count}条'))
        return orders

    def generate_consultation_reviews(self, counselor, orders, count):
        """生成咨询评价表数据"""
        self.stdout.write('生成咨询评价表数据...')
        created = 0

        for order in orders:
            if created >= count:
                break
            # 每个订单可能有0-1个评价
            if random.choice([True, False]):
                ConsultationReview.objects.create(
                    order=order,
                    counselor=counselor,
                    rating=random.randint(1, 5),
                    content=random.choice([
                        '咨询师很专业，帮助很大',
                        '服务态度很好，很满意',
                        '效果不错，推荐',
                        '一般般',
                        '还需要继续咨询'
                    ])
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 咨询评价表: {created}条'))

    def generate_counselor_schedules(self, counselor, count):
        """生成咨询师排班表数据"""
        self.stdout.write('生成咨询师排班表数据...')
        created = 0
        start_date = timezone.now().date()

        for i in range(count * 2):  # 多生成一些，因为同一天只能有一个排班
            if created >= count:
                break
            schedule_date = start_date + timedelta(days=i)
            # 检查是否已存在
            if CounselorSchedule.objects.filter(counselor=counselor, schedule_date=schedule_date).exists():
                continue

            time_slots = [
                {'start': '09:00', 'end': '10:00', 'available': True},
                {'start': '10:00', 'end': '11:00', 'available': True},
                {'start': '14:00', 'end': '15:00', 'available': True},
                {'start': '15:00', 'end': '16:00', 'available': True},
            ]

            CounselorSchedule.objects.create(
                counselor=counselor,
                schedule_date=schedule_date,
                time_slots=time_slots,
                max_appointments=random.randint(3, 8),
                available_slots=random.randint(0, 5)
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 咨询师排班表: {created}条'))

    def generate_counselor_absences(self, counselor, count):
        """生成停诊记录表数据"""
        self.stdout.write('生成停诊记录表数据...')
        absence_types = ['sick_leave', 'personal_leave', 'other']
        statuses = ['pending', 'approved']

        for i in range(count):
            start_time = timezone.now() + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
            end_time = start_time + timedelta(days=random.randint(1, 3))

            CounselorAbsence.objects.create(
                counselor=counselor,
                absence_type=random.choice(absence_types),
                start_time=start_time,
                end_time=end_time,
                reason=random.choice(['生病', '个人事务', '培训', '其他']),
                status=random.choice(statuses)
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 停诊记录表: {count}条'))

    def generate_file_storage(self, counselor, count):
        """生成文件存储表数据"""
        self.stdout.write('生成文件存储表数据...')
        file_types = ['image/jpeg', 'image/png', 'application/pdf', 'application/msword']
        modules = ['consultation', 'education', 'referral', 'other']

        for i in range(count):
            FileStorage.objects.create(
                file_name=f'测试文件{i+1}.{random.choice(["jpg", "png", "pdf", "doc"])}',
                file_path=f'/static/files/test_file_{i+1}.{random.choice(["jpg", "png", "pdf", "doc"])}',
                file_size=random.randint(1024, 10485760),  # 1KB - 10MB
                file_type=random.choice(file_types),
                module=random.choice(modules),
                associated_id=random.randint(1, 1000),
                uploader=counselor
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 文件存储表: {count}条'))

    def generate_appointments(self, counselor, count):
        """生成预约订单表数据"""
        self.stdout.write('生成预约订单表数据...')
        service_types = ['个体咨询', '团体咨询', '家庭咨询', '危机干预']
        statuses = ['未开始', '进行中', '已完成']
        genders = ['男', '女']

        for i in range(count):
            order_no = f'APT{timezone.now().strftime("%Y%m%d")}{str(i+1).zfill(6)}'
            Appointment.objects.create(
                order_no=order_no,
                client_name=f'客户{random.randint(1, 1000)}',
                client_gender=random.choice(genders),
                client_age=random.randint(10, 60),
                service_type=random.choice(service_types),
                counseling_keywords=random.choice(['焦虑', '抑郁', '人际关系', '学习压力', '家庭问题']),
                appointment_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                time_slot=random.choice(['上午', '下午', '晚上']),
                status=random.choice(statuses),
                counselor=counselor,
                end_time=timezone.now() + timedelta(days=random.randint(0, 10)) if random.choice([True, False]) else None
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 预约订单表: {count}条'))

    def generate_banner_modules(self, count):
        """生成轮播图模块表数据"""
        self.stdout.write('生成轮播图模块表数据...')
        modules = ['首页', '咨询页', '教育页', '关于我们']

        for i in range(count):
            BannerModule.objects.create(
                module_name=f'{random.choice(modules)}{i+1}',
                carousel_count=random.randint(1, 5),
                created_by='系统',
                pictures=[
                    f'/static/banners/banner_{j+1}.jpg' for j in range(random.randint(1, 5))
                ]
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 轮播图模块表: {count}条'))

    def generate_notifications(self, count):
        """生成通知表数据"""
        self.stdout.write('生成通知表数据...')
        titles = [
            '系统维护通知',
            '新功能上线通知',
            '重要公告',
            '服务更新通知',
            '节假日安排通知'
        ]

        for i in range(count):
            Notification.objects.create(
                title=f'{random.choice(titles)} {i+1}',
                content=f'这是第{i+1}条通知的详细内容。' * 10,
                is_published=random.choice([True, False]),
                created_by='系统'
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 通知表: {count}条'))

    def generate_categories(self, count):
        """生成宣教栏目表数据"""
        self.stdout.write('生成宣教栏目表数据...')
        categories = []
        category_names = [
            '心理健康知识', '情绪管理', '人际关系', '学习指导',
            '家庭教育', '职业规划', '压力管理', '自我成长'
        ]

        for i in range(count):
            category = Category.objects.create(
                category_name=f'{random.choice(category_names)}{i+1}',
                sort_order=i,
                created_by='系统'
            )
            categories.append(category)

        self.stdout.write(self.style.SUCCESS(f'  ✓ 宣教栏目表: {count}条'))
        return categories

    def generate_articles(self, categories, count):
        """生成宣教资讯表数据"""
        self.stdout.write('生成宣教资讯表数据...')
        article_types = ['article', 'video']

        for i in range(count):
            Article.objects.create(
                category=random.choice(categories),
                title=f'心理健康知识文章 {i+1}',
                content=f'这是第{i+1}篇心理健康知识文章的详细内容。' * 50,
                collect_count=random.randint(0, 1000),
                like_count=random.randint(0, 500),
                read_count=random.randint(0, 5000),
                created_by='系统',
                video=f'https://example.com/video_{i+1}.mp4' if random.choice([True, False]) else '',
                video_path=f'/static/videos/video_{i+1}.mp4' if random.choice([True, False]) else '',
                resource=random.choice(['网络', '书籍', '期刊', '其他']),
                type=random.choice(article_types)
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 宣教资讯表: {count}条'))

    def generate_referral_units(self, count):
        """生成转介单位表数据"""
        self.stdout.write('生成转介单位表数据...')
        units = []
        unit_names = [
            '第一人民医院', '第二人民医院', '精神卫生中心',
            '心理咨询中心', '康复医院', '专科医院'
        ]

        for i in range(count):
            unit = ReferralUnit.objects.create(
                unit_name=f'{random.choice(unit_names)}{i+1}',
                address=f'测试市测试区测试街道{i+1}号',
                contact_phone=f'0{random.randint(100, 999)}-{random.randint(10000000, 99999999)}',
                created_by='系统'
            )
            units.append(unit)

        self.stdout.write(self.style.SUCCESS(f'  ✓ 转介单位表: {count}条'))
        return units

    def generate_student_referrals(self, referral_units, count):
        """生成学生转介表数据"""
        self.stdout.write('生成学生转介表数据...')
        genders = ['男', '女']
        schools = ['第一中学', '第二中学', '实验中学']
        grades = ['初一', '初二', '初三', '高一', '高二', '高三']

        for i in range(count):
            StudentReferral.objects.create(
                student_name=f'学生{random.randint(1, 1000)}',
                gender=random.choice(genders),
                school=random.choice(schools),
                grade=random.choice(grades),
                class_name=f'{random.randint(1, 20)}班',
                referral_unit=random.choice(referral_units) if referral_units else None,
                referral_reason='需要专业心理评估和干预',
                referral_date=timezone.now().date() - timedelta(days=random.randint(0, 365)),
                image_path=f'/static/referral_images/referral_{i+1}.jpg' if random.choice([True, False]) else '',
                created_by='系统'
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 学生转介表: {count}条'))

    def generate_negative_events(self, count):
        """生成负面事件表数据"""
        self.stdout.write('生成负面事件表数据...')
        organizations = ['第一中学', '第二中学', '实验中学']
        grades = ['初一', '初二', '初三', '高一', '高二', '高三']

        for i in range(count):
            NegativeEvent.objects.create(
                student_name=f'学生{random.randint(1, 1000)}',
                organization=random.choice(organizations),
                grade=random.choice(grades),
                class_name=f'{random.randint(1, 20)}班',
                event_details=f'第{i+1}个负面事件的详细描述',
                event_date=timezone.now().date() - timedelta(days=random.randint(0, 365)),
                created_by='系统',
                disabled=random.choice([True, False])
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 负面事件表: {count}条'))

    def generate_interview_assessments(self, count):
        """生成访谈评估表数据"""
        self.stdout.write('生成访谈评估表数据...')
        organizations = ['第一中学', '第二中学', '实验中学']
        grades = ['初一', '初二', '初三', '高一', '高二', '高三']
        interview_statuses = ['待处理', '进行中', '已完成']
        interview_types = ['初次访谈', '定期访谈', '紧急访谈']
        doctor_assessments = ['正常', '轻度', '中度', '重度']
        follow_up_plans = ['继续观察', '定期回访', '转介', '结案']

        for i in range(count):
            InterviewAssessment.objects.create(
                organization=random.choice(organizations),
                grade=random.choice(grades),
                class_name=f'{random.randint(1, 20)}班',
                student_name=f'学生{random.randint(1, 1000)}',
                interview_count=random.randint(1, 10),
                interview_status=random.choice(interview_statuses),
                interview_type=random.choice(interview_types),
                doctor_assessment=random.choice(doctor_assessments),
                follow_up_plan=random.choice(follow_up_plans)
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 访谈评估表: {count}条'))

    def generate_schedules(self, counselor, count):
        """生成排班表数据（管理员端）"""
        self.stdout.write('生成排班表数据（管理员端）...')
        start_date = timezone.now().date()

        for i in range(count):
            work_date = start_date + timedelta(days=i)
            # 检查是否已存在
            if Schedule.objects.filter(counselor=counselor, work_date=work_date).exists():
                continue

            Schedule.objects.create(
                counselor=counselor,
                work_date=work_date,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime('17:00', '%H:%M').time(),
                created_by='系统'
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 排班表（管理员端）: {count}条'))

    def generate_cancellations(self, counselor, count):
        """生成停诊表数据（管理员端）"""
        self.stdout.write('生成停诊表数据（管理员端）...')

        for i in range(count):
            cancel_start = timezone.now() + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
            cancel_end = cancel_start + timedelta(days=random.randint(1, 3))

            Cancellation.objects.create(
                counselor=counselor,
                cancel_start=cancel_start,
                cancel_end=cancel_end,
                created_by='系统'
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ 停诊表（管理员端）: {count}条'))

