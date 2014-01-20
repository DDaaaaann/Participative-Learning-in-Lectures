from django.conf.urls import patterns, url

from teacher import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name='index'),
    url(r'^(?P<course_id>\d+)/results/$', views.course_results, name='course_results'),
    url(r'^(?P<question_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^$', views.course_index, name='course_index'),
    url(r'^(?P<course_id>\d+)/change/$', views.course_change, name='course_change'),
    url(r'^(?P<course_id>\d+)/$', views.lecture_index,
        name='lecture_index'),

    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/$', views.question_index, 
        name='question_index'),

    url(r'^(?P<course_id>\d+)/(?P<lecture_id>\d+)/(?P<question_id>\d+)/$',
        views.answer_index, 
        name='answer_index'),
   
)

