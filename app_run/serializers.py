from rest_framework import serializers
from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from django.contrib.auth.models import User
from . import utils


#Основной User сериализатор
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
        return 0 if athlete_info is None else utils.get_runs_finished_count(athlete_info.user)


#Отдельный сериализатор для краткой информации по юзеру в Run
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


class PositionSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(min_value=-90, max_value=90, max_digits=7, decimal_places=4)
    longitude = serializers.DecimalField(min_value=-180, max_value=180, max_digits=7, decimal_places=4)
    class Meta:
        model = Position
        fields = '__all__'

    def validate_run(self, value):
        if not Run.run_in_progress_status(value):
            raise serializers.ValidationError('Только для запущенных забегов!')
        return value


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ['name', 'uid', 'latitude', 'longitude', 'picture', 'value']


#Отдельный сериализатор под конкретный метод GET+ID
class UserItemsSerializer(UserSerializer):
    items = CollectibleItemSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['items']
