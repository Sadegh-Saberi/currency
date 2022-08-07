from threading import Thread
import requests
import pyodbc
from utils import percatge_difference, number_rounder
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ChromeOptions
import hashlib
import hmac
import json
import time
import os

class CurrencyRequest:
    def __init__(self,allowed_currencies_file:str,extra_currencies:list,access_file:str):
        self.data = {
            "MEXC":{},
            "MEXC_STATUS":{},
            "MEXC_CHANGE_PERCENT":{},
            "XT":{},
            "XT_STATUS":{},
            "GATE":{},
            "GATE_STATUS":{},
            "LBANK":{},
            "PHEMEX":{},
            "COINEX":{},
            "COINEX_STATUS":{},
            "BIBOX":{},
            "BIBOX_STATUS":{},
        }            
        # set time sleep for each currancy request duration
        self.sleep_time = 3
        # database file absolute path
        file_path = os.path.abspath(access_file)
        # the string connection for connection to access database
        self.connection_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};' \
            fr'DBQ={file_path};'
        with open(allowed_currencies_file, "r") as file:


            # an allowed currency has 2 parts separated with '/' (slash) containing the name and the price of the currency
            allowed_currencies = {currency.upper() for currency in file.read().replace(
                " ", "").replace("\n", ",").replace("/","_").split(",") if currency != ''}  # read the data in the text file and convert them to the list of wnated currencies

            try:
                # remove the empty string items from the set
                allowed_currencies.remove("")
            except:
                pass
            finally:
                # names like BTC, PIL, SHIB ,...
                self.allowed_names = {name.split(
                    "/")[0] for name in allowed_currencies}



        self.allowed_currencies = list(allowed_currencies)
        self.allowed_currencies.extend(extra_currencies)  

    def create_database(self):
        with pyodbc.connect(self.connection_string) as connection:
            with connection.cursor() as cursor:
                try:
                    query = """CREATE TABLE currencies 
                        ([currency name] VARCHAR,
                        mexc VARCHAR,
                        mexc_status VARCHAR,
                        lbank VARCHAR,
                        xt VARCHAR,
                        xt_status VARCHAR,
                        gate VARCHAR,
                        gate_status VARCHAR,
                        phemex VARCHAR,
                        coinex VARCHAR,
                        coinex_status VARCHAR,
                        bibox VARCHAR,
                        bibox_status VARCHAR,
                        [percentage difference] NUMBER
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

    def update_access(self):
        with pyodbc.connect(self.connection_string) as connection:
            with connection.cursor() as cursor:
                while True:
                    for exchange, value in list(self.data.items()):
                        for currency_name, price in list(value.items()):
                            try:
                                query = f"""UPDATE currencies
                                        SET {exchange.lower()} = '{price}'
                                        WHERE [currency name] = '{currency_name}';"""
                                cursor.execute(query)
                                connection.commit()
                            except: pass

                    query = "SELECT * FROM currencies"
                    rows = cursor.execute(query).fetchall()
                    expected_rows_values = []
                    for row in rows:
                        temperory_list = []
                        for price in row[1:-1]:
                            try:
                                temperory_list.append(float(price))
                            except: pass

                        # try:
                        #     temperory_list.pop(1)
                        # except: pass
                        expected_rows_values.append(temperory_list)

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
                    time.sleep(10)

    def update_access2(self):
        with pyodbc.connect(self.connection_string) as connection:
            with connection.cursor() as cursor:
                try:
                    query = """
                        CREATE TABLE currencies2
                            ([currency name] VARCHAR,
                            mexc VARCHAR,
                            mexc_change_percent VARCHAR,
                            mexc_status VARCHAR,
                            lbank VARCHAR,
                            xt VARCHAR,
                            xt_status VARCHAR,
                            gate VARCHAR,
                            gate_status VARCHAR,
                            phemex VARCHAR,
                            coinex VARCHAR,
                            coinex_status VARCHAR,
                            bibox VARCHAR,
                            bibox_status VARCHAR,
                            [percentage difference] NUMBER
                            )
                    """
                    cursor.execute(query)
                    connection.commit()
                except: pass
                while True:
                    for exchange, value in list(self.data.items()):
                        for currency_name, price in list(value.items()):
                            # try:

                                query = f"SELECT * FROM currencies2 WHERE [currency name] = '{currency_name}'"
                                if cursor.execute(query).fetchone() == None and exchange == "MEXC":
                                    query = f"INSERT INTO currencies2 ([currency name]) VALUES ('{currency_name}')"
                                    cursor.execute(query)
                                    connection.commit()
                                else:
                                    query = f"""UPDATE currencies2
                                            SET {exchange.lower()} = '{price}'
                                            WHERE [currency name] = '{currency_name}';"""
                                    cursor.execute(query)
                                    connection.commit()


                    query = "SELECT * FROM currencies2"
                    rows = cursor.execute(query).fetchall()
                    expected_rows_values = []
                    for row in rows:
                        temperory_list = []
                        for price in row[1:-1]:
                            try:
                                temperory_list.append(float(price))
                            except: pass

                        expected_rows_values.append(temperory_list)

                    for row in expected_rows_values:
                        # get the row index in 'expected_rows_values' list
                        row_index = expected_rows_values.index(row)
                        # get the row currency name for adding the percentage difference data
                        currency_name = rows[row_index][0]
                        # if more that one price is in the row ...
                        if len(row) > 1:
                            result = percatge_difference(row)
                            query = f"""
                                        UPDATE currencies2
                                        SET [percentage difference] = '{result}'
                                        WHERE [currency name] = '{currency_name}';
                                        """
                            cursor.execute(query)
                            connection.commit()
                    time.sleep(10)
    # def update_access(self,data:dict):
    #     with pyodbc.connect(self.connection_string) as connection:
    #         with connection.cursor() as cursor:

    #                 for exchange, value in list(data.items()):
    #                     for currency_name, price in list(value.items()):
    #                         query = f"""UPDATE currencies
    #                                 SET {exchange.lower()} = '{price}'
    #                                 WHERE [currency name] = '{currency_name}';"""
    #                         cursor.execute(query)
    #                         connection.commit()

    #                 query = "SELECT * FROM currencies"
    #                 rows = cursor.execute(query).fetchall()
    #                 expected_rows_values = []
    #                 for row in rows:
    #                     temperory_list = []
    #                     for price in row[1:-1]:
    #                         try:
    #                             temperory_list.append(float(price))
    #                         except: pass

    #                     # try:
    #                     #     temperory_list.pop(1)
    #                     # except: pass
    #                     expected_rows_values.append(temperory_list)

    #                 for row in expected_rows_values:
    #                     # get the row index in 'expected_rows_values' list
    #                     row_index = expected_rows_values.index(row)
    #                     # get the row currency name for adding the percentage difference data
    #                     currency_name = rows[row_index][0]
    #                     # if more that one price is in the row ...
    #                     if len(row) > 1:
    #                         result = percatge_difference(row)
    #                         query = f"""
    #                                     UPDATE currencies
    #                                     SET [percentage difference] = '{result}'
    #                                     WHERE [currency name] = '{currency_name}';
    #                                     """
    #                         cursor.execute(query)
    #                         connection.commit()
    #                 time.sleep(10)

    def options(self, hidden: bool = True):

        prefs = {'profile.default_content_setting_values': {'images': 2,
                                                            'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2,
                                                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2,
                                                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                                                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
                                                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2,
                                                            'durable_storage': 2}}

        options = ChromeOptions()
        options.add_experimental_option('prefs', prefs)
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        if hidden == True:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        else:
            options.add_argument("--start-maximized")
        return options

    def mexc_price_change(self):        
        "document: https://mxcdevelop.github.io/APIDoc/open.api.v2.en.html#ticker-information"
        base_url = 'https://www.mexc.com/'
        prices_path = 'open/api/v2/market/ticker'
        change_percent_url = "https://api.mexc.com/api/v3/ticker/24hr"

        while True:
            change_percent_data = {}
            with requests.get(change_percent_url) as response:
                for currency in response.json():
                    symbol = currency.get("symbol")
                    change_percent = currency.get("priceChangePercent")
                    change_percent_data.update({symbol:change_percent})

            with requests.get(base_url+prices_path) as response:
                currencies = response.json()['data']
                for pair_currency in currencies:
                    symbol = pair_currency.get('symbol')
                    # try:
                    _str_change_percent = change_percent_data.get(symbol.replace("_",""))
                    try:
                        change_percent = float(_str_change_percent)*100
                        if symbol in self.allowed_currencies and change_percent > 5 or change_percent < -5:
                            price = number_rounder(float(pair_currency['last']))
                            self.data.get("MEXC").update({symbol:price})
                            self.data.get("MEXC_CHANGE_PERCENT").update({symbol:f"{number_rounder(change_percent)}%"})
                            # print(symbol)
                    except:pass
            time.sleep(self.sleep_time)
    
    def mexc(self):        
        "document: https://mxcdevelop.github.io/APIDoc/open.api.v2.en.html#ticker-information"
        base_url = 'https://www.mexc.com/'
        prices_path = '/open/api/v2/market/ticker'

        while True:
            try:
                with requests.get(base_url+prices_path) as response:
                    currencies = response.json()['data']
                    # data = {}
                    for pair_currency in currencies:
                        symbol = pair_currency['symbol']
                        if symbol in self.allowed_currencies:
                            price = number_rounder(float(pair_currency['last']))
                            # self.data.get("MEXC").update({symbol:price})
                            # print({"MEXC":{symbol:price}})
                            # data.update({symbol:price})
                            yield {symbol:price}
                    # self.update_access({"MEXC":data})
            except: print("mexc request failed!")
            time.sleep(self.sleep_time)


    
    def mexc_status(self):
        base_url = 'https://www.mexc.com/'
        withdraw_deposit_path = "/open/api/v2/market/coin/list"
        while True:
            try:
                with requests.get(base_url+withdraw_deposit_path) as first:
                    currencies_status = first.json().get("data")

                for allowed_currency in self.allowed_currencies:
                    expected_currency = allowed_currency.split("_")[0]
                    for currency in currencies_status:
                        currency_name = currency.get('currency')
                        if currency_name == expected_currency:
                            # get the first coin for testing ...
                            chain = currency.get('coins')[0]
                            status  = 'w' if chain.get('is_withdraw_enabled') == True else '' 
                            status += 'd' if chain.get("is_deposit_enabled") == True else ''
                            # insert ' / ' into status for separating 'w' and 'd' letters
                            if len(status) == 2:
                                status_list = list(status)
                                status_list.insert(1,' / ')
                                status = ''.join(status_list)
                            self.data.get("MEXC_STATUS").update({allowed_currency:status})
                            break
                break
            except: print("mexc_status request failed!")
            time.sleep(self.sleep_time)



    def hotbit(self):
        "document: https://github.com/hotbitex/hotbit.io-api-docs/blob/master/rest_api_en.md"
        path = 'https://api.hotbit.io/api/v1/allticker'
        while True:
            try:
                request = requests.get(path)
                currencies = request.json()['ticker']
                for currency in currencies:
                    symbol = currency['symbol']
                    if symbol in self.allowed_currencies:
                        price = number_rounder(float(currency['last']))
                        self.data.get("HOTBIT").update({symbol:price})
            except: print("hotbit request failed!")
            time.sleep(self.sleep_time)



    def lbank(self):
        "document: https://github.com/LBank-exchange/lbank-official-api-docs"
        base_url = 'https://api.lbkex.com/'
        path = 'v1/ticker.do'
        params = {'symbol':'all'}

        # allowed_scraping_currencies = self.allowed_currencies.copy()

        while True:
            try:
                response = requests.get(base_url+path,params=params)
                currencies = response.json()
                for currency in currencies:
                    symbol = currency['symbol'].upper() 
                    if symbol in self.allowed_currencies:
                        currency_index = self.allowed_currencies.index(symbol)
                        price = number_rounder(currency['ticker']['latest'])
                        self.data.get("LBANK").update({self.allowed_currencies[currency_index]:price})
                        # allowed_scraping_currencies.remove(symbol)

            except: print("lbank request failed!")
            # print('lbank request updated')


    def lbank_scraping(self):
        base_url = 'https://api.lbkex.com/'
        path = 'v1/ticker.do'
        params = {'symbol':'all'}
        api_currencies = list()
        with requests.get(base_url+path,params=params) as response:
            for currency in response.json():
                api_currencies.append(currency.get("symbol").upper())

        
        allowed_scraping_currencies = [currency for currency in self.allowed_currencies if currency not in api_currencies]
        print(allowed_scraping_currencies)
            
        driver = Chrome(options=self.options(hidden=False))
        action = ActionChains(driver)
        driver.get("https://www.lbank.info/quotes.html#/exchange/usd")
        search_box = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CSS_SELECTOR,"body > div.quptes > div.g-wrap > div > div.market > div.table-container > div.market-header.g-between-center > div > div > div.el-input.el-input--prefix > input")))
        while True:
            for currency in allowed_scraping_currencies:
                search_box.clear()
                search_box.send_keys(currency.replace('_','/'))
                try:
                    first_search_result = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'body > div.el-autocomplete-suggestion.el-popper > div.el-scrollbar > div:nth-child(1) > ul > li:nth-child(1)')))
                    action.click(first_search_result).perform()
                    price = WebDriverWait(driver,5).until(EC.presence_of_element_located(((By.CSS_SELECTOR,"body > div.quptes > div.g-wrap > div > div.market > div.table-container > div.market-body > table > tr:nth-child(2) > td:nth-child(3) > span:nth-child(1)")))).text
                    self.data.get("LBANK").update({currency:price})
                    print(currency,"accepted :)")
                except: allowed_scraping_currencies.remove(currency); print(currency,"deleted!")
            print("lbank scraping updated")
            print(allowed_scraping_currencies)
            

    
    def biture(self):
        base_url = 'https://openapi.bitrue.com/'
        path = '/api/v1/exchangeInfo'
        expected_allowed_currencies = [currency.replace("_",'') for currency in self.allowed_currencies]
        while True:
            try:
                request = requests.get(base_url+path)
                currencies = request.json().get('symbols')
                for currency in currencies:
                    symbol = currency.get("symbol")
                    if symbol.upper() in expected_allowed_currencies:
                        currency_index = expected_allowed_currencies.index(symbol.upper())
                        float_price = float(currency.get('filters')[0].get('maxPrice'))*(1/10)
                        price = number_rounder(float_price)
                        self.data.get("BITURE").update({self.allowed_currencies[currency_index]:price})
                        # expected_currencies.update({self.allowed_currencies[currency_index]:price})

            except: print("biture request failed!")
            time.sleep(self.sleep_time)



    def gate(self):
        "document: https://www.gate.io/docs/apiv4/en/#get-details-of-a-specifc-order"
        host = "https://api.gateio.ws"
        perfix = "/api/v4"
        url = '/spot/tickers'
        while True:
            try:
                request = requests.get(host+perfix+url)
                currencies = request.json()
                for currency in currencies:
                    symbol = currency.get("currency_pair")
                    if symbol in self.allowed_currencies:
                        price = number_rounder(float(currency.get("last")))
                        self.data.get("GATE").update({symbol:price})

            except: print("gate request failed!")
            time.sleep(self.sleep_time)


    def gate_status(self):
        "document: https://www.gate.io/docs/apiv4/en/#list-all-currencies-details"
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '/spot/currencies'
        while True:
            try:
                response = requests.request('GET', host + prefix + url, headers=headers)
                for currency in response.json():
                    symbol = currency.get("currency")
                    if symbol != None:
                        for allowed_currency in self.allowed_currencies:
                            if allowed_currency.split("_")[0] == symbol:
                                status = 'w' if not currency.get("withdraw_disabled") else ""
                                status += 'd' if not currency.get("deposit_disabled") else ""
                                if len(status) == 2:
                                    status_list = list(status)
                                    status_list.insert(1,' / ')
                                    status = ''.join(status_list)
                                self.data.get("GATE_STATUS").update({allowed_currency:status})
                break
            except: print("gate_status request failed!")
            time.sleep(self.sleep_time)


    def xt(self):
        "document: https://github.com/xtpub/api-doc/blob/master/rest-api-v1-en.md"
        host = "https://api.xt.pub"
        perfix = "/data/api/v1"
        url = "/getTickers"
        while True:
            try:
                response = requests.get(host+perfix+url)
                currencies = response.json()
                for symbol, value in currencies.items():
                    if symbol.upper() in self.allowed_currencies:
                        price = number_rounder(value.get("price"))
                        self.data.get("XT").update({symbol:price})
                time.sleep(self.sleep_time)
            except: print("xt request failed!")
            time.sleep(self.sleep_time)

    
    def xt_status(self):
        base_url = "https://www.xt.pub"
        path = "/exchange/api/assets"
        while True:
            try:
                response = requests.get(base_url+path)
                currencies = response.json()
                for allowed_currency in self.allowed_currencies:
                    allowed_single_currency = allowed_currency.split("_")[0]
                    for currency in currencies:
                        for currency_name, value in currency.items():
                            if currency_name == allowed_single_currency:
                                status = 'w' if value.get("can_deposit") == "true" else ""
                                status += "d" if value.get("can_withdraw") == "true" else ""
                                if len(status) == 2:
                                    list_status = list(status)
                                    list_status.insert(1," / ")
                                    status = "".join(list_status)
                                self.data.get("XT_STATUS").update({allowed_currency:status})
                break
            except: print("xt_status request failed!")
            time.sleep(self.sleep_time)


    def phemex(self):
        try:
            driver = Chrome(options=self.options())
            driver.get("https://phemex.com/markets?tabType=Spot")
            elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "body > div.wrap.svelte-1jjhroo > div.wrap.svelte-a0hxct > div > div.row.cp.wsn")))
            expected_elements = {}
            for element in elements:
                currency = element.find_element(
                    By.CSS_SELECTOR, "div:nth-child(2) > div > div > span").text.replace(" ", "").replace("/","_")
                if currency in self.allowed_currencies:
                    price_element = element.find_element(
                        By.CSS_SELECTOR, "div:nth-child(3)")
                    expected_elements.update({currency: price_element})
        except: print("phemex get data for scraping failed!")
        while True:
            try:
                for currency, price_element in expected_elements.items():
                    price = number_rounder(float(price_element.text))
                    self.data.get("PHEMEX").update({currency: price})
                    time.sleep(self.sleep_time)
            except: print("phemex scraping failed!")
            time.sleep(self.sleep_time)

                
            
    # coinext needs VPN to be connected ...
    def coinex(self):
        "document: https://viabtc.github.io/coinex_api_en_doc/spot/#docsspot001_market008_all_market_ticker"

        base_url = "https://api.coinex.com"
        path = "/v1/market/ticker/all"
        expected_allowed_currencies = [currency.replace("_","") for currency in self.allowed_currencies]
        while True:
            try:
                with requests.get(base_url+path) as request:
                    currencies = request.json().get("data").get("ticker")
                    for currency, value in currencies.items():
                        if currency in expected_allowed_currencies:
                            index = expected_allowed_currencies.index(currency)
                            price = number_rounder(float(value.get("last")))
                            self.data.get("COINEX").update({self.allowed_currencies[index]:price})
            except: print("coinex Error! Maybe your vpn is not connected!")
            time.sleep(self.sleep_time)


    def coinex_status(self):
        "document: https://viabtc.github.io/coinex_api_en_doc/spot/#docsspot001_market010_asset_config"
        base_url = "https://api.coinex.com"
        path = "/v1/common/asset/config"
        # expected_allowed_currencies = [currency.split("_")[0] for currency in self.allowed_currencies]
        # while True:
        try:
            with requests.get(base_url+path) as request:
                currencies = request.json().get("data")
                for currency in self.allowed_currencies:
                    expected_currency = currency.split("_")[0]
                    value = currencies.get(expected_currency)
                    if value != None:
                        status = 'w' if value.get("can_withdraw") == True else ''
                        status += 'd' if value.get("can_deposit") == True else ''
                        if len(status) == 2:
                            status_list = list(status)
                            status_list.insert(1,' / ')
                            status = ''.join(status_list)
                        self.data.get('COINEX_STATUS').update({currency:status})
        except: print("coinex_status Error! Maybe your vpn is not connected!")
        time.sleep(self.sleep_time)



    def bibiox(self):
        base_url = "https://api.bibox.com"
        path = "/v3/mdata/marketAll"
        while True:
            try:
                with requests.get(base_url+path) as request:
                    currencies = request.json().get("result")
                    for currency in currencies:
                        symbol = currency.get("coin_symbol")+"_"+currency.get("currency_symbol")
                        if symbol in self.allowed_currencies:
                            price = number_rounder(float(currency.get("last")))
                            self.data.get("BIBOX").update({symbol:price})
            except: print("bibox request failed!")
            time.sleep(self.sleep_time)



    def bibox_status(self):
        "document: https://biboxcom.github.io/v3/spot/en/?python#get-currency-configuration"
        base_url = "https://api.bibox.com" # 'https://api.bibox.tel' #
        # path = "/v3.1/transfer/coinConfig"
        API_KEY = 'fc12d470d95e33187c1846b99894d245d6b9d56c'
        SECRET_KEY = '20dc6f4afb368158a6a64fd44ab9fe88a67d456d'

        def do_sign(body):
            timestamp = int(time.time()) * 1000
            # to_sign = str(timestamp)+json.dumps(body,separators=(',',':'))
            to_sign = str(timestamp) + json.dumps(body)
            sign = hmac.new(SECRET_KEY.encode("utf-8"), to_sign.encode("utf-8"), hashlib.md5).hexdigest()
            headers = {
                'bibox-api-key': API_KEY,
                'bibox-api-sign': sign,
                'bibox-timestamp': str(timestamp)
            }
            return headers


        def do_request():
            path = '/v3.1/transfer/coinConfig'
            body = {

            }
            headers = do_sign(body)
            response = requests.post(base_url + path, json=body, headers=headers)
            currencies = response.json().get("result")
            for allowed_currency in self.allowed_currencies:
                expected_allowed_currency = allowed_currency.split("_")[0]
                for currency in currencies:
                    if currency.get("coin_symbol") == expected_allowed_currency:
                        status = 'w' if currency.get("enable_withdraw") == 1 else ''
                        status += 'd' if currency.get("enable_deposit") == 1 else ''
                        if len(status) == 2:
                            list_status = list(status)
                            list_status.insert(1,' / ')
                            status = ''.join(list_status)
                        self.data.get("BIBOX_STATUS").update({allowed_currency:status})
                        break
        while True:
            try:
                do_request()
            except: print("bibox_status request failed!")
            time.sleep(self.sleep_time)


