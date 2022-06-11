import datetime
import os
import json
import time
import uuid
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By

from config import base_path, chrome_service, config_params


def get_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--disable-infobars')
    options.add_argument('-disable-notifications')
    options.add_argument('--no-sandbox')
    return options


def get_location_terms(site):
    f = open(os.path.join(base_path, 'locations.json'))
    location_terms = json.load(f)
    f.close()
    return location_terms["location_terms"][site]


def get_location_urls(site):
    f = open(os.path.join(base_path, 'locations.json'))
    location_terms = json.load(f)
    f.close()
    return location_terms["location_url"][site]


def get_page_tree(driver):
    page = driver.page_source
    page_soup = BeautifulSoup(page, 'html.parser')
    return etree.HTML(str(page_soup))


def reload_main_page(site_id, driver):
    driver.get(config_params["MAIN"][site_id].strip())
    time.sleep(3)


def click_on_side(driver):
    driver.find_element(by=By.XPATH,
                        value='//body').click()


def scroll_to_footer(driver):
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    for i in range(1, total_height, 1000):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(1)


def save_scraped_data(site_id, file_iter, room_data_list):
    r_id = str(uuid.uuid4())[:8]
    save_file_path = os.path.join(base_path,
                                  "scraped_data",
                                  f"{str(datetime.datetime.now().date())}_{site_id}_{file_iter}_{r_id}.csv")
    pd.DataFrame(room_data_list).to_csv(save_file_path, index=False)


def quit_driver(driver):
    driver.stop_client()
    driver.close()
    driver.quit()
