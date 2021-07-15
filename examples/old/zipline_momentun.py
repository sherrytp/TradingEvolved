import pandas as pd
import matplotlib.pyplot as plt

from zipline.finance.commission import PerShare
from zipline.api import set_commission, symbol, order_target_percent
import zipline

from models.live_momentum import LiveMomentum

with open('/Users/landey/Desktop/Eonum/live_model/eouniverse/stock_list.txt', 'r') as f:
    data = f.read().split()

tickers = data[:20]
etf_list = tickers[15:]


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

    live = LiveMomentum(equity_hist_, etf_hist_, etf_mom=300, mom1=20, mom2=40,
                        min_long_mom=20, max_short_mom=-2, long=10,
                        short=5, etf=3)

    # print(equity_hist_)
    equity, etf = live.risk_model()

    if equity:
        for ticker, weight in equity.items():
            if data.can_trade(symbol(ticker)) and weight != 0:
                order_target_percent(symbol(ticker), weight)

    if etf:
        for ticker, weight in etf.items():
            if data.can_trade(symbol(ticker)) and weight != 0:
                order_target_percent(symbol(ticker), weight)


start = pd.Timestamp('2020-3-22', tz='utc')
end = pd.Timestamp('2020-4-28', tz='utc')

perf = zipline.run_algorithm(start=start,
                             end=end,
                             initialize=initialize,
                             capital_base=100000,
                             handle_data=handle_data,
                             bundle='sep')

perf.portfolio_value.plot()
plt.show()
