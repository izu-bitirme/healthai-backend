from django.db import models


class NutrientUnit(models.Model):
    unit = models.CharField(max_length=100)


class Nutrient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    kalories = models.PositiveIntegerField(default=0)
    proteins = models.PositiveIntegerField(default=0)
    fats = models.PositiveIntegerField(default=0)
    carbohydrates = models.PositiveIntegerField(default=0)
    unit = models.ForeignKey(NutrientUnit, on_delete=models.CASCADE)


class MealPlan(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    user = models.ForeignKey("user_profile.UserProfile", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    assigner = models.ForeignKey(
        "user_profile.UserProfile",
        on_delete=models.CASCADE,
        related_name="assigner",
    )

    def to_prompt(self):
        """
        Will generate part of the prompt to tell model about the diet
        """


class Meal(models.Model):
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)


class PromptLog(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
