#!/usr/bin/env python
# coding: utf-8

# In[4]:


get_ipython().run_line_magic('matplotlib', 'notebook')

import zipline
from zipline.api import future_symbol,      set_commission, set_slippage, schedule_function, date_rules,     time_rules, continuous_future, order_target
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib
import pyfolio as pf
import pandas as pd
import numpy as np
from zipline.finance.commission import PerShare, PerTrade, PerContract
from zipline.finance.slippage import VolumeShareSlippage,     FixedSlippage, VolatilityVolumeShare

"""
Model Settings
"""
starting_portfolio = 10000000
risk_factor = 0.001
vola_window = 60
short_trend_window = 125
long_trend_window = 250

"""
Prepare for dynamic chart
"""
dynamic_results = pd.DataFrame()
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111)
ax.set_title('Time Return Performance')


def initialize(context):
    """
    Cost Settings
    """
    context.enable_commission = True
    context.enable_slippage = True    
    
    if context.enable_commission:
        comm_model = PerContract(cost=0.85, exchange_fee=1.5)
    else:
        comm_model = PerTrade(cost=0.0)
        
    set_commission(us_futures=comm_model)
    
    if context.enable_slippage:
        slippage_model=VolatilityVolumeShare(volume_limit=0.2)
    else:
        slippage_model=FixedSlippage(spread=0.0)      
        
    set_slippage(us_futures=slippage_model)
    
    currencies = [
        'AD',
        'BP',
        'CD',
        'CU',
        'DX',
        'JY',
        'NE',
        'SF',
    ]
    agriculturals = [
        'BL',
        'BO',
        '_C',
        'CC',
        'CT',
        'FC',
        'KC',
        'LB',
        'LC',
        'LR',
        'LS',
        '_O',
        '_S',
        'SB',
        '_W',
    ]
    nonagriculturals = [
        'CL',
        'GC',
        'HG',
        'HO',
        'LG',
        'NG',
        'PA',
        'PL',
        'RB',
        'SI',
    ]
    equities = [
        'ES',
        'NK',
        'NQ',
        'TW',
        'VX',
        'YM',
    ]
    rates = [
        'ED',
        'FV',
        'TU',
        'TY',
        'US',
    ]
    
    # Join sector lists into one list
    markets = currencies + agriculturals + nonagriculturals + equities + rates 
    
    # Make a list of all continuations
    context.universe = [
        continuous_future(market, offset=0, roll='volume', adjustment='mul')
            for market in markets
    ]
    
    # Schedule daily trading 
    schedule_function(rebalance, date_rules.month_start(), time_rules.market_close())
    
    # Schedule daily roll check
    schedule_function(roll_futures,date_rules.every_day(), time_rules.market_close())
    
    # Schedule monthly chart update
    schedule_function(update_chart,date_rules.month_start(), time_rules.market_close())
    
def update_chart(context,data):
    # This function continuously update the graph during the backtest
    today = data.current_session.date()
    dynamic_results.loc[today, 'PortfolioValue'] = context.portfolio.portfolio_value
    
    if ax.lines: # Update existing line
        ax.lines[0].set_xdata(dynamic_results.index)
        ax.lines[0].set_ydata(dynamic_results.PortfolioValue)
    else: # Create new line
        ax.semilogy(dynamic_results)
        
    # Update scales min/max
    ax.set_ylim(
        dynamic_results.PortfolioValue.min(),
        dynamic_results.PortfolioValue.max()
    )
    ax.set_xlim(
        dynamic_results.index.min(),
        dynamic_results.index.max()
    )
    
    # Redraw the graph
    fig.canvas.draw()

def roll_futures(context,data):
    today = data.current_session.date()
    open_orders = zipline.api.get_open_orders()
    for held_contract in context.portfolio.positions:
        if held_contract in open_orders:
            continue
        days_to_auto_close = (held_contract.auto_close_date.date() - today).days
        if days_to_auto_close > 10:
            continue    
            
        # Make a continuation
        continuation = continuous_future(
                held_contract.root_symbol, 
                offset=0, 
                roll='volume', 
                adjustment='mul'
                )
        continuation_contract = data.current(continuation, 'contract')
        
        if continuation_contract != held_contract:
            pos_size = context.portfolio.positions[held_contract].amount
            order_target(held_contract, 0)
            order_target(continuation_contract, pos_size)

def position_size(portfolio_value, std, pv, avg_volume):
    target_variation = portfolio_value * risk_factor
    contract_variation = std * pv
    contracts = target_variation / contract_variation
    return int(np.nan_to_num(contracts))

def rebalance(context, data):
    # Get the history
    hist = data.history(
        context.universe, 
        fields=['close', 'volume'], 
        frequency='1d', 
        bar_count=long_trend_window,
    ) 
    
    # Make a dictionary of open positions
    open_pos = {pos.root_symbol: pos for pos in context.portfolio.positions} 
    
    # Loop all markets
    for continuation in context.universe:
        # Slice off history for this market
        h = hist.xs(continuation, 2)
        root = continuation.root_symbol
        
        # Calculate volatility
        std = h.close.diff()[-vola_window:].std()
        
        if root in open_pos: # Position is already open
            p = context.portfolio.positions[open_pos[root]]
            if p.amount > 0: # Long position
                if h.close[-1] < h.close[-long_trend_window]:
                    # Lost slow trend, close position
                    order_target(open_pos[root], 0)
                elif h.close[-1] < h.close[-short_trend_window]:
                    # Lost fast trend, close position
                    order_target(open_pos[root], 0)
            else: # Short position
                if h.close[-1] > h.close[-long_trend_window]:
                    # Lost slow trend, close position
                    order_target(open_pos[root], 0)
                elif h.close[-1] > h.close[-short_trend_window]:
                    # Lost fast trend, close position
                    order_target(open_pos[root], 0)
        
        else:   # No position open yet.   
            if (h.close[-1] > h.close[-long_trend_window])                 and                 (h.close[-1] > h.close[-short_trend_window]):
                    # Buy new position
                    contract = data.current(continuation, 'contract')
                    contracts_to_trade = position_size(                                            context.portfolio.portfolio_value,                                            std,                                            contract.price_multiplier,                                            h['volume'][-20:].mean())
                
                    order_target(contract, contracts_to_trade)
            elif (h.close[-1] < h.close[-long_trend_window])                 and                 (h.close[-1] < h.close[-short_trend_window]):
                    # New short position
                    contract = data.current(continuation, 'contract')
                    contracts_to_trade = position_size(                                            context.portfolio.portfolio_value,                                            std,                                            contract.price_multiplier,                                            h['volume'][-20:].mean())

                    order_target(contract, contracts_to_trade *-1)

start = datetime(2001, 1, 1, 8, 15, 12, 0, pytz.UTC)
end = datetime(2018, 12, 31, 8, 15, 12, 0, pytz.UTC)

perf = zipline.run_algorithm(
    start=start, end=end, 
    initialize=initialize, 
    capital_base=starting_portfolio,  
    data_frequency = 'daily', 
    bundle='futures' )


# In[5]:


get_ipython().run_line_magic('matplotlib', 'inline')
returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
pf.create_returns_tear_sheet(returns, benchmark_rets=None)


# In[6]:


perf.portfolio_value.to_csv('time_return.csv')

