from django.db import models


class Post(models.Model):
    name = models.CharField(max_length=128, blank=False)

    def __str__(self):
        return self.name
