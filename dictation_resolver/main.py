import configparser

from audio_downloader import download_topthema_audio
from whisper_audio_splitter import split_audio_and_generate_transcript
from subtitle_extractor import fetch_topthema_transcript


def get_top_thema_material(title_: str, url_: str):
    # 1. Top Thema の音声をダウンロード
    download_topthema_audio(title_, url_)

    # 2. Whisper を使って音声をチャンクに分割し、スクリプトと音声ファイルを保存
    split_audio_and_generate_transcript(title_)

    # 3. DW サイトから字幕スクリプトを抽出して reference.txt に保存
    fetch_topthema_transcript(url_)


if __name__ == "__main__":
    # read config
    config = configparser.ConfigParser()
    config.read('config.ini')
    title = config['TOP_THEMA']['title']
    url = config['TOP_THEMA']['url']

    get_top_thema_material(title, url)
