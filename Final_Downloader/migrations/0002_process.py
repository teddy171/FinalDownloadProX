# Generated by Django 4.0.5 on 2022-08-08 06:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Final_Downloader', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.TextField()),
                ('video_id', models.TextField()),
                ('video_name', models.TextField()),
                ('video_size', models.BigIntegerField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
