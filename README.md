# foreign_crime_stats

日本における検挙人員数、外国人区分別人口、入出国者数、不法残留者数などの統計データを整形・統合し、1万人あたり検挙人員数や対日本人倍率、年齢調整後の倍率を算出するための分析プロジェクトです。

## 目的

このプロジェクトでは、複数の公的統計を共通の形式に整え、以下の指標を作成します。

- 区分別・在留資格別・罪種別の検挙人員数
- 区分別・在留資格別・年代別の人口
- 1万人あたり検挙人員数
- 日本人を基準にした検挙人員倍率
- 年齢構成を調整した対日本人倍率

主な比較区分は以下です。

- 日本人
- 外国人
    - 来日外国人
    - 永住者等

## ディレクトリ構成

```text
foreign_crime_stats/
├── data/
│   ├── 00_raw/            # 元データ
│   │   └── 999_reseach/   # 06_research系で使う raw Excel / PDF / URL
│   ├── 01_tidy/           # 個別統計を整形したデータ
│   ├── 02_standardized/   # 表記ゆれ・カテゴリを名寄せしたデータ
│   ├── 03_estimated/      # 推計・補正後データ
│   ├── 04_integrated/     # 検挙人員・人口の統合データ
│   ├── 05_analytics/      # 分析用の最終出力
│   ├── 06_research/       # テーマ別の研究用出力（現行）
│   └── 99_work/           # 中間確認・補助データ
├── scripts/
│   ├── 01_tidy/           # 元データの整形
│   ├── 02_standardize/    # 名寄せ・標準化
│   ├── 03_estimate/       # 不足区分の推計・補正
│   ├── 04_integrated/     # 検挙人員・人口の統合
│   ├── 05_analytics/      # 分析指標の作成
│   ├── 06_research/       # テーマ別の研究用スクリプト（現行）
│   ├── 99_work/           # 補助処理
│   └── 999_calculation_check/ # 数値チェック
└── notebooks/             # レポート・確認用ノートブック
```

## 06_research の構成

`data/06_research/` と `scripts/06_research/` は、テーマごとに対応する構造へ整理しています。

```text
data/06_research/
├── age_adjustment/
├── dispatch_worker_estimation/
├── hate_speech/
├── japanese_ability/
├── japanese_ability_wage/
├── japanese_spouse/
├── resident_nationality/
├── resident_philippines_gender_age/
├── school_attendance/
└── simulation/

scripts/06_research/
├── age_adjustment/
├── dispatch_worker_estimation/
├── hate_speech/
├── japanese_ability/
├── japanese_ability_wage/
├── japanese_spouse/
├── non_visitor_nationality/
├── permanent_resident/
├── report_supplemental/
├── resident_nationality/
├── resident_philippines_gender_age/
├── school_attendance/
└── simulation/
```

各テーマの基本構成は次のとおりです。

```text
data/06_research/<theme>/
├── 01_tidy/              # 研究テーマ用に整形したCSV
├── 02_intermediate/      # 推計途中のCSV（必要なテーマのみ）
└── 03_output/
    └── png/              # 最終図
```

補足:

- `scripts/06_research/` に研究用スクリプトを集約しています。
- `00_raw/999_reseach/` には、`06_research` 系テーマで参照する raw ファイルを集約しています。

## データ処理の流れ

### 1. 元データの整形

`scripts/01_tidy/` で、統計ごとの元データを扱いやすい縦持ち形式に整形します。

対象データの例:

- 日本全体の検挙人員数
- 外国人全体の検挙人員数
- 来日外国人の検挙人員数
- 在留資格別の検挙人員数
- 在留資格別人口
- 日本人人口
- 出国者数
- 入国者数
- 不法残留者数

出力先:

```text
data/01_tidy/
```

### 2. 名寄せ・標準化

`scripts/02_standardize/standardize.py` で、罪種、年代、在留資格などの表記を統一します。

出力先:

```text
data/02_standardized/
```

### 3. 推計・補正

`scripts/03_estimate/` で、分析に必要な区分を作成します。

主な処理:

- 来日外国人以外の外国人検挙人員数の推計
- 日本人検挙人員数の推計
- 在留資格別人口の年齢不詳処理
- 日本人人口の人数換算
- 入国者数の年代別・年換算人口の作成
- 不法残留者の在留資格別・年代別推計

出力先:

```text
data/03_estimated/
```

### 4. 統合データの作成

`scripts/04_integrated/` で、検挙人員データと人口データをそれぞれ統合します。

主な出力:

```text
data/04_integrated/09_検挙人員数_統合.csv
data/04_integrated/15_人口_統合.csv
```

統合後の主な列:

検挙人員データ:

- 年
- 区分00
- 区分01
- 在留資格
- 罪種00
- 罪種01
- 検挙人員

人口データ:

- 年
- 区分00
- 区分01
- 在留資格
- 年代
- 人数

### 5. 分析指標の作成

`scripts/05_analytics/` で、分析用の指標を作成します。

主な出力:

```text
data/05_analytics/20_1万人あたり検挙人員数及び対日本人倍率.csv
data/05_analytics/20_1万人あたり検挙人員数及び対日本人倍率_クロス集計.xlsx
data/05_analytics/33_対推定検挙人員及び年齢調整後対日本人倍率.csv
data/05_analytics/33_対推定検挙人員及び年齢調整後対日本人倍率_クロス集計.xlsx
```

