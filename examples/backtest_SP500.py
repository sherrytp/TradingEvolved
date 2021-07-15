import pickle
import requests
import bs4 as bs
import pandas as pd
import pandas_datareader as pdr

path = './sp500.pickle'
def save_sp500_tickers(path=path, build=False):
    if build:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
        res = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=headers)
    else:
        res = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(res.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
    with open(path, 'wb') as f:
        pickle.dump(tickers, f)
    return tickers


def compile_data(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open(path, 'rb') as f:
            tickers = pickle.load(f)
    # if not os.path.exists('stock_dfs'):
    #     os.makedirs('stock_dfs')

    start = pd.Timestamp('2010-1-1', tz='utc')
    end = pd.Timestamp('2010-1-5', tz='utc')
    main_df = pd.DataFrame()
    elim = 0
    # pdr.get_data_yahoo('MMM', pd.Timestamp('2010-1-1', tz='utc'), pd.Timestamp('2010-1-5', tz='utc'))
    # pdr.DataReader('MMM', 'yahoo', pd.Timestamp('2010-1-1', tz='utc'), pd.Timestamp('2010-1-4', tz='utc'))
    for count, ticker in enumerate(tickers):
        # just in case your connection breaks, we'd like to save our progress! if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
        try:
            df = pdr.get_data_yahoo(ticker, start, end)
        except pdr._utils.RemoteDataError:
            print(ticker)
            elim += 1
            continue
        df.reset_index(inplace=True).set_index("Date", inplace=True)
        df = df.drop("Symbol", axis=1)
        # df.to_csv('stock_dfs/{}.csv'.format(ticker))

        # df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df.set_index('Date', inplace=True)
        df.rename(columns={'Adj Close': ticker}, inplace=True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')

        if count % 10 == 0:
            print(count)

    print(elim, 'sets of tickers are eliminated due to get_yahoo price unavailable, \n', main_df.head())
    main_df.to_csv('sp500_joined_closes.csv')


def visualize_data():
    import matplotlib as plt
    import numpy as np
    df = pd.read_csv('sp500_joined_closes.csv')
    df_corr = df.corr()
    print(df_corr.head())
    df_corr.to_csv('sp500corr.csv')
    data1 = df_corr.values
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)

    ax1.set_xticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1, 1)
    plt.tight_layout()
    plt.show()

"""
###### Zipline SP500 Universe ############
def initialize(context):
    context.target_weight = 0.1
    fetch_csv(
        'https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/Indicies/SP500.csv',
        pre_func=add_data_column,
        date_column='date',
        symbol_column='Ticker',
    )
    schedule_function(order_function, date_rules.every_day(), time_rules.market_open(hours=0, minutes=1))

def process_data(df):
    df['date'] = '10/01/2013'
    df = df.rename(columns={'Ticker': 'symbol'})
    financials = df[df['Sector'] == 'Financials']
    sids = [symbol(s) for s in set(financials['symbol'])]
    return sids

# Function for returning a set of SIDS from fetcher_data
def my_universe(context, fetcher_data):
    # Grab just the SIDs for the Financials sector w/in SNP500:
    financials = fetcher_data[fetcher_data['Sector'] == 'Financials']
    sids = set(financials['symbol'])
    symbols = [symbol(s) for s in sids]
    print('Total universe size: {}'.format(len(symbols)))

    # Compute target equal-weight for each stock in SNP500 Financials universe
    context.target_weight = 1.0 / len(symbols)
    print('what is sids', sids)
    return sids

def order_function(context, data):
    print(data)
    print(data.history(context.symbol, 'close', 250, '1d'))
    for stock in data:
        if 'price' in data[stock]:
            print(stock)
            order_target_percent(stock, context.target_weight)
        else:
            print('No price for {}'.format(stock))


##### Zipline Pipeline of Futures ######## 
def initialize(context):
    comm_model = commission.PerContract(cost=0.85, exchange_fee=1.5)
    set_commission(us_futures=comm_model)
    slippage_model = slippage.VolatilityVolumeShare(volume_limit=0.2)
    set_slippage(us_futures=slippage_model)markets = [
        'AD',
        'BP',
        'CD',
        'CU',
        'DX',
        'JY',
        'NE',
        'SF',
    ]
    context.universe = [continuous_future(market, offset=0, roll='volume', adjustment='mul')
                        for market in markets]
    context.highest_in_pos = {market: 0 for market in markets}
    context.lowest_in_pos = {market: 0 for market in markets}
    # schedule_function(daily_trade, date_rules.every_day(), time_rules.market_close())
    # schedule_function(func=analyze, date_rule=date_rules.month_start(), time_rule=time_rules.market_open())

def roll_equity(context, data):
    open_orders = get_open_orders()

    # don't roll positions that are set to change by core logic
    for kept_positions in context.portfolio.positions:
        if kept_positions in open_orders:
            continue

        # save time by checking rolls only for contracts stopping trading in the next days
        days_to_auto_close = (
            kept_positions.auto_close_date.date() - data.current_session.date()
        ).days
        if days_to_auto_close > 5:
            continue

        # Make a continuation
        continuation = continuous_future(
            kept_positions.root_symbol,
            offset=0,
            roll='volume',
            adjustment='mul'
        )

        # Get the current contract of the continuation
        continuation_contract = data.current(continuation, 'contract')
        if continuation_contract != kept_positions:
            # Check how many contracts we hold
            pos_size = context.portfolio.positions[kept_positions].amount
            # Close current position
            order_target(kept_positions, 0)
            # Open new position
            order_target(continuation_contract, pos_size)

def position_size(portfolio_value, std, point_value, risk_factor=0.0015):
    target_var = portfolio_value * risk_factor
    contract_var = std * point_value
    contracts = target_var / contract_var
    return int(np.nan_to_num(contracts))

def daily_trade(context, data):
    # Get continuation data
    hist = data.history(context.universe, fields=['close', 'volume'], frequency='1d', bar_count=250)
    # Calculate trend
    hist['trend'] = hist['close'].ewm(span=40).mean() > hist['close'].ewm(span=80).mean()
    # Make a dictionary of open positions
    open_pos = {
        pos.symbol: pos for pos in context.portfolio.positions
    }

    for continuation in context.universe:
        root = continuation.symbol
        h = hist.xs(continuation, 2)
        std = h.close.diff()[-vola_window:].std()

        if root in open_pos:    # position is open
            p = context.portfolio.positions[open_pos[root]]
            if p.amount > 0:    # position is long
                if context.highest_in_position[root] == 0: # First day holding the position
                    context.highest_in_position[root] = p.cost_basis
                else:
                    context.highest_in_position[root] = max(
                        h['close'].iloc[-1], context.highest_in_position[root]
                    )

def analyze(context, perf):
    context.months += 1
    yr_ret = np.power(context.portfolio.portfolio_value / context.capital_base, 12 / context.months) - 1
    out.value = '{} We have traded <b>{}</b> months and the annualized return is <b>{:.2%}</b>'.format(
        get_datetime().date(), context.months, yr_ret)

    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
    pf.create_returns_tear_sheet(returns, benchmark_rets=None)


bundle_name = 'random_futures_data' # "a bundle name"
calendar_name = 'NYSE' # "the calendar name"
window=100 # how many days you want to look back
bundle_data = bundles.load(bundle_name)
data_por = DataPortal(bundle_data.asset_finder,
                      get_calendar(calendar_name),
                      bundle_data.equity_daily_bar_reader.first_trading_day,
                      equity_minute_reader=bundle_data.equity_minute_bar_reader,
                      equity_daily_reader=bundle_data.equity_daily_bar_reader,
                      adjustment_reader=bundle_data.adjustment_reader)

sym = data_por.asset_finder.lookup_symbol('AD', start)
data = data_por.get_history_window(assets=[sym],
                                   end_dt=start,
                                   bar_count=window,
                                   frequency='1d',
                                   data_frequency='daily',
                                   field='close')

# bundle_data = bundles.load(bundle_name)
# # Set the dataloader
# pricing_loader = USEquityPricingLoader.without_fx(bundle_data.equity_daily_bar_reader, bundle_data.adjustment_reader)
#
# # Define the function for the get_loader parameter
# def choose_loader(column):
#     if column not in USEquityPricing.columns:
#         raise Exception('Column not in USEquityPricing')
#     return pricing_loader
#
# # Set the trading calendar
# trading_calendar = get_calendar('NYSE')
#
# start_date = pd.Timestamp('2019-07-05', tz='utc')
# end_date = pd.Timestamp('2020-11-13', tz='utc')
#
# # Create a data portal
# data_portal = DataPortal(bundle_data.asset_finder,
#                          trading_calendar = trading_calendar,
#                          first_trading_day = start_date,
#                          equity_daily_reader = bundle_data.equity_daily_bar_reader,
#                          adjustment_reader = bundle_data.adjustment_reader)
#
# equity = bundle_data.asset_finder.lookup_symbol("ACES", end_date)
# data_portal.get_history_window(assets=[equity], end_dt=end_date, bar_count=10,
#                                frequency='1d',
#                                field='close',
#                                data_frequency='daily')
"""