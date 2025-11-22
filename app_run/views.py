from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, PositionSerializer
from .models import Run, AthleteInfo, Challenge, Position


@api_view(['GET'])
def company_details_view(request):
    return Response({
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS,
    })


class Pagination(PageNumberPagination):
    # page_size = 3  # Количество объектов на странице по умолчанию (не обязательный параметр)
    page_size_query_param = 'size'  # Разрешаем изменять количество объектов через query параметр size в url
    max_page_size = 50  # Ограничиваем максимальное количество объектов на странице


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    ordering = ['id']
    pagination_class = Pagination


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    ordering = ['id']
    pagination_class = Pagination

    def get_queryset(self):
        qs = self.queryset
        user_type = self.request.query_params.get('type', None)
        if user_type == 'coach':
            qs = qs.filter(is_staff=True)
        elif user_type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class RunStartView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == Run.Status.INIT:
            run.status = Run.Status.IN_PROGRESS
            run.save()
            return Response({'detail': f'Статус объекта {run_id} обновлен на {Run.Status.IN_PROGRESS}.'})
        else:
            return Response({'detail': f'Статус объекта {run_id} - {run.status}. Обновление статуса не выполнено.'},
                            status=status.HTTP_400_BAD_REQUEST)


class RunStopView(APIView):
    def patch(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == Run.Status.IN_PROGRESS:
            run.status = Run.Status.FINISHED
            run.save()
            runs_finished = run.athlete.athlete_info.get_runs_finished_count()
            if runs_finished >= 10:
                challenge, _ = Challenge.objects.get_or_create(
                    full_name='Сделай 10 Забегов!', athlete=run.athlete
                )
            return Response({'detail': f'Статус объекта {run_id} обновлен на {Run.Status.FINISHED}.'})
        else:
            return Response({'detail': f'Статус объекта {run_id} - {run.status}. Обновление статуса не выполнено.'},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, run_id):
        return self.patch(request, run_id)


class AthleteInfoView(APIView):
    user = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.user = get_object_or_404(User, id=kwargs['user_id'])

    def get(self, request, user_id):
        athlete_info, created = AthleteInfo.objects.get_or_create(user=self.user, defaults={'user': self.user, 'goals': '',
                                                                                          'weight': 0})
        serializer = AthleteInfoSerializer(athlete_info)
        return Response(serializer.data)

    def put(self, request, user_id):
        athlete_info, created = AthleteInfo.objects.get_or_create(user=self.user, defaults={'user': self.user,
                                                                            'goals': request.data.get('goals', ''),
                                                                            'weight': request.data.get('weight', 0)})
        serializer = AthleteInfoSerializer(athlete_info, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['athlete']


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['run']
