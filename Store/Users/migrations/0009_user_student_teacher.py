# Generated by Django 4.2.1 on 2024-10-11 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0008_user_photo_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='student_teacher',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]
