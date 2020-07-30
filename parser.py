import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



d = webdriver.Chrome()
with open('saved_bands.txt') as f:
    saved_bands = f.read().splitlines()
count = len(saved_bands)
d.implicitly_wait(2)
d.get("https://www.metal-archives.com/lists/black")
next_page = "//a[@class='paginate_active']/following-sibling::a"
bands = []
wait = WebDriverWait(d, 2)
elt = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sorting_1')))
while d.find_elements_by_xpath(next_page):
    nav = d.find_element_by_xpath(next_page)
    d.find_element_by_xpath(next_page).click()
    elt2 = wait.until(EC.staleness_of(nav))
    bands_rows = d.find_elements_by_xpath("//tbody//td/a")
    for b in bands_rows:
        band_name = re.sub('[?.!/;:]', '', b.text)
        band_url = b.get_attribute('href')
        with open("out2.csv", "a+", newline="", encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([band_name, band_url])
        count+=1
        print('total bands: ' + str(count))

