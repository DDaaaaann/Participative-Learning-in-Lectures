import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    course_text = models.CharField(max_length=50, default='')
    #teachers = models.ForeignKey(User, related_name='courses')

    teachers = models.ManyToManyField(User)
    
    def __str__(self):
        return self.course_text

class Lecture(models.Model):
    lecture_text = models.CharField(max_length=50, default='')
    teacher = models.ForeignKey(User, related_name='lectures')
    course = models.ForeignKey(Course, related_name='lectures')
    # Editable is the boolean that says if the edit row, with setAnswerTime and
    # setVoteTime, is visible.
    editable = models.BooleanField(default=False)

    def __str__(self):
        return self.lecture_text

class Question(models.Model):
    def __str__(self):
        return self.question_text

    """
    The function that shows if the Question is open for voting, and thus visible for the students.
    """
    def receiving_answers(self):
        return self.answerable

    receiving_answers.admin_order_field = 'answerable'
    receiving_answers.boolean = True
    receiving_answers.short_description = 'Voting in progress'

    """
    The functions that shows if the Question has been published already, and thus visible for the students.
    """
    def has_been_published(self):
        return self.pub_date < timezone.now()
    
    has_been_published.admin_order_field = 'pub_date'
    has_been_published.boolean = True
    has_been_published.short_description = 'Published'

    """
    All the variables and their explanations related to the class and database of Question.
    """
    
    # Lecture is the Foreign Key of the lecture of which the question is part.
    lecture = models.ForeignKey(Lecture, related_name='questions')
    # Question_text is the string that holds the question.
    question_text = models.CharField(max_length=200, default='')
    # Pub_Date is the date the poll was created.
    pub_date = models.DateTimeField('date published', default=timezone.now())
    # Answerable is the boolean to decide if the poll / question is still
    # vulnerable for new votes.
    answerable = models.BooleanField('Open for voting',default=True)
    # English is the boolean to set the language, True for English, False for
    # Dutch.
    english = models.BooleanField('Language', default=True)
    # Tags are the keywords the teacher wants to see in the student's answers.
    tags = models.CharField(max_length=200, default='')
    # Voting is an unknown boolean.
    voting = models.BooleanField(default=False)
    # Vote_duration is the time the students have to vote for an answer.
    vote_duration = models.IntegerField(default=30)
    # Answer_time is the time the students have to answer the question.
    answer_time = models.IntegerField('Close voting', default=90)
    # Editable is the boolean that says if the edit row, with setAnswerTime and
    # setVoteTime, is visible.
    editable = models.BooleanField(default=False)

class Answer(models.Model):
    class Meta:
        """
        Orders all the answer alphabetically.
        """
        ordering = ['answer_text']

    def __str__(self):
        return self.answer_text

    """
    All the variables and their explanations related to the class and database of Answer.
    """
    # Question is the class that holds the question, answers and votes.
    question = models.ForeignKey(Question, related_name='answers')
    # Answer_text is the string that holds the possible choice.
    answer_text = models.CharField(max_length=200, default='')
    # Votes is the number of votes for the specific choice.
    votes = models.IntegerField(default=0)
    # OpenForVoting determines the fact if the answer can be voted on.
    openForVoting = models.BooleanField(default=True)
