# 来日外国人以外の国籍別検挙人員割合を算出するコード

# ======================== ライブラリインポート ========================
from pathlib import Path
import re
import unicodedata

import pandas as pd


# ======================== パス設定 ========================
BASE_PATH = Path(__file__).resolve().parents[3] / "data"
TIDY_PATH = BASE_PATH / "01_tidy"
WORK_PATH = BASE_PATH / "99_work"
OUTPUT_DIR = BASE_PATH / "06_research" / "non_visitor_nationality" / "01_tidy"

input_foreign_arrests = TIDY_PATH / "99_merge" / "02_検挙人員数_外国人全体_merge.csv"
input_visitor_arrests = TIDY_PATH / "99_merge" / "03_検挙人員数_来日外国人_merge.csv"
input_status_map = WORK_PATH / "10_人口_在留資格別" / "02_map" / "10_人口_在留資格別_マップ_在留資格.csv"
input_attribute_map = WORK_PATH / "02_検挙人員数_外国人全体" / "02_map" / "02_検挙人員数_外国人全体_マップ_属性.csv"
input_foreign_crime_map = WORK_PATH / "02_検挙人員数_外国人全体" / "02_map" / "02_検挙人員数_外国人全体_マップ_罪種.csv"
input_visitor_crime_map = WORK_PATH / "03_検挙人員数_来日外国人" / "02_map" / "03_検挙人員数_来日外国人_マップ.csv"

output_arrests = OUTPUT_DIR / "01_来日外国人以外_国籍別_検挙人員.csv"
output_population = OUTPUT_DIR / "02_来日外国人以外_国籍別_人口.csv"
output_arrest_rate = OUTPUT_DIR / "03_来日外国人以外_国籍別_1万人あたり検挙人員数.csv"

TARGET_YEARS = list(range(2021, 2025))
OTHER_NATIONALITY = "その他"


# ======================== 関数定義 ========================
def normalize_text(value):
    """文字列をNFKC正規化する。"""
    if pd.isna(value):
        return pd.NA
    return unicodedata.normalize("NFKC", str(value)).strip()


def normalize_nationality(value):
    """国籍・地域名を検挙人員データの国籍区分に寄せる。"""
    value = normalize_text(value)
    if pd.isna(value):
        return pd.NA

    # 例: "02アジア  001アフガニスタン" -> "アフガニスタン"
    value = re.sub(r"^\d{2}\D+?\s*\d{3}", "", value).strip()
    # 例: "001アフガニスタン" -> "アフガニスタン"
    value = re.sub(r"^\d+", "", value).strip()
    value = value.strip("()（）")

    if "韓国" in value or "朝鮮" in value:
        return "韓国・朝鮮"
    if value == "米国":
        return "アメリカ"
    if value == "英国":
        return "イギリス"
    return value


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

    if df["属性"].isna().any():
        raise ValueError("属性マップに存在しない値があります")

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


def aggregate_arrests(df):
    """検挙人員を年・国籍・罪種別に集計する。"""
    group_columns = ["年", "国籍・地域", "罪種00", "罪種01"]
    return df.groupby(group_columns, as_index=False, dropna=False)["検挙人員"].sum()


def subtract_arrests(left, right):
    """同じ粒度の検挙人員を left - right で差し引く。"""
    group_columns = ["年", "国籍・地域", "罪種00", "罪種01"]
    df = pd.merge(
        left.rename(columns={"検挙人員": "外国人全体_在日米軍関係者以外"}),
        right.rename(columns={"検挙人員": "来日外国人"}),
        on=group_columns,
        how="outer",
    )
    df[["外国人全体_在日米軍関係者以外", "来日外国人"]] = df[
        ["外国人全体_在日米軍関係者以外", "来日外国人"]
    ].fillna(0)
    df["検挙人員"] = df["外国人全体_在日米軍関係者以外"] - df["来日外国人"]
    return df[group_columns + ["外国人全体_在日米軍関係者以外", "来日外国人", "検挙人員"]]


def aggregate_crime_hierarchies(df, value_column):
    """罪種合計行を作る。"""
    frames = []
    for hierarchy in [[], ["罪種00"], ["罪種00", "罪種01"]]:
        group_columns = ["年", "国籍・地域"] + hierarchy
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

        frames.append(df_grouped[["年", "国籍・地域", "罪種00", "罪種01", value_column]])

    return pd.concat(frames, ignore_index=True)


def load_population_by_nationality_and_status():
    """国籍・地域、在留資格、年齢つきの在留外国人人口を読み込む。"""
    frames = []
    for year in TARGET_YEARS:
        input_file = TIDY_PATH / "10_人口_在留資格別" / f"10_{year}_tidy.csv"
        df = pd.read_csv(input_file, encoding="utf-8-sig")
        frames.append(df)

    df = pd.concat(frames, ignore_index=True)
    df["国籍・地域"] = df["国籍・地域"].map(normalize_nationality)
    return df


