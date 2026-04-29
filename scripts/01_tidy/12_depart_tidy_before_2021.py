# 2021年以前の出国者データについて、tidy化するコード

# ======================== ライブラリインポート ======================== 
import pandas as pd
from pathlib import Path


# ======================== パス設定 ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
INPUT_DIR = BASE_PATH / "00_raw" / "12_出国者" / "before_2021"
output_file = BASE_PATH / "01_tidy" / "12_出国者" / "before_2021" / "12_出国者_tidydata_2021年以前.csv"


CONFIG = {
    2021: {"input_file": INPUT_DIR / "21-00-15.xlsx", "start_row": 2, "end_row":4, "check_val": 83742},
    2020: {"input_file": INPUT_DIR / "20-00-15.xlsx", "start_row": 3, "end_row":6, "check_val": 3947214},
    2019: {"input_file": INPUT_DIR / "19-00-15.xlsx", "start_row": 3, "end_row":6, "check_val": 27747535},
    2018: {"input_file": INPUT_DIR / "18-00-15.xlsx", "start_row": 3, "end_row":6, "check_val": 26958343},
    2017: {"input_file": INPUT_DIR / "17-00-15.xlsx", "start_row": 3, "end_row":6, "check_val": 24509770},
    2016: {"input_file": INPUT_DIR / "16-00-15.xlsx", "start_row": 3, "end_row":6, "check_val": 20573766},
    2015: {"input_file": INPUT_DIR / "15-00-15.xlsx", "start_row": 3, "end_row":6, "check_val": 17282449},
    2014: {"input_file": INPUT_DIR / "14-00-15.xlsx", "start_row": 3, "end_row":6, "check_val": 11935952},
    2013: {"input_file": INPUT_DIR / "13-00-15.xls", "start_row": 3, "end_row":6, "check_val": 9182466},
}


# ======================== 関数定義 ======================== 
def process_one(target_year):
    """
    各年の平均滞在日数算出用の滞在期間別人数をデータフレームで返す
    """
    # ======================== 設定 ======================== 
    input_file = CONFIG[target_year]["input_file"]
    start_row  = CONFIG[target_year]["start_row"]
    end_row    = CONFIG[target_year]["end_row"]
    check_val  = CONFIG[target_year]["check_val"]
    skiprows   = start_row - 1
    nrows      = end_row - skiprows


    # ======================== 処理 ======================== 
    df = pd.read_excel(io=input_file, skiprows=skiprows, nrows=nrows, header=None)

    # 縦横反転
    df = df.T.reset_index(drop=True)

    # 0列目が NaN の行を削除
    df = df.dropna(subset=[0])

    # 特定の文字列を除外
    df = df[~df[0].isin(["国籍・地域", "総数"])].reset_index(drop=True)

    # 列名変更
    df = df.rename(columns={0: "滞在期間", df.columns[-1]: "人数"})

    # 必要行に絞る
    df = df[["滞在期間", "人数"]]

    # 型変更
    df["人数"] = df["人数"].astype(float)

    # 年列追加
    df["年"] = target_year

    # 列順整理
    df = df[["年", "滞在期間", "人数"]]

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

    # クレンジング
    df_final["滞在期間"] = (
        df_final["滞在期間"]
        .astype(str)
        .str.normalize("NFKC")
        .str.replace(r"[\s　]+", "", regex=True) # スペース類(全角・半角スペース、タブ\t、改行\n、復帰\r、改頁\f)を削除
    )

    # ソート
    df_final = df_final.sort_values(by=["年"], ascending=True)


    # ======================== 保存 ========================
    df_final.to_csv(output_file, index=False, encoding="utf-8-sig")
    print("処理完了")

