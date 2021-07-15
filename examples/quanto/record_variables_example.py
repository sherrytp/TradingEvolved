# This initialize function sets any data or variables that you'll use in
# your algorithm.
def initialize(context):
    context.stock = symbol('BA')  # Boeing


# Now we get into the meat of the algorithm.
def handle_data(context, data):
    # Create a variable for the price of the Boeing stock
    context.price = data[context.stock].price

    # Create variables to track the short and long moving averages.
    # The short moving average tracks over 20 days and the long moving average
    # tracks over 80 days.
    short = data[context.stock].mavg(20)
    long = data[context.stock].mavg(80)

    # If the short moving average is higher than the long moving average, then
    # we want our portfolio to hold 500 stocks of Boeing
    if (short > long):
        order_target(context.stock, +500)

    # If the short moving average is lower than the long moving average, then
    # then we want to sell all of our Boeing stocks and own 0 shares
    # in the portfolio.
    elif (short < long):
        order_target_value(context.stock, 0)

    # Record our variables to see the algo behavior. You can record up to
    # 5 custom variables. To see only a certain variable, deselect the
    # variable name in the custom graph in the backtest.
    record(short_mavg = short,
        long_mavg = long,
        goog_price = context.price)