import datetime
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from config import airbnb_logger
from utility import get_page_tree, scroll_to_footer, click_on_side


def get_page_name(room_page_tree):
    try:
        room_name = room_page_tree.xpath(
            '//*[@id="site-content"]/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[1]/span/h1')[0].text
    except Exception as error:
        room_name = None
        airbnb_logger.error(f"get_page_name: {str(error)}")

    return room_name


def get_room_rating(room_page_tree):
    try:
        room_rating = room_page_tree.xpath(
            '//*[@id="site-content"]/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[1]/span[2]')[
            0].text.split(" ", 1)[0]
    except Exception as error:
        room_rating = None
        airbnb_logger.error(f"get_room_rating: {str(error)}")

    return room_rating


def get_room_rating_count(room_page_tree, room_rating):
    try:
        if room_rating:
            room_rating_count = room_page_tree.xpath(
                '//*[@id="site-content"]/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[1]/span[3]/button')[
                0].text
        else:
            room_rating_count = list(room_page_tree.xpath(
                '//*[@id="site-content"]/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[1]/span[2]')[
                                         0].itertext())[0]
    except Exception as error:
        room_rating_count = None
        airbnb_logger.error(f"get_room_rating_count: {str(error)}")

    return room_rating_count


def get_room_intro(room_page_tree):
    try:
        room_intro = room_page_tree.xpath(
            '//*[@id="site-content"]/div/div[1]/div[3]/div/div[1]/div/div[1]/div/div/section/div/div/div/div[1]/div/h2')[
            0].text
    except Exception as error:
        room_intro = None
        airbnb_logger.error(f"get_room_intro: {str(error)}")

    return room_intro


def get_room_highlights(room_page_tree):
    try:
        room_highlights = "".join(list(room_page_tree.xpath(
            '//*[@id="site-content"]/div/div[1]/div[3]/div/div[1]/div/div[1]/div/div/section/div/div/div/div[1]/ol')[
                                           0].itertext()))
    except Exception as error:
        room_highlights = None
        airbnb_logger.error(f"get_room_highlights: {str(error)}")

    return room_highlights


def get_room_price(room_page_tree):
    try:
        price_temp_spans = room_page_tree.xpath("//*[contains(text(), 'per night')]")
        if price_temp_spans:
            room_price = price_temp_spans[0].text
        else:
            room_price = list(room_page_tree.xpath(
                '//*[@id="site-content"]/div/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div[1]/div[1]/div/div/div/span[2]')[
                                  0].itertext())[0]
    except Exception as error:
        room_price = None
        airbnb_logger.error(f"get_room_price: {str(error)}")

    return room_price


def get_check_in_date(room_page_tree):
    try:
        check_in_date = room_page_tree.xpath("//div[@data-testid='change-dates-checkIn']")[0].text
    except Exception as error:
        check_in_date = None
        airbnb_logger.error(f"get_check_in_date: {str(error)}")
    return check_in_date


def get_check_out_date(room_page_tree):
    try:
        check_out_date = room_page_tree.xpath("//div[@data-testid='change-dates-checkOut']")[0].text
    except Exception as error:
        check_out_date = None
        airbnb_logger.error(f"get_check_out_date: {str(error)}")
    return check_out_date


def get_14_month_availability(driver):
    def __get_date(day_val):
        try:
            date_str = day_val.attrib["data-testid"].split("calendar-day-")[1]
            return datetime.datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
        except Exception as error:
            airbnb_logger.error(f"get_14_month_availability: {str(error)}")
            return ""

    def __get_avail(day_val):
        try:
            disabled = day_val.attrib["data-is-day-blocked"]
            if disabled == "true":
                return "unavailable"
            else:
                return "available"
        except Exception as error:
            airbnb_logger.error(f"get_14_month_availability: {str(error)}")
            return "unknown"

    cal_element = driver.find_element(by=By.XPATH, value='//*[contains(@data-testid, "inline-availability-calendar")]')
    driver.execute_script("arguments[0].scrollIntoView();", cal_element)
    days_avail = {}
    try:
        for _ in range(15):
            temp_tree = get_page_tree(driver=driver)
            days = temp_tree.xpath('//*[contains(@data-testid, "calendar-day")]')

            for day in days:
                day_str = __get_date(day)
                if day_str not in days_avail and day_str != "":
                    days_avail[day_str] = __get_avail(day)
            time.sleep(2)
            driver.find_element(by=By.XPATH,
                                value='//*[contains(@aria-label, "Move forward to switch to the next month")]').click()
    except Exception as error:
        airbnb_logger.error(f"get_14_month_availability: {str(error)}")
    return json.dumps(days_avail)


