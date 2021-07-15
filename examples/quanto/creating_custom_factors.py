from zipline.api import attach_pipeline, pipeline_output
from zipline.pipeline import Pipeline
from zipline.pipeline import CustomFactor
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.data import morningstar
from zipline.pipeline.factors import SimpleMovingAverage


# Create custom factor subclass to calculate a market cap based on yesterday's
# close
class MarketCap(CustomFactor):

    # Pre-declare inputs and window_length
    inputs = [USEquityPricing.close, morningstar.valuation.shares_outstanding]
    window_length = 1

    # Compute market cap value
    def compute(self, today, assets, out, close, shares):
        out[:] = close[-1] * shares[-1]


def initialize(context):

    pipe = Pipeline()
    attach_pipeline(pipe, 'example')

    # Note that we don't call add_factor on these Factors.
    # We don't need to store intermediate values if we're not going to use them
    sma_short = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=30)
    sma_long = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=100)

    sma_val = sma_short/sma_long

    # Construct the custom factor
    mkt_cap = MarketCap()

    # Create and apply a filter representing the top 500 equities by MarketCap
    # every day.
    mkt_cap_top_500 = mkt_cap.top(500)

    remove_penny_stocks = sma_short > 1.0

    pipe.add(sma_val, 'sma_val')
    pipe.add(mkt_cap, 'mkt_cap')
    # Use mkt_cap_top_500 as a mask on rank
    pipe.add(sma_val.rank(mask=mkt_cap_top_500), 'sma_rank')

    # Use multiple screens to narrow the universe
    pipe.set_screen(mkt_cap.top(500) & remove_penny_stocks)


def before_trading_start(context, data):
    context.output = pipeline_output('example')

    context.short_list = context.output.sort(['sma_rank'], ascending=True).iloc[:200]
    context.long_list = context.output.sort(['sma_rank'], ascending=True).iloc[-200:]

    update_universe(context.long_list.index.union(context.short_list.index))


def handle_data(context, data):

    print "SHORT LIST"
    log.info("\n" + str(context.short_list.sort(['sma_rank'], ascending=True).head()))

    print "LONG LIST"
    log.info("\n" + str(context.long_list.sort(['sma_rank'], ascending=False).head()))
