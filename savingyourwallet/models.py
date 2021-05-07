from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.timezone import now
# Create your models here.
#Expense
class Expense(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.CharField(max_length=266)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=266)

    def __str__(self):
        return self.category

    class Meta:
        ordering: ['-date']

#Category
class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
#User income
class UserIncome(models.Model):
    amount = models.FloatField()  # DECIMAL
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    source = models.CharField(max_length=266)

    class Meta:
        ordering: ['-date']



#
class UserPreference(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    currency=models.CharField(max_length=50 , blank=True, null=True)

    def __str__(self):
        return str(self.user)+'s' + 'preferences'