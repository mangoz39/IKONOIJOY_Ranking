from django.db import models


class UserChoice(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    ip = models.CharField(max_length=32, null=True, blank=True)
    love = models.CharField(max_length=16, null=True, blank=True)
    me = models.CharField(max_length=16, null=True, blank=True)
    joy = models.CharField(max_length=16, null=True, blank=True)
    song = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_choices'
