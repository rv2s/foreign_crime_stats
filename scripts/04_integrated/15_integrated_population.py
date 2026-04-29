# 日本人・永住者等・来日外国人の人口データを統合するコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_status_population = BASE_PATH / "03_estimated" / "10_人口_在留資格別_不詳を70代以上に合算.csv"
input_japanese = BASE_PATH / "03_estimated" / "11_人口_日本人_人数換算.csv"
input_entry = BASE_PATH / "03_estimated" / "13_入国者_年代別年換算人口_統合.csv"
input_illegal = BASE_PATH / "03_estimated" / "14_不法残留者_在留資格別年代別推計.csv"
output_file = BASE_PATH / "04_integrated" / "15_人口_統合.csv"

df_status_population = pd.read_csv(input_status_population, encoding="utf-8-sig")
df_japanese = pd.read_csv(input_japanese, encoding="utf-8-sig")
df_entry = pd.read_csv(input_entry, encoding="utf-8-sig")
df_illegal = pd.read_csv(input_illegal, encoding="utf-8-sig")


# ======================== 処理: 年範囲の統一 ========================
df_status_population = df_status_population[df_status_population["年"] >= 2013].reset_index(drop=True)
df_japanese = df_japanese[df_japanese["年"] >= 2013].reset_index(drop=True)
df_entry = df_entry[df_entry["年"] >= 2013].reset_index(drop=True)
df_illegal = df_illegal[df_illegal["年"] >= 2013].reset_index(drop=True)


# ======================== 処理: 区分列の追加 ========================
df_status_population = df_status_population.rename(columns={"人口": "人数"})
df_status_population["区分00"] = "外国人"
df_status_population["区分01"] = "来日外国人"
is_permanent = df_status_population["在留資格"] == "永住者等"
df_status_population.loc[is_permanent, "区分01"] = "永住者等"
df_status_population.loc[is_permanent, "在留資格"] = pd.NA

df_japanese["区分00"] = "日本人"
df_japanese["区分01"] = pd.NA
df_japanese["在留資格"] = pd.NA

df_entry["区分00"] = "外国人"
df_entry["区分01"] = "来日外国人"
df_entry["在留資格"] = "短期滞在"

df_illegal["区分00"] = "外国人"
df_illegal["区分01"] = "来日外国人"


# ======================== 処理: 統合 ========================
final_columns = ["年", "区分00", "区分01", "在留資格", "年代", "人数"]

check_val = (
    df_status_population["人数"].sum()
    + df_japanese["人数"].sum()
    + df_entry["人数"].sum()
    + df_illegal["人数"].sum()
)

df = pd.concat(
    [
        df_status_population[final_columns],
        df_japanese[final_columns],
        df_entry[final_columns],
        df_illegal[final_columns],
    ],
    ignore_index=True,
)

df = df.groupby(final_columns[:-1], as_index=False, dropna=False)["人数"].sum()
df = df.sort_values(["年", "区分00", "区分01", "在留資格", "年代"]).reset_index(drop=True)


# ======================== 数値チェック・保存 ========================
total_val = df["人数"].sum()
print(f"差分: {check_val - total_val:.6f}")

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
