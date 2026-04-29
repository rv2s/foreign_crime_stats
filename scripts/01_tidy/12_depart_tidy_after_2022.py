# 2022年以降の出国者データについて、tidy化するコード

# ======================== ライブラリインポート ======================== 
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "00_raw" / "99_manual" / "12_出国者" / "after_2022" / "02_created" / "手作成_出国者数_2022以降.xlsx"
output_file = BASE_PATH / "01_tidy" / "12_出国者" / "after_2022" / "12_出国者_tidydata_2022年以降.csv"


# ======================== 処理: 出国者データのtidy化 ======================== 
sheet_name_list = [2024, 2023, 2022]
df_list = []

for y in sheet_name_list:
    # 読み込み
    df = pd.read_excel(input_file, sheet_name=str(y))

    # tidy化
    df = df.melt(id_vars=["行ラベル"], var_name="年代", value_name="人数")

    # 列名の変更
    df = df.rename(columns={"行ラベル": "滞在期間"})

    # クレンジング
    for col in ["滞在期間", "年代"]:
        df[col] = df[col].astype(str).str.normalize("NFKC").str.replace(r"[\s　]+", "", regex=True) # スペース類(全角・半角スペース、タブ\t、改行\n、復帰\r、改頁\f)を削除

    # 「:」で区切って後半だけ残す(「:」がない場合はそのまま残す)
    df["滞在期間"] = df["滞在期間"].str.split(":", n=1).str[-1]

    # 年列の追加
    df["年"] = y

    # リストに追加
    df_list.append(df)


# リストに溜まった各年のdfを縦に結合する
df = pd.concat(df_list, ignore_index=True)

# 列順の整理
df = df[["年", "年代", "滞在期間", "人数"]]

# 出国者データの保存
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("処理完了")

