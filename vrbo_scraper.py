import datetime
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from config import vrbo_logger
from utility import get_page_tree, scroll_to_footer, click_on_side


def get_page_name(room_page_tree):
    try:
        room_name = room_page_tree.xpath('//*[@data-wdio="property-headline__headline"]')[0].text

    except Exception as error:
        room_name = None
        vrbo_logger.error(f"get_page_name: {str(error)}")

    return room_name


def get_room_rating(room_page_tree):
    try:
        room_rating = room_page_tree.xpath('//*[@class="review-summary__ratings-score"]')[0].text
    except Exception as error:
        room_rating = None
        vrbo_logger.error(f"get_room_rating: {str(error)}")

    return room_rating


def get_room_rating_count(room_page_tree, room_rating):
    try:
        if room_rating:
            room_rating_count = room_page_tree.xpath('//*[contains(@class, "reviews-wrapper")]')[0].find("h2").text
        else:
            room_rating_count = 0
    except Exception as error:
        room_rating_count = None
        vrbo_logger.error(f"get_room_rating_count: {str(error)}")

    return room_rating_count


def get_room_intro(room_page_tree):
    try:
        room_intro = room_page_tree.xpath('//*[@class="collapsible-content"]')[0].find("h3").text
    except Exception as error:
        room_intro = None
        vrbo_logger.error(f"get_room_intro: {str(error)}")

    return room_intro


def get_room_highlights(room_page_tree):
    try:
        items = room_page_tree.xpath('//*[contains(@class, "four-pack__block-bod")]')

        complete_string = ""
        for item in items:
            item_values = item.findall("li")
            complete_string += " . ".join([item_value.text for item_value in item_values]) + " | "

        room_highlights = complete_string.strip()
    except Exception as error:
        room_highlights = None
        vrbo_logger.error(f"get_room_highlights: {str(error)}")

    return room_highlights


def get_room_price(room_page_tree):
    try:
        room_price = room_page_tree.xpath('//*[@class="rental-price__amount"]')[0].text
    except Exception as error:
        room_price = None
        vrbo_logger.error(f"get_room_price: {str(error)}")

    return room_price


def get_check_in_date(room_page_tree):
    try:
        check_in_date = room_page_tree.xpath("//input[@name='arriveDate']")[0].attrib["value"]
    except Exception as error:
        check_in_date = None
        vrbo_logger.error(f"get_check_in_date: {str(error)}")
    return check_in_date


def get_check_out_date(room_page_tree):
    try:
        check_out_date = room_page_tree.xpath("//input[@name='departDate']")[0].attrib["value"]
    except Exception as error:
        check_out_date = None
        vrbo_logger.error(f"get_check_out_date: {str(error)}")
    return check_out_date


def get_14_month_availability(driver):
    def __get_date(day_val):
        try:
            date_str = day_val.attrib["aria-label"].split("is")[0].strip()
            return datetime.datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
        except Exception as error:
            vrbo_logger.error(f"get_14_month_availability: {str(error)}")
            return ""

    def __get_avail(day_val):
        try:
            class_val = day_val.xpath("*//div")[0].attrib["class"]
            if "disabled" in class_val:
                return "unavailable"
            else:
                return "available"
        except Exception as error:
            vrbo_logger.error(f"get_14_month_availability: {str(error)}")
            return "unknown"

    cal_element = driver.find_element(by=By.XPATH, value='//*[contains(@data-wdio, "availability-section-title")]')
    driver.execute_script("arguments[0].scrollIntoView();", cal_element)

    days_avail = {}
    for _ in range(15):
        temp_tree = get_page_tree(driver=driver)
        days = temp_tree.xpath('//*[contains(@class, "day") and contains(@class, "no-gridlines")]')
        days = [day for day in days if day.tag == "td"]

        for day in days:
            day_str = __get_date(day)
            if day_str not in days_avail and day_str != "":
                days_avail[day_str] = __get_avail(day)
        time.sleep(2)
        driver.find_element(by=By.XPATH,
                            value='//*[contains(@class, "cal-controls__button--next")]').click()

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
        vrbo_logger.error(f"get_room_data: {str(error)}")
        return {}


