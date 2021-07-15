import zipline
import pandas as pd
from zipline.finance.commission import PerShare
from zipline.api import set_commission, symbol
from datetime import date, timedelta
from iexfinance.stocks import get_historical_data, Stock

from utils.process_iex_df import transform_df
from models.live_momentum import LiveMomentum

with open('/Users/Eonum/live_model/EoUniverse/data/stock_list.txt', 'r') as f:
    data = f.read().split()
    stocks = data

tickers = data[:20]
etf_list = tickers[15:]
start = pd.Timestamp('2020-3-22', tz='utc')
end = pd.Timestamp('2020-4-30', tz='utc')
iex_token = "pk_b1f2c995169a416a9f6c810698fc5d7f"


def initialize(context):
    context.momemtum_window = 5
    context.momemtum_window2 = 10

    context.min_long_momentum = 60
    context.max_short_momentum = -10

    context.long = 15
    context.short = 15
    context.etfs = 5

    comm_model = PerShare(cost=0.0005)
    set_commission(comm_model)


def handle_data(context, data):
    equity_symbols = [symbol(i) for i in tickers]
    etf_symbols = [symbol(i) for i in etf_list]

    hist_window = max(context.momemtum_window, context.momemtum_window2)

    equity_hist = data.history(equity_symbols, 'close', hist_window, "1d").copy()
    etf_hist = data.history(etf_symbols, 'close', hist_window, "1d").copy()

    equity_hist_ = equity_hist.rename(columns={col: col.symbol for col in equity_hist.columns})
    etf_hist_ = etf_hist.rename(columns={col: col.symbol for col in etf_hist.columns})

    print(etf_hist_)


perf = zipline.run_algorithm(start=start,
                             end=end,
                             initialize=initialize,
                             capital_base=100000,
                             handle_data=handle_data,
                             bundle='sep')

today = date.today()
start = today - timedelta(days=60)
today = today - timedelta(days=1)
start_date = "{}-{}-{}".format(start.year, start.month, start.day)
today = "{}-{}-{}".format(today.year, today.month, today.day)

df = get_historical_data(stocks[:20],
                         start,
                         today,
                         close_only=True,
                         output_format='pandas',
                         token=iex_token)

processed_df = transform_df(df)
etf_df = processed_df.loc[:, 'AAPL':'INTC'].copy()


if __name__ == '__main__':
    live = LiveMomentum(processed_df,
                        etf_df,
                        etf_mom=300,
                        mom1=20,
                        mom2=40,
                        min_long_mom=20,
                        max_short_mom=-2,
                        long=10,
                        short=5,
                        etf=5)

    print(live.risk_model())
