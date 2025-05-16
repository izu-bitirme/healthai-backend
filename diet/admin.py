from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Nutrient)
admin.site.register(NutrientUnit)
admin.site.register(MealPlan)
admin.site.register(Meal)
admin.site.register(PromptLog)