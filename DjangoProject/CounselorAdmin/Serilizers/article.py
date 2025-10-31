from rest_framework import serializers
from CounselorAdmin.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    宣教资讯序列化器
    数据库表: articles
    外键: category_id -> categories.id (NOT NULL)
    """
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['id', 'created_time']


