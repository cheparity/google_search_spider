import time
from urllib.parse import quote_plus, quote

from bs4 import BeautifulSoup
from selenium.common import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tools import *

UA_LIST = get_data(file_path="meta/user_agents.txt")
URL_LINK_XPATH = ("/html/body/div[5]/div/div[12]/div/div[2]/div[2]/div/div/div[{number}]/div/div/div["
                  "1]/div/div/span/a")
H3_LINK_XPATH = ("/html/body/div[5]/div/div[12]/div/div[2]/div[2]/div/div/div[{number}]/div/div/div["
                 "1]/div/div/span/a/h3")
# self.URL_SEARCH = "https://{domain}/search?hl={language}&q={query}&btnG=Search"
URL_SEARCH = "https://{domain}/search?hl={language}&q={query}&btnG=Search&gbv=2"


class GoogleSpider:
    def __init__(self, question):
        # todo Please replace the browser you want to use
        # self.driver = init_chrome_driver()
        self.driver = init_firefox_driver()
        self.question = question
        self.logger = MyLogger(name="GoogleSpider", output_path=f"./data/log/google_spider_"
                                                                f"of_{quote(self.question)}.log")
        self.results_set = set()
        self.max_refresh_turn = 1000

    def scroll_to_bottom(self, scroll_pause_time=1, max_scroll_count=20):
        scroll_count = 0
        time.sleep(scroll_pause_time)

        try:
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight")
        except NoSuchWindowException:
            self.logger.warning("Browser closes unexpectedly...")
            raise

        while scroll_count < max_scroll_count:
            try:
                self.driver.execute_script("javascript:void(0);")
            except Exception as e:
                self.logger.warning(
                    f"An error occurred while checking the page status, try reloading:{e}")
                self.driver.refresh()
                time.sleep(5)
                self.scroll_to_bottom()
                raise

            try:
                self.driver.execute_script(
                    "window.scrollTo(0, document.documentElement.scrollHeight);"
                )
            except NoSuchWindowException:
                self.logger.warning(
                    "Browser closes unexpectedly when closing the window...")
                raise

            time.sleep(scroll_pause_time)
            try:
                new_height = self.driver.execute_script(
                    "return document.documentElement.scrollHeight"
                )
            except NoSuchWindowException:
                self.logger.warning(
                    "Browser closes unexpectedly when scroll down the page...")
                raise

            if new_height == last_height:
                break

            last_height = new_height
            scroll_count += 1
            self.logger.info(
                f"Scroll down {scroll_count} times / Maximum scroll {max_scroll_count} times")

    def check_card(self):
        try:
            card = self.driver.find_element(By.CSS_SELECTOR, ".card-section")
            info = card.text
            self.logger.info(f"Find card: {info}")
            a = card.find_element(By.CSS_SELECTOR, "a")
            a.click()
            self.logger.debug("Click the card's url" + a.get_attribute("href"))
            time.sleep(5)
            return True
        except Exception:
            return False

    def check_next_page_button(self):
        button = self.driver.find_element(By.CSS_SELECTOR, ".RVQdVd")
        if "More results" in button.text:
            self.logger.info("Found next-page button")
            return True
        self.logger.info("Not found next-page button")
        return False

    def click_next_page_button(self):
        if self.check_card():
            return False
        if self.check_next_page_button():
            try:
                wait = WebDriverWait(self.driver, 10)
                element = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".GNJvt")))
                element.click()
                # self.driver.find_element(By.CSS_SELECTOR, ".GNJvt").click()
            except Exception as e:
                self.logger.debug(
                    f"Error when clicking the next-page button: {e}")
                save_as_csv([self.driver.current_url],
                            file_path=f"data/progress_of_{quote(self.question)}.csv")
                raise

    def get_result_from_soup(self):
        page = self.driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        all_divs = soup.find_all(name="a", attrs={"jsname": "UWckNb"})
        self.logger.info(f"Got {len(all_divs)} a-divs")
        save_as_csv([self.driver.current_url],
                    file_path=f"data/progress_of_{quote(self.question)}.csv")
        for a in all_divs:  # a jsname="UWckNb"
            self.logger.info("Got one a-div")
            try:
                url = a["href"]
                header = a.find("h3").text
                self.logger.info(f"Got one result{header}, {url}")
                yield [header, url]
            except Exception as e:
                self.logger.warning(f"Error occured when parsing divs: {e}")
                save_as_csv([self.driver.current_url],
                            file_path=f"data/progress_of_{quote(self.question)}.csv")

    def scroll_and_click_next_btn(self):
        max_try = 10
        while self.max_refresh_turn > 0:  # Continue to scroll down until the maximum number of scrolls is reached
            try:
                self.scroll_to_bottom(max_scroll_count=self.max_refresh_turn)
                self.click_next_page_button()
                self.max_refresh_turn -= 1
            except Exception as e:
                self.logger.info(
                    f"The element is not in place. Try to wait and re-scroll the page. The progress has been saved. try = {max_try}")
                self.logger.warning(f" exception: {e}")
                save_as_csv([self.driver.current_url],
                            file_path=f"data/progress_of_{quote(self.question)}.csv")
                if max_try <= 0:
                    self.logger.warning(
                        "Too many attempts, give up this round of scrolling")
                    self.save_result()
                    break
                max_try -= 1
                time.sleep(3)
                continue

    def save_result(self):
        results = self.get_result_from_soup()
        result_file_path = f"data/results_of_{quote(self.question)}.csv"
        for result in results:
            if tuple(result) not in self.results_set:
                self.results_set.add(tuple(result))
                save_as_csv(result, file_path=result_file_path)  # save result
        self.logger.info(
            f"A total of {len(self.results_set)} results have been parsed and have been stored in the file {result_file_path}")

    def run(self):
        self.logger.info("=====start to search=====")
        url_2_search = URL_SEARCH.format(
            domain=get_random_domain(),
            language="en",
            query=quote_plus(self.question),
        )
        self.logger.info("url: " + url_2_search)
        self.driver.get(url_2_search)
        # if jumped to the verification page, manually verify
        if "consent.google" in self.driver.current_url:
            self.logger.info(
                "Jumped to the verification page, manually verify please")
            input("Please login and press Enter to continue.")
            self.driver.get(url_2_search)

        # page = self.driver.page_source
        self.logger.info("=====start to catch results in page=====")
        self.scroll_and_click_next_btn()
        self.logger.info(
            f"The scroll ends and the progress is saved: URL of the current page: {self.driver.current_url}")
        save_as_csv([self.driver.current_url],
                    file_path=f"data/progress_of_{quote(self.question)}.csv")
        self.save_result()
        self.logger.info("=====end to catch results in page=====")
        self.driver.quit()
        return self.results_set


if __name__ == '__main__':
    # todo Please replace the question you want to search
    GoogleSpider(question="The Question you want to search").run()
