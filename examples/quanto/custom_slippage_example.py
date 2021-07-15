from zipline.api import slippage, sid, set_slippage
# Our custom slippage model
class PerStockSpreadSlippage(slippage.SlippageModel):

    # We specify the constructor so that we can pass state to this class, but this is optional.
    def __init__(self, spreads):
        # Store a dictionary of spreads, keyed by sid.
        self.spreads = spreads

    def process_order(self, trade_bar, my_order):
        spread = self.spreads[my_order.sid]

        # In this model, the slippage is going to be half of the spread for
        # the particular stock
        slip_amount = spread / 2
        # Compute the price impact of the transaction. Size of price impact is
        # proprotional to order size.
        # A buy will increase the price, a sell will decrease it.
        new_price = trade_bar.price + (slip_amount * my_order.direction)

        log.info('executing order ' + str(trade_bar.sid) + ' stock bar price: ' + \
                 str(trade_bar.price) + ' and trade executes at: ' + str(new_price))

        # Create the transaction using the new price we've calculated.
        return slippage.create_transaction(
            trade_bar,
            my_order,
            new_price,
            my_order.amount
        )

def initialize(context):
    # Provide the bid-ask spread for each of the securities in the universe.
    spreads = {
        sid(24): 0.05,
        sid(3766): 0.08
    }

    # Initialize slippage settings given the parameters of our model
    set_slippage(PerStockSpreadSlippage(spreads))


def handle_data(context, data):
    # We want to own 100 shares of each stock in our universe
    for stock in data:
            order_target(stock, 100)
            log.info('placing market order for ' + str(stock.symbol) + ' at price ' \
                     + str(data[stock].price))