from __future__ import unicode_literals
from celery import shared_task
import youtube_dl

@shared_task
def download_video(content, location):
    ydl_opts = {"writeinfojson": True, "outtmpl":f"{location}/%(id)s/%(title)s.%(ext)s"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([content])

        