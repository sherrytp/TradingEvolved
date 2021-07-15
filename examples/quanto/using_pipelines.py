# The pipeline API requires imports.
from zipline.api import attach_pipeline, pipeline_output, update_universe
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import SimpleMovingAverage

def initialize(context):

    # Create, register and name a pipeline in initialize.
    pipe = Pipeline()
    attach_pipeline(pipe, 'example')

    # Construct a simple moving average factor and add it to the pipeline.
    sma_short = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=10)
    pipe.add(sma_short, 'sma_short')

    # Set a screen on the pipelines to filter out securities.
    pipe.set_screen(sma_short > 1.0)


def before_trading_start(context, data):
    # Pipeline_output returns the constructed dataframe.
    output = pipeline_output('example')

    # Select and update your universe.
    context.my_universe = output.sort('sma_short', ascending=False).iloc[:200]
    update_universe(context.my_universe.index)


def handle_data(context, data):
    log.info("\n" + str(context.my_universe.head(5)))
