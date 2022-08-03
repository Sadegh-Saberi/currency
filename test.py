from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import time

import pickle
import os
options = ChromeOptions()
driver = Chrome(options=options)
driver.get("https://www.lbank.info/")
if os.path.exists('cookies.pkl'):
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        try:
            cookie["expiry"] = time.time()
        except: pass
        driver.add_cookie(cookie)
        print(cookie)
    driver.refresh()

def slash_adder(self,status):
    if len(status) == 2:
        list_status = list(status)
        list_status.insert(1," / ")
        return "".join(list_status)

driver.get("https://www.lbank.info/wallet.html#/wallet-coin")
elements = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[3]/table/tbody/tr")
for element in elements:
    print(element.text)
    status = 'w' if element.find_element(By.XPATH,"/td[6]/div/div/a[1]").get_attribute("class") == "g-glod" else ""
    status += 'd' if element.find_element(By.XPATH,"/td[6]/div/div/a[2]").get_attribute("class") == "g-gold" else ""
    print(slash_adder(status))

# pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
