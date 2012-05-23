from django.db import models
from django.contrib.auth.models import User
import os.path

class Note(models.Model):
	note = models.TextField(blank=True)
	title = models.CharField(max_length=200)
	file = models.FileField(upload_to='pdf', blank=True)
	user = models.ForeignKey(User)
	uploaded = models.BooleanField()
	
	def __unicode__(self):
		return self.title
		
	def __str__(self):
		return '%s, %s' % (self.user.username, self.title)
		
	def filename(self):
		return os.path.basename(self.file.name)
	
class Tag(models.Model):
	name = models.CharField(max_length=64, unique=True)
	notes = models.ManyToManyField(Note)
	
	def __str__(self):
		return self.name
		
class Vote(models.Model):
	note = models.ForeignKey(Note, unique=True)
	date = models.DateTimeField(auto_now_add=True)
	votes = models.IntegerField(default=0)
	users_voted = models.ManyToManyField(User)
	
	def __str__(self):
		return '%s, %s' % self.note, self.votes
		
class Comment(models.Model):
	note = models.ForeignKey(Note)
	user = models.ForeignKey(User)
	title = models.CharField(max_length=50)
	date = models.DateTimeField(auto_now_add=True)
	content = models.TextField()