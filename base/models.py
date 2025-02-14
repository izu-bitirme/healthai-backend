from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    priority = models.IntegerField(default=0)


class Faq(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    priority = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

