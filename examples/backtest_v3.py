from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions, discrete_allocation
from zipline.api import order, symbol, schedule_function, get_datetime, date_rules, time_rules, attach_pipeline, pipeline_output
from zipline.pipeline import Pipeline, CustomFactor, factors
from zipline.finance import commission, slippage
from zipline import run_algorithm
import numpy as np
import pandas as pd
import pyfolio as pf
import matplotlib.pyplot as plt
from zipline.errors import SymbolNotFound
from utils.scoring import momentum_score
import pickle

inv_members = 30
momentum_window = 125

##### Initialization and trading logic - Commission and Slippage Settings
def initialize(context, enable_slippage=False, slippage_vol_limit=0.025, slippage_impact=0.05):
    if enable_slippage:
        slippage_model = slippage.VolumeShareSlippage(volume_limit=slippage_vol_limit, price_impact=slippage_impact)
    else:
        slippage_model = slippage.FixedSlippage(spread=0)
    context.set_slippage(slippage_model)
    context.set_commission(commission.PerShare(cost=0.0005, min_trade_cost=None))
    context.index_members = pd.read_csv('../ml4t_data/russell3000.csv', index_col=0)
    context.sectors = pd.read_csv('../ml4t_data/russell3000_sectors.csv', index_col='ticker')
    attach_pipeline(make_pipeline(), 'my_pipeline')
    # Schedule rebalance monthly to ensure turnover*2
    schedule_function(func=rebalance, date_rule=date_rules.every_day(), time_rule=time_rules.market_open())


def make_pipeline():
    """
    Create a new column of simple beta calculated with a window of 125, compared to benchmark SPY.
    The other way is to create a new ranking of (your_existing_rank * 0.8 + simplebeta_rank * 0.2).rank()
    """
    beta = factors.SimpleBeta(target=symbol('SPY'), regression_length=momentum_window)
    pipe = Pipeline(columns={'beta': beta}, screen=None)
    return pipe


def rebalance(context, data):
    BETA_THRESHOLD = .25
    pipeline = pipeline_output('my_pipeline')
    beta_buy_list = pipeline[(np.abs(pipeline.beta) < BETA_THRESHOLD)]
    prices = data.history(beta_buy_list.index, 'price', momentum_window, '1d')
    prices.columns = [str(i).split('[')[1].split(']')[0] for i in prices.columns]
    sector_mapper = {i: context.sectors.loc[i, 'sector'] for i in context.sectors.index}
    for i in prices.columns:
        if i not in context.index_members:
            prices.drop(columns=i)
    mu = expected_returns.mean_historical_return(prices.fillna(method='ffill'), frequency=252)
    s = risk_models.sample_cov(prices.fillna(method='ffill'), frequency=252)
    ef = EfficientFrontier(mu, s, weight_bounds=(0, 0.075))
    print('Successful part1')
    try:
        ef.add_objective(objective_functions.L2_reg, gamma=1.0)
        weights = ef.efficient_risk(target_volatility=0.25, market_neutral=True)
        # output_weights = ef.add_sector_constraints(sector_mapper=sector_mapper,
        #                                            sector_lower={i: 0 for i in context.sectors.sector.unique()},
        #                                            sector_upper={i: 0.25 for i in context.sectors.sector.unique()})
        # ef.min_volatility()  # np.array([ef.max_sharpe()])  efficient_return(target_return=0.2, market_neutral=True)
        da = discrete_allocation.DiscreteAllocation(weights, total_portfolio_value=100000000,
                                                    latest_prices=discrete_allocation.get_latest_prices(prices))
        buy_allocation, _ = da.lp_portfolio()
        print(buy_allocation)
        for security in buy_allocation.keys():
            order(symbol(security), buy_allocation[security])
    except ValueError and TypeError:
        print('Not enough data for calculating, Volatile Market of Date: ', get_datetime().date())


def analyze(context, perf):
    perf['max'] = perf.portfolio_value.cummax()
    perf['dd'] = perf.portfolio_value / perf['max'] - 1
    maxdd = perf['dd'].min()
    yr_ret = (np.power((perf.portfolio_value.iloc[-1] / perf.portfolio_value.iloc[0]), (252/len(perf)))) - 1
    # Use PyFolio to generate a performance report
    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
    # pf.create_returns_tear_sheet(returns=returns,
    #                              live_start_date='2020-01-01',
    #                              benchmark_rets=None)
    plt.show()
    print('Annualized Return: {:.2%} ; Max Drawdown: {:.2%}'.format(yr_ret, maxdd))
    print('Pyfolio Return: {:.2%}\n'.format(returns.max()), positions)
    return


def get_benchmark(symbol=None, start=None, end=None):
    import pandas_datareader as pdr
    bm = pdr.get_data_yahoo(symbol, pd.Timestamp(start), pd.Timestamp(end))['Close']
    bm.index = bm.index.tz_localize('UTC')
    return bm.pct_change(periods=1).fillna(0)


perf = run_algorithm(start=pd.Timestamp('2016-1-1', tz='utc'), end=pd.Timestamp('2016-2-1', tz='utc'),
                     initialize=initialize,
                     analyze=analyze,
                     capital_base=100000000,
                     benchmark_returns=get_benchmark('SPY', pd.Timestamp('2016-1-1', tz='utc'),
                                                     end=pd.Timestamp('2016-2-1', tz='utc')),
                     data_frequency='daily',
                     bundle='sep')
