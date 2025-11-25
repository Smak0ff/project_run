from django.db import models
from django.contrib.auth.models import User
from geopy.distance import geodesic


class Run(models.Model):
    class Status(models.TextChoices):
        INIT = 'init', 'init'
        IN_PROGRESS = 'in_progress', 'in_progress'
        FINISHED = 'finished', 'finished'
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    distance = models.FloatField(default=0.0)
    status = models.CharField(
        choices=Status.choices,
        default=Status.INIT
    )

    def __str__(self):
        return f'{self.athlete}: {self.comment}'

    def distance_calculation(self):
        positions = Position.objects.filter(run=self).order_by('id')
        total_distance_km = 0.0
        prev_position = None
        for pos in positions:
            if prev_position is not None:
                prev_position = (prev_position.latitude, prev_position.longitude)
                position = (pos.latitude, pos.longitude)
                segment = geodesic(prev_position, position).km
                total_distance_km += segment
            prev_position = pos
        return total_distance_km


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

    def get_type(self):
        return 'coach' if self.user.is_staff else 'athlete'


class Challenge(models.Model):
    full_name = models.CharField(max_length=300)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=7, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)

    def __str__(self):
        return f'{str(self.latitude)}:{str(self.longitude)}'
