from django.contrib import admin
from models import Question, Course, Lecture, Answer

class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3


class CourseAdmin(admin.ModelAdmin):
    fieldsets = [
            ('Course text', {'fields': ['course_text']})
    ]
    list_display = ('course_text',)
    inlines = [LectureInline]
    Search_fields = ['course_text']


class LectureAdmin(admin.ModelAdmin):
    fieldsets = [
            ('Lecture text', {'fields': ['lecture_text']}),
            ('Course', {'fields': ['course']})
    ]
    list_display = ('lecture_text',)
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
            (None,               {'fields': ['question_text']}),
            ('Lecture', {'fields': ['lecture']}),
            ('Date information', {'fields': ['pub_date'],
                                  'classes': ['collapse']}),
    ]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    Search_fields = ['question_text']


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
