import requests
params = {
  "symbol":"dali_usdt",
  "size":"1",
}
request = requests.get(url = "https://api.lbkex.com/v1/trades.do", params=params)
print(request.json())
print(request.url)