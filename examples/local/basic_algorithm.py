from zipline.api import symbol, order, order_target, record
import logbook
logbook.StderrHandler().push_application()
log = logbook.Logger("-")

def initialize(context):
    context.security = symbol('AAPL')

def handle_data(context, data):
    average_price = data[context.security].mavg(5)
    current_price = data[context.security].price

    cash = context.portfolio.cash

    if current_price > 1.01*average_price and cash > current_price:
        number_of_shares = int(cash/current_price)
        order(context.security, +number_of_shares)
        log.info("Buying %s" % (context.security.symbol))
    elif current_price < average_price:
        order_target(context.security, 0)
        log.info("Selling %s" % (context.security.symbol))

    record(stock_price=data[context.security].price)


def analyze(context=None, results=None):
    import matplotlib.pyplot as plt

    ax1 = plt.subplot(211)
    results.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('Portfolio value (USD)')
    ax2 = plt.subplot(212, sharex=ax1)
    results.stock_price.plot(ax=ax2)
    ax2.set_ylabel('AAPL price (USD)')

    plt.gcf().set_size_inches(18, 8)
    plt.show()

if __name__ == '__main__':
    from datetime import datetime
    import pytz
    from zipline.algorithm import TradingAlgorithm
    from zipline.utils.factory import load_from_yahoo

    start = datetime(2015, 10, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2015, 11, 1, 0, 0, 0, 0, pytz.utc)

    data = load_from_yahoo(stocks=['AAPL'], indexes={}, start=start, end=end)

    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, identifiers=['AAPL'])
    results = algo.run(data)

    analyze(results=results)