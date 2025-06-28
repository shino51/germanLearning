# 📚 Dictation Resolver

このプロジェクトは、ドイツ語学習者向けに **ディクテーション（書き取り）やシャドーイング** のための音声・スクリプト教材を自動生成するツールです。特に `Tagesschau` や `DW Top Thema` などのニュース素材を対象とし、以下の3つの主要機能を提供します：

---

## 📌 1. Whisper 音声スプリッター（音声からスクリプトと区切り音声を生成）

### 🔧 スクリプト
[whisper_audio_splitter.py](whisper_audio_splitter.py)

### ✅ 機能
- Whisper を使って `.mp3` 音声から自動で文字起こしを行う
- 音声を文ごとに区切って出力（`.mp3`）
- 各文のスクリプトも `script.txt` に保存
- 文の先頭に無音（500ms）を追加可能

### 🗂️ 入力
- `input/{title}/audio.mp3`

### 📁 出力
- `output/{title}/001.mp3`, `002.mp3`, ...
- `output/{title}/script.txt`


### 📌 注意点
Whisper の文字起こしには正確でない箇所が含まれているので、[字幕ファイルの抽出](#3-字幕ファイル抽出)を同時に行い、出力されたスクリプトと公式のスクリプトを比べて直しておくべき

---

## 📌 2. 公式スクリプトベースの音声切り出し（字幕と音声をマッチ）

### 🔧 スクリプト
[dictation_audio_from_reference.py](dictation_audio_from_reference.py)

### ✅ 機能
- Whisper でタイムスタンプを取得
- 公式のスクリプト (`script.txt`) とマッチング
- 類似度が低い行は `unmatched.txt` に記録
- マッチした文に対応する音声のみを切り出して保存
- 切り出した音声の先頭に 0.5 秒の無音を追加

### 🗂️ 入力
ダウンロードする際、タイトルをつける
- `input/audio/{title}.mp3`
- `input/reference.txt`（1文1行、すでに整形済み）

成形済みのreferenceを取得するためには、先に [字幕ファイルの抽出](#3-字幕ファイル抽出)をやっておくべき

### 📁 出力
- `output/{title}/001.mp3`, ...
- `output/{title}/000.script.txt`
- `output/{title}/000.unmatched.txt`

---

## 3. 字幕ファイルの抽出
DW Top Thema / Tagesschau などの字幕ファイルを抽出

### 🔧 スクリプト
[subtitle_extractor.py](subtitle_extractor.py)

### ✅ 機能
#### fetch_tagesschau_transcript
- Tagesschau の `.xml` 形式の字幕ファイルからスクリプト抽出
- 空白行や不自然な改行を正規化
- 文単位にピリオドで改行

#### fetch_topthema_transcript
- DW Top Thema のManuscriptのページからスクリプト抽出
- 空白行や不自然な改行を正規化

---

## 使用方法

1. 必要な Python パッケージをインストール：

```bash
pip install -r requirements.txt
