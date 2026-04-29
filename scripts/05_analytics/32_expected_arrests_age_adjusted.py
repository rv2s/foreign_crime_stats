# 年代別検挙人員割合を各区分の人口構成に当てはめ、推定検挙人員を算出するコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_population = BASE_PATH / "04_integrated" / "15_人口_統合.csv"
input_age_rate = BASE_PATH / "05_analytics" / "intermediate" / "31_年代別検挙人員割合.csv"
output_file = BASE_PATH / "05_analytics" / "intermediate" / "32_推定検挙人員.csv"

df_population = pd.read_csv(input_population, encoding="utf-8-sig")
df_age_rate = pd.read_csv(input_age_rate, encoding="utf-8-sig")


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


EXPECTED_DIMENSIONS = ["区分00", "区分01", "在留資格", "罪種00", "罪種01"]
EXPECTED_HIERARCHIES = [
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


# ======================== 処理: 推定検挙人員算出 ========================
df_population = df_population[df_population["年代"] != "0~13歳"].reset_index(drop=True)

df = pd.merge(
    left=df_population,
    right=df_age_rate[["年", "年代", "罪種00", "罪種01", "年代別検挙人員割合"]],
    on=["年", "年代"],
    how="left",
)

missing_rate = df[df["年代別検挙人員割合"].isna()][["年", "年代"]].drop_duplicates()
if not missing_rate.empty:
    raise ValueError(
        "年代別検挙人員割合が存在しない年・年代があります: "
        + ", ".join(f"{row.年}:{row.年代}" for row in missing_rate.itertuples(index=False))
    )

df["推定検挙人員"] = df["人数"] * df["年代別検挙人員割合"]

df = aggregate_hierarchies(
    df=df,
    value_column="推定検挙人員",
    dimensions=EXPECTED_DIMENSIONS,
    hierarchy_columns=EXPECTED_HIERARCHIES,
)


# ======================== 保存 ========================
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
