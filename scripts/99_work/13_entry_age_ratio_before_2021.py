# 入国者マクロデータ(2021年以前)の年代構成比を計算するコード

# ======================== ライブラリインポート ======================== 
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "01_tidy" / "13_入国者" / "before_2021" / "年代別" / "13_入国者_tidydata_2021年以前_年代別.csv"
output_file = BASE_PATH / "99_work" / "13_入国者" / "before_2021" / "03_parameters" / "13_入国者マクロ_年代構成比_2021年以前.csv"

df = pd.read_csv(input_file, encoding="utf-8-sig")


# ======================== 処理: 年代構成比算出 ======================== 
# マクロ入国者の年代構成比算出
df["年別合計人数"] = df.groupby(["年"], as_index=False)["人数"].transform("sum")
df["年代構成比"] = df["人数"] / df["年別合計人数"]


# 保存
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")