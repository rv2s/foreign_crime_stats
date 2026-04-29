# 2021年以前の入国者データ(年代別マクロ)について、tidy化するコード

# ======================== ライブラリインポート ======================== 
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
INPUT_DIR = BASE_PATH / "00_raw" / "13_入国者" / "before_2021" / "年代別"
output_file = BASE_PATH / "01_tidy" / "13_入国者" / "before_2021" / "年代別" / "13_入国者_tidydata_2021年以前_年代別.csv"

CONFIG = {
    2021: {"input_file": INPUT_DIR / "21-00-12.xlsx", "start_row": 2, "end_row":5, "check_val": 196191 + 156928},
    2020: {"input_file": INPUT_DIR / "20-00-12.xlsx", "start_row": 3, "end_row":6, "check_val": 2138616 + 2168641},
    2019: {"input_file": INPUT_DIR / "19-00-12.xlsx", "start_row": 3, "end_row":6, "check_val": 14520939 + 16666240},
    2018: {"input_file": INPUT_DIR / "18-00-12.xlsx", "start_row": 3, "end_row":6, "check_val": 13876824 + 16225278},
    2017: {"input_file": INPUT_DIR / "17-00-12.xlsx", "start_row": 3, "end_row":6, "check_val": 12600233 + 14828549},
    2016: {"input_file": INPUT_DIR / "16-00-12.xlsx", "start_row": 3, "end_row":6, "check_val": 10712511 + 12506401},
    2015: {"input_file": INPUT_DIR / "15-00-12.xlsx", "start_row": 3, "end_row":6, "check_val": 9157571 + 10530676},
    2014: {"input_file": INPUT_DIR / "14-00-12.xlsx", "start_row": 3, "end_row":6, "check_val": 6865017 + 7285168},
    2013: {"input_file": INPUT_DIR / "13-00-12.xls", "start_row": 3, "end_row":6, "check_val": 5617034 + 5638187},
}


# ======================== 関数定義 ======================== 
def process_one(target_year):
    """
    各年の按分比用の年代別人数をデータフレームで返す
    """
    # ======================== 設定 ======================== 
    input_file = CONFIG[target_year]["input_file"]
    start_row  = CONFIG[target_year]["start_row"]
    end_row    = CONFIG[target_year]["end_row"]
    check_val    = CONFIG[target_year]["check_val"]
    skiprows   = start_row - 1
    nrows      = end_row - skiprows


    # ======================== 処理 ======================== 
    df = pd.read_excel(io=input_file, skiprows=skiprows, nrows=nrows, header=None)

    # 縦横反転
    df = df.T.reset_index(drop=True)

    # 下方向fill
    df[0] = df[0].ffill()

    # 国籍・地域以外を残す
    df = df[(df[0] != "国籍・地域") & (df[0] != "総数") ].reset_index(drop=True)

    # 集計(性別を合算)
    df = df.groupby([0], as_index=False)[3].sum()

    # 列名変更
    df = df.rename(columns={0: "年代", 3: "人数"})

    # 型変更
    df["人数"] = df["人数"].astype(float)

    # 年列追加
    df["年"] = target_year

    # 列順整理
    df = df[["年", "年代", "人数"]]

    # 正規化
    df["年代"] = df["年代"].astype(str).str.normalize("NFKC").str.replace(r"[\s　]+", "", regex=True)

    # 数値チェック
    total_val = df["人数"].sum()
    print(f"{target_year}年: 差分{total_val - check_val}")

    return df


# ======================== 実行 ========================
if __name__ == "__main__":
    dfs = []

    for y in CONFIG.keys():
        df = process_one(y) # df = (関数内の)df
        dfs.append(df)


    # ======================== データフレームの結合 ========================
    df_final = pd.concat(dfs, ignore_index=True)

    # ソート
    df_final = df_final.sort_values(by=["年", "年代"], ascending=True)


    # ======================== 保存 ========================
    df_final.to_csv(output_file, index=False, encoding="utf-8-sig")
    print("処理完了")

