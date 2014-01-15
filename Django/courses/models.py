import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    course_text = models.CharField(max_length=50, default='')
    teachers = models.ForeignKey(User, related_name='courses')
    #teachers = models.IntegerField(max_length=10)
    #teachers = models.ManyToManyField(User)
    
    def __str__(self):
        return self.course_text


class Lecture(models.Model):
    lecture_text = models.CharField(max_length=50, default='')
    teacher = models.ForeignKey(User, related_name='lectures')
    course = models.ForeignKey(Course, related_name='lectures')
    

    def __str__(self):
        return self.lecture_text


class Question(models.Model):

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    lecture = models.ForeignKey(Lecture, related_name='questions')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class Answer(models.Model):
    answer_text = models.CharField(max_length=200, default='')
    question = models.ForeignKey(Question, related_name='answers')

    def __str__(self):
        return self.answer_text
