from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions, discrete_allocation
from zipline.api import order, symbol, schedule_function, order_target_percent, get_datetime, date_rules, time_rules
from zipline.finance import commission, slippage
from zipline import run_algorithm
from zipline.errors import SymbolNotFound
import numpy as np
import pandas as pd
import pyfolio as pf
import matplotlib.pyplot as plt
from utils.scoring import momentum_score

inv_members = 30
momentum_window = 125
min_momentum = 40
vola_window = 20

##### Initialization and trading logic - Commission and Slippage Settings
def initialize(context, enable_slippage=False, slippage_vol_limit=0.025, slippage_impact=0.05):
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
    schedule_function(func=rebalance, date_rule=date_rules.every_day(), time_rule=time_rules.market_open())


def rebalance(context, data):
    """
    Execute orders according to schedule_function date and time rules
    1. beta ranking to filter out stocks outside of beta_threshold range
    2. build universe of tickers to trade with
    3. Ranking consists of momentum_0.8 + simplebeta_rank * 0.2).rank()
    4. maximum sharpe ratio and minimum volatility
    """
    today_universe = []
    del_list = []
    for ticker in context.index_members.get_values():
        try:
            today_universe.append(symbol(ticker[0]))
        except SymbolNotFound:
            del_list.append(ticker[0])
    print(get_datetime().date(), 'Tickers taken care of ', del_list, '; total tickers of universe: ', len(today_universe))
    prices = data.history(today_universe, 'close', momentum_window, '1d')
    ranking_table = prices.apply(momentum_score).sort_values(ascending=False)

    # Stock Selection Logic #
    kept_positions = list(context.portfolio.positions.keys())
    # Sell Logic #
    for security in context.portfolio.positions:
        if security not in today_universe:
            order(security, 0.0)
            kept_positions.remove(security)
        elif ranking_table[security] < min_momentum:
            order(security, 0.0)
            kept_positions.remove(security)

    replacement_stocks = inv_members - len(kept_positions)
    buy_list = ranking_table.loc[~ranking_table.index.isin(kept_positions)][:replacement_stocks]
    new_portfolio = pd.concat((buy_list, ranking_table.loc[ranking_table.index.isin(kept_positions)]))
    opt_portfolio = prices[new_portfolio.index].fillna(method='ffill')
    """
    optimization of max sharpe and min volatility
    Several optimization methods to test: 
    1. ef.max_sharpe() is old method, giving out beta=~8 but neg beta and return not good 
    2. ef.efficient_return of 0.2 and market neutral, giving out beta=~11 and neg beta, sharpe=10
    3. ef_efficient_risk and market neutral of 0.25, the best one so far beta=~-6.83 and negative most, sharpe=1.6
    4. ef.min_volatility().efficient_risk(target_volatility, market_neutral=True), beta=~9, sharpe=4
    # historical_returns = expected_returns.returns_from_prices(prices[new_portfolio.index)
    5. target_volatility=0.4 to get a positive beta 
    6. change the expected returns and cov_matrix with target_volatility around 0.2
    """
    mu = expected_returns.mean_historical_return(opt_portfolio, frequency=252)
    s = risk_models.CovarianceShrinkage(opt_portfolio, frequency=252).ledoit_wolf()
    ef = EfficientFrontier(mu, s, weight_bounds=(0, 0.075))
    try:
        ef.add_objective(objective_functions.L2_reg, gamma=1.0)
        weights = ef.efficient_risk(target_volatility=0.4, market_neutral=True)
        # ef.min_volatility()  # np.array([ef.max_sharpe()])  efficient_return(target_return=0.2, market_neutral=True)
        print(weights)
        da = discrete_allocation.DiscreteAllocation(weights, total_portfolio_value=100000000,
                                                    latest_prices=discrete_allocation.get_latest_prices(opt_portfolio))
        buy_allocation, _ = da.lp_portfolio()
        print(buy_allocation)
        for security in buy_allocation.keys():
            if security in kept_positions:
                print(security, buy_allocation[security])
                order(security, buy_allocation[security])
            elif ranking_table[security] > min_momentum:
                order(security, buy_allocation[security])
    except ValueError and TypeError:
        print('Not enough data for calculating, Volatile Market of Date: ', get_datetime().date())


def analyze(context, perf):
    perf['max'] = perf.portfolio_value.cummax()
    perf['dd'] = perf.portfolio_value / perf['max'] - 1
    maxdd = perf['dd'].min()
    yr_ret = (np.power((perf.portfolio_value.iloc[-1] / perf.portfolio_value.iloc[0]), (252/len(perf)))) - 1
    # Use PyFolio to generate a performance report
    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
    pf.create_returns_tear_sheet(returns=returns,
                                 live_start_date='2020-01-01',
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


perf = run_algorithm(start=pd.Timestamp('2016-1-1', tz='utc'), end=pd.Timestamp('2020-7-1', tz='utc'),
                     initialize=initialize,
                     analyze=analyze,
                     capital_base=100000000,
                     benchmark_returns=get_benchmark('SPY', pd.Timestamp('2016-1-1', tz='utc'),
                                                     end=pd.Timestamp('2020-10-1', tz='utc')),
                     data_frequency='daily',
                     bundle='sep')
# 2016-6-8 Failed with solver: cvxpy.error.SolverError: Solver 'ECOS' failed. Try another solver, or solve with verbose=True for more information.