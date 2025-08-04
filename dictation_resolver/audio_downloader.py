import os
import time
import configparser
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def download_topthema_audio(title_: str, url_: str, output_folder="input/audio"):
    # -- Seleniumの設定 --
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        # leページにアクセス
        le_url = url_.strip("/") + "/le"
        driver.get(le_url)
        time.sleep(5)  # JSの読み込み待機

        # <a href="...mp3"> を探す
        links = driver.find_elements(By.TAG_NAME, "a")
        mp3_links = [a.get_attribute("href") for a in links if a.get_attribute("href") and a.get_attribute("href").endswith(".mp3")]

        if not mp3_links:
            raise ValueError("MP3 リンクが見つかりませんでした。")

        audio_url = mp3_links[0]  # 最初のmp3リンクを使用

        # ファイル名として使えない文字を除去
        safe_title = "".join(c for c in title_ if c.isalnum() or c in " _-").rstrip()
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, f"{safe_title}.mp3")

        # 音声をダウンロード
        print(f"🎧 ダウンロード中: {audio_url}")
        response = requests.get(audio_url)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ 保存完了: {output_path}")

    except Exception as e:
        print(f"⚠️ エラー: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    # read config
    config = configparser.ConfigParser()
    config.read('config.ini')
    title = config['TOP_THEMA']['title']
    url = config['TOP_THEMA']['url']

    download_topthema_audio(title, url)
