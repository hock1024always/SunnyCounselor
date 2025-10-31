from rest_framework import serializers
from CounselorAdmin.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryListItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source='category_name')
    order = serializers.IntegerField(source='sort_order')
    create_time = serializers.DateTimeField(source='created_time')
    creator = serializers.CharField(source='created_by', allow_blank=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'order', 'create_time', 'creator']


class CategoryCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='category_name')
    order = serializers.IntegerField(source='sort_order', required=False)
    creator = serializers.CharField(source='created_by', required=False, allow_blank=True)

    class Meta:
        model = Category
        fields = ['name', 'order', 'creator']


class CategoryUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='category_name', required=False)
    order = serializers.IntegerField(source='sort_order', required=False)
    creator = serializers.CharField(source='created_by', required=False, allow_blank=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'order', 'creator']


