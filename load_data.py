import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kgi_project.settings')

django.setup()
from kgi_app.models import User

def read_csv(filename='account.csv'):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
    return rows

User.objects.all().delete()

accounts = read_csv('account.csv')

for account in accounts:
    User.objects.create(name=account[0], id_number=account[1], password=account[2])