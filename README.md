# TokenIQ Sentinel AI (Zovereign Algorithm)

A state-of-the-art algorithmic trading terminal built with Streamlit, leveraging the Delta Exchange API for live trading, coupled with AI-driven analytics powered by Google Gemini 1.5.

## ⚠️ Disclaimer
**The application and strategy are just demos of a connected Delta Exchange API testnet/demo account. They are not real, and are still for research purposes. Use at your own risk!**

## 🚀 Features

- **Live Market Scanner:** Monitors BTC/USD on multiple timeframes (15m, 4h).
- **Zovereign Algorithm:** Uses EMA crossovers, RSI, and ATR for trend-following and dynamic scale-out strategies.
- **Virtual Portfolio Dashboard:** Monitor your Delta Exchange portfolio in real-time, visualizing equity curves and maximum drawdowns.
- **AI Chief Risk Officer:** Powered by Gemini 1.5, evaluates your trading performance and provides real-time risk management insights.
- **AI News Radio:** Fetches global crypto headlines, summarizes sentiment with Gemini, and broadcasts via audio in multiple languages (English, Hindi, Kannada).

## 📂 Project Structure
- `app.py`: Main entry gate for the Streamlit dashboard.
- `algo_engine.py`: Core trading logic, API connectivity, and indicator calculations.
- `backtester.py`: Offline backtesting module to simulate the Zovereign strategy over historical data.
- `risk_management.py`: Position sizing and risk scaling utilities.
- `pages/`: Additional dashboard modules (Settings, AI News Radio, Research).

## 🛠️ Setup & Installation

1. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory with the following keys:
   ```env
   DELTA_API_KEY=your_delta_exchange_api_key
   DELTA_API_SECRET=your_delta_exchange_api_secret
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

3. **Run the Dashboard:**
   ```bash
   streamlit run app.py
   ```

## 📊 Backtesting
To generate a historical performance report (requires historical CSV data like `btc_1yr_15m.csv` in the root folder):
```bash
python backtester.py
```
This will produce a `strategy_results.csv` which the dashboard uses to display the equity curve.

## 🧠 Technologies Used
- **Streamlit**: Web interface and dashboard.
- **Pandas & Pandas-TA**: Data manipulation and technical indicators.
- **Delta Exchange REST Client**: Real-time order execution.
- **Google Generative AI (Gemini)**: AI risk analysis and market sentiment generation.
- **gTTS & Deep-Translator**: Real-time translated audio broadcasts.
- **Plotly**: Advanced charting and data visualization.
