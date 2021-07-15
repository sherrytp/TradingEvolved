from zipline.api import symbol, schedule_function, order_target_percent, get_datetime, date_rules, time_rules
from zipline.finance import commission, slippage
from zipline import run_algorithm
from zipline.errors import SymbolNotFound
import pickle
import numpy as np
import pandas as pd
import pyfolio as pf
import matplotlib.pyplot as plt
from utils.scoring import momentum_score
from ranking_models.momentum import MomentumRankingModel
##### Initialization and trading logic - Commission and Slippage Settings
def initialize(context, enable_slippage=False, slippage_vol_limit=0.025, slippage_impact=0.05):
    context.momentum_window = 60
    context.momentum_window2 = 125

    context.min_long_momentum = 60
    context.min_long_etf_momentum = 5
    context.max_short_momentum = None

    context.long = 100
    context.short = None
    context.etfs = 20

    context.sector = True
    context.l2 = True
    context.weight_bounds = (0.0, 0.075)
    context.etf_weight_bounds = (0, 0.1)

    context.capital = 100000000
    context.equity_allocation = (0.7 - 0.05) * context.capital
    context.etf_allocation = (1 - 0.7) * context.capital

    context.trend_filter_symbol = symbol('SPY')
    context.trend_window_length = 125

    if enable_slippage:
        slippage_model = slippage.VolumeShareSlippage(volume_limit=slippage_vol_limit, price_impact=slippage_impact)
    else:
        slippage_model = slippage.FixedSlippage(spread=0)
    context.set_slippage(slippage_model)
    context.set_commission(commission.PerShare(cost=0.0005, min_trade_cost=None))
    context.index_members = pd.read_csv('../ml4t_data/russell3000.csv', index_col=0)
    context.sectors = pd.read_csv('../ml4t_data/russell3000_sectors.csv')
    context.etfs = ['SPY', 'IWM', 'QQQ', 'GLD', 'MDY', 'EEM', 'EFA', 'HYG', 'TLT', 'GDX', 'DIA', 'IYR', 'XOP', 'SMH',
                    'EWJ', 'VNQ', 'XRT', 'IBB', 'FEZ', 'PFF', 'XHB', 'XLF', 'XLI', 'XLK', 'XLP', 'XME', 'XLU', 'XLV',
                    'XLY', 'SHY', 'FXI', 'XBI', 'XLB', 'IEF']
    # Schedule rebalance monthly to ensure turnover*2
    schedule_function(func=handle_data, date_rule=date_rules.every_day(), time_rule=time_rules.market_open(minutes=30))


def handle_data(context, data):
    today_universe = []
    del_list = []
    for ticker in context.index_members.get_values():
        try:
            today_universe.append(symbol(ticker[0]))
        except SymbolNotFound:
            del_list.append(ticker[0])
    print(get_datetime().date(), 'Tickers taken care of ', del_list, '; total tickers of universe: ', len(today_universe))
    equity_allocation = context.portfolio.portfolio_value * (0.7 - 0.05)
    # Find the rolling window size
    hist_window = max(context.momentum_window, context.momentum_window2)
    prices = data.history(today_universe, 'close', hist_window, '1d')
    ranking_table = prices.apply(momentum_score).sort_values(ascending=False)
    equity_hist = prices.rename(columns={col: col.symbol for col in prices.columns})
    etf_prices = data.history([symbol(i) for i in context.etfs], 'close', hist_window, '1d')
    etf_hist = etf_prices.rename(columns={col: col.symbol for col in etf_prices.columns})
    # Risk model ranking and optimization
    live = MomentumRankingModel(equity_hist, etf_hist, mom1=context.momentum_window, mom2=context.momentum_window2,
                                min_long_mom=context.min_long_momentum, etf_mom=context.min_long_etf_momentum,
                                max_short_mom=context.max_short_momentum, long=context.long, short=context.short,
                                etf=context.etfs)
    equity, etf = live.risk_model(weight_bounds=context.weight_bounds, etf_weight_bounds=context.etf_weight_bounds,
                                  sector=context.sector, l2=context.l2)
    buy_list = list(equity.keys()) + list(etf.keys())
    with open('/Users/sherrytp/Desktop/buy_list.pickle') as f:
        pickle.dump(buy_list, f)

    for security in context.portfolio.positions:
        if security.symbol not in buy_list:
            order_target_percent(security, 0.0)

    if equity:
        for security, weight in equity.items():
            security = symbol(security)
            if data.can_trade(security):
                order_target_percent(security, weight * 0.7)
    if etf:
        for security, weight in etf.items():
            security = symbol(security)
            if data.can_trade(security):
                order_target_percent(security, weight * 0.3)


def analyze(context, perf):
    perf['max'] = perf.portfolio_value.cummax()
    perf['dd'] = perf.portfolio_value / perf['max'] - 1
    maxdd = perf['dd'].min()
    yr_ret = (np.power((perf.portfolio_value.iloc[-1] / perf.portfolio_value.iloc[0]), (252/len(perf)))) - 1
    # Use PyFolio to generate a performance report
    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
    pf.create_returns_tear_sheet(returns=returns,
                                 live_start_date='2019-10-01',
                                 benchmark_rets=None)
    plt.show()
    print('Annualized Return: {:.2%} ; Max Drawdown: {:.2%}'.format(yr_ret, maxdd))
    print('Pyfolio Return: {:.2%}\n'.format(returns.max()), positions)
    return


def get_benchmark(symbol=None, start=None, end=None):
    import pandas_datareader as pdr
    bm = pdr.get_data_yahoo(symbol, pd.Timestamp(start), pd.Timestamp(end))['Close']
    bm.index = bm.index.tz_localize('UTC')
    return bm.pct_change(periods=1).fillna(0)


perf = run_algorithm(start=pd.Timestamp('2020-1-1', tz='utc'), end=pd.Timestamp('2020-10-1', tz='utc'),
                     initialize=initialize,
                     analyze=analyze,
                     capital_base=100000000,
                     benchmark_returns=get_benchmark('SPY', pd.Timestamp('2020-1-1', tz='utc'),
                                                     end=pd.Timestamp('2020-10-1', tz='utc')),
                     data_frequency='daily',
                     bundle='sep')
