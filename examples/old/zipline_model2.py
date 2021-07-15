#!/usr/bin/env python
# coding: utf-8
# # Data Access with Zipline
# Zipline is the algorithmic trading library that used to power the now-defunct Quantopian backtesting and live-trading platform. It is also available offline to develop a strategy using a limited number of free data bundles that can be ingested and used to test the performance of trading ideas.
# ## Zipline installation
# Please follow installation instructions [here](../../installation/README.md)
# Run the Docker image as explained in the installation [instructions](../../installation/README.md) and select the `ml4t-zipline` environment after starting the jupyter server.
# There is much more information about Zipline in [Chapter 8](../../08_ml4t_workflow/04_ml4t_workflow_with_zipline).
# ## Imports & Settings
# In[1]:
# get_ipython().run_line_magic('matplotlib', 'inline')
import pandas as pd
# In[2]:
# get_ipython().run_line_magic('load_ext', 'zipline')
# ## zipline Demo
# ### Ingest Data
# Get QUANDL API key and follow instructions to download zipline bundles [here](http://www.zipline.io/bundles.html). This boils down to running:
# In[3]:
# !zipline ingest
# See `zipline` [docs](http://www.zipline.io/bundles.html) on the download and management of data bundles used to simulate backtests.
#
# The following commandline instruction lists the available bundles (store per default in `~/.zipline`.
# In[4]:
# !zipline bundles
# ### Data access using zipline
# The following code illustrates how zipline permits us to access daily stock data for a range of companies. You can run zipline scripts in the Jupyter Notebook using the magic function of the same name.
# First, you need to initialize the context with the desired security symbols. We'll also use a counter variable. Then zipline calls handle_data, where we use the `data.history()` method to look back a single period and append the data for the last day to a .csv file:
# In[5]:
# get_ipython().run_cell_magic('zipline', '--start 2010-1-1 --end 2018-1-1 --data-frequency daily', 'from zipline.api import order_target, record, symbol\nimport pandas as pd\n\ndef initialize(context):\n    context.i = 0\n    context.assets = [symbol(\'FB\'), symbol(\'GOOG\'), symbol(\'AMZN\')]\n    \ndef handle_data(context, data):\n    df = data.history(context.assets, fields=[\'price\', \'volume\'], bar_count=1, frequency="1d")\n    df = df.to_frame().reset_index()\n    \n    if context.i == 0:\n        df.columns = [\'date\', \'asset\', \'price\', \'volume\']\n        df.to_csv(\'stock_data.csv\', index=False)\n    else:\n        df.to_csv(\'stock_data.csv\', index=False, mode=\'a\', header=None)\n    context.i += 1')
from zipline.api import order_target, record, symbol
import matplotlib.pyplot as plt
import pandas as pd
import zipline


def initialize(context):
    context.i = 0
    context.assets = [symbol('FB'), symbol('GOOG'), symbol('AMZN')]
def handle_data(context, data):
    df = data.history(context.assets, fields=['price', 'volume'], bar_count=1, frequency="1d")
    df = df.to_frame().reset_index()
    if context.i == 0:
        df.columns = ['date', 'asset', 'price', 'volume']
        df.to_csv('stock_data.csv', index=False)
    else:
        df.to_csv('stock_data.csv', index=False, mode='a', header=None)
    context.i += 1
# We can plot the data as follows:
start = pd.Timestamp('2010-01-01', tz='utc')
end = pd.Timestamp('2018-12-30', tz='utc')
perf = zipline.run_algorithm(start=start,
                             end=end,
                             initialize=initialize,
                             handle_data=handle_data,
                             data_frequency='daily',
                             bundle='quandl',
                             capital_base=1000000)
df = pd.read_csv('stock_data.csv')
df.date = pd.to_datetime(df.date)
df.set_index('date').groupby('asset').price.plot(lw=2, legend=True, figsize=(14, 6))
plt.show()
# ### Simple moving average strategy
# The following code example illustrates a [Dual Moving Average Cross-Over Strategy](https://www.zipline.io/beginner-tutorial.html#access-to-previous-prices-using-history) to demonstrate Zipline in action: get_ipython().run_cell_magic('zipline', '--start 2014-1-1 --end 2018-1-1 -o dma.pickle', 'from zipline.api import order_target, record, symbol\nimport matplotlib.pyplot as plt\n\ndef initialize(context):\n    context.i = 0\n    context.asset = symbol(\'AAPL\')\n\n\ndef handle_data(context, data):\n    # Skip first 300 days to get full windows\n    context.i += 1\n    if context.i < 300:\n        return\n\n    # Compute averages\n    # data.history() has to be called with the same params\n    # from above and returns a pandas dataframe.\n    short_mavg = data.history(context.asset, \'price\', bar_count=100, frequency="1d").mean()\n    long_mavg = data.history(context.asset, \'price\', bar_count=300, frequency="1d").mean()\n\n    # Trading logic\n    if short_mavg > long_mavg:\n        # order_target orders as many shares as needed to\n        # achieve the desired number of shares.\n        order_target(context.asset, 100)\n    elif short_mavg < long_mavg:\n        order_target(context.asset, 0)\n\n    # Save values for later inspection\n    record(AAPL=data.current(context.asset, \'price\'),\n           short_mavg=short_mavg,\n           long_mavg=long_mavg)\n\n\ndef analyze(context, perf):\n    fig, (ax1, ax2) = plt.subplots(nrows=2,figsize=(14, 8))\n    perf.portfolio_value.plot(ax=ax1)\n    ax1.set_ylabel(\'portfolio value in $\')\n\n    perf[\'AAPL\'].plot(ax=ax2)\n    perf[[\'short_mavg\', \'long_mavg\']].plot(ax=ax2)\n\n    perf_trans = perf.ix[[t != [] for t in perf.transactions]]\n    buys = perf_trans.ix[[t[0][\'amount\'] > 0 for t in perf_trans.transactions]]\n    sells = perf_trans.ix[\n        [t[0][\'amount\'] < 0 for t in perf_trans.transactions]]\n    ax2.plot(buys.index, perf.short_mavg.ix[buys.index],\n             \'^\', markersize=10, color=\'m\')\n    ax2.plot(sells.index, perf.short_mavg.ix[sells.index],\n             \'v\', markersize=10, color=\'k\')\n    ax2.set_ylabel(\'price in $\')\n    plt.legend(loc=0)\n    plt.show() ')

