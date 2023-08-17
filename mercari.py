import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.conf import settings


class ScrapingEngine:
    def scrape_data(self, source_url):
        with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
            settings_attrs = f.read()

        res = json.loads(settings_attrs)
    
        options = webdriver.ChromeOptions() 
        options.headless = True
        driver = webdriver.Chrome(options=options)

        driver.get(source_url)

        driver.implicitly_wait(5)
        data = {}

        try:
            data['purchase_price'] = int(driver.find_element(By.XPATH, "//*[@id='item-info']/section[1]/section[1]/div/div/span[2]").text.replace(',', ''))
            data['product_name'] = driver.find_element(By.XPATH, "//*[@id='item-info']/section[1]/div[1]/div/div/h1").text
            product_date = driver.find_element(By.XPATH, "//*[@id='item-info']/section[2]/p").text

            data['nothing'] = False

            if product_date.find(res['mercari']) != -1:
                data['nothing'] = True
        except:
            data['nothing'] = True

        return data
