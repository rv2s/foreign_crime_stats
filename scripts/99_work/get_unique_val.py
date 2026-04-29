# ユニーク値を取得するコード

# ======================== ライブラリインポート ========================
import pandas as pd
from pathlib import Path


# ======================== 関数定義 ========================
def get_unique_values(input_file, output_file, column_name):
    """
    指定されたCSVファイルから指定カラムのユニーク値を取得し、CSVファイルとして保存する関数

    Args:
        input_file (Path): 入力CSVファイルのパス
        output_file (Path): 出力CSVファイルのパス
        column_name (str): ユニーク値を取得するカラム名
    """
    input_file = Path(input_file)
    output_file = Path(output_file)

    # データ読み込み
    df = pd.read_csv(input_file)

    # ユニーク値取得
    df_unique = df[[column_name]].drop_duplicates()

    # 保存
    df_unique.to_csv(output_file, index=False, encoding="utf-8-sig")


# ======================== メイン処理 ========================
if __name__ == "__main__":
    BASE_PATH = Path(__file__).resolve().parents[2] / "data"
    TIDY_PATH = BASE_PATH / "01_tidy"
    WORK_PATH = BASE_PATH / "99_work"

    # 出国者データ(2021年以前)の滞在期間
    get_unique_values(
        input_file=TIDY_PATH / "12_出国者" / "before_2021" / "12_出国者_tidydata_2021年以前.csv",
        output_file=WORK_PATH / "12_出国者" / "before_2021" / "01_unique" / "12_出国者_滞在期間ユニーク値_2021年以前.csv",
        column_name="滞在期間"
    )

    # 出国者データ(2022年以降)の滞在期間
    get_unique_values(
        input_file=TIDY_PATH / "12_出国者" / "after_2022" / "12_出国者_tidydata_2022年以降.csv",
        output_file=WORK_PATH / "12_出国者" / "after_2022" / "01_unique" / "12_出国者_滞在期間ユニーク値_2022年以降.csv",
        column_name="滞在期間"
    )

    # 出国者データ(2022年以降)の年代
    get_unique_values(
        input_file=TIDY_PATH / "12_出国者" / "after_2022" / "12_出国者_tidydata_2022年以降.csv",
        output_file=WORK_PATH / "12_出国者" / "after_2022" / "01_unique" / "12_出国者_年代ユニーク値_2022年以降.csv",
        column_name="年代"
    )

    # 入国者データ(2021年以前・年代別)の年代
    get_unique_values(
        input_file=TIDY_PATH / "13_入国者" / "before_2021" / "年代別" / "13_入国者_tidydata_2021年以前_年代別.csv",
        output_file=WORK_PATH / "13_入国者" / "before_2021" / "01_unique" / "13_入国者_年代ユニーク値_2021年以前.csv",
        column_name="年代"
    )
    
    # 入国者データ(2022年以降)の年代
    get_unique_values(
        input_file=TIDY_PATH / "13_入国者" / "after_2022" / "13_入国者_tidydata_2022年以降.csv",
        output_file=WORK_PATH / "13_入国者" / "after_2022" / "01_unique" / "13_入国者_年代ユニーク値_2022年以降.csv",
        column_name="年代"
    )

    # 検挙人員数_日本全体 の年齢
    get_unique_values(
        input_file=TIDY_PATH / "99_merge" / "01_検挙人員数_日本全体_merge.csv",
        output_file=WORK_PATH / "01_検挙人員数_日本全体" / "01_unique" / "01_検挙人員数_日本全体_ユニーク値_年齢.csv",
        column_name="年齢層"
    )

    # 検挙人員数_外国人全体 の属性
    get_unique_values(
        input_file=TIDY_PATH / "99_merge" / "02_検挙人員数_外国人全体_merge.csv",
        output_file=WORK_PATH / "02_検挙人員数_外国人全体" / "01_unique" / "02_検挙人員数_外国人全体_ユニーク値_属性.csv",
        column_name="属性"
    )

    # 検挙人員数_在留資格別 の在留資格
    get_unique_values(
        input_file=TIDY_PATH / "99_merge" / "08_検挙人員数_在留資格別_merge.csv",
        output_file=WORK_PATH / "08_検挙人員数_在留資格別" / "01_unique" / "08_検挙人員数_在留資格別_ユニーク値_在留資格.csv",
        column_name="在留資格"
    )

    # 人口_在留資格別 の在留資格
    get_unique_values(
        input_file=TIDY_PATH / "99_merge" / "10_人口_在留資格別_merge.csv",
        output_file=WORK_PATH / "10_人口_在留資格別" / "01_unique" / "10_人口_在留資格別_ユニーク値_在留資格.csv",
        column_name="在留資格"
    )

    # 人口_在留資格別 の年齢
    get_unique_values(
        input_file=TIDY_PATH / "99_merge" / "10_人口_在留資格別_merge.csv",
        output_file=WORK_PATH / "10_人口_在留資格別" / "01_unique" / "10_人口_在留資格別_ユニーク値_年齢.csv",
        column_name="年齢"
    )

    # 人口_日本人 の年齢
    get_unique_values(
        input_file=TIDY_PATH / "99_merge" / "11_人口_日本人_merge.csv",
        output_file=WORK_PATH / "11_人口_日本人" / "01_unique" / "11_人口_日本人_ユニーク値_年齢.csv",
        column_name="年齢"
    )

    # 人口_不法残留者 の在留資格
    get_unique_values(
        input_file=TIDY_PATH / "99_merge" / "14_不法残留者_merge.csv",
        output_file=WORK_PATH / "14_不法残留者" / "01_unique" / "14_不法残留者_ユニーク値_在留資格.csv",
        column_name="在留資格"
    )

    print("処理完了")

