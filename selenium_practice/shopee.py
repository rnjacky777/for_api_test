import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

xpath = "//div[contains(@data-sqe ,'item')][{index}]"

with open("token.json") as f:
    cookies = json.load(f)


# f.close()   
options = Options()
options.add_argument('--ignore-certificate-errors')
options.chrome_executable_path = "chromedriver_path"
driver=webdriver.Chrome(options=options)


driver.get("https://shopee.tw/")

for cookie in cookies:
    driver.add_cookie(cookie)

driver.refresh()

#取得網頁原始碼 print(driver.page_source)
#selenium無法執行shadowRoot,所以需要叫driver去執行script
driver.execute_script('document.querySelector("shopee-banner-popup-stateful").shadowRoot.querySelector(".shopee-popup__close-btn").click()')
#Xpath(網頁的絕對路徑) 以蝦皮搜尋鍵為例子:Console > $x("//*[@id='main']/div/header/div[2]/div/div[1]/div[1]/button") 地址的概念
time.sleep(5)
search_xpath = "//input[@class ='shopee-searchbar-input__input']"
search = driver.find_element(By.XPATH,search_xpath)
search.clear()
search.send_keys("航海王")
time.sleep(5)
search_buttom_xpath = "//button[contains(@class ,'btn-solid-primary')]"
search_buttom = driver.find_element(By.XPATH,search_buttom_xpath)
search_buttom.click()
# time.sleep(40)
thing_xpath = "//div[@class='dpiR4u']"
thing =  driver.find_elements(By.XPATH,thing_xpath)
price_xpath = "//div[@class='hpDKMN']"
price =  driver.find_elements(By.XPATH,price_xpath)
for prices in price:
    print(price.text)
driver.quit()