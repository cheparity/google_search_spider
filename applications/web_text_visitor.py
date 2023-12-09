import requests
from bs4 import BeautifulSoup

from tools import *


def get_web_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        page_content = response.content.decode('utf-8')
        soup = BeautifulSoup(page_content, "html.parser")

        # 移除不需要的标签
        for script in soup(["script", "style"]):
            script.extract()

        # 获取纯文本内容
        text_content = soup.get_text(separator="\n")

        # 去除多余的空行
        lines = (line.strip() for line in text_content.splitlines() if line.strip())
        clean_text_content = "\n".join(lines)
        return url, clean_text_content
    else:
        Exception(f"response code:{response.status_code}")


class WebVisitor:
    def __init__(self, read_from_path: str, error_web_path: str = "./data/error_webs.txt"):
        self.logger = MyLogger(output_path="./data/log/web_visitor_logger.log", name="WebVisitor")
        self.read_from = read_from_path
        self.error_webs_path = error_web_path
        self.error_webs = []

    def get_title_and_url(self):
        with open(self.read_from, 'r', encoding="utf-8") as f:
            for line in f:
                data = line.strip()
                if data == "":
                    continue
                json_data = json.loads(data)
                yield json_data["title"], json_data["url"]

    def write_web_text_in_file(self, write_to_path: str = "./data/web_text.txt"):
        with open(write_to_path, 'a', encoding="utf-8") as f:
            for title, url in self.get_title_and_url():
                self.logger.info(f"正在解析网页：{title},{url}")
                try:
                    web_text = get_web_text(url)
                    json_data = {"title": title, "url": url, "text": web_text}
                    json.dump(json_data, f, indent=None, ensure_ascii=False)
                except Exception as e:
                    error_data = {"title": title, "url": url}
                    self.error_webs.append(error_data)
                    with open(self.error_webs_path, "a", encoding="utf-8") as f_error:
                        json.dump(error_data, f_error, indent=None, ensure_ascii=False)
                    self.logger.warning(f"解析网页出错：{error_data}")
                    continue
        return self.error_webs


if __name__ == '__main__':
    web_visitor = WebVisitor(read_from_path="./data/result_after_deduplication_new2.txt")
    print("开始解析网页")
    web_visitor.write_web_text_in_file()
