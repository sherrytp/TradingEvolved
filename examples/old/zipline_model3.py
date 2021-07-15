from zipline import run_algorithm
from zipline.api import order_target_percent, symbol  # , symbols
from datetime import datetime as dt
import pytz
import matplotlib.pyplot as plt
# 2sigma API access
import requests
import time
# from ta import macd: AV: 2/13/20 this doesnt work
from datetime import timedelta
# Replace these with your API connection info from the dashboard
base_url = 'https://paper-api.alpaca.markets'
api_key_id = 'PKCWX8Y8GD30W1CXFBAR'
api_secret = 'SAoMsJFBL6Oxv7Y2DGhSrpVWRs0o3o8AtnSImBvJ'
# Making Requests
# curl "https://trade.pics-twosigma.com/api" -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
# headers = {
#     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
# }
#
# url = 'https://trade.pics-twosigma.com/api'
# response = requests.post(url, headers=headers)
# print(response.text)
# Get All Strategies: false: active, true: inactive as well
# curl "https://trade.pics-twosigma.com/api/strategies?includeInactive=false"
# -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
params = (
    ('includeInactive', 'false'),
)
response = requests.get('https://trade.pics-twosigma.com/api/strategies', headers=headers, params=params)
print(response.text)
# Create new strategies: limit: 5/user
# curl "https://trade.pics-twosigma.com/api/strategies"
#   -X POST -d '{"name": "New Strategy", "description": "New Strategy Description"}'
#   -H "Content-Type: application/json"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
# headers = {
#     'Content-Type': 'application/json',
#     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
# }
#
# data = '{"name": "TwoSigma_v1", "description": "Submitting new strategies in Zipline-Live"}'
#
# response = requests.post('https://trade.pics-twosigma.com/api/strategies', headers=headers, data=data)
# print(response.text)
# Close strategy:   A strategy cannot be closed if there are open positions or pending orders.
# Orders and positions must be manually closed out before attempting to close the strategy.
# curl "https://trade.pics-twosigma.com/api/strategies/5f0f7f0b-5659-4833-ac5e-c4d78ce6308c"
#   -X DELETE
#   -H "Content-Type: application/json"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
# headers = {
#     'Content-Type': 'application/json',
#     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
# }
#
# response = requests.delete('https://trade.pics-twosigma.com/api/strategies/9474be2e-b9b2-4c8b-8207-964526116a9f', headers=headers)
# print(response.text)
# Orders
# Query single order
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders/c38f90f7-90bf-40be-9684-62d0b109879c"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"\
# headers = {
#     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
# }
#
# response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders/c38f90f7-90bf-40be-9684-62d0b109879c', headers=headers)
# print(response.text)
# Querying for all orders
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
response = requests.get('https://trade.pics-twosigma.com/api/strategies/3dabe7ad-4727-4ff0-88c0-e106564e6dda/orders',
                        headers=headers)
print(response.text)
# Querying for all AMZN orders
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders?instrumentId=BBG000BVPV84"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
# headers = {
#     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
# }
#
# params = (
#     ('instrumentId', 'BBG000BVPV84'),
# )
# response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders', headers=headers)
# print(response.text)
#
#
# # Querying for AMZN orders submitted between two dates
# # curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders?instrumentId=BBG000BVPV84&beginDate=2017-11-01&endDate=2017-12-01"
# # # #   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
# # # SPY: BBG001ZKMP13
#
# headers = {
#     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
# }
#
# params = (
#     ('instrumentId', 'BBG000BVPV84'),
#     ('beginDate', '2017-11-01'),
#     ('endDate', '2017-12-01'),
# )
#
# response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders',
#                         headers=headers, params=params)
# print(response.text)
# Get all positions:
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/positions"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
# headers = {
#     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
# }
#
# response = requests.get('https://trade.pics-twosigma.com/api/strategies//positions', headers=headers)
# print(response.text)
# Get all positions:
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/positions"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
# headers = {
#     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
# }
#
# response = requests.get('https://trade.pics-twosigma.com/api/strategies/b2fd1a8-b0dc-44d4-b16d-fa455a0b7d6c/positions',
#                         headers=headers)
# print(response.text)
# coding: utf-8

# In[3]:
# This ensures that our graphs will be shown properly in the notebook.
# get_ipython().magic('matplotlib inline')
# Import Zipline functions that we need
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol
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
        # Submit Order with optional limit price
        # curl "https://trade.pics-twosigma.com/api/strategies/d0ce4d4e-9e1a-4976-9b31-ac2b113bafd0/orders"
        #   -X POST -d '[{"instrumentId": "BBG000BVPV84", "shares": 100, "limit": 123.43}]'
        #   -H "Content-Type: application/json"
        #   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
        # }
        #
        # data = '[{"instrumentId": "BBG000BVPV84", "shares": 1}]'
        #
        # response = requests.post(
        #     'https://trade.pics-twosigma.com/api/strategies/3dabe7ad-4727-4ff0-88c0-e106564e6dda/orders',
        #     headers=headers, data=data)
        # print(response.text)
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
start_date = dt(2010, 1, 1, tzinfo=pytz.UTC)
end_date = dt(2019, 7, 1, tzinfo=pytz.UTC)
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