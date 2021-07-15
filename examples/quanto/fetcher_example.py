import pandas

def rename_col(df):
    df = df.rename(columns={'New York 15:00': 'price'})
    df = df.rename(columns={'Value': 'price'})
    df = df.fillna(method='ffill')
    df = df[['price', 'sid']]
    # Correct look-ahead bias in mapping data to times
    df = df.tshift(1, freq='b')
    log.info(' \n %s ' % df.head())
    return df

def initialize(context):
    # import the external data
    fetch_csv('https://www.quandl.com/api/v1/datasets/JOHNMATT/PALL.csv?trim_start=2012-01-01',
        date_column='Date',
        symbol='palladium',
        pre_func = preview,
        post_func=rename_col,
        date_format='%Y-%m-%d')

    fetch_csv('https://www.quandl.com/api/v1/datasets/BUNDESBANK/BBK01_WT5511.csv?trim_start=2012-01-01',
        date_column='Date',
        symbol='gold',
        pre_func = preview,
        post_func=rename_col,
        date_format='%Y-%m-%d')

    # Tiffany
    context.stock = symbol('TIF')

def preview(df):
    log.info(' \n %s ' % df.head())
    return df

def handle_data(context, data):
    # Invest 10% of the portfolio in Tiffany stock when the price of gold is low.
    # Decrease the Tiffany position to 5% of portfolio when the price of gold is high.

    if (data['gold'].price < 1600):
       order_target_percent(context.stock, 0.10)
    if (data['gold'].price > 1750):
       order_target_percent(context.stock, 0.05)

    #record the variables
    if 'price' in data['palladium']:
       record(palladium=data['palladium'].price, gold=data['gold'].price)