def get_room_data(loaded_page_driver):
    try:
        scroll_to_footer(driver=loaded_page_driver)
        room_page_tree = get_page_tree(driver=loaded_page_driver)

        availability = get_14_month_availability(driver=loaded_page_driver)
        print(f"14 DAYS AVAILABILITY: {availability}")

        room_name = get_page_name(room_page_tree=room_page_tree)
        print(f"ROOM NAME: {room_name}")

        room_rating = get_room_rating(room_page_tree=room_page_tree)
        print(f"ROOM RATING: {room_rating}")

        check_in = get_check_in_date(room_page_tree=room_page_tree)
        print(f"CHECK IN: {check_in}")

        check_out = get_check_out_date(room_page_tree=room_page_tree)
        print(f"CHECK OUT: {check_out}")

        room_rating_count = get_room_rating_count(room_page_tree=room_page_tree, room_rating=room_rating)
        print(f"ROOM RATING COUNT: {room_rating_count}")

        room_intro = get_room_intro(room_page_tree=room_page_tree)
        print(f"ROOM INTRO: {room_intro}")

        room_highlights = get_room_highlights(room_page_tree=room_page_tree)
        print(f"ROOM HIGHLIGHT: {room_highlights}")

        room_price = get_room_price(room_page_tree=room_page_tree)
        print(f"ROOM PRICE: {room_price}")

        return {
            "room_name": room_name,
            "check_in": check_in,
            "check_out": check_out,
            "room_rating": room_rating,
            "room_rating_count": room_rating_count,
            "room_intro": room_intro,
            "room_highlighted": room_highlights,
            "room_price": room_price,
            "availability": availability
        }
    except Exception as error:
        airbnb_logger.error(f"get_room_data: {str(error)}")
        return {}


def get_room_urls(driver):
    try:
        search_result_page = driver.current_url
        scroll_to_footer(driver=driver)
        page_tree = get_page_tree(driver=driver)

        url_elements = page_tree.xpath('//*[@itemprop="url"]')
        urls = [url_element.attrib["content"] for url_element in url_elements]

        while len(driver.find_elements(by=By.XPATH,
                                       value='//a[@aria-label="Next"]')) > 0:
            driver.find_element(by=By.XPATH,
                                value='//a[@aria-label="Next"]').click()
            wait = WebDriverWait(driver, 5)
            wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="site-content"]/div[2]/div[3]')))
            time.sleep(5)
            scroll_to_footer(driver=driver)
            page_tree = get_page_tree(driver=driver)
            temp_url_elements = page_tree.xpath('//*[@itemprop="url"]')
            urls.extend([temp_url_element.attrib["content"] for temp_url_element in temp_url_elements])

        driver.get(search_result_page)
        wait = WebDriverWait(driver, 5)
        wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="site-content"]/div[2]/div[3]')))
        time.sleep(2)

        return urls
    except Exception as error:
        airbnb_logger.error(f"get_room_urls: {str(error)}")
        return []


def scroll_down_and_up(driver):
    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 1000);")


def initiate_airbnb_search(search_type, driver, search_location_or_url):
    try:
        if search_type == "URL":
            driver.get(search_location_or_url)

        elif search_type == "DESTINATION":
            # open adding destination
            driver.find_element(by=By.XPATH,
                                value='//button[@data-index="0"]').click()

            # enter destination
            driver.find_element(by=By.NAME,
                                value='query').send_keys(search_location_or_url)
            click_on_side(driver=driver)

            # open adding date range
            driver.find_element(by=By.XPATH,
                                value='//button[@data-index="1"]').click()

            # select start date (select date after current date)
            driver.find_elements(by=By.XPATH,
                                 value='//*[contains(@aria-label, "Choose")]')[1].click()

            # select end date (select 3 days after current date)
            driver.find_elements(by=By.XPATH,
                                 value='//*[contains(@aria-label, "Choose")]')[3].click()
            scroll_down_and_up(driver=driver)

            # open adding member count
            driver.find_element(by=By.XPATH,
                                value='//button[@data-index="2"]').click()

            # adding one adult
            driver.find_element(by=By.XPATH,
                                value='//*[@id="stepper-adults"]/button[2]').click()

            # search
            driver.find_element(by=By.XPATH,
                                value='//*[@id="search-tabpanel"]/div/div[5]/div[3]/button').click()

        else:
            print("ERROR: Invalid search type")
            airbnb_logger.error(
                f"initiate_airbnb_search (URL/DESTINATION: {search_location_or_url}): Invalid search type")
    except Exception as error:
        airbnb_logger.error(f"initiate_airbnb_search (URL/DESTINATION: {search_location_or_url}): {str(error)}")


def scrape_airbnb_data(driver, search_location_or_url, site_id, search_type):
    try:
        initiate_airbnb_search(search_type=search_type, driver=driver, search_location_or_url=search_location_or_url)

        time.sleep(2)
        driver.refresh()

        wait = WebDriverWait(driver, 5)
        wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="site-content"]/div[2]/div[3]')))

        urls = get_room_urls(driver=driver)

        room_data_list = []
        for url in urls:
            print(f"URL: {url}")
            driver.get(f"https://{url}")
            wait = WebDriverWait(driver, 5)
            wait.until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/div[2]/div/div/div/div')))

            print("Extracting room data...")
            time.sleep(3)
            room_data = get_room_data(loaded_page_driver=driver)
            room_data["search_location_or_url"] = search_location_or_url
            room_data["search_type"] = search_type
            room_data["site"] = site_id
            if room_data:
                room_data_list.append(room_data)
            else:
                airbnb_logger.error(f"No data extracted for URL: {str(url)}")

            driver.back()
            wait = WebDriverWait(driver, 5)
            wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="site-content"]/div[2]/div[3]')))
            time.sleep(2)

        return room_data_list

    except Exception as error:
        airbnb_logger.error(f"scrape_airbnb_data (URL/DESTINATION: {search_location_or_url}): {str(error)}")
        return {}
