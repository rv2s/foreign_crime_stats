# 2022年以降の出国者データについて、年代別の平均滞在日数を計算するコード

# ======================== ライブラリインポート ========================
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "01_tidy" / "12_出国者" / "after_2022" / "12_出国者_tidydata_2022年以降.csv"
input_map = BASE_PATH / "99_work" / "12_出国者" / "after_2022" / "02_map" / "12_出国者_滞在期間別平均滞在日数map_2022年以降.csv"
output_file = BASE_PATH / "99_work" / "12_出国者" / "after_2022" / "03_parameters" / "12_出国者_年代別平均滞在日数.csv"

df = pd.read_csv(input_file)
df_map = pd.read_csv(input_map)


# ======================== 処理: 年代別の平均滞在日数の計算 ========================
# マップファイルを使って滞在期間を平均滞在日数に変換
df = pd.merge(
    left  = df[["年", "年代", "滞在期間", "人数"]], # 残したいカラム名
    right = df_map[["滞在期間", "平均滞在日数"]],
    on    = ["滞在期間"], # 共通カラム名
    how   = "left" # 指定した側はデータが落ちない
)

# 滞在日数算出
df["滞在日数"] = df["平均滞在日数"] * df["人数"]

# 年代別に人数と滞在日数を集計
df = df.groupby(["年", "年代"], as_index=False).agg({"人数": "sum", "滞在日数": "sum"})

# 年代別の平均滞在日数算出
df["年代別平均滞在日数"] = df["滞在日数"] / df["人数"]

# 保存
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")