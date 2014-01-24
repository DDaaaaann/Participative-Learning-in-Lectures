from django.conf.urls import patterns, url

from courses import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name='index'),
# Waar is 'course_results' voor nodig? [Patrick]
    url(r'^(?P<course_id>\d+)/results/$',
        views.course_results, name='course_results'),
    url(r'^$',
        views.course_index, name='course_index'),
    url(r'^(?P<course_id>\d+)/$',
        views.lecture_index, name='lecture_index'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/$',
        views.question_index, name='question_index'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/(?P<question_id>\d+)/$',
        views.answer_index, name='answer_index'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/(?P<question_id>\d+)/vote/$',
        views.vote, name='vote'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/(?P<question_id>\d+)/results/$',
        views.results, name='results'),
    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/(?P<question_id>\d+)/answer/$',
        views.answer, name='answer'),
    url(r'^enroll/$', views.course_enroll, name='course_enroll'),

)
