from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Category(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/')


class FunkoPop(models.Model):
    collection = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    price = models.FloatField(null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    rate = models.IntegerField(default=1, validators=[
        MinValueValidator(1), MaxValueValidator(5)
    ])


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(FunkoPop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