def add_other_population(df_population, explicit_nationalities):
    """検挙人員データの「その他」に対応する人口を作る。"""
    df_explicit = df_population[df_population["国籍・地域"].isin(explicit_nationalities)].copy()
    df_other = df_population[~df_population["国籍・地域"].isin(explicit_nationalities)].copy()
    df_other["国籍・地域"] = OTHER_NATIONALITY
    return pd.concat([df_explicit, df_other], ignore_index=True)


# ======================== 検挙人員: 来日外国人以外を国籍別に算出 ========================
df_foreign = pd.read_csv(input_foreign_arrests, encoding="utf-8-sig")
df_visitor = pd.read_csv(input_visitor_arrests, encoding="utf-8-sig")

df_foreign = df_foreign[df_foreign["年"].isin(TARGET_YEARS)].reset_index(drop=True)
df_visitor = df_visitor[df_visitor["年"].isin(TARGET_YEARS)].reset_index(drop=True)

df_foreign = apply_crime_map(df_foreign, input_foreign_crime_map, ["罪種00", "罪種01", "罪種02"])
df_visitor = apply_crime_map(df_visitor, input_visitor_crime_map, ["罪種00", "罪種01", "罪種02"])
df_foreign = apply_attribute_map(df_foreign)

df_foreign["国籍・地域"] = df_foreign["国籍・地域"].map(normalize_nationality)
df_visitor["国籍・地域"] = df_visitor["国籍・地域"].map(normalize_nationality)
df_foreign["国籍・地域"] = df_foreign["国籍・地域"].fillna(OTHER_NATIONALITY).replace("", OTHER_NATIONALITY)
df_visitor["国籍・地域"] = df_visitor["国籍・地域"].fillna(OTHER_NATIONALITY).replace("", OTHER_NATIONALITY)

df_foreign = df_foreign[df_foreign["属性"] == "在日米軍関係者以外"].reset_index(drop=True)
df_foreign = aggregate_arrests(df_foreign)
df_visitor = aggregate_arrests(df_visitor)

df_arrests = subtract_arrests(df_foreign, df_visitor)

negative_arrests = df_arrests[df_arrests["検挙人員"] < 0]
if not negative_arrests.empty:
    raise ValueError("来日外国人以外の国籍別検挙人員に負値があります")

df_arrests_for_rate = aggregate_crime_hierarchies(
    df_arrests[["年", "国籍・地域", "罪種00", "罪種01", "検挙人員"]],
    "検挙人員",
)


# ======================== 人口: 来日外国人以外を国籍別に算出 ========================
df_population = load_population_by_nationality_and_status()
df_population = add_status_group(df_population)
df_population = df_population[df_population["在留資格_名寄せ後"] == "永住者等"].copy()
df_population = df_population[~df_population["年齢"].map(is_age_under_14)].reset_index(drop=True)

explicit_nationalities = set(df_arrests.loc[df_arrests["国籍・地域"] != OTHER_NATIONALITY, "国籍・地域"])
df_population = add_other_population(df_population, explicit_nationalities)

df_population = (
    df_population
    .groupby(["年", "国籍・地域"], as_index=False, dropna=False)["人口"]
    .sum()
    .rename(columns={"人口": "人数"})
)


# ======================== 1万人あたり検挙人員数 ========================
df_rate = pd.merge(
    df_arrests_for_rate,
    df_population,
    on=["年", "国籍・地域"],
    how="left",
    validate="m:1",
)

missing_population = df_rate[df_rate["人数"].isna()][["年", "国籍・地域"]].drop_duplicates()
if not missing_population.empty:
    raise ValueError(
        "人口データが存在しないキーがあります: "
        + ", ".join(f"{row.年}:{row._1}" for row in missing_population.itertuples(index=False))
    )

df_rate["検挙人員数_1万人あたり"] = df_rate["検挙人員"] / df_rate["人数"] * 10000
df_rate["区分00"] = "外国人"
df_rate["区分01"] = "来日外国人以外"
df_rate = df_rate[
    [
        "年",
        "区分00",
        "区分01",
        "国籍・地域",
        "罪種00",
        "罪種01",
        "検挙人員",
        "人数",
        "検挙人員数_1万人あたり",
    ]
].sort_values(["年", "国籍・地域", "罪種00", "罪種01"]).reset_index(drop=True)


# ======================== 保存 ========================
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df_arrests.to_csv(output_arrests, index=False, encoding="utf-8-sig")
df_population.to_csv(output_population, index=False, encoding="utf-8-sig")
df_rate.to_csv(output_arrest_rate, index=False, encoding="utf-8-sig")

print(f"対象年: {min(TARGET_YEARS)}-{max(TARGET_YEARS)}")
print(f"検挙人員: {output_arrests}")
print(f"人口: {output_population}")
print(f"検挙人員割合: {output_arrest_rate}")
print("処理完了")
