# Generated by Django 4.2.1 on 2024-10-09 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluations',
            name='evaluations',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='evaluations',
            name='subjects',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='home_work',
            name='file_home_work',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='home_work',
            name='subjects',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='schedule',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]