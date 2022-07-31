import requests
import pyodbc
from utils import percatge_difference, number_rounder
from time import sleep
import os

class CurrencyRequest:
    def __init__(self,allowed_currencies_file,access_file):
        # database file absolute path
        file_path = os.path.abspath(access_file)
        # the string connection for connection to access database
        self.connection_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};' \
            fr'DBQ={file_path};'
        with open(allowed_currencies_file, "r") as file:


            # an allowed currency has 2 parts separated with '/' (slash) containing the name and the price of the currency
            allowed_currencies = list({currency.upper() for currency in file.read().replace(
                " ", "").replace("\n", ",").replace("/","_").split(",") if currency != ''})  # read the data in the text file and convert them to the list of wnated currencies

            try:
                # remove the empty string items from the set
                allowed_currencies.remove("")
            except:
                pass
            finally:
                self.allowed_currencies = allowed_currencies
                # names like BTC, PIL, SHIB ,...
                self.allowed_names = {name.split(
                    "/")[0] for name in allowed_currencies}
    def create_database(self):
        with pyodbc.connect(self.connection_string) as connection:
            with connection.cursor() as cursor:
                try:
                    query = """CREATE TABLE currencies 
                        ([currency name] VARCHAR,
                        mexc VARCHAR,
                        hotbit VARCHAR,
                        lbank VARCHAR,
                        biture VARCHAR,
                        xt VARCHAR,
                        gate VARCHAR,
                        phemex VARCHAR,
                        [percentage difference] VARCHAR
                        )"""
                    cursor.execute(query)
                    connection.commit()
                except:
                    print("tables are already created!")
                finally:
                    # delete all rows in the database
                    query = f"DELETE FROM currencies;"
                    cursor.execute(query)
                    connection.commit()
                    # insert currencies name into the database
                    for currency in self.allowed_currencies:
                        query = f"INSERT INTO currencies ([currency name]) VALUES ('{currency}')"
                        cursor.execute(query)
                        connection.commit()

    def update_access(self, data: dict = None):
        with pyodbc.connect(self.connection_string) as connection:
            with connection.cursor() as cursor:
                for exchange, value in data.items():
                    for currency_name, price in value.items():
                        query = f"""UPDATE currencies
                                SET {exchange.lower()} = '{price}'
                                WHERE [currency name] = '{currency_name}';"""
                        cursor.execute(query)
                        connection.commit()

                query = "SELECT * FROM currencies"
                rows = cursor.execute(query).fetchall()
                expected_rows_values = [
                    [float(price) for price in row[1:-1] if price != None] for row in rows
                ]

                for row in expected_rows_values:
                    # get the row index in 'expected_rows_values' list
                    row_index = expected_rows_values.index(row)
                    # get the row currency name for adding the percentage difference data
                    currency_name = rows[row_index][0]
                    # if more that one price is in the row ...
                    if len(row) > 1:
                        result = percatge_difference(row)
                        query = f"""
                                    UPDATE currencies
                                    SET [percentage difference] = '{result}'
                                    WHERE [currency name] = '{currency_name}';
                                    """
                        cursor.execute(query)
                        connection.commit()

    def mexc(self):
        "document: https://mxcdevelop.github.io/APIDoc/open.api.v2.en.html#ticker-information"
        base_url = 'https://www.mexc.com/'
        path = '/open/api/v2/market/ticker'
        request = requests.get(base_url+path)
        currencies = request.json()['data']
        result = {}
        for currency in currencies:
            symbol = currency['symbol']
            if symbol in self.allowed_currencies:
                price = number_rounder(float(currency['last']))
                result.update({symbol:price})
        return {"MEXC":result}


    # def mexc_status(self):
    #     base_url = "https://www.mexc.com"
    #     path = "/open/api/v2/market/coin/list"
    #     request = requests.get(base_url+path)
    #     print(request.url)
        
        

    def hotbit(self):
        "document: https://github.com/hotbitex/hotbit.io-api-docs/blob/master/rest_api_en.md"
        path = 'https://api.hotbit.io/api/v1/allticker'
        request = requests.get(path)
        currencies = request.json()['ticker']
        expected_currencies = {}
        for currency in currencies:
            symbol = currency['symbol']
            if symbol in self.allowed_currencies:
                price = number_rounder(float(currency['last']))
                expected_currencies.update({symbol:price})
        return {"HOTBIT":expected_currencies}

    def lbank(self):
        "document: https://github.com/LBank-exchange/lbank-official-api-docs"
        base_url = 'https://api.lbkex.com/'
        path = 'v1/ticker.do'
        params = {'symbol':'all'}
        request = requests.get(base_url+path,params=params)
        print(request.url)
        currencies = request.json()
        expected_currencies = {}
        for currency in currencies:
            symbol = currency['symbol'].upper() 
            if symbol in self.allowed_currencies:
                currency_index = self.allowed_currencies.index(symbol)
                price = number_rounder(currency.get('ticker').get('latest'))
                expected_currencies.update({self.allowed_currencies[currency_index]:price})
        return {"LBANK":expected_currencies}
    
    def biture(self):
        base_url = 'https://openapi.bitrue.com/'
        path = '/api/v1/exchangeInfo'
        request = requests.get(base_url+path)
        currencies = request.json().get('symbols')
        expected_currencies = {}
        for currency in currencies:
            symbol = currency.get("symbol")
            expected_allowed_currencies = [currency.replace("_",'') for currency in self.allowed_currencies]
            if symbol.upper() in expected_allowed_currencies:
                currency_index = expected_allowed_currencies.index(symbol.upper())
                float_price = float(currency.get('filters')[0].get('maxPrice'))*(1/10)
                price = number_rounder(float_price)
                expected_currencies.update({self.allowed_currencies[currency_index]:price})
        return {"BITURE":expected_currencies}

    def gate(self):
        "document: https://www.gate.io/docs/apiv4/en/#get-details-of-a-specifc-order"
        host = "https://api.gateio.ws"
        perfix = "/api/v4"
        url = '/spot/tickers'
        request = requests.get(host+perfix+url)
        currencies = request.json()
        expected_currencies = {}
        for currency in currencies:
            symbol = currency.get("currency_pair")
            if symbol in self.allowed_currencies:
                price = number_rounder(float(currency.get("last")))
                expected_currencies.update({symbol:price})
        return {"GATE":expected_currencies}

    def gate_status(self):
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        url = '/spot/currencies'
        request = requests.get(host + prefix + url)
        currencies = request.json()
        expected_data = {}
        for currency in currencies:
            try:
                symbol = currency.get('currency')+"_"+currency.get("chain")
                status = ''
                if symbol in self.allowed_currencies:
                    print(currency.get("withdraw_disabled"))
                    if currency.get("withdraw_disabled") == False:
                        status += 'w'
                    if currency.get("deposit_disabled") == False:
                        status += ' / d'
                    expected_data.update({symbol:status})
            except: pass
        return {"GATE_STATUS":expected_data}



    def xt(self):
        "document: https://github.com/xtpub/api-doc/blob/master/rest-api-v1-en.md"
        host = "https://api.xt.pub"
        perfix = "/data/api/v1"
        url = "/getTickers"
        request = requests.get(host+perfix+url)
        currencies = request.json()
        expected_currencies = {}
        for symbol, value in currencies.items():
            if symbol.upper() in self.allowed_currencies:
                price = number_rounder(value.get("price"))

                expected_currencies.update({symbol:price})
        return {"XT":expected_currencies} 
    


            

currency_request = CurrencyRequest("allowed_currencies.txt","data.accdb")

currency_request.create_database()

while True:
    try:
        currency_request.update_access(currency_request.mexc()) 
    except: print("mexc request failed")
    try:
        currency_request.update_access(currency_request.hotbit())
    except: print("hotbit request failed")
    try:
        currency_request.update_access(currency_request.biture())
    except: print("biture request failed")
    try:
        currency_request.update_access(currency_request.gate())
    except: print("gate request failed")
    try:
        currency_request.update_access(currency_request.lbank())
    except: print("lbank request failed")
    try:
        currency_request.update_access(currency_request.xt())
    except: print("xt request failed")
