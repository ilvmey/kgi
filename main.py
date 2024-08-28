import csv
import os
import time
from kgi_api.kgi_client import KGIClient


QUOTE_HOST = 'quoteapi.kgi.com.tw'
QUOTE_PORT = 443
TRADE_HOST = 'tradeapi.kgi.com.tw'
TRADE_PORT = 443

retry_times = 5

def read_csv(filename='account.csv'):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
    return rows

def get_users():
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kgi_project.settings')

    django.setup()
    from kgi_app.models import User

    users = User.objects.all()
    return users

if __name__ == '__main__':
    kgi_client = KGIClient()
    users = get_users()

    for user in users:
        id_number = user.id_number
        password = user.password
        kgi_client.login(id_number, password)
        accounts = kgi_client.get_accounts()

        for account in accounts['accounts']:
            broker = account['broker']
            kgi_account_number = account['account']
            kgi_client.get_inventory(broker, kgi_account_number)

        time.sleep(5) # 等待資料列印
    kgi_client.dispose()

# TODO: 把凱基的callback function資料轉接進rabbitmq, 這樣用自己的worker比較好開發