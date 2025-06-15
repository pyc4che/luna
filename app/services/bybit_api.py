import httpx

import ta

from core.logger import root
from core.config import settings
from core.caching import logged_cache, ttl_for

from services.data_provider import DataProvider


from collections import defaultdict


class BybitAPI:
    def __init__(self) -> None:
        self.trades_url = settings.BYBIT_TRADES_URL
        self.tickers_url = settings.BYBIT_TICKERS_URL
        self.candles_url = settings.BYBIT_CANDLESTCIKS_URL


    async def __request(self, url: str, params: dict, timeout: int = 10) -> list:
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(
                    url, 
                    params=params
                )
                response.raise_for_status()

                data = response.json()

                if data.get('retCode') == 0:
                    return data.get(
                        'result', {}
                    ).get(
                        'list', []
                    )

                else:
                    root.error(
                        f'API Error: {data.get("retMsg")}'
                    )
                    return []

            except Exception as _ex:
                root.error(
                    f'BybitAPI request error: {_ex}'
                )
                return []

    @logged_cache(expire=ttl_for('volatility_data'))
    async def volatility_data(self, category: str = 'linear', limit: int = 10) -> list:
        params = {'category': category}

        raw = await self.__request(
            url=self.tickers_url,
            params=params
        )

        if not raw:
            return []

        result = []

        for item in raw:
            try:
                low = float(item['lowPrice24h'])
                high = float(item['highPrice24h'])

                if low == 0:
                    continue

                volatility = (high - low) / low * 100

                result.append(
                    {
                        'symbol': item['symbol'],
                        'high': high,
                        'low': low,
                        'volatility': volatility
                    }
                )

            except Exception as _ex:
                root.warning(f"Parse error: {_ex} in item {item}")
                continue

        return sorted(
            result, 
            key=lambda x: x['volatility'],
            reverse=True
        )[:limit]


    @logged_cache(expire=ttl_for('candlestick_data'))
    async def candlestick_data(self, symbol: str, interval: str = '60', limit: int = 48) -> list:
        params = {
            'category': 'linear',
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        return await self.__request(
            url=self.candles_url,
            params=params
        )

    @logged_cache(expire=ttl_for('volume_clusters'))
    async def volume_clusters(
        self, symbol: str, bin_size: int = settings.BIN_SIZE,
        trade_limit: int = settings.TRADES_LIMIT, limit: int = 10) -> list:

        categories = ['linear', 'spot', 'inverse']

        for category in categories:
            params = {
                'category': category,
                'symbol': symbol,
                'limit': trade_limit
            }

            trades = await self.__request(
                url=self.trades_url,
                params=params
            )

            if not trades:
                continue

            volume_cluster = defaultdict(float)

            for trade in trades:
                try:
                    price = float(trade.get('price', trade.get('p', 0)))
                    volume = float(trade.get('size', trade.get('v', 0)))

                    if (price == 0 
                        and volume == 0):
                        continue

                    price_bin = price / bin_size * bin_size

                    volume_cluster[price_bin] += volume

                except Exception as _ex:
                    root.warning(
                        f'Trade parse error {_ex} in trade {trade}'
                    )
                    continue

            return sorted(
                volume_cluster.items(), key=lambda x: x[1], reverse=True
            )[:limit]

        return []


    @logged_cache(expire=ttl_for('sma_trend'))
    async def sma_trend(
        self, symbol: str, interval: str = settings.SMA_INTERVAL,
        period: int = settings.SMA_PERIOD, category: str = 'linear') -> dict:

        params = {
            'category': category,
            'symbol': symbol,
            'interval': interval,
            'limit': period
        }

        data = await self.__request(
            url=self.candles_url,
            params=params
        )

        if data:
            prices = [float(candle[4]) for candle in data]

        else:
            root.error("ValueError Empty field in 'result.list'")

        sma = sum(prices) / len(prices) if prices else 0
        trend = 'UP' if prices[-1] > sma else 'DOWN'

        return {
            'price': prices[-1],
            'sma': sma,
            'trend': trend
        }


    @logged_cache(expire=ttl_for('ad_trend'))
    async def ad_trend(
        self, symbol: str, interval: str = settings.AD_INTERVAL, 
        limit: int = settings.AD_LIMIT, category: str = 'linear', hours: int = 48) -> dict:

        ad_line = 0
        ad_values =[]

        params = {
            'category': category,
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        data = await self.__request( 
            url=settings.BYBIT_CANDLESTCIKS_URL,
            params=params
        )

        data = DataProvider().to_dataframe(
            raw=data,
            hours=hours
        )

        for open, high, low, close, volume in data.values.tolist():
            if high != low:
                flow = ((close - low) - (high - close)) / (high - low)

            else:
                flow = 0

            ad_line += flow * volume

            ad_values.append(ad_line)

        trend = 'UP' if ad_values[-1] > ad_values[-2] else 'DOWN'

        return {
            'price': data.values.tolist(),
            'ad': ad_values,
            'trend': trend
        }


    @logged_cache(expire=ttl_for('fibonacci_levels'))
    async def fibonacci_levels(
        self, symbol: str, interval: str = settings.INTERVAL, 
        limit: int = settings.LIMIT) -> dict:

        candles = await self.candlestick_data(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        if not candles:
            return {}

        lows = [float(candle[3]) for candle in candles]
        highs = [float(candle[2]) for candle in candles]

        ratios = [1, 0.786, 0.618, 0.5, 0.328, 0.236, 0]

        levels = {str(r): max(highs) - (max(highs) - max(lows)) * r for r in ratios}

        return {
            'high': max(highs),
            'low': max(lows),
            'fib': levels
        }


    @logged_cache(expire=ttl_for('support_resistance_levels'))
    async def support_resistance_levels(
        self, symbol: str, interval: str = settings.INTERVAL,
        limit: int = settings.LIMIT, category: str = 'linear', hours: int = 48) -> dict:

        params = {
            'category': category,
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        data = await self.__request( 
            url=settings.BYBIT_CANDLESTCIKS_URL,
            params=params
        )

        data = DataProvider().to_dataframe(
            raw=data,
            hours=hours    
        )

        support = data['low'].min()
        resistance = data['high'].max()

        return {
            'support': support,
            'resistance': resistance
        }


    @logged_cache(expire=ttl_for('rsi'))
    async def rsi(
        self, symbol: str, interval: str = settings.INTERVAL,
        limit: int = settings.LIMIT, period: int = 14, hours: int = 48) -> dict:

        data = await self.candlestick_data(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        data = DataProvider().to_dataframe(
            raw=data,
            hours=hours
        )

        if data.empty:
            return {}

        data['rsi'] = ta.momentum.RSIIndicator(
            close=data['close'],
            window=period
        ).rsi()

        data = DataProvider().safe_json(
            series=data,
            subset=['rsi']
        )

        return data[['open_time', 'rsi']].to_dict(orient='records')


    @logged_cache(expire=ttl_for('macd'))
    async def macd(
        self, symbol: str, interval: str = settings.INTERVAL,
        limit: int = settings.LIMIT, hours: int = 48) -> dict:

        data = await self.candlestick_data(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        data = DataProvider().to_dataframe(
            raw=data,
            hours=hours
        )

        if data.empty:
            return {}

        macd = ta.trend.MACD(close=data['close'])   

        data['macd'] = macd.macd()
        data['signal'] = macd.macd_signal()
        data['histogram'] = macd.macd_diff()

        data = DataProvider().safe_json(
            series=data,
            subset=['macd', 'signal', 'histogram']
        )

        return data[['open_time', 'macd', 'signal', 'histogram']].to_dict(orient='records')


    @logged_cache(expire=ttl_for('bollinger'))
    async def bollinger(
        self, symbol: str, interval: str = settings.INTERVAL,
        limit: int = settings.LIMIT, window: int = 20, hours: int = 48) -> dict:

        data = await self.candlestick_data(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        data = DataProvider().to_dataframe(
            raw=data,
            hours=hours
        )

        if data.empty:
            return {}

        bb = ta.volatility.BollingerBands(
            close=data['close'],
            window=window
        )

        data['upper'] = bb.bollinger_hband()
        data['lower'] = bb.bollinger_lband()
        data['middle'] = bb.bollinger_mavg()

        data = DataProvider().safe_json(
            series=data,
            subset=['upper', 'lower', 'middle']
        )

        

        return data[['open_time', 'upper', 'lower', 'middle']].to_dict(orient='records')
