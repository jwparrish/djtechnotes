from django.http import HttpResponse, Http404
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.shortcuts import render_to_response

def main_page(request):
	return render_to_response(
		'main_page.html',
		{ 'user': request.user },
	)


def user_page(request, username):
	try:
		user = User.objects.get(username=username)
	except:
		raise Http404('Requested user not found.')
	notes = user.note_set.all()
	template = get_template('user_page.html')
	variables = Context({
		'username': username,
		'notes': notes,
	})
	output = template.render(variables)
	return HttpResponse(output)


def note_page(request, username):
	user = User.objects.get(username=username)
	notes = user.note_set.all()
	template = get_template('note.html')
	variables = Context({
		'username': username,
		'notes': notes,
	})
	output = template.render(variables)
	return HttpResponse(output)
	