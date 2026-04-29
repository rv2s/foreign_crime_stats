# 09_検挙人員数_統合に在日米軍関係者を足した年別合計が、日本全体の年別合計と一致するか確認するコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
SCRIPT_DIR = Path(__file__).resolve().parent

input_total = BASE_PATH / "02_standardized" / "01_検挙人員数_日本全体_名寄せ後.csv"
input_foreign = BASE_PATH / "02_standardized" / "02_検挙人員数_外国人全体_名寄せ後.csv"
input_integrated = BASE_PATH / "04_integrated" / "09_検挙人員数_統合.csv"
output_file = SCRIPT_DIR / "09_検挙人員数_統合_年別合計チェック.csv"

df_total = pd.read_csv(input_total, encoding="utf-8-sig")
df_foreign = pd.read_csv(input_foreign, encoding="utf-8-sig")
df_integrated = pd.read_csv(input_integrated, encoding="utf-8-sig")


# ======================== 処理: 2015年以降の年別合計算出 ========================
df_total = df_total[df_total["年"] >= 2015].reset_index(drop=True)
df_foreign = df_foreign[df_foreign["年"] >= 2015].reset_index(drop=True)
df_integrated = df_integrated[df_integrated["年"] >= 2015].reset_index(drop=True)

df_total_yearly = (
    df_total.groupby("年", as_index=False, dropna=False)["検挙人員"]
    .sum()
    .rename(columns={"検挙人員": "日本全体_検挙人員"})
)

df_us_forces_yearly = (
    df_foreign[df_foreign["属性"] == "在日米軍関係者"]
    .groupby("年", as_index=False, dropna=False)["検挙人員"]
    .sum()
    .rename(columns={"検挙人員": "在日米軍関係者_検挙人員"})
)

df_integrated_yearly = (
    df_integrated.groupby("年", as_index=False, dropna=False)["検挙人員"]
    .sum()
    .rename(columns={"検挙人員": "09統合_検挙人員"})
)


# ======================== 処理: 突合 ========================
df_check = pd.merge(df_total_yearly, df_integrated_yearly, on="年", how="outer")
df_check = pd.merge(df_check, df_us_forces_yearly, on="年", how="outer")
df_check[["日本全体_検挙人員", "09統合_検挙人員", "在日米軍関係者_検挙人員"]] = df_check[
    ["日本全体_検挙人員", "09統合_検挙人員", "在日米軍関係者_検挙人員"]
].fillna(0)

df_check["09統合_在日米軍関係者加算後"] = df_check["09統合_検挙人員"] + df_check["在日米軍関係者_検挙人員"]
df_check["差分"] = df_check["日本全体_検挙人員"] - df_check["09統合_在日米軍関係者加算後"]
df_check["一致"] = df_check["差分"].abs() < 1e-9
df_check = df_check.sort_values("年").reset_index(drop=True)


# ======================== 結果出力 ========================
df_check.to_csv(output_file, index=False, encoding="utf-8-sig")

print(df_check.to_string(index=False))
print(f"最大絶対差分: {df_check['差分'].abs().max():.6f}")
print(f"不一致年数: {(~df_check['一致']).sum()}")
print(f"保存先: {output_file}")
