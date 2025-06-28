import os
import shutil
import whisper
from pydub import AudioSegment
import nltk
from nltk.tokenize import sent_tokenize


def split_audio_and_generate_transcript(title):
    nltk.download("punkt")
    # --- 設定 ---
    # 入力ファイル
    input_file = f"input/audio/{title}.mp3"
    output_dir = f"output/{title}"
    script_file = "script.txt"
    silence_duration = 500  # 無音（ms）

    # --- 出力ディレクトリ初期化 ---
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # --- モデル読み込み & 文字起こし ---
    model = whisper.load_model("base")
    result = model.transcribe(input_file, word_timestamps=True)

    # --- 音声読み込み ---
    audio = AudioSegment.from_file(input_file)
    silence = AudioSegment.silent(duration=silence_duration)

    # --- 全単語と全文テキストの準備 ---
    words = []
    full_text = ""

    for seg in result["segments"]:
        for w in seg["words"]:
            words.append(w)
            full_text += w["word"]

    # --- 文単位で分割 ---
    sentences = sent_tokenize(full_text, language="german")

    # --- 1文ずつ処理して、単語タイムスタンプとマッチング ---
    with open(os.path.join(output_dir, script_file), "w", encoding="utf-8") as f_script:
        word_index = 0
        for i, sentence in enumerate(sentences):
            # 文の先頭と末尾を探す
            matched_words = []
            while word_index < len(words) and len("".join([w["word"] for w in matched_words])) < len(sentence):
                matched_words.append(words[word_index])
                word_index += 1

            # 音声切り出しのための時間取得
            if not matched_words:
                continue
            start_ms = int(matched_words[0]["start"] * 1000)
            end_ms = int(matched_words[-1]["end"] * 1000) + 300

            # 音声切り出し + 無音追加
            clip = silence + audio[start_ms:end_ms]
            audio_filename = f"sentence_{i+1:03d}.mp3"
            clip.export(os.path.join(output_dir, audio_filename), format="mp3")

            # スクリプト出力
            f_script.write(f"{sentence.strip()}\n")


if __name__ == "__main__":
    title = "kaffe_drinken"
    split_audio_and_generate_transcript(title)