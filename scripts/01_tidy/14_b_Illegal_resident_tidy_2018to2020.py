# 2018~2020年の不法残留者データをtidy化するコード

import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "00_raw" / "14_不法残留者" / "2018to2021" / "001356693.xlsx"
output_file = BASE_PATH / "01_tidy" / "14_不法残留者" / "14_2018~2020_tidy.csv"

start_row = 7
end_row = 18
usecols = "B:F"
col_names = ["在留資格", "資格詳細", 2018, 2019, 2020]

skip_rows = start_row - 1
nrows = end_row - skip_rows

df = pd.read_excel(input_file, sheet_name="第２表・第３図", skiprows=skip_rows, usecols=usecols, nrows=nrows, header=None)

# 数値チェック用
check_val = 66498 + 74167 + 82892

# ======================== 処理 ======================== 
# 列名の付与
df.columns = col_names

# ffillで右埋め
df = df.ffill(axis=1)

# 在留資格列の削除
df = df.drop(columns=["在留資格"])

# 資格詳細列を在留資格列に名称変更
df = df.rename(columns={"資格詳細": "在留資格"})

# 在留資格列の正規化: "（"以降を削除し、KNFCを使って正規化
df["在留資格"] = df["在留資格"].str.split("（").str[0]
df["在留資格"] = df["在留資格"].astype(str).str.normalize("NFKC").str.replace(r"[\s　]+", "", regex=True) # スペース類(全角・半角スペース、タブ\t、改行\n、復帰\r、改頁\f)を削除

# 小計行である技能実習を削除
df = df[df["在留資格"] != "技能実習"].reset_index(drop=True)

# tidy化
df = df.melt(id_vars=["在留資格"], var_name="年", value_name="人数")

# 列順整理
df = df[["年", "在留資格", "人数"]]

# 数値チェック
total_val = df["人数"].sum()
print(f"差分: {check_val - total_val}")

# 保存
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")

