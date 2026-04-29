print("処理を開始します")
import pandas as pd
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"

INPUT_DIR = BASE_PATH / "00_raw" / "01_検挙人員数_日本全体"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "01_検挙人員数_日本全体"

print("処理中です")

# ======== 基本情報 ========
SHEET_CONFIGS = [
    {
        "input_file": "R06_043.xlsx",
        "output_file": "2024_tidy.csv",
        "year": "2024",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 60,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 191826
    },
    {
        "input_file": "R05_043.xlsx",
        "output_file": "2023_tidy.csv",
        "year": "2023",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 60,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 183269
    },
    {
        "input_file": "R04_043.xlsx",
        "output_file": "2022_tidy.csv",
        "year": "2022",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 169409
    },
    {
        "input_file": "R03_043.xlsx",
        "output_file": "2021_tidy.csv",
        "year": "2021",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 175041
    },
    {
        "input_file": "R02_043.xlsx",
        "output_file": "2020_tidy.csv",
        "year": "2020",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 182582
    },
    {
        "input_file": "R01_043.xlsx",
        "output_file": "2019_tidy.csv",
        "year": "2019",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 192607
    },
    {
        "input_file": "H30_043.xls",
        "output_file": "2018_tidy.csv",
        "year": "2018",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 206094
    },
    {
        "input_file": "H29_043.xls",
        "output_file": "2017_tidy.csv",
        "year": "2017",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 215003

    },
    {
        "input_file": "H28_043.xls",
        "output_file": "2016_tidy.csv",
        "year": "2016",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 226376
    },
    {
        "input_file": "H27_043.xls",
        "output_file": "2015_tidy.csv",
        "year": "2015",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 239355
    },
    {
        "input_file": "H26_043.xls",
        "output_file": "2014_tidy.csv",
        "year": "2014",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 251115
    },
    {
        "input_file": "H25_043.xls",
        "output_file": "2013_tidy.csv",
        "year": "2013",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 262486
    },
    {
        "input_file": "H24_043.xls",
        "output_file": "2012_tidy.csv",
        "year": "2012",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 287021
    },
    {
        "input_file": "H23_043.xls",
        "output_file": "2011_tidy.csv",
        "year": "2011",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 305631
    },
    {
        "input_file": "H22_043.xls",
        "output_file": "2010_tidy.csv",
        "year": "2010",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 322620
    },
    {
        "input_file": "H21_043.xls",
        "output_file": "2009_tidy.csv",
        "year": "2009",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 332888
    },
    {
        "input_file": "H20_043.xls",
        "output_file": "2008_tidy.csv",
        "year": "2008",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 339752
    },
    {
        "input_file": "H19_043.xls",
        "output_file": "2007_tidy.csv",
        "year": "2007",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 365577
    },
    {
        "input_file": "H18_043.xls",
        "output_file": "2006_tidy.csv",
        "year": "2006",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 384250
    },
    {
        "input_file": "H17_43.xls",
        "output_file": "2005_tidy.csv",
        "year": "2005",
        "sheet_name": "01",
        "header": None,
        "skiprows": 6,
        "last_row": 61,
        "usecols": "C:G, J:O, R:Y",
        "cat_cols": ["罪種00", "罪種01", "罪種02", "罪種03", "罪種04"],
        "val_cols": ["14歳", "15歳", "16歳", "17歳", "18歳", "19歳", "20~24歳", "25~29歳", "30代", "40代", "50代", "60~64歳", "65~69歳", "70代以上"],
        "check_val": 386955
    },
]

