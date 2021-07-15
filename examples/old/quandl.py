import quandl
from datetime import datetime, timedelta

QUANDL_KEY = "fvy5hW5Eeg8U4ecXQyVz"
quandl.ApiConfig.api_key = QUANDL_KEY

today = datetime.today()
start_date = today - timedelta(days=60)
print("{}-{}-{}".format(start_date.year, start_date.month, start_date.day))

df_quandl = quandl.get(dataset=["WIKI/AAPL",
                                "WIKI/AMZN",
                                "WIKI/MSFT",
                                "WIKI/AMD",
                                "WIKI/GE",
                                "WIKI/JPM"],
                       start_date="2000-01-01",
                       end_date="2010-12-31")

df = df_quandl[['WIKI/AAPL - Close',
                'WIKI/AMZN - Close',
                'WIKI/MSFT - Close',
                'WIKI/AMD - Close',
                'WIKI/GE - Close',
                'WIKI/JPM - Close']].copy()

df.rename(columns={'WIKI/AAPL - Close': 'AAPL',
                   'WIKI/AMZN - Close': 'AMZN',
                   'WIKI/MSFT - Close': 'MSFT',
                   'WIKI/AMD - Close': 'AMD',
                   'WIKI/GE - Close': 'GE',
                   'WIKI/JPM - Close': 'JPM'}, inplace=True)

df.to_csv('./data/toy_price.csv')

print(df)
