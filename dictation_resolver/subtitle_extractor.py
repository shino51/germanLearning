import requests
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def fetch_tagesschau_transcript(tagesschau_untertitel_xml_url, output_file="input/reference.txt"):
    # tagesschau はEBU を使っているので、そこのuntertitel.xml から全スクリプトを抽出する
    # 字幕XMLを取得
    response = requests.get(tagesschau_untertitel_xml_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    # 名前空間の定義
    ns = {"tt": "http://www.w3.org/ns/ttml"}

    # 全字幕テキストを連結して1つの文章に
    paragraphs = root.findall(".//tt:body//tt:div//tt:p", ns)
    all_text = ""
    for p in paragraphs:
        text = " ".join(p.itertext())  # 改行・複数スペースをまとめる
        cleaned = re.sub(r"\s+", " ", text).strip()
        all_text += cleaned + " "

    # ピリオド・疑問符・感嘆符で文単位に分割
    sentences = re.split(r"(?<=[.?!])\s+", all_text.strip())

    # 出力
    with open(output_file, "w", encoding="utf-8") as f:
        for i, sentence in enumerate(sentences, 1):
            f.write(f"{sentence.strip()} \n")

    print(f"✅ クリーンなスクリプトを抽出しました: {output_file}")


def fetch_topthema_transcript(url, output_file="input/reference.txt"):
    # -- Seleniumブラウザ設定 --
    options = Options()
    options.add_argument('--headless')  # ヘッドレスモード（画面を表示しない）
    driver = webdriver.Chrome(options=options)

    driver.get(url)
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
    # ▼ 使用例：取得済みの字幕XMLのURLを指定
    # tagesschau_untertitel_xml_url = "https://www.tagesschau.de/multimedia/sendung/tagesschau_20_uhr/untertitel-74704.xml"
    # fetch_tagesschau_transcript(tagesschau_untertitel_xml_url)

    url = "https://learngerman.dw.com/de/kaffee-trinken-f%C3%BCr-die-gesundheit/l-72970964/lm"
    fetch_topthema_transcript(url)

