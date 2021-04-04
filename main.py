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
  #mode = 'spot'
  Custos = Custodian(tokens)
  mode = input("Do you want to do spot trading or futures trading? Enter spot or futures ")
  if mode == 'futures':
    Custos = FuturesCustodian(tokens)
  if mode == 'spot':
    Custos = Custodian(tokens)
  Custos.initalizeData()
  while Custos.switch:
    Custos.track()
    

        
        



        




    

    
    