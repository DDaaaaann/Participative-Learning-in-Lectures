from django.contrib import admin
from collections import Counter
from django.contrib.auth.models import User
from models import Question, Course, Lecture, Answer
import math
from teacher.admin import user_admin_site

def openVoting(modeladmin, request, queryset):
    queryset.update(answerable=True)
openVoting.short_description = "Mark selected polls as open for voting"

def closeVoting(modeladmin, request, queryset):
    queryset.update(answerable=False)
closeVoting.short_description = "Mark selected polls as closed for voting"

def filterAnswers(modeladmin, request, queryset):
    """
    Filter the answers with less votes than the median number, by changing
    the boolean 'openForVoting' to false. The minimum of answers is five, this
    is to make sure that there'll never be less than two answers (that way
    voting becomes pointless).
    """
    # Get all the answers out of the database, with their 'openForVoting'-
    # boolean as True. Immediately order the entries by the amount of votes,
    # this makes it easier to calculate the median in the next step.
    list_of_answers = Answer.objects.filter(question_id=queryset, openForVoting=True).order_by('-votes')
    print list_of_answers, len(list_of_answers)
    # Determine median. If the number of answers is even, the median is the
    # value of the entry just under the halfway point. For example, with twenty
    # answers the median should use the value of entry number ten.
    element = int(math.ceil(0.5 * len(list_of_answers)))
    print "Element of median:", element, list_of_answers[element - 1]
    # A small check to make sure the minimum number of answers, open for voting,
    # is five.
    if element < 5:
        element = 5
    median = list_of_answers[element - 1].votes
    # For every answer, a check should be done to identify the ones with less
    # votes than the calculated median.
    for answer in list_of_answers:
        if answer.votes < median:
            # If the number of votes is indeed less than the calculated median,
            # set the 'openForVoting'-boolean to False.
            answer.openForVoting = False
            answer.save()
            print answer, answer.openForVoting
filterAnswers.short_description = "Filter the most unlikely answers from the selected polls"

def resetAnswers(modeladmin, request, queryset):
    """
    Reset all the 'openForVoting'-booleans to True.
    """
    # Get all the answers out of the database.
    list_of_answers = Answer.objects.filter(question_id=queryset)
    # For every answer set the 'openForVoting'-boolean to True.
    for answer in list_of_answers:
        answer.openForVoting = True
        answer.save()
resetAnswers.short_description = "Reset all the 'openForVoting'-booleans"

class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "teachers":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super(CourseAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    fieldsets = [
            ('Course name', {'fields': ['course_text']}),
            ('Teachers', {'fields': ['teachers']}),
            ('Catalogue number', {'fields': ['cat_number']}),
    ]
    
    filter_horizontal = ('teachers',)
    list_display = ('course_text','cat_number')
    inlines = [LectureInline]
    search_fields = ['course_text','cat_number']

    
class LectureAdmin(admin.ModelAdmin):
    fieldsets = [
            ('Lecture name', {'fields': ['lecture_text']}),
            ('Course', {'fields': ['course']}),
    ]
    list_display = ('lecture_text',)
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
            (None,               {'fields': ['question_text']}),
            ('Lecture', {'fields': ['lecture']}),
            ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [AnswerInline]
    list_display = ('question_text', 'pub_date',
                    'has_been_published', 'receiving_answers')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    actions = [openVoting, closeVoting, filterAnswers, resetAnswers]


class AnswerAdmin(admin.ModelAdmin):
    fieldsets = [
            ('Answer text', {'fields': ['answer_text']}),
            ('Question', {'fields': ['question']})
            
    ]
    list_display = ('answer_text',)




admin.site.register(Question, QuestionAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(Answer, AnswerAdmin)
user_admin_site.register(Course, CourseAdmin)