import clr

dll_path = 'kgi_api/dll'
dlls = ['Package', 'PushClient', 'QuoteCom', 'TradeCom']
for dll in dlls:
    clr.AddReference(f'{dll_path}/{dll}')

from Package import PackageBase  #from namespace import class
from Package import P001503         #from namespace import class
from Intelligence import PushClient #from namespace import class
from Intelligence import QuoteCom   #from namespace import class
from Intelligence import COM_STATUS #from namespace import class
from Intelligence import DT         #from namespace import class
from Intelligence import IdxKind    #from namespace import class

from Smart import TaiFexCom

from Intelligence import Security_OrdType
from Intelligence import Security_Lot
from Intelligence import Security_Class
from Intelligence import Security_PriceFlag
from Intelligence import SIDE_FLAG
from Intelligence import TIME_IN_FORCE
from Intelligence import RECOVER_STATUS

def initialize():
    global quote_com
    quote_com = initialize_quote_com()
    trade_com = initialize_trade_com()
    return quote_com, trade_com


def initialize_quote_com():
    print('QuoteCom API initialize........')
    token='b6eb'
    sid='API'
    quote_com = QuoteCom('', 8000, sid, token)
    quote_com.OnRcvMessage += onQuoteRcvMessage
    quote_com.OnGetStatus += onQuoteGetStatus

    return quote_com
def initialize_trade_com():

    global trade_com
    global ridDict

    sid='API'
    print('TradeCom API initialize........')
    trade_com = TaiFexCom('', 8000, sid)
    ridDict=dict()
    trade_com.OnRcvMessage += onTradeRcvMessage
    trade_com.OnGetStatus += onTradeGetStatus
    # trade_com.OnRecoverStatus += OnRecoverStatus
    return trade_com


def onQuoteRcvMessage(sender, pkg):
    global quote_receive_message
    quote_receive_message = pkg
    print(f'onQuoteRcvMessage:{pkg.DT}')
    if (pkg.DT==DT.LOGIN.value__):
        account_count=pkg.Count
        print(f'登入成功, 帳號筆數[{account_count}]')
        # for subpkg in pkg.p001503_2:
        #     broker = subpkg.BrokeId
        #     account = subpkg.Account
        #     print(f'帳號資料: 分公司=[{broker}], 帳號=[{account}]')
        # if (int(quote_com.QuoteStock)==True):
        #     print('可註冊證券報價')
        #     if (pkg.Code==0):
        #         print(f'可註冊檔數：{pkg.Qnum}\n')
        # else:
        #     print('無證券報價API權限')

def onQuoteGetStatus(sender, status, msg):
    print('onQuoteGetStatus')
    print(msg)
    smsg = bytes(msg).decode('UTF-8','strict')

    if status == COM_STATUS.LOGIN_READY:
        print(f'STATUS:LOGIN_READY:[{smsg}]')


def onTradeRcvMessage(sender, pkg):
    global trade_receive_message
    trade_receive_message = pkg
    dt = pkg.DT
    print(f'onTradeRcvMessage DT=[{dt}]')

    if (pkg.DT==DT.LOGIN.value__):
        if (pkg.Code==0):
            print('登入成功')
        else:
            errmsg=trade_com.GetMessageMap(pkg.Code)
            code = pkg.Code
            msg = errmsg
            print(f'登入失敗 CODE=[{code}], MSG=[{msg}]')

    if (pkg.DT==DT.FINANCIAL_WSINVENTORYSUM.value__):
        code = pkg.Code
        code_desc = pkg.CodeDesc
        print(f'證券庫存彙總查詢回覆 CODE=[{code},{code_desc}]]')
        rows = pkg.Rows
        print(f'明細筆數=[{rows}]')

        if (pkg.Code == 0) :
            for subpkg in pkg.Detail:
                print("商品代碼=[{symbol}]".format(symbol=subpkg.Symbol))
                print("今日餘額股數=[{ netqty5}]".format(netqty5=subpkg. NETQTY5))
                print("庫存市值=[{ asset }]".format(asset=subpkg. ASSET))
                print("未實現損益=[{netpl}]".format(netpl=subpkg.NETPL))


def onTradeGetStatus(sender, status, msg):
    smsg = ' '
    print(msg)
    if (status==COM_STATUS.CONNECT_READY):
        print(f'交易伺服器連線成功:[{smsg}]')