# 罪種ユニーク値を取得するコード

# ======================== ライブラリインポート ========================
import pandas as pd
from pathlib import Path


# ======================== 関数定義 ========================
def get_unique_crimes(input_file, output_file, crime_columns):
    """
    指定されたCSVファイルから罪種カラムのユニークな組み合わせを取得し、CSVファイルとして保存する関数

    Args:
        input_file (Path): 入力CSVファイルのパス
        output_file (Path): 出力CSVファイルのパス
        crime_columns (list[str]): 罪種カラム名のリスト
    """
    input_file = Path(input_file)
    output_file = Path(output_file)

    # データ読み込み
    df = pd.read_csv(input_file, encoding="utf-8-sig")

    # 罪種列だけを抜き出し、ユニークな組み合わせを取得
    df_crimes = df[crime_columns].drop_duplicates()

    # 罪種列を統合(/区切り)
    df_crimes["罪種統合"] = df_crimes[crime_columns[0]].str.cat(
        [df_crimes[column] for column in crime_columns[1:]],
        sep="/",
        na_rep=""
    )

    # 罪種統合列のみに絞る
    df_crimes = df_crimes[["罪種統合"]]

    # 保存
    df_crimes.to_csv(output_file, index=False, encoding="utf-8-sig")


# ======================== メイン処理 ========================
if __name__ == "__main__":
    BASE_PATH = Path(__file__).resolve().parents[2] / "data"
    TIDY_PATH = BASE_PATH / "01_tidy"
    WORK_PATH = BASE_PATH / "99_work"

    # 検挙人員数_日本全体の罪種ユニーク値取得
    get_unique_crimes(
        input_file=TIDY_PATH / "99_merge" / "01_検挙人員数_日本全体_merge.csv",
        output_file=WORK_PATH / "01_検挙人員数_日本全体" / "01_unique" / "01_検挙人員数_日本全体_ユニーク値_罪種.csv",
        crime_columns=["罪種00", "罪種01", "罪種02"]
    )

    # 検挙人員数_外国人全体の罪種ユニーク値取得
    get_unique_crimes(
        input_file=TIDY_PATH / "99_merge" / "02_検挙人員数_外国人全体_merge.csv",
        output_file=WORK_PATH / "02_検挙人員数_外国人全体" / "01_unique" / "02_検挙人員数_外国人全体_ユニーク値_罪種.csv",
        crime_columns=["罪種00", "罪種01", "罪種02"]
    )

    # 検挙人員数_来日外国人全体の罪種ユニーク値取得
    get_unique_crimes(
        input_file=TIDY_PATH / "99_merge" / "03_検挙人員数_来日外国人_merge.csv",
        output_file=WORK_PATH / "03_検挙人員数_来日外国人" / "01_unique" /  "03_検挙人員数_来日外国人_ユニーク値_罪種.csv",
        crime_columns=["罪種00", "罪種01", "罪種02"]
    )

    # 検挙人員数_在留資格別の罪種ユニーク値取得
    get_unique_crimes(
        input_file=TIDY_PATH / "99_merge" / "08_検挙人員数_在留資格別_merge.csv",
        output_file=WORK_PATH / "08_検挙人員数_在留資格別" / "01_unique" / "08_検挙人員数_在留資格別_ユニーク値_罪種.csv",
        crime_columns=["罪種00", "罪種01", "罪種02"]
    )

    print("処理完了")


