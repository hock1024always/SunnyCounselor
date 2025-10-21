from rest_framework import serializers
from .models import Counselor, Consultation, Schedule, Review


class CounselorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counselor
        fields = ['id', 'name', 'gender', 'age', 'phone', 'email', 'avatar',
                  'service_types', 'introduction', 'years_of_experience']


class ConsultationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_gender = serializers.CharField(source='client.gender', read_only=True)
    client_age = serializers.IntegerField(source='client.age', read_only=True)

    class Meta:
        model = Consultation
        fields = ['id', 'client', 'client_name', 'client_gender', 'client_age',
                  'type', 'status', 'scheduled_at', 'started_at', 'ended_at',
                  'description', 'notes', 'created_at']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'date', 'start_time', 'end_time', 'is_available', 'reason']


class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'client_name', 'rating', 'comment', 'is_anonymous', 'created_at']

    def get_client_name(self, obj):
        return "匿名用户" if obj.is_anonymous else obj.client.name


class DashboardStatsSerializer(serializers.Serializer):
    today_stats = serializers.DictField()
    yearly_total = serializers.IntegerField()
    type_distribution = serializers.ListField()
    gender_distribution = serializers.ListField()
    age_distribution = serializers.ListField()
    time_slot_distribution = serializers.ListField()
    average_rating = serializers.FloatField()


class BulkScheduleSerializer(serializers.Serializer):
    dates = serializers.ListField(child=serializers.DateField())
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def create(self, validated_data):
        counselor = validated_data['counselor']
        dates = validated_data['dates']
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']

        schedules = []
        for date in dates:
            schedule = Schedule.objects.create(
                counselor=counselor,
                date=date,
                start_time=start_time,
                end_time=end_time
            )
            schedules.append(schedule)

        return schedules


class ServiceTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counselor
        fields = ['service_types']