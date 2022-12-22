from __future__ import unicode_literals
from celery import shared_task
import youtube_dl

@shared_task(autoretry_for=(Exception, ))
def download_video(content, location):
    ydl_opts = {
        "outtmpl": f"{location}/%(id)s/%(title)s.%(ext)s", 
        # "external_downloader": "aria2c",
        # "external_downloader_args": ["-x 16", "-k 1M", "-c", "-n"]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([content])
