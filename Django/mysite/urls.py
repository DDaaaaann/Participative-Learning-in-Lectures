from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^courses/', include('courses.urls', namespace="courses")),
    url(r'^teacher/', include('teacher.urls', namespace="teacher")),
    url(r'^admin/', include(admin.site.urls)),
)
