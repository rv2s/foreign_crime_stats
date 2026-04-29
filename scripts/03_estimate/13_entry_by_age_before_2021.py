# 2021年以前の入国者データについて、年代別の年換算人口を算出するコード
# 年換算人口 = (年代別人数 × 年代別平均滞在日数) / 365
# ※年代別平均滞在日数は入国者の直接データがないため、近似として出国者データの年代別平均滞在日数を用いる
# ※10~14歳の年換算人口は、10~14歳人口を5で割った数値を14歳とし、残りを10~13歳とする方法で推計する
# ※年代別人数は、入国者(短期滞在者)の直接データがないため、近似として入国者マクロデータの年代別構成比を用いて、年代別人数を算出する方法で推計する

# ======================== ライブラリインポート ======================== 
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ======================== 
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "01_tidy" / "13_入国者" / "before_2021" / "在留資格別" / "13_入国者_tidydata_2021年以前_在留資格別.csv"
input_params_by_age = BASE_PATH / "99_work" / "13_入国者" / "before_2021" / "03_parameters" / "13_入国者マクロ_年代構成比_2021年以前.csv"
input_params_ave_stay = BASE_PATH / "99_work" / "12_出国者" / "before_2021" / "03_parameters" / "12_出国者_年別平均滞在日数.csv"
input_map = BASE_PATH / "99_work" / "13_入国者" / "before_2021" / "02_map" / "13_入国者_年代マップ_2021年以前.csv"
output_file = BASE_PATH / "03_estimated" / "13_統合前" / "13_入国者_年代別年換算人口_2021年以前.csv"

df = pd.read_csv(input_file, encoding="utf-8-sig")
df_params_by_age = pd.read_csv(input_params_by_age, encoding="utf-8-sig")
df_params_ave_stay = pd.read_csv(input_params_ave_stay, encoding="utf-8-sig")
df_map = pd.read_csv(input_map, encoding="utf-8-sig")

# ======================== 処理1: 年代別短期入国者数算出 ======================== 
# 2つのデータフレーム統合
df = pd.merge(
    left  = df[["年", "人数"]], # 残したいカラム名
    right = df_params_by_age[["年", "年代", "年代構成比"]],
    on    = ["年"], # 共通カラム名
    how   = "right" # 指定した側はデータが落ちない
)

# カラム名変更
df = df.rename(columns={"人数": "合計人数"})

# 年代別短期入国者数の算出
df["人数"] = df["合計人数"] * df["年代構成比"]


# ======================== 処理2: 年代別年換算人口算出 ======================== 
# 年別平均滞在日数データのマージ
df = pd.merge(
    left  = df[["年", "年代", "人数"]], # 残したいカラム名
    right = df_params_ave_stay[["年", "年別平均滞在日数"]],
    on    = ["年"], # 共通カラム名
    how   = "right" # 指定した側はデータが落ちない
)

# 年換算人口の算出
df["年換算人口"] = (df["人数"] * df["年別平均滞在日数"]) / 365

# 必要列に絞る
df = df[["年", "年代", "年換算人口"]]

# 列名変更
df = df.rename(columns={"年換算人口": "人数"})

# 数値チェック用
check_val = df["人数"].sum()


# ======================== 処理3: 10~14歳を10~13歳と14歳の行に分ける ※ 14歳人口推計方法 = 10~14歳人口 ÷ 5 ========================
# 10~14歳だけのdfを作成
df_10to14 = df[df["年代"] == "10~14歳"].reset_index(drop=True)

# 14歳(5分の1)列と10~13歳(5分の4)列を作成
df_10to14["14歳"] = df_10to14["人数"] / 5
df_10to14["10~13歳"] = df_10to14["人数"] - df_10to14["14歳"]

# meltでtidy化
df_10to14 = df_10to14.melt(id_vars=["年"], value_vars=["10~13歳", "14歳"], var_name="年代", value_name="人口")

# 列名変更
df_10to14 = df_10to14.rename(columns={"人口": "人数"})

# データの結合
df = pd.concat([df, df_10to14], ignore_index=True)

# 10~14歳の行を削除
df = df[df["年代"] != "10~14歳"].reset_index(drop=True)


# ======================== 処理3: 年代の名寄せ & 保存 ========================
# 名寄せ
df_dict = df_map.set_index("年代")["年代_名寄せ後"].to_dict()
df["年代_名寄せ後"] = df["年代"].map(df_dict)

# 必要列で集計 ※ 名寄せ前の粒度でなく名寄せ後の粒度で行を削減する
df = df.groupby(["年", "年代_名寄せ後"], as_index=False, dropna=False)["人数"].sum()

# 列名変更
df = df.rename(columns={"年代_名寄せ後": "年代"})

# 数値チェック
total_val = df["人数"].sum()
print(f"差分: {check_val - total_val:.6f}")

# 保存
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("処理完了")
