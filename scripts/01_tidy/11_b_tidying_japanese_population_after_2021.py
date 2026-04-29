# 2021~2024年の日本人の年齢別・男女別人口のデータをtidy化するスクリプト

print("処理開始")

import pandas as pd
import numpy as np
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"

# ======================== パス設定 ======================== 
INPUT_DIR = BASE_PATH / "00_raw" / "11_人口_日本人"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "11_人口_日本人"


# ======================== 基本情報 ======================== 
# start_row: 表として読み込みたい最初の行, end_row: 表として読み込みたい最後の行, usecols: 表として読み込みたい列の範囲, check_val: 日本人合計値, skiprows: 上から飛ばす行数, nrows: 使用する行数
CONFIG = [
    {"year": 2024,
     "input_path": INPUT_DIR / "2024" / "a00100_2.xlsx",
     "output_path": OUTPUT_DIR / "11_2024_tidy.csv",
     "sheet_name": "第１表",
     "header": None,
     "start_row": 10,
     "end_row": 111,
     "usecols": "J, O:Q",
     "check_val": 120296,
     "cols": ["年齢", "男女計", "男", "女"],
    },
    {"year": 2023,
     "input_path": INPUT_DIR / "2023" / "a00100_2.xlsx",
     "output_path": OUTPUT_DIR / "11_2023_tidy.csv",
     "sheet_name": "第１表",
     "header": None,
     "start_row": 10,
     "end_row": 111,
     "usecols": "J, O:Q",
     "check_val": 121193,
     "cols": ["年齢", "男女計", "男", "女"],
    },
    {"year": 2022,
     "input_path": INPUT_DIR / "2022" / "a00100_2.xlsx",
     "output_path": OUTPUT_DIR / "11_2022_tidy.csv",
     "sheet_name": "第１表",
     "header": None,
     "start_row": 10,
     "end_row": 111,
     "usecols": "J, O:Q",
     "check_val": 122031,
     "cols": ["年齢", "男女計", "男", "女"],
    },
    {"year": 2021,
     "input_path": INPUT_DIR / "2021" / "a00100_2.xlsx",
     "output_path": OUTPUT_DIR / "11_2021_tidy.csv",
     "sheet_name": "第１表",
     "header": None,
     "start_row": 10,
     "end_row": 111,
     "usecols": "J, O:Q",
     "check_val": 122780,
     "cols": ["年齢", "男女計", "男", "女"],
    },







]

def process_one(cfg: dict) -> None:

    # ======================== 読み込み ========================
    skiprows = cfg["start_row"] - 1
    nrows = cfg["end_row"] - skiprows
    df = pd.read_excel(io=cfg["input_path"], sheet_name=cfg["sheet_name"], header=cfg["header"], skiprows=skiprows, nrows=nrows, usecols=cfg["usecols"], names=cfg["cols"])


    # ======================== メイン処理 ======================== 
    # total_val値取得(年齢列が総数の行の男女計列の値)
    total_val = df.loc[df["年齢"] == "総数", "男女計"].values[0]

    # 総数行を落とす(「年齢」が「総数」ではない行だけを残す)
    df = df[df["年齢"] != "総数"].reset_index(drop=True)


    # ==== 年齢別・男女別人口列の作成 ====
    # 年齢計列を作成
    df["男女計_年齢計"] = df["男女計"].sum()

    # 年齢構成比列を作成
    df["年齢構成比"] = df["男女計"] / df["男女計_年齢計"]

    # 年齢別の男女計列を作成
    df["男女積上"] = df["男"] + df["女"]

    # 年齢別・男女別構成比列を算出
    df["男構成比"] = df["男"] / df["男女積上"]
    df["女構成比"] = df["女"] / df["男女積上"]

    # 年齢別・男女別人口算出
    df["日本人/男"] = total_val * df["年齢構成比"] * df["男構成比"]
    df["日本人/女"] = total_val * df["年齢構成比"] * df["女構成比"]


    # tidy化
    tidy = df.melt(id_vars=["年齢"], value_vars=["日本人/男", "日本人/女"], var_name="性別", value_name="人口_千人")


    # ==== 見栄え調整等 ====
    # 日本人/男or女 を / で区切って別列にする
    tidy[["区分", "性別"]] = tidy["性別"].str.split("/", expand=True)

    # 「年」列を作成
    tidy["年"] = cfg["year"]

    # 列順整理
    tidy = tidy[["年", "区分", "性別", "年齢", "人口_千人"]]


    # 数値チェック
    diff = total_val - tidy["人口_千人"].sum()
    print(f"{cfg['year']}年: 差分{diff:.6f}")


    # ======================== 保存 ======================== 
    tidy.to_csv(cfg["output_path"], index=False, encoding="utf-8-sig")
    print(f"保存完了: {cfg['year']}年")


# ======================== 実行 ======================== 
def main():
    for cfg in CONFIG:
        process_one(cfg)

if __name__ == "__main__":
    main()


