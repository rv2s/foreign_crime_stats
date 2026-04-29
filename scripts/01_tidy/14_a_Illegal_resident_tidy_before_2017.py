# 2015~2017年の不法残留者データをtidy化するコード

import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "00_raw" / "14_不法残留者" / "1990to2019" / "4-9-1-02.xlsx"
output_file = BASE_PATH / "01_tidy" / "14_不法残留者" / "14_2013~2017_tidy.csv"

start_row = 30
end_row = 34
usecols = "B:C"
col_names = ["年", "人数"]

skip_rows = start_row - 1
nrows = end_row - skip_rows

df = pd.read_excel(input_file, sheet_name="4-9-1-2図", skiprows=skip_rows, usecols=usecols, nrows=nrows, header=None)


# ======================== 処理 ======================== 
# 列名の付与
df.columns = col_names

# 年を和暦から西暦に変更 ※ 和暦(平成)に1988を足すと西暦になる仕組みを利用
df["年"] = df["年"] + 1988

# 保存
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")

