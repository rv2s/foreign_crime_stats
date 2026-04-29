# データの名寄せ・標準化を行うコード

# ======================== ライブラリインポート ========================
import pandas as pd
from pathlib import Path


# ======================== 関数定義 ========================
def add_crime_combined_column(df, crime_columns):
    """
    罪種カラムを / 区切りで統合した「罪種統合」列を追加する関数

    Args:
        df (pd.DataFrame): 入力データ
        crime_columns (list[str]): 罪種カラム名のリスト

    Returns:
        pd.DataFrame: 罪種統合列を追加したデータ
    """
    df = df.copy()
    df["罪種統合"] = df[crime_columns[0]].str.cat(
        [df[column] for column in crime_columns[1:]],
        sep="/",
        na_rep=""
    )
    return df


def apply_crime_map(df, input_map, crime_columns):
    """
    罪種マップを使って罪種を名寄せする関数

    Args:
        df (pd.DataFrame): 入力データ
        input_map (Path): 罪種マップCSVファイルのパス
        crime_columns (list[str]): 罪種カラム名のリスト

    Returns:
        pd.DataFrame: 罪種を名寄せしたデータ
    """
    input_map = Path(input_map)
    df = df.copy()
    df_map = pd.read_csv(input_map, encoding="utf-8-sig", keep_default_na=False)

    # get_unique_crime.py と同じロジックで罪種統合列を作成
    df = add_crime_combined_column(df, crime_columns)

    # 罪種の名寄せ
    df_dict = df_map.set_index("罪種統合")["罪種統合_名寄せ後"].to_dict()
    df["罪種統合_名寄せ後"] = df["罪種統合"].map(df_dict)

    # マップ漏れチェック
    missing_crimes = df.loc[df["罪種統合_名寄せ後"].isna(), "罪種統合"].drop_duplicates()
    if not missing_crimes.empty:
        raise ValueError(
            "罪種マップに存在しない罪種統合があります: "
            + ", ".join(missing_crimes.astype(str).tolist())
        )

    # 名寄せ後の罪種統合を罪種00~02に戻す
    standardized_crimes = df["罪種統合_名寄せ後"].str.split("/", expand=True)
    for i, column in enumerate(crime_columns):
        df[column] = standardized_crimes[i]

    return df.drop(columns=["罪種統合", "罪種統合_名寄せ後"])


def apply_column_map(df, input_map, source_column, map_source_column, map_target_column, output_column):
    """
    1列のマップを使って値を名寄せする関数

    Args:
        df (pd.DataFrame): 入力データ
        input_map (Path): マップCSVファイルのパス
        source_column (str): 入力データ側の名寄せ前カラム名
        map_source_column (str): マップ側の名寄せ前カラム名
        map_target_column (str): マップ側の名寄せ後カラム名
        output_column (str): 出力データ側のカラム名

    Returns:
        pd.DataFrame: 指定列を名寄せしたデータ
    """
    input_map = Path(input_map)
    df = df.copy()
    df_map = pd.read_csv(input_map, encoding="utf-8-sig", keep_default_na=False)

    map_key = df_map[map_source_column].fillna("").astype(str)
    df_dict = dict(zip(map_key, df_map[map_target_column]))

    source_value = df[source_column].fillna("").astype(str)
    df[output_column] = source_value.map(df_dict)

    # マップ漏れチェック
    missing_values = source_value[df[output_column].isna()].drop_duplicates()
    if not missing_values.empty:
        raise ValueError(
            f"{source_column}マップに存在しない値があります: "
            + ", ".join(missing_values.astype(str).tolist())
        )

    if output_column != source_column:
        df = df.drop(columns=[source_column])

    return df


