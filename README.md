# luna 🌕

A lightweight local API service built with FastAPI that wraps Bybit’s official REST API to provide enriched market data endpoints — including volatility ranking, candlestick retrieval, volume clusters, SMA, A/D, Fibonacci Retracement Levels, Support & Resistance Levels, RSI, MACD & Bollinger Bands Indicators.

This project lets you run a local server to query Bybit market data via easy REST API endpoints, enabling rapid prototyping, custom dashboards, or integration into your trading systems — all with error handling and consistent data processing.

---

## Setup ⚙️

1. Clone Git Repository - `git clone https://github.com/pyc4che/luna.git && cd luna`;
2. Create a Python Virtual Environment - `python3 -m venv .venv && source .venv/bin/activate`;
3. Install Python Requirements - `pip install -r requirements.txt`;
4. Create `.env` File (or copy configuration from `.env.example`);
5. Create `logs` directory & create `logs/service.log` file - `mkdir logs && touch logs/service.log` (change logs directory in `.env` configuration);
6. Run the App - `PYTHONPATH=app uvicorn main:app --host 127.0.0.1 --port 9000 --reload`

---

## Service Setup 🛠️

Proceed with `Setup ⚙️` section, but in `/opt` directory (root required)

### Linux 🐧

1. Create `run.sh` file - `touch run.sh`;
2. Make the file executable - `chmod 700 run.sh`
3. Paste this into `run.sh` (you may use `0.0.0.0` or `127.0.0.1`, depends on whether you want to make API visible on LAN or accessible only from machine):
```bash
#!/bin/bash

cd /opt/luna
export PYTHONPATH=app
source .venv/bin/activate
exec uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```
4. Create the service file - `sudo nano /etc/systemd/system/luna.service`;
5. Paste this into `luna.service`:
```ini
[Unit]
Description=Bybit API (luna)
After=network.target

[Service]
User=your-username
WorkingDirectory=/opt/luna
ExecStart=/opt/luna/run.sh
Restart=always
RestartSec=5
Enironment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
6. Enable & start the service - `sudo systemctl deamon-reexec && sudo systemctl deamon-reload && sudo systemctl enable luna && systemctl start luna`

---

## API Functions 🔍

- **bin_size** - prices are rounded to the nearest level specified by the parameter;
- **category** - market type (spot, linear, inverse);
- **hours** - look-back time;
- **interval** - candlestick interval;
- **limit** *(for volatility/volume clusters)* - limit of pairs, e.g. 10;
- **limit** - number of candles per request;
- **trade_limit** - number of trades to analyze (volume clusters);
**period** - SMA/RSI parameter, candlestick period for analysis; 
**symbol** - crypto pair, e.g. BTCUSDT;
- **window** - same as period, but for Bollinger Bands.

---

1. **Volatile Pairs:** You can access *N* (**limit** parameter) number of pairs - access point `/api/volatile`, params `category, limit`;

2. **Candlesticks Data:** Access candlestick data - access point `/api/candlesticks`, params `symbol, interval, hours`;

3. **Volume Clusters:** Access *N* (**limit** parameter) number of prices, where the main volume is concentrated - access point `/api/clusters`, params `symbol, bin_size, trade_limit, limit`;

4. **SMA:** Access SMA value - access point `/api/sma`, params `symbol, interval, period, category`;

5. **A/D Line:** Access A/D value - access point `/api/adline`, params `symbol, interval, limit, hours`;

6. **Fibonacci Retracement Levels:** Access Fibonacci levels - access point `/api/fibonacci`, params `symbol, interval, limit, category`;

7. **Support & Resistance Levels:** Access Global Support & Resistance Levels - access point `/api/support_resistance`, params `symbol, interval, limit, category, hours`;

8. **Indicators:**
    - **RSI** - access point `/api/rsi`, params `symbol, interval, limit, period, hours`
    - **MACD** - access point `/api/macd`, params `symbol, interval, limit, hours`
    - **Bollinger Bands** - access point `/api/bollinger`, params `symbol, interval, limit, window, hours`

---
