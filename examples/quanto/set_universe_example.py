# This is the standard Quantopian function that initializes your data and
# variables. In it, we define how large of a 'bet' we're making (in dollars) and what
# stock we're working with.
def initialize(context):
    # we want to try this on a range of highly liquid stocks
    set_universe(universe.DollarVolumeUniverse(98, 99))
    context.bet_amount = 1000
    context.count = 20

# This is the standard Quantopian event handling function. This function is
# run once for each bar of data.  In this example, it the min and max
# prices for the trailing window.  If the price exceeds the recent high, it
# goes short; if the price dips below the recent low, it goes long. The algo
# is a contrarian/mean reversion bet.
def handle_data(context, data):
    # Until our batch transform's datapanel is full, it will return None.  Once
    # the datapanel is full, then we have a max and min to work with.

    prices = history(bar_count=10, frequency='1d', field='price')

    ranking = sort_returns(prices)

    if ranking is not None:
        column_name = ranking.columns[0]
        # bottom quantile to go long
        bottom = ranking[-1*context.count:]
        longs = bottom[bottom[column_name] < 0]

        # top quantile to go short
        top = ranking[:context.count]
        shorts = top[top[column_name] > 0]

        for stock in data.keys():
            if stock in longs.index:
                amount = calculate_order_amount(context, stock, 1, data[stock].price)
            elif stock in shorts.index:
                amount = calculate_order_amount(context, stock, -1, data[stock].price)
            else:
                amount = calculate_order_amount(context, stock, 0, data[stock].price)

            order(stock, amount)

# This method is purely for order managment. It calculates and returns an
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
    elif signal_val == 0:
        return -1 * current_amount
    else:
        return 0

def sort_returns(prices):
    shifted_prices = prices.shift(9)
    returns = (prices - shifted_prices) / shifted_prices
    # use a slice operator to get the most recent returns
    last_returns = returns[-1:]
    last_date = last_returns.index[-1]
    sorted_returns = last_returns.T.sort(columns=last_date, ascending=0)
    return sorted_returns    