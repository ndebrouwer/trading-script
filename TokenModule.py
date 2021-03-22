import logging
import time
import threading
import os
from datetime import datetime
import binance
#for the API key
#for the order functions
from binance.enums import *
from binance.client import Client
from Key import *
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

class Token:
    client = Client(api_key, api_secret)
    def __init__(self, name):
        if name != 'USDT' and name != '' and name != 'CURRENT_ASSET' and name != 'PREVIOUS_ASSET' and name != 'DUMMY':
            self.bm = BinanceSocketManager(self.client)
            # start any sockets here, i.e a trade socket
            # then start the socket manager
            self.name = name
            self.buy_in = 0
            self.mean = 0
            self.dev = 0
            self.normDev = 0
            #the fruit is ready to be plucked
            self.ripeness = 0
            self.orders = []
            self.info = self.client.get_symbol_info(symbol=self.pair())
            self.price = self.client.get_symbol_ticker(symbol=self.pair())['price']
            self.stepsize = self.info["filters"][2]["stepSize"]
            self.stepSizeIndex = self.stepsize.index('1')
            self.ticksize = self.info['filters'][0]['tickSize']
            self.tickSizeIndex = self.ticksize.index('1')
            self.priceIndex = self.price.index('.')
            self.price = self.correctPrice()
            print(self.name+' Token Object instantiated')
            print(self.price)
            self.trade = []
            self.conn_key = self.bm.start_trade_socket(self.pair(), self.process_message)
            self.bm.start()
            self.flag = '' #set to bull or bear
            self.interval_percentage = 0
            self.time_to_deviate = 0
            self.max = 0
            self.min = 0
        else: 
              self.name = name
    def correctPrice(self) -> float:
        return self.price[0:self.priceIndex+self.tickSizeIndex-2+1]
    def correct_tick(self,number)->float:
        str_number = str(number)
        index = str_number.index('.')
        return float(str_number[0:index+self.tickSizeIndex-2+1])
    def correct_step(self,number)->float:
        if type(number)==float:
            str_number = str(number)
            index = str_number.index('.')
            return float(str_number[0:index+self.stepSizeIndex-2+1] )
        if type(number)==str:
            index = number.index('.')
            return float(number[0:index+self.stepSizeIndex-2+1] )
    def avgBuyPrice(self,orderCount):
        recent_trades = self.client.get_my_trades(symbol=self.pair(),limit=orderCount)
        Qty = 0
        buy_price = 0
        for trade in recent_trades:
            Qty += float(trade['qty'])
            buy_price += float(trade['price'])*float(trade['qty'])
        buy_price /= Qty
        self.setBuyIn(buy_price)
    def avgSellPrice(self,orderCount):
        recent_trades = self.client.get_my_trades(symbol=self.pair(),limit=orderCount)
        Qty = 0
        sell_price = 0
        for trade in recent_trades:
            Qty += float(trade['qty'])
            sell_price += float(trade['price'])*float(trade['qty'])
        sell_price /= Qty
        return sell_price

    def process_message(self,msg):
        self.trade = msg
         #print(self.ticker)
        self.price = self.trade['p']
        self.price = self.correctPrice()
        # do something
    def getPrice(self):
         #if self.trade:
            #self.price = self.trade['p']
             #self.price = self.price[0:self.price.index('.')+4]
         #self.price = self.price[0:self.price.index('.')+4]
        return self.price
    def stopWS(self):
        self.bm.close()
        reactor.stop()
        print("Socket was stopped")
    def startWS(self):
        self.bm.start()
        print("Socket was started")
    def get1m(self):
        return self.client.get_historical_klines(symbol=self.pair(),interval='1m',start_str='1 minute ago')
    def pair(self):
        return self.name+'USDT'
    def get7days(self):
        return self.client.get_historical_klines(symbol=self.pair(),interval='1m',start_str='7 days ago, UTC',end_str='0 hours ago, UTC')
    def getBuyPrice(self):
        if self.buy_in == 0:
            print("Custodian was paused, retrieving purchase price from exchange")
            self.buy_in = float(self.client.get_my_trades(symbol=self.pair(),limit=1)[0]['price'])
        return self.buy_in
    def getName(self):
        return self.name
    def buy_in(self,order):
        self.buy_in = float(order["price"])
    def setBuyIn(self,buy_in):
        self.buy_in = buy_in
    def getBalance(self):
        balance = self.client.get_asset_balance(asset=self.name)
        if balance and self.name != 'USDT':
            return self.correct_step(float(balance['free'] ) )
        else:
            if balance and self.name == 'USDT': return float(balance['free'])
    def stats(self,prices):
        self.dev = statistics.stdev(prices)
        self.mean = statistics.mean(prices)
        self.normDev = self(dev / mean)
        return (self.mean, self.dev)
    def getMean(self):
        return self.mean
    def setMean(self,mean):
        self.mean = self.correct_tick(mean)
    def getDev(self):
        return self.dev
    def setDev(self,dev):
        self.dev = self.correct_tick(dev)
    def normDev(self,):
        return self.normDev
    def setRipeness(self,ripeness):
       self.ripeness = ripeness
    def getRipeness(self):
        return self.ripeness
    def addOrder(self,order):
        self.orders.append(order)
    def getStepSizeIndex(self):
        return self.stepSizeIndex
    def setFlag(self,flag):
        self.flag = flag
    def getFlag(self):
        return self.flag
    def set_interval_percentage(self,interval_percentage):
        self.interval_percentage = interval_percentage
    def get_interval_percentage(self):
        return self.interval_percentage
    def get_time_to_deviate(self):
        return self.time_to_deviate
    def set_time_deviate(self,time_to_deviate):
        self.time_to_deviate = time_to_deviate
    def setMax(self,max):
        self.max = max
    def setMin(self,min):
        self.min = min
    def getMin(self):
        return self.min
    def getMax(self):
        return self.max

class USDT(Token):
    def __init__(self,name):
        self.name = name
    def getBalance(self):
        return Token.correct_step(float(self.client.get_asset_balance(asset=self.name)['free']) )

