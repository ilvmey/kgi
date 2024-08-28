import csv
import os
import time
import kgi_api.load_dll as load_dll

quote_com, trade_com = load_dll.initialize()

from Intelligence import IdxKind
from Intelligence import DT
# ACCOUNT = os.getenv('KGI_ACCOUNT')
# PASSWORD = os.getenv('KGI_PASSWORD')

QUOTE_HOST = 'quoteapi.kgi.com.tw'
QUOTE_PORT = 443
TRADE_HOST = 'tradeapi.kgi.com.tw'
TRADE_PORT = 443

retry_times = 5

def login_quote_api(account, password):
    quote_com.Connect2Quote(QUOTE_HOST, QUOTE_PORT, account, password, ' ', '')
    return get_accounts()

def get_accounts():
    for _ in range(retry_times):
        time.sleep(1)
        if hasattr(load_dll, 'quote_receive_message'):
            if load_dll.quote_receive_message.DT==DT.LOGIN.value__:
                p001503 = load_dll.quote_receive_message
                p001503_2 = p001503.p001503_2
                name = p001503.Name
                data = {'name': name, 'accounts': []}
                try:
                    for subpkg in p001503_2:
                        broker = subpkg.BrokeId
                        account = subpkg.Account

                        print(f'帳號資料: 姓名：{name}, 分公司：{broker}, 帳號：{account}')
                        data['accounts'].append({
                            'broker': broker,
                            'account': account
                        })
                except Exception as e:
                    print(f'get account data error: {e}')
                finally:
                    return data


def login_trade_api(account, password):
    timeout=10000
    trade_com.ComStatus()
    trade_com.Connect(TRADE_HOST, TRADE_PORT, timeout)

    for _ in range(retry_times):
        time.sleep(1)
        if trade_com.ComStatus().ToString() == 'CONNECT_READY':
            trade_com.AutoSubReportSecurity=True
            trade_com.AutoRecoverReportSecurity=True
            trade_com.Login(account, password, ' ')
            break

def get_inventory(broker, account):
    for _ in range(retry_times):
        resp = trade_com.RetrieveWsInventorySum('B', broker, account, '')
        if resp == 0:
            break
        time.sleep(1)
    else:
        print('RetrieveWsInventorySum 取得庫存失敗')

def read_csv(filename='account.csv'):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
    return rows

if __name__ == '__main__':
    accounts = read_csv()
    for account in accounts:
        login_account = account[0]
        password = account[1]
        kgi_account = login_quote_api(login_account, password)
        login_trade_api(login_account, password)

        for kgi_account in kgi_account['accounts']:
            broker = kgi_account['broker']
            kgi_account_number = kgi_account['account']
            get_inventory(broker, kgi_account_number)

        time.sleep(5) # 等待資料列印
    quote_com.Dispose()
    trade_com.Dispose()
# TODO: 把凱基的callback function資料轉接進rabbitmq, 這樣用自己的worker比較好開發