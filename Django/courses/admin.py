from django.contrib import admin
from collections import Counter
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
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
    extra = 0

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    
    # Only display staff accounts as option to link with a course
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
    list_display = ('course_text','cat_number',)

    inlines = [LectureInline]
    search_fields = ['course_text','cat_number']

class CourseStaffAdmin(admin.ModelAdmin):

    # Only display the courses to which a teacher is added (at "/courses/course/")
    def queryset(self, request):
        qs = super(CourseStaffAdmin, self).queryset(request)
        return qs.filter(id__in=request.user.course_set.all())
                
    
    # Only display staff accounts as option to link with a course
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "teachers":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super(CourseStaffAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def course_link(self, obj):
        return u'<a href="/courses/lecture/?course=%s">%s</a>' % (obj.id, obj)
        
    course_link.allow_tags = True
    course_link.short_description = "Course"
    
    def edit_link(self, obj):
        return u'<a class="changelink" href="/courses/course/%s/">Edit</a>' % (obj.id)
    
    edit_link.allow_tags = True
    edit_link.short_description = "Edit Course"
    
    def __init__(self, *args, **kwargs):
        super(CourseStaffAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )    
        
    fieldsets = [
            ('Course name', {'fields': ['course_text']}),
            ('Teachers', {'fields': ['teachers']}),
            ('Catalogue number', {'fields': ['cat_number']}),
    ]
    
    filter_horizontal = ('teachers',)
    list_display = ('course_link','cat_number','edit_link',)

    inlines = [LectureInline]
    search_fields = ['course_text','cat_number']
    
    
    
class LectureAdmin(admin.ModelAdmin):
    fieldsets = [
            ('Lecture name', {'fields': ['lecture_text']}),
            ('Course', {'fields': ['course']}),
    ]
    list_display = ('lecture_text',)
    inlines = [QuestionInline]
    
    
class CourseFilter(SimpleListFilter):
    title = _('Courses')
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        list_tuple = []
        for course in request.user.course_set.all():
            #print category
            list_tuple.append((course.id, course.course_text))
        return list_tuple
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(course__id=self.value())
        else:
            return queryset
    
    
class LectureStaffAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = super(LectureStaffAdmin, self).queryset(request)
        return qs.filter(course_id__in=request.user.course_set.all())
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "course":
            kwargs["queryset"] = request.user.course_set.all()
        return super(LectureStaffAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def lecture_link(self, obj):
        return u'<a href="/courses/question/?lecture=%s">%s</a>' % (obj.id, obj)
        
    lecture_link.allow_tags = True
    lecture_link.short_description = "Lecture"
    
    def edit_link(self, obj):
        return u'<a class="changelink" href="/courses/lecture/%s/">Edit</a>' % (obj.id)
    
    edit_link.allow_tags = True
    edit_link.short_description = "Edit Lecture"

    def sessionButton(self, obj):
        courseid = obj.course_id
        return u'<form action="/teacher/%s/%s/startSession"> <button type="submit" class="toggleButton" name="question_id"> Start Session </button> </form>' % (courseid, obj.id)

    sessionButton.allow_tags = True
    sessionButton.short_description = "Start Session"
    def __init__(self, *args, **kwargs):
        super(LectureStaffAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, ) 
    
    
    fieldsets = [
            ('Lecture name', {'fields': ['lecture_text']}),
            ('Course', {'fields': ['course']}),
    ]
    
    list_filter = (CourseFilter,)
    list_display = ('lecture_link','course', 'sessionButton', 'edit_link',)
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
            ('Question', {'fields': ['question_text']}),
            ('Lecture', {'fields': ['lecture']}),
            ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [AnswerInline]
    list_display = ('question_text', 'pub_date',
                    'has_been_published', 'receiving_answers')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    actions = [openVoting, closeVoting, filterAnswers, resetAnswers]

    
class LectureFilter(SimpleListFilter):
    title = _('Lecture')
    parameter_name = 'lecture'

    def lookups(self, request, model_admin):
        list_tuple = []
        qs = Lecture.objects.all()
        lectures = qs.filter(course_id__in=request.user.course_set.all())
        for lecture in lectures:
            #print category
            list_tuple.append((lecture.id, lecture.lecture_text))
        return list_tuple
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(lecture__id=self.value())
        else:
            return queryset    
    
class QuestionStaffAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = super(QuestionStaffAdmin, self).queryset(request)
        return qs.filter(lecture_id__course_id__in=request.user.course_set.all())
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "lecture":
            kwargs["queryset"] = Lecture.objects.all().filter(course_id__in=request.user.course_set.all())
        return super(QuestionStaffAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
    def question_link(self, obj):
        return u'<a href="/courses/answer/?question__id__exact=%s">%s</a>' % (obj.id, obj)
        
    question_link.allow_tags = True
    question_link.short_description = "Question"
    
    def edit_link(self, obj):
        return u'<a class="changelink" href="/courses/question/%s/">Edit</a>' % (obj.id)
    
    edit_link.allow_tags = True
    edit_link.short_description = "Edit Question"
    
    def voteButton(self, obj):
        courseid = obj.lecture.course_id
        if obj.voting:
            return u'<form action="/teacher/%s/%s/closeVoting"> <button type="submit" class="toggleButton" name="question_id" value="%s"> Close question </button> </form>' % (courseid, obj.lecture_id, obj.id)
        else:
            return u'<form action="/teacher/%s/%s/openVoting"> <button type="submit" class="toggleButton" name="question_id" value="%s"> Open question </button> </form>' % (courseid, obj.lecture_id, obj.id)
        
    voteButton.allow_tags = True
    voteButton.short_description = "Toggle Question"
    
    def __init__(self, *args, **kwargs):
        super(QuestionStaffAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, ) 
    
    fieldsets = [
            ('Question', {'fields': ['question_text']}),
            ('Lecture', {'fields': ['lecture']}),
            ('Date information', {'fields': ['pub_date', 'vote_duration', 'answer_time']}),
            
    ]
    inlines = [AnswerInline]
    list_display = ('question_link', 'lecture', 'pub_date',
                     'receiving_answers', 'voteButton', 'edit_link',)
    list_filter = [LectureFilter, 'pub_date']
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
user_admin_site.register(Course, CourseStaffAdmin)
user_admin_site.register(Lecture, LectureStaffAdmin)
user_admin_site.register(Question, QuestionStaffAdmin)
user_admin_site.register(Answer, AnswerAdmin)
