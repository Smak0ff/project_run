from .models import Run


def get_runs_finished_count(user):
    return Run.objects.filter(athlete=user, status=Run.Status.FINISHED).count()
