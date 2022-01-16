
from cmath import nan
import websocket
import json
import numpy as np
import talib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()    
mensajes=[
 
  
]
mensaje= {
  "correo":float,
  "nombre":float,
  "telefono":float,
  "id":int,
  "leido":False
}



class Strategy():
  def __init__(self):
    
        
    self.cc = 'btcusd'
    self.interval = '1m'

    self.socket = f'wss://stream.binance.com:9443/ws/{self.cc}t@kline_{self.interval}'

    # Trading Strategy Parameters
    self.aroon_time_period = 2

    self.amount = 1000
    self.core_trade_amount = self.amount*0.80
    self.core_quantity = 0
    self.trade_amount = self.amount*0.20
    self.core_to_trade = True

    self.portfolio = 0
    self.investment, self.real_time_portfolio_value, self.closes, self.highs, self.lows = [], [], [], [], []
    self.money_end = self.amount
    
    ws = websocket.WebSocketApp(self.socket, on_message= self.on_message, on_close=self.on_close)

    ws.run_forever()    

  # Buying and Selling functions

  def buy(self,allocated_money, price):
      
    quantity = allocated_money/price
    self.money_end -= quantity*price
    self.portfolio += quantity
    if self.investment == []:
      self.investment.append(allocated_money)
    else:
      self.investment.append(allocated_money)
      self.investment[-1] += self.investment[-2]

  def sell(self, allocated_money, price):
      
    quantity = allocated_money / price
    self.money_end += allocated_money
    self.portfolio -= quantity
    self.investment.append(-allocated_money)
    self.investment[-1] += self.investment[-2]
    
  # Bitcoin Bot

  def on_close(self,ws):
    port_value = self.portfolio*self.closes[-1]
    if port_value > 0:
      self.sell(port_value,price = self.closes[-1])
    else:
      self.buy(-port_value, price = self.closes[-1])
    self.money_end += self.investment[-1]
    print('All trades settled')

  def on_message(self,ws,message):
    
    json_message = json.loads(message)
    cs = json_message['k']
    candle_closed, close, high, low = cs['x'], cs['c'], cs['h'], cs['l']

    if candle_closed:
      self.closes.append(float(close))
      self.highs.append(float(high))
      self.lows.append(float(low))
      last_price = self.closes[-1]
      print(f'Closes: {self.closes}')
      mensaje['nombre']=self.closes[-1]
      
      
                              
    
      if self.core_to_trade:
        self.buy(self.core_trade_amount, price=self.closes[-1])
        print(f'Core Investment: We bought ${self.core_trade_amount} worth of bitcoin', '\n')
        self.core_quantity += self.core_trade_amount/self.closes[-1]
        core_to_trade = False

      aroon = talib.AROONOSC(np.array(self.highs), np.array(self.lows), self.aroon_time_period)
      last_aroon = round(aroon[-1],2)
      amt = last_aroon * self.trade_amount / 100
      port_value = self.portfolio * last_price - self.core_quantity*last_price
      trade_amt = amt - port_value
      RT_portfolio_value = self.money_end + port_value + self.core_quantity*last_price
      self.real_time_portfolio_value.append(float(RT_portfolio_value))
      print(f'The Last Aroon is "{last_aroon}" and recommended exposure is "${amt}"')
      print(f'Real-Time Portfolio Value: ${RT_portfolio_value}', '\n')
      mensaje['correo'] = (round(RT_portfolio_value-1000,2))
          
      if trade_amt > 0:
        self.buy(trade_amt, price=last_price)
        print(f'We bought ${trade_amt} worth of bitcoin', '\n', '\n')
        mensaje['telefono']= (round(trade_amt,2))
      elif trade_amt < 0:
        self.sell(-trade_amt, price=last_price)
        print(f'We sold ${-trade_amt} worth of bitcoin', '\n', '\n')
        mensaje['telefono'] = (round(trade_amt),2)
    
       
      
      
        
      docs = db.collection('usuarios').where("cantM", ">", 0).get()
      for doc in docs:
        mensajes =((doc.to_dict()['mensajes']))
        mensaje['id'] = doc.to_dict()['cantM'] +1 
        mensajes.append(mensaje)

    
        db.collection('usuarios').document("ldMsmEagn2qDQLhoMX8q").update({
        "mensajes": mensajes,
        "cantM": mensaje['id']+1
        })
        

if __name__ == "__main__": 
  ws = Strategy()