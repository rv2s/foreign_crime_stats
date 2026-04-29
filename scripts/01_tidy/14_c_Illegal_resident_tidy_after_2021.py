# 2021~2024年の不法残留者のデータをtidy化するコード

print("処理開始")
# ======================================== ライブラリインポート ========================================
import pandas as pd
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"


# ======================================== 基本情報 ========================================
INPUT_DIR = BASE_PATH / "00_raw" / "14_不法残留者"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "14_不法残留者"

CONFIG = {
    2024: {
        "year": 2024,
        "input_file": INPUT_DIR / "2024"/ "001425985.xlsx",
        "output_file": OUTPUT_DIR / "14_2024_tidy.csv",
        "sheet_name": "第２図、第２表",
        "start_row": 30,
        "end_row": 43,
        "usecols": "B:O",
        "header": None,
        "type": "h2",
    },
    2023: {
        "year": 2023,
        "input_file": INPUT_DIR / "2023"/ "001403959.xlsx",
        "output_file": OUTPUT_DIR / "14_2023_tidy.csv",
        "sheet_name": "第3表",
        "start_row": 3,
        "end_row": 19,
        "usecols": "B:O",
        "header": None,
        "type": "h5",
    },
    2022: {
        "year": 2022,
        "input_file": INPUT_DIR / "2022"/ "001381740.xlsx",
        "output_file": OUTPUT_DIR / "14_2022_tidy.csv",
        "sheet_name": "第３表",
        "start_row": 3,
        "end_row": 19,
        "usecols": "B:O",
        "header": None,
        "type": "h5",
    },
    2021: {
        "year": 2021,
        "input_file": INPUT_DIR / "2018to2021"/ "001356693.xlsx",
        "output_file": OUTPUT_DIR / "14_2021_tidy.csv",
        "sheet_name": "第３表",
        "start_row": 3,
        "end_row": 19,
        "usecols": "B:O",
        "header": None,
        "type": "h5",
    },
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
    start_row   = CONFIG[target_year]["start_row"]
    end_row     = CONFIG[target_year]["end_row"]
    usecols     = CONFIG[target_year]["usecols"]
    header      = CONFIG[target_year]["header"]
    type        = CONFIG[target_year]["type"]

    skiprows = start_row - 1    # 上から飛ばす行数
    nrows = end_row - skiprows  # 使用する行数

    df = pd.read_excel(io=input_file, sheet_name=sheet_name, skiprows=skiprows, nrows=nrows, usecols=usecols, header=header)


    # ======================================== メイン処理 ========================================
    print(f"{year}年: 処理開始")

    # ======== ヘッダーを1行に ========
    if type == "h2":
        header_df = df.iloc[:2] # 先頭2行を取得
        df = df.iloc[2:].copy().reset_index(drop=True) # 本体(df)の2行目以降を切り出し

    elif type == "h5":
        header_df = df.iloc[:5] # 先頭5行を取得
        df = df.iloc[5:].copy().reset_index(drop=True) # 本体(df)の5行目以降を切り出し

    else:
        print("想定外のtypeです")

    filled_header = header_df.ffill() # 上から埋める
    new_header = filled_header.iloc[-1] # 一番下の行だけ取得(ヘッダーにする)
    df.columns = new_header # 新しいヘッダーをセットする


    # 正規化
    df.columns = df.columns.str.replace("\n", "", regex=False) # カラム名の改行コード(\n)を空文字に置換
    df.columns = df.columns.str.replace(r"[ 　]", "", regex=True)
    df = df.replace(r"[ 　]", "", regex=True) # DataFrame全体の全角・半角スペースを削除
    df.columns = df.columns.str.normalize("NFKC") # カラムの正規化
    df["国籍・地域"] = df["国籍・地域"].str.normalize("NFKC") # 国籍・地域列の正規化

    # 数値チェック用に「国籍・地域」列の値に「総」が含まれていて、カラムが「総数」の値を取得
    total_val = df.loc[df["国籍・地域"].str.contains("総"), "総数"].values[0]

    # 「総数」列と「技能実習」列を削除
    df = df.drop(columns=["総数", "技能実習"])

    # 「総」が含まれている行を削除
    df = df[~df["国籍・地域"].str.contains("総")].reset_index(drop=True)

    # 「国籍・地域」列を固定列としてtidy化
    tidy = df.melt(id_vars=["国籍・地域"], var_name="在留資格", value_name="人数")

    # 列の追加と並べ替え
    tidy["年"] = year # 年列の追加
    tidy = tidy[["年", "国籍・地域", "在留資格", "人数"]] # 列の並べ替え

    # 数値チェック
    check_val = tidy["人数"].sum()
    diff_val = total_val - check_val
    print(f"{year}年: 差分 {diff_val}")

    # CSV保存
    tidy.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"{year}年: 処理完了")


# ======================================== 実行 ========================================
if __name__ == "__main__":
    for y in CONFIG.keys():
        process_one(target_year=y)

print("全ての処理完了")


