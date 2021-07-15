import pandas as pd
import matplotlib.pyplot as plt

from zipline.finance.commission import PerShare
from zipline.api import set_commission, symbol, order_target_percent
import zipline
from utils.scoring import momentum_score
from optimizers.optimizers import Optimizer
# ------------ Define parameters
# context.index_members = pd.read_csv(
#     '/Users/sherrytp/OneDrive/Eonum/ALGOFin/Trading Evolved/data/sp500.csv', index_col=0, parse_dates=[0])
# [context.index_members.index < today].iloc[-1, 0].split(',')

class LiveMomentum:
    def __init__(self, stocks_df, etf_df, mom1, long, etf, min_long_mom, etf_mom,
                 mom2=None, max_short_mom=None, short=None):
        """
        Calculate portfolio allocation for given equities and ETFs based on momentum strategy
        :param stocks_df: pandas dataframe
        :param etf_df: pandas dataframe
        :param mom1: int, rolling window length
        :param long: int, number of equities to long
        :param etf: int, number of etfs to long
        :param min_long_mom: int, minimum momentum for a equity to be considered longing
        :param etf_mom: int, minimum momentum for an ETF to be considered longing
        :param mom2: int, default None, second rolling window length; if specify a number,
        the momentum will be the average of mom1 and mom2
        :param max_short_mom: int, maximum momentum for a equity to be considered shorting
        :param short: int, number of equities to short
        """
        if max_short_mom:
            if not short:
                raise Exception('When max_short_mom arg is specified, short arg should be specified too.')
            else:
                self.maximum_short_momentum = max_short_mom
                self.short = short
        else:
            self.maximum_short_momentum = max_short_mom

        self.df = stocks_df

        self.minimum_long_momentum = min_long_mom

        mom1_equity = stocks_df[-mom1:].copy().apply(momentum_score)

        self.etf_list = etf_df[-mom1:].copy().apply(momentum_score)

        if not mom2:
            self.momentum_combine_list = mom1_equity.apply(momentum_score)
        else:
            mom2_equity = stocks_df[-mom2:].copy()
            self.momentum_combine_list = pd.concat([mom1_equity, mom2_equity.apply(momentum_score)])
            mom2_etf = etf_df[-mom2:].copy().apply(momentum_score)
            self.etf_list = pd.concat([self.etf_list, mom2_etf])

        self.long = long

        self.etf_df = etf_df
        self.etf = etf
        self.etf_mom = etf_mom

    def equity_order_list(self):
        # Make momentum ranking table
        ranking_table = self.momentum_combine_list.groupby(self.momentum_combine_list.index).mean() \
            .sort_values(ascending=False)

        buy_list = ranking_table[:self.long]
        short_list = ranking_table[-self.short:]

        # Stocks that pass the requirement
        final_buy_list = buy_list[buy_list > self.minimum_long_momentum]
        final_short_list = short_list[short_list < self.maximum_short_momentum]

        finalized_list_tuples = pd.concat([final_buy_list, final_short_list]).index

        return self.df.loc[:, finalized_list_tuples].copy()

    def etf_order_list(self):
        # Make momentum ranking table
        ranking_table = self.etf_list.groupby(self.etf_list.index).mean() \
            .sort_values(ascending=False)

        buy_list = ranking_table[:self.etf]

        final_buy_list = buy_list[buy_list > self.etf_mom].index

        return self.etf_df.loc[:, final_buy_list].copy()

    def risk_model(self, target_volatility=0.10,
                   weight_bounds=(-0.075, 0.075),
                   market_neutral=True,
                   gamma=1e-2,
                   verbose=False):
        """
        :param target_volatility: float, default 0.1
        :param weight_bounds: tuple
        :param market_neutral: bool, default True
        :param gamma: float
        :param verbose: bool, default fALSE
        :return: tuple, 1st is a dictionary of the equities to long or short;
        2nd is a dictionary of the ETFs to long
        """

        opt_equity_target = self.equity_order_list()
        opt_etf_target = self.etf_order_list()

        if not opt_equity_target.columns.empty:
            opt = Optimizer(opt_equity_target)
            equity_weights = opt.long_short_opt(target_volatility=target_volatility,
                                                weight_bounds=weight_bounds,
                                                verbose=verbose,
                                                market_neutral=market_neutral,
                                                gamma=gamma)
        else:
            equity_weights = {}
            print('No equities satisfy momentum requirement...')

        if not opt_etf_target.columns.empty:
            opt1 = Optimizer(opt_etf_target)
            etf_weights = opt1.max_sharpe_ratio_opt()
        else:
            etf_weights = {}
            print('No ETFs satisfy momentum requirement...')

        return equity_weights, etf_weights

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
