from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
from teacher.admin import user_admin_site


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^courses/', include('courses.urls', namespace="courses")),
    url(r'^teacher/', include('teacher.urls', namespace="teacher")),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^(?P<poll_id>\d+)/ajaxvote/$', 'polls.views.ajax_vote'),
	url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^', include(user_admin_site.urls)),
)

urlpatterns += patterns('',
(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
)

urlpatterns += patterns('',
(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
)
