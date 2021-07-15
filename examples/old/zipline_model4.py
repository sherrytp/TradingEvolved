import pytz
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import pandas_datareader.data as yahoo_reader

from zipline.utils.calendars import get_calendar
from zipline.api import order_target, symbol
from zipline.data import bundles
from zipline import run_algorithm


def get_benchmark(symbol=None, start=None, end=None):
    bm = yahoo_reader.DataReader(symbol,
                                 'yahoo',
                                 pd.Timestamp(start),
                                 pd.Timestamp(end))['Close']
    bm.index = bm.index.tz_localize('UTC')
    return bm.pct_change(periods=1).fillna(0)


def initialize(context):
    context.equity = symbol("AMZN")


def handle_data(context, data):
    order_target(context.equity, 100)


def before_trading_start(context, data):
    pass


def analyze(context, perf):
    ax1 = plt.subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    ax2 = plt.subplot(212, sharex=ax1)
    perf.sym.plot(ax=ax2, color='r')
    plt.gcf().set_size_inches(18, 8)
    plt.legend(['Algo', 'Benchmark'])
    plt.ylabel("Returns", color='black', size=25)


if __name__ == '__main__':
    bundle_name = 'quandl'
    bundle_data = bundles.load(bundle_name)

    # Set the trading calendar
    trading_calendar = get_calendar('NYSE')

    start = pd.Timestamp(datetime(2020, 1, 1, tzinfo=pytz.UTC))
    end = pd.Timestamp(datetime(2020, 11, 1, tzinfo=pytz.UTC))

    r = run_algorithm(start=start,
                      end=end,
                      initialize=initialize,
                      capital_base=100000,
                      handle_data=handle_data,
                      benchmark_returns=get_benchmark(symbol="SPY",
                                                      start=start.date().isoformat(),
                                                      end=end.date().isoformat()),
                      bundle='quandl',
                      broker=None,
                      state_filename="./demo.state",
                      trading_calendar=trading_calendar,
                      before_trading_start=before_trading_start,
                      #                   analyze=analyze,
                      data_frequency='daily'
                      )
    fig, axes = plt.subplots(1, 1, figsize=(16, 5), sharex=True)
    r.algorithm_period_return.plot(color='blue')
    r.benchmark_period_return.plot(color='red')

    plt.legend(['Algo', 'Benchmark'])
    plt.ylabel("Returns", color='black', size=20)
    plt.show()