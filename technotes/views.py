from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.contrib.auth import logout


def main_page(request):
	return render_to_response(
		'main_page.html', RequestContext(request),
	)


def user_page(request, username):
	try:
		user = User.objects.get(username=username)
	except:
		raise Http404('Requested user not found.')
	notes = user.note_set.all()
	variables = RequestContext(request, {
		'username' : username,
		'notes': notes,
	})
	return render_to_response('user_page.html', variables)


def note_page(request, username):
	user = User.objects.get(username=username)
	notes = user.note_set.all()
	variables = RequestContext(request, {
		'username': username,
		'notes': notes,
	})
	return render_to_response('note.html', variables)
	
	
def logout_page(request):
	logout(request)
	return HttpResponseRedirect('/')