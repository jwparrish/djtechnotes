from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout
from technotes.forms import *
from technotes.models import *
from django.contrib.auth.decorators import login_required


def main_page(request):
	return render_to_response(
		'main_page.html', RequestContext(request),
	)


def user_page(request, username):
	user = get_object_or_404(User, username=username)
	notes = user.note_set.order_by('-id')
	#notes = Note.objects.filter(user__username=username)
	variables = RequestContext(request, {
		'username' : username,
		'notes': notes,
		'show_tags': True,
		'show_user': False,
	})
	return render_to_response('user_page.html', variables)

#legacy
def note_page(request, username):
	user = User.objects.get(username=username)
	notes = Note.objects.filter(user__username=user)
	variables = RequestContext(request, {
		'username': username,
		'notes': notes,
	})
	return render_to_response('note.html', variables)
	
	
def logout_page(request):
	logout(request)
	return HttpResponseRedirect('/logout/success/')
	
def register_page(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(
				username = form.cleaned_data['username'],
				password = form.cleaned_data['password1'],
				email = form.cleaned_data['email']
			)
			return HttpResponseRedirect('/register/success/')
	else:
		form = RegistrationForm()
	variables = RequestContext(request, {
		'form': form
	})
	return render_to_response('registration/register.html', variables)
	
@login_required
def note_save_page(request):
	if request.method == 'POST':
		form = NoteSaveForm(request.POST)
		if form.is_valid():
			#Create or get note
			note, created = Note.objects.get_or_create(
				user = request.user,
				note = form.cleaned_data['note'],
				title = form.cleaned_data['title'],
			)
			#If the note is being updated, clear old tag list.
			if not created:
				note.tag_set.clear()
			#Create new tag list.
			tag_names = form.cleaned_data['tags'].split()
			for tag_name in tag_names:
				tag, created = Tag.objects.get_or_create(name=tag_name)
				note.tag_set.add(tag)
			#Save Note to DB
			note.save()
			return HttpResponseRedirect(
				'/user/%s/' % request.user.username
			)
	else:
		form = NoteSaveForm()
	variables = RequestContext(request, {
		'form': form
	})
	return render_to_response('note_save.html', variables)
	
#def fake_redirect(request, path):
#	if request.user.is_authenticated:
#		raise Http404()
#	else:
#		return HttpResponseRedirect('/login/?next=/%s' % path)

def display_note(request, username, noteid):
	note = Note.objects.get(id=noteid)
	variables = RequestContext(request, {
		'username': username,
		'note': note
	})
	return render_to_response('note.html', variables)
	
def tag_page(request, tag_name):
	tag = get_object_or_404(Tag, name=tag_name)
	notes = tag.notes.order_by('-id')
	variables = RequestContext(request, {
		'notes': notes,
		'tag_name': tag_name,
		'show_tags': True,
		'show_user': True,
	})
	return render_to_response('tag_page.html', variables)
	
def tag_cloud_page(request):
	MAX_WEIGHT = 5
	tags = Tag.objects.order_by('name')
	#Calculate tag, min and max counts.
	min_count = max_count = tags[0].notes.count()
	for tag in tags:
		tag.count = tag.notes.count()
		if tag.count < min_count:
				min_count = tag.count
		if max_count < tag.count:
			max_count = tag.count
	#Calculate count range.  Avoid dividing by zero.
	range = float(max_count - min_count)
	if range == 0.0:
		range = 1.0
	#Caculate tag weights.
	for tag in tags:
		tag.weight = int(
			MAX_WEIGHT * (tag.count - min_count) / range
		)
	variables = RequestContext(request, {
		'tags': tags
	})
	return render_to_response('tag_cloud_page.html', variables)
	
def search_page(request):
	form = SearchForm()
	notes = []
	show_results = False
	if request.GET.has_key('query'):
		show_results = True
		query = request.GET['query'].strip()
		if query:
			form = SearchForm({'query': query})
			notes = Note.objects.filter(title__icontains=query)[:10]
	variables = RequestContext(request, {'form': form,
		'notes': notes,
		'show_results': show_results,
		'show_tags': True,
		'show_user': True
	})
	if request.GET.has_key('ajax'):
		return render_to_response('note_list.html', variables)
	else:
		return render_to_response('search.html', variables)