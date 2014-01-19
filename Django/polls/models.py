import datetime
from django.utils import timezone
from django.db import models

class Poll(models.Model):
    def __unicode__(self):
        return self.question

    """
    The function that shows if the Poll is open for voting, and thus visible
    for the students.
    """
    def receiving_answers(self):
        return self.answerable

    def get_absolute_url(self):
        return u"/polls/%s/" % self.pk

    receiving_answers.admin_order_field = 'answerable'
    receiving_answers.boolean = True
    receiving_answers.short_description = 'Voting in progress'

    """
    The functions that shows if the Poll has been published already, and thus
    visible for the students.
    """
    def has_been_published(self):
        return self.pub_date < timezone.now()
    
    has_been_published.admin_order_field = 'pub_date'
    has_been_published.boolean = True
    has_been_published.short_description = 'Published'

    """
    All the variables and their explanations related to the class and database
    of Poll.
    """
    
    # Question is the string that holds the question.
    question = models.CharField(max_length=200)
    # Pub_Date is the date the poll was created.
    pub_date = models.DateTimeField('date published')
    # Answerable is the boolean to decide if the poll / question is still
    # vulnerable for new votes.
    answerable = models.BooleanField('Open for voting',default=True)
    # Tags are the keywords the teacher wants to see in the student's answers.
    tags = models.CharField(max_length=200)
    
    closing = models.BooleanField();


class Choice(models.Model):
    class Meta:
        """
        Orders all the choices alphabetically.
        """
        ordering = ['choice_text']

    def __unicode__(self):
        return self.choice_text

    """
    All the variables and their explanations related to the class and database
    of Choice.
    """
    # Poll is the class that holds the question, answers and votes.
    poll = models.ForeignKey(Poll)
    # Choice_Text is the string that holds the possible choice.
    choice_text = models.TextField()
    # Votes is the number of votes for the specific choice.
    votes = models.IntegerField(default=0)
    # OpenForVoting determines the fact if the answer can be voted on.
    openForVoting = models.BooleanField(default=True)
    
class Sessionlink(models.Model):
	def __unicode__(self):
		return self.choice_text
		
	poll_id = models.ForeignKey(Poll)
	session_id = models.IntegerField(default=1)
	open = models.IntegerField(default=0)
	close = models.IntegerField()
