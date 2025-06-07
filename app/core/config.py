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

    LOG_DIR: Path = Field(default=Path('logs'))
    LOG_FILE: Path = Field(default=Path('logs/service.log'))

    class Config:
        case_sensitive = False


settings = Settings.parse_obj(environ)
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)