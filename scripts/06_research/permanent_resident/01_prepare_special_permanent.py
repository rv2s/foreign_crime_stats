# 来日外国人以外を、特別永住者近似とそれ以外に分けて検挙人員割合を算出するコード

# ======================== ライブラリインポート ========================
from pathlib import Path
import re
import unicodedata

import pandas as pd


# ======================== パス設定 ========================
BASE_PATH = Path(__file__).resolve().parents[3] / "data"
TIDY_PATH = BASE_PATH / "01_tidy"
ESTIMATED_PATH = BASE_PATH / "03_estimated"
INTEGRATED_PATH = BASE_PATH / "04_integrated"
WORK_PATH = BASE_PATH / "99_work"
OUTPUT_DIR = BASE_PATH / "06_research" / "permanent_resident" / "02_intermediate"

input_foreign_arrests = TIDY_PATH / "99_merge" / "02_検挙人員数_外国人全体_merge.csv"
input_visitor_arrests = TIDY_PATH / "99_merge" / "03_検挙人員数_来日外国人_merge.csv"
input_non_visitor_arrests_total = ESTIMATED_PATH / "04_検挙人員数_来日外国人以外_推計.csv"
input_population_total = INTEGRATED_PATH / "15_人口_統合.csv"
input_status_map = WORK_PATH / "10_人口_在留資格別" / "02_map" / "10_人口_在留資格別_マップ_在留資格.csv"
input_attribute_map = WORK_PATH / "02_検挙人員数_外国人全体" / "02_map" / "02_検挙人員数_外国人全体_マップ_属性.csv"
input_foreign_crime_map = WORK_PATH / "02_検挙人員数_外国人全体" / "02_map" / "02_検挙人員数_外国人全体_マップ_罪種.csv"
input_visitor_crime_map = WORK_PATH / "03_検挙人員数_来日外国人" / "02_map" / "03_検挙人員数_来日外国人_マップ.csv"

output_nationality_composition = OUTPUT_DIR / "01_特別永住者_国籍構成.csv"
output_proxy_arrests = OUTPUT_DIR / "02_韓国朝鮮籍_来日外国人以外_検挙人員.csv"
output_proxy_population = OUTPUT_DIR / "03_韓国朝鮮籍_来日外国人以外_人口.csv"
output_arrest_rate = OUTPUT_DIR / "04_来日外国人以外_特別永住者近似別_1万人あたり検挙人員数.csv"

TARGET_YEARS = [2021, 2022, 2023, 2024]
PROXY_LABEL = "特別永住者近似"
NON_PROXY_LABEL = "特別永住者近似以外"


# ======================== 関数定義 ========================
def normalize_text(value):
    """文字列をNFKC正規化する。"""
    if pd.isna(value):
        return pd.NA
    return unicodedata.normalize("NFKC", str(value)).strip()


def normalize_nationality(value):
    """国籍・地域名からコードや地域プレフィックスを除去する。"""
    value = normalize_text(value)
    if pd.isna(value):
        return pd.NA

    if "韓国" in value:
        return "韓国"
    if "朝鮮" in value:
        return "朝鮮"

    # 例: "02アジア  001アフガニスタン" -> "アフガニスタン"
    value = re.sub(r"^\d{2}\D+\s+\d{3}", "", value).strip()
    # 例: "001アフガニスタン" -> "アフガニスタン"
    value = re.sub(r"^\d+", "", value).strip()
    return value


def is_korea_or_chosen(series):
    """韓国・朝鮮籍かどうかを判定する。"""
    return series.fillna("").astype(str).str.contains("韓国|朝鮮", regex=True)


def is_age_under_14(value):
    """0~13歳かどうかを判定する。"""
    value = normalize_text(value)
    if pd.isna(value):
        return False
    match = re.search(r"\d+", value)
    if match is None:
        return False
    return int(match.group()) <= 13


def add_crime_combined_column(df, crime_columns):
    """罪種列を / 区切りで結合する。"""
    df = df.copy()
    df["罪種統合"] = df[crime_columns[0]].str.cat(
        [df[column] for column in crime_columns[1:]],
        sep="/",
        na_rep="",
    )
    return df


