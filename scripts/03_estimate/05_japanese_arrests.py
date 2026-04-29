# 日本人検挙人員数を差分で算出するコード
# 日本人 = 日本全体 - 外国人全体

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== 関数定義 ========================
def aggregate_arrests(df, group_columns):
    """指定した粒度で検挙人員を集計する。"""
    return df.groupby(group_columns, as_index=False, dropna=False)["検挙人員"].sum()


def subtract_arrests(left, right, group_columns, left_name, right_name):
    """同じ粒度に集計済みの2データを結合し、left - right を計算する。"""
    df = pd.merge(
        left=left.rename(columns={"検挙人員": left_name}),
        right=right.rename(columns={"検挙人員": right_name}),
        on=group_columns,
        how="outer",
    )
    df[[left_name, right_name]] = df[[left_name, right_name]].fillna(0)
    df["検挙人員"] = df[left_name] - df[right_name]
    return df[group_columns + ["検挙人員"]]


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_total = BASE_PATH / "02_standardized" / "01_検挙人員数_日本全体_名寄せ後.csv"
input_foreign = BASE_PATH / "02_standardized" / "02_検挙人員数_外国人全体_名寄せ後.csv"
output_file = BASE_PATH / "03_estimated" / "05_検挙人員数_日本人_推計.csv"

df_total = pd.read_csv(input_total, encoding="utf-8-sig")
df_foreign = pd.read_csv(input_foreign, encoding="utf-8-sig")


# ======================== 処理: 日本人検挙人員数算出 ========================
group_columns = ["年", "罪種00", "罪種01", "罪種02"]

# 外国人全体には年代列がないため、日本全体も年代を合計して同じ粒度に揃える
df_total = aggregate_arrests(df_total, group_columns)
df_foreign = aggregate_arrests(df_foreign, group_columns)

df = subtract_arrests(
    left=df_total,
    right=df_foreign,
    group_columns=group_columns,
    left_name="日本全体",
    right_name="外国人全体",
)
df = df.sort_values(group_columns).reset_index(drop=True)


# ======================== 数値チェック・保存 ========================
negative_rows = df[df["検挙人員"] < 0]
print(f"負値行数: {len(negative_rows)}")
if not negative_rows.empty:
    print(f"最小値: {negative_rows['検挙人員'].min()}")

check_val = df_total["検挙人員"].sum() - df_foreign["検挙人員"].sum()
total_val = df["検挙人員"].sum()
print(f"差分: {check_val - total_val:.6f}")

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
