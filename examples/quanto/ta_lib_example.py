# This example algorithm uses the Relative Strength Index indicator as a buy/sell signal.
# When the RSI is over 70, a stock can be seen as overbought and it's time to sell.
# When the RSI is below 30, a stock can be seen as oversold and it's time to buy.

# Because this algorithm uses the history function, it will only run in minute mode.
# We will constrain the trading to once per day at market open in this example.

import talib
import numpy as np
import math

from zipline.api import history
# Setup our variables
def initialize(context):
    context.max_notional = 100000
    context.intc = symbol('INTC')   # Intel
    context.LOW_RSI = 30
    context.HIGH_RSI = 70

def handle_data(context, data):

    #Get a trailing window of data
    prices = history(15, '1d', 'price')


    # Use pandas dataframe.apply to get the last RSI value
    # for for each stock in our basket
    rsi_data = prices.apply(talib.RSI, timeperiod=14).iloc[-1]

    intc_rsi = rsi_data[context.intc]

    # check how many shares of Intel we currently own
    current_intel_shares = context.portfolio.positions[context.intc].amount

    # until 14 time periods have gone by, the rsi value will be numpy.nan

    # RSI is above 70 and we own GOOG, time to close the position.
    if intc_rsi > context.HIGH_RSI and current_intel_shares > 0:
        order_target(context.intc, 0)
        log.info('RSI is at ' + str(intc_rsi) + ', selling ' + str(current_intel_shares) + ' shares')

    # RSI is below 30 and we don't have any Intel stock, time to buy.
    elif intc_rsi < context.LOW_RSI and current_intel_shares == 0:
        num_shares = math.floor(context.max_notional / data[context.intc].close_price)
        order(context.intc, num_shares)
        log.info('RSI is at ' + str(intc_rsi) + ', buying ' + str(num_shares)  + ' shares')

    # record the current RSI value and the current price of INTC.
    record(intcRSI=intc_rsi, intcPRICE=data[context.intc].close_price)