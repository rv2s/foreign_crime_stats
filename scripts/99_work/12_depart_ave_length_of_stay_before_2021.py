# 2021年以前の出国者データについて、平均滞在日数を計算するコード

# ======================== ライブラリインポート ========================
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "01_tidy" / "12_出国者" / "before_2021" / "12_出国者_tidydata_2021年以前.csv"
input_map = BASE_PATH / "99_work" / "12_出国者" / "before_2021" / "02_map" / "12_出国者_滞在期間マップ_2021年以前.csv"
output_file = BASE_PATH / "99_work" / "12_出国者" / "before_2021" / "03_parameters" / "12_出国者_年別平均滞在日数.csv"

df = pd.read_csv(input_file)
df_map = pd.read_csv(input_map)


# ======================== 処理: 平均滞在日数の計算 ========================
# マップファイルを使って平均滞在日数をマージ
df = pd.merge(
    left  = df[["年", "滞在期間", "人数"]], # 残したいカラム名
    right = df_map[["滞在期間", "平均滞在日数"]],
    on    = ["滞在期間"], # 共通カラム名
    how   = "left" # 指定した側はデータが落ちない
)

# 滞在日数算出
df["滞在日数"] = df["平均滞在日数"] * df["人数"]

# 年別に人数と滞在日数を集計
df = df.groupby(["年"], as_index=False).agg({"人数": "sum", "滞在日数": "sum"})

# 年別の平均滞在日数算出
df["年別平均滞在日数"] = df["滞在日数"] / df["人数"]

# 保存
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")