#!/usr/bin/env python
# coding: utf-8

# In[3]:

import zipline
from zipline.api import order_target_percent, symbol,      set_commission, set_slippage, schedule_function, date_rules, time_rules
from datetime import datetime
import pytz
import pandas as pd
import numpy as np  
from scipy import stats  
from zipline.finance.commission import PerDollar
from zipline.finance.slippage import VolumeShareSlippage, FixedSlippage

"""
Model Settings
"""
intial_portfolio = 10000000
momentum_window = 125
minimum_momentum = 40
portfolio_size = 30
vola_window = 20

"""
Commission and Slippage Settings
"""
enable_commission = True
commission_pct = 0.001
enable_slippage = True 
slippage_volume_limit = 0.25
slippage_impact = 0.1

"""
Helper functions.
"""

def momentum_score(ts):
    """
    Input:  Price time series.
    Output: Annualized exponential regression slope, 
            multiplied by the R2
    """
    # Make a list of consecutive numbers
    x = np.arange(len(ts)) 
    # Get logs
    log_ts = np.log(ts) 
    # Calculate regression values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_ts)
    # Annualize percent
    annualized_slope = (np.power(np.exp(slope), 252) - 1) * 100
    #Adjust for fitness
    score = annualized_slope * (r_value ** 2)
    return score

def volatility(ts):
    return ts.pct_change().rolling(vola_window).std().iloc[-1]

def output_progress(context):
    """
    Output some performance numbers during backtest run
    This code just prints out the past month's performance
    so that we have something to look at while the backtest runs.
    """
    
    # Get today's date
    today = zipline.api.get_datetime().date()
    
    # Calculate percent difference since last month
    perf_pct = (context.portfolio.portfolio_value / context.last_month) - 1
    
    # Print performance, format as percent with two decimals.
    print("{} - Last Month Result: {:.2%}".format(today, perf_pct))
    
    # Remember today's portfolio value for next month's calculation
    context.last_month = context.portfolio.portfolio_value

"""
Initialization and trading logic
"""
def initialize(context):
   
    # Set commission and slippage.
    if enable_commission:
        comm_model = PerDollar(cost=commission_pct)
    else:
        comm_model = PerDollar(cost=0.0)
    set_commission(comm_model)
    
    if enable_slippage:
        slippage_model=VolumeShareSlippage(volume_limit=slippage_volume_limit, price_impact=slippage_impact)
    else:
        slippage_model=FixedSlippage(spread=0.0)   
    set_slippage(slippage_model)    
    
    # Used only for progress output.
    context.last_month = intial_portfolio
    
    # Fetch and store index membership
    context.index_members = pd.read_csv('/Users/sherrytp/OneDrive/Eonum/ALGOFin/Trading Evolved/data/sp500.csv', index_col=0, parse_dates=[0])
    
    #Schedule rebalance monthly.
    schedule_function(
        func=rebalance,
        date_rule=date_rules.month_start(),
        time_rule=time_rules.market_open()
    )
    
def rebalance(context, data):
    # Write some progress output during the backtest
    output_progress(context)
    
    # Ok, let's find which stocks can be traded today.

    # First, get today's date
    today = zipline.api.get_datetime()
    # There's your daily universe. But we could of course have done this in one go.
    del_list = []
    for ticker in context.index_members.loc[context.index_members.index < today].iloc[-1, 0].split(','):
        try:
            todays_universe = [symbol(ticker)]
            # Get historical data
            hist = data.history(todays_universe, "close", momentum_window, "1d")

            # Make momentum ranking table
            ranking_table = hist.apply(momentum_score).sort_values(ascending=False)

            """
            Sell Logic
            
            First we check if any existing position should be sold.
            * Sell if stock is no longer part of index.
            * Sell if stock has too low momentum value.
            """
            kept_positions = list(context.portfolio.positions.keys())
            for security in context.portfolio.positions:
                if (security not in todays_universe):
                    order_target_percent(security, 0.0)
                    kept_positions.remove(security)
                elif ranking_table[security] < minimum_momentum:
                    order_target_percent(security, 0.0)
                    kept_positions.remove(security)


            """
            Stock Selection Logic
            
            Check how many stocks we are keeping from last month.
            Fill from top of ranking list, until we reach the
            desired total number of portfolio holdings.
            """
            replacement_stocks = portfolio_size - len(kept_positions)
            buy_list = ranking_table.loc[
                ~ranking_table.index.isin(kept_positions)][:replacement_stocks]

            new_portfolio = pd.concat(
                (buy_list,
                 ranking_table.loc[ranking_table.index.isin(kept_positions)])
            )


            """
            Calculate inverse volatility for stocks, 
            and make target position weights.
            """
            vola_table = hist[new_portfolio.index].apply(volatility)
            inv_vola_table = 1 / vola_table
            sum_inv_vola = np.sum(inv_vola_table)
            vola_target_weights = inv_vola_table / sum_inv_vola

            for security, rank in new_portfolio.iteritems():
                weight = vola_target_weights[security]
                if security in kept_positions:
                    order_target_percent(security, weight)
                else:
                    if ranking_table[security] > minimum_momentum:
                        order_target_percent(security, weight)
        except:
            del_list.append(ticker)
    print('Delete tickers ', del_list)

def analyze(context, perf):
    
    perf['max'] = perf.portfolio_value.cummax()
    perf['dd'] = (perf.portfolio_value / perf['max']) - 1
    maxdd = perf['dd'].min()
    
    ann_ret = (np.power((perf.portfolio_value.iloc[-1] / perf.portfolio_value.iloc[0]),(252 / len(perf)))) - 1
    
    print("Annualized Return: {:.2%} Max Drawdown: {:.2%}".format(ann_ret, maxdd))

    return   


start = pd.Timestamp('2017-3-1', tz='utc')
end = pd.Timestamp('2018-12-31', tz='utc')
perf = zipline.run_algorithm(
    start=start, end=end, 
    initialize=initialize, 
    analyze=analyze, 
    capital_base=intial_portfolio,  
    data_frequency='daily',
    bundle='sep')


# In[46]:


data = perf['portfolio_value'].copy()
data.index = data.index.date

# data.to_csv('systematic_momentum.csv')
#
#
# # In[2]:
#
#
# returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
# pf.create_returns_tear_sheet(returns, benchmark_rets=None)
# perf.portfolio_value.to_csv('125d version.csv')

