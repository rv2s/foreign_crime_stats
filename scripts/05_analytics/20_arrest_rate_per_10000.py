# 人口に対する検挙人員数を1万人あたりで算出し、日本人基準の倍率も付与するコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_arrests = BASE_PATH / "04_integrated" / "09_検挙人員数_統合.csv"
input_population = BASE_PATH / "04_integrated" / "15_人口_統合.csv"
output_file = BASE_PATH / "05_analytics" / "20_1万人あたり検挙人員数及び対日本人倍率.csv"

df_arrests = pd.read_csv(input_arrests, encoding="utf-8-sig")
df_population = pd.read_csv(input_population, encoding="utf-8-sig")


def aggregate_hierarchies(
    df: pd.DataFrame,
    value_column: str,
    dimensions: list[str],
    hierarchy_columns: list[list[str]],
) -> pd.DataFrame:
    """指定した階層ごとに集計し、集計対象外の列を「計」にする。"""
    frames = []
    for hierarchy in hierarchy_columns:
        group_columns = ["年"] + hierarchy
        df_target = df.copy()
        if hierarchy:
            df_target = df_target.dropna(subset=hierarchy)

        df_grouped = df_target.groupby(
            group_columns,
            as_index=False,
            dropna=False,
        )[value_column].sum()

        for column in dimensions:
            if column not in df_grouped.columns:
                df_grouped[column] = "計"

        frames.append(df_grouped[["年"] + dimensions + [value_column]])

    return pd.concat(frames, ignore_index=True)


ARREST_DIMENSIONS = ["区分00", "区分01", "在留資格", "罪種00", "罪種01"]
ARREST_HIERARCHIES = [
    [],
    ["罪種00"],
    ["罪種00", "罪種01"],
    ["区分00"],
    ["区分00", "罪種00"],
    ["区分00", "罪種00", "罪種01"],
    ["区分00", "区分01"],
    ["区分00", "区分01", "罪種00"],
    ["区分00", "区分01", "罪種00", "罪種01"],
    ["区分00", "区分01", "在留資格"],
    ["区分00", "区分01", "在留資格", "罪種00"],
    ["区分00", "区分01", "在留資格", "罪種00", "罪種01"],
]
POPULATION_DIMENSIONS = ["区分00", "区分01", "在留資格"]
POPULATION_HIERARCHIES = [
    [],
    ["区分00"],
    ["区分00", "区分01"],
    ["区分00", "区分01", "在留資格"],
]


# ======================== 処理: 人口データと検挙人員データを階層別に集計 ========================
# 旧 foreigners_crimes の 20_inte.py と同じく、刑事責任年齢未満に相当する0~13歳は母数から外す。
df_population = df_population[df_population["年代"] != "0~13歳"].reset_index(drop=True)

df_arrests = aggregate_hierarchies(
    df=df_arrests,
    value_column="検挙人員",
    dimensions=ARREST_DIMENSIONS,
    hierarchy_columns=ARREST_HIERARCHIES,
)
df_population = aggregate_hierarchies(
    df=df_population,
    value_column="人数",
    dimensions=POPULATION_DIMENSIONS,
    hierarchy_columns=POPULATION_HIERARCHIES,
)


# ======================== 処理: 1万人あたり検挙人員数算出 ========================
key_columns = ["年", "区分00", "区分01", "在留資格"]
df = pd.merge(
    left=df_arrests,
    right=df_population,
    on=key_columns,
    how="left",
    validate="m:1",
)

missing_population = df[df["人数"].isna()][key_columns].drop_duplicates()
if not missing_population.empty:
    raise ValueError(
        "人口データが存在しないキーがあります: "
        + ", ".join(
            f"{row.年}:{row.区分00}:{row.区分01}:{row.在留資格}"
            for row in missing_population.itertuples(index=False)
        )
    )

df["検挙人員数_1万人あたり"] = df["検挙人員"] / df["人数"] * 10000

df_japanese = df[df["区分00"] == "日本人"][
    ["年", "罪種00", "罪種01", "検挙人員数_1万人あたり"]
].rename(columns={"検挙人員数_1万人あたり": "日本人_検挙人員数_1万人あたり"})

df = pd.merge(
    left=df,
    right=df_japanese,
    on=["年", "罪種00", "罪種01"],
    how="left",
    validate="m:1",
)

df["対日本人倍率"] = df["検挙人員数_1万人あたり"] / df["日本人_検挙人員数_1万人あたり"]

df = df[
    [
        "年",
        "区分00",
        "区分01",
        "在留資格",
        "罪種00",
        "罪種01",
        "検挙人員",
        "人数",
        "検挙人員数_1万人あたり",
        "日本人_検挙人員数_1万人あたり",
        "対日本人倍率",
    ]
]


# ======================== 保存 ========================
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
