import configparser
import logging
import os
import datetime
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

base_path = os.path.dirname(os.path.realpath(__file__))

chrome_service = Service(ChromeDriverManager().install())
config_params = configparser.ConfigParser()
config_params.read(os.path.join(base_path, "config.ini"))

logging.basicConfig(filename=os.path.join(base_path, "logs", f"{str(datetime.datetime.now().date())}-uploader.log"),
                    filemode='w',
                    format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


def setup_logger(logger_name, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    file_name = os.path.join(base_path, "logs", logger_name, f"{str(datetime.datetime.now().date())}-{logger_name}.log")

    handler = logging.FileHandler(file_name, mode='w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


airbnb_logger = setup_logger('airbnb')
vrbo_logger = setup_logger('vrbo')
