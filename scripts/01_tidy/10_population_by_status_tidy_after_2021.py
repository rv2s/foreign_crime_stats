
print("処理開始")
# ======================================== ライブラリインポート ========================================
import pandas as pd
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
import unicodedata


# ======================================== 基本情報 ========================================
INPUT_DIR = BASE_PATH / "00_raw" / "10_人口_在留資格別"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "10_人口_在留資格別"

CONFIG = {
    2024: {"year": 2024, "input_file": INPUT_DIR / "24-06-t1.xlsx", "output_file": OUTPUT_DIR / "10_2024_tidy.csv", "sheet_name": "令和６年６月末", "header": 0},
    2023: {"year": 2023, "input_file": INPUT_DIR / "23-06-t1.xlsx", "output_file": OUTPUT_DIR / "10_2023_tidy.csv", "sheet_name": "ページ1_1", "header": 0},
    2022: {"year": 2022, "input_file": INPUT_DIR / "22-06" / "在留外国人統計テーブルデータ.xlsx", "output_file": OUTPUT_DIR / "10_2022_tidy.csv", "sheet_name": "ページ1_1", "header": 0},
    2021: {"year": 2021, "input_file": INPUT_DIR / "21-06" / "在留外国人統計テーブルデータ.xlsx", "output_file": OUTPUT_DIR / "10_2021_tidy.csv", "sheet_name": "基データ", "header": 0},
}


# ======================================== 関数定義 ========================================
def process_one(target_year):
    """
    1年分の設定を受け取りtidy化をして保存までを行う
    """
    # ======================================== 読み込み ========================================
    year        = CONFIG[target_year]["year"]
    input_file  = CONFIG[target_year]["input_file"]
    output_file = CONFIG[target_year]["output_file"]
    sheet_name  = CONFIG[target_year]["sheet_name"]
    header      = CONFIG[target_year]["header"]

    df = pd.read_excel(io=input_file, sheet_name=sheet_name, header=header)

    # ======================================== メイン処理 ========================================
    print(f"{year}年: 処理開始")

    # カラム名の変更
    df = df.rename(columns={"在留外国人数": "人口"})

    # 文字列系の列を正規化
    text_cols = [
        col
        for col in df.columns
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col])
    ]
    for col in text_cols:
        df[col] = df[col].map(lambda x: unicodedata.normalize("NFKC", x) if isinstance(x, str) else x)

    # 「:」以降の文字を残す ※n=1は区切り文字の右側を残す。str[-1]は区切り文字がない場合は文字がそのまま残る(str[1]ならNaNになる)
    for col in text_cols:
        df[col] = df[col].astype(str).str.split(":", n=1).str[-1]
        # astype(str)によって "nan" という文字列になってしまった欠損値を正しい欠損値（NoneやNaN）に差し戻す
        df[col] = df[col].replace("nan", pd.NA)

    # 年列を追加
    df["年"] = year

    # 列順を整理
    df = df[["年", "国籍・地域", "在留資格", "性別", "年齢", "都道府県", "人口"]]

    # 保存
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"{year}年: 処理完了")


# ======================================== 実行 ========================================
if __name__ == "__main__":
    for y in CONFIG.keys():
        process_one(target_year=y)

print("処理完了")
























