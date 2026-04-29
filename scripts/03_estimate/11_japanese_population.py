# 日本人人口の千人単位データを人数単位に変換するコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "02_standardized" / "11_人口_日本人_名寄せ後.csv"
output_file = BASE_PATH / "03_estimated" / "11_人口_日本人_人数換算.csv"

df = pd.read_csv(input_file, encoding="utf-8-sig")
check_val = df["人口_千人"].sum() * 1000


# ======================== 処理: 人数単位への変換 ========================
df["人数"] = df["人口_千人"] * 1000
df = df.drop(columns=["人口_千人"])


# ======================== 数値チェック・保存 ========================
total_val = df["人数"].sum()
print(f"差分: {check_val - total_val:.6f}")

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
