from pathlib import Path

from os import environ
from dotenv import load_dotenv

from pydantic import BaseModel, Field

load_dotenv()

class Settings(BaseModel):
    BYBIT_TRADES_URL: str = Field(
        default='https://api.bybit.com/v5/market/recent-trade'
    )
    BYBIT_TICKERS_URL: str = Field(
        default='https://api.bybit.com/v5/market/tickers'
    )
    BYBIT_CANDLESTCIKS_URL: str = Field(
        default='https://api.bybit.com/v5/market/kline'
    )

    BIN_SIZE: int = Field(
        default=50
    )
    TRADES_LIMIT: int = Field(
        default=1000
    )

    SMA_PERIOD: int = Field(
        default=10
    )
    SMA_INTERVAL: str = Field(
        default='1'
    )

    AD_LIMIT: str = Field(
        default=50
    )
    AD_INTERVAL: str = Field(
        default='15'
    )

    INTERVAL: str = Field(
        default='60'
    )
    LIMIT: int = Field(
        default=48
    )

    LOG_DIR: Path = Field(default=Path('logs'))
    LOG_FILE: Path = Field(default=Path('logs/service.log'))

    TTL_DEFAULT: int = Field(
        default=300
    )
    
    TTL_RSL: int = Field(
        default=120
    )
    TTL_MACD: int = Field(
        default=120
    )
    TTL_AD_TREND: int = Field(
        default=300
    )
    TTL_SMA_TREND: int = Field(
        default=300
    )
    TTL_BOLLINGER: int = Field(
        default=180
    )
    TTL_CANDLESTICK_DATA: int = Field(
        default=10
    )
    TTL_VOLUME_CLUSTERS: int = Field(
        default=300
    )
    TTL_VOLATILITY_DATA: int = Field(
        default=300
    )
    TTL_FIBONACCI_LEVELS: int = Field(
        default=300
    )
    TTL_SUPPORT_RESISTANCE_LEVELS: int = Field(
        default=300
    )

    class Config:
        case_sensitive = False


settings = Settings.parse_obj(environ)
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
