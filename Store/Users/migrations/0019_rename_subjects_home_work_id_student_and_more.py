# Generated by Django 4.2.1 on 2025-03-01 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0018_schedule_student'),
    ]

    operations = [
        migrations.RenameField(
            model_name='home_work',
            old_name='subjects',
            new_name='id_student',
        ),
        migrations.AlterField(
            model_name='home_work',
            name='file_home_work',
            field=models.FileField(upload_to='home_work'),
        ),
    ]
