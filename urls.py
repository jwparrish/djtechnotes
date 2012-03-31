import os.path

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import logout
from django.views.generic.simple import direct_to_template

from technotes.views import *

site_media = os.path.join(os.path.dirname(__file__), 'site_media')

admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', main_page),
	(r'^user/(\w+)/$', user_page),
	(r'^user/(\w+)/note/(\d+)$', display_note),
	(r'^login/$', 'django.contrib.auth.views.login'),
	(r'^logout/$', logout_page),
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': site_media }),
	(r'^register/$', register_page),
	(r'^register/success/$', direct_to_template, {'template': 'registration/register_success.html' }),
	(r'^logout/success/$', direct_to_template, {'template': 'logout.html'}),
	(r'^changepw/$', 'django.contrib.auth.views.password_change'),
	(r'^changepwdone/$', 'django.contrib.auth.views.password_change_done'),
	(r'^save/$', note_save_page),
	(r'^tag/(.+)/$', tag_page),
	(r'^tag/$', tag_cloud_page),
	url(r'^search/$', search_page, name="search"),
	(r'^ajax/tag/autocomplete/$', ajax_tag_autocomplete),
	#(r'^admin/', include('django.contrib.admin.urls')),
	url(r'^admin/', include(admin.site.urls)),
	# FAKE REDIRECT FOR NOT AUTHENTICATED USERS
#	(r'^(?P<path>.+)$', fake_redirect),
)
