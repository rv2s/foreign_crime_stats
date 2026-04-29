# 不法残留者データを在留資格別・年代別に推計するコード

# ======================== ライブラリインポート ========================
from pathlib import Path
import pandas as pd


# ======================== 関数定義 ========================
def load_legal_population(base_path):
    """在留資格別人口と短期滞在の年換算人口を結合し、正規側の母集団を作る。"""
    input_population = base_path / "02_standardized" / "10_人口_在留資格別_名寄せ後.csv"
    input_entry = base_path / "03_estimated" / "13_入国者_年代別年換算人口_統合.csv"

    df_population = pd.read_csv(input_population, encoding="utf-8-sig")
    df_population = df_population.rename(columns={"人口": "人数"})

    df_entry = pd.read_csv(input_entry, encoding="utf-8-sig")
    df_entry["在留資格"] = "短期滞在"

    df = pd.concat(
        [
            df_population[["年", "在留資格", "年代", "人数"]],
            df_entry[["年", "在留資格", "年代", "人数"]],
        ],
        ignore_index=True,
    )

    return df.groupby(["年", "在留資格", "年代"], as_index=False, dropna=False)["人数"].sum()


def allocate_other_status(df_illegal, df_status_ratio):
    """2018年以降の「その他」を、定住者とその他の構成比で按分する。"""
    df_other = df_illegal[df_illegal["在留資格"] == "その他"].reset_index(drop=True)
    df_other = df_other.rename(columns={"人数": "不法残留者数"})

    df_other = pd.merge(
        left=df_other[["年", "不法残留者数"]],
        right=df_status_ratio[["年", "在留資格", "構成比_定住者とその他"]],
        on=["年"],
        how="right",
    )
    df_other["人数"] = df_other["不法残留者数"] * df_other["構成比_定住者とその他"]
    df_other = df_other[["年", "在留資格", "人数"]]

    df_illegal = df_illegal[df_illegal["在留資格"] != "その他"].reset_index(drop=True)
    df_illegal = pd.concat([df_illegal, df_other], ignore_index=True)
    return df_illegal.sort_values(["年", "在留資格"]).reset_index(drop=True)


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_illegal = BASE_PATH / "02_standardized" / "14_不法残留者_名寄せ後.csv"
input_status_ratio = (
    BASE_PATH
    / "99_work"
    / "14_不法残留者"
    / "03_parameters"
    / "14_不法残留者_定住者その他構成比_2018年以降.csv"
)
input_illegal_legal_ratio = (
    BASE_PATH
    / "99_work"
    / "14_不法残留者"
    / "03_parameters"
    / "14_不法残留者_不法対正規人数比_2018-2019平均.csv"
)
input_age_ratio = (
    BASE_PATH
    / "99_work"
    / "14_不法残留者"
    / "03_parameters"
    / "14_不法残留者_在留資格別年代構成比.csv"
)
output_file = BASE_PATH / "03_estimated" / "14_不法残留者_在留資格別年代別推計.csv"

df_illegal = pd.read_csv(input_illegal, encoding="utf-8-sig")
df_status_ratio = pd.read_csv(input_status_ratio, encoding="utf-8-sig")
df_illegal_legal_ratio = pd.read_csv(input_illegal_legal_ratio, encoding="utf-8-sig")
df_age_ratio = pd.read_csv(input_age_ratio, encoding="utf-8-sig")
df_legal = load_legal_population(BASE_PATH)


# ======================== 処理1: 2018年以降の在留資格別人数 ========================
df_illegal_a2018 = df_illegal[df_illegal["年"] >= 2018].reset_index(drop=True)
df_illegal_a2018 = allocate_other_status(df_illegal_a2018, df_status_ratio)


# ======================== 処理2: 2017年以前の在留資格別人数推計 ========================
df_illegal_b2017_macro = df_illegal[df_illegal["年"] <= 2017].reset_index(drop=True)
df_illegal_b2017_macro = df_illegal_b2017_macro.groupby(["年"], as_index=False, dropna=False)["人数"].sum()
target_years_b2017 = df_illegal_b2017_macro["年"].drop_duplicates()

df_legal_b2017 = df_legal[df_legal["年"] <= 2017].reset_index(drop=True)
df_legal_b2017 = df_legal_b2017[df_legal_b2017["年"].isin(target_years_b2017)].reset_index(drop=True)
df_legal_b2017 = df_legal_b2017.groupby(["年", "在留資格"], as_index=False, dropna=False)["人数"].sum()

df_illegal_b2017 = pd.merge(
    left=df_legal_b2017[["年", "在留資格", "人数"]],
    right=df_illegal_legal_ratio[["在留資格", "人数比_不法対正規"]],
    on=["在留資格"],
    how="inner",
)
df_illegal_b2017["不法推定人数"] = df_illegal_b2017["人数"] * df_illegal_b2017["人数比_不法対正規"]

df_correction = df_illegal_b2017.groupby(["年"], as_index=False, dropna=False)["不法推定人数"].sum()
df_correction = pd.merge(
    left=df_correction[["年", "不法推定人数"]],
    right=df_illegal_b2017_macro[["年", "人数"]],
    on=["年"],
    how="left",
)
df_correction["補正係数"] = df_correction["人数"] / df_correction["不法推定人数"]

df_illegal_b2017 = pd.merge(
    left=df_illegal_b2017[["年", "在留資格", "不法推定人数"]],
    right=df_correction[["年", "補正係数"]],
    on=["年"],
    how="left",
)
df_illegal_b2017["人数"] = df_illegal_b2017["不法推定人数"] * df_illegal_b2017["補正係数"]
df_illegal_b2017 = df_illegal_b2017[["年", "在留資格", "人数"]]


# ======================== 処理3: 年代別人数推計 ========================
df_illegal = pd.concat([df_illegal_b2017, df_illegal_a2018], ignore_index=True)
check_by_year = df_illegal.groupby("年", as_index=False, dropna=False)["人数"].sum()

df_illegal = pd.merge(
    left=df_illegal[["年", "在留資格", "人数"]],
    right=df_age_ratio[["年", "在留資格", "年代", "年代別構成比"]],
    on=["年", "在留資格"],
    how="left",
)

missing_age_ratio = df_illegal[df_illegal["年代別構成比"].isna()][["年", "在留資格"]].drop_duplicates()
if not missing_age_ratio.empty:
    raise ValueError(
        "年代別構成比が存在しない年・在留資格があります: "
        + ", ".join(
            f"{row.年}:{row.在留資格}" for row in missing_age_ratio.itertuples(index=False)
        )
    )

df_illegal["年代別人数"] = df_illegal["人数"] * df_illegal["年代別構成比"]
df = df_illegal[["年", "在留資格", "年代", "年代別人数"]].rename(columns={"年代別人数": "人数"})


# ======================== 数値チェック・保存 ========================
total_by_year = df.groupby("年", as_index=False, dropna=False)["人数"].sum()
df_check = pd.merge(check_by_year, total_by_year, on="年", suffixes=("_推計前", "_年代按分後"))
df_check["差分"] = df_check["人数_推計前"] - df_check["人数_年代按分後"]
max_abs_diff = df_check["差分"].abs().max()
print(f"最大年別差分: {max_abs_diff:.6f}")

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
