import requests
# Making Requests
# curl "https://trade.pics-twosigma.com/api" -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
url = 'https://trade.pics-twosigma.com/api'
response = requests.post(url, headers=headers)
print(response.text)
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
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
data = '{"name": "test_v1", "description": "Learning and Rupert Emails"}'
response = requests.post('https://trade.pics-twosigma.com/api/strategies', headers=headers, data=data)
print(response.text)
# Close strategy:   A strategy cannot be closed if there are open positions or pending orders.
# Orders and positions must be manually closed out before attempting to close the strategy.
# curl "https://trade.pics-twosigma.com/api/strategies/5f0f7f0b-5659-4833-ac5e-c4d78ce6308c"
#   -X DELETE
#   -H "Content-Type: application/json"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
response = requests.delete('https://trade.pics-twosigma.com/api/strategies/5f0f7f0b-5659-4833-ac5e-c4d78ce6308c', headers=headers)
print(response.text)
# Orders
# Query single order
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders/c38f90f7-90bf-40be-9684-62d0b109879c"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"\
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders/c38f90f7-90bf-40be-9684-62d0b109879c', headers=headers)
print(response.text)
# Querying for all orders
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders', headers=headers)
print(response.text)
# Querying for all AMZN orders
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders?instrumentId=BBG000BVPV84"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
params = (
    ('instrumentId', 'BBG000BVPV84'),
)
response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders', headers=headers)
print(response.text)
# Querying for AMZN orders submitted between two dates
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders?instrumentId=BBG000BVPV84&beginDate=2017-11-01&endDate=2017-12-01"
# # #   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67ea"
# # SPY: BBG001ZKMP13
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67ea',
}
params = (
    ('instrumentId', 'BBG000BVPV84'),
    ('beginDate', '2017-11-01'),
    ('endDate', '2017-12-01'),
)
response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders',
                        headers=headers, params=params)
print(response.text)
# Submit Order with optional limit price
# curl "https://trade.pics-twosigma.com/api/strategies/d0ce4d4e-9e1a-4976-9b31-ac2b113bafd0/orders"
#   -X POST -d '[{"instrumentId": "BBG000BVPV84", "shares": 100, "limit": 123.43}]'
#   -H "Content-Type: application/json"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
}
data = '[{"instrumentId": "BBG000BVPV84", "shares": 100, "limit": 123.43}]'
response = requests.post('https://trade.pics-twosigma.com/api/strategies/d0ce4d4e-9e1a-4976-9b31-ac2b113bafd0/orders', headers=headers, data=data)
print(response.text)
# Request body JSON for a Next Tick order:
# [
#   {
#     "instrumentId": "BBG000BVPV84",
#     "shares": 100,
#     "limit": 123.43,
#     "execution": {
#       "type": "NEXT_TICK"
#     }
#   }
# ]
# Cancel an order
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders/5873f21c-26a2-4656-871e-2012dc39c686"
#   -X DELETE
#   -H "Content-Type: application/json"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
}
response = requests.delete('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777%208517264a029c/orders/5873f21c-26a2-4656-871e-2012dc39c686', headers=headers)
print(response.text)
# Cancel all orders
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders"
#   -X DELETE
#   -H "Content-Type: application/json"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67eY"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67eY',
}
response = requests.delete('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/orders', headers=headers)
print(response.text)
# Get all positions:
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/positions"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
}
response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/positions', headers=headers)
print(response.text)
# Get AMZN positions between two dates:
# curl "https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/positions?instrumentId=BBG000BVPV84&beginDate=2017-11-01&endDate=2017-12-01"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
}
params = (
    ('instrumentId', 'BBG000BVPV84'),
    ('beginDate', '2017-11-01'),
    ('endDate', '2017-12-01'),
)
response = requests.get('https://trade.pics-twosigma.com/api/strategies/8a61c73a-5ff7-40ba-9777-8517264a029c/positions',
                        headers=headers, params=params)
print(response.text)
# Get all instruments
# curl "https://trade.pics-twosigma.com/api/instruments"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
}
response = requests.get('https://trade.pics-twosigma.com/api/instruments', headers=headers)
print(response.text)
# Get specific instrument
# Lookup by FIGI
# curl "https://trade.pics-twosigma.com/api/instruments/BBG000BVPV84"
# #   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
# SPY: BBG001ZKMP13
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
}
response = requests.get('https://trade.pics-twosigma.com/api/instruments/BBG000BVPV84', headers=headers)
print(response.text)
# Lookup by ticker
# curl "https://trade.pics-twosigma.com/api/instruments/AMZN"
#   -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
}
response = requests.get('https://trade.pics-twosigma.com/api/instruments/AMZN', headers=headers)
print(response.text)
# Performance summary
# curl "https://trade.pics-twosigma.com/api/strategies/0c247d19-95e7-44a9-a5a3-b406dde42a5e/summary/lifetime?date=2017-10-31"
#     -H "Authorization: Bearer 4e6264031dbf4a51864a797b9b7c67e"
headers = {
    'Authorization': 'Bearer 4e6264031dbf4a51864a797b9b7c67e',
}
params = (
    ('date', '2017-10-31'),
)
response = requests.get('https://trade.pics-twosigma.com/api/strategies/0c247d19-95e7-44a9-a5a3-b406dde42a5e/summary/'
                        'lifetime', headers=headers, params=params)
print(response.text)