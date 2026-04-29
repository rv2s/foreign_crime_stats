# 在留資格別人口の年代「不詳」を「70代以上」に含めるコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "02_standardized" / "10_人口_在留資格別_名寄せ後.csv"
output_file = BASE_PATH / "03_estimated" / "10_人口_在留資格別_不詳を70代以上に合算.csv"

df = pd.read_csv(input_file, encoding="utf-8-sig")
check_val = df["人口"].sum()


# ======================== 処理: 不詳を70代以上に統合 ========================
df["年代"] = df["年代"].replace({"不詳": "70代以上"})
df = df.groupby(["年", "在留資格", "年代"], as_index=False, dropna=False)["人口"].sum()


# ======================== 数値チェック・保存 ========================
total_val = df["人口"].sum()
print(f"差分: {check_val - total_val:.6f}")
print(f"不詳行数: {(df['年代'] == '不詳').sum()}")

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
