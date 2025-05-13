from django.contrib import admin
from .models import (
DailyRecoveryLog, ExerciseLog, MedicationLog,
SleepLog, MoodLog, PainLog, NutritionLog,
RecoveryCycle,DistractionLog,LengtheningMilestone,LimbLengtheningInfo,BoneConsolidationCheck

)

admin.site.register(ExerciseLog)
admin.site.register(PainLog)
admin.site.register(NutritionLog)
admin.site.register(MoodLog)
admin.site.register(MedicationLog)
admin.site.register(SleepLog)
admin.site.register(DailyRecoveryLog)
admin.site.register(RecoveryCycle)
admin.site.register(DistractionLog)
admin.site.register(LengtheningMilestone)
admin.site.register(LimbLengtheningInfo)
admin.site.register(BoneConsolidationCheck)
