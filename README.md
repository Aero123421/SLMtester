# Local LLM Benchmark Tool

LM StudioのローカルAPIサーバーに対して、品質と速度（TTFT/E2E）を計測するベンチマークツールです。

## 前提条件

*   Python 3.8+
*   LM Studio が起動しており、ローカルサーバーが有効になっていること（デフォルト: `http://localhost:1234/v1`）

## セットアップ

1.  依存ライブラリのインストール:
    ```bash
    pip install -r bench/requirements.txt -r bench/requirements-dev.txt
    ```
2.  テスト用アセットの生成（初回のみ）:
    ```bash
    python setup_assets.py
    ```
    (プロジェクトルートで実行してください)

## 使い方 (Web UI)

推奨される利用方法です。リアルタイムでログと結果を確認できます。

```bash
uvicorn bench.server:app --reload
```
ブラウザで `http://localhost:8000` にアクセスしてください。

## 使い方 (CLI)

```bash
python -m bench.main --suite bench/suite.yaml [オプション]
```

### 主なオプション

*   `--suite`: テストスイート定義ファイル（必須）
*   `--models`: 対象モデルの正規表現（例: `".*qwen.*"`, `".*"`）
*   `--base-url`: APIのエンドポイント（デフォルト: `http://localhost:1234/v1`）
*   `--runs`: 各ケースの計測回数
*   `--warmup`: 計測前のウォームアップ回数
*   `--out`: 結果出力ディレクトリ

### 実行例

```bash
# Web UI起動 (ルートディレクトリで実行)
uvicorn bench.server:app

# CLIで全モデルを実行
python -m bench.main --suite bench/suite.yaml --models ".*"
```

## 出力

実行後、`bench/out/` ディレクトリに以下が生成されます:

*   `results_YYYYMMDD_HHMMSS.jsonl`: 生ログ（JSON Lines形式）
*   `report_YYYYMMDD_HHMMSS.html`: HTML形式のレポート（CLI実行時のみ生成、Web UIは画面上で確認）

---

## ディレクトリ構造

```
bench/
├── suite.yaml          # メインスイート（カテゴリファイルをinclude）
├── suite_auto.yaml     # 自動評価特化（厳密出力・大量）スイート
├── suites/             # カテゴリ別テストファイル
│   ├── 01_translation.yaml   # 翻訳能力
│   ├── 02_reading.yaml       # 読解・推論
│   ├── 03_logic.yaml         # 論理的推論
│   ├── 04_generation.yaml    # 表現力・生成
│   ├── 05_instruction.yaml   # 指示追従
│   ├── 06_knowledge.yaml     # 知識・常識
│   ├── 07_math.yaml          # 計算・数学
│   ├── 08_code.yaml          # コード理解
│   └── 09_vision.yaml        # VLMテスト
├── suites_auto/        # 自動評価特化スイート（厳密出力・大量）
├── images/             # テスト用画像
├── main.py             # ベンチマークエンジン
├── server.py           # Web UIサーバー
└── out/                # 結果出力先
```

## テストカテゴリ一覧

| ID | 名前 | 説明 | テスト数 |
|----|------|------|----------|
| `translation` | 翻訳能力 | 英日・日英翻訳、慣用表現、専門用語 | 3 |
| `reading` | 読解・推論 | 情報抽出、自然言語推論（NLI）、感情分析 | 4 |
| `logic` | 論理的推論 | 対偶、三段論法、数列パターン | 3 |
| `generation` | 表現力・生成 | 敬語変換、制約付き要約、定義説明 | 3 |
| `instruction` | 指示追従 | JSON出力、番号付きリスト、文字数制限 | 3 |
| `knowledge` | 知識・常識 | 地理、科学、常識推論 | 3 |
| `math` | 計算・数学 | 四則演算、割合計算、文章題 | 3 |
| `code` | コード理解 | 出力予測、エラー種類特定 | 2 |
| `vision` | VLMテスト | OCR、物体カウント（Vision対応モデルのみ） | 2 |
| `format` | 形式順守 | JSON/単一ラベル/固定行などの厳密出力 | 4 |
| `extraction` | 抽出 | 文中情報をJSONへ抽出 | 4 |
| `classification` | 分類 | ラベル分類（単一語） | 4 |
| `reasoning` | 推論 | 条件推論/順序/制約充足 | 4 |
| `summarization` | 要約・整形 | 構造付き要約/アクション抽出 | 3 |
| `code_slm` | コード（SLM） | 短いコード理解/変換 | 4 |
| `math_slm` | 計算（SLM） | 小数/単位変換を含む計算 | 4 |
| `calibration` | 不確実性・校正 | 情報不足時に推測しない | 3 |
| `safety` | 安全性 | 危険/個人情報依頼の拒否 | 2 |

**合計: 26テストケース（従来スイート: `bench/suite.yaml`）**

**合計: 34テストケース（SLM最適化スイート: `bench/suite_slm.yaml`）**

**合計: 50テストケース（自動評価特化スイート: `bench/suite_auto.yaml` / variants: 1141）**

---

## テストケースの構造

各テストケースには以下のフィールドがあります：

```yaml
- id: trans_en2ja_idiom          # 一意のID（システム用）
  name: 英日翻訳（慣用句）         # 人間向けのテスト名
  description: 英語の慣用表現を...  # テストの説明
  modality: text                  # text または vision
  weight: 4                       # 重み（5が最高難度）
  request: ...                    # リクエスト定義
  eval: ...                       # 評価ルール
```

### CLI出力例

```
[model-name] [翻訳能力] 英日翻訳（慣用句） #0: ○ (TTFT: 123.4ms, E2E: 567.8ms)
[model-name] [読解・推論] NLI（含意判定） #0: × (TTFT: 89.2ms, E2E: 234.5ms)
```

### HTMLレポート

生成されるレポートには以下が含まれます：
- 📊 カテゴリ別サマリカード（正解率、テスト数、平均TTFT）
- 📋 モデル別詳細テーブル（カテゴリ、テスト名＋説明、正解率）
- 📝 全結果詳細（レスポンスプレビュー付き）

---

## テストの追加・カスタマイズ

新しいテストを追加するには：

1. 適切なカテゴリファイル（`suites/XX_category.yaml`）を編集
2. または新しいカテゴリファイルを作成し、`suite.yaml`のincludesに追加

```yaml
# suites/10_custom.yaml の例
category:
  id: custom
  name: カスタムテスト
  description: 独自のテストケース

cases:
  - id: custom_test_1
    name: カスタムテスト1
    description: このテストは...
    modality: text
    weight: 3
    request:
      messages:
        - role: user
          content: "質問..."
    eval:
      type: contains_all
      keywords: ["期待キーワード"]
```
