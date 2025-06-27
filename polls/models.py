import datetime
from django.contrib import admin
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=300)    
    pub_date = models.DateTimeField("date published")
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Récemment publié ?"
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=300)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text

class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses_from_responses_app')
    response_text = models.CharField(max_length=200)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return self.response_text

class Restaurant(models.Model):
    address = models.CharField(blank=True, null=True)
    name = models.CharField(max_length=255)
    longitude = models.FloatField()
    latitude = models.FloatField()
    type = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(blank=True, default="")
    image_url = models.URLField(blank=True, null=True)  
    
    def __str__(self):
        return self.name