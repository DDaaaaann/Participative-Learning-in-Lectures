from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone


from polls.models import Choice, Poll, Sessionlink 

def openVoting(modeladmin, request, queryset):
    queryset.update(answerable=True)
    
openVoting.short_description = "Mark selected polls as open for voting"

def closeVoting(modeladmin, request, queryset):
    queryset.update(answerable=False)
closeVoting.short_description = "Mark selected polls as closed for voting"

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
    actions = [openVoting, closeVoting]

admin.site.register(Poll, PollAdmin)
