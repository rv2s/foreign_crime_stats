# 不法残留者推計に使う按分・推計パラメータを作成するコード

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
    df_a2018 = df_illegal[df_illegal["年"] >= 2018].reset_index(drop=True)

    df_other = df_a2018[df_a2018["在留資格"] == "その他"].reset_index(drop=True)
    df_other = df_other.rename(columns={"人数": "不法残留者数"})

    df_other = pd.merge(
        left=df_other[["年", "不法残留者数"]],
        right=df_status_ratio[["年", "在留資格", "構成比_定住者とその他"]],
        on=["年"],
        how="right",
    )
    df_other["人数"] = df_other["不法残留者数"] * df_other["構成比_定住者とその他"]
    df_other = df_other[["年", "在留資格", "人数"]]

    df_a2018 = df_a2018[df_a2018["在留資格"] != "その他"].reset_index(drop=True)
    df_a2018 = pd.concat([df_a2018, df_other], ignore_index=True)
    return df_a2018.sort_values(["年", "在留資格"]).reset_index(drop=True)


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_illegal = BASE_PATH / "02_standardized" / "14_不法残留者_名寄せ後.csv"
output_dir = BASE_PATH / "99_work" / "14_不法残留者" / "03_parameters"

df_illegal = pd.read_csv(input_illegal, encoding="utf-8-sig")
df_legal = load_legal_population(BASE_PATH)
output_dir.mkdir(parents=True, exist_ok=True)


# ======================== 処理1: 定住者・その他の構成比 ========================
df_status_ratio = df_legal[df_legal["年"] >= 2018].reset_index(drop=True)
df_status_ratio = df_status_ratio[df_status_ratio["在留資格"].isin(["定住者", "その他"])].reset_index(drop=True)
df_status_ratio = df_status_ratio.groupby(["年", "在留資格"], as_index=False, dropna=False)["人数"].sum()
df_status_ratio["合計人数"] = df_status_ratio.groupby("年")["人数"].transform("sum")
df_status_ratio["構成比_定住者とその他"] = df_status_ratio["人数"] / df_status_ratio["合計人数"]
df_status_ratio.to_csv(
    output_dir / "14_不法残留者_定住者その他構成比_2018年以降.csv",
    index=False,
    encoding="utf-8-sig",
)


# ======================== 処理2: 2018-2019年平均の不法対正規人数比 ========================
df_illegal_a2018 = allocate_other_status(df_illegal, df_status_ratio)

df_legal_by_status = df_legal[df_legal["年"] >= 2018].reset_index(drop=True)
df_legal_by_status = df_legal_by_status.groupby(["年", "在留資格"], as_index=False, dropna=False)["人数"].sum()
df_legal_by_status = df_legal_by_status.rename(columns={"人数": "正規人数"})

df_ratio = pd.merge(
    left=df_legal_by_status[["年", "在留資格", "正規人数"]],
    right=df_illegal_a2018[["年", "在留資格", "人数"]],
    on=["年", "在留資格"],
    how="left",
)
df_ratio["人数比_不法対正規"] = df_ratio["人数"] / df_ratio["正規人数"]
df_ratio = df_ratio[df_ratio["年"] <= 2019].reset_index(drop=True)
df_ratio = df_ratio.groupby(["在留資格"], as_index=False, dropna=False)["人数比_不法対正規"].mean()
df_ratio = df_ratio.dropna(subset=["人数比_不法対正規"]).reset_index(drop=True)
df_ratio.to_csv(
    output_dir / "14_不法残留者_不法対正規人数比_2018-2019平均.csv",
    index=False,
    encoding="utf-8-sig",
)


# ======================== 処理3: 在留資格別・年代別構成比 ========================
df_age_ratio = df_legal[df_legal["年代"] != "不詳"].reset_index(drop=True)
df_age_ratio = df_age_ratio.groupby(["年", "在留資格", "年代"], as_index=False, dropna=False)["人数"].sum()
df_age_ratio["合計人数"] = df_age_ratio.groupby(["年", "在留資格"])["人数"].transform("sum")
df_age_ratio["年代別構成比"] = df_age_ratio["人数"] / df_age_ratio["合計人数"]
df_age_ratio.to_csv(
    output_dir / "14_不法残留者_在留資格別年代構成比.csv",
    index=False,
    encoding="utf-8-sig",
)

print("処理完了")
