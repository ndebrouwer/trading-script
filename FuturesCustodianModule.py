from CustodianModule import Custodian

class FuturesCustodian(Custodian):
    def __init__(self,tokens):
        super().__init__(tokens)
        self.futures_threshold = .002
        self.futures_min_notional = 5 #10 usdt is minimum notional value for orders
        self.futures_account_info = self.client.futures_account()
        self.mode = 'futures'
        self.defaultLeverage = 2
        self.marginRatio = 1/self.defaultLeverage
        self.current_asset = self.assetHeld()
        self.bm = BinanceSocketManager(self.client)
        self.conn_key = self.bm.
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
            print(name)
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
        if self.order_update and self.order_update['o']['i'] == order['orderId']:
            self.client.futures_cancel_order(symbol=self.order_update["s"],orderId=self.order_updater['o']['i'])
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
            amount =  token.correct_step( self.defaultLeverage*(1-self.marginRatio)*useable_balance/float(limit))
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
            amount =  token.correct_step(self.defaultLeverage*(1-self.marginRatio)*useable_balance/float(token.markPrice) )
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