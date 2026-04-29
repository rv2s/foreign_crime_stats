import pandas as pd
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

INPUT_DIR = BASE_PATH / "00_raw" / "08_検挙人員数_在留資格別"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "08_検挙人員数_在留資格別"

# ======== 基本情報 ========
SHEET_CONFIGS = [
    {
        "input_file": "r6toukeisotai0315.csv",
        "output_file": "08_2024_tidy.csv",
        "format_type": "v1_R4later",
        "year": "2024",
        "header": None,
        "check_val": 6368,
        "sheet":[
            {
                "sheet_name": "r6toukeisotai0315",
                "use_row": {"start": 2, "end": 15}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B, E:O",
                "cat_cols": ["在留資格"],
                "val_cols_map": {
                    "殺人": "凶悪犯/殺人",
                    "強盗": "凶悪犯/強盗",
                    "放火": "凶悪犯/放火",
                    "不同意性交等": "凶悪犯/不同意性交等",
                    "粗暴犯": "粗暴犯",
                    "うち傷害": "粗暴犯/傷害",
                    "窃盗犯": "窃盗犯",
                    "うち侵入窃盗": "窃盗犯/侵入盗",
                    "知能犯": "知能犯",
                    "風俗犯": "風俗犯",
                    "その他の刑法犯": "その他の刑法犯",
                },
            }
        ]
    },
    {
        "input_file": "r5toukeisotai0315.csv",
        "output_file": "08_2023_tidy.csv",
        "format_type": "v1_R4later",
        "year": "2023",
        "header": None,
        "check_val": 5735,
        "sheet":[
            {
                "sheet_name": "r5toukeisotai0315",
                "use_row": {"start": 2, "end": 14}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "C, F:P",
                "cat_cols": ["在留資格"],
                "val_cols_map": {
                    "殺人": "凶悪犯/殺人",
                    "強盗": "凶悪犯/強盗",
                    "放火": "凶悪犯/放火",
                    "不同意性交等": "凶悪犯/不同意性交等",
                    "粗暴犯": "粗暴犯",
                    "うち傷害": "粗暴犯/傷害",
                    "窃盗犯": "窃盗犯",
                    "うち侵入窃盗": "窃盗犯/侵入盗",
                    "知能犯": "知能犯",
                    "風俗犯": "風俗犯",
                    "その他の刑法犯": "その他の刑法犯",
                },
            }
        ]
    },
    {
        "input_file": "r4toukeisotai0314.csv",
        "output_file": "08_2022_tidy.csv",
        "format_type": "v1_R4later",
        "year": "2022",
        "header": None,
        "check_val": 5014,
        "sheet":[
            {
                "sheet_name": "r4toukeisotai0314",
                "use_row": {"start": 3, "end": 17}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "C, F:P",
                "cat_cols": ["在留資格"],
                "val_cols_map": {
                    "殺人": "凶悪犯/殺人",
                    "強盗": "凶悪犯/強盗",
                    "放火": "凶悪犯/放火",
                    "強制性交等": "凶悪犯/強制性交等",
                    "粗暴犯": "粗暴犯",
                    "うち傷害": "粗暴犯/傷害",
                    "窃盗犯": "窃盗犯",
                    "うち侵入窃盗": "窃盗犯/侵入盗",
                    "知能犯": "知能犯",
                    "風俗犯": "風俗犯",
                    "その他の刑法犯": "その他の刑法犯",
                },
            }
        ]
    },
]


def excel_col_to_idx(col: str) -> int:
    """Excel列文字(A, B, ..., Z, AA, AB, ...) -> 0-based index"""
    col = col.strip().upper()
    n = 0
    for ch in col:
        if not ("A" <= ch <= "Z"):
            raise ValueError(f"Invalid excel column: {col}")
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def parse_usecols_excel_like(usecols: str) -> list[int]:
    """
    "B, E:O" のようなExcel表記を 0-based index の list に展開（CSV向け）
    """
    parts = [p.strip() for p in usecols.split(",")]
    idxs = []
    for p in parts:
        if ":" in p:
            a, b = [x.strip() for x in p.split(":")]
            ia, ib = excel_col_to_idx(a), excel_col_to_idx(b)
            if ia <= ib:
                idxs.extend(list(range(ia, ib + 1)))
            else:
                idxs.extend(list(range(ib, ia + 1)))
        else:
            idxs.append(excel_col_to_idx(p))

    # 重複除去して順序維持
    seen = set()
    out = []
    for i in idxs:
        if i not in seen:
            out.append(i)
            seen.add(i)
    return out


def remove_inner_spaces(s: pd.Series) -> pd.Series:
    # 文字列化 → すべての空白（半角/全角/タブ等）を削除 → 空文字はNAへ
    s = s.astype("string").str.replace(r"\s+", "", regex=True)
    return s.replace("", pd.NA)


def to_numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace({"-": 0, "－": 0, "―": 0, "−": 0})
    return df.apply(pd.to_numeric, errors="coerce")


