from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    """The url the user is going to download."""
    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Return a string representation of the model.""" 
        return self.content

class Process(models.Model):
    '''存储正在下载的视频信息'''
    task_id = models.TextField()
    video_id = models.TextField()
    video_name = models.TextField()
    video_size = models.BigIntegerField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self) -> str:
        """Return a string representation of the model.""" 
        return self.task_id

class SearchResult(models.Model):
    video_id = models.TextField()
    video_title = models.TextField()
    video_description = models.TextField()
    video_url = models.TextField()
    video_author = models.TextField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return self.video_title
