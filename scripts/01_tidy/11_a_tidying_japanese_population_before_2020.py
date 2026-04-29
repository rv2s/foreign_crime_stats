# 2010~2020年の日本人の年齢別・男女別人口のデータをtidy化するスクリプト

print("処理を開始します")

import pandas as pd
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"


# ======================== パス設定 ======================== 
INPUT_DIR = BASE_PATH / "00_raw" / "11_人口_日本人"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "11_人口_日本人"


# ======================== 基本情報 ======================== 
CONFIG = {
    2020: {
        "year": 2020,
        "input_path": INPUT_DIR / "2020" / "001.xls",
        "output_path": OUTPUT_DIR / "11_2020_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "B, G:I", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 123399, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 17, # 表として読み込みたい最初の行
                "end_row": 67, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 90, # 表として読み込みたい最初の行
                "end_row": 140, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2019: {
        "year": 2019,
        "input_path": INPUT_DIR / "2019" / "a00100.xls",
        "output_path": OUTPUT_DIR / "11_2019_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "H, N:P", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 123731, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 19, # 表として読み込みたい最初の行
                "end_row": 69, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 92, # 表として読み込みたい最初の行
                "end_row": 142, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2018: {
        "year": 2018,
        "input_path": INPUT_DIR / "2018" / "a00100.xls",
        "output_path": OUTPUT_DIR / "11_2018_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "H, N:P", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 124218, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 19, # 表として読み込みたい最初の行
                "end_row": 69, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 92, # 表として読み込みたい最初の行
                "end_row": 142, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2017: {
        "year": 2017,
        "input_path": INPUT_DIR / "2017" / "a00100.xls",
        "output_path": OUTPUT_DIR / "11_2017_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "H, N:P", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 124648, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 19, # 表として読み込みたい最初の行
                "end_row": 69, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 92, # 表として読み込みたい最初の行
                "end_row": 142, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2016: {
        "year": 2016,
        "input_path": INPUT_DIR / "2016" / "a00100.xls",
        "output_path": OUTPUT_DIR / "11_2016_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "H, N:P", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 125020, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 19, # 表として読み込みたい最初の行
                "end_row": 69, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 92, # 表として読み込みたい最初の行
                "end_row": 142, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2015: {
        "year": 2015,
        "input_path": INPUT_DIR / "2015" / "001.xls",
        "output_path": OUTPUT_DIR / "11_2015_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "B, G:I", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 125319, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 17, # 表として読み込みたい最初の行
                "end_row": 67, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 90, # 表として読み込みたい最初の行
                "end_row": 140, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2014: {
        "year": 2014,
        "input_path": INPUT_DIR / "2014" / "a00100.xls",
        "output_path": OUTPUT_DIR / "11_2014_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "H, N:P", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 125431, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 19, # 表として読み込みたい最初の行
                "end_row": 69, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 92, # 表として読み込みたい最初の行
                "end_row": 142, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2013: {
        "year": 2013,
        "input_path": INPUT_DIR / "2013" / "a00100.xls",
        "output_path": OUTPUT_DIR / "11_2013_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "H, N:P", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 125704, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 19, # 表として読み込みたい最初の行
                "end_row": 69, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 92, # 表として読み込みたい最初の行
                "end_row": 142, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2012: {
        "year": 2012,
        "input_path": INPUT_DIR / "2012" / "a00100.xls",
        "output_path": OUTPUT_DIR / "11_2012_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "H, N:P", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 125957, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 19, # 表として読み込みたい最初の行
                "end_row": 69, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 92, # 表として読み込みたい最初の行
                "end_row": 142, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2011: {
        "year": 2011,
        "input_path": INPUT_DIR / "2011" / "a00100.xls",
        "output_path": OUTPUT_DIR / "11_2011_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "H, N:P", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 126180, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 19, # 表として読み込みたい最初の行
                "end_row": 69, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 92, # 表として読み込みたい最初の行
                "end_row": 142, # 表として読み込みたい最後の行                   
            },
        },   
    },
    2010: {
        "year": 2010,
        "input_path": INPUT_DIR / "2010" / "10t2210.xlsx",
        "output_path": OUTPUT_DIR / "11_2010_tidy.csv",
        "sheet_name": "第１表",
        "header": None,
        "usecols": "B, G:I", # 表として読み込みたい列の範囲
        "col_names": ["年齢", "男女計", "男", "女"],
        "check_val": 126382, # 日本人合計値
        "sheet": {
            "under50": {
                "start_row": 17, # 表として読み込みたい最初の行
                "end_row": 67, # 表として読み込みたい最後の行                              
            },
            "over50": {
                "start_row": 90, # 表として読み込みたい最初の行
                "end_row": 140, # 表として読み込みたい最後の行                   
            },
        },   
    },

}


# ======================== 関数定義 ========================
def add_age_suffix(df, col_name="年齢"):
    """
    年齢列の値が「総数」でなく、かつ「歳」が含まれていない場合に「歳」を付与する
    """
    df[col_name] = df[col_name].astype(str)
    mask = (~df[col_name].str.contains("歳")) & (df[col_name] != "総数")
    df.loc[mask, col_name] = df.loc[mask, col_name] + "歳"
    return df


def process_one(target_year):
    """
    1年分の設定を受け取りtidy化をして保存までを行う
    """      
    # ======================== 読み込み ========================
    year        = CONFIG[target_year]["year"]
    input_path  = CONFIG[target_year]["input_path"]
    output_path = CONFIG[target_year]["output_path"]
    sheet_name  = CONFIG[target_year]["sheet_name"]
    header      = CONFIG[target_year]["header"]
    usecols     = CONFIG[target_year]["usecols"]
    names       = CONFIG[target_year]["col_names"]
    check_val   = CONFIG[target_year]["check_val"]
    skiprows_under50 = CONFIG[target_year]["sheet"]["under50"]["start_row"] - 1               # 上から飛ばす行数
    nrows_under50    = CONFIG[target_year]["sheet"]["under50"]["end_row"] - skiprows_under50  # 使用する行数
    skiprows_over50  = CONFIG[target_year]["sheet"]["over50"]["start_row"] - 1                # 上から飛ばす行数
    nrows_over50     = CONFIG[target_year]["sheet"]["over50"]["end_row"] - skiprows_over50    # 使用する行数

    df_under50 = pd.read_excel(io=input_path, sheet_name=sheet_name, header=header, usecols=usecols, names=names, skiprows=skiprows_under50, nrows = nrows_under50)
    df_over50 = pd.read_excel(io=input_path, sheet_name=sheet_name, header=header, usecols=usecols, names=names, skiprows=skiprows_over50, nrows = nrows_over50)


    # ======================== dfの結合と細かい正規化 ========================
    # 2つのdfを縦に結合
    df = pd.concat([df_under50, df_over50], ignore_index=True)

    # 年齢列の値の余計なスペースを取り除く
    df["年齢"] = df["年齢"].astype(str).str.replace(r'[\s　]+', '', regex=True)

    # 関数呼び出し: 指定した列が「総数」でなく、かつ「歳」が含まれていない場合に「歳」を付与する。
    df = add_age_suffix(df)


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
    tidy["年"] = year

    # 列順整理
    tidy = tidy[["年", "区分", "性別", "年齢", "人口_千人"]]

    # 数値チェック
    diff = check_val - tidy["人口_千人"].sum()
    print(f"{year}年: 差分{diff:.6f}")


    # ======================== 保存 ======================== 
    tidy.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"保存完了: {year}年")


# ======================== 実行 ========================
if __name__ == "__main__":
    for y in CONFIG.keys():
        process_one(target_year=y)




