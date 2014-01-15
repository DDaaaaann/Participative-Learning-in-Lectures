from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone


from polls.models import Choice, Poll, Sessionlink 
import math

def openVoting(modeladmin, request, queryset):
    queryset.update(answerable=True)
openVoting.short_description = "Mark selected polls as open for voting"

def closeVoting(modeladmin, request, queryset):
    queryset.update(answerable=False)
closeVoting.short_description = "Mark selected polls as closed for voting"

def filterAnswers1(modeladmin, request, queryset):
    # I'm not sure if this function should be here, or in another file. Second,
    # the boolean-field 'openForVoting' needs to be added to the database.
    """
    Filter the answers with less votes than the median number, by changing
    the boolean 'openForVoting' to false
    """
    # Get all the answers out of the database, with their 'openForVoting'-
    # boolean as True. Immediately ordered by the amount of votes.
    list_of_answers = Choice.objects.filter(poll_id=queryset).order_by('-votes')
    print list_of_answers
    counter = 0
    # For every answer, a check should be done to identify the ones with a
    # position below a certain threshold.
    for answer in list_of_answers:
        if counter > round(0.5 * len(list_of_answers)):
            print answer, answer.openForVoting
            # If the answer is indeed ranked below a certain position, set the
            # 'openForVoting'-boolean to False.
            # It's either this:
            answer.openForVoting = False
            answer.save()
            print answer, answer.openForVoting
filterAnswers1.short_description = "Simply filter the most unlikely answers from the selected polls"

def filterAnswers2(modeladmin, request, queryset):
    # I'm not sure if this function should be here, or in another file. Second,
    # the boolean-field 'openForVoting' needs to be added to the database.
    """
    Filter the answers with less votes than the median number, by changing
    the boolean 'openForVoting' to false
    """
    # Get all the answers out of the database, with their 'openForVoting'-
    # boolean as True. Immediately order the entries by the amount of votes,
    # this makes it easier to calculate the median in the next step.
    list_of_answers = Choice.objects.filter(poll_id=queryset, openForVoting=True).order_by('-votes')
    print list_of_answers
    # Determine median. If the number of answers is even, the median is the
    # value of the entry just above the halfway point. For example, with twenty
    # answers the median should use the value of entry number eleven.
    element = int(math.ceil(0.5 * len(list_of_answers)))
    print "Element of median:", list_of_answers[element]
    median = list_of_answers[element].votes
    # For every answer, a check should be done to identify the ones with less
    # votes than the calculated median.
    for answer in list_of_answers:
        if answer.votes < median:
            # If the number of votes is indeed less than the calculated median,
            # set the 'openForVoting'-boolean to False.
            answer.openForVoting = False
            answer.save()
            print answer, answer.openForVoting
filterAnswers2.short_description = "Filter the most unlikely answers from the selected polls, scientifically"

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question', 'pub_date',
                    'has_been_published', 'receiving_answers')
    list_filter = ['pub_date']
    actions = [openVoting, closeVoting, filterAnswers1, filterAnswers2]

admin.site.register(Poll, PollAdmin)