def initialize(context):
    context.i = 0
    context.asset = symbol('AAPL')
def handle_data(context, data):
    # Skip first 300 days to get full windows
    context.i += 1
    if context.i < 300:
        return
    # Compute averages
    # data.history() has to be called with the same params
    # from above and returns a pandas dataframe.
    short_mavg = data.history(context.asset, 'price', bar_count=100, frequency="1d").mean()
    long_mavg = data.history(context.asset, 'price', bar_count=300, frequency="1d").mean()
    # Trading logic
    if short_mavg > long_mavg:
        # order_target orders as many shares as needed to
        # achieve the desired number of shares.
        order_target(context.asset, 100)
    elif short_mavg < long_mavg:
        order_target(context.asset, 0)
    # Save values for later inspection
    record(AAPL=data.current(context.asset, 'price'),
           short_mavg=short_mavg,
           long_mavg=long_mavg)
def analyze(context, perf):
    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(14, 8))
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value in $')
    perf['AAPL'].plot(ax=ax2)
    perf[['short_mavg', 'long_mavg']].plot(ax=ax2)
    perf_trans = perf.ix[[t != [] for t in perf.transactions]]
    buys = perf_trans.ix[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
    sells = perf_trans.ix[
        [t[0]['amount'] < 0 for t in perf_trans.transactions]]
    ax2.plot(buys.index, perf.short_mavg.ix[buys.index],
             '^', markersize=10, color='m')
    ax2.plot(sells.index, perf.short_mavg.ix[sells.index],
             'v', markersize=10, color='k')
    ax2.set_ylabel('price in $')
    plt.legend(loc=0)
    plt.show()
start = pd.Timestamp('2014-01-01', tz='utc')
end = pd.Timestamp('2018-01-01', tz='utc')
perf = zipline.run_algorithm(start=start,
                             end=end,
                             initialize=initialize,
                             handle_data=handle_data,
                             analyze=analyze,
                             bundle='quandl',
                             capital_base=1000000)


####### Added similar examples of model-3 #######################
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol
# Import date and time zone libraries
from datetime import datetime
import pytz
# Import visualization
import matplotlib.pyplot as plt
def initialize(context):
    # Which stock to trade
    context.stock = symbol('AMZN')
    # Moving average window
    context.index_average_window = 100
def handle_data(context, data):
    # Request history for the stock
    equities_hist = data.history(context.stock, "close",
                                 context.index_average_window, "1d")
    # Check if price is above moving average
    if equities_hist[-1] > equities_hist.mean():
        stock_weight = 1.0

    else:
        stock_weight = 0.0
        # Place order
    order_target_percent(context.stock, stock_weight)

    def analyze(context, perf):
        fig = plt.figure(figsize=(12, 8))
        # First chart
        ax = fig.add_subplot(311)
        ax.set_title('Strategy Results')
        ax.semilogy(perf['portfolio_value'], linestyle='-',
                    label='Equity Curve', linewidth=3.0)
        ax.legend()
        ax.grid(False)
        # Second chart
        ax = fig.add_subplot(312)
        ax.plot(perf['gross_leverage'],
                label='Exposure', linestyle='-', linewidth=1.0)
        ax.legend()
        ax.grid(True)
        # Third chart
        ax = fig.add_subplot(313)
        ax.plot(perf['returns'], label='Returns', linestyle='-.', linewidth=1.0)
        ax.legend()
        ax.grid(True)
        plt.show()

    # Set start and end date
    start_date = datetime(2010, 1, 1, tzinfo=pytz.UTC)
    end_date = datetime(2019, 7, 1, tzinfo=pytz.UTC)
    # Fire off the backtest
    # results = run_algorithm(
    #     start=start_date,
    #     end=end_date,
    #     initialize=initialize,
    #     analyze=analyze,
    #     handle_data=handle_data,
    #     capital_base=100000000,
    #     data_frequency='daily', bundle='quandl'
    # )
