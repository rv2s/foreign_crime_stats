# 入国者の年代別年換算人口について、2021年以前と2022年以降の推計ファイルを統合するコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_before = BASE_PATH / "03_estimated" / "13_統合前" / "13_入国者_年代別年換算人口_2021年以前.csv"
input_after = BASE_PATH / "03_estimated" / "13_統合前" / "13_入国者_年代別年換算人口_2022年以降.csv"
output_file = BASE_PATH / "03_estimated" / "13_入国者_年代別年換算人口_統合.csv"

df_before = pd.read_csv(input_before, encoding="utf-8-sig")
df_after = pd.read_csv(input_after, encoding="utf-8-sig")


# ======================== 処理: 統合 ========================
expected_columns = ["年", "年代", "人数"]
if df_before.columns.tolist() != expected_columns:
    raise ValueError(f"2021年以前ファイルの列が想定と異なります: {df_before.columns.tolist()}")
if df_after.columns.tolist() != expected_columns:
    raise ValueError(f"2022年以降ファイルの列が想定と異なります: {df_after.columns.tolist()}")

df = pd.concat([df_before, df_after], ignore_index=True)

duplicated_keys = df[df.duplicated(subset=["年", "年代"], keep=False)]
if not duplicated_keys.empty:
    duplicated_values = duplicated_keys[["年", "年代"]].drop_duplicates()
    raise ValueError(
        "年・年代が重複しています: "
        + ", ".join(f"{row.年}:{row.年代}" for row in duplicated_values.itertuples(index=False))
    )

df = df.sort_values(["年", "年代"]).reset_index(drop=True)


# ======================== 数値チェック・保存 ========================
check_val = df_before["人数"].sum() + df_after["人数"].sum()
total_val = df["人数"].sum()
print(f"差分: {check_val - total_val:.6f}")

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
