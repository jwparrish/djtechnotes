from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import logout
from technotes.views import *
import os.path

site_media = os.path.join(os.path.dirname(__file__), 'site_media')

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', main_page),
	(r'^user/(\w+)/$', user_page),
	(r'^user/(\w+)/note.html', note_page),
	(r'^login/$', 'django.contrib.auth.views.login'),
	(r'^logout/$', logout_page),
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': site_media }),
	(r'^register/$', register_page),
	(r'^register/success/$', direct_to_template, {'template': 'registration/register_success.html' }),
	(r'^logout/success/$', direct_to_template, {'template': 'logout.html'}),
	(r'^changepw/$', 'django.contrib.auth.views.password_change'),
	(r'^changepwdone/$', 'django.contrib.auth.views.password_change_done'),
	(r'^save/$', note_save_page),
	
	# FAKE REDIRECT FOR NOT AUTHENTICATED USERS
#	(r'^(?P<path>.+)$', fake_redirect),
)


""" ORIGINAL URL EXAMPLES """

    # Examples:
    # url(r'^$', 'djtechnotes.views.home', name='home'),
    # url(r'^djtechnotes/', include('djtechnotes.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
#)



