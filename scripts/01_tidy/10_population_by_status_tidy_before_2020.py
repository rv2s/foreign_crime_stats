print("処理開始")
import pandas as pd
import numpy as np
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"

# ======================== パス設定 ========================
INPUT_DIR = BASE_PATH / "00_raw" / "10_人口_在留資格別"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "10_人口_在留資格別"

# ======================== 基本情報 ========================
CONFIG = [
    {"input_path": INPUT_DIR / "20-06-03.xlsx", "output_path": OUTPUT_DIR / "10_2020_tidy.csv", "sheet_name": "20-06-03", "header": None, "usecols": "A:FJ", "skiprows": 3,  "check_val": 2885904, "year": 2020, "pattern": 1},
    {"input_path": INPUT_DIR / "19-06-03.xlsx", "output_path": OUTPUT_DIR / "10_2019_tidy.csv", "sheet_name": "19-06-03", "header": None, "usecols": "B:FK", "skiprows": 3,  "check_val": 2829416, "year": 2019, "pattern": 2},
    {"input_path": INPUT_DIR / "18-06-03.xlsx", "output_path": OUTPUT_DIR / "10_2018_tidy.csv", "sheet_name": "18-06-03", "header": None, "usecols": "B:FK", "skiprows": 3,  "check_val": 2637251, "year": 2018, "pattern": 2},
    {"input_path": INPUT_DIR / "17-06-03.xlsx", "output_path": OUTPUT_DIR / "10_2017_tidy.csv", "sheet_name": "17-06-03", "header": None, "usecols": "B:FM", "skiprows": 3,  "check_val": 2471458, "year": 2017, "pattern": 2},
    {"input_path": INPUT_DIR / "16-06-03.xlsx", "output_path": OUTPUT_DIR / "10_2016_tidy.csv", "sheet_name": "16-06-03 ", "header": None, "usecols": "B:FM", "skiprows": 3,  "check_val": 2307388, "year": 2016, "pattern": 2},
    {"input_path": INPUT_DIR / "15-06-03.xlsx", "output_path": OUTPUT_DIR / "10_2015_tidy.csv", "sheet_name": "15-06-03", "header": None, "usecols": "B:FM", "skiprows": 3,  "check_val": 2172892, "year": 2015, "pattern": 2},
    {"input_path": INPUT_DIR / "14-06-03.xlsx", "output_path": OUTPUT_DIR / "10_2014_tidy.csv", "sheet_name": "14-06-03", "header": None, "usecols": "B:FM", "skiprows": 3,  "check_val": 2086603, "year": 2014, "pattern": 2},
    {"input_path": INPUT_DIR / "13-06-03.xlsx", "output_path": OUTPUT_DIR / "10_2013_tidy.csv", "sheet_name": "13-06-03", "header": None, "usecols": "B:FM", "skiprows": 3,  "check_val": 2049123, "year": 2013, "pattern": 2},
]

def process_one(cfg: dict) -> None:
    input_path: Path = cfg["input_path"]
    output_path: Path = cfg["output_path"]

    # ======================== 読み込み ========================
    df_raw = pd.read_excel(
        io=input_path,
        sheet_name=cfg["sheet_name"],
        header=cfg["header"],
        usecols=cfg["usecols"],
        skiprows=cfg["skiprows"],
    )

    # ======================== メイン処理 ========================
    # == 0行目(年齢行)を取得(Series)し、欠損をffillで埋める ==
    print(f"{cfg['year']}年: 処理開始")

    target_row = 0
    df_raw.loc[target_row, :] = df_raw.loc[target_row, :].ffill()

    # == 総数が入っている列を削除 == 
    target_word = "総"
    df_raw = df_raw.loc[:, ~df_raw.iloc[target_row, :].astype(str).str.contains(target_word, na=False)]

    # == 総数が入っている行を削除 == 
    # pattern1: 総数が入っている行を削除(0列目指定) ※pattern1は在留資格記載列と同列に総数の文字が入っている
    if cfg["pattern"] == 1:
        df_raw = df_raw.loc[~df_raw.iloc[:, 0].astype(str).str.contains(target_word, na=False), :].reset_index(drop=True)
    # pattern2: 上から3行目(pattern1でいう総数の行)を削除 ※pattern2は在留資格記載列の左列に総数の文字が入っている
    elif cfg["pattern"] == 2:
        df_raw = df_raw.drop(index=df_raw.index[2:3]).reset_index(drop=True)
    # 事故防止
    else:
        raise ValueError(f"未知の pattern: {cfg['pattern']}")

    # == 年齢行と性別行を「/」で結合 == 
    # 1. 0行目と1行目を取得
    row0 = df_raw.iloc[0, :].astype(str).replace("nan", "")
    row1 = df_raw.iloc[1, :].astype(str).replace("nan", "")

    # 2. Series同士を「/」で結合（全166列が一瞬で結合される）
    new_columns = (row0 + "/" + row1).str.strip("/")
    df_raw.columns = new_columns

    # == 不要な年齢と性別が入った行を削除(上から2行を削除) == 
    df_raw = df_raw.drop(index=df_raw.index[0:2]).reset_index(drop=True)

    # == 1番目の列名(インデックス0)を「在留資格」に書き換え == 
    # columnsオブジェクトは直接変更できないため、一旦リストに変換して行う
    columns_list = df_raw.columns.to_list()
    columns_list[0] = "在留資格"
    df_raw.columns = columns_list

    # == meltでtidy化 == 
    df_tidy = df_raw.melt(id_vars=["在留資格"], var_name="年齢/性別", value_name="人口")

    # == 年齢/性別列の分割 == 
    df_tidy[["年齢", "性別"]] = df_tidy["年齢/性別"].str.split("/", expand=True)

    # == 不要になった年齢/性別列の削除 == 
    df_tidy = df_tidy.drop(columns="年齢/性別")

    # == 年齢列と在留資格列の数値を半角に == 
    zen = "０１２３４５６７８９"
    han = "0123456789"
    df_tidy["年齢"] = df_tidy["年齢"].astype(str).str.translate(str.maketrans(zen, han))
    df_tidy["在留資格"] = df_tidy["在留資格"].astype(str).str.translate(str.maketrans(zen, han))

    # == 念のため余計なスペースを除去 == 
    # 対象とする列のリスト（人口列以外）
    target_cols = ["在留資格", "年齢", "性別"]

    # 正規表現 \s は「半角スペース、全角スペース、改行、タブ」すべてにヒットします
    # これを空文字 ""に置き換えることで、文字を完全に詰めます
    for col in target_cols:
        df_tidy[col] = df_tidy[col].str.replace(r"\s+", "", regex=True)

    # 年列の追加
    df_tidy["年"] = cfg["year"]

    # 列順の整理
    df_tidy = df_tidy[["年", "在留資格", "性別", "年齢", "人口"]]

    # == 数値チェック == 
    sum_val = df_tidy["人口"].sum()
    diff = cfg["check_val"] - sum_val
    print(f"{cfg['year']}年 差分: {diff}")

    # == 保存 == 
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_tidy.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"{cfg['year']}年: 処理完了")

def main():
    for cfg in CONFIG:
        process_one(cfg)

if __name__ == "__main__":
    main()

print("処理完了")






