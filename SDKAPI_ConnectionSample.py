from System import Action
from time import sleep
import sys
import clr
import datetime
clr.AddReferenceToFileAndPath(r'Insert here your path to DLL file')
from tt_net_sdk import *

appKey = 'Insert here your TT AppKey'
algoName = 'Arbitrage'

m_isOrderBookDownloaded = 0
netPosition = ''
netPositionDetected = False
m_instrument = None
m_accounts = None
m_api = None
m_ts = None
enableTrading = True
currentOrderId = None
lastNetPosition = 0
stopLoss = True
mktOrdersRatio = 2

acc = 0 
accNum = #insert here your acc number as int
accName = 'insert here your acc name as string'

netPosProductName = 'Insert Product name for leg1 as string' # ex: CL
netPosAlias = 'Insert leg1 product alias as string' # ex: CL Sep22'
spreadAlias = 'Insert spread alias created on TT enviroment as string'

contractsQty = 6
DisQty = 4
mktDepth = 2

# this is for control market order in case of issue
mktBuyControl = contractsQty*2
mktSellControl = contractsQty*2

mktBuy = 0
mktSell = 0

LE_orderKey = None
SE_orderKey = None
LX_orderKey = None
SX_orderKey = None

dollarStop = 500

LE = # insert here your long entry level
SE = # insert here your short entry level
SX = # insert here your short exit level
LX = # insert here your long exit level

longStopLoss = LE - dollarStop
shortStopLoss = SE + dollarStop



def m_priceSubscription_FieldsUpdated(sender, e): 

    if e.Error is None:     
        now = datetime.datetime.now().time()
        obtainNetPosition()
        
        if (e.Fields.GetBestAskPriceField().Value != None
        and m_isOrderBookDownloaded == 1 and enableTrading == True
        and netPositionDetected): 
            'Insert here your algo logic'
            
    else:
        print(e.Error)   

    
def insertOrder(type, qty, price):
    global currentOrderId

    if abs(int(netPosition)) == 0:
            dis_X = DisQty 
    else:
        if abs(int(netPosition)) <= DisQty:
            dis_X = abs(int(netPosition))
        else:
            dis_X = DisQty
        
    if type == 'buy_limit':        
        op = OrderProfile(m_instrument)
        op.Account = m_accounts[acc]
        op.BuySell = BuySell.Buy
        op.OrderType = OrderType.Limit
        op.OrderQuantity = Quantity.FromDecimal(m_instrument, qty)
        op.DisclosedQuantity = Quantity.FromDecimal(m_instrument, dis_X)
        op.LimitPrice = Price.FromDecimal(m_instrument, price)  

        if m_ts.SendOrder(op) == False:
            print(str(datetime.datetime.now()) + ' Send new order Failed!! ')
            sys.exit()                                   
        else:          
            print(str(datetime.datetime.now()) + ' Sent new order key = ' + op.SiteOrderKey)
            currentOrderId =  op.SiteOrderKey

    if type == 'sell_limit':
        op = OrderProfile(m_instrument)
        op.Account = m_accounts[acc]
        op.BuySell = BuySell.Sell
        op.OrderType = OrderType.Limit
        op.OrderQuantity = Quantity.FromDecimal(m_instrument, qty)
        op.DisclosedQuantity = Quantity.FromDecimal(m_instrument, dis_X)
        op.LimitPrice = Price.FromDecimal(m_instrument, price)  

        if m_ts.SendOrder(op) == False:
            print(str(datetime.datetime.now()) + ' Send new order Failed!! ')
            sys.exit()                                   
        else:          
            print(str(datetime.datetime.now()) + ' Sent new order key = ' + op.SiteOrderKey)
            currentOrderId =  op.SiteOrderKey

    if type == 'buy_market':
        global mktBuy

        op = OrderProfile(m_instrument)
        op.Account = m_accounts[acc]
        op.BuySell = BuySell.Buy
        op.OrderType = OrderType.Limit
        op.OrderQuantity = Quantity.FromDecimal(m_instrument, qty)
        op.LimitPrice = Price.FromDecimal(m_instrument, price + mktDepth) 

        if m_ts.SendOrder(op) == False:
            print(str(datetime.datetime.now()) + ' Send new order Failed!! ')
            sys.exit()                                   
        else:          
            print(str(datetime.datetime.now()) + ' Sent new order key = ' + op.SiteOrderKey)
            currentOrderId =  op.SiteOrderKey
            mktBuy += 1

    if type == 'sell_market':
        global mktSell

        op = OrderProfile(m_instrument)
        op.Account = m_accounts[acc]
        op.BuySell = BuySell.Sell
        op.OrderType = OrderType.Limit
        op.OrderQuantity = Quantity.FromDecimal(m_instrument, qty)
        op.LimitPrice = Price.FromDecimal(m_instrument, price - mktDepth)

        if m_ts.SendOrder(op) == False:
            print(str(datetime.datetime.now()) + ' Send new order Failed!! ')
            sys.exit()                                   
        else:          
            print(str(datetime.datetime.now()) + ' Sent new order key = ' + op.SiteOrderKey)
            currentOrderId =  op.SiteOrderKey
            mktSell +=1


