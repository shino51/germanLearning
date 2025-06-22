import os
from pydub import AudioSegment
import whisper

# ---------- 設定 ----------
title = "einfacher_nach"
INPUT_AUDIO = f"audio/{title}.mp3"
INPUT_SCRIPT = "input/tagesschau_script.txt"
OUTPUT_DIR = f"output/{title}"
silence_duration = 500  # 無音（ms）
MODEL_SIZE = "medium"  # whisper model size

# ---------- スクリプト読み込み ----------
def load_script(script_path):
    with open(script_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

# ---------- Whisper でタイムスタンプ取得 ----------
def transcribe_with_whisper(audio_path):
    model = whisper.load_model(MODEL_SIZE)
    result = model.transcribe(audio_path, word_timestamps=False)
    return result["segments"]

# ---------- 音声を分割・保存 ----------
def split_audio_by_segments(audio_path, segments, script_lines, output_dir):
    audio = AudioSegment.from_file(audio_path)
    silence = AudioSegment.silent(duration=silence_duration)
    os.makedirs(output_dir, exist_ok=True)

    final_script_lines = []

    for i, (seg, text) in enumerate(zip(segments, script_lines), 1):
        start_ms = int(seg["start"] * 1000)
        end_ms = int(seg["end"] * 1000)

        # 少し余裕を持たせる（切れ防止）
        padding = 100  # ms
        start_ms = max(start_ms - padding, 0)
        end_ms = min(end_ms + padding, len(audio))

        # 音声切り出し + 無音追加
        segment_audio = silence + audio[start_ms:end_ms]
        filename = f"{i:03d}.mp3"
        segment_audio.export(os.path.join(output_dir, filename), format="mp3")

        final_script_lines.append(f"- [ ] {i}. {text}")

    with open(os.path.join(output_dir, "000script.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(final_script_lines))

# ---------- 実行 ----------
def main():
    print("📄 スクリプト読み込み中...")
    script_lines = load_script(INPUT_SCRIPT)

    print("🧠 Whisperで音声処理中...")
    segments = transcribe_with_whisper(INPUT_AUDIO)

    if len(script_lines) != len(segments):
        print(f"⚠️ script.txt（{len(script_lines)}行）とWhisperセグメント（{len(segments)}件）が一致していません。最小数に揃えます。")

    min_len = min(len(script_lines), len(segments))
    segments = segments[:min_len]
    script_lines = script_lines[:min_len]

    print("🎧 音声を分割中...")
    split_audio_by_segments(INPUT_AUDIO, segments, script_lines, OUTPUT_DIR)

    print("✅ 完了！output フォルダに音声と script.txt を保存しました。")

if __name__ == "__main__":
    main()
