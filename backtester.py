import pandas as pd
import pandas_ta as ta
import datetime

def run_backtest():
    print("Loading 1-Year historical data...")
    try:
        df = pd.read_csv("btc_1yr_15m.csv")
    except FileNotFoundError:
        print("❌ ERROR: 'btc_1yr_15m.csv' not found.")
        return
        
    df.columns = [col.strip().lower() for col in df.columns]
    df['time'] = pd.to_datetime(df['time'])
    for col in ['open', 'high', 'low', 'close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print("Calculating Multi-Timeframe Indicators...")
    
    # --- 4H BIAS (Fixed Pandas '4h' warning) ---
    df_4h = df.resample('4h', on='time').last().dropna()
    df_4h.ta.ema(length=200, append=True)
    df['4h_ema_200'] = df['time'].dt.floor('4h').map(df_4h['EMA_200'])

    # --- 15M INDICATORS ---
    df.ta.ema(length=9, append=True)
    df.ta.ema(length=20, append=True) 
    df.ta.rsi(length=14, append=True)
    df.ta.atr(length=14, append=True)
    
    df.rename(columns={'EMA_9': 'ema_9', 'EMA_20': 'ema_20', 'RSI_14': 'rsi', 'ATRr_14': 'atr'}, inplace=True)
    df.dropna(subset=['ema_20', '4h_ema_200', 'rsi', 'atr'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # --- SIMULATION VARIABLES ---
    position = None
    completed_trades = []
    
    current_day = None
    trades_today = 0
    DAILY_TRADE_LIMIT = 4

    # The Winning Risk Settings
    TOTAL_RISK_USD = 2.00 
    TOTAL_CONTRACTS = 16
    RISK_PER_CONTRACT = TOTAL_RISK_USD / TOTAL_CONTRACTS 

    print("Simulating Winning Scale-Out Strategy (16 Contracts -> 8, 4, 2, 1, 1)...")
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        
        if row['time'].date() != current_day:
            current_day = row['time'].date()
            trades_today = 0
            
        # --- ENTRY SYSTEM ---
        if position is None:
            if trades_today < DAILY_TRADE_LIMIT and row['time'].weekday() < 5:
                bias = "BULL" if row['close'] > row['4h_ema_200'] else "BEAR"
                
                is_bull_trigger = bias == "BULL" and prev['ema_9'] <= prev['ema_20'] and row['ema_9'] > row['ema_20'] and row['rsi'] > 55
                is_bear_trigger = bias == "BEAR" and prev['ema_9'] >= prev['ema_20'] and row['ema_9'] < row['ema_20'] and row['rsi'] < 45
                
                if is_bull_trigger or is_bear_trigger:
                    trade_type = 'LONG' if is_bull_trigger else 'SHORT'
                    entry_price = row['close']
                    sl_dist = 1.5 * row['atr']
                    sl_price = entry_price - sl_dist if trade_type == 'LONG' else entry_price + sl_dist
                    
                    # Build the 5 scaling tranches dynamically
                    tranches = []
                    sizes = [8, 4, 2, 1, 1]
                    for idx, size in enumerate(sizes):
                        r_mult = idx + 2 # Starts at 1:2, ends at 1:6
                        tp_dist = r_mult * sl_dist
                        tp_price = entry_price + tp_dist if trade_type == 'LONG' else entry_price - tp_dist
                        tranches.append({
                            'id': idx + 1, 'size': size, 'r_mult': r_mult, 
                            'tp_price': tp_price, 'status': 'OPEN'
                        })
                        
                    position = {
                        'type': trade_type, 'entry_price': entry_price, 'sl': sl_price,
                        'entry_time': row['time'], 'tranches': tranches, 'net_pnl': 0.0
                    }
                    trades_today += 1

        # --- EXIT / SCALING SYSTEM ---
        else:
            all_closed = True
            
            # Static Stop Loss (This is what makes the 36% profit!)
            sl_hit = (position['type'] == 'LONG' and row['low'] <= position['sl']) or \
                     (position['type'] == 'SHORT' and row['high'] >= position['sl'])
            
            if sl_hit:
                for t in position['tranches']:
                    if t['status'] == 'OPEN':
                        t['status'] = 'STOPPED_OUT'
                        position['net_pnl'] -= (t['size'] * RISK_PER_CONTRACT)
                all_closed = True
                
            else:
                for t in position['tranches']:
                    if t['status'] == 'OPEN':
                        tp_hit = (position['type'] == 'LONG' and row['high'] >= t['tp_price']) or \
                                 (position['type'] == 'SHORT' and row['low'] <= t['tp_price'])
                        
                        if tp_hit:
                            t['status'] = 'PROFIT_TAKEN'
                            position['net_pnl'] += (RISK_PER_CONTRACT * t['size'] * t['r_mult'])
                        else:
                            all_closed = False 
            
            if all_closed:
                completed_trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': row['time'],
                    'type': position['type'],
                    'pnl': position['net_pnl'],
                    'status': 'WIN' if position['net_pnl'] > 0 else 'LOSS'
                })
                position = None

    generate_report(completed_trades, 100)

def generate_report(trades, start_balance):
    if not trades:
        print("\nNo trades were triggered.")
        return
        
    df_results = pd.DataFrame(trades)
    wins = len(df_results[df_results['status'] == 'WIN'])
    losses = len(df_results[df_results['status'] == 'LOSS'])
    net_pnl = df_results['pnl'].sum()
    
    print("\n" + "="*45)
    print("🏆 DYNAMIC SCALE-OUT BACKTEST REPORT 🏆")
    print("="*45)
    print(f"Total Trade Setups : {len(df_results)}")
    print(f"Profitable Setups  : {wins} (Any trade closed in green)")
    print(f"Losing Setups      : {losses}")
    print(f"Setup Win Rate     : {(wins/len(df_results))*100:.2f}%")
    print("-" * 45)
    print(f"Starting Balance   : ${start_balance:.2f}")
    print(f"Net Profit/Loss    : ${net_pnl:.2f}")
    print(f"Final Balance      : ${start_balance + net_pnl:.2f}")
    print(f"Total Growth       : {(net_pnl/start_balance)*100:.2f}%")
    print("="*45)
    df_results.to_csv("scale_out_results.csv", index=False)

if __name__ == "__main__":
    run_backtest()

else:
    print("the tra")