def deleteOrder(ordKey):   
    if m_ts.Orders.ContainsKey(ordKey):
        op = m_ts.Orders[ordKey].GetOrderProfile()
        op.Account = m_accounts[acc]
        op.Action = OrderAction.Delete               
        if m_ts.SendOrder(op) == False:
            print(str(datetime.datetime.now()) + ' Order Delete failed!!')
        else:
            print(str(datetime.datetime.now()) + ' Order Delete succeeded.')


def updateOrder(ordKey, type, price):
    if (type == 'price'):
        if (m_ts.Orders.ContainsKey(ordKey) 
        and m_ts.Orders[ordKey].LimitPrice != Price.FromDecimal(m_instrument, closeD1)):
            op = m_ts.Orders[ordKey].GetOrderProfile()
            op.Account = m_accounts[acc]
            op.LimitPrice = Price.FromDecimal(m_instrument, price)  
            op.Action = OrderAction.Change               
            if m_ts.SendOrder(op) == False:
                print(str(datetime.datetime.now()) + ' Order Update failed!!')
            else:
                print(str(datetime.datetime.now()) + ' Order Update succeeded.')


def m_ts_OrderBookDownload(sender, e):
    print(str(datetime.datetime.now()) + ': OrderBookDownload complete...')
    global m_isOrderBookDownloaded
    m_isOrderBookDownloaded = 1


def m_ts_OrderAdded(sender, e):
    print(str(datetime.datetime.now()) + ': Order added: ' + e.ToString())


def m_ts_OrderDeleted(sender, e):
    print(str(datetime.datetime.now()) + ': Order deleted: ' + e.ToString())
    sys.exit()

    
def m_ts_OrderFilled(sender, e):
    print(str(datetime.datetime.now()) + ': Order filled: ' + e.ToString())

    
def m_ts_OrderRejected(sender, e):
    print(str(datetime.datetime.now()) + ': Order rejected: ' + e.ToString())
    sys.exit()


def m_ts_OrderUpdated(sender, e):
    print(str(datetime.datetime.now()) + ': Order updated: ' + e.ToString())


def m_ts_OrderStatusUnknown(sender, e):
    print(str(datetime.datetime.now()) + ': Order status unknown: ' + e.ToString())
    sys.exit()


def m_ts_OrderTimeout(sender, e):
    print(str(datetime.datetime.now()) + ': Order timed out: ' + e.ToString())
    sys.exit()


def obtainNetPosition():
    global netPositionDetected
    global netPosition
    list1 = []
    instKey = InstrumentKey(MarketId.CME, ProductType.Future, netPosProductName, netPosAlias) # MarketId.CME, MarketId.ICE, etc.
    accKey = AccountKey(accNum, accName) 
    lista1 = m_api.GetPositionSnapshot(accKey, instKey)
    netPosition = str(lista1)
    start = netPosition.find('NetPos:') + 7
    end = netPosition.find('Buys:') 
    netPosition = netPosition[start:end]
    netPositionDetected = True 


def m_api_TTAPIStatusUpdate(sender, e):
    print(algoName + ' is about to start...')
    print('Look up instrument...')
    m_instrLookupRequest = InstrumentLookup(Dispatcher.Current,
                                           MarketId.ASE, 
                                           ProductType.Synthetic, 
                                           'ASE', spreadAlias)
    e2 = m_instrLookupRequest.Get()
    if e2 == ProductDataEvent.Found:
        global m_instrument
        global m_accounts
        global m_ts

        m_instrument = m_instrLookupRequest.Instrument
        print('Instrument found...')           
            
        m_accounts = m_api.Accounts
        print('Account ' + str(m_accounts[acc]) + ' is ready...') 

        m_ts = TradeSubscription(Dispatcher.Current)
        m_ts.OrderBookDownload += m_ts_OrderBookDownload
        m_ts.OrderAdded += m_ts_OrderAdded
        m_ts.OrderDeleted += m_ts_OrderDeleted
        m_ts.OrderFilled += m_ts_OrderFilled
        m_ts.OrderUpdated += m_ts_OrderUpdated
        m_ts.OrderUpdated += m_ts_OrderStatusUnknown
        m_ts.OrderUpdated += m_ts_OrderTimeout
        m_ts.Start()
       
        m_priceSubsciption = PriceSubscription(m_instrLookupRequest.Instrument, Dispatcher.Current)
        m_priceSubsciption.Settings = PriceSubscriptionSettings(PriceSubscriptionType.MarketDepth)
        m_priceSubsciption.FieldsUpdated += m_priceSubscription_FieldsUpdated
        m_priceSubsciption.Start()
       
    else:
        print('Cannot find instrument: ' + e.ToString())


def ttNetApiInitHandler(api, ex):
    if ex is None:
        global m_api
        m_api = api
        print('TT.NET SDK Initialization Succeded')
        api.TTAPIStatusUpdate += m_api_TTAPIStatusUpdate
        api.Start()
    else:
        print('TT.NET SDK Initialization Failed: ' + ex.Message)


def Init():
    opt = TTAPIOptions(ServiceEnvironment.ProdLive, appKey, 5000)
    opt.EnablePositions = True 
    apiInitializeHandler = ApiInitializeHandler(ttNetApiInitHandler)
    TTAPI.CreateTTAPI(Dispatcher.Current, opt, apiInitializeHandler)


m_disp = Dispatcher.AttachWorkerDispatcher()
m_disp.DispatchAction(Action(Init))
m_disp.Run()