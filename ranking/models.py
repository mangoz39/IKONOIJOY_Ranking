from django.db import models


class Music(models.Model):
    name = models.TextField(default="song")
    singer = models.TextField(default="=LOVE")
    url = models.TextField(default='https://www.youtube.com/')
    samune = models.IntegerField(default='0')

    class Meta:
        db_table = "music"
