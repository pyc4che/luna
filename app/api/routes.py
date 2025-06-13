from fastapi import APIRouter, Query

from core.logger import root

from services.bybit_api import BybitAPI
from services.data_provider import DataProvider


router = APIRouter()
api = BybitAPI()
dp = DataProvider()


@router.get('/volatile')
async def get_top_volatile_pairs(category: str = Query('linear'), limit: int = Query(10)):
    root.info(
        f'Request: volatile (category={category}, limit={limit})'
    )

    return {
        'result': api.volatility_data(
            category=category,
            limit=limit
        )
    }


@router.get('/candlesticks')
async def get_candles(symbol: str = Query(...), interval: str = Query('60'), hours: int = Query(48)):
    root.info(
        f'Request: candlesticks (symbol={symbol}, interval={interval}, hours={hours})'
    )

    raw = api.candlestick_data(
        symbol=symbol,
        interval=interval,
        limit = int(hours * 60 / int(interval))
    )

    df = dp.to_dataframe(
        raw, hours=hours
    )

    return {
        'result': df.reset_index().to_dict(orient='records')
    }


@router.get('/clusters')
async def get_clusters(symbol: str = Query(...), bin_size: int = Query(50), trade_limit: int = Query(1000), limit: int = Query(10)):
    root.info(
        f'Request: clusters (symbol={symbol}, bin_size={bin_size}, trade_limit={trade_limit}, limit={limit})'
    )

    return {
        'result': api.volume_clusters(
            symbol=symbol,
            bin_size=bin_size,
            trade_limit=trade_limit,
            limit=limit
        )
    }


@router.get('/sma')
async def get_sma(symbol: str = Query(...), interval: str = Query('1'), period: int = Query(10), category: str = Query('linear')):
    root.info(
        f'Request: sma (symbol={symbol}, interval={interval}, period={period}, category={category})'
    )

    return {
        'result': api.sma_trend(
            symbol=symbol,
            interval=interval,
            period=period,
            category=category
        )
    }


@router.get('/adline')
async def get_ad_line(symbol: str = Query(...), interval: str = Query('15'), limit: int = Query(50)):
    root.info(
        f'Request: adline (symbol={symbol}, interval={interval}, limit={limit})'
    )

    return {
        'result': api.ad_trend(
            symbol=symbol,
            interval=interval,
            limit=limit
        )
    }


@router.get('/fibonacci')
async def get_fibonacci_levels(symbol: str = Query(...), interval: str = Query('60'), limit: int = Query(48), category: str = 'linear'):
    root.info(
        f'Request: fibonacci (symbol={symbol}, interval={interval}, limit={limit}, category={category})'
    )

    return {
        'result': api.fibonacci_levels(
            symbol=symbol,
            interval=interval,
            limit=limit,
            category=category
        )
    }


@router.get('/support_resistance')
async def get_support_resistance_levels(symbol: str = Query(...), interval: str = Query('60'), limit: int = Query(48), category: str = 'linear'):
    root.info(
        f'Request support_resistance (symbol={symbol}, interval={interval}, limit={limit}, category={category})'
    )

    return {
        'result': api.support_resistance_levels(
            symbol=symbol,
            interval=interval,
            limit=limit,
            category=category
        )
    }


@router.get('/rsi')
async def get_rsi(symbol: str = Query(...), interval: str = Query('60'), limit: int = Query(48), period: int = Query(14)):
    root.info(
        f'Request rsi (symbol={symbol}, interval={interval}, limit={limit}'
    )

    return {
        'result': api.rsi(
            symbol=symbol,
            interval=interval,
            limit=limit,
            period=period
        )
    }


@router.get('/macd')
async def get_macd(symbol: str = Query(...), interval: str = Query('60'), limit: int = Query(48)):
    root.info(
        f'Request macd (symbol={symbol}, interval={interval}, limit={limit})'
    )

    return {
        'result': api.macd(
            symbol=symbol,
            interval=interval,
            limit=limit
        )
    }


@router.get('/bollinger')
async def get_bollinger(symbol: str = Query(...), interval: str = Query('60'), limit: int = Query(48), window: int = Query(20)):
    root.info(
        f'Request bollinger (symbol={symbol}, interval={interval}, limit={limit}, window={window})'
    )

    return {
        'result': api.bollinger(
            symbol=symbol,
            interval=interval,
            limit=limit,
            window=window
        )
    }
