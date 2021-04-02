from CustodianModule import Custodian
from TokenModule import Token
from datetime import datetime
import time
 #the purpose of this program is assist me in visualizing the %change in prices in the past 5 hours of a list of assets, 
 #for now the list is intended to be possible coinbase-listable tokens, run on tuesday morning's 
if True:
    names = ['ALGO','GRT','ETH','BTC','ADA','MATIC']
    tokens = []
    for i in names:
        tokens.append(Token(i) )
    Custos = Custodian(tokens)
    priceData = Custos.CustomFillAndStripData("5 hours ago, UTC","0 hours ago, UTC") #intended to run this program every tuesday at 6 am for coinbase
    intervalHourLength = 5 #hours
    intervalLength = intervalHourLength*60
    priorityInterval = 5 #minutes
    intervalFrequency = 60 #minutes
    def dataTracker(self):
        pass    
    while True:
        if datetime.now().second%15 == 0:
            print("Starting calculations")
            for i in range(len(Custos.tokens)):
                Custos.data[i].append( float(Custos.tokens[i].getPrice() ) )
                Custos.data[i].remove(Custos.data[i][0])
                priceData = Custos.data
                print(Custos.tokens[i].pair()+" hourly percent change data:")
                hourly_change_list = []
                for hourIndex in range(0,intervalHourLength):
                    percent_change = 100*(priceData[i][(intervalFrequency*(hourIndex+1))-1]-priceData[i][intervalFrequency*hourIndex ] )/priceData[i][intervalFrequency*hourIndex]
                    if hourIndex == intervalHourLength-1 and percent_change > 5:
                        print(Custos.tokens[i].pair()+" had a 5 percent change in the last hour")
                    percent_change = str(percent_change)[0:5]
                    hourly_change_list.append(str(percent_change)+'%')
                print(hourly_change_list)
                print("5 min percent change:")
                five_min_change = 100*(priceData[i][intervalLength-1]-priceData[i][intervalLength-priorityInterval])/priceData[i][intervalLength-priorityInterval]
                five_min_change = str(five_min_change)[0:5]
                print(str( five_min_change )+'%'  )
                time.sleep(2)                             

