import requests
from bs4 import BeautifulSoup

from tools import *


def get_web_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, "html.parser")

        # 移除不需要的标签
        for script in soup(["script", "style"]):
            script.extract()

        # 获取纯文本内容
        text_content = soup.get_text(separator="\n")

        # 去除多余的空行
        lines = (line.strip() for line in text_content.splitlines() if line.strip())
        clean_text_content = "\n".join(lines)

        print("URL:", url)
        print("Text Content:")
        print(clean_text_content)
    else:
        print("Failed to fetch URL:", url)


class WebVisitor:
    def __init__(self, webs):
        self.driver = init_firefox_driver()
        self.result_set = webs

    # 获取网页文字内容，不包括渲染


if __name__ == '__main__':
    get_web_text("https://english.news.cn/20230309/6fabecde80d94b56887f819e75715a93/c.html")
