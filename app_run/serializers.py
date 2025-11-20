from rest_framework import serializers
from .models import Run, AthleteInfo, Challenge
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        athlete_info = getattr(obj, 'athlete_info', None)
        return 'coach' if athlete_info is None else obj.athlete_info.get_type()

    def get_runs_finished(self, obj):
        athlete_info = getattr(obj, 'athlete_info', None)
        return 0 if athlete_info is None else obj.athlete_info.get_runs_finished_count()


class UserSerializerSmall(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializerSmall(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class AthleteInfoSerializer(serializers.ModelSerializer):
    weight = serializers.IntegerField(min_value=1, max_value=899)
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=User.objects.all()
    )

    class Meta:
        model = AthleteInfo
        fields = '__all__'


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'
