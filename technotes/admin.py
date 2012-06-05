from django.contrib import admin
from djtechnotes.technotes.models import *

class NoteAdmin(admin.ModelAdmin):
	list_display = ('title', 'note', 'user',)
	list_filter = ('user',)
	ordering = ('title',)
	search_fields = ('title','user',)
	
admin.site.register(Note, NoteAdmin)

class CommentAdmin(admin.ModelAdmin):
	list_display = ('content', 'note', 'user', 'date')
	list_per_page = 20
	list_filter = ('note', 'user', 'date')
	ordering = ['date']
	search_fields = ['user', 'content']
	
admin.site.register(Comment, CommentAdmin)