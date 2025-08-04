# 📚 Dictation Resolver

このプロジェクトは、ドイツ語学習者向けに **ディクテーション（書き取り）やシャドーイング** のための音声・スクリプト教材を自動生成するツールです。特に `Tagesschau` や `DW Top Thema` などのニュース素材を対象とし、以下の3つの主要機能を提供します：

---
## 1. DW Top Thema 音声ダウンローダー（`audio_downloader.py`）

### 🔧 スクリプト
[audio_downloader.py](audio_downloader.py)

### ✅ 機能
- Top Thema ページから JavaScript を実行して音声ファイルリンクを取得（Selenium 使用）
- 音声（MP3）を `input/audio/` に保存（`config.ini` で指定したタイトルで保存）

---

### 📁 入力設定

以下のような構成の `config.ini` を用意してください：

```ini
[TOP_THEMA]
url = https://learngerman.dw.com/de/handy-aus-offline-sein-ist-im-trend/l-72709529
title = handy-aus-offline-sein
```

### 📂 出力例
- input/audio/handy-aus-offline-sein.mp3
　⇨ ダウンロードされた音声ファイル

### 💡 備考
Selenium を使って JavaScript 実行後の DOM から音声リンクを取得します。

## 📌 2. Whisper 音声スプリッター（音声からスクリプトと区切り音声を生成）

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
