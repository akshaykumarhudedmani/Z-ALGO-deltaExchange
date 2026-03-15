import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import google.generativeai as genai
from dotenv import load_dotenv

import algo_engine as ae

load_dotenv()

st.set_page_config(page_title="Dashboard | TokenIQ", page_icon="📊", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please enter via the main App Gate.")
    st.stop()
    
# Initialize Live Trading State
if 'live_trading_active' not in st.session_state:
    st.session_state.live_trading_active = False

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    model = None
    st.sidebar.error(f"Gemini AI not configured: {e}")

st.title("⚡ Master Zovereign Algorithm")
st.markdown("Live Multi-Timeframe Strategy Monitoring & AI Portfolio Diagnostics")

# --- DATA PARSING HELPERS ---
@st.cache_data(ttl=5)
def load_backtest_metrics():
    try:
        df = pd.read_csv("strategy_results.csv")
        df['time'] = pd.to_datetime(df['entry_time'])
        
        total_trades = len(df)
        wins = len(df[df['realized_pnl'] > 0])
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
        net_pnl = df['realized_pnl'].sum()
        
        # Max Drawdown & Equity Curve Calculations
        df['cum_pnl'] = df['realized_pnl'].cumsum()
        df['peak_pnl'] = df['cum_pnl'].cummax()
        df['drawdown'] = df['cum_pnl'] - df['peak_pnl']
        max_drawdown = df['drawdown'].min() 
        
        df_display = df.tail(10)[['entry_time', 'type', 'entry_price', 'status', 'realized_pnl']].copy()
        df_display.rename(columns={
            'entry_time': 'Time', 'type': 'Side', 'entry_price': 'Entry', 
            'status': 'Status', 'realized_pnl': 'PnL'
        }, inplace=True)
        
        return total_trades, win_rate, net_pnl, max_drawdown, df_display, df
        
    except FileNotFoundError:
        return 0, 0.0, 0.0, 0.0, pd.DataFrame(), pd.DataFrame()

total_trades, win_rate, net_pnl, max_dd, df_trades, df_full = load_backtest_metrics()

# --- SECTION 1: VIRTUAL DEMO PORTFOLIO & LIVE TOGGLE ---
st.header("1. Delta Exchange Virtual Portfolio")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

col1.metric("Exchange Connection", "Delta Mainnet", delta="API Live", delta_color="normal")
col2.metric("Base Account Balance", "$100.00", delta="Local Demo Mode")

# The Live Trading Toggle
with col4:
    st.write("**Master Execution Switch**")
    if st.session_state.live_trading_active:
        if st.button("🔴 STOP LIVE TRADING", use_container_width=True):
            st.session_state.live_trading_active = False
            st.rerun()
    else:
        if st.button("🟢 START LIVE TRADING", use_container_width=True):
            st.session_state.live_trading_active = True
            st.rerun()
            
if st.session_state.live_trading_active:
    col3.metric("Zovereign Algorithm", "ACTIVE", delta="Searching for Signals...", delta_color="normal")
else:
    col3.metric("Zovereign Algorithm", "STANDBY", delta="Switch OFF", delta_color="inverse")

# Action block if live trading is ON
if st.session_state.live_trading_active:
    st.warning("⚡ **LIVE TRADING IS ENABLED** - Zovereign Algo is querying Delta API...")
    with st.spinner("Executing Market Analysis..."):
         signal, price, atr, df_live = ae.check_strategy_signal()
         if signal in ["BUY", "SELL"]:
             st.success(f"**SIGNAL DETECTED ({signal})!** Routing orders to Delta Testnet...")
             exec_result = ae.execute_trade(signal, price, atr)
             st.code(exec_result)
         elif signal == "HOLD":
             st.info("No valid entry setups on the current 15M candle. Waiting...")
         else:
             st.error(f"Engine Status: {signal}")

st.divider()

# --- SECTION 2: EQUITY CURVE & PERFORMANCE METRICS ---
st.header("2. Zovereign Historical Performance")

col_a, col_b, col_c = st.columns(3)
col_a.metric("Total Trades Executed", f"{total_trades}")
col_b.metric("Strategy Win Rate", f"{win_rate:.2f}%")
col_c.metric("Historical Net Profit", f"{net_pnl:.2f}", delta=f"{net_pnl:.2f} Growth")

if not df_full.empty:
    st.subheader("Equity Curve & Drawdown Visualizer")
    
    # Create a subplot: Top is Equity Curve, Bottom is Drawdown
    fig_eq = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.1, row_heights=[0.7, 0.3])
    
    # Equity Curve Line
    fig_eq.add_trace(go.Scatter(
        x=df_full['time'], y=df_full['cum_pnl'], 
        mode='lines', name='Equity Curve', line=dict(color='#00ffcc', width=2)
    ), row=1, col=1)
    
    # Drawdown Area (Filled Red)
    fig_eq.add_trace(go.Scatter(
        x=df_full['time'], y=df_full['drawdown'], 
        fill='tozeroy', mode='none', name='Drawdown', fillcolor='rgba(255, 0, 0, 0.3)'
    ), row=2, col=1)
    
    fig_eq.update_layout(
        height=500, template='plotly_dark',
        title_text="Zovereign Algorithm: Cumulative PnL vs Drawdown",
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )
    st.plotly_chart(fig_eq, use_container_width=True)

