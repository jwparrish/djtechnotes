from django.contrib import admin
from djtechnotes.technotes.models import *

class NoteAdmin(admin.ModelAdmin):
	list_display = ('title', 'note', 'user',)
	list_filter = ('user',)
	ordering = ('title',)
	search_fields = ('title','user',)
	
admin.site.register(Note, NoteAdmin)