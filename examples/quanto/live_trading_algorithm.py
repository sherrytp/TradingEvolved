'''
    This algorithm defines a long-only equal weight portfolio and
    rebalances it at a user-specified frequency.
    NOTE: This algo is intended to run in minute-mode simulation and is compatible with LIVE TRADING.

'''

# Import the libraries we will use here
import datetime
import pytz
import pandas as pd

def initialize(context):
    # This initialize function sets any data or variables
    # that you'll use in your algorithm.
    # You'll also want to define any parameters or values
    # you're going to use.

    # In our example, we're looking at 9 sector ETFs.
    context.secs = symbols('XLY',  # XLY Consumer Discrectionary SPDR Fund
                           'XLF',  # XLF Financial SPDR Fund
                           'XLK',  # XLK Technology SPDR Fund
                           'XLE',  # XLE Energy SPDR Fund
                           'XLV',  # XLV Health Care SPRD Fund
                           'XLI',  # XLI Industrial SPDR Fund
                           'XLP',  # XLP Consumer Staples SPDR Fund
                           'XLB',  # XLB Materials SPDR Fund
                           'XLU')  # XLU Utilities SPRD Fund

    # Change this variable if you want to rebalance less frequently
    context.Rebalance_Days = 21

    # These other variables are used in the algorithm for leverage, trade time, etc.
    # Rebalance at 10:15AM EST
    context.rebalance_date = None
    context.weights = 0.99/len(context.secs)
    context.rebalance_hour_start = 10
    context.rebalance_hour_end = 15

    # These are the default commission and slippage settings.  Change them to fit your
    # brokerage fees. These settings only matter for backtesting.  When you trade this
    # algorithm, they are moot - the brokerage and real market takes over.
    set_commission(commission.PerTrade(cost=0.03))
    set_slippage(slippage.VolumeShareSlippage(volume_limit=0.25, price_impact=0.1))

def handle_data(context, data):

    # Get the current exchange time, in the exchange timezone
    exchange_time = pd.Timestamp(get_datetime()).tz_convert('US/Eastern')

    # If it's a rebalance day (defined in intialize()) then rebalance:
    if  context.rebalance_date == None or exchange_time > context.rebalance_date + datetime.timedelta(days=context.Rebalance_Days):

        # Do nothing if there are open orders:
        if has_orders(context):
            print('has open orders - doing nothing!')
            return

        rebalance(context, data, exchange_time)

def rebalance(context, data, exchange_time):
    # Only rebalance if we are in the user specified rebalance time-of-day window
    if exchange_time.hour < context.rebalance_hour_start or exchange_time.hour > context.rebalance_hour_end:
       return

    # Do the rebalance. Loop through each of the stocks and order to the target
    # percentage.  If already at the target, this command doesn't do anything.
    # A future improvement could be to set rebalance thresholds.
    for sec in context.secs:
        order_target_percent(sec, context.weights, limit_price=None, stop_price=None)

    context.rebalance_date = exchange_time
    log.info("Rebalanced to target portfolio weights at %s" % str(exchange_time))

def has_orders(context):
    # Return true if there are pending orders.
    has_orders = False
    for sec in context.secs:
        orders = get_open_orders(sec)
        if orders:
            for oo in orders:
                message = 'Open order for {amount} shares in {stock}'
                message = message.format(amount=oo.amount, stock=sec)
                log.info(message)

            has_orders = True
    return has_orders