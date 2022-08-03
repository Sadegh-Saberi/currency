from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from time import sleep
chrome_options = ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = Chrome(options=chrome_options)
driver.get("https://www.bitrue.com/home/")
action = ActionChains(driver)
sleep(3)
login_element = driver.find_element(By.XPATH,'//*[@id="page-common-header"]/div/div[3]/a[1]')
action.click(login_element).perform()
sleep(3)
user_element = driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div/div/div[1]/input')
user_element.send_keys("sadeghsaberi330@gmail.com")
password_element = driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div/div/div[2]/input')
password_element.send_keys("199B6y3ORt@vb")
login_button = driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div/div/a')
action.click(login_button).perform()
sleep(3)
tick_element = driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div/div[1]/div[2]/label/i')
action.click(tick_element).perform()
code_input = driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div/div[1]/div[2]/div/input')
password = int(input("Enter your password: "))
code_input.send_keys(password)
sleep(10)
confirm_button = driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div/div[1]/div[2]/a')
action.click(confirm_button).perform()
