from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class evaluations(models.Model):
    subjects = models.CharField(blank=True, max_length=200, null=True)
    evaluations = models.CharField(blank=True, max_length=200, null=True)


class Home_work(models.Model):
    subjects = models.CharField(blank=True, max_length=200, null=True)
    file_home_work = models.CharField(blank=True, max_length=200, null=True)


class Schedule(models.Model):
    schedule = models.CharField(blank=True, max_length=200, null=True)


class User(AbstractUser):
    profile = models.CharField(max_length=200,blank = True,null=True)
    predment = models.CharField(max_length=100,blank = True,null=True)
    name = models.CharField(max_length=200,blank=True)
    fullname = models.CharField(max_length=200, blank=True)
    patronymic = models.CharField(max_length=200, blank=True)
    timecourse = models.CharField(blank=True,max_length=200,null=True)
    schedule = models.ForeignKey(Schedule,on_delete=models.CASCADE,related_name="schedul",blank = True,null=True)
    evaluations = models.ForeignKey(evaluations, on_delete=models.CASCADE, related_name="evaluat",blank = True,null=True)
    home_work = models.ForeignKey(Home_work, on_delete=models.CASCADE, related_name="work_hom",blank = True,null=True)
    photo_teacher = models.CharField(max_length=100,blank=True,null = True)
    student_teacher = models.CharField(max_length=50,blank=True,null=True,default=None)
    regalia_teacher = models.CharField(max_length=300,blank = True,null = True,default=None)





