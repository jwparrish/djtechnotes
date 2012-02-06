from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
	note = models.TextField()
	title = models.CharField(max_length=200)
	user = models.ForeignKey(User)
	
	def __unicode__(self):
		return self.title
	

"""
class Bookmark(models.Model):
	title = models.CharField(max_length=200)
	user = models.ForeignKey(User)
	note = models.ForeignKey(Note)
"""