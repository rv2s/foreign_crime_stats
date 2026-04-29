# 2022年以降の入国者データについて、tidy化するコード

# ======================== ライブラリインポート ======================== 
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "00_raw" / "99_manual" / "13_入国者" / "after_2022" / "02_created" / "手作成_入国者数_2022以降.xlsx"
output_file = BASE_PATH / "01_tidy" / "13_入国者" / "after_2022" / "13_入国者_tidydata_2022年以降.csv"

df = pd.read_excel(input_file, sheet_name="Sheet1")


# ======================== 処理: 入国者データの正規化 及び csv保存 ======================== 
df["年代"] = df["年代"].astype(str).str.normalize("NFKC").str.replace(r"[\s　]+", "", regex=True) # スペース類(全角・半角スペース、タブ\t、改行\n、復帰\r、改頁\f)を削除
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
