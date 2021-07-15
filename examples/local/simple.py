from zipline.api import symbol, order, order_target, record
import logbook
logbook.StderrHandler().push_application()
log = logbook.Logger("-")


def initialize(context):
    pass

def handle_data(context, data):
    pass

if __name__ == '__main__':
    from datetime import datetime
    import pytz
    from zipline.algorithm import TradingAlgorithm
    from zipline.utils.factory import load_from_yahoo

    start = datetime(2015, 10, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2015, 11, 1, 0, 0, 0, 0, pytz.utc)

    data = load_from_yahoo(stocks=['AAPL'], indexes={}, start=start, end=end)

    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, identifiers=['AAPL'])
    algo.run(data)
