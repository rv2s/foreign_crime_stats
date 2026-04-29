# 2022年以降の入国者データについて、年代別の年換算人口を算出するコード
# 年換算人口 = (年代別人数 × 年代別平均滞在日数) / 365
# ※年代別平均滞在日数は入国者の直接データがないため、近似として出国者データの年代別平均滞在日数を用いる

# ======================== ライブラリインポート ========================
import pandas as pd
from pathlib import Path


# ======================== パス設定・データ読み込み ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
input_file = BASE_PATH / "01_tidy" / "13_入国者" / "after_2022" / "13_入国者_tidydata_2022年以降.csv"
input_params = BASE_PATH / "99_work" / "12_出国者" / "after_2022" / "03_parameters" / "12_出国者_年代別平均滞在日数.csv"
input_map = BASE_PATH / "99_work" / "13_入国者" / "after_2022" / "02_map" / "13_入国者_年代map_2022年以降.csv"
output_file = BASE_PATH / "03_estimated" / "13_統合前" / "13_入国者_年代別年換算人口_2022年以降.csv"

df = pd.read_csv(input_file)
df_params = pd.read_csv(input_params)
df_map = pd.read_csv(input_map)


# ======================== 処理1: 年換算人口の算出 ========================
# マージ
df = pd.merge(
    left  = df[["年", "年代", "人数"]], # 残したいカラム名
    right = df_params[["年", "年代", "年代別平均滞在日数"]],
    on    = ["年", "年代"], # 共通カラム名
    how   = "left" # 指定した側はデータが落ちない
)

# 年換算人口の算出
df["年換算人口"] = (df["人数"] * df["年代別平均滞在日数"]) / 365

# 必要列に絞る
df = df[["年", "年代", "年換算人口"]]

# 列名変更
df = df.rename(columns={"年換算人口": "人数"})

# 数値チェック用
check_val = df["人数"].sum()


# ======================== 処理2: 10~14歳を10~13歳と14歳の行に分ける ※ 14歳人口推計方法 = 10~14歳人口 ÷ 5 ========================
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
