from core.logger import root

from pandas import DataFrame, Timedelta, to_datetime


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

            df.set_index('open_time', inplace=True)
            df = df.sort_index()

            df = df.astype(float)[['open', 'high', 'low', 'close', 'volume']]

            df = df.loc[
                df.index[-1] - Timedelta(hours=hours):df.index[-1]
            ]

            return df

        except Exception as _ex:
            root.error(
                f"DataProvider parsing error: {_ex}" 
            )

            return DataFrame()
