    # This is a sample mean-reversion algorithm on Quantopian for you to test and adapt.

# Algorithm investment thesis:
# Top-performing stocks from last week will do worse this week, and vice-versa.

# Every Monday, we rank high-volume stocks based on their previous 5 day returns.
# We go long the bottom 20% of stocks with the WORST returns over the past 5 days.
# We go short the top 20% of stocks with the BEST returns over the past 5 days.

# This type of algorithm may be used in live trading and in the Quantopian Open.

# Import the libraries we will use here
from zipline.api import get_open_orders
import numpy as np

# The initialize function is the place to set your tradable universe and define any parameters.
def initialize(context):
    # Use the top 1% of stocks defined by average daily trading volume.
    set_universe(universe.DollarVolumeUniverse(99, 100))

    # Set execution cost assumptions. For live trading with Interactive Brokers
    # we will assume a $1.00 minimum per trade fee, with a per share cost of $0.0075.
    set_commission(commission.PerShare(cost=0.0075, min_trade_cost=1.00))

    # Set market impact assumptions. We limit the simulation to
    # trade up to 2.5% of the traded volume for any one minute,
    # and  our price impact constant is 0.1.
    set_slippage(slippage.VolumeShareSlippage(volume_limit=0.025, price_impact=0.10))

    # Define the other variables
    context.long_leverage = 0.5
    context.short_leverage = -0.5
    context.lower_percentile = 20
    context.upper_percentile = 80
    context.returns_lookback = 5

    # Rebalance every Monday (or the first trading day if it's a holiday).
    # At 11AM ET, which is 1 hour and 30 minutes after market open.
    schedule_function(rebalance,
                      date_rules.week_start(days_offset=0),
                      time_rules.market_open(hours = 1, minutes = 30))

# The handle_data function is run every bar.
def handle_data(context,data):
    # Record and plot the leverage of our portfolio over time.
    record(leverage = context.account.leverage)

    # We also want to monitor the number of long and short positions
    # in our portfolio over time. This loop will check our positition sizes
    # and add the count of longs and shorts to our plot.
    longs = shorts = 0
    for position in context.portfolio.positions.itervalues():
        if position.amount > 0:
            longs += 1
        if position.amount < 0:
            shorts += 1
    record(long_count=longs, short_count=shorts)

# This rebalancing is called according to our schedule_function settings.
def rebalance(context,data):
    # Get the last N days of prices for every stock in our universe.
    prices = history(context.returns_lookback, '1d', 'price')

    # Calculate the past 5 days' returns for each security.
    returns = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]

    # Remove stocks with missing prices.
    # Remove any stocks we ordered last time that still have open orders.
    # Get the cutoff return percentiles for the long and short portfolios.
    returns = returns.dropna()
    open_orders = get_open_orders()
    if open_orders:
        eligible_secs = [sec for sec in data if sec not in open_orders]
        returns = returns[eligible_secs]

    # Lower percentile is the threshhold for the bottom 20%, upper percentile is for the top 20%.
    lower, upper = np.percentile(returns, [context.lower_percentile,
                                           context.upper_percentile])

    # Select the X% worst performing securities to go long.
    long_secs = returns[returns <= lower]

    # Select the Y% best performing securities to short.
    short_secs = returns[returns >= upper]

    # Set the allocations to even weights in each portfolio.
    long_weight = context.long_leverage / len(long_secs)
    short_weight = context.short_leverage / len(short_secs)

    for security in data:

        # Buy/rebalance securities in the long leg of our portfolio.
        if security in long_secs:
            order_target_percent(security, long_weight)

        # Sell/rebalance securities in the short leg of our portfolio.
        elif security in short_secs:
            order_target_percent(security, short_weight)

        # Close any positions that fell out of the list of securities to long or short.
        else:
            order_target(security, 0)

    log.info("This week's longs: "+", ".join([long_.symbol for long_ in long_secs.index]))
    log.info("This week's shorts: "  +", ".join([short_.symbol for short_ in short_secs.index]))
