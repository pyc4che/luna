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
def get_sma(symbol: str = Query(...), interval: str = Query('1'), period: int = Query(10), category: str = Query('linear')):
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
def get_ad_line(symbol: str = Query(...), interval: str = Query('15'), limit: int = Query(50), category: str = 'linear'):
    root.info(
        f'Request: adline (symbol={symbol}, interval={interval}, limit={limit}, category={category})'
    )

    return {
        'result': api.ad_trend(
            symbol=symbol,
            interval=interval,
            limit=limit,
            category=category
        )
    }
