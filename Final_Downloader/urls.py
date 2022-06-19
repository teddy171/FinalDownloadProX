from django.urls import path

from . import views

app_name = 'YoutubeDownloader'



urlpatterns = [
    path(r'', views.new_task, name='new_task'),
    path(r'download_task/', views.download_task, name='download_task'),
    path(r'download_status/', views.download_status, name='download_status'),
    path(r'search/<str:key_word>', views.search_video, name='search_video'),
    path(r'search/video/<str:video_id>', views.display_video_info, name='display_video_info'),
    path(r'transmit/<str:video_id>', views.transmit_file, name='transmit_task')
]
