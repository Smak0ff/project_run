from django.db import models
from django.contrib.auth.models import User


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

    @classmethod
    def run_in_progress_status(cls, run_id):
        run = Run.objects.filter(id=run_id.id).first()
        if not run:
            return False
        return run.status == Run.Status.IN_PROGRESS


class AthleteInfo(models.Model):
    goals = models.TextField()
    weight = models.IntegerField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_info')

    def __str__(self):
        return self.goals

    def get_runs_finished_count(self):
        return Run.objects.filter(athlete=self.user, status=Run.Status.FINISHED).count()

    def get_type(self):
        return 'coach' if self.user.is_staff else 'athlete'


class Challenge(models.Model):
    full_name = models.CharField(max_length=300)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=7, decimal_places=4)
    longtitude = models.DecimalField(max_digits=7, decimal_places=4)

    def __str__(self):
        return f'{str(self.latitude)}:{str(self.longtitude)}'
