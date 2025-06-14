from core.logger import root

from numpy import inf, nan
from pandas import DataFrame, Timedelta, Series, to_datetime


class DataProvider:
    def to_dataframe(self, raw: list, hours: int = 48) -> DataFrame:
        try:
            df = DataFrame(
                raw,
                columns=[
                    'open_time', 'open', 'high',
                    'low', 'close', 'volume',
                    'turnover'
                ]
            )

            df['open_time'] = to_datetime(
                df['open_time'].astype('int64'), unit='ms'
            )

            df = df.sort_values(by='open_time')

            df = df.astype(float, errors='ignore')

            df = df.loc[
                df['open_time'] >= df['open_time'].max() - Timedelta(hours=hours)
            ]

            return df

        except Exception as _ex:
            root.error(
                f"DataProvider parsing error: {_ex}" 
            )

            return DataFrame()


    def safe_json(self, series: Series, subset: list) -> Series:
        return series.replace([inf, -inf], nan).dropna(subset=subset)