作成される主な指標:

- `検挙人員数_1万人あたり`
- `日本人_検挙人員数_1万人あたり`
- `対日本人倍率`
- `推定検挙人員`
- `対推定値倍率`
- `日本人_対推定値倍率`
- `対日本人倍率_年齢調整後`

### 6. 研究用出力の作成

`scripts/06_research/` では、レポートや補足分析で使う図表をテーマ別に出力します。

主なテーマ:

- `age_adjustment`
- `dispatch_worker_estimation`
- `japanese_spouse`
- `resident_nationality`
- `japanese_ability`
- `japanese_ability_wage`
- `hate_speech`
- `school_attendance`
- `simulation`

出力先:

```text
data/06_research/
```

## 実行順

基本的には以下の順に実行します。

```powershell
# 1. 元データ整形
python scripts/01_tidy/01_total_arrests_tidy.py
python scripts/01_tidy/02_foreign_arrests_tidy.py
python scripts/01_tidy/03_visitor_arrests_tidy.py
python scripts/01_tidy/08_arrests_by_status_tidy_before_2021.py
python scripts/01_tidy/08_arrests_by_status_tidy_after_2022.py
python scripts/01_tidy/10_population_by_status_tidy_before_2020.py
python scripts/01_tidy/10_population_by_status_tidy_after_2021.py
python scripts/01_tidy/11_a_tidying_japanese_population_before_2020.py
python scripts/01_tidy/11_b_tidying_japanese_population_after_2021.py
python scripts/01_tidy/12_depart_tidy_before_2021.py
python scripts/01_tidy/12_depart_tidy_after_2022.py
python scripts/01_tidy/13_entry_tidy_before_2021_age.py
python scripts/01_tidy/13_entry_tidy_before_2021_status.py
python scripts/01_tidy/13_entry_tidy_after_2022.py
python scripts/01_tidy/14_a_Illegal_resident_tidy_before_2017.py
python scripts/01_tidy/14_b_Illegal_resident_tidy_2018to2020.py
python scripts/01_tidy/14_c_Illegal_resident_tidy_after_2021.py
python scripts/01_tidy/99_merge.py
python scripts/01_tidy/99_merge_10.py

# 2. 名寄せ
python scripts/02_standardize/standardize.py

# 3. 推計
python scripts/03_estimate/04_non_visitor_foreign_arrests.py
python scripts/03_estimate/05_japanese_arrests.py
python scripts/03_estimate/10_population_by_status_unknown_age_to_70plus.py
python scripts/03_estimate/11_japanese_population.py
python scripts/03_estimate/13_entry_by_age_before_2021.py
python scripts/03_estimate/13_entry_by_age_after_2022.py
python scripts/03_estimate/13_entry_by_age_merge.py
python scripts/03_estimate/14_illegal_resident_by_status_age.py

# 4. 統合
python scripts/04_integrated/09_integrated_arrests.py
python scripts/04_integrated/15_integrated_population.py

# 5. 分析
python scripts/05_analytics/20_arrest_rate_per_10000.py
python scripts/05_analytics/31_age_specific_arrest_rate.py
python scripts/05_analytics/32_expected_arrests_age_adjusted.py
python scripts/05_analytics/33_ratio_to_expected_arrests.py
python scripts/05_analytics/40_cross_tables.py

# 6. 研究用図表（例）
python scripts/06_research/age_adjustment/03_visualize.py
python scripts/06_research/dispatch_worker_estimation/01_prepare_foreign_employment.py
python scripts/06_research/dispatch_worker_estimation/01_prepare_labor_force.py
python scripts/06_research/dispatch_worker_estimation/02_estimate.py
python scripts/06_research/dispatch_worker_estimation/03_visualize.py
python scripts/06_research/japanese_spouse/03_visualize.py
python scripts/06_research/resident_nationality/01_prepare_arrests.py
python scripts/06_research/resident_nationality/03_visualize_population.py
python scripts/06_research/resident_nationality/03_visualize_age.py
```

## 必要な環境

Python 3.11 系を想定しています。

主な利用ライブラリ:

- pandas
- numpy
- openpyxl
- xlrd

例:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install pandas numpy openpyxl xlrd
```

## 注意点

- 分析対象年は、統合処理で主に 2013 年以降に揃えています。
- 1万人あたり検挙人員数の計算では、刑事責任年齢未満に相当する `0~13歳` を人口母数から除外しています。
- `永住者等` は、在留資格別人口の一部を統合した区分として扱っています。
- 入国者や不法残留者など、一部の人口相当データには推計処理を含みます。
- Excel のクロス集計ファイルは閲覧用であり、再利用や追加分析には CSV を使う想定です。

## 主な成果物

最終的に確認するファイルは主に以下です。

```text
data/05_analytics/20_1万人あたり検挙人員数及び対日本人倍率.csv
data/05_analytics/20_1万人あたり検挙人員数及び対日本人倍率_クロス集計.xlsx
data/05_analytics/33_対推定検挙人員及び年齢調整後対日本人倍率.csv
data/05_analytics/33_対推定検挙人員及び年齢調整後対日本人倍率_クロス集計.xlsx
```
