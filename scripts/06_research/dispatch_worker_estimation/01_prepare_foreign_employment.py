# 001389472.xlsx の別表4・別表6をtidy化するコード

from pathlib import Path

import pandas as pd


# ======================== パス設定 ========================
BASE_PATH = Path(__file__).resolve().parents[3] / "data"
INPUT_FILE = BASE_PATH / "00_raw" / "999_reseach" / "派遣労働者数推計" / "001389472.xlsx"
OUTPUT_DIR = BASE_PATH / "06_research" / "dispatch_worker_estimation" / "01_tidy"

OUTPUT_TABLE4 = OUTPUT_DIR / "01_別表4_業種別外国人労働者数_tidy.csv"
OUTPUT_TABLE6 = OUTPUT_DIR / "02_別表6_在留資格別業種構成比_tidy.csv"


# ======================== 共通関数 ========================
def clean_text(value):
    """文字列の改行・空白を整える。"""
    if pd.isna(value):
        return pd.NA

    text = str(value).replace("\n", "")
    text = " ".join(text.split())
    text = text.replace("　", "")
    return text if text else pd.NA


def to_number(value) -> float:
    """数値セルをfloatに変換する。"""
    if pd.isna(value):
        return pd.NA

    if isinstance(value, str):
        value = value.replace(",", "").replace("%", "").strip()
        if value in {"", "-", "－", "―", "−"}:
            return pd.NA

    return pd.to_numeric(value, errors="coerce")


# ======================== 別表4 ========================
def tidy_table4(input_file: Path) -> pd.DataFrame:
    """別表4 A3:M40 から、業種と外国人労働者数関連列を抽出する。"""
    raw = pd.read_excel(input_file, sheet_name="別表４", header=None)

    # Excel表記 A3:M40 -> pandas iloc[2:40, 0:13]
    df = raw.iloc[2:40, 0:13].copy().reset_index(drop=True)

    # C列: 業種, K列: 外国人労働者数, L列: 派遣及び請負事業, M列: 派遣及び請負事業割合
    df = df.iloc[:, [2, 10, 11, 12]].copy()
    df.columns = [
        "業種",
        "外国人労働者数",
        "外国人労働者数_派遣及び請負事業",
        "外国人労働者_派遣及び請負事業割合",
    ]

    df["業種"] = df["業種"].map(clean_text)
    df = df[df["業種"].notna()].copy()

    numeric_columns = [
        "外国人労働者数",
        "外国人労働者数_派遣及び請負事業",
        "外国人労働者_派遣及び請負事業割合",
    ]
    for column in numeric_columns:
        df[column] = df[column].map(to_number)

    # 元表の比率は 17.3 のようなパーセント値なので、列名を明示し、小数割合列も付与する。
    df = df.rename(
        columns={
            "外国人労働者_派遣及び請負事業割合": "外国人労働者_派遣及び請負事業割合_pct"
        }
    )
    df["外国人労働者_派遣及び請負事業割合"] = df["外国人労働者_派遣及び請負事業割合_pct"] / 100

    df.insert(0, "年", 2024)
    return df[
        [
            "年",
            "業種",
            "外国人労働者数",
            "外国人労働者数_派遣及び請負事業",
            "外国人労働者_派遣及び請負事業割合",
            "外国人労働者_派遣及び請負事業割合_pct",
        ]
    ].reset_index(drop=True)


# ======================== 別表6 ========================
def tidy_table6(input_file: Path) -> pd.DataFrame:
    """別表6 A4:S19 から、指定行の在留資格別・業種別構成比を抽出する。"""
    raw = pd.read_excel(input_file, sheet_name="別表６", header=None)

    # Excel表記 A4:S19 -> pandas iloc[3:19, 0:19]
    df = raw.iloc[3:19, 0:19].copy().reset_index(drop=True)

    # Excel行 11,13,15,16,17,18 -> 範囲内では0始まりで 7,9,11,12,13,14
    target_row_positions = [7, 9, 11, 12, 13, 14]
    target = df.iloc[target_row_positions].copy()

    # 在留資格名はA列またはB列に入っている
    target["在留資格"] = target.iloc[:, 1].where(target.iloc[:, 1].notna(), target.iloc[:, 0])
    target["在留資格"] = (
        target["在留資格"]
        .map(clean_text)
        .astype("string")
        .str.replace(r"^[①②③④⑤⑥]", "", regex=True)
        .str.replace(r"^うち", "", regex=True)
        .str.strip()
    )

    # 構成比列 E,F,I,K,M,O,Q,S のうち、業種名は各構成比列の1つ左の列。
    # ユーザー指定の E は表構造上「建設業」の構成比列、以降は F/I/K/M/O/Q/S を構成比列として扱う。
    composition_col_positions = [4, 6, 8, 10, 12, 14, 16, 18]

    rows = []
    for _, row in target.iterrows():
        status = row["在留資格"]
        for composition_col in composition_col_positions:
            industry_col = composition_col - 1
            industry = clean_text(df.iloc[0, industry_col])
            industry = str(industry).replace("うち", "").strip()
            # 元表の構成比はパーセント値として入っているため、小数割合に直す。
            composition_pct = to_number(row.iloc[composition_col])
            rows.append(
                {
                    "年": 2024,
                    "在留資格": status,
                    "業種": industry,
                    "業種構成比": composition_pct / 100 if pd.notna(composition_pct) else pd.NA,
                    "業種構成比_pct": composition_pct,
                }
            )

    return pd.DataFrame(rows)


# ======================== 実行 ========================
if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_table4 = tidy_table4(INPUT_FILE)
    df_table4.to_csv(OUTPUT_TABLE4, index=False, encoding="utf-8-sig")

    df_table6 = tidy_table6(INPUT_FILE)
    df_table6.to_csv(OUTPUT_TABLE6, index=False, encoding="utf-8-sig")

    print(f"別表4 行数: {len(df_table4)}")
    print(f"別表4 保存先: {OUTPUT_TABLE4}")
    print(f"別表6 行数: {len(df_table6)}")
    print(f"別表6 保存先: {OUTPUT_TABLE6}")
    print("処理完了")
