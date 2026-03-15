import os
import time
import datetime
import requests
import pandas as pd
import pandas_ta as ta
from delta_rest_client import DeltaRestClient, OrderType
from dotenv import load_dotenv

load_dotenv()

delta_client = DeltaRestClient(
    base_url='https://api.india.delta.exchange', 
    api_key=os.getenv('DELTA_API_KEY'),
    api_secret=os.getenv('DELTA_API_SECRET')
)

PRODUCT_ID = 27  
DAILY_TRADE_LIMIT = 4
trade_count = 0
current_date = datetime.date.today()

def fetch_candles(symbol="BTCUSD", resolution="15m", limit=250):
    url = "https://api.india.delta.exchange/v2/history/candles"
    end_time = int(time.time())
    res_map = {"15m": 15, "4h": 240}
    start_time = end_time - (limit * res_map.get(resolution, 15) * 60)
    
    params = {"symbol": symbol, "resolution": resolution, "start": start_time, "end": end_time}
    try:
        response = requests.get(url, params=params)
        data = response.json().get('result', [])
        if not data: return None
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df.sort_values(by='time').reset_index(drop=True)
    except Exception:
        return None

def get_4h_bias():
    df_4h = fetch_candles(resolution="4h", limit=201)
    if df_4h is None: return "NEUTRAL"
    df_4h.ta.ema(length=200, append=True)
    latest = df_4h.iloc[-1]
    return "BULL" if latest['close'] > latest['EMA_200'] else "BEAR"

def calculate_indicators(df):
    df.ta.ema(length=9, append=True)
    df.ta.ema(length=20, append=True) 
    df.ta.rsi(length=14, append=True)
    df.ta.atr(length=14, append=True)
    df.rename(columns={'EMA_9': 'ema_9', 'EMA_20': 'ema_20', 'RSI_14': 'rsi', 'ATRr_14': 'atr'}, inplace=True)
    return df

def check_strategy_signal():
    global trade_count, current_date
    
    if datetime.date.today() != current_date:
        current_date = datetime.date.today()
        trade_count = 0

    if trade_count >= DAILY_TRADE_LIMIT:
        return "LIMIT_REACHED", 0, 0, None

    bias = get_4h_bias()
    df = fetch_candles(resolution="15m", limit=100)
    if df is None: return "ERROR", 0, 0, None
    df = calculate_indicators(df)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    if bias == "BULL":
        if (prev['ema_9'] <= prev['ema_20']) and (latest['ema_9'] > latest['ema_20']) and (latest['rsi'] > 55):
            return "BUY", latest['close'], latest['atr'], df
            
    elif bias == "BEAR":
        if (prev['ema_9'] >= prev['ema_20']) and (latest['ema_9'] < latest['ema_20']) and (latest['rsi'] < 45):
            return "SELL", latest['close'], latest['atr'], df

    return "HOLD", 0, 0, df

def execute_trade(signal, price, atr):
    global trade_count
    if signal in ["HOLD", "ERROR", "LIMIT_REACHED"]: return f"Status: {signal}"
    
    # 16 Contracts for the 36% Profit Strategy
    total_size = 16 
    current_size = total_size
    sl_dist = 1.5 * atr
    
    side = 'buy' if signal == "BUY" else 'sell'
    exit_side = 'sell' if side == 'buy' else 'buy'
    
    sl_price = round(price - sl_dist if side == 'buy' else price + sl_dist, 1)

    try:
        delta_client.place_order(product_id=PRODUCT_ID, size=total_size, side=side, order_type=OrderType.MARKET)
        delta_client.place_stop_order(product_id=PRODUCT_ID, size=total_size, side=exit_side, stop_price=str(sl_price), order_type=OrderType.MARKET)
        
        reward_multiplier = 2  
        tp_messages = []
        
        while current_size > 0:
            if current_size == 1:
                chunk_size = 1
            else:
                chunk_size = int(current_size * 0.5) 
            
            tp_dist = reward_multiplier * sl_dist
            tp_price = round(price + tp_dist if side == 'buy' else price - tp_dist, 1)
            
            delta_client.place_order(product_id=PRODUCT_ID, size=chunk_size, side=exit_side, limit_price=str(tp_price), order_type=OrderType.LIMIT)
            
            tp_messages.append(f"1:{reward_multiplier} @ {tp_price} (Sz:{chunk_size})")
            current_size -= chunk_size
            reward_multiplier += 1
            
        trade_count += 1
        tp_log = " | ".join(tp_messages)
        return f"{signal} Executed! SL: {sl_price}\nTargets: {tp_log}\nCount: {trade_count}/4"
        
    except Exception as e:
        return f"Execution Error: {e}"