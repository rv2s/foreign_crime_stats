# 年代別の検挙人員割合を算出するコード
# 年齢調整の基準率として、日本全体の年代別検挙人員数を統合人口の年代別人数で割る

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_arrests_total = BASE_PATH / "02_standardized" / "01_検挙人員数_日本全体_名寄せ後.csv"
input_population = BASE_PATH / "04_integrated" / "15_人口_統合.csv"
output_file = BASE_PATH / "05_analytics" / "intermediate" / "31_年代別検挙人員割合.csv"

df_arrests = pd.read_csv(input_arrests_total, encoding="utf-8-sig")
df_population = pd.read_csv(input_population, encoding="utf-8-sig")


# ======================== 処理: 粒度調整 ========================
df_arrests = df_arrests[df_arrests["年"] >= 2013].reset_index(drop=True)
df_arrests = df_arrests.drop(columns=["罪種02"], errors="ignore")
df_arrests = df_arrests.groupby(
    ["年", "年代", "罪種00", "罪種01"],
    as_index=False,
    dropna=False,
)["検挙人員"].sum()

# 刑事責任年齢未満に相当する0~13歳は母数から外す。
df_population = df_population[df_population["年代"] != "0~13歳"].reset_index(drop=True)
df_population = df_population.groupby(["年", "年代"], as_index=False, dropna=False)["人数"].sum()


# ======================== 処理: 年代別検挙人員割合算出 ========================
df = pd.merge(
    left=df_arrests,
    right=df_population,
    on=["年", "年代"],
    how="left",
    validate="m:1",
)

missing_population = df[df["人数"].isna()][["年", "年代"]].drop_duplicates()
if not missing_population.empty:
    raise ValueError(
        "人口データが存在しない年・年代があります: "
        + ", ".join(f"{row.年}:{row.年代}" for row in missing_population.itertuples(index=False))
    )

df["年代別検挙人員割合"] = df["検挙人員"] / df["人数"]


# ======================== 保存 ========================
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
