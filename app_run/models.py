from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    class Status(models.TextChoices):
        INIT = 'INIT', 'init'
        IN_PROGRESS = 'IN_PROGRESS', 'in_progress'
        FINISHED = 'FINISHED', 'finished'
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(
        choices=Status.choices,
        default=Status.INIT
    )

    def __str__(self):
        return f'{self.athlete}: {self.comment}'


