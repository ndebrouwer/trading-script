import logging
import time
import threading
import os
from datetime import datetime
import binance
#for the API key
#for the order functions
from binance.enums import *
import smtplib, ssl
from email.message import EmailMessage
import statistics
from binance.client import Client
from Key import *
from TokenModule import Token
import pickle
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
#get and initalise binance client using api keys (this cant withdraw yet , not enabled too)
#we can use the client to execute trades and call data, but since we already have the websocket for now we wont call data

class Custodian:
    def __init__(self,tokens):
        self.client =  Client(api_key, api_secret)
        self.switch = True
        self.tokens = tokens #token list
        #orders master list for all the currencies' buy ins, doesnt log sells
        self.min_notional = 10
        self.current_asset = self.CustodianAssetHeld()
        self.previous_asset = ''
        self.current_assets = []
        self.gains = self.getGains()
        self.threshold = .0002
        self.alert_threshold = .9
        self.divisor = .5
        self.data = []
        self.fee = .001
        self.m = 10080 #minute time interval over which we look at data
         #get 3 days of price data per token when Custodian is instantiated
        self.previous_asset = ''
        self.market = 'bull'
        self.last_4_tokens = []
        self.automated = False
        self.gains_USDT = 0
        self.bm = BinanceSocketManager(self.client)
        self.conn_key = self.bm.start_user_socket(self.process_message)
        self.user_info = {}
        self.account_update = {}
        self.balance_update = {}
        self.order_update = {}
    def process_message(self,msg):
        print(msg)
        self.user_info = msg
        if msg['e'] == 'executionReport':
            self.order_update = msg
        if msg['e'] == 'outboundAccountPosition':
            self.account_update = msg
        if msg['e'] == 'balanceUpdate':
            self.balance_update = msg

       
    def getGains(self):
        gains = 0
        if os.stat("gains.pickle").st_size != 0:
            pickle_off = open("gains.pickle", 'rb')
            gains = pickle.load(pickle_off)
            pickle_off.close()
        return gains
    def CustodianAssetHeld(self):
        if self.getUSDT() < self.min_notional :
            for asset in self.client.get_account()["balances"]:
                if float(asset["free"]) >  1 or float(asset["locked"]) > 1:
                    return Token(asset["asset"])
        else:
            return Token('USDT')
                
    def log_asset_prices(self):
        if datetime.now().timetuple().tm_sec == 61:
            for token in self.tokens:
                logging.basicConfig(filename=token.name+'.txt', level=logging.INFO, encoding =None,format='%(message)s')
                logging.info(token.getPrice())
    def fillAndStripData(self):
        for token in self.tokens:
            self.data.append(token.get7days())
            dummydata = self.data
            for priceData in dummydata[-1]:
                savedIndex = dummydata[-1].index(priceData)
                self.data[-1][savedIndex] = float( (priceData[1]) ) 
            token.setMean( statistics.mean(self.data[-1]) )
            token.setDev(statistics.stdev(self.data[-1] ) )
        return self.data
    def CustomFillAndStripData(self,start_interval,end_interval):
        for token in self.tokens:
            print("Appending data")
            self.data.append(token.getPastData(start_interval,end_interval))
            dummydata = self.data
            for priceData in dummydata[-1]:
                savedIndex = dummydata[-1].index(priceData)
                self.data[-1][savedIndex] = float( (priceData[1]) ) 
            token.setMean( statistics.mean(self.data[-1]) )
            token.setDev(statistics.stdev(self.data[-1] ) )
        return self.data

    def initalizeData(self):
        if os.stat("data.pickle").st_size == 0:
            print("Calling data from client")    
            self.fillAndStripData()
        else:
            print("Loading pickled data")
            pickle_off = open("data.pickle", 'rb')
            self.data = pickle.load(pickle_off)
            print('Loaded data.pickle into data variable for price data')     
        if len(self.data) != 0:
            print('Successfully instantiated Custodian and filled data, data length is '+str(len(self.data)) )     
    def updateDivisor(self,divisor):
        self.divisor = divisor
    def recording(self):
            logging.basicConfig(filename=i+'log.txt', level=logging.DEBUG, encoding =None)
            logging.info()
    def alert(self,type):
        port = 465  # For SSL
        password = "Kidsclub1!"
        # Create a secure SSL contex
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.ehlo
        server.login("ducinaltum1998@gmail.com", password)
        sender_email = "ducinaltum1998@gmail.com"
        receiver_email = "nicdebrouwer@gmail.com"
        if type=='alert':
            message =  """\
            Subject: Alert from Custodian Custos, your loyal liege

            Sire, prices hath plummeted catastrophically and thine profit wanes, affairs require thine attention."""
        if type=='gains':
             message =  """\
            Subject: Gains update from Custodian Custos, your loyal liege

            Sire, thine daily gains today are """+str(gains*100)+"%"
        server.sendmail(sender_email, receiver_email, message)
        server.close()
    def dailyUpdate(self):
        current_time = datetime.now()
        if current_time:
            time.sleep(10)
            self.alert('gains')
    def update_previous_assets(self,token):
        if len(self.last_4_tokens) == 4:
            self.last_4_tokens.remove(self.last_4_tokens[0] )
        self.last_4_tokens.append(token)
    def is_previous_asset(self,token):
        for previous_token in self.last_4_tokens:
            if token.name == previous_token.name:
                return True
        return False  
    def rank(self,tokens):
        if self.market=='bull':
            ripest = Token('DUMMY')
            ripest.setRipeness(10000)
            for i in range(len(tokens)):
                tokens[i].setMean(statistics.mean(self.data[i] )  )
                tokens[i].setDev(statistics.stdev(self.data[i] ) )
                tokens[i].setMax(max(self.data[i]) )
                tokens[i].setMin(min(self.data[i] ) )
                print(tokens[i].getName())
                print(tokens[i].getMean())
                print(tokens[i].getDev())
                 #z = float(tokens[i].getPrice())/tokens[i].getMin()
                z = ( float(tokens[i].getPrice())+ (self.threshold*tokens[i].getMean())-tokens[i].getMean()   )/tokens[i].getDev()
                ripeness = z
                tokens[i].setRipeness(ripeness)
                if(tokens[i].getRipeness() < ripest.getRipeness()) and self.is_previous_asset(tokens[i]) == False:
                    ripest = tokens[i]
            return ripest
        else:
            pass
    def sell(self,token,amount:int,limit:str)->dict:
        order = self.client.order_limit_sell( symbol=token.pair(), quantity=amount, price=limit)       
        return order
    def buy(self,token,amount:int,limit:str)->dict:
        order = self.client.order_limit_buy( symbol=token.pair(), quantity=amount, price=limit)       
        return order   
    def filled(self,order)->str:
        #if order: return self.client.get_order(symbol=order["symbol"],orderId=order["orderId"])["status"]
        if self.order_update and order['orderId'] == self.order_update['i']:
            return self.order_update['X']
        else: return 'FALSE'
    def changeThreshold(self,threshold):
        self.threshold = threshold
    def manualRank(self):
        print("Input the token of your choice")
        primeToken = Token(input(""))
        print("You selected "+primeToken.name)
        positionType = input("Input the position type you would like (long or short) ")
        orderType = input("Input the order type you would like (market or limit) ")
        return {'token':primeToken,'positionType':positionType,'orderType':orderType}
    def addToken(self):
        token = Token(input())
        tokens.append(token)
        print("Succesfully added to tokens list, "+self.tokens[-1].name)
    def getUSDT(self):
        balance = self.client.get_asset_balance(asset='USDT')
        return float(balance['free'])
    def selling(self,order):
        limit = self.current_asset.getPrice()
        order= self.sell(self.current_asset,self.current_asset.getBalance(),limit)
        print(order)
        orderCount = 1
        counter = 0
        gains_average = 0
        while self.filled(order) != 'FILLED'  :
                time.sleep(2)
                counter += 1
                if counter == 10:
                    self.cancel_order(order)
                    if float(limit)*1.01 < float(primeToken.getPrice()) and self.current_asset.getBalance()*float(self.current_asset.getPrice()) > self.min_notional :
                        limit = self.current_asset.getPrice()
                        order = self.sell(self.current_asset,self.current_asset.getBalance(),limit)
                        counter = 0
                        orderCount += 1
                    else:
                        break
        sell_price = self.current_asset.avgSellPrice(orderCount)
        self.gains += sell_price/self.current_asset.getBuyPrice()
        self.gains -= self.fee
        return True       
    def buying(self,orderMain,primeToken):
        #NEED TO IMPLEMENT SOME FUNCTION TO CHECK IF ALL OUR USDT IS USED UP SO WE DONT HOLD MULTIPLE TOKENS
        #MAYBE IMPLEMENT WAY TO HOLD AND CHECK MULTIPLE TOKENS
        order = orderMain
        starting_balance = self.getUSDT()
        limit = primeToken.getPrice()
        quantity = primeToken.correct_step(float(self.getUSDT())/float(limit))
        order= self.buy(primeToken,quantity, limit )
        orderCount = 1
        counter = 0
        while( self.filled(order) !='FILLED' ):
                time.sleep(2)
                counter += 1
                if counter == 9:
                    self.cancel_order(order)
                    if float(limit)*1.02 > float(primeToken.getPrice()) and self.getUSDT() > self.min_notional :
                        limit = primeToken.getPrice()
                        order = self.buy(primeToken,primeToken.correct_step(self.current_asset.getBalance()/float(limit)),limit)
                        counter = 0
                        orderCount += 1
                    else:
                        break
        primeToken.avgBuyPrice(orderCount)
        print(str(primeToken.getBuyPrice() ) )
        self.current_asset = primeToken
        self.gains -= self.fee
        return True
    def pickleGains(self):
        pickling_on = open("gains.pickle",'wb')
        pickle.dump(self.gains,pickling_on)
        pickling_on.close()  
    def pickleData(self):
        print('Pickling')
        pickling_on = open("data.pickle",'wb')
        pickle.dump(self.data,pickling_on)
        pickling_on.close()
    def pickleTokens(self):
        pass        
    def cancel_order(self,order):
        self.client.cancel_order(symbol=order["symbol"],orderId=order['orderId'])    
    def profit(self):
        return float(self.current_asset.getPrice())/self.current_asset.getBuyPrice()
    def dataTracker(self):
        if datetime.now().second == 59:
            print("iterating through data[]")
            for i in range(len(self.tokens)):
                self.data[i].append( float(self.tokens[i].getPrice() ) )
                self.data[i].remove(self.data[i][0])
                self.tokens[i].set_interval_percentage(  ( self.data[i][ len(self.data[i])-1 ]-self.data[i][0] )/self.data[i][0]       )
                self.tokens[i].setMean(statistics.mean(self.data[i] ) )
                self.tokens[i].setDev(statistics.stdev(self.data[i] ) )
                print("7 day change %: ")
                print(str(self.tokens[i].get_interval_percentage ) )
                print("7 day deviation: " )
                print(str(self.tokens[i].getDev() ) )
                print("7 day mean:")
                print(str(self.tokens[i].getMean() ) )
                self.pickleData()
    
    def spot(self):
        order = {}
        if self.current_asset.name  == 'USDT':
            print("Currently holding USDT")
             #ALGORITHM FOR BUYING GOES IN HERE
            primeToken = self.rank(self.tokens)
            print("The token the algorithm selected is "+primeToken.getName())
            if self.buying(order,primeToken):
                self.previous_asset = self.current_asset
                print("successfully bought")
            else:
                print('Failed to buy at current price')
        else:
            if self.current_asset.name != 'USDT' :
                    print("We are holding "+str(self.current_asset.getBalance())+" in "+self.current_asset.name)
                    while  self.profit() > 1 + self.threshold :  
                        print("Executing order above threshold")
                        if self.selling(order) :
                            print("Sell order executed above threshold")
                            self.previous_asset = self.current_asset
                            self.update_previous_assets(self.current_asset)
                            self.current_asset=Token('USDT')
                            self.pickleGains()
                            break
        if self.current_asset.name != 'USDT':                
                    self.current_asset.printBuyIn()
                    self.current_asset.printPrice()
                    print("Our current return is "+str( (self.profit()-1)*100 )[0:6]+'%' )
                    if  self.profit() < self.alert_threshold :
                        #implement intervention function right here
                        print("ALERT ALERT , WE ARE DOWN 10%, OUR BOT BRAIN EXPLODED, ALL HANDS OVERBOARD, ALERT THE PROGRAMMERS")
    def track(self):
        time.sleep(1)
        print("Tracking tokens")
        self.dataTracker()
        self.spot()
    
