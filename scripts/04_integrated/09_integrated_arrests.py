# 日本人・永住者等・来日外国人の検挙人員数を統合するコード

# ======================== ライブラリインポート ========================
from pathlib import Path
import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_japanese = BASE_PATH / "03_estimated" / "05_検挙人員数_日本人_推計.csv"
input_permanent = BASE_PATH / "03_estimated" / "04_検挙人員数_来日外国人以外_推計.csv"
input_visitor = BASE_PATH / "02_standardized" / "08_検挙人員数_在留資格別_名寄せ後.csv"
output_file = BASE_PATH / "04_integrated" / "09_検挙人員数_統合.csv"

df_japanese = pd.read_csv(input_japanese, encoding="utf-8-sig")
df_permanent = pd.read_csv(input_permanent, encoding="utf-8-sig")
df_visitor = pd.read_csv(input_visitor, encoding="utf-8-sig")


# ======================== 処理: 年範囲の統一 ========================
# 在留資格別の来日外国人データが2013年以降のため、全データを2013年以降に揃える。
df_japanese = df_japanese[df_japanese["年"] >= 2013].reset_index(drop=True)
df_permanent = df_permanent[df_permanent["年"] >= 2013].reset_index(drop=True)
df_visitor = df_visitor[df_visitor["年"] >= 2013].reset_index(drop=True)


# ======================== 処理: 区分列の追加 ========================
df_japanese["区分00"] = "日本人"
df_japanese["区分01"] = pd.NA
df_japanese["在留資格"] = pd.NA

df_permanent["区分00"] = "外国人"
df_permanent["区分01"] = "永住者等"
df_permanent["在留資格"] = pd.NA

df_visitor["区分00"] = "外国人"
df_visitor["区分01"] = "来日外国人"


# ======================== 処理: 統合 ========================
final_columns = [
    "年",
    "区分00",
    "区分01",
    "在留資格",
    "罪種00",
    "罪種01",
    "検挙人員",
]

check_val = (
    df_japanese["検挙人員"].sum()
    + df_permanent["検挙人員"].sum()
    + df_visitor["検挙人員"].sum()
)

df = pd.concat(
    [
        df_japanese[final_columns],
        df_permanent[final_columns],
        df_visitor[final_columns],
    ],
    ignore_index=True,
)

df = df.groupby(final_columns[:-1], as_index=False, dropna=False)["検挙人員"].sum()
df = df.sort_values(["年", "区分00", "区分01", "在留資格", "罪種00", "罪種01"]).reset_index(drop=True)


# ======================== 数値チェック・保存 ========================
total_val = df["検挙人員"].sum()
print(f"差分: {check_val - total_val:.6f}")

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
