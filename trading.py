from binance import Client
import time
from halo import Halo
import sys


KEY='Yourkey'
SECRET= 'Yoursecret'
client = Client(KEY,SECRET)

class Binance():
    def __init__(self, KEY, SECRET):
        self.client = Client(KEY, SECRET)
    def spot_balance(self,symbol):
        return float(self.client.get_asset_balance(asset=symbol)['free'])
    
    def get_ask(self,symbol):
         return float(self.client.get_order_book(symbol=symbol)["asks"][0][0])
    
    def get_bid(self,symbol):
         return float(self.client.get_order_book(symbol=symbol)["bids"][0][0])
    def get_future_ask(self,symbol):
         return float(self.client.futures_coin_order_book(symbol=symbol)["asks"][0][0])

    def get_trade_price(self,symbol,order_id):
        order_info = client.get_all_orders(symbol=symbol, orderId=order_id)[0]
        # Extract relevant information
        executed_qty = float(order_info['executedQty'])
        cumulative_quote_qty = float(order_info['cummulativeQuoteQty'])
        # Calculate average price
        average_price = cumulative_quote_qty / executed_qty
        return average_price
    
    def get_future_balance(self,symbol):
        balance=client.futures_coin_account_balance()
        for asset in balance:
            if asset['asset']==symbol:
                return float(asset['balance'])
        return 0
        
             

    def get_future_position(self,symbol):
         position=client.futures_coin_position_information()
         for ticker in position:
              if ticker['symbol']==symbol:
                   return float(ticker['positionAmt'])
         return 0

    def get_future_trade_price(self,symbol,order_id):
        order_info = client.futures_coin_get_order(symbol=symbol, orderId=order_id)

        average_price = float(order_info['avgPrice'])
        return average_price
    def exe_qty(self,symbol,order_id):
              o=client.get_order(symbol=symbol,orderId=order_id)
              if float(o['origQty'])-float(o['executedQty'])==float(o['origQty']):
                   return 0
              else:
                   return float(o['executedQty']) 
    def cancel_order(self,symbol,orderId):
         self.client.cancel_order(symbol=symbol,orderId=orderId)
    def order_mkt_spot(self,side,symbol,q):
        order = self.client.create_order(
        symbol=symbol,
        side=side,
        type='MARKET',
        quantity=q)
        #timeInForce='GTC',
        #price=p)
        print(order)
        return order
    
    def order_spot(self,side,symbol,q,p):
        order = self.client.create_order(
        symbol=symbol,
        side= side,
        type='LIMIT',
        quantity=q,
        timeInForce='GTC',
        price=p)
        return order

    def order_mkt_future(self,side,q,symbol):
            order=self.client.futures_coin_create_order(
            symbol=symbol,#'ETHUSD_231229',
            quantity=q,
            type="MARKET",
            side=side)
            return order

    def order_mkt_margin(self,side,symbol,q):
        order = self.client.create_margin_order(
        symbol=symbol,
        side=side,
        type='MARKET',
        quantity=q)
        return order
    def create_loan(self,symbol,q):
       transaction = self.client.create_margin_loan(asset=symbol, amount=q)
       return transaction

    def repay_loan(self,symbol,q):
        transaction = self.client.repay_margin_loan(asset=symbol, amount=q)
        return transaction
    def transfer(self,symbol,q,type):
        transaction = self.client.futures_account_transfer(asset=symbol, amount=q,type=type)
        return transaction
    def LTprice(self,symbol):
        return float(self.client.get_klines(symbol=symbol, interval='30m')[-1][3])
    def margin_risk(self):
        print('margin level: ' + self.client.get_margin_account()['marginLevel'])
    def max_margin_transfer(self,symbol):
        print(self.client.get_max_margin_transfer(asset=symbol))








