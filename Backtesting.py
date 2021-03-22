import logging
import time
import threading
import os
from datetime import datetime
import binance
#for the API key
from Key import *
#for the order functions
from binance.enums import *
from twisted.internet import reactor

import statistics
import ssl, smtplib

#get and initalise binance client using api keys (this cant withdraw yet , not enabled too)
#we can use the client to execute trades and call data, but since we already have the websocket for now we wont call data
from binance.client import Client
client = Client(api_key, api_secret)
switch = False 
tokens = ['ALGO','GRT','INJ','XLM','ETH','BTC','ADA']
switch1 = False
switch2 = True
m = 480
threshold = .01
master = []
from binance.websockets import BinanceSocketManager
from TokenModule import Token

ticker = []
price = 0

def getTicker(token):
    return client.get_ticker(symbol=token)
def pair(token):
    return token+'USDT'

def getPastPrice(token):
        #returns the close of the interval for the product
        return client.get_historical_klines(symbol=pair(token), interval = '1m', start_str = '1 week ago, UTC' , end_str = "0 weeks ago, UTC"  )
def getPastPrice1(token, beginning='',end=''):
        #returns the close of the interval for the product
        return client.get_historical_klines(symbol=pair(token), interval = '1m', start_str = beginning , end_str = end  )


def TradesToPrices(Trades:list):
    prices = []
    for i in Trades:
        prices.append(float(i[1]))
        print("appending data")
    return prices


def rank(tokens:list, prices:list):
    pass
gains = 0
buy_in = 0
current_asset = 'USDT'
previous_asset = ''
primeIndex = 0
buyinIndex = 0
if switch:
    for i in tokens:
        master.append(TradesToPrices(getPastPrice(i)))
        print("Finished data for "+i)
    print(len(master[-1]))
time.sleep(10)
if switch:
    for i in range(m,len(master[-1]) ):
        if current_asset == 'USDT':
            prime = 100000000
            currentPrime = 0
            index = 0
            for j in master:
                
                
                k = i-m
                slicedList = j[k:i] 
                dataTuple = stats(slicedList)
                mean = dataTuple[0]
                threshold = dataTuple[1]                
                #^reset std dev if volatility too high
                #z score for if price will go up by threshold at current price
                #higher z score = less probability of going up
                z = ( j[i]+(mean*.01)-mean )/threshold
                currentPrime = z
                if min(currentPrime,prime) == currentPrime and currentPrime != previous_asset:
                    prime = currentPrime
                    buy_in = j[i]
                    primetoken = tokens[master.index(j)]
                    primeIndex = master.index(j)
                    current_asset = primetoken
            dataTuple = stats(master[primeIndex][i-480:i])
            mean = dataTuple[0]
            threshold = dataTuple[1]
            buy_in = master[primeIndex][i]
                
            print("The prime token was selected to be "+primetoken)
            print("Current asset is "+current_asset)
            print("The prime index is "+str(primeIndex))
            print("The buy in price for the current asset was "+str(buy_in))
        if current_asset != 'USDT' and master[primeIndex][i]/buy_in >= (1+.01 ) :
            gains += master[primeIndex][i]/buy_in -.001-.001-1
            print("Sold current asset for a profit! Gains are currently"+str(gains*100)[0:5])
            previous_asset = current_asset
            current_asset = 'USDT'
    print("The final profit after a week was "+str(gains*100)+" percent" )
    print("Time period here was "+str(4320)+"to "+str(len(master[-1])))
if os.stat("backtesting_data.pickle").st_size == 0:
    if switch:
    for i in tokens:
        master.append(TradesToPrices(getPastPrice(i)))
        print("Finished data for "+i)
    print(len(master[-1]))
    time.sleep(10)
    pickling_on = open("data.pickle",'wb')
    pickle.dump(self.data,pickling_on)
    pickling_on.close()  
else:
    pickling_off = open("backtesting_data.pickle",'rb')
    pickle.load(master,pickling_off)
                


    



#get_past_ticker(ALGOTrades)

    
    
 #print(statistics.mean(prices) )
 #print(statistics.pstdev(prices) )
 #first get a weeks worth of data, get the cycle over the week


        
        



        




    

    
    