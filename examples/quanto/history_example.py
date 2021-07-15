# Standard Deviation Using History
# Use history() to calculate the standard deviation of the days' closing
# prices of the last 10 trading days, including price at the time of
# calculation.
def initialize(context):
    # this example works on Apple's data
    context.aapl = symbol('AAPL')

def handle_data(context, data):
    # use history to pull the last 10 days of price
    price_history = history(bar_count=10, frequency='1d', field='price')
    # calculate the standard deviation using std()
    std = price_history.std()
    # record the standard deviation as a custom signal
    record(std=std[context.aapl])