def standardize_dataset(
    input_file,
    output_file,
    value_column,
    crime_map=None,
    column_maps=None,
    drop_columns=None
):
    """
    複数のマップを順番に適用し、名寄せ後の粒度で集計して保存する関数

    Args:
        input_file (Path): 入力CSVファイルのパス
        output_file (Path): 出力CSVファイルのパス
        value_column (str): 集計対象の値カラム名
        crime_map (dict | None): 罪種マップ設定
        column_maps (list[dict] | None): 1列マップ設定のリスト
        drop_columns (list[str] | None): 集計前に削除するカラム名のリスト
    """
    input_file = Path(input_file)
    output_file = Path(output_file)
    column_maps = column_maps or []
    drop_columns = drop_columns or []

    df = pd.read_csv(input_file, encoding="utf-8-sig")
    check_val = df[value_column].sum()

    if crime_map is not None:
        df = apply_crime_map(
            df=df,
            input_map=crime_map["input_map"],
            crime_columns=crime_map["crime_columns"]
        )

    for column_map in column_maps:
        df = apply_column_map(
            df=df,
            input_map=column_map["input_map"],
            source_column=column_map["source_column"],
            map_source_column=column_map["map_source_column"],
            map_target_column=column_map["map_target_column"],
            output_column=column_map["output_column"]
        )

    df = df.drop(columns=drop_columns, errors="ignore")

    # 必要列で集計 ※ 名寄せ前の粒度でなく名寄せ後の粒度で行を削減する
    group_columns = [column for column in df.columns if column != value_column]
    df = df.groupby(group_columns, as_index=False, dropna=False)[value_column].sum()

    # 数値チェック
    total_val = df[value_column].sum()
    print(f"差分: {check_val - total_val:.6f}")

    # 保存
    df.to_csv(output_file, index=False, encoding="utf-8-sig")


