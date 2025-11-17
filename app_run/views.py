from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from django.conf import settings
from .serializers import RunSerializer, UserSerializer
from .models import Run
from django.contrib.auth.models import User


@api_view(['GET'])
def company_details_view(request):
    return Response({
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS,
    })


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().filter(is_superuser=False)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset
        user_type = self.request.query_params.get('type', None)
        if user_type == 'coach':
            qs = qs.filter(is_staff=True)
        elif user_type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class RunStartView(APIView):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer

    def patch(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == Run.Status.INIT:
            run.status = Run.Status.IN_PROGRESS
            run.save()
            return Response({f'Статус объекта {run_id} обновлен на IN_PROGRESS.'})
        else:
            return Response({f'Статус объекта {run_id} - {run.status}. Обновление статуса не выполнено.'},
                            status=status.HTTP_400_BAD_REQUEST)


class RunEndView(APIView):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer

    def patch(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == Run.Status.IN_PROGRESS:
            run.status = Run.Status.FINISHED
            run.save()
            return Response({f'Статус объекта {run_id} обновлен на FINISHED.'})
        else:
            return Response({f'Статус объекта {run_id} - {run.status}. Обновление статуса не выполнено.'},
                            status=status.HTTP_400_BAD_REQUEST)
