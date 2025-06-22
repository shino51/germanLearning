import requests
import xml.etree.ElementTree as ET
import re

def extract_clean_sentences_from_ebu_tt(xml_url, output_file="input/reference.txt"):
    # 字幕XMLを取得
    response = requests.get(xml_url)
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
            f.write(f"{sentence.strip()} ")

    print(f"✅ クリーンなスクリプトを抽出しました: {output_file}")

# ▼ 使用例：取得済みの字幕XMLのURLを指定
xml_url = "https://www.tagesschau.de/multimedia/sendung/tagesschau_20_uhr/untertitel-74704.xml"
extract_clean_sentences_from_ebu_tt(xml_url)
