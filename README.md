# TokenIQ Sentinel

A python-based algorithmic trading terminal built with Streamlit, leveraging the Delta Exchange API for live trading and Google Gemini 1.5 for risk analytics.

## ⚠️ Disclaimer
**The application and strategy are currently configured as a demo connecting to a Delta Exchange testnet/demo account. Do not use for real money trading without thorough testing and understanding of the code!**

## 🚀 Features

- **Live Market Scanner:** Monitors BTC/USD on 15m and 4h timeframes using real-time API data.
- **Zovereign Algorithm:** A trend-following strategy using 9/20 EMA crossovers, RSI confirmation, and ATR-based dynamic scale-out taking profits in multiple chunks (16 contracts -> 8, 4, 2, 1, 1).
- **Virtual Portfolio Dashboard:** Visualizes equity curves, maximum drawdowns, and live execution logs.
- **AI Risk Officer:** Uses Google Gemini 1.5 to analyze your backtest metrics and provide concise risk management advice.
- **Crypto Radio:** Fetches recent crypto headlines and broadcasts an AI-generated sentiment summary via audio (English, Hindi, Kannada).

## 📂 Project Structure
- `app.py`: Main entry point for the Streamlit dashboard.
- `algo_engine.py`: Core trading logic, Delta Exchange API connectivity, and technical indicators.
- `backtester.py`: Offline backtesting module to simulate the strategy over historical data.
- `risk_management.py`: Position sizing and risk scaling utilities.
- `pages/`: Dashboard modules (Settings, News Radio, Research).
- `sample_data.csv`: A small mock dataset for testing the backtester out-of-the-box.

## 🛠️ Setup & Installation

1. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory with the following API keys:
   ```env
   DELTA_API_KEY=your_delta_exchange_api_key
   DELTA_API_SECRET=your_delta_exchange_api_secret
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

3. **Run the Dashboard:**
   ```bash
   streamlit run app.py
   ```

## 📊 Backtesting & Custom Data
To generate a historical performance report:
```bash
python backtester.py
```
This produces a `strategy_results.csv` which the dashboard reads to display the equity curve.

**Using Your Own Data:** 
By default, the backtester will look for a 1-year dataset named `btc_1yr_15m.csv`. If it is not found, it will automatically fallback to the included `sample_data.csv` so you can verify the code works.

To get full 1-year historical data for serious backtesting:
1. We recommend using **QuantDataManager** or downloading historical OHLCV data from Binance/Delta.
2. You will need two CSV files (15-minute timeframe and 4-hour timeframe).
3. Ensure the CSVs have columns named: `time`, `open`, `high`, `low`, `close`.
4. Place `btc_1yr_15m.csv` in the root folder, and the backtester will automatically use it instead of the sample data.

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