def get_room_urls(driver):
    try:
        search_result_page = driver.current_url
        close_date_input(driver=driver)
        scroll_to_footer(driver=driver)
        page_tree = get_page_tree(driver=driver)
        url_elements = page_tree.xpath('//*[@class="media-flex__content"]')
        urls = [f'https://www.vrbo.com{url_element.attrib["href"]}' for url_element in url_elements]

        while len(driver.find_elements(by=By.XPATH,
                                       value='//a[@data-wdio="pager-next"]')) > 0:
            driver.find_element(by=By.XPATH,
                                value='//a[@aria-label="Next page"]').click()
            wait = WebDriverWait(driver, 5)
            wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'HitCollection')))
            time.sleep(2)

            close_date_input(driver=driver)
            scroll_to_footer(driver=driver)
            page_tree = get_page_tree(driver=driver)

            temp_url_elements = page_tree.xpath('//*[@class="media-flex__content"]')
            urls.extend([temp_url_element.attrib["href"] for temp_url_element in temp_url_elements])

        driver.get(search_result_page)
        wait = WebDriverWait(driver, 5)
        wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'HitCollection')))
        time.sleep(2)
        close_date_input(driver=driver)

        return urls
    except Exception as error:
        vrbo_logger.error(f"get_room_urls: {str(error)}")
        return []


def close_date_input(driver):
    try:
        driver.find_element(by=By.XPATH,
                            value='//*[contains(@class, "picker__close-btn")]').click()
    except Exception as error:
        vrbo_logger.error(f"close_date_input: {str(error)}")


def initiate_vrbo_search(search_type, driver, search_location_or_url):
    try:
        if search_type == "URL":
            driver.get(search_location_or_url)

        elif search_type == "DESTINATION":
            # enter destination
            driver.find_element(by=By.ID,
                                value='react-destination-typeahead').send_keys(search_location_or_url)

            # select start date (select date after current date)
            driver.find_elements(by=By.XPATH,
                                 value='//td[@tabindex="-1"]')[0].click()

            # select end date (select 3 days after current date)
            driver.find_elements(by=By.XPATH,
                                 value='//td[@tabindex="-1"]')[3].click()

            # adding one adult
            driver.find_element(by=By.XPATH,
                                value='//*[contains(@class, "quantity-selector__btn--increase")]').click()
            # close guests input
            close_date_input(driver=driver)

            # search
            driver.find_element(by=By.XPATH,
                                value='//*[contains(@class, "search-form__button-field")]').click()

        else:
            print("ERROR: Invalid search type")
            vrbo_logger.error(
                f"initiate_vrbo_search (URL/DESTINATION: {search_location_or_url}): Invalid search type")
    except Exception as error:
        vrbo_logger.error(f"initiate_vrbo_search (URL/DESTINATION: {search_location_or_url}): {str(error)}")


def scrape_vrbo_data(driver, search_location_or_url, site_id, search_type):
    try:
        initiate_vrbo_search(search_type, driver, search_location_or_url)

        time.sleep(2)
        driver.refresh()

        wait = WebDriverWait(driver, 5)
        wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'HitCollection')))

        close_date_input(driver=driver)
        urls = get_room_urls(driver=driver)

        room_data_list = []
        for url in urls:
            print(f"URL: {url}")
            driver.get(url)
            wait = WebDriverWait(driver, 5)
            wait.until(ec.presence_of_element_located(
                (By.CLASS_NAME, 'photo-grid')))

            print("Extracting room data...")
            time.sleep(3)
            room_data = get_room_data(loaded_page_driver=driver)
            room_data["search_location_or_url"] = search_location_or_url
            room_data["search_type"] = search_type
            room_data["site"] = site_id
            if room_data:
                room_data_list.append(room_data)
            else:
                vrbo_logger.error(f"No data extracted for URL: {str(url)}")

            driver.back()
            wait = WebDriverWait(driver, 5)
            wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'HitCollection')))
            time.sleep(2)

        return room_data_list

    except Exception as error:
        vrbo_logger.error(f"scrape_vrbo_data (URL/DESTINATION: {search_location_or_url}): {str(error)}")
        return {}
