from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import Context, RequestContext
from django.template.loader import get_template

from technotes.forms import *
from technotes.models import *

def main_page(request):
	return render(request, 'main_page.html')

def user_page(request, username):
	user = get_object_or_404(User, username=username)
	notes = user.note_set.order_by('-id')
	#notes = Note.objects.filter(user__username=username)
	return render(request, 'user_page.html', {'username': username,
		'notes': notes, 'show_tags': True, 'show_user': False, 
		'show_edit': username == request.user.username })

#legacy
def note_page(request, username):
	user = User.objects.get(username=username)
	notes = Note.objects.filter(user__username=user)
	return render(request, 'note.html', {
		'username': username, 'notes': notes })
	
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
	return render(request, 'registration/register.html', {'form': form })
	
@login_required
def note_save_page(request):
	if request.method == 'POST':
		if request.POST.has_key('noteid'):
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
				required = 'File required for import.'
				return render(request, 'note_save.html', {'form': form, 'importForm': importForm, 'required': required })
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
	elif request.GET.has_key('title'):
		title = request.GET['title']
		tags = ''
		note = ''
		try:
			originalNote = Note.objects.get(title=title)
			note = originalNote.note
			noteid = originalNote.id
			tags = ' '.join(
				tag.name for tag in originalNote.tag_set.all()
			)
			file = originalNote.filename()
			uploaded = originalNote.uploaded
			
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
		return render(request, 'note_save.html', {'form': form })
	else:
		form = NoteSaveForm()
		importForm = ImportFileForm()
		uploadPDF = UploadPDFForm()
	return render(request, 'note_save.html', {'form': form, 'importForm': importForm, 'uploadPDF': uploadPDF })
	
#def fake_redirect(request, path):
#	if request.user.is_authenticated:
#		raise Http404()
#	else:
#		return HttpResponseRedirect('/login/?next=/%s' % path)

def display_note(request, username, noteid):
	note = Note.objects.get(id=noteid)
	if note.file:
		return render(request, 'show_pdf.html', {'username': username, 'note': note })
	else:
		return render(request, 'note.html', {'username': username, 'note': note })
	
def tag_page(request, tag_name):
	tag = get_object_or_404(Tag, name=tag_name)
	notes = tag.notes.order_by('-id')
	return render(request, 'tag_page.html', {'notes': notes, 
		'tag_name': tag_name, 'show_tags': True, 'show_user': True })
	
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
	
def search_page(request):
	form = SearchForm()
	notes = []
	show_results = False
	if request.GET.has_key('query'):
		show_results = True
		query = request.GET['query'].strip()
		if query:
			#form = SearchForm({'query': query})
			notes = Note.objects.filter(title__icontains=query)[:10]
	
	variables = {
		'query': query,
		'form': form, 
		'notes': notes,
		'show_results': show_results,
		'show_tags': True,
		'show_user': True
	}
	
	if request.GET.has_key('ajax'):
		return render(request, 'note_list.html', variables)
	else:
		return render(request, 'search.html', variables)
		
		
def _note_save(request, form):
	try:
		note = Note.objects.get(id=form.cleaned_data['noteid'])
		note.user = request.user
		note.note = form.cleaned_data['note']
		note.title = form.cleaned_data['title']
	except:
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
	return note
	
def ajax_tag_autocomplete(request):
	if request.GET.has_key('q'):
		tags = Tag.objects.filter(name__istartswith=request.GET['q'])[:10]
		return HttpResponse('\n'.join(tag.name for tag in tags))
	return HttpResponse()
	
def importText(request):
	importedFile = request.FILES['importFile']
		
	if importedFile.multiple_chunks():
		context['uploadError'] = 'Uploaded file is too big (%.2f MB).' % (importedFile.size,)
	else:
		importedContent = importedFile.read()
		form = NoteSaveForm(initial={'note': importedContent})
		context = {
			'form': form,
		}
	return context
	