class SporvsFuture():
    def __init__(self,q,clipA,symbolA,futsymbolA,price,hold_spot):
          self.q=q #Total quantity
          self.clipA=clipA #Clip order, how big do you want each order to be
          self.symbolA=symbolA #"XRPUSDT"
          self.fut_symbolA=futsymbolA #'XRPUSD_231229' -> Is set for just 10usd futers contract (NOT BTC)
          self.hold_spot=hold_spot #Hold spot False = no symbolA in account
          self.price=price #Target price difference between spot and future
    def get_price(self,symbol,fut_symbol):
         difference= B.get_future_ask(symbol=fut_symbol) - B.get_bid(symbol=symbol)
         return round(difference,4)
    def check_price(self,symbol,fut_symbol):
         #Check price is ok for trading
         difference= self.get_price(symbol,fut_symbol)
         if difference>self.price:
              return True
         else:
              return False
    def get_decimals(self):
         #Know presicion of the spot asset
         exchange_info = client.get_exchange_info()
         symbol_info = next(item for item in exchange_info['symbols'] if item['symbol'] == self.symbolA)
         decimals=len(str(float(symbol_info['filters'][1]['minQty'])))-2
         if symbol_info['filters'][1]['minQty'][0]!=0:
              decimals=0
         return decimals
    
    def conversion_USDTtoQ(self,symbol,amount,decimals):
         current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
         q=amount/current_price
         return round(q,decimals)


    def check_trade_price(self,order_id,fut_order_id):
         #Check price of the trade
         trade_price=B.get_future_trade_price(self.fut_symbolA,fut_order_id)-B.get_trade_price(self.symbolA,order_id)
         print("-------------------------------  Trade price: @ %s  -----------------------------"%trade_price)
         if trade_price>self.price:
              return True
         else:
              return False
    def initial_balance(self):
         #Calculates initial balances
         initial_spot=B.spot_balance(self.symbolA[:-4])
         initial_future_balance=B.get_future_balance(self.symbolA[:-4])
         initial_position=B.get_future_position(self.fut_symbolA)
         return [initial_spot,initial_future_balance,initial_position]

    def check_hedge(self,initial_balance):
         #calculates difference between futures position and future balance (minus initial balance)
         spot=B.spot_balance(st.symbolA[:-4])
         future_balance=(B.get_future_balance(self.symbolA[:-4])-initial_balance[0]-initial_balance[1]+spot)*B.get_bid(symbol=self.symbolA)
         position=(B.get_future_position(self.fut_symbolA)-initial_balance[2])*10
         if abs(future_balance+position)<=0.03*future_balance:
              return True
         else:
              return False    def spot_order(self,decimals):
                #Calculate quantity in spot terms
                spot_order_quantity=self.conversion_USDTtoQ(self.symbolA,clipA,decimals)
                #Create market making order on spot (limit order)
                o=B.order_spot("BUY",self.symbolA,spot_order_quantity,B.get_bid(symbol=self.symbolA))
                #Check clip order is not completed
                return o
    def open_leg(self,o,traded):
                executed=B.exe_qty(symbol=self.symbolA,order_id=o['orderId'])
                count=0
                #Wait until order we placed gets any fills                  
                while executed==traded or (executed-traded)*B.get_bid(symbol=self.symbolA)<=10: 
                        with Halo(text='Order open, waiting for fills ', spinner='dots') as spinner:  
                                count+=1
                                check_price=self.check_price(self.symbolA,self.fut_symbolA)
                                #Wait 120 secs to change order or cancel if price is no ok
                                if count==120 or check_price==False:
                                    #try to cancel, might be filled 
                                    try:
                                        B.cancel_order(self.symbolA,o['orderId'])
                                        print("Canceled order")
                                        break
                                    except Exception as E:
                                        print(E)
                                        print("Order filled before cancel")
                                        break
                                time.sleep(1)
                                return B.exe_qty(symbol=self.symbolA,order_id=o['orderId'])

    def trasnfer_trade(self,executed,traded):
                # The following code addresses potential discrepancies caused by Binance's rounding policies.   
                if self.hold_spot==True:
                    B.transfer(symbol=self.symbolA[:-4],q=executed-traded,type=3)
                elif self.hold_spot==False:
                    B.transfer(symbol=self.symbolA[:-4],q=B.spot_balance(self.symbolA[:-4]),type=3) 
    def adjust_clip(self,o,fut_o):
                last_trade_price=self.check_trade_price(o['orderId'],fut_o['orderId'])
                if last_trade_price==False:
                    clipA=self.clipA
                    clipA=round(clipA*0.5,3)
                    return True
                #If price is above, clip is the one we set
                elif last_trade_price==True:
                    clipA=self.clipA
                    return True
    def leg_a(self):
         q=self.q
         clipA=self.clipA
         decimals=self.get_decimals()
         while q>0:
            #Halo just gives a fancy loading format
            with Halo(text="Current price: ", spinner='dots') as spinner:          
                    while True:
                         spinner.text="Current price: "
                         spinner.text+=str(self.get_price(self.symbolA,self.fut_symbolA))
                         if self.check_price(self.symbolA,self.fut_symbolA)==True:
                            break
                    #ReCheck price is ok
                    while self.check_price(self.symbolA,self.fut_symbolA)==True:
                            spinner.stop()
                            traded=0
                            #Check that the order is not completed
                            if q>=self.clipA:  
                                o=self.spot_order(decimals)
                                while traded!=clipA:
                                    executed = self.open_leg(o,traded)
                                    spinner.stop()
                                    #Update executed Q before checking, not nesesary, could be delated 
                                    executed=B.exe_qty(symbol=self.symbolA,order_id=o['orderId'])
                                    #Break if order been canceled, ensure there is no new fill
                                    if executed==traded:
                                            break
                                    self.trasnfer_trade(executed,traded)
                                    print("Transfered from Spot to Futures account  %s  %s"%(executed-traded,self.symbolA))
                                    print("Hedging future leg..")
                                    #Create taking order in futures (market order)
                                    fut_o=B.order_mkt_future('SELL',round(((executed-traded)*B.get_trade_price(self.symbolA,o['orderId']))/10,0),self.fut_symbolA)
                                    traded=executed-traded
                                    print("Strategy Hedged")
                                    #If trade was below price, next trade is going to be 1/2 of the clip
                                    if self.adjust_clip(o,fut_o) == True:
                                         break
                                q=q-traded*B.get_trade_price(self.symbolA,o['orderId'])
                                print('----------------------------- Traded: %s  remaning quantity: %s -----------------------------'%(traded*B.get_trade_price(self.symbolA,o['orderId']),q) )
                            else:
                                break
            #Stop order if quantity remaning is less than one clip
            if q<=self.clipA:
                 break
         print("-----------------------------Order finished---------------------------------")
         raise Exception("Finished, checking hedge")
                




if __name__ == '__main__':
        print('Bot created for trading maker orders in spot, taker orders in future; this is for lowering fees')
        q = int(input('Total quantity in USD: '))
        clipA = int(input('Clip order, how big do you want each order to be: '))
        symbolA = input("Symbol you want to trade (e.g., XRPUSDT): ")
        fut_symbolA = input('The future of the previous symbol (e.g., XRPUSD_231229, set for just $10 futures contract): ')
        hold_spot = input('False/True - True if holding spot of the symbol, False if no spot balance of the symbol in the account: ')
        price = float(input('Target price difference between spot and future: '))

        try:
            B=Binance(KEY,SECRET)
            st = SporvsFuture(q, clipA, symbolA, fut_symbolA, price, hold_spot)
            initial_balance=st.initial_balance() #Storing data before star trading
            st.leg_a()
        except Exception as E:
            print(E)
            if st.check_hedge(initial_balance) is False:
                print("Warning: Hedge check failed.")
                sys.exit()
            else:
                print("Strategy implemented correctly")
     

