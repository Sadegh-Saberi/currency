import requests

with requests.get("https://www.mexc.com/open/api/v2/market/coin/list") as request:
    currencies = request.json().get("data")[:10]
    for currency in currencies: print(currency); print('*'*10)
    