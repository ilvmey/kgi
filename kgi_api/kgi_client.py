import time
import kgi_api.load_dll as load_dll

QUOTE_HOST = 'quoteapi.kgi.com.tw'
QUOTE_PORT = 443
TRADE_HOST = 'tradeapi.kgi.com.tw'
TRADE_PORT = 443

class KGIClient:

    def __init__(self, retry_times=5):
        quote_com, trade_com = load_dll.initialize()
        from Intelligence import IdxKind
        from Intelligence import DT
        self.DT = DT
        self.quote_com = quote_com
        self.trade_com = trade_com
        self.retry_times = retry_times

    def login(self, account, password):
        self.login_quote_api(account, password)
        self.login_trade_api(account, password)

    def login_quote_api(self, account, password):
        self.quote_com.Connect2Quote(QUOTE_HOST, QUOTE_PORT, account, password, ' ', '')

    def login_trade_api(self, account, password):
        timeout=10000
        trade_com = self.trade_com
        trade_com.ComStatus()
        trade_com.Connect(TRADE_HOST, TRADE_PORT, timeout)

        for _ in range(self.retry_times):
            time.sleep(1)
            if trade_com.ComStatus().ToString() == 'CONNECT_READY':
                trade_com.AutoSubReportSecurity=True
                trade_com.AutoRecoverReportSecurity=True
                trade_com.Login(account, password, ' ')
                break

    def get_accounts(self):
        for _ in range(self.retry_times):
            time.sleep(1)
            if hasattr(load_dll, 'quote_receive_message'):
                if load_dll.quote_receive_message.DT==self.DT.LOGIN.value__:
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

    def get_inventory(self, broker, account):
        for _ in range(self.retry_times):
            # 整股:A, 零股:B
            resp = self.trade_com.RetrieveWsInventorySum('B', broker, account, '')
            if resp == 0:
                break
            time.sleep(1)
        else:
            print('RetrieveWsInventorySum 取得庫存失敗')

    def dispose(self):
        self.quote_com.Dispose()
        self.trade_com.Dispose()