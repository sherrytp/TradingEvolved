from zipline.api import batch_transform, symbols
# This is the standard Quantopian function that initializes your data and
# variables. In it, we define how large of a 'bet' we're making (in dollars) and what
# stock we're working with.
def initialize(context):
    # we will be trading in AMZN and WMT shares
    context.stocks = symbols('AMZN', 'WMT')
    context.bet_amount = 100000
    context.long = 0

# This is the standard Quantopian event handling function. This function is
# run once for each bar of data.  In this example, it the min and max
# prices for the trailing window.  If the price exceeds the recent high, it
# goes short; if the price dips below the recent low, it goes long. The algo
# is a contrarian/mean reversion bet.
def handle_data(context, data):
    # Until our batch transform's datapanel is full, it will return None.  Once
    # the datapanel is full, then we have a max and min to work with.
    rval = minmax(data)

    if rval is None:
        return

    maximums, minimums = rval

    for stock in context.stocks:
        cur_max = maximums[stock]
        cur_min = minimums[stock]
        cur_price = data[stock].price
        cur_position = context.portfolio.positions[stock]

        order_direction = calculate_direction(stock, cur_min, cur_max, cur_price, cur_position)
        order_amount = calculate_order_amount(context, stock, order_direction, cur_price)

        # Optional: uncomment the log line below if you're looking for more detail about what's
        # going on.  It will log all the information that is a 'moving part' of this
        # algorithm. Note: if you're doing a full backtest it's a lot of log lines!
        logmsg = '\n{s}: max {m} min {i} price {p} position amount {l}\nordering {n} shares'
        log.info(logmsg.format(
            s=stock,
            m=cur_max,
            i=cur_min,
            p=cur_price,
            l=cur_position.amount,
            n=order_amount
        ))

        order(stock, order_amount)

# Here we do our test to see if we should buy or sell or do nothing.  This is
# the main part of the algorithm. Once we establish a position (long or short)
# we use the context.long variable to remember which we took.
def calculate_direction(stock, cur_min, cur_max, cur_price, cur_position):
    if cur_max is not None and cur_position.amount <= 0 and cur_price >= cur_max:
        return -1
    elif cur_min is not None and cur_position.amount >= 0 and cur_price <= cur_min:
        return 1

    return 0

# This method is purely for order management. It calculates and returns an
# order amount to place binary bets.
# If signal_val is -1, get to a short position of -1 * context.bet_size
# If signal_val is 1, get to a long position of context.bet_size
def calculate_order_amount(context, stock, signal_val, cur_price):
    current_amount = context.portfolio.positions[stock].amount
    abs_order_amount = int(context.bet_amount / cur_price)

    if signal_val == -1:
        return (-1 * abs_order_amount) - current_amount
    elif signal_val == 1:
        return abs_order_amount - current_amount
    else:
        return 0

# This is our batch transform decorator/declaration. We set the
# refresh_period and length of the window.  In this case, once per day we're loading
# the last 10 trading days and evaluating them.
@batch_transform(refresh_period=1, window_length=10)
def minmax(datapanel):
    # We are looking for the min and the max price to return. Just because it's interesting
    # we also are logging the current price.
    prices_df = datapanel['price']
    min_price = prices_df.min()
    max_price = prices_df.max()

    if min_price is not None and max_price is not None:
        return (max_price, min_price)
    else:
        return None