class FuturesCustodian(Custodian):
    def __init__(self,tokens):
        super().__init__(tokens)
        self.futures_threshold = .002
        self.futures_min_notional = 5 #10 usdt is minimum notional value for orders
        self.futures_account_info = self.client.futures_account()
        self.mode = 'futures'
        self.defaultLeverage = 10
        self.current_asset = self.assetHeld()
        self.bm = BinanceSocketManager(self.client)
        self.conn_key = self.bm.start_futures_socket(self.process_message)
        self.account_update = {}
        self.order_update = {}
    def process_message(self,msg):
        print(msg)
        if msg['e'] == 'ACCOUNT_UPDATE':
            self.account_update = msg
        if msg['e'] == 'ORDER_TRADE_UPDATE':
            self.order_update = msg
    def futures_filled(self,order):
        #return self.client.futures_get_order(symbol=order['symbol'],orderId=order['orderId'])['status']
        if self.order_update and order['orderId'] == self.order_update['o']['i']:
            return self.order_update['o']['X']
        else: return 'FALSE'
    def futures_getUSDT(self):
        balance = float(self.futures_account_info['assets'][0]['walletBalance'])
        if balance  > self.futures_min_notional:
            print("Balance is "+str(balance))
            return balance
        else: 
            if len(self.futures_account_info['positions']) != 0:
                print("We have positions currently")
            else:
                print("We have 0 USDT")
            return 0
    def assetHeld(self):
        if self.futures_getUSDT() < self.futures_min_notional:
            name = self.futures_account_info['positions']['symbol']
            name = name[0:len(name)-3] #ends at character u in 'usdt'
            current_asset = Token(name)
            current_asset.isPosition = True
            print('Our current asset is a position in '+self.current_asset.name)
            return current_asset
        else:
            return Token('USDT')
    def realizedPNL(self,token,orderCount):
        for trades in self.client.futures_account_trades(symbol=token.pair(),limit=orderCount ):
            realizedPnl += float(trades['realizedPnl'])
        return realizedPnl
    def getPosition(self):
        self.futures_account_info = self.client.futures_account()
        return self.futures_account_info['positions'][0]['positionSide']
    def futures_cancel_order(self,order):
        self.client.futures_cancel_order(symbol=order["symbol"],orderId=order['orderId'])
    def dataTracker(self):
        if datetime.now().second == 59:
            print("iterating through data[]")
            for i in range(len(self.tokens)):
                self.data[i].append( float(self.tokens[i].getPrice() ) )
                self.data[i].remove(self.data[i][0])
                self.tokens[i].set_interval_percentage(  ( self.data[i][ len(self.data[i])-1 ]-self.data[i][0] )/self.data[i][0]       )
                self.tokens[i].setMean(statistics.mean(self.data[i] ) )
                self.tokens[i].setDev(statistics.stdev(self.data[i] ) )
                print("7 day change %: ")
                print(str(self.tokens[i].get_interval_percentage ) )
                print("7 day deviation: " )
                print(str(self.tokens[i].getDev() ) )
                print("7 day mean:")
                print(str(self.tokens[i].getMean() ) )
                self.pickleData()
                time.sleep(4)
    def futures_profit(self):
        return float(self.current_asset.markPrice)/self.current_asset.get_futures_entry_price()
    def closePosition(self,token,orderType,positionType):
        if positionType == 'short':
            order = self.enterLong(token,orderType)
            return order
        if positionType == 'long':
            order = self.enterShort(token,orderType)
            return order
    def enterPosition(self,token,orderType,positionType):
        if positionType == 'long':
            order = self.enterLong(token,orderType)
            print("Entering long position...")
            return order
        if positionType == 'short':
            order = self.enterShort(token,orderType)
            print("Entering short position...")
            return order
    def changeLeverage(self,token,leverageLevel):
        order = self.client.futures_change_leverage(symbol=token.pair(),leverage=leverageLevel)
        return order
    def enterLong(self,token,orderType):
        if orderType == 'limit':
            self.changeLeverage(token,self.defaultLeverage) #make sure leverage is set at 10
            useable_balance = self.futures_getUSDT()*(1- (1/self.defaultLeverage))
            limit = token.markPrice
            amount =  token.correct_step(self.defaultLeverage*useable_balance/float(limit))
            print(amount)
            order = self.client.futures_create_order(symbol=token.pair(),side='BUY', type='LIMIT', quantity = amount, timeInForce='GTC',price=limit)
            return order
        else:
            self.changeLeverage(token,self.defaultLeverage)
            useable_balance = self.futures_getUSDT()*(1- (1/self.defaultLeverage))
            amount =  token.correct_step(self.defaultLeverage*useable_balance/float(token.markPrice))
            order = self.client.futures_create_order(symbol=token.pair(),side='BUY', type='MARKET', 
            quantity = amount)
            return order
    def enterShort(self,token,orderType):
        if orderType == 'limit':
            self.changeLeverage(token,self.defaultLeverage) #make sure leverage is set at 10
            useable_balance = self.futures_getUSDT()*(1- (1/self.defaultLeverage))
            limit = token.markPrice
            amount =  token.correct_step(self.defaultLeverage*useable_balance/float(token.markPrice) )
            print("Order amount is "+str(amount))
            order = self.client.futures_create_order(symbol=token.pair(),side='SELL', type='LIMIT', 
            quantity = amount, timeInForce='GTC',price=limit)
            return order
        else:
            self.changeLeverage(token,self.defaultLeverage)
            useable_balance = self.futures_getUSDT()*(1- (1/self.defaultLeverage))
            amount =  token.correct_step(self.defaultLeverage*useable_balance/float(token.markPrice) )
            order = self.client.futures_create_order(symbol=token.pair(),side='SELL', type='MARKET', 
            quantity = amount)
            return order
    def buyingFutures(self,order,primeToken,orderType,positionType):
        #NEED TO IMPLEMENT SOME FUNCTION TO CHECK IF ALL OUR USDT IS USED UP SO WE DONT HOLD MULTIPLE TOKENS
        order = self.enterPosition(primeToken,orderType,positionType)
        orderCount = 1
        counter = 0
        limit = float(primeToken.markPrice)
        while self.futures_filled(order) != 'FILLED' :
                time.sleep(1)
                counter += 1
                if counter == 9:
                    print("30 seconds passed, order not filled, canceling")
                    self.futures_cancel_order(order)
                    if limit*1.01 > float(primeToken.markPrice) and self.futures_getUSDT() > self.futures_min_notional :
                            order = self.enterPosition(primeToken,orderType,positionType)
                            counter = 0
                            orderCount += 1
                    else:
                        break
        if orderType == 'limit' :   
            primeToken.futures_avgBuyPrice(orderCount)
            print(str(primeToken.futures_entry_price) )
        else:
            print(str(primeToken.get_futures_entry_price() ) )
        print("Successfully bought")
        self.current_asset = primeToken
        self.gains -= self.fee
        return True
    def sellingFutures(self,order,orderType,positionType):
        order = self.closePosition(self.current_asset,orderType,positionType)
        orderCount = 1
        counter = 0
        limit = float(primeToken.markPrice)
        while self.futures_filled(order) != 'FILLED':
                time.sleep(1)
                counter += 1
                if counter == 9:
                    print("30 seconds passed, order not filled, canceling")
                    self.futures_cancel_order(order)
                    if limit*1.01 > float(primeToken.markPrice) and self.futures_getUSDT() > self.futures_min_notional :
                        order = self.closePosition(self.current_asset,orderType,positionType)
                        counter = 0
                        orderCount += 1
                    else:
                        break
        if orderType == 'limit' :   
            primeToken.futures_avgSellPrice(orderCount)
            print(str(primeToken.futures_exit_price) )
        else:
            print(str(primeToken.get_futures_exit_price() ) )
        print("Successfully bought")
        self.current_asset = Token('USDT')
        self.gains_USDT += self.realizedPNL(primeToken)
        return True
    def futures(self):
        order = {}
        primeToken = Token('USDT')
        positionType = ''
        orderType = ''
        if self.current_asset.name  == 'USDT':
            print("Currently holding USDT")
            if self.automated:
                primeToken = self.rank(self.tokens)
            else:
                choices = self.manualRank()
                primeToken = choices['token']
                positionType = choices['positionType']
                orderType = choices['orderType']
            print("The token the algorithm selected is "+primeToken.getName())
            if self.buyingFutures(order,primeToken,orderType,positionType):
                print("successfully bought")
            else:
                print('Failed to buy at current price')
        else:
            if self.current_asset.name != 'USDT' :
                    self.current_asset.printBalance()
                    while  self.futures_profit() > 1 + self.threshold :  
                        print("Executing order above threshold")
                        if self.sellingFutures('limit',self.getPosition()) :
                            print("Sell order executed above threshold")
                            self.previous_asset = self.current_asset
                            self.previous_assets(self.current_asset)
                            self.current_asset=Token('USDT')
                            self.pickleGains()
                            break                 
        print("Our current return is "+ str( (self.futures_profit()-1)*100 )[0:6]+'%' )
        print("Gains in USDT are "+str(self.gains_USDT))
        self.current_asset.printMarkPrice()
        self.current_asset.printFuturesEntryPrice()
        if  self.futures_profit() < self.alert_threshold and self.current_asset.name != 'USDT':
                 #implement intervention function right here
                print("ALERT ALERT , WE ARE DOWN 10%, OUR BOT BRAIN EXPLODED, ALL HANDS OVERBOARD, ALERT THE PROGRAMMERS")
    def track(self):
        self.futures()
        





         
 