def build_one_sheet_wide_v1(input_path: Path, file_cfg: dict, sh_cfg: dict) -> pd.DataFrame:
    """
    v1（R4以降）：CSVから、合算のみの在留資格×罪種 wide を作る
    """
    # 1) 読み込み（CSV全体→列位置で抜く）
    usecol_idxs = parse_usecols_excel_like(sh_cfg["usecols"])
    raw = pd.read_csv(input_path, header=file_cfg["header"], encoding="cp932")
    df = raw.iloc[:, usecol_idxs].copy()

    # 2) 行範囲で切る（cfg通り）
    r0 = sh_cfg["use_row"]["start"]
    r1 = sh_cfg["use_row"]["end"]
    df = df.iloc[r0:r1].copy()

    # 3) 列名付与
    cat_cols = sh_cfg["cat_cols"]  # ["在留資格"]
    val_keys = list(sh_cfg["val_cols_map"].keys())
    expected = len(cat_cols) + len(val_keys)
    if df.shape[1] != expected:
        raise ValueError(
            f"Column count mismatch: got {df.shape[1]}, expected {expected}. "
            f"cat_cols={len(cat_cols)}, val_cols_map={len(val_keys)}"
        )

    df.columns = cat_cols + val_keys

    # 4) cat列整形
    for c in cat_cols:
        df[c] = remove_inner_spaces(df[c])

    # 5) 不要行の削除（保険：構成比など）
    drop_labels = {"構成比", "構成比率", "在留資格別構成比", "包括罪種等別", "刑法犯人員"}
    if "在留資格" in df.columns:
        df = df[~df["在留資格"].isin(drop_labels)].copy()
        df = df[df["在留資格"].notna()].copy()

    # 6) v1は合算固定列を追加して index を統一
    df.insert(0, "正規・非正規区分", "合算")
    df.insert(1, "正規・非正規詳細", pd.NA)

    # 7) val列を階層名へリネーム（"殺人" -> "凶悪犯/殺人" など）
    df = df.rename(columns=sh_cfg["val_cols_map"])

    # 8) wide化（index化）
    idx_cols = ["正規・非正規区分", "正規・非正規詳細", "在留資格"]
    df = df.set_index(idx_cols)

    # 9) 数値化
    df = to_numeric_df(df)

    return df


def add_breakdown_other_and_drop_parents_v1(wide: pd.DataFrame) -> pd.DataFrame:
    wide = wide.copy()

    # ===== 窃盗犯：侵入盗があれば「その他」を作って親を落とす =====
    theft_parent = "窃盗犯"
    theft_child = "窃盗犯/侵入盗"
    if theft_parent in wide.columns and theft_child in wide.columns:
        other = "窃盗犯/その他"
        wide[other] = wide[theft_parent] - wide[theft_child]
        wide[other] = wide[other].clip(lower=0)
        wide = wide.drop(columns=[theft_parent], errors="ignore")

    # ===== 粗暴犯：傷害しか無いので「その他」を作って親を落とす =====
    assault_parent = "粗暴犯"
    assault_child = "粗暴犯/傷害"
    if assault_parent in wide.columns and assault_child in wide.columns:
        other = "粗暴犯/その他"
        wide[other] = wide[assault_parent] - wide[assault_child]
        wide[other] = wide[other].clip(lower=0)
        wide = wide.drop(columns=[assault_parent], errors="ignore")

    # ===== 親階層（子を持つ列）を削除 =====
    cols = list(wide.columns)
    parents_to_drop = [c for c in cols if any(d.startswith(c + "/") for d in cols)]
    wide = wide.drop(columns=parents_to_drop, errors="ignore")

    return wide


def wide_to_tidy(wide: pd.DataFrame, year: str) -> pd.DataFrame:
    tidy = (
        wide.reset_index()
        .melt(
            id_vars=list(wide.index.names),
            var_name="罪種",
            value_name="検挙人員",
        )
    )

    tidy.insert(0, "年", year)
    tidy["検挙人員"] = pd.to_numeric(tidy["検挙人員"], errors="coerce")

    # 罪種分解（最大3階層）
    crime_split = tidy["罪種"].astype("string").str.split("/", n=2, expand=True)
    tidy["罪種00"] = crime_split[0]
    tidy["罪種01"] = crime_split[1] if 1 in crime_split.columns else pd.NA
    tidy["罪種02"] = crime_split[2] if 2 in crime_split.columns else pd.NA

    # 列順
    front = ["年", "正規・非正規区分", "正規・非正規詳細", "在留資格", "罪種00", "罪種01", "罪種02", "検挙人員"]
    tidy = tidy[front]

    return tidy


def process_one_file_cfg_v1(cfg: dict) -> None:
    input_path = INPUT_DIR / cfg["input_file"]
    output_path = OUTPUT_DIR / cfg["output_file"]

    dfs_wide = []
    for sh_cfg in cfg["sheet"]:
        dfs_wide.append(build_one_sheet_wide_v1(input_path, cfg, sh_cfg))

    wide_merged = pd.concat(dfs_wide, axis=1)

    # 侵入窃盗の「その他」作成 + 親列削除
    wide_merged = add_breakdown_other_and_drop_parents_v1(wide_merged)

    # tidy化
    df_tidy = wide_to_tidy(wide_merged, cfg["year"])

    # 数値チェック（合算のみ）
    sum_val = df_tidy["検挙人員"].sum()
    diff_val = sum_val - cfg["check_val"]

    # 保存
    df_tidy.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"処理完了: {cfg['year']}年分, 差分: {diff_val}")

def main():
    # ======== 実行 ========
    for cfg in SHEET_CONFIGS:
        process_one_file_cfg_v1(cfg)


if __name__ == "__main__":
    main()


