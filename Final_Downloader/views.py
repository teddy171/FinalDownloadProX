import os
#import aria2p
import shutil
import json
from urllib.parse import urlparse, quote

from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from celery.result import AsyncResult
import youtube_dl

from Final_Downloader.tasks import download_video

from .models import Task, Process, SearchResult
from .forms import TaskForm

def clean_data(user):
    Process.objects.filter(owner=user).delete()

    try:
        shutil.rmtree(f"data/{user}/")
    except:
        pass
    if not os.path.exists("data/"):
        os.makedirs("data/")
    if not os.path.exists(f"data/{user}/"):
        os.mkdir(f"data/{user}/")
    if not os.path.exists(f"data/{user}/search/"):
        os.mkdir(f"data/{user}/search/")
    return f"data/{user}"

def get_pure_filename(user_path, video_id):
    files = os.listdir(f"{user_path}/{video_id}")
    if len(files) != 1:
        raise ValueError(f"More than a file {files}")
    else:
        return files[0]

def download_video_info(content, location):
    ydl_opts = {
        "writeinfojson": True, 
        "outtmpl": f"{location}/info/", 
        "skip_download": True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([content])

def save_form(form, owner):
    if form.is_valid():
        new_task = form.save(commit=False)
        new_task.owner = owner
        new_task.save()

@login_required
def new_task(request):
    """Add a new task."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TaskForm()
    else:
        # POST data submitted; process data.
        form = TaskForm(data=request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            if urlparse(content).scheme == "http" or urlparse(content).scheme == "https":
                same_task = Task.objects.filter(content=content, owner=request.user)
                if same_task:
                    return redirect('Final_Downloader:new_task')
                else:
                    save_form(form, request.user)
                    return redirect('Final_Downloader:download_task')
            else:
                return redirect("Final_Downloader:search_video", key_word=content)
                    

    #Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'Final_Downloader/new_task.html', context)


@login_required
def download_task(request):
    if request.method != 'POST':
        return render(request, 'Final_Downloader/download_video.html')
    else:
        if 'whether_donwload' in request.POST:
            tasks = Task.objects.filter(owner=request.user)
            user_path = clean_data(request.user)
            if len(tasks) == 0:
                return redirect('Final_Downloader:new_task')
            for task in tasks:
                download_video_info(str(task), user_path)
                with open(f"{user_path}/info/.info.json") as f:
                    info = json.load(f)
                    video_id = info["id"]
                    video_name = info["title"]
                    video_size = max([format["filesize"] for format in info["formats"] if format["filesize"]])
                shutil.rmtree(f"{user_path}/info/")
                task = download_video.delay(str(task), user_path)
                Process.objects.create(
                    task_id=task.id,
                    video_id=video_id,
                    video_name=video_name,
                    video_size=video_size,
                    owner=request.user
                )

            tasks.delete()
            return redirect('Final_Downloader:download_status')
        elif 'whether_add' in request.POST:
            return redirect('Final_Downloader:new_task')

@login_required
def download_status(request):
    user_path = f"data/{request.user}"
    # aria2 = aria2p.API(
    #     aria2p.Client(
    #         host="http://localhost",
    #         port=6800,
    #         secret=""
    #     )
    # )

    processes = get_list_or_404(Process, owner=request.user)

    message = {}
    for process in processes:
        # status, video_id, file_size, info_file, video_title = task_status
        async_res = AsyncResult(process.task_id)
        status = async_res.state
        if status == 'SUCCESS':
            message[process.video_id] = {"status": status, "file_name": process.video_name}

        elif status == "PENDING":
            # downloadings = aria2.get_downloads()
            # file_curr_size = ""
            # for downloading in downloadings:
            #     if downloading.name.count(process.video_name) > 0:
            #         file_curr_size = "{:,}".format(downloading.progress)
            files_curr_sizes = dict()

            try:
                files = os.listdir(f"{user_path}/{process.video_id}")
            except FileNotFoundError:
                files_curr_sizes = 0
            else:
                for file in files:
                    files_curr_sizes[file] = "{:,}".format(os.path.getsize(f"{user_path}/{process.video_id}/{file}"))

            message[process.video_id] = {
                "status": status,
                "file_name": process.video_name,
                "files_curr_sizes": files_curr_sizes,
                "file_size": f"{process.video_size:,}"
            }
    message = {"message": message}
    return render(request, 'Final_Downloader/download_status.html', message)

@login_required
def transmit_file(request, video_id):
    user_path = f"data/{request.user}"
    process = get_object_or_404(Process, owner=request.user, video_id=video_id)
    async_res = AsyncResult(process.task_id)
    status = async_res.state
    if status != 'SUCCESS':
        raise Http404
    else:
        pure_file_name = get_pure_filename(user_path, video_id)
        return HttpResponseRedirect(f"/{user_path}/{video_id}/{quote(pure_file_name)}")

@login_required
def search_video(request, key_word):
    user_path = f"data/{request.user}"

    SearchResult.objects.filter(owner=request.user).delete()

    ydl_opts = {"skip_download": True,"writeinfojson": True, "default_search": "ytsearch10", "outtmpl": f"{user_path}/search/%(id)s"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([key_word])
    files = os.listdir(f"{user_path}/search/")

    for file in files:
        with open(f"{user_path}/search/{file}") as f:
            info = json.load(f)

        SearchResult.objects.create(
            video_id = info["id"],
            video_title = info["title"],
            video_description = info["description"].replace(r'\n', '<br>'),
            video_url = info["webpage_url"],
            owner = request.user,
        )
    
    shutil.rmtree(f"{user_path}/search")
    os.mkdir(f"{user_path}/search")

    titles = dict()
    searchresults = get_list_or_404(SearchResult, owner=request.user)
    for searchresult in searchresults:
        titles[searchresult.video_id] = searchresult.video_title
    content = {"titles": titles}
    return render(request, 'Final_Downloader/search_video.html', content)

@login_required
def display_video_info(request, video_id):
    searchresult = get_object_or_404(SearchResult, owner=request.user, video_id=video_id)
    
    content = {
        "title": searchresult.video_title,
        "description": searchresult.video_description.replace(r'\n', '<br>'),
        "url": searchresult.video_url
    }
    return render(request, 'Final_Downloader/display_video_info.html', content)
