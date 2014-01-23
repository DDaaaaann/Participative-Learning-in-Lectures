from django.conf.urls import patterns, url

from teacher import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name='index'),
# This url shouldn't be necessary.
    url(r'^(?P<course_id>\d+)/results/$', views.course_results, name='course_results'),
# This url shouldn't be necessary.
    url(r'^(?P<question_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^$',
        views.course_index, name='course_index'),
    url(r'^(?P<course_id>\d+)/change/$',
        views.course_change, name='course_change'),
    url(r'^(?P<course_id>\d+)/$',
        views.lecture_index, name='lecture_index'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/$',
        views.question_index, name='question_index'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/(?P<question_id>\d+)/$',
<<<<<<< HEAD
        views.answer_index, name='answer_index'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/closeVoting$',
        views.closeVoting, name='closeVoting'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/openVoting$',
        views.openVoting, name='openVoting'),
    url(r'^(?P<course_id>\d+)/saveChangesLecture$',
        views.saveChangesLecture, name='saveChangesLecture'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/saveChangesQuestion$',
        views.saveChangesQuestion, name='saveChangesQuestion'),
    url(r'^(?P<course_id>\d+)/editToggleLecture$',
        views.editToggleLecture, name='editToggleLecture'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/editToggleQuestion$',
        views.editToggleQuestion, name='editToggleQuestion'),

=======
        views.answer_index, 
        name='answer_index'),
    url(r'^my_profile/$', views.profile_page,
        name='profile_page'),
>>>>>>> git profielpagina in juiste map
)

