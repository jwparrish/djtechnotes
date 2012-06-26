import os.path

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import logout
#from django.contrib.auth.views import login as auth_login
from django.views.generic.simple import direct_to_template
from django.conf import settings

from technotes.views import *

site_media = os.path.join(os.path.dirname(__file__), 'site_media')
upload = os.path.join(os.path.dirname(__file__), 'upload')
static_compiled = os.path.join(os.path.dirname(__file__), 'static_compiled')

admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', main_page),
	url(r'^user/(?P<username>\w+)/$', user_page, name="user_page"),
	url(r'^user/(?P<username>\w+)/note/(?P<noteid>\d+)$', display_note, name="display_note"),
	url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
	#(r'^login/$', auth_login),
	url(r'^logout/$', logout_page, name="logout"),
	url(r'^register/$', register_page, name="register"),
	(r'^register/success/$', direct_to_template, {'template': 'registration/register_success.html' }),
	(r'^logout/success/$', direct_to_template, {'template': 'logout.html'}),
	(r'^changepw/$', 'django.contrib.auth.views.password_change'),
	(r'^changepwdone/$', 'django.contrib.auth.views.password_change_done'),
	url(r'^save/$', note_save_page, name="note_save"),
	url(r'^tag/(?P<tag_name>.+)/$', tag_page, name="tag_page"),
	url(r'^tag/$', tag_cloud_page, name="tag_cloud"),
	url(r'^search/$', search_page, name="search"),
	(r'^ajax/tag/autocomplete/$', ajax_tag_autocomplete),
	url(r'^admin/', include(admin.site.urls)),
	(r'^import/$', importText),
	(r'^vote/$', note_vote_page),
	(r'^comment/note/add/$', add_comment),
	(r'^ckeditor/', include('ckeditor.urls')),
	# FAKE REDIRECT FOR NOT AUTHENTICATED USERS
	#(r'^(?P<path>.+)$', fake_redirect),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': site_media }),
		(r'^upload/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': upload }),
		(r'^static_compiled/(?P<path>.*)$', 'django.views.static.serve', {'document_root': static_compiled }),
	)