st.markdown("#### Real Execution Log (Latest 10 Signals)")
if not df_trades.empty:
    def color_pnl(val):
        color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
        return f'color: {color}'
    st.dataframe(df_trades.style.applymap(color_pnl, subset=['PnL']).format({'PnL': "{:.2f}"}), use_container_width=True)
else:
    st.warning("No backtest data found. Please run backtester.py locally first.")
    
st.divider()

# --- SECTION 3: THE ALGO ENGINE CHART ---
st.header("3. Live Market Scanner (BTC/USD)")

with st.spinner("Fetching latest Delta Exchange orderbook data..."):
    df_15m = ae.fetch_candles(limit=150)
    
    if df_15m is not None:
        df_15m = ae.calculate_indicators(df_15m)
        df_chart = df_15m.tail(100).copy()
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_chart['time'], open=df_chart['open'], high=df_chart['high'],
            low=df_chart['low'], close=df_chart['close'], name='BTC/USD 15m'
        ))
        
        fig.add_trace(go.Scatter(x=df_chart['time'], y=df_chart['ema_9'], mode='lines', line=dict(color='blue', width=1), name='9 EMA'))
        fig.add_trace(go.Scatter(x=df_chart['time'], y=df_chart['ema_20'], mode='lines', line=dict(color='orange', width=2), name='20 EMA'))
        
        fig.update_layout(
            title='BTC/USD 15-Minute Technical Chart',
            yaxis_title='USD Price', xaxis_title='Time UTC',
            template='plotly_dark', height=450, uirevision='constant',
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- SECTION 4: AI PORTFOLIO ASSISTANT (GEMINI 1.5) ---
st.header("🧠 Gemini 1.5 Flash: Chief Risk Officer")

portfolio_context = f"""
Current System State:
- Total Trades Evaluated: {total_trades}
- Zovereign Algorithm Win Rate: {win_rate:.2f}%
- Net Profit: {net_pnl:.2f}
- Max Recorded Drawdown: {max_dd:.2f}

Analyze this exact real-world portfolio state and provide 3 quick bullet points on risk management advice for the user based on the drawdown and win rate data. Keep it professional, concise, and under 150 words total. Do not use the word 'units'.
"""

if st.button("Generate Dynamic AI Risk Report"):
    with st.spinner("Gemini 1.5 Flash is analyzing your Master Zovereign Algorithm metrics..."):
        try:
            if model is None:
                raise Exception("API Key Missing or Invalid Configuration.")
                
            response = model.generate_content(portfolio_context)
            st.success("**Dynamic AI Risk Report Generated**")
            st.markdown(response.text)
            
        except Exception as e:
            st.warning("**AI Assistant Offline - Executing Fallback Scanner**")
            st.info(f"""
            * **Drawdown Control**: Max drawdown was measured at {max_dd:.2f}. If this exceeds your max threshold, limit daily trades.
            * **Current Performance Feedback**: Given the {win_rate:.2f}% win-rate, check if the fractional grid logic (50% slicing) is sacrificing too much momentum on big runs compared to the 1.5 SL drag.
            * **Exposure Limits**: Keep maximum risk strictly capped to prevent ruin strings.
            """)
