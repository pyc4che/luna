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

    CACHE_RSI_TTL: int = Field(
        default=90
    )
    CACHE_MACD_TTL: int = Field(
        default=120
    )
    CACHE_DEFAULT_TTL: int = Field(
        default=60
    )
    CACHE_BOLLINGER_TTL: int = Field(
        default=180
    )

    def get_ttl(self, key: str, default: int = None) -> int:
        return getattr(self, key, default or self.CACHE_DEFAULT_TTL)


    class Config:
        case_sensitive = False


settings = Settings.parse_obj(environ)
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
