from django.db import models

class Validator(models.Model):
    coldkey = models.CharField(max_length=255)
    hotkey = models.CharField(max_length=255, unique=True)
    stake = models.FloatField()
    parentkey_netuids = models.JSONField(default=list)
    childkeys = models.JSONField(default=list)
    parentkeys = models.JSONField(default=list)

    def __str__(self):
        return self.hotkey