from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
	note = models.TextField()
	title = models.CharField(max_length=200)
	user = models.ForeignKey(User)
	
	def __unicode__(self):
		return self.title
		
	def __str__(self):
		return '%s, %s' % (self.user.username, self.title)
	
class Tag(models.Model):
	name = models.CharField(max_length=64, unique=True)
	notes = models.ManyToManyField(Note)
	
	def __str__(self):
		return self.name


"""
class Bookmark(models.Model):
	title = models.CharField(max_length=200)
	user = models.ForeignKey(User)
	note = models.ForeignKey(Note)
"""