# ======================== メイン処理 ========================
if __name__ == "__main__":
    BASE_PATH = Path(__file__).resolve().parents[2] / "data"
    TIDY_PATH = BASE_PATH / "01_tidy"
    WORK_PATH = BASE_PATH / "99_work"
    STANDARDIZED_PATH = BASE_PATH / "02_standardized"

    # 検挙人員数_日本全体の標準化
    standardize_dataset(
        input_file=TIDY_PATH / "99_merge" / "01_検挙人員数_日本全体_merge.csv",
        output_file=STANDARDIZED_PATH / "01_検挙人員数_日本全体_名寄せ後.csv",
        value_column="検挙人員",
        crime_map={
            "input_map": WORK_PATH / "01_検挙人員数_日本全体" / "02_map" / "01_検挙人員数_日本全体_マップ_罪種.csv",
            "crime_columns": ["罪種00", "罪種01", "罪種02"]
        },
        column_maps=[
            {
                "input_map": WORK_PATH / "01_検挙人員数_日本全体" / "02_map" / "01_検挙人員数_日本全体_マップ_年齢.csv",
                "source_column": "年齢層",
                "map_source_column": "年齢層",
                "map_target_column": "年代",
                "output_column": "年代"
            }
        ]
    )

    # 検挙人員数_外国人全体の標準化
    standardize_dataset(
        input_file=TIDY_PATH / "99_merge" / "02_検挙人員数_外国人全体_merge.csv",
        output_file=STANDARDIZED_PATH / "02_検挙人員数_外国人全体_名寄せ後.csv",
        value_column="検挙人員",
        crime_map={
            "input_map": WORK_PATH / "02_検挙人員数_外国人全体" / "02_map" / "02_検挙人員数_外国人全体_マップ_罪種.csv",
            "crime_columns": ["罪種00", "罪種01", "罪種02"]
        },
        column_maps=[
            {
                "input_map": WORK_PATH / "02_検挙人員数_外国人全体" / "02_map" / "02_検挙人員数_外国人全体_マップ_属性.csv",
                "source_column": "属性",
                "map_source_column": "属性",
                "map_target_column": "属性_名寄せ後",
                "output_column": "属性"
            }
        ],
        drop_columns=["州", "国籍・地域"]
    )

    # 検挙人員数_来日外国人全体の標準化
    standardize_dataset(
        input_file=TIDY_PATH / "99_merge" / "03_検挙人員数_来日外国人_merge.csv",
        output_file=STANDARDIZED_PATH / "03_検挙人員数_来日外国人_名寄せ後.csv",
        value_column="検挙人員",
        crime_map={
            "input_map": WORK_PATH / "03_検挙人員数_来日外国人" / "02_map" / "03_検挙人員数_来日外国人_マップ.csv",
            "crime_columns": ["罪種00", "罪種01", "罪種02"]
        },
        drop_columns=["州", "国籍・地域"]
    )

    # 検挙人員数_在留資格別の標準化
    standardize_dataset(
        input_file=TIDY_PATH / "99_merge" / "08_検挙人員数_在留資格別_merge.csv",
        output_file=STANDARDIZED_PATH / "08_検挙人員数_在留資格別_名寄せ後.csv",
        value_column="検挙人員",
        crime_map={
            "input_map": WORK_PATH / "08_検挙人員数_在留資格別" / "02_map" / "08_検挙人員数_在留資格別_マップ_罪種.csv",
            "crime_columns": ["罪種00", "罪種01", "罪種02"]
        },
        column_maps=[
            {
                "input_map": WORK_PATH / "08_検挙人員数_在留資格別" / "02_map" / "08_検挙人員数_在留資格別_マップ_在留資格.csv",
                "source_column": "在留資格",
                "map_source_column": "在留資格",
                "map_target_column": "在留資格_名寄せ後",
                "output_column": "在留資格"
            }
        ],
        drop_columns=["正規・非正規区分", "正規・非正規詳細"]
    )

    # 人口_在留資格別の標準化
    standardize_dataset(
        input_file=TIDY_PATH / "99_merge" / "10_人口_在留資格別_merge.csv",
        output_file=STANDARDIZED_PATH / "10_人口_在留資格別_名寄せ後.csv",
        value_column="人口",
        column_maps=[
            {
                "input_map": WORK_PATH / "10_人口_在留資格別" / "02_map" / "10_人口_在留資格別_マップ_在留資格.csv",
                "source_column": "在留資格",
                "map_source_column": "在留資格",
                "map_target_column": "在留資格_名寄せ後",
                "output_column": "在留資格"
            },
            {
                "input_map": WORK_PATH / "10_人口_在留資格別" / "02_map" / "10_人口_在留資格別_マップ_年齢.csv",
                "source_column": "年齢",
                "map_source_column": "年齢",
                "map_target_column": "年代",
                "output_column": "年代"
            }
        ],
        drop_columns=["性別"]
    )

    # 人口_日本人の標準化
    standardize_dataset(
        input_file=TIDY_PATH / "99_merge" / "11_人口_日本人_merge.csv",
        output_file=STANDARDIZED_PATH / "11_人口_日本人_名寄せ後.csv",
        value_column="人口_千人",
        column_maps=[
            {
                "input_map": WORK_PATH / "11_人口_日本人" / "02_map" / "11_人口_日本人_マップ_年齢.csv",
                "source_column": "年齢",
                "map_source_column": "年齢",
                "map_target_column": "年代",
                "output_column": "年代"
            }
        ],
        drop_columns=["区分", "性別"]
    )

    # 不法残留者の標準化
    standardize_dataset(
        input_file=TIDY_PATH / "99_merge" / "14_不法残留者_merge.csv",
        output_file=STANDARDIZED_PATH / "14_不法残留者_名寄せ後.csv",
        value_column="人数",
        column_maps=[
            {
                "input_map": WORK_PATH / "14_不法残留者" / "02_map" / "14_不法残留者_マップ_在留資格.csv",
                "source_column": "在留資格",
                "map_source_column": "在留資格",
                "map_target_column": "在留資格_名寄せ後",
                "output_column": "在留資格"
            }
        ],
        drop_columns=["国籍・地域"]
    )

    print("処理完了")
