# 在留資格別・国籍等別検挙人員数のうち、定住者の表をtidy化するコード

from pathlib import Path

import pandas as pd


# ======================== パス設定 ========================
BASE_PATH = Path(__file__).resolve().parents[3] / "data"
INPUT_DIR = BASE_PATH / "00_raw" / "999_reseach" / "在留資格別国籍別検挙人員数"
OUTPUT_DIR = BASE_PATH / "06_research" / "resident_nationality" / "01_tidy"

INPUT_FILE = INPUT_DIR / "r6toukeisotai0316.csv"
OUTPUT_FILE = OUTPUT_DIR / "01_定住者_国籍別検挙人員数_tidy.csv"


# ======================== 設定 ========================
CONFIG = {
    "input_file": INPUT_FILE,
    "output_file": OUTPUT_FILE,
    "encoding": "cp932",
    "status": "定住者",
    "table_range": {
        # Excel表記 A4:L11
        # pandasでは0始まり、endはilocの終端なので+1する
        "row_start": 3,
        "row_end": 11,
        "col_start": 0,
        "col_end": 12,
    },
    "header_row_offset": 0,
    "total_row_label": "総数",
    "nationality_column_position": 1,
    "year_column_start_position": 2,
}


# ======================== 関数定義 ========================
def convert_japanese_era_year(value) -> int:
    """H28, R元, R2 のような年表記を西暦に変換する。"""
    text = str(value).strip()
    if text.startswith("H"):
        return 1988 + int(text.replace("H", ""))
    if text.startswith("R"):
        year_text = text.replace("R", "")
        year = 1 if year_text == "元" else int(year_text)
        return 2018 + year
    raise ValueError(f"想定外の年表記です: {value}")


def to_number(value) -> int:
    """カンマ付き数値やハイフンを整数に変換する。"""
    if pd.isna(value):
        return 0

    text = str(value).strip().replace(",", "")
    if text in {"", "-", "－", "―", "−"}:
        return 0

    return int(float(text))


def tidy_resident_table(config: dict) -> pd.DataFrame:
    """定住者表を読み込み、年・在留資格・国籍地域・検挙人員の縦持ちに変換する。"""
    raw = pd.read_csv(
        config["input_file"],
        header=None,
        encoding=config["encoding"],
    )

    table_range = config["table_range"]
    df = raw.iloc[
        table_range["row_start"] : table_range["row_end"],
        table_range["col_start"] : table_range["col_end"],
    ].copy()
    df = df.reset_index(drop=True)

    header = df.iloc[config["header_row_offset"]]
    years = [
        convert_japanese_era_year(value)
        for value in header.iloc[config["year_column_start_position"] :]
    ]

    body = df.iloc[config["header_row_offset"] + 1 :].copy()
    nationality_col = body.columns[config["nationality_column_position"]]
    body = body.rename(columns={nationality_col: "国籍・地域"})
    body["国籍・地域"] = body["国籍・地域"].astype("string").str.strip()

    body = body[
        body["国籍・地域"].notna()
        & (body["国籍・地域"] != "")
        & (body["国籍・地域"] != config["total_row_label"])
    ].copy()

    value_columns = list(body.columns[config["year_column_start_position"] :])
    rename_map = dict(zip(value_columns, years, strict=True))
    body = body.rename(columns=rename_map)
    body["_国籍順"] = range(len(body))

    tidy = body.melt(
        id_vars=["国籍・地域", "_国籍順"],
        value_vars=years,
        var_name="年",
        value_name="検挙人員",
    )
    tidy["在留資格"] = config["status"]
    tidy["検挙人員"] = tidy["検挙人員"].map(to_number)
    tidy = tidy.sort_values(["年", "_国籍順"]).reset_index(drop=True)
    tidy = tidy[["年", "在留資格", "国籍・地域", "検挙人員"]]

    return tidy


# ======================== 実行 ========================
if __name__ == "__main__":
    df_tidy = tidy_resident_table(CONFIG)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_tidy.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"行数: {len(df_tidy)}")
    print(f"検挙人員合計: {df_tidy['検挙人員'].sum()}")
    print(f"保存先: {OUTPUT_FILE}")
    print("処理完了")
