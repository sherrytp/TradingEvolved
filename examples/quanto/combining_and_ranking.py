from zipline.api import attach_pipeline, pipeline_output
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import SimpleMovingAverage


def initialize(context):

    pipe = Pipeline()
    attach_pipeline(pipe, 'example')

    sma_short = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=30)
    sma_long = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=100)

    # Combined factors to create new factors
    sma_val = sma_short/sma_long

    # Create and apply a screen to remove penny stocks
    remove_penny_stocks = sma_short > 1.0
    pipe.set_screen(remove_penny_stocks)

    pipe.add(sma_short, 'sma_short')
    pipe.add(sma_long, 'sma_long')
    pipe.add(sma_val, 'sma_val')
    # Rank a factor using a mask to ignore the values we're 
    # filtering out by passing mask=remove_penny_stocks to rank.
    pipe.add(sma_val.rank(mask=remove_penny_stocks), 'sma_rank')


def before_trading_start(context, data):
    context.output = pipeline_output('example')

    # Set the list of securities to short
    context.short_list = context.output.sort(['sma_rank'], ascending=True).iloc[:200]

    # Set the list of securities to long
    context.long_list = context.output.sort(['sma_rank'], ascending=True).iloc[-200:]

    # Update your universe with the SIDs of long and short securities
    update_universe(context.long_list.index.union(context.short_list.index))

def handle_data(context, data):

    print "SHORT LIST"
    log.info("\n" + str(context.short_list.sort(['sma_rank'], ascending=True).head()))

    print "LONG LIST"
    log.info("\n" + str(context.long_list.sort(['sma_rank'], ascending=False).head()))
