def initialize(context):
    context.stocks = symbols('CERN', 'DLTR')

def handle_data(context, data):
    # This will order as many shares as needed to
    # achieve the desired portfolio allocation.
    # In our case, we end up with 20% allocation for
    # one stock and 80% allocation for the other stock.
    order_target_percent(context.stocks[0], .2)
    order_target_percent(context.stocks[1], .8)

    # Plot portfolio allocations
    pv = float(context.portfolio.portfolio_value)
    portfolio_allocations = []
    for stock in context.stocks:
        pos = context.portfolio.positions[stock]
        portfolio_allocations.append(
            pos.last_sale_price * pos.amount / pv * 100
        )

    record(perc_stock_0=portfolio_allocations[0],
           perc_stock_1=portfolio_allocations[1])