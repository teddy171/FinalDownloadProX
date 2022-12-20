from django.contrib import admin

from .models import Task, Process, SearchResult

class TaskAdmin(admin.ModelAdmin):
    list_display = ('content', 'owner', )

    list_per_page = 20

    list_filter = ('content', 'owner', )

class ProcessAdmin(admin.ModelAdmin):
    list_display = ('video_name', 'video_id', 'task_id', 'video_size')

    list_per_page = 20

    list_filter = ('video_name', 'video_id', 'task_id', 'video_size')

class SearchResultAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'video_id', 'video_url', 'video_author')

    list_per_page = 20

    list_filter = ('video_title', 'video_id', 'video_url', 'video_author')

admin.site.register(Task)
admin.site.register(Process)
admin.site.register(SearchResult)
