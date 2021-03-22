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
#get and initalise binance client using api keys (this cant withdraw yet , not enabled too)
#we can use the client to execute trades and call data, but since we already have the websocket for now we wont call data

class Custodian:
    def __init__(self,tokens):
        self.client =  Client(api_key, api_secret)
        self.switch = True
        self.tokens = tokens #token list
        #orders master list for all the currencies' buy ins, doesnt log sells
        self.current_asset = self.assetHeld()
        self.previous_asset = ''
        self.current_assets = []
        self.gains = self.getGains()
        self.threshold = .01
        self.alert_threshold = .9
        self.divisor = .5
        self.data = []
        self.fee = .001
        self.m = 10080 #minute time interval over which we look at data
         #get 3 days of price data per token when Custodian is instantiated
        self.previous_asset = ''
        self.market = 'bull'
        self.last_4_tokens = []
    def getGains(self):
        gains = 0
        if os.stat("gains.pickle").st_size != 0:
            pickle_off = open("gains.pickle", 'rb')
            gains = pickle.load(pickle_off)
            pickle_off.close()
        return gains
    def assetHeld(self):
        if self.getUSDT() < 1:
            for asset in self.client.get_account()["balances"]:
                if float(asset["free"]) >  1 or float(asset["locked"]) > 1:
                    return Token(asset["asset"])
    def log_asset_prices(self):
        if datetime.now().timetuple().tm_sec == 61:
            for token in self.tokens:
                logging.basicConfig(filename=token.name+'.txt', level=logging.INFO, encoding =None,format='%(message)s')
                logging.info(token.getPrice())
    def initalizeData(self):
        if os.stat("data.pickle").st_size == 0:
            print("Calling data from client")    
            for i in self.tokens:
                self.data.append(i.get7days())
                dummydata = self.data
                for j in dummydata[-1]:
                    k = dummydata[-1].index(j)
                    self.data[-1][k] = float( (j[1]) ) 
                i.setMean( statistics.mean(self.data[-1]) )
                i.setDev(statistics.stdev(self.data[-1] ) )
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
    def previous_assets(self,token):
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
                if(tokens[i].getRipeness() < ripest.getRipeness()) and self.is_previous_asset() == False:
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
        if order: return self.client.get_order(symbol=order["symbol"],orderId=order["orderId"])["status"]
    def changeThreshold(self,threshold):
        self.threshold = threshold
    def manualOverride(self):
         #MUST IMPROVE
        token = Token(input())
        if(self.current_asset.name == 'USDT'):
            #set holding cash true so next body of logic doesnt execute, and buy into the desired token
            #this will be rare, most of the time well be holding a crypto
            buy_order = buy(token,current_asset.getBalance(),token.getPrice())
            if bought(buy_order):
               self.gains -= fee
               self.current_asset=token

         #implement here to check if the manual override is worth it, how down we are, etc.
        if self.current_asset.name !='USDT' :
            print("current gains are "+self.gains+'%'+'in '+self.current_asset.name())
            print("Are you sure you would like to manually override and convert to "+token)
             #get input for Y here
            confirmation = input()
             #use execute order to ensure order execution, then swap from USDT to token
            order = sell(self.current_asset,self.current_asset.getBalance(),self.current_asset.getPrice())
        if sold(order):
                updateGains(order)
                order = buy(token,self.current_asset.getBalance(),token.getPrice())
                if bought(order):
                    self.gains -= fee
                    self.current_asset=token
        else:
            return 'iterated sell order at limit of current price failed to execute'
    def addToken(self):
        token = Token(input())
        tokens.append(token)
        print("Succesfully added to tokens list, "+self.tokens[-1].name)
    def getUSDT(self):
        return float(self.client.get_asset_balance(asset='USDT')['locked'])
    def selling(self,order):
        starting_balance = self.current_asset.getBalance()
        limit = self.current_asset.getPrice()
        order= self.sell(self.current_asset,self.current_asset.getBalance(),limit)
        print('Limit type is '+str(type(limit) ))
        print(str(limit))
        orderCount = 1
        counter = 0
        gains_average = 0

        while( self.filled(order) != 'FILLED' and self.current_asset.getBalance()*float(self.current_asset.getPrice()) > 10 ):
                time.sleep(10)
                counter += 1
                if counter == 10:
                       if self.filled(order) !='FILLED':
                            self.cancel_order(order)
                            if float(limit)*1.01 < float(primeToken.getPrice()) :
                                limit = self.current_asset.getPrice()
                                order = self.sell(self.current_asset,self.current_asset.getBalance(),limit)
                                counter = 0
                                orderCount += 1
                            else:
                                return False
        sell_price = self.current_asset.avgSellPrice(orderCount)
        self.gains += sell_price/self.current_asset.getBuyPrice()
        self.gains -= self.fee
        return True
    def buying(self,order,primeToken):
        #NEED TO IMPLEMENT SOME FUNCTION TO CHECK IF ALL OUR USDT IS USED UP SO WE DONT HOLD MULTIPLE TOKENS
        #MAYBE IMPLEMENT WAY TO HOLD AND CHECK MULTIPLE TOKENS
        starting_balance = self.current_asset.getBalance()
        print(str(starting_balance))
        print("step size for the pair here is"+str(primeToken.stepsize) )
        limit = primeToken.getPrice()
        quantity = primeToken.correct_step(float(starting_balance)/float(limit))
        order= self.buy(primeToken,quantity, limit ) 
        print('Limit type is'+str(type(limit))  )
        print(limit)
        print("quantity is")
        print(str(quantity))
        orderCount = 1
        counter = 0
        while( self.getUSDT() > 10):
                time.sleep(5)
                counter += 1
                if counter == 9:
                       if self.filled(order) !='FILLED' and self.getUSDT() > 10 :
                            self.cancel_order(order)
                            if float(limit)*1.02 > float(primeToken.getPrice()) :
                                limit = primeToken.getPrice()
                                order = self.buy(primeToken,primeToken.correct_step(self.current_asset.getBalance()*float(limit)),limit)
                                counter = 0
                                orderCount += 1
                            else:
                                return False
        primeToken.avgBuyPrice(orderCount)
        print(str(primeToken.getBuyPrice() ) )
        self.current_asset = primeToken
        self.gains -= self.fee
        return True
    def executedQty(self,order):
        return float(self.client.get_order(order['orderId'])['executedQty'])
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
    def track(self):
        print("Tracking tokens")
        order = {}
        self.dataTracker()
        start_time = time.time()
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
                            self.previous_assets(self.current_asset)
                            self.current_asset=Token('USDT')
                            self.pickleGains()
                            break                 
        if self.filled(order)==False :
                print("order failed to execute above threshold and/or price dipped/was below profit threshold")
        print("Our current return is "+ str( (self.profit()-1)*100 )[0:6]+'%' )
        print("Buy in price was "+str(self.current_asset.getBuyPrice() ) )
        print("Current price is "+str(self.current_asset.getPrice() ) )
        print("Profit is "+str(float(self.current_asset.getPrice())/self.current_asset.getBuyPrice() ) )
        if  self.profit() < self.alert_threshold and self.current_asset.name != 'USDT':
                 #implement intervention function right here
                print("ALERT ALERT , WE ARE DOWN 10%, OUR BOT BRAIN EXPLODED, ALL HANDS OVERBOARD, ALERT THE PROGRAMMERS")
        if self.current_asset.name == 'CURRENT_ASSET':
            print("Not enough funds were deposited to trigger trackign")
        end_time = time.time()
        print(end_time - start_time, "seconds")
        print('${gains}')



         
 