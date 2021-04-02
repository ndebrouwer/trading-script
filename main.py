from CustodianModule import Custodian
from CustodianModule import FuturesCustodian
from TokenModule import Token

#DOESNT TAKE XXX/USD PAIRS, ONLY XXX/USDT XXX/BTC, XXX/ETH, ETC. JUST A NOTE TO AVOID API ERROR
#test loop
if __name__ == "__main__":
  names = ['ALGO','GRT','ETH','BTC','ADA','MATIC']
  tokens = []
  for i in names:
    tokens.append(Token(i) )
  Custos = FuturesCustodian(tokens)
   #Custos.initalizeData()
  while Custos.switch:
    Custos.track()
    

        
        



        




    

    
    