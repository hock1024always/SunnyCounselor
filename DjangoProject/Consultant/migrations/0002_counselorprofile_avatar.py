# Generated manually for adding avatar field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Consultant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='counselorprofile',
            name='avatar',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='头像路径'),
        ),
    ]

