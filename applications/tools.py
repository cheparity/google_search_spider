import json
import os
import pickle
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def init_firefox_driver():
    options = FirefoxOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--incognito")
    options.add_argument(f"--user-data-dir=./temp")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    return webdriver.Firefox(options=options)


def get_random_user_agent(ua_list):
    return random.choice(ua_list)


def get_random_domain():
    domain_list = get_data("data/all_domain.txt")
    BLACK_DOMAIN = ["www.google.gf", "www.google.io", "www.google.com.lc"]
    domain = random.choice(domain_list)
    if domain in BLACK_DOMAIN:
        get_random_domain()
    else:
        return domain


def get_data(file_path):
    """Read data from file and output data in list format

    Args:
        file_path ([str]): file path
    """
    text_list = []
    with open(file_path, encoding="utf-8") as fp:
        for line in fp:
            line = line.replace("\n", "").strip()
            if line:
                text_list.append(line)
    return text_list


def write_error_log(message, file_path="./data/log/error.txt"):
    with open(file_path, "a") as file:
        file.write(message + "\n")


def save_cookies(driver, cookies_file_path):
    with open(cookies_file_path, "wb") as f:  # pickle must use "wb" and "rb"
        pickle.dump(driver.get_cookies(), f)


def load_cookies(driver, cookies_file_path):
    if os.path.exists(cookies_file_path):
        with open(cookies_file_path, "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        return True
    return False


def manual_login(driver, cookies_file):
    input("请登录，登录成功跳转后，按回车键继续...")
    save_cookies(driver, cookies_file)  # save cookies
    print("程序正在继续运行")


def get_firefox_driver(options=None):
    options = get_firefox_options() if None else options
    driver = webdriver.Firefox(options=options)
    return driver


def get_firefox_options(temp_dir="./temp"):
    options = FirefoxOptions()
    get_options(options, temp_dir)
    return options


def get_options(options, temp_dir="./temp"):
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--incognito")
    options.add_argument(f"--user-data-dir={temp_dir}")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    return options


def get_chrome_options(temp_dir="./temp"):
    chrome_options = ChromeOptions()
    # 将Chrome的缓存目录设置为刚刚创建的临时目录
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--mute-audio")
    # 开启无头模式，禁用视频、音频、图片加载，开启无痕模式，减少内存占用
    chrome_options.add_argument("--headless")  # 开启无头模式以节省内存占用，较低版本的浏览器可能不支持这一功能
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )
    chrome_options.add_argument("--incognito")
    # 禁用GPU加速，避免浏览器崩溃
    chrome_options.add_argument("--disable-gpu")


def get_progress(init_progress_json, progress_path="./data/log/progress.txt"):
    if os.path.exists(progress_path):
        with open(progress_path, "r") as file:
            progress = json.load(file)
        return progress
    else:
        progress = init_progress_json  # must be json
