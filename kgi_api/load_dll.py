import clr

dll_path = 'kgi_api/dll'
dlls = ['Package', 'PushClient', 'QuoteCom', 'TradeCom']
for dll in dlls:
    clr.AddReference(f'{dll_path}/{dll}')

from Package import PackageBase
from Package import P001503
from Intelligence import PushClient
from Intelligence import QuoteCom
from Intelligence import COM_STATUS
from Intelligence import DT
from Intelligence import IdxKind

from Smart import TaiFexCom

from Intelligence import Security_OrdType
from Intelligence import Security_Lot
from Intelligence import Security_Class
from Intelligence import Security_PriceFlag
from Intelligence import SIDE_FLAG
from Intelligence import TIME_IN_FORCE
from Intelligence import RECOVER_STATUS

from message_queue.base import conn, TradeMessageProducer, trade_message_queue

trade_receive_message_producer = TradeMessageProducer(conn, trade_message_queue)

def initialize():
    quote_com = initialize_quote_com()
    trade_com = initialize_trade_com()

    return quote_com, trade_com


def initialize_quote_com():
    print('QuoteCom API initialize........')
    global quote_com

    token='b6eb'
    sid='API'
    quote_com = QuoteCom('', 8000, sid, token)
    quote_com.OnRcvMessage += on_quote_receive_message
    quote_com.OnGetStatus += on_quote_get_status

    return quote_com
def initialize_trade_com():
    print('TradeCom API initialize........')
    global trade_com

    sid='API'

    trade_com = TaiFexCom('', 8000, sid)
    trade_com.OnRcvMessage += on_trade_receive_message
    trade_com.OnGetStatus += on_trade_get_status
    trade_com.OnRecoverStatus += on_recover_status
    return trade_com


def on_quote_receive_message(sender, pkg):
    global quote_receive_message
    quote_receive_message = pkg
    print(f'on_quote_receive_message:{pkg.DT}')
    if (pkg.DT==DT.LOGIN.value__):
        account_count=pkg.Count
        print(f'登入成功, 帳號筆數[{account_count}]')


def on_quote_get_status(sender, status, msg):
    print('on_quote_get_status')
    print(msg)
    smsg = bytes(msg).decode('UTF-8','strict')

    if status == COM_STATUS.LOGIN_READY:
        print(f'STATUS:LOGIN_READY:[{smsg}]')


def on_trade_receive_message(sender, pkg):
    # trade_receive_message_producer.send({'msg': pkg})
    global trade_receive_message
    trade_receive_message = pkg
    dt = pkg.DT
    print(f'on_trade_receive_message DT=[{dt}]')

    if pkg.DT == DT.LOGIN.value__:
        if (pkg.Code == 0):
            print('交易伺服器登入成功')
        else:
            errmsg=trade_com.GetMessageMap(pkg.Code)
            code = pkg.Code
            msg = errmsg
            print(f'交易伺服器登入失敗 CODE=[{code}], MSG=[{msg}]')

    if pkg.DT == DT.FINANCIAL_WSINVENTORYSUM.value__:
        code = pkg.Code
        code_desc = pkg.CodeDesc
        print(f'證券庫存彙總查詢回覆 CODE=[{code},{code_desc}]]')
        rows = pkg.Rows
        print(f'明細筆數={rows}')

        if pkg.Code == 0:
            for subpkg in pkg.Detail:
                symbol = subpkg.Symbol
                # netqty5=subpkg.NETQTY5
                # asset=subpkg.ASSET
                # netpl=subpkg.NETPL
                print(f'商品代碼={symbol}')
                # print(f'今日餘額股數={netqty5}')
                # print(f'庫存市值={asset}')
                # print(f'未實現損益={netpl}')


def on_trade_get_status(sender, status, msg):
    smsg = ' '
    print(msg)
    if (status==COM_STATUS.CONNECT_READY):
        print(f'交易伺服器連線成功:[{smsg}]')

def on_recover_status(sender, topic, status, recover_count):
    if (status==RECOVER_STATUS.RS_DONE):
        #回補資料結束
        if (recover_count==0):
            print(f'結束回補 Topic:{topic}')
        else:
            tp = topic
            count = recover_count
            print(f'結束回補 Topic={tp}, 筆數={count}')
    elif (status==RECOVER_STATUS.RS_BEGIN):
        #開始回補資料
        print(f'開始回補 Topic:{topic}')