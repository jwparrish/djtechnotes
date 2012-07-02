from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import Context, RequestContext
from django.template.loader import get_template, render_to_string
from django.utils import simplejson
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings

from technotes.forms import *
from technotes.models import *

import requests


ITEMS_PER_PAGE = 10

def main_page(request):
	return render(request, 'main_page.html')
	

@login_required
def user_page(request, username):
	user = get_object_or_404(User, username=username)
	query_set = user.note_set.order_by('-id')
	paginator = Paginator(query_set, ITEMS_PER_PAGE)
	try:
		page = int(request.GET['page'])
	except:
		page = 1
	try:
		notes = paginator.page(page)
	except:
		raise Http404
	return render(request, 'user_page.html', {'username': username,
		'notes': notes.object_list, 'show_tags': True, 'show_user': False, 
		'show_edit': username == request.user.username, 
		'show_paginator': paginator.num_pages > 1, 
		'has_prev': paginator.page(page).has_previous(), 
		'has_next': paginator.page(page).has_next(),
		'page': page,
		'pages': paginator.num_pages,
		'next_page': page + 1,
		'prev_page': page - 1
		})
		
		
def logout_page(request):
	logout(request)
	return HttpResponseRedirect('/logout/success/')

@login_required	
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
	return render(request, 'registration/register.html', {'form': form })
	
@login_required
def note_save_page(request):
	if request.method == 'POST':
		if request.POST.has_key('noteid'):
			if 'delete' in request.POST:
				note = Note.objects.get(id=request.POST['noteid'])
				note.delete()
				return HttpResponseRedirect('/user/%s/' % request.user.username)
			else:
				form = NoteEditForm(request.POST)
				if form.is_valid():
					note = _note_save(request, form)
		elif 'import' in request.POST:
			try:
				context = importText(request)
				return render(request, 'note_save.html', context)
			except:
				form = NoteSaveForm()
				importForm = ImportFileForm()
				uploadPDF = UploadPDFForm()
				required = 'File required for import.'
				return render(request, 'note_save.html', {'form': form, 'importForm': importForm, 'required': required, 'uploadPDF': uploadPDF })
		elif 'uploadPDF' in request.POST:
			form = UploadPDFForm(request.POST, request.FILES)
			if form.is_valid():
				note = Note.objects.create(
					user = request.user,
					title = form.cleaned_data['title'],
					file = request.FILES['upPDF'],
					uploaded = True,
				)
				#Create new tag list.
				tag_names = form.cleaned_data['tags'].split()
				for tag_name in tag_names:
					tag, created = Tag.objects.get_or_create(name=tag_name)
					note.tag_set.add(tag)
				#Create corresponding Vote object
				vote, created = Vote.objects.get_or_create(note=note)
				if created:
					vote.users_voted.add(request.user)
					vote.save()
				note.save()
				return HttpResponseRedirect('/user/%s/' % request.user.username)
			else:
				return HttpResponseRedirect('/save/#2/')
		else:	
			form = NoteSaveForm(request.POST)
			if form.is_valid():
				note = _note_save(request, form)
			else:
				return render(request, 'note_save.html', {'form': form})

		return HttpResponseRedirect(
			'/user/%s/' % request.user.username
		)
	elif request.GET.has_key('id'):
		id = request.GET['id']
		tags = ''
		note = ''
		try:
			originalNote = Note.objects.get(id=id)
			note = originalNote.note
			noteid = originalNote.id
			tags = ' '.join(
				tag.name for tag in originalNote.tag_set.all()
			)
			file = originalNote.filename()
			uploaded = originalNote.uploaded
			title = originalNote.title
			
		except ObjectDoesNotExist:
			pass
		if uploaded:
			form = UploadEditForm({
				'title': title,
				'tags': tags,
				'file': file,
				'noteid': noteid,
			})
		else:
			form = NoteEditForm({
				'note': note,
				'title': title,
				'tags': tags,
				'noteid': noteid,
			})
		return render(request, 'note_save.html', {'form': form, 'delete': True, 'disable_upload': True, 'edit': True})
	else:
		form = NoteSaveForm()
		importForm = ImportFileForm()
		uploadPDF = UploadPDFForm()
	return render(request, 'note_save.html', {'form': form, 'importForm': importForm, 'uploadPDF': uploadPDF })
	
@login_required
def display_note(request, username, noteid):
	note = Note.objects.get(id=noteid)
	comments = Comment.objects.filter(note__id=noteid).order_by('date')
	comment_form = CommentForm()
	#if note.file:
	#	return render(request, 'show_pdf.html', {'username': username, 'note': note, 'comments': comments, 'comment_form': comment_form })
	if note.file:
		response = render_to_zoho(note)
		if response == 'error':
			return render(request, 'note_external.html', {'username': username, 'note': note })
		else:
			templink = response
			return render(request, 'note_external.html', {'username': username, 'note': note, 'templink': templink, 'comments': comments, 'comment_form': comment_form})

	else:
		return render(request, 'note.html', {'username': username, 'note': note, 'comments': comments, 'comment_form': comment_form })

@login_required
def tag_page(request, tag_name):
	tag = get_object_or_404(Tag, name=tag_name)
	notes = tag.notes.order_by('-id')
	return render(request, 'tag_page.html', {'notes': notes, 
		'tag_name': tag_name, 'show_tags': True, 'show_user': True })
	
