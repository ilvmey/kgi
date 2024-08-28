from django.db import models


class User(models.Model):
    name = models.CharField(max_length=10)
    id_number = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=50)


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    broker = models.CharField(max_length=4)
    account_number = models.CharField(max_length=10, unique=True)

    @property
    def full_account_number(self):
        return f'{self.broker}{self.account_number}'