# This example runs the same momentum play as the first sample
# (https://www.quantopian.com/help#sample-basic), but this time it uses more
# securities during the backtest.

# Important note: All securities in an algorithm must be traded for the
# entire length of the backtest.  For instance, if you try to backtest both
# Google and Facebook against 2011 data you will get an error; Facebook
# wasn't traded until 2012.

# First step is importing any needed libraries.

import datetime
import pytz

def initialize(context):
    # Here we initialize each stock.
    # By calling symbols('AAPL', 'IBM', 'CSCO') we're storing the Security objects.
    context.stocks = symbols('AAPL', 'IBM', 'CSCO')
    context.vwap = {}
    context.price = {}

    # Setting our maximum position size, like previous example
    context.max_notional = 1000000.1
    context.min_notional = -1000000.0

    # Initializing the time variables we use for logging
    # Convert timezone to US EST to avoid confusion
    est = pytz.timezone('US/Eastern')
    context.d=datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=est)


def handle_data(context, data):
    # Initializing the position as zero at the start of each frame
    notional=0

    # This runs through each stock.  It computes
    # our position at the start of each frame.
    for stock in context.stocks:
        price = data[stock].price
        notional = notional + context.portfolio.positions[stock].amount * price
        tradeday = data[stock].datetime

    # This runs through each stock again.  It finds the price and calculates
    # the volume-weighted average price.  If the price is moving quickly, and
    # we have not exceeded our position limits, it executes the order and
    # updates our position.
    for stock in context.stocks:
        vwap = data[stock].vwap(3)
        price = data[stock].price

        if price < vwap * 0.995 and notional > context.min_notional:
            order(stock,-100)
            notional = notional - price*100
        elif price > vwap * 1.005 and notional < context.max_notional:
            order(stock,+100)
            notional = notional + price*100

    # If this is the first trade of the day, it logs the notional.
    if (context.d + datetime.timedelta(days=1)) < tradeday:
        log.debug(str(notional) + ' - notional start ' + tradeday.strftime('%m/%d/%y'))
        context.d = tradeday
