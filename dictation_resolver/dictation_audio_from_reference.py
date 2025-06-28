import os
import difflib
import shutil
import whisper
from pydub import AudioSegment


def split_audio_with_whisper(title):
    # ========== 設定 ==========
    input_audio_path = f"input/audio/{title}.mp3"
    input_script_path = "input/reference.txt"
    output_dir = f"output/{title}"
    similarity_threshold = 0.5
    # 類似度しきい値
    silence_duration_ms = 500  # 無音追加：500ms
    margin_ms = 300

    # --- 出力ディレクトリ初期化 ---
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # ========== ステップ1: スクリプトの読み込み ==========
    with open(input_script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    # ピリオドで区切って文リストにする（文末空白も除去）
    script_sentences = [s.strip() for s in script_text.split("\n") if s.strip()]
    # script_sentences = re.split(r"(?<=[.?!])\s+", script_text.strip())
    # ========== ステップ2: Whisperでタイムスタンプ付き文字起こし ==========
    model = whisper.load_model("base")  # 必要に応じて small や medium に変更
    result = model.transcribe(input_audio_path, word_timestamps=False)
    segments = result['segments']

    # ========== ステップ3: 公式スクリプトとのマッチング ==========
    max_combine = 3  # 最大何個のセグメントを連結してよいか
    matched = []
    used = set()
    unmatched_lines = []

    for official in script_sentences:
        best_score = 0
        best_seg_indices = None

        for start_idx in range(len(segments)):
            if any(i in used for i in range(start_idx, min(len(segments), start_idx + max_combine))):
                continue

            for n in range(1, max_combine + 1):
                end_idx = start_idx + n
                if end_idx > len(segments):
                    break

                combo_text = " ".join(segments[i]['text'].strip() for i in range(start_idx, end_idx))
                score = difflib.SequenceMatcher(None, official.lower(), combo_text.lower()).ratio()

                if score > best_score:
                    best_score = score
                    best_seg_indices = list(range(start_idx, end_idx))

        if best_score > similarity_threshold and best_seg_indices is not None:
            used.update(best_seg_indices)
            seg_start = segments[best_seg_indices[0]]['start']
            seg_end = segments[best_seg_indices[-1]]['end']
            matched.append((official, seg_start, seg_end))
        else:
            unmatched_lines.append(official)
            matched.append((official, None, None))

    # ========== ステップ4: 音声分割＋無音追加＋スクリプト出力 ==========
    audio = AudioSegment.from_file(input_audio_path)
    silence = AudioSegment.silent(duration=silence_duration_ms)

    with open(os.path.join(output_dir, "000.script.txt"), "w", encoding="utf-8") as f_script, \
         open(os.path.join(output_dir, "000.unmatched.txt"), "w", encoding="utf-8") as f_unmatched:
        for i, (text, start_time, end_time) in enumerate(matched, 1):
            if start_time is None:
                f_unmatched.write(f"[{i:03}] {text}\n")
                continue
            start = max(0, int(start_time * 1000) - margin_ms)
            end = int(end_time * 1000) + margin_ms
            chunk = audio[start:end]
            chunk = silence + chunk
            filename = f"{i:03}.mp3"
            chunk.export(os.path.join(output_dir, filename), format="mp3")
            f_script.write(f"- [ ] {i}. {text}\n")


if __name__ == "__main__":
    title = "kaffe_drinken"
    split_audio_with_whisper(title)

