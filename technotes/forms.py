import re

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from technotes.models import Comment
from ckeditor.widgets import CKEditorWidget


class RegistrationForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	email = forms.EmailField(label='Email')
	password1 = forms.CharField(
		label='Password',
		widget=forms.PasswordInput(),
	)
	password2 = forms.CharField(
		label='Password (Again)',
		widget=forms.PasswordInput(),
	)
	
	def clean_password2(self):
		if 'password1' in self.cleaned_data:
			password1 = self.cleaned_data['password1']
			password2 = self.cleaned_data['password2']
			if password1 == password2:
				return password2
		raise forms.ValidationError('Passwords do not match.')
	
	def clean_username(self):
		username = self.cleaned_data['username']
		if not re.search(r'^\w+$', username):
			raise forms.ValidationError('Username can only contain alphanumeric characters and the underscore.')
		try:
			User.objects.get(username=username)
		except ObjectDoesNotExist:
			return username
		raise forms.ValidationError('Username is already taken!')
		
	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			User.objects.get(email__exact=email)
		except ObjectDoesNotExist:
			return email
		raise forms.ValidationError('Email address is already registered!')
		
class NoteSaveForm(forms.Form):
	title = forms.CharField(
		label = 'Title',
		widget = forms.TextInput(attrs={'size': 64, 'class': 'field span8'})
	)
	note = forms.CharField(
		label = 'Note',
		widget = CKEditorWidget(),
		#widget = forms.widgets.Textarea(attrs={'class': 'noteinput field span8'})
	)
	tags = forms.CharField(
		label = 'Tags',
		required = False,
		widget = forms.TextInput(attrs={'size':64, 'class': 'field span8'}),
		help_text = 'separated by spaces. e.g. "Cheddar Swiss Nacho".'
	)
	
class SearchForm(forms.Form):
	query = forms.CharField(
		label = 'Enter a keyword to search for',
		widget = forms.TextInput(attrs={'size': 32})
	)
		
class NoteEditForm(forms.Form):
	title = forms.CharField(
		label = 'Title',
		widget = forms.TextInput(attrs={'size': 64, 'class': 'field span8'})
	)
	note = forms.CharField(
		label = 'Note',
		required = False,
		widget = CKEditorWidget(),
		#widget = forms.widgets.Textarea(attrs={'class': 'noteinput field span8'})
	)
	tags = forms.CharField(
		label = 'Tags',
		required = False,
		widget = forms.TextInput(attrs={'size':64, 'class': 'field span8'}),
		help_text = 'separated by spaces. e.g. "Cheddar Swiss Nacho".'
	)
	noteid = forms.CharField(
		label='NoteID',
		widget=forms.HiddenInput()
	)
	
class ImportFileForm(forms.Form):
	importFile = forms.FileField()
		
class UploadPDFForm(forms.Form):
	title = forms.CharField(
		label = 'Title',
		widget = forms.TextInput(attrs={'size': 64, 'class': 'field span8'})
	)
	tags = forms.CharField(
		label = 'Tags',
		required = False,
		widget = forms.TextInput(attrs={'size':64, 'class': 'field span8'}),
		help_text = 'separated by spaces. e.g. "Cheddar Swiss Nacho".'
	)
	upPDF = forms.FileField(label = 'Upload')
	
class UploadEditForm(forms.Form):
	title = forms.CharField(
		label = 'Title',
		widget = forms.TextInput(attrs={'size': 64, 'class': 'field span8'})
	)
	file = forms.CharField(
		label = 'File',
		required = False,
		widget = forms.TextInput(attrs={'size': 64, 'readonly': True})
	)
	tags = forms.CharField(
		label = 'Tags',
		required = False,
		widget = forms.TextInput(attrs={'size':64, 'class': 'field span8'}),
		help_text = 'separated by spaces. e.g. "Cheddar Swiss Nacho".'
	)
	noteid = forms.CharField(
		label='NoteID',
		widget=forms.HiddenInput()
	)
	
class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		exclude = ('user', 'note')
		widgets = {
			'content': forms.Textarea(attrs={'rows': 4, 'class': 'field span8'})
		}
		