def apply_crime_map(df, input_map, crime_columns):
    """罪種マップを使って罪種を名寄せする。"""
    df = df.copy()
    df_map = pd.read_csv(input_map, encoding="utf-8-sig", keep_default_na=False)
    df = add_crime_combined_column(df, crime_columns)

    crime_dict = df_map.set_index("罪種統合")["罪種統合_名寄せ後"].to_dict()
    df["罪種統合_名寄せ後"] = df["罪種統合"].map(crime_dict)

    missing_crimes = df.loc[df["罪種統合_名寄せ後"].isna(), "罪種統合"].drop_duplicates()
    if not missing_crimes.empty:
        raise ValueError(
            "罪種マップに存在しない罪種統合があります: "
            + ", ".join(missing_crimes.astype(str).tolist())
        )

    standardized_crimes = df["罪種統合_名寄せ後"].str.split("/", expand=True)
    for i, column in enumerate(crime_columns):
        df[column] = standardized_crimes[i].replace("", pd.NA)

    return df.drop(columns=["罪種統合", "罪種統合_名寄せ後"])


def apply_attribute_map(df):
    """外国人全体検挙人員の属性を名寄せする。"""
    df = df.copy()
    df_map = pd.read_csv(input_attribute_map, encoding="utf-8-sig", keep_default_na=False)
    attr_dict = dict(zip(df_map["属性"].fillna("").astype(str), df_map["属性_名寄せ後"]))
    df["属性"] = df["属性"].fillna("").astype(str).map(attr_dict)

    missing_attributes = df.loc[df["属性"].isna(), "属性"].drop_duplicates()
    if not missing_attributes.empty:
        raise ValueError("属性マップに存在しない値があります")

    return df


def aggregate_arrests(df):
    """検挙人員を年・罪種別に集計する。"""
    group_columns = ["年", "罪種00", "罪種01"]
    return df.groupby(group_columns, as_index=False, dropna=False)["検挙人員"].sum()


def subtract_arrests(left, right, left_name, right_name):
    """同じ粒度の検挙人員を left - right で差し引く。"""
    group_columns = ["年", "罪種00", "罪種01"]
    df = pd.merge(
        left.rename(columns={"検挙人員": left_name}),
        right.rename(columns={"検挙人員": right_name}),
        on=group_columns,
        how="outer",
    )
    df[[left_name, right_name]] = df[[left_name, right_name]].fillna(0)
    df["検挙人員"] = df[left_name] - df[right_name]
    return df[group_columns + [left_name, right_name, "検挙人員"]]


def aggregate_crime_hierarchies(df, value_column):
    """罪種合計行を作る。"""
    frames = []
    for hierarchy in [[], ["罪種00"], ["罪種00", "罪種01"]]:
        group_columns = ["年", "特別永住者近似区分"] + hierarchy
        df_target = df.copy()
        if hierarchy:
            df_target = df_target.dropna(subset=hierarchy)

        df_grouped = df_target.groupby(
            group_columns,
            as_index=False,
            dropna=False,
        )[value_column].sum()

        for column in ["罪種00", "罪種01"]:
            if column not in df_grouped.columns:
                df_grouped[column] = "計"

        frames.append(df_grouped[["年", "特別永住者近似区分", "罪種00", "罪種01", value_column]])

    return pd.concat(frames, ignore_index=True)


def load_population_by_nationality_and_status():
    """国籍・地域、在留資格、年齢つきの在留外国人人口を読み込む。"""
    frames = []
    for year in TARGET_YEARS:
        input_file = TIDY_PATH / "10_人口_在留資格別" / f"10_{year}_tidy.csv"
        df = pd.read_csv(input_file, encoding="utf-8-sig")
        frames.append(df)

    df = pd.concat(frames, ignore_index=True)
    df["国籍・地域_名寄せ後"] = df["国籍・地域"].map(normalize_nationality)
    df["韓国・朝鮮籍フラグ"] = is_korea_or_chosen(df["国籍・地域_名寄せ後"])
    return df


def add_status_group(df):
    """在留資格を既存マップで名寄せする。"""
    df = df.copy()
    df_map = pd.read_csv(input_status_map, encoding="utf-8-sig", keep_default_na=False)
    status_dict = df_map.set_index("在留資格")["在留資格_名寄せ後"].to_dict()
    df["在留資格_名寄せ後"] = df["在留資格"].map(status_dict)

    missing_statuses = df.loc[df["在留資格_名寄せ後"].isna(), "在留資格"].drop_duplicates()
    if not missing_statuses.empty:
        raise ValueError(
            "在留資格マップに存在しない在留資格があります: "
            + ", ".join(missing_statuses.astype(str).tolist())
        )

    return df


# ======================== 人口: 特別永住者の国籍構成 ========================
df_population_nationality = load_population_by_nationality_and_status()

df_special_permanent = df_population_nationality[df_population_nationality["在留資格"] == "特別永住者"].copy()
df_nationality_composition = (
    df_special_permanent
    .groupby(["年", "国籍・地域_名寄せ後"], as_index=False, dropna=False)["人口"]
    .sum()
)
df_year_total = df_nationality_composition.groupby("年", as_index=False)["人口"].sum().rename(columns={"人口": "特別永住者_総人口"})
df_nationality_composition = pd.merge(df_nationality_composition, df_year_total, on="年", how="left", validate="m:1")
df_nationality_composition["構成比"] = df_nationality_composition["人口"] / df_nationality_composition["特別永住者_総人口"]
df_nationality_composition["韓国・朝鮮籍フラグ"] = is_korea_or_chosen(df_nationality_composition["国籍・地域_名寄せ後"])
df_nationality_composition = df_nationality_composition.sort_values(["年", "人口"], ascending=[True, False]).reset_index(drop=True)


# ======================== 人口: 特別永住者近似 / 近似以外 ========================
df_population_nationality = add_status_group(df_population_nationality)
df_population_non_visitor = df_population_nationality[df_population_nationality["在留資格_名寄せ後"] == "永住者等"].copy()
df_population_non_visitor = df_population_non_visitor[~df_population_non_visitor["年齢"].map(is_age_under_14)].reset_index(drop=True)

df_proxy_population = (
    df_population_non_visitor[df_population_non_visitor["韓国・朝鮮籍フラグ"]]
    .groupby("年", as_index=False)["人口"]
    .sum()
    .rename(columns={"人口": "人数"})
)
df_proxy_population["特別永住者近似区分"] = PROXY_LABEL

df_population_total = pd.read_csv(input_population_total, encoding="utf-8-sig")
df_population_total = df_population_total[
    (df_population_total["年"].isin(TARGET_YEARS))
    & (df_population_total["区分00"] == "外国人")
    & (df_population_total["区分01"] == "永住者等")
    & (df_population_total["年代"] != "0~13歳")
].copy()
df_population_total = (
    df_population_total
    .groupby("年", as_index=False)["人数"]
    .sum()
    .rename(columns={"人数": "来日外国人以外_人数"})
)

df_population_split = pd.merge(df_population_total, df_proxy_population[["年", "人数"]], on="年", how="left", validate="1:1")
df_population_split["人数"] = df_population_split["人数"].fillna(0)
df_non_proxy_population = df_population_split[["年", "来日外国人以外_人数", "人数"]].copy()
df_non_proxy_population["人数"] = df_non_proxy_population["来日外国人以外_人数"] - df_non_proxy_population["人数"]
df_non_proxy_population["特別永住者近似区分"] = NON_PROXY_LABEL
df_non_proxy_population = df_non_proxy_population[["年", "特別永住者近似区分", "人数"]]
df_proxy_population = df_proxy_population[["年", "特別永住者近似区分", "人数"]]
df_population_for_rate = pd.concat([df_proxy_population, df_non_proxy_population], ignore_index=True)


# ======================== 検挙人員: 韓国・朝鮮籍の来日外国人以外 ========================
df_foreign = pd.read_csv(input_foreign_arrests, encoding="utf-8-sig")
df_visitor = pd.read_csv(input_visitor_arrests, encoding="utf-8-sig")

df_foreign = df_foreign[df_foreign["年"].isin(TARGET_YEARS)].reset_index(drop=True)
df_visitor = df_visitor[df_visitor["年"].isin(TARGET_YEARS)].reset_index(drop=True)

df_foreign = apply_crime_map(df_foreign, input_foreign_crime_map, ["罪種00", "罪種01", "罪種02"])
df_visitor = apply_crime_map(df_visitor, input_visitor_crime_map, ["罪種00", "罪種01", "罪種02"])
df_foreign = apply_attribute_map(df_foreign)

df_foreign_proxy = df_foreign[
    (is_korea_or_chosen(df_foreign["国籍・地域"]))
    & (df_foreign["属性"] == "在日米軍関係者以外")
].reset_index(drop=True)
df_visitor_proxy = df_visitor[is_korea_or_chosen(df_visitor["国籍・地域"])].reset_index(drop=True)

df_foreign_proxy = aggregate_arrests(df_foreign_proxy)
df_visitor_proxy = aggregate_arrests(df_visitor_proxy)
df_proxy_arrests = subtract_arrests(
    left=df_foreign_proxy,
    right=df_visitor_proxy,
    left_name="韓国朝鮮籍_外国人全体",
    right_name="韓国朝鮮籍_来日外国人",
)
df_proxy_arrests["特別永住者近似区分"] = PROXY_LABEL

negative_proxy = df_proxy_arrests[df_proxy_arrests["検挙人員"] < 0]
if not negative_proxy.empty:
    raise ValueError("韓国・朝鮮籍の来日外国人以外検挙人員に負値があります")


# ======================== 検挙人員: 特別永住者近似以外 ========================
df_non_visitor_total_arrests = pd.read_csv(input_non_visitor_arrests_total, encoding="utf-8-sig")
df_non_visitor_total_arrests = df_non_visitor_total_arrests[df_non_visitor_total_arrests["年"].isin(TARGET_YEARS)].copy()
df_non_visitor_total_arrests = df_non_visitor_total_arrests.drop(columns=["罪種02"], errors="ignore")
df_non_visitor_total_arrests = aggregate_arrests(df_non_visitor_total_arrests)

df_non_proxy_arrests = subtract_arrests(
    left=df_non_visitor_total_arrests,
    right=df_proxy_arrests[["年", "罪種00", "罪種01", "検挙人員"]],
    left_name="来日外国人以外_検挙人員",
    right_name="特別永住者近似_検挙人員",
)
df_non_proxy_arrests["特別永住者近似区分"] = NON_PROXY_LABEL

negative_non_proxy = df_non_proxy_arrests[df_non_proxy_arrests["検挙人員"] < 0]
if not negative_non_proxy.empty:
    raise ValueError("特別永住者近似以外の検挙人員に負値があります")

df_arrests_for_rate = pd.concat(
    [
        df_proxy_arrests[["年", "特別永住者近似区分", "罪種00", "罪種01", "検挙人員"]],
        df_non_proxy_arrests[["年", "特別永住者近似区分", "罪種00", "罪種01", "検挙人員"]],
    ],
    ignore_index=True,
)
df_arrests_for_rate = aggregate_crime_hierarchies(df_arrests_for_rate, "検挙人員")


# ======================== 1万人あたり検挙人員数 ========================
df_rate = pd.merge(
    df_arrests_for_rate,
    df_population_for_rate,
    on=["年", "特別永住者近似区分"],
    how="left",
    validate="m:1",
)

missing_population = df_rate[df_rate["人数"].isna()][["年", "特別永住者近似区分"]].drop_duplicates()
if not missing_population.empty:
    raise ValueError(
        "人口データが存在しないキーがあります: "
        + ", ".join(f"{row.年}:{row.特別永住者近似区分}" for row in missing_population.itertuples(index=False))
    )

df_rate["検挙人員数_1万人あたり"] = df_rate["検挙人員"] / df_rate["人数"] * 10000
df_rate["区分00"] = "外国人"
df_rate["区分01"] = "来日外国人以外"
df_rate = df_rate[
    [
        "年",
        "区分00",
        "区分01",
        "特別永住者近似区分",
        "罪種00",
        "罪種01",
        "検挙人員",
        "人数",
        "検挙人員数_1万人あたり",
    ]
].sort_values(["年", "特別永住者近似区分", "罪種00", "罪種01"]).reset_index(drop=True)


# ======================== 保存 ========================
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df_nationality_composition.to_csv(output_nationality_composition, index=False, encoding="utf-8-sig")
df_proxy_arrests.to_csv(output_proxy_arrests, index=False, encoding="utf-8-sig")
df_population_for_rate.to_csv(output_proxy_population, index=False, encoding="utf-8-sig")
df_rate.to_csv(output_arrest_rate, index=False, encoding="utf-8-sig")

print(f"対象年: {min(TARGET_YEARS)}-{max(TARGET_YEARS)}")
print(f"特別永住者国籍構成: {output_nationality_composition}")
print(f"検挙人員割合: {output_arrest_rate}")
print("処理完了")
