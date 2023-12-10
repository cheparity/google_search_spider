import time
from urllib.parse import quote_plus, quote

from bs4 import BeautifulSoup
from selenium.common import NoSuchWindowException
from selenium.webdriver.common.by import By

from tools import *

UA_LIST = get_data(file_path="data/user_agents.txt")
URL_LINK_XPATH = ("/html/body/div[5]/div/div[12]/div/div[2]/div[2]/div/div/div[{number}]/div/div/div["
                  "1]/div/div/span/a")
H3_LINK_XPATH = ("/html/body/div[5]/div/div[12]/div/div[2]/div[2]/div/div/div[{number}]/div/div/div["
                 "1]/div/div/span/a/h3")
# self.URL_SEARCH = "https://{domain}/search?hl={language}&q={query}&btnG=Search"
URL_SEARCH = "https://{domain}/search?hl={language}&q={query}&btnG=Search&gbv=2"


class GoogleSpider:
    def __init__(self, question):
        self.driver = init_firefox_driver()
        self.question = question
        self.logger = MyLogger(name="GoogleSpider", output_path=f"./data/log/google_spider_"
                                                                f"of_{quote(self.question)}.log")
        self.results_set = set()
        self.max_refresh_turn = 50

    def scroll_to_bottom(self, scroll_pause_time=1, max_scroll_count=20):
        scroll_count = 0

        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
        except NoSuchWindowException:
            self.logger.warning("浏览器意外关闭...")
            raise

        while scroll_count < max_scroll_count:
            try:
                self.driver.execute_script("javascript:void(0);")
            except Exception as e:
                self.logger.warning(f"检测页面状态时出错，尝试重新加载: {e}")
                self.driver.refresh()
                time.sleep(5)
                self.scroll_to_bottom()
                time.sleep(scroll_pause_time)
                raise

            try:
                self.driver.execute_script(
                    "window.scrollTo(0, document.documentElement.scrollHeight);"
                )
            except NoSuchWindowException:
                self.logger.warning("关闭小窗时，浏览器意外关闭...")
                raise

            time.sleep(scroll_pause_time)
            try:
                new_height = self.driver.execute_script(
                    "return document.documentElement.scrollHeight"
                )
            except NoSuchWindowException:
                self.logger.warning("页面向下滚动时，浏览器意外关闭...")
                raise

            if new_height == last_height:
                break

            last_height = new_height
            scroll_count += 1
            self.logger.info(f"下滑滚动第{scroll_count}次 / 最大滚动{max_scroll_count}次")

    def check_card(self):
        try:
            card = self.driver.find_element(By.CSS_SELECTOR, ".card-section")
            info = card.text
            self.logger.info(f"找到卡片，信息为：{info}")
            a = card.find_element(By.CSS_SELECTOR, "a")
            a.click()
            self.logger.debug("点击卡片链接" + a.get_attribute("href"))
            time.sleep(5)
            return True
        except Exception:  # 如果没有则return false
            return False

    def check_next_page_button(self):
        button = self.driver.find_element(By.CSS_SELECTOR, ".RVQdVd")
        if "More results" in button.text:
            self.logger.info("找到下一页按钮")
            return True
        self.logger.info("未找到下一页按钮")
        return False

    def click_next_page_button(self):
        if self.check_card():
            return False
        if self.check_next_page_button():
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".GNJvt").click()
            except Exception as e:
                self.logger.debug(f"点击下一页按钮出错: {e}")
                save_as_csv([self.driver.current_url], file_path=f"data/progress_of_{quote(self.question)}.csv")
                raise

    def get_result_from_soup(self):
        page = self.driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        all_divs = soup.find_all(name="a", attrs={"jsname": "UWckNb"})
        self.logger.info(f"解析到{len(all_divs)}个a标签")
        save_as_csv([self.driver.current_url], file_path=f"data/progress_of_{quote(self.question)}.csv")
        for a in all_divs:  # a jsname="UWckNb"
            self.logger.info("解析到一个a标签")
            try:
                url = a["href"]
                header = a.find("h3").text
                self.logger.info(f"解析到一个结果：{header}, {url}")
                yield [header, url]
            except Exception as e:
                self.logger.warning(f"解析出错: {e}")
                save_as_csv([self.driver.current_url], file_path=f"data/progress_of_{quote(self.question)}.csv")

    def scroll_and_click_next_btn(self):
        max_try = 5
        while self.max_refresh_turn > 0:  # 一直滚
            try:
                self.scroll_to_bottom(max_scroll_count=self.max_refresh_turn)
                self.click_next_page_button()
                self.max_refresh_turn -= 1
            except Exception:
                self.logger.info("元素未到位，尝试等待后重新滚动页面，进度已保存")
                save_as_csv([self.driver.current_url], file_path=f"data/progress_of_{quote(self.question)}.csv")
                if max_try <= 0:
                    self.logger.warning("尝试次数过多，放弃本轮滚动")
                    self.save_result()
                    break
                max_try -= 1
                time.sleep(5)  # 停顿5s继续滚
                continue

    def save_result(self):
        results = self.get_result_from_soup()
        result_file_path = f"data/results_of_{quote(self.question)}.csv"
        for result in results:
            if tuple(result) not in self.results_set:
                self.results_set.add(tuple(result))
                save_as_csv(result, file_path=result_file_path)  # 保存结果
        self.logger.info(f"共解析到{len(self.results_set)}个结果，已经存入文件{result_file_path}")

    def run(self):
        self.logger.info("=====start to search=====")
        url_2_search = URL_SEARCH.format(
            domain=get_random_domain(),
            language="en",
            query=quote_plus(self.question),
        )
        self.logger.info("url: " + url_2_search)
        self.driver.get(url_2_search)
        # 如果跳转到了验证页面，手动验证
        if "consent.google" in self.driver.current_url:
            self.logger.info("跳转到了验证页面，手动验证")
            input("请登录，登录成功跳转后，按回车键继续...")
            self.driver.get(url_2_search)

        # page = self.driver.page_source
        self.logger.info("=====start to catch results in page=====")
        self.scroll_and_click_next_btn()
        self.logger.info(f"滚动结束，保存进度：当前页面的url: {self.driver.current_url}")
        save_as_csv([self.driver.current_url], file_path=f"data/progress_of_{quote(self.question)}")
        self.save_result()
        self.logger.info("=====end to catch results in page=====")
        self.driver.quit()
        return self.results_set


if __name__ == '__main__':
    result_set = GoogleSpider("China modernization").run()