all_allowed_currencies = []
with requests.get("https://www.mexc.com/open/api/v2/market/symbols") as request:
    for currency in request.json().get("data"):
        symbol = currency.get("symbol")
        symbol_list = list(symbol.split("_")[0])[::-1]
        for chr in symbol_list:
            try:
                int(chr)
                break
            except: pass
        else: all_allowed_currencies.append(symbol)


currency_request = CurrencyRequest("allowed_currencies.txt",all_allowed_currencies,"data.accdb")
currency_request.create_database()
Thread(target=currency_request.update_access2).start()
Thread(target=currency_request.update_access).start()

status_getters = [
    currency_request.mexc_status,
    currency_request.gate_status,
    currency_request.coinex_status,
    currency_request.bibox_status,
    currency_request.xt_status,
    
] 

# # mexc_data = {}
# for symbol_data in currency_request.mexc():
#     mexc_data.update(symbol_data)
#     print(symbol_data)
# print(mexc_data)
# currency_request.update_access({"MEXC":mexc_data})

# Thread(target=currency_request.mexc).start()

Thread(target=currency_request.mexc_price_change).start()
Thread(target=currency_request.gate).start()
Thread(target=currency_request.coinex).start()
Thread(target=currency_request.bibiox).start()
Thread(target=currency_request.xt).start()
Thread(target=currency_request.lbank).start()
Thread(target=currency_request.lbank_scraping).start()
Thread(target=currency_request.phemex).start()

while True:
    for method in status_getters:
        Thread(target=method).start()
    time.sleep(300)