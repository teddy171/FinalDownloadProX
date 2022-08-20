from django.contrib import admin

from .models import Task, Process, SearchResult

admin.site.register(Task)
admin.site.register(Process)
admin.site.register(SearchResult)
