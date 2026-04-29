# 分析結果CSVを閲覧用のExcelクロス集計表に変換するコード

# ======================== ライブラリインポート ========================
from pathlib import Path

import pandas as pd


# ======================== パス設定 ========================
BASE_PATH = Path(__file__).resolve().parents[2] / "data"

input_20 = BASE_PATH / "05_analytics" / "20_1万人あたり検挙人員数及び対日本人倍率.csv"
input_33 = BASE_PATH / "05_analytics" / "33_対推定検挙人員及び年齢調整後対日本人倍率.csv"

output_20 = BASE_PATH / "05_analytics" / "20_1万人あたり検挙人員数及び対日本人倍率_クロス集計.xlsx"
output_33 = BASE_PATH / "05_analytics" / "33_対推定検挙人員及び年齢調整後対日本人倍率_クロス集計.xlsx"


# ======================== 設定 ========================
INDEX_COLUMNS = ["区分00", "区分01", "在留資格", "罪種00", "罪種01"]

CATEGORY_ORDER = {
    "区分00": ["計", "日本人", "外国人"],
    "区分01": ["計", "来日外国人", "永住者等"],
    "在留資格": ["計", "定住者", "日本人の配偶者等", "短期滞在", "技能実習", "留学", "その他"],
    "罪種00": ["計", "凶悪犯", "粗暴犯", "窃盗犯", "知能犯", "風俗犯", "その他の刑法犯"],
    "罪種01": ["計", "殺人", "強盗", "放火", "不同意性交等", "傷害", "侵入盗", "その他"],
}


def apply_category_order(df: pd.DataFrame) -> pd.DataFrame:
    """主要カテゴリを指定順に並べ、定義外の値は後ろに追加する。"""
    df = df.copy()
    for column, base_order in CATEGORY_ORDER.items():
        values = df[column].dropna().astype(str).unique().tolist()
        extra_values = sorted(value for value in values if value not in base_order)
        df[column] = pd.Categorical(
            df[column],
            categories=base_order + extra_values,
            ordered=True,
        )
    return df


def make_pivot_table(df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """年を列にしたクロス集計表を作成する。"""
    return df.pivot_table(
        index=INDEX_COLUMNS,
        columns="年",
        values=value_column,
        observed=True,
    )


def adjust_sheet_widths(writer: pd.ExcelWriter, sheet_name: str, index_columns: int) -> None:
    """Excelで確認しやすいように列幅と固定ペインを調整する。"""
    worksheet = writer.sheets[sheet_name]
    worksheet.freeze_panes = worksheet["F2"]

    for column_cells in worksheet.columns:
        column_letter = column_cells[0].column_letter
        max_length = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column_cells
        )
        worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, 10), 24)

    for column_number in range(1, index_columns + 1):
        column_letter = worksheet.cell(row=1, column=column_number).column_letter
        worksheet.column_dimensions[column_letter].width = 18


def write_cross_table(
    input_file: Path,
    output_file: Path,
    sheet_values: dict[str, str],
) -> None:
    """1つのCSVから複数指標のクロス集計シートを作成する。"""
    df = pd.read_csv(input_file, encoding="utf-8-sig")
    df = apply_category_order(df)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_name, value_column in sheet_values.items():
            pt = make_pivot_table(df, value_column)
            pt.to_excel(writer, sheet_name=sheet_name)
            adjust_sheet_widths(writer, sheet_name, len(INDEX_COLUMNS))


# ======================== クロス集計表作成 ========================
write_cross_table(
    input_file=input_20,
    output_file=output_20,
    sheet_values={
        "1万人あたり検挙人員数": "検挙人員数_1万人あたり",
        "対日本人倍率": "対日本人倍率",
    },
)

write_cross_table(
    input_file=input_33,
    output_file=output_33,
    sheet_values={
        "対推定値倍率": "対推定値倍率",
        "年齢調整後対日本人倍率": "対日本人倍率_年齢調整後",
    },
)

print("処理完了")
