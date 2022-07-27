from __future__ import unicode_literals
from celery import shared_task
import youtube_dl

@shared_task
def download_video(content, location):
    ydl_opts = {
        "writeinfojson": True, 
        "outtmpl": f"{location}/%(id)s/%(title)s.%(ext)s", 
        "external_downloader": "aria2c",
        "external_downloader_args": ["-x 16", "-k 1M", "--enable-rpc"]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([content])