@login_required
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
	return render(request, 'tag_cloud_page.html', {'tags': tags })

@login_required
def search_page(request):
	form = SearchForm()
	show_results = False
	if request.GET.has_key('query'):
		show_results = True
		searchterms = request.GET['query']
		query = request.GET['query'].strip()
		if query:
			notes = []
			keywords = query.split()
			q = Q()
			for keyword in keywords:
				q = q | Q(title__icontains=keyword)
			form = SearchForm({'query': query})
			query_set = Note.objects.filter(q)[:200]
			paginator = Paginator(query_set, ITEMS_PER_PAGE)
			try:
				page = int(request.GET['page'])
			except:
				page = 1
			try:
				notes = paginator.page(page)
			except:
				raise Http404
			
			
			variables = {
				'searchterms': searchterms,
				'query': query,
				'form': form, 
				'notes': notes.object_list,
				'show_results': show_results,
				'show_tags': True,
				'show_user': True,
				'show_paginator': paginator.num_pages > 1,
				'has_prev': paginator.page(page).has_previous(),
				'has_next': paginator.page(page).has_next(),
				'page': page,
				'pages': paginator.num_pages,
				'next_page': page + 1,
				'prev_page': page - 1
			}
		else:
			variables = {
				'form': form,
				'searchterms': searchterms,
				'show_results': show_results,
			}
	
		if request.GET.has_key('ajax'):
			return render(request, 'note_list.html', variables)
		else:
			return render(request, 'search.html', variables)

@login_required
def _note_save(request, form):
	try:
		#Try to get note
		note = Note.objects.get(
			user = request.user,
			id = form.cleaned_data['noteid'],
		)
		#If the note is being updated, clear old tag list.
		note.tag_set.clear()
		note.note = form.cleaned_data['note']
		note.title = form.cleaned_data['title']			
	except KeyError:
		note = Note()
		note.user = request.user
		note.note = form.cleaned_data['note']
		note.title = form.cleaned_data['title']
		note.save()

	#Create new tag list.
	tag_names = form.cleaned_data['tags'].split()
	for tag_name in tag_names:
		tag, created = Tag.objects.get_or_create(name=tag_name)
		note.tag_set.add(tag)
	#Create corresponding Vote object
	vote, created = Vote.objects.get_or_create(note=note)
	if created:
		vote.users_voted.add(request.user)
		vote.save()
	#Save Note to DB
	note.save()
	return note
	
@login_required
def ajax_tag_autocomplete(request):
	if request.GET.has_key('q'):
		tags = Tag.objects.filter(name__istartswith=request.GET['q'])[:10]
		return HttpResponse('\n'.join(tag.name for tag in tags))
	return HttpResponse()
	
@login_required
def importText(request):
	importedFile = request.FILES['importFile']
		
	if importedFile.multiple_chunks():
		context['uploadError'] = 'Uploaded file is too big (%.2f MB).' % (importedFile.size,)
	else:
		importedContent = importedFile.read()
		form = NoteSaveForm(initial={'note': importedContent})
		uploadPDF = UploadPDFForm()
		importForm = ImportFileForm()
		context = {
			'form': form,
			'uploadPDF': uploadPDF,
			'importForm': importForm,
		}
	return context
	
@login_required
def note_vote_page(request):
	if request.GET.has_key('id'):
		try:
			id = request.GET['id']
			vote = Vote.objects.get(id=id)
			user_voted = vote.users_voted.filter(username=request.user.username)
			
			if not user_voted:
				vote.votes += 1
				vote.users_voted.add(request.user)
				vote.save()
		except ObjectDoesNotExist:
			raise Http404('Note not found.')
	if request.META.has_key('HTTP_REFERER'):
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	return HttpResponseRedirect('/')
	
@login_required
def add_comment(request):
	form = CommentForm(request.POST)
	if form.is_valid():
		comment = form.save(commit=False)
		noteid = request.POST.get('noteid')
		note = Note.objects.get(id=noteid)
		comment.user = request.user
		comment.note = note
		comment.save()
		
		template = "note_comment.html"
		html = render_to_string(template, {'comment': comment })
		response = simplejson.dumps({'success':'True', 'html': html})
	else:
		html = form.errors.as_ul()
		response = simplejson.dumps({'success': 'False', 'html': html})
	return HttpResponse(response, content_type='application/javascript; charset=utf-8')

def render_to_zoho(note):
	apikey = settings.ZOHOAPIKEY
	keys = {'apikey': apikey, 'displayfilename': 'false'}
	url = 'https://viewer.zoho.com/api/view.do'
	path = str(note.file.file)
	files = {'file': (note.filename(), open(path, 'rb'))}
	r = requests.post(url, files=files, data=keys)
	if r.status_code == 200:
		response = str(r.json['response']['url'])
	else:
		response = 'error'
	return response	
	
def redirect_500_error(request):
	return render_to_response('500.html', {}, RequestContext(request))

""" FAKE REDIRECT
def fake_redirect(request, path):
	if request.user.is_authenticated:
		raise Http404()
	else:
		return HttpResponseRedirect('/login/?next=/%s' % path)
"""
	
