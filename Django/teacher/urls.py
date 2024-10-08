from django.conf.urls import patterns, url

from teacher import views

urlpatterns = patterns('',
    url(r'^$',
        views.course_index, name='course_index'),
    url(r'^(?P<course_id>\d+)/$',
        views.lecture_index, name='lecture_index'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/$',
        views.question_index, name='question_index'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/(?P<question_id>\d+)/$',
        views.answer_index, name='answer_index'),
    url(r'^course/$',
        views.course, name='course'),
    url(r'^(?P<course_id>\d+)/lecture/$',
        views.lecture, name='lecture'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/question/$',
        views.question, name='question'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/(?P<question_id>\d+)/answer/$',
        views.answer, name='answer'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/closeVoting$',
        views.closeVoting, name='closeVoting'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/openVoting$',
        views.openVoting, name='openVoting'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/startSession$',
        views.startSession, name='startSession'),
    url(r'^(?P<course_id>\d+)/saveChangesLecture$',
        views.saveChangesLecture, name='saveChangesLecture'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/saveChangesQuestion$',
        views.saveChangesQuestion, name='saveChangesQuestion'),
    url(r'^(?P<course_id>\d+)/editToggleLecture$',
        views.editToggleLecture, name='editToggleLecture'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/editToggleQuestion$',
        views.editToggleQuestion, name='editToggleQuestion'),
    url(r'^my_profile/$',
        views.profile_page, name='profile_page'),
    url(r'^analytics/$',
        views.analytics, name='analytics'),

)

