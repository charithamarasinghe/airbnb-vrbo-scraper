import os
import sys
import time
from selenium import webdriver

from config import config_params, chrome_service
from airbnb_scraper import scrape_airbnb_data
from utility import get_chrome_options, get_location_terms, save_scraped_data, quit_driver, reload_main_page, \
    get_location_urls
from vrbo_scraper import close_date_input, scrape_vrbo_data

base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, base_path)


def extract_airbnb():
    site_id = "airbnb"
    # options = get_chrome_options()
    # driver = webdriver.Chrome(service=chrome_service, options=options)
    driver = webdriver.Chrome(service=chrome_service)
    driver.get(config_params["MAIN"][site_id].strip())
    time.sleep(3)

    location_terms = get_location_terms(site_id)
    location_urls = get_location_urls(site_id)

    file_iter = 1
    # if location_terms:
    #     for location in location_terms:
    #         room_data_list = scrape_airbnb_data(driver=driver, search_location_or_url=location, site_id=site_id,
    #                                             search_type="DESTINATION")
    #         save_scraped_data(site_id=site_id, file_iter=file_iter, room_data_list=room_data_list)
    #         time.sleep(3)
    #         reload_main_page(site_id=site_id, driver=driver)
    #         file_iter += 1

    if location_urls:
        for location_url in location_urls:
            room_data_list = scrape_airbnb_data(driver=driver, search_location_or_url=location_url, site_id=site_id,
                                                search_type="URL")
            save_scraped_data(site_id=site_id, file_iter=file_iter, room_data_list=room_data_list)
            time.sleep(3)
            file_iter += 1

    quit_driver(driver)


def extract_vrbo():
    site_id = "vrbo"
    options = get_chrome_options()
    driver = webdriver.Chrome(service=chrome_service, options=options)
    # driver = webdriver.Chrome(service=chrome_service)
    driver.get(config_params["MAIN"][site_id].strip())
    close_date_input(driver)
    time.sleep(3)

    location_terms = get_location_terms(site_id)
    location_urls = get_location_urls(site_id)

    file_iter = 1
    if location_terms:
        for location in location_terms:
            room_data_list = scrape_vrbo_data(driver=driver, search_location_or_url=location, site_id=site_id,
                                              search_type="DESTINATION")
            save_scraped_data(site_id=site_id, file_iter=file_iter, room_data_list=room_data_list)
            time.sleep(3)
            reload_main_page(site_id=site_id, driver=driver)
            file_iter += 1
    if location_urls:
        for location_url in location_urls:
            room_data_list = scrape_vrbo_data(driver=driver, search_location_or_url=location_url, site_id=site_id,
                                              search_type="URL")
            save_scraped_data(site_id=site_id, file_iter=file_iter, room_data_list=room_data_list)
            time.sleep(3)
            file_iter += 1

    quit_driver(driver)


if __name__ == '__main__':
    extract_airbnb()
    # extract_vrbo()
