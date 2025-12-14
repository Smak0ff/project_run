from .models import Run, Challenge
from .enum import ChallengeEvent
from django.db.models import Sum


def get_runs_finished_count(user):
    return Run.objects.filter(athlete=user, status=Run.Status.FINISHED).count()


def overall_distance(user):
    #в aggregate вызываем sum для distance в бд, 0.0 для защиты от None в значении
    result = Run.objects.filter(athlete=user,
                                status=Run.Status.FINISHED).aggregate(result=Sum("distance"))['result'] or 0.0
    return result


def challenge_check(event, instance):
    handler = EVENT_HANDLERS.get(event)
    if handler:
        handler(instance)


def handle_run_finished(run: Run):
    athlete = run.athlete
    #Проверка на челлендж 10 забегов
    runs_finished = get_runs_finished_count(athlete)
    if runs_finished >= 10:
        challenge, _ = Challenge.objects.get_or_create(
            full_name='Сделай 10 Забегов!', athlete=athlete
        )
    #Проверка на челлендж 50 км
    all_distance = overall_distance(athlete)
    if all_distance >= 50:
        challenge, _ = Challenge.objects.get_or_create(
            full_name='Пробеги 50 километров!', athlete=athlete
        )
    # Проверка на челлендж "2км за 10 минут"
    if run.run_time_seconds <= 600 and run.distance >= 2:
        challenge, _ = Challenge.objects.get_or_create(
            full_name='2 километра за 10 минут!', athlete=athlete
        )


def handle_run_started(run: Run):
    pass


EVENT_HANDLERS = {
    ChallengeEvent.RUN_FINISHED: handle_run_finished,
    ChallengeEvent.RUN_STARTED: handle_run_started,
}
