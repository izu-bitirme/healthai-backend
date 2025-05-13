from rest_framework import serializers
from .models import (
    DailyRecoveryLog,
    ExerciseLog,
    MedicationLog,
    NutritionLog,
    SleepLog,
    PainLog,
    MoodLog
)


class ExerciseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseLog
        fields = ['id', 'exercise_name', 'duration_minutes', 'exercise_type', 'intensity', 'notes', 'daily_log']

    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Egzersiz süresi sıfırdan büyük olmalıdır.")
        return value


class MedicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationLog
        fields = ['id', 'medicine_name', 'dosage', 'taken', 'daily_log']


class NutritionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionLog
        fields = ['id', 'calories', 'protein_g', 'water_intake_ml', 'notes', 'daily_log']


class SleepLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepLog
        fields = ['id', 'sleep_duration', 'sleep_quality', 'daily_log']


class PainLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PainLog
        fields = ['id', 'body_part', 'intensity', 'daily_log']


class MoodLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodLog
        fields = ['id', 'mood_description', 'level', 'daily_log']


class DailyRecoveryLogSerializer(serializers.ModelSerializer):
    exercises = ExerciseLogSerializer(many=True, required=False)
    medications = MedicationLogSerializer(many=True, required=False)
    nutrition = NutritionLogSerializer(many=True, required=False)
    sleep = SleepLogSerializer(many=True, required=False)
    pain_details = PainLogSerializer(many=True, required=False)
    moods = MoodLogSerializer(many=True, required=False)

    class Meta:
        model = DailyRecoveryLog
        fields = "__all__"

    def create(self, validated_data):
        # Alt modelleri ayıkla
        exercises = validated_data.pop("exercises", [])
        medications = validated_data.pop("medications", [])
        nutrition = validated_data.pop("nutrition", [])
        sleep = validated_data.pop("sleep", [])
        pain_details = validated_data.pop("pain_details", [])
        moods = validated_data.pop("moods", [])

        # Ana kayıt
        daily_log = DailyRecoveryLog.objects.create(**validated_data)

        # Alt kayıtları ekle
        for item in exercises:
            ExerciseLog.objects.create(daily_log=daily_log, **item)
        for item in medications:
            MedicationLog.objects.create(daily_log=daily_log, **item)
        for item in nutrition:
            NutritionLog.objects.create(daily_log=daily_log, **item)
        for item in sleep:
            SleepLog.objects.create(daily_log=daily_log, **item)
        for item in pain_details:
            PainLog.objects.create(daily_log=daily_log, **item)
        for item in moods:
            MoodLog.objects.create(daily_log=daily_log, **item)

        return daily_log