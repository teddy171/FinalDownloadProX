import os
import aria2p
import shutil
import json

import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from celery.result import AsyncResult
import youtube_dl

from Final_Downloader.tasks import download_video

from .models import Task
from .forms import TaskForm

def clean_data(user):
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


def get_pure_filename(info_file, user_path, video_id):
    files = os.listdir(f"{user_path}/{video_id}")
    try:
        files.remove(info_file)
        files.remove("full_size.json")
    except ValueError:
        pass
    return files[0]

def download_video_info(content, location):
    ydl_opts = {
        "writeinfojson": True, 
        "outtmpl": f"{location}/%(id)s/%(title)s.%(ext)s", 
        "skip_download": True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([content])

def save_form(form, owner):
    if form.is_valid():
        new_task = form.save(commit=False)
        new_task.owner = owner
        new_task.save()

def get_download_satus(task_worker_dict, user_path):
    for video_id, task_id in task_worker_dict.items():
        async_res = AsyncResult(task_id)
        status = async_res.state
        files = os.listdir(f"{user_path}/{video_id}")
        for file in files:
            element = file.split('.')
            if(element[-1] == 'json' and element[-2] == "info"):
                info_file = file
                files.remove(info_file)   
        with open(f"{user_path}/{video_id}/{info_file}") as f:
            info = json.load(f)
            file_title = info["title"]
            file_sizes = []
            for format in info["formats"]:
                if format["filesize"] != None:
                    file_sizes.append(format["filesize"])
            file_size = max(file_sizes)
            yield (status, video_id, file_size, info_file, file_title)

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
            try:
                r = requests.get(content)
            except requests.exceptions.MissingSchema:
                return redirect("Final_Downloader:search_video", key_word=content)
            else:
                same_task = Task.objects.filter(content=content, owner=request.user)
                if same_task or not(r.ok):
                    return redirect('Final_Downloader:new_task')
                else:
                    save_form(form, request.user)
                    return redirect('Final_Downloader:download_task')
                    

    #Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'Final_Downloader/new_task.html', context)


@login_required
def download_task(request):
    if request.method != 'POST':
        return render(request, 'Final_Downloader/download_video.html')
    else:
        whether_donwload = request.POST.get('whether_donwload', None)
        whether_add = request.POST.get('whether_add', None)
        if whether_donwload:
            tasks = Task.objects.filter(owner=request.user)
            path = clean_data(request.user)
            if len(tasks) == 0:
                return redirect('Final_Downloader:new_task')
            task_status = {}
            for task in tasks:
                origin_file = set(os.listdir(path))
                download_video_info(str(task), path)
                curr_file = set(os.listdir(path))
                task = download_video.delay(str(task), path)
                
                task_status[list(curr_file-origin_file)[0]] = task.id

            with open(f"{path}/work.json", 'w') as f:
                json.dump(task_status, f)
            tasks.delete()
            return redirect('Final_Downloader:download_status')
        elif whether_add:
            return redirect('Final_Downloader:new_task')

@login_required
def download_status(request):
    user_path = f"data/{request.user}"
    try:
        with open(f"{user_path}/work.json") as f:
            task_worker = json.load(f)
    except:
        raise Http404
    else:
        tasks_status = list(get_download_satus(task_worker, user_path))
        message = {}
        for task_status in tasks_status:
            status, video_id, file_size, info_file, video_title = task_status
            if status == 'SUCCESS':
                message[video_id] = {"status": status, "file_name": video_title}

            elif status == "PENDING":
                aria2 = aria2p.API(
                    aria2p.Client(
                        host="http://localhost",
                        port=6800,
                        secret=""
                    )
                )

                while True:
                    try:
                        downloadings = aria2.get_downloads()
                    except:
                        pass
                    else:
                        break
                file_curr_size = ""
                for downloading in downloadings:
                    if downloading.name.count(video_title) > 0:
                        file_curr_size = "{:,}".format(downloading.progress)
                if file_curr_size == "":
                    file_curr_size = 0
                file_size = "{:,}".format(file_size)
                message[video_id] = {"status": status, "file_name": video_title, "file_curr_size": file_curr_size, "file_size" :file_size}
        message = {"message": message}
        return render(request, 'Final_Downloader/download_status.html', message)

@login_required
def transmit_file(request, video_id):
    user_path = f"data/{request.user}"
    try:
        with open(f"{user_path}/work.json") as f:
            task_worker = json.load(f)
    except FileNotFoundError:
        raise Http404
    else:
        tasks_status = list(get_download_satus(task_worker, user_path))
        for task_status in tasks_status:
            status, video_id_tmp, _, info_file, file_title = task_status
            if video_id == video_id_tmp:
                if status != 'SUCCESS':
                    raise Http404
                else:
                    pure_file_name = get_pure_filename(info_file, user_path, video_id)
                    return HttpResponseRedirect(f"/{user_path}/{video_id}/{pure_file_name}")

@login_required
def search_video(request, key_word):
    user_path = f"data/{request.user}"
    ydl_opts = {"skip_download": True,"writeinfojson": True, "default_search": "ytsearch10", "outtmpl": f"{user_path}/search/%(id)s"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([key_word])
    files = os.listdir(f"{user_path}/search/")
    titles = dict()
    for file in files[:20]:
        with open(f"{user_path}/search/{file}") as f:
            info = json.load(f)
            titles[info["id"]] = info["title"]
    content = {"titles": titles}
    return render(request, 'Final_Downloader/search_video.html', content)

@login_required
def display_video_info(request, video_id):
    user_path = f"data/{request.user}"
    with open(f"{user_path}/search/{video_id}.info.json") as f:
        info = json.load(f)
    content = {"title": info["title"], "description": info["description"].replace(r'\n', '<br>'), "url":info["webpage_url"]}
    return render(request, 'Final_Downloader/display_video_info.html', content)

