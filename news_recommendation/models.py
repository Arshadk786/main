from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Title(models.Model):
    title = models.CharField(max_length = 500, null = True)
    desc = models.CharField(max_length = 5000)

class Result(models.Model):
    result = models.CharField(max_length = 5000)

class Recommend(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    title = models.ManyToManyField(Title,related_name='titlee')
    result = models.ManyToManyField(Result, null = True)
    

class userDetails(models.Model):
    user=models.ForeignKey(User,on_delete = models.CASCADE)
    topic=models.CharField(max_length=100)
    