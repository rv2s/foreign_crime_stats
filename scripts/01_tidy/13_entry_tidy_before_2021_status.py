# 2021年以前の入国者データ(在留資格別)について、短期滞在部分を抜き出してtidy化するコード

# ======================== ライブラリインポート ======================== 
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
INPUT_DIR = BASE_PATH / "00_raw" / "13_入国者" / "before_2021" / "在留資格別"
output_file = BASE_PATH / "01_tidy" / "13_入国者" / "before_2021" / "在留資格別" / "13_入国者_tidydata_2021年以前_在留資格別.csv"


CONFIG = {
    2021: {"input_file": INPUT_DIR / "21-00-06.xlsx", "usecols": "AF", "userow": 10, "check_val": 71771},
    2020: {"input_file": INPUT_DIR / "20-00-06.xlsx", "usecols": "AH", "userow": 11, "check_val": 3360941},
    2019: {"input_file": INPUT_DIR / "19-00-06.xlsx", "usecols": "AH", "userow": 11, "check_val": 27812646},
    2018: {"input_file": INPUT_DIR / "18-00-06.xlsx", "usecols": "AF", "userow": 11, "check_val": 27056619},
    2017: {"input_file": INPUT_DIR / "17-00-06.xlsx", "usecols": "AF", "userow": 11, "check_val": 24618379},
    2016: {"input_file": INPUT_DIR / "16-00-06.xlsx", "usecols": "AC", "userow": 11, "check_val": 20666612},
    2015: {"input_file": INPUT_DIR / "15-00-06.xlsx", "usecols": "AC", "userow": 11, "check_val": 17405723},
    2014: {"input_file": INPUT_DIR / "14-00-06.xlsx", "usecols": "AC", "userow": 11, "check_val": 12052224},
    2013: {"input_file": INPUT_DIR / "13-00-06.xls", "usecols": "AC", "userow": 11, "check_val": 9247675},
}


# ======================== 関数定義 ======================== 
def process_one(target_year):
    """
    各年の入国者数を取得してdict形式で返す
    """
    input_file = CONFIG[target_year]["input_file"]
    usecols    = CONFIG[target_year]["usecols"]
    userow     = CONFIG[target_year]["userow"]
    check_val  = CONFIG[target_year]["check_val"]
    skiprows   = userow - 1


    # ======================== 読み込み ======================== 
    df = pd.read_excel(io=input_file, usecols=usecols, skiprows=skiprows, nrows=1, header=None)

    # データ取得
    base_pop = df.iloc[0, 0]

    # 数値確認
    print(f"{target_year}年: 差分{check_val - base_pop}")

    return {"年": target_year, "人数": base_pop}


# ======================== 実行 ========================
if __name__ == "__main__":
    dict_by_year = []

    for y in CONFIG.keys():
        dict_pop = process_one(y)
        dict_by_year.append(dict_pop)

    # データフレーム化
    df = pd.DataFrame(dict_by_year)

    # ソート
    df = df.sort_values(by="年", ascending=True)


    # ======================== 保存 ========================
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print("処理完了")
