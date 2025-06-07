import requests

from core.logger import root
from core.config import settings

from collections import defaultdict


class BybitAPI:
    def __init__(self) -> None:
        self.trades_url = settings.BYBIT_TRADES_URL
        self.tickers_url = settings.BYBIT_TICKERS_URL
        self.candles_url = settings.BYBIT_CANDLESTCIKS_URL


    def __request(self, url: str, params: dict, timeout: int = 10) -> list:
        try:
            response = requests.get(
                url, 
                params=params,
                timeout=timeout
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


    def volatility_data(self, category: str = 'linear', limit: int = 10) -> list:
        params = {'category': category}

        raw = self.__request(
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


    def candlestick_data(self, symbol: str, interval: str = '60', limit: int = 48) -> list:
        if limit in range(48, 169):
            params = {
                'category': 'linear',
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }

            return self.__request(
                url=self.candles_url,
                params=params
            )

        else: 
            return []


    def volume_clusters(
        self, symbol: str, bin_size: int = settings.BIN_SIZE,
        trade_limit: int = settings.TRADES_LIMIT, limit: int = 10) -> list:

        categories = ['linear', 'spot', 'inverse']

        for category in categories:
            params = {
                'category': category,
                'symbol': symbol,
                'limit': trade_limit
            }

            trades = self.__request(
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
