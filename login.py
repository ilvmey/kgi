import os
import time
import kgi_api.load_dll as load_dll

quote_com, trade_com = load_dll.initialize()

from Intelligence import IdxKind    #from namespace import class
from Intelligence import DT
ACCOUNT = os.getenv('KGI_ACCOUNT')
PASSWORD = os.getenv('KGI_PASSWORD')

QUOTE_HOST = 'quoteapi.kgi.com.tw'
QUOTE_PORT = 443
TRADE_HOST = 'tradeapi.kgi.com.tw'
TRADE_PORT = 443


def login_quote_api():
    quote_com.Connect2Quote(QUOTE_HOST, QUOTE_PORT, ACCOUNT, PASSWORD, ' ', '')
    brokers, accounts = get_accounts()
    return brokers, accounts

def get_accounts():
    while True:
        time.sleep(1)
        if hasattr(load_dll, 'quote_receive_message'):
            if load_dll.quote_receive_message.DT==DT.LOGIN.value__:
                brokers = []
                accounts = []
                try:
                    for subpkg in load_dll.quote_receive_message.p001503_2:
                        broker = subpkg.BrokeId
                        account = subpkg.Account
                        print(f'帳號資料: 分公司=[{broker}], 帳號=[{account}]')
                        brokers.append(broker)
                        accounts.append(account)
                except Exception as e:
                    print(f'get account data error: {e}')
                finally:
                    return brokers, accounts


def login_trade_api():
    timeout=5000
    trade_com.ComStatus()
    trade_com.Connect(TRADE_HOST, TRADE_PORT, timeout)
    while True:
        time.sleep(1)
        if trade_com.ComStatus().ToString() == 'CONNECT_READY':
            trade_com.AutoSubReportSecurity=True
            trade_com.AutoRecoverReportSecurity=True
            trade_com.Login(ACCOUNT, PASSWORD, ' ')
            break

if __name__ == '__main__':
    brokers, accounts = login_quote_api()
    login_trade_api()

    while brokers and accounts:
        trade_com.RetrieveWsInventorySum('B', brokers[0], accounts[0], '2330')
        time.sleep(1)


# TODO: 把凱基的callback function資料轉接進rabbitmq, 這樣用自己的worker比較好開發