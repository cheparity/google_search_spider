import time
from urllib.parse import quote_plus

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

    def __init__(self):

        self.driver = init_firefox_driver()

        self.results_set = set()
        self.max_refresh_turn = 50

    def scroll_to_bottom(self, scroll_pause_time=1, max_scroll_count=20):
        scroll_count = 0

        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
        except NoSuchWindowException:
            print("浏览器意外关闭...")
            raise

        while scroll_count < max_scroll_count:
            try:
                self.driver.execute_script("javascript:void(0);")
            except Exception as e:
                print(f"检测页面状态时出错，尝试重新加载: {e}")
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
                print("关闭小窗时，浏览器意外关闭...")
                raise

            time.sleep(scroll_pause_time)
            try:
                new_height = self.driver.execute_script(
                    "return document.documentElement.scrollHeight"
                )
            except NoSuchWindowException:
                print("页面向下滚动时，浏览器意外关闭...")
                raise

            if new_height == last_height:
                break

            last_height = new_height
            scroll_count += 1
            print(f"下滑滚动第{scroll_count}次 / 最大滚动{max_scroll_count}次")

    def check_card(self):
        try:
            card = self.driver.find_element(By.CSS_SELECTOR, ".card-section")
            info = card.text
            print("找到卡片，信息为：", info)
            a = card.find_element(By.CSS_SELECTOR, "a")
            a.click()
            print("点击卡片链接", a.get_attribute("href"))
            time.sleep(5)
            return True
        except Exception:
            return False

    def check_next_page_button(self):
        button = self.driver.find_element(By.CSS_SELECTOR, ".RVQdVd")
        if "More results" in button.text:
            print("找到下一页按钮")
            return True
        print("未找到下一页按钮")
        return False

    def click_next_page_button(self):
        if self.check_card():
            return False
        if self.check_next_page_button():
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".GNJvt").click()
            except Exception as e:
                print(f"点击下一页按钮出错: {e}")
                raise

    def get_result_from_soup(self):
        page = self.driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        for a in soup.find_all(name="a", attrs={"jsname": "UWckNb"}):  # a jsname="UWckNb"
            print("解析到一个a标签")
            try:
                url = a["href"]
                header = a.find("h3").text
                ret = {
                    "title": header,
                    "url": url,
                }
                print("解析到一个结果", ret)
                self.results_set.add(ret)
            except Exception as e:
                print("解析出错: ", e)

    def scroll_and_scrap(self):
        while self.max_refresh_turn > 0:  # 一直滚
            try:
                self.scroll_to_bottom(max_scroll_count=self.max_refresh_turn)
                self.click_next_page_button()
                self.max_refresh_turn -= 1
            except Exception as e:
                print("出现异常，尝试重新加载页面。加载完成后会继续执行", e)
                self.max_refresh_turn -= 1
                time.sleep(5)  # 停顿5s继续滚
                continue

    def run(self, question):
        print("=====start to search=====")
        question = quote_plus(question)
        url_2_search = URL_SEARCH.format(
            domain=get_random_domain(),
            language="en",
            query=question,
        )
        print("url: ", url_2_search)
        self.driver.get(url_2_search)
        # 如果跳转到了验证页面，手动验证
        if "consent.google" in self.driver.current_url:
            print("跳转到了验证页面，手动验证")
            input("请登录，登录成功跳转后，按回车键继续...")
            self.driver.get(url_2_search)

        # page = self.driver.page_source
        print("=====start to catch results in page=====")
        self.scroll_and_scrap()
        print("解析结束，共解析到", len(self.results_set), "个结果")
        with open(f"data/result_of_{question}.txt", "a", encoding="utf-8") as output_result_file:
            for result in self.results_set:
                output_result_file.write(json.dumps(result, ensure_ascii=False) + "\n")
        print("=====end to catch results in page=====")
        return self.results_set


if __name__ == '__main__':
    result_set = GoogleSpider().run("China modernization")
