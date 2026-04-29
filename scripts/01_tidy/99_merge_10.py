import pandas as pd
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"

TIDY_PATH = BASE_PATH / "01_tidy"
output_file = TIDY_PATH / "99_merge" / "10_人口_在留資格別_merge.csv"

CONFIG = {
    2024: {"input_file": TIDY_PATH / "10_人口_在留資格別" /"10_2024_tidy.csv", "pattern": 1},
    2023: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2023_tidy.csv", "pattern": 1},
    2022: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2022_tidy.csv", "pattern": 1},
    2021: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2021_tidy.csv", "pattern": 1},
    2020: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2020_tidy.csv", "pattern": 2},
    2019: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2019_tidy.csv", "pattern": 2},
    2018: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2018_tidy.csv", "pattern": 2},
    2017: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2017_tidy.csv", "pattern": 2},
    2016: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2016_tidy.csv", "pattern": 2},
    2015: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2015_tidy.csv", "pattern": 2},
    2014: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2014_tidy.csv", "pattern": 2},
    2013: {"input_file": TIDY_PATH / "10_人口_在留資格別" / "10_2013_tidy.csv", "pattern": 2},
}


# ======================== 関数定義 ========================
def process_year_data(target_year):
    """指定された年のファイルを読み込み、集計してDataFrameを返す。"""

    input_file = CONFIG[target_year]["input_file"]
    pattern = CONFIG[target_year]["pattern"]

    df = pd.read_csv(input_file, encoding="utf-8-sig")

    # 数値チェック
    check_val = df["人口"].sum()

    # 集計
    if pattern == 1:
        df = df.groupby(["年", "在留資格", "性別", "年齢"], as_index=False)["人口"].sum()
    elif pattern == 2:
        pass
    else:
        raise ValueError("未知のpattern: {pattern}")

    # 数値チェック
    total_val = df["人口"].sum()
    diff_val = check_val - total_val
    print(f"{target_year}: 差分{diff_val}")

    return df


# ======================== 実行 ========================
if __name__ == "__main__":
    dfs = []
    
    for y in CONFIG.keys():
        df_processed = process_year_data(y)
        dfs.append(df_processed)


    # ======================== 結合と保存 ========================
    # リスト内のdfを連結
    df_final = pd.concat(dfs, ignore_index=True)
    df_final.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"処理完了")

