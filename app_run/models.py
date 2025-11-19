from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Run(models.Model):
    class Status(models.TextChoices):
        INIT = 'init', 'init'
        IN_PROGRESS = 'in_progress', 'in_progress'
        FINISHED = 'finished', 'finished'
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(
        choices=Status.choices,
        default=Status.INIT
    )

    def __str__(self):
        return f'{self.athlete}: {self.comment}'


class AthleteInfo(models.Model):
    goals = models.TextField()
    weight = models.IntegerField()
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.goals
