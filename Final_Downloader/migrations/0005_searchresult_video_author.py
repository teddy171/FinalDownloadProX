# Generated by Django 4.0.5 on 2022-08-18 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Final_Downloader', '0004_searchresult_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchresult',
            name='video_author',
            field=models.TextField(default='cross mind'),
            preserve_default=False,
        ),
    ]
