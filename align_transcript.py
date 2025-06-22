def load_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def split_reference_into_sentences(reference_text):
    import re
    sentences = re.split(r'(?<=[.!?])\s+', reference_text)
    return [s.strip() for s in sentences if s.strip()]

def main():
    whisper_lines = load_lines("whisper_transcript.txt")

    with open("reference.txt", 'r', encoding='utf-8') as f:
        reference_raw = f.read()

    reference_sentences = split_reference_into_sentences(reference_raw)

    # 長さのチェック
    if len(reference_sentences) < len(whisper_lines):
        print(f"⚠️ Warning: Whisper lines ({len(whisper_lines)}) are more than reference sentences ({len(reference_sentences)}). Truncating whisper lines.")
        whisper_lines = whisper_lines[:len(reference_sentences)]
    elif len(reference_sentences) > len(whisper_lines):
        print(f"ℹ️ Info: Reference sentences ({len(reference_sentences)}) are more than whisper lines ({len(whisper_lines)}). Extra references will be ignored.")

    # 置き換え
    corrected_lines = reference_sentences[:len(whisper_lines)]

    # 出力
    with open("corrected_transcript.txt", 'w', encoding='utf-8') as f:
        for line in corrected_lines:
            f.write(line + "\n")

    print("✅ 書き換え完了：corrected_transcript.txt に出力しました。")

if __name__ == "__main__":
    main()