def process_one_year(cfg: dict) -> None:
    input_path = INPUT_DIR / cfg["input_file"]
    output_path = OUTPUT_DIR / cfg["output_file"]
    nrows = cfg["last_row"] - cfg["skiprows"]
    check_val = cfg.get("check_val", 0)

    # ======== データ読み込み ========
    raw = pd.read_excel(input_path, sheet_name=cfg["sheet_name"], header=cfg["header"], nrows=nrows, usecols=cfg["usecols"], skiprows=cfg["skiprows"])

    # 列名の設定
    cat_cols = cfg["cat_cols"]
    val_cols = cfg["val_cols"]
    raw.columns = cat_cols + val_cols

    # ========= 階層パスの作成 ========
    stack = [None] * len(cat_cols)
    rows = []

    for _, r in raw.iterrows():

        # ==== 罪種の階層が何段目か探しdepthに代入 ====
        depth = None
        for i, c in enumerate(cat_cols):
            if pd.notna(r[c]):
                depth = i
                break
        if depth is None:
            continue

        # ==== その階層の罪種名を取得（&文字を整える） ====
        name = str(r[cat_cols[depth]]).strip()

        # ==== うち系なら、右側から本当の罪種名を拾う ====
        if "うち" in name:
            real_name = None
            for c2 in cat_cols[depth+1:]:
                if pd.notna(r[c2]):
                    real_name = str(r[c2]).strip()
                    break
            name = real_name

        # ==== stackを更新（その階層に罪種名をセット。下の階層はリセット） ====
        stack[depth] = name
        for d in range(depth + 1, len(stack)):
            stack[d] = None

        # ==== path と parent_path を作る ====
        parts = [x for x in stack if x is not None]
        path = "/".join(parts)
        parent_path = "/".join(parts[:-1])

        # ==== 数値列をまとめて保持（あとでmeltするので、ここではそのまま列で持つ） ====
        row_dict = {
            "path": path,
            "parent_path": parent_path,
            "depth": depth,
            "罪種名": name,
        }
        for c in val_cols:
            row_dict[c] = r[c]

        rows.append(row_dict)

    pdf = pd.DataFrame(rows)

    # ======== 「その他」行を作成する ========
    parent_paths = set(pdf["parent_path"].dropna()) - {""}

    others_rows = []

    for p in parent_paths:
        # 親行（合計行）
        parent_row = pdf[pdf["path"] == p]
        if parent_row.empty:
            continue
        parent_row = parent_row.iloc[0]

        # 直下の子（parent_path が p の行）
        children = pdf[pdf["parent_path"] == p]
        if children.empty:
            continue

        # 親の値
        parent_vals = parent_row[val_cols]

        # 子の合計
        children_sum = children[val_cols].sum(axis=0)

        # 差分 = その他
        diff = parent_vals - children_sum

        # 差分がある場合のみ「その他」を作る
        if (diff > 0.5).any():
            row = {
                "path": p + "/その他",
                "parent_path": p,
                "depth": int(parent_row["depth"]) + 1,
                "罪種名": str(parent_row["罪種名"]) + "（その他）",
            }
            for c in val_cols:
                row[c] = diff[c]
            others_rows.append(row)

    df_others = pd.DataFrame(others_rows)
    pdf2 = pd.concat([pdf, df_others], ignore_index=True)

    # 念のため：数値にならないものは0にする
    for c in val_cols:
        pdf2[c] = pd.to_numeric(pdf2[c], errors="coerce").fillna(0)

    # ======== 合計行(親)を消す ========
    parent_paths2 = set(pdf2["parent_path"].dropna()) - {""}

    # 親でない行だけ残す（= 子 + その他）
    leaf = pdf2[~pdf2["path"].isin(parent_paths2)].copy()
    leaf = leaf.reset_index(drop=True)

    # ======== tidy化 ========
    df_tidy = leaf.melt(
        id_vars=["path", "parent_path", "depth", "罪種名"],
        value_vars=val_cols,
        var_name="年齢層",
        value_name="検挙人員"
    )

    # ======== path を分解して 罪種00, 罪種01,... を作る ========
    # depth の最大値から階層数を決める（depth は 0始まりなので +1）
    max_depth = int(leaf["depth"].max())
    n_levels = max_depth + 1

    crime_cols = [f"罪種{str(i).zfill(2)}" for i in range(n_levels)]

    # path を / で分割して列化（足りない階層は NaN になる）
    split_df = df_tidy["path"].astype(str).str.split("/", expand=True)

    split_df.columns = crime_cols

    # df_tidy に結合
    df_tidy = pd.concat([split_df, df_tidy[["年齢層", "検挙人員"]]], axis=1)

    # "年"列を一番左に追加
    df_tidy.insert(0, "年", cfg["year"])

    # ======== 合計値チェック ========
    tidy_sum = df_tidy["検挙人員"].sum()
    diff_val = check_val - tidy_sum

    # ======== 保存 ========
    df_tidy.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"処理完了: {cfg['year']}年分, 差分: {diff_val}")

def main():
    for cfg in SHEET_CONFIGS:
        process_one_year(cfg)

if __name__ == "__main__":
    main()

print("全ての処理が完了しました")
