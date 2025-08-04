import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import configparser


def fetch_topthema_transcript(url_: str, output_file="input/reference.txt"):
    # -- Seleniumブラウザ設定 --
    options = Options()
    options.add_argument('--headless')  # ヘッドレスモード（画面を表示しない）
    driver = webdriver.Chrome(options=options)

    script_url = url_ = url_.strip("/") + "/lm"

    driver.get(script_url)
    time.sleep(5)  # JavaScriptの読み込み待ち

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # -- スクリプト本文の抽出（クラス名などは都度確認） --
    article_div = soup.find("div", class_="richtext-content-container")

    paragraphs = article_div.find_all("p")
    script_text = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())
    script_sentences = re.split(r"(?<=[.?\n!])\s+", script_text.strip())

    with open(output_file, "w", encoding="utf-8") as f:
        for i, sentence in enumerate(script_sentences, 1):
            if sentence.strip() != '':
                f.write(f"{sentence.strip()}\n")

    driver.quit()


if __name__ == "__main__":
    # read config
    config = configparser.ConfigParser()
    config.read('config.ini')
    url = config['TOP_THEMA']['url']

    fetch_topthema_transcript(url)

