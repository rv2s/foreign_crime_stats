# 実際の検挙人員数を年齢調整後の推定検挙人員数で割り、日本人基準の倍率も付与するコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_arrests = BASE_PATH / "04_integrated" / "09_検挙人員数_統合.csv"
input_expected = BASE_PATH / "05_analytics" / "intermediate" / "32_推定検挙人員.csv"
output_file = BASE_PATH / "05_analytics" / "33_対推定検挙人員及び年齢調整後対日本人倍率.csv"

df_arrests = pd.read_csv(input_arrests, encoding="utf-8-sig")
df_expected = pd.read_csv(input_expected, encoding="utf-8-sig")


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


# ======================== 処理: 対推定値倍率算出 ========================
key_columns = ["年", "区分00", "区分01", "在留資格", "罪種00", "罪種01"]
df_arrests = aggregate_hierarchies(
    df=df_arrests,
    value_column="検挙人員",
    dimensions=ARREST_DIMENSIONS,
    hierarchy_columns=ARREST_HIERARCHIES,
)

df = pd.merge(
    left=df_expected,
    right=df_arrests,
    on=key_columns,
    how="left",
    validate="1:1",
)

df["検挙人員"] = df["検挙人員"].fillna(0)
df["対推定値倍率"] = df["検挙人員"] / df["推定検挙人員"]

df_japanese = df[df["区分00"] == "日本人"][
    ["年", "罪種00", "罪種01", "対推定値倍率"]
].rename(columns={"対推定値倍率": "日本人_対推定値倍率"})

df = pd.merge(
    left=df,
    right=df_japanese,
    on=["年", "罪種00", "罪種01"],
    how="left",
    validate="m:1",
)

df["対日本人倍率_年齢調整後"] = df["対推定値倍率"] / df["日本人_対推定値倍率"]

df = df[
    key_columns
    + [
        "検挙人員",
        "推定検挙人員",
        "対推定値倍率",
        "日本人_対推定値倍率",
        "対日本人倍率_年齢調整後",
    ]
]


# ======================== 保存 ========================
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
