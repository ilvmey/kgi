from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=10)
    id_number = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=50)


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)