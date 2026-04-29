import pandas as pd
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
import warnings
import re

warnings.filterwarnings("ignore", category=FutureWarning)

# ======== 設定 ========
INPUT_DIR = BASE_PATH / "00_raw" / "08_検挙人員数_在留資格別"
MANUAL_INPUT_DIR = BASE_PATH / "00_raw" / "99_manual" / "08_検挙人員数_在留資格別"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "08_検挙人員数_在留資格別"

SHEET_CONFIGS = [
    {
        "input_file": "R03.toukei.sotai_03-17.csv",
        "output_file": "08_2021_tidy.csv",
        "year": "2021",
        "check_val": 5573,
        "sheets": [
            {
                "sheet_name": "R03.toukei.sotai_03-17",
                "use_row": {"start": 7, "end": 28}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:D, G:Q",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
    {
        "input_file": "R02.toukei.sotai_03.xlsx",
        "output_file": "08_2020_tidy.csv",
        "year": "2020",
        "check_val": 5634,
        "sheets": [
            {
                "sheet_name": "【図表３－１４　包括罪種等別・在留資格別検挙状況】",
                "use_row": {"start": 8, "end": 29}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "C:E, H:R",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
    {
        "input_file": "R01.toukei.sotai_03.xlsx",
        "output_file": "08_2019_tidy.csv",
        "year": "2019",
        "check_val": 5563,
        "sheets": [
            {
                "sheet_name": "【図表３－１４　包括罪種等別・在留資格別検挙状況】",
                "use_row": {"start": 8, "end": 29}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "C:E, H:R",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
    {
        "input_file": "h30.toukei.sotai_03.xlsx",
        "output_file": "08_2018_tidy.csv",
        "year": "2018",
        "check_val": 5844,
        "sheets": [
            {
                "sheet_name": "【図表３－１４　包括罪種等別・在留資格別検挙状況】",
                "use_row": {"start": 8, "end": 29}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "C:E, H:R",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
    {
        "input_file": "h29.toukei.sotai_04.xlsx",
        "output_file": "08_2017_tidy.csv",
        "year": "2017",
        "check_val": 6113,
        "sheets": [
            {
                "sheet_name": "図表４－14　包括罪種等別・在留資格別刑法犯検挙人員",
                "use_row": {"start": 13, "end": 34}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "C:E, H:R",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
    {
        "input_file": "h28.toukei.sotai_04.xlsx",
        "output_file": "08_2016_tidy.csv",
        "year": "2016",
        "check_val": 6097,
        "sheets": [
            {
                "sheet_name": "図表４－13",
                "use_row": {"start": 13, "end": 34}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "C:E, H:R",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
    {
        "input_file": "h25~27_在留資格別_刑法犯検挙人員.xlsx",
        "output_file": "08_2015_tidy.csv",
        "year": "2015",
        "check_val": 6187,
        "sheets": [
            {
                "sheet_name": "H27",
                "use_row": {"start": 8, "end": 29}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:D, G:Q",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
    {
        "input_file": "h25~27_在留資格別_刑法犯検挙人員.xlsx",
        "output_file": "08_2014_tidy.csv",
        "year": "2014",
        "check_val": 5787,
        "sheets": [
            {
                "sheet_name": "H26",
                "use_row": {"start": 8, "end": 29}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:D, G:Q",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
    {
        "input_file": "h25~27_在留資格別_刑法犯検挙人員.xlsx",
        "output_file": "08_2013_tidy.csv",
        "year": "2013",
        "check_val": 5620,
        "sheets": [
            {
                "sheet_name": "H25",
                "use_row": {"start": 8, "end": 29}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:D, G:Q",
                "cat_cols": ["正規・非正規区分", "正規・非正規詳細", "在留資格"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/強盗/侵入強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "風俗犯", "その他の刑法犯"],
            }
        ]
    },
]

MANUAL_INPUT_FILES = {
    "h25~27_在留資格別_刑法犯検挙人員.xlsx",
}


def resolve_input_path(input_file: str) -> Path:
    if input_file in MANUAL_INPUT_FILES:
        return MANUAL_INPUT_DIR / input_file
    return INPUT_DIR / input_file


# =========================================================
#  Excel列指定（"B:D, G:Q" 等）を 0-based index の list[int] に変換
# =========================================================
def _col_letter_to_idx(col: str) -> int:
    col = col.strip().upper()
    n = 0
    for ch in col:
        if not ("A" <= ch <= "Z"):
            raise ValueError(f"invalid column letter: {col}")
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1  # 0-based


def parse_excel_usecols_to_indices(usecols: str) -> list[int]:
    # "B:D, G:Q" -> [1,2,3, 6..16]
    indices: list[int] = []
    parts = [p.strip() for p in usecols.split(",")]
    for p in parts:
        if ":" in p:
            a, b = [x.strip() for x in p.split(":")]
            ia = _col_letter_to_idx(a)
            ib = _col_letter_to_idx(b)
            if ia > ib:
                ia, ib = ib, ia
            indices.extend(list(range(ia, ib + 1)))
        else:
            indices.append(_col_letter_to_idx(p))
    # 重複があっても困らないが、念のためユニーク化して元の順を維持
    seen = set()
    out = []
    for i in indices:
        if i not in seen:
            out.append(i)
            seen.add(i)
    return out


# =========================================================
#  読み込み処理（xlsx / csv の違いを吸収）
# =========================================================
def read_table(input_path: Path, sheet_name: str | None, use_row: dict, usecols: str) -> pd.DataFrame:
    col_idx = parse_excel_usecols_to_indices(usecols)

    if input_path.suffix.lower() == ".csv":
        # CSVは usecols="B:D" みたいな指定が使えないので index list で抜く
        # エンコーディングは utf-8-sig -> cp932 の順で試す
        last_err = None
        for enc in ("utf-8-sig", "cp932"):
            try:
                df_all = pd.read_csv(input_path, header=None, encoding=enc)
                break
            except Exception as e:
                last_err = e
                df_all = None
        if df_all is None:
            raise last_err

        df_all = df_all.iloc[:, col_idx]
    else:
        # Excelは list[int] の usecols が使える
        df_all = pd.read_excel(input_path, sheet_name=sheet_name, header=None, usecols=col_idx)

    # 行切り出し：start は「Excel行-1」、end は「Excelの終了行(1始まり)」として扱う
    # iloc は end が排他的なので、Excel end 行を含めたい場合はそのまま end を渡す
    start = int(use_row["start"])
    end = int(use_row["end"])
    df = df_all.iloc[start:end].copy()

    # 余計な全空行を落とす
    df = df.dropna(how="all").reset_index(drop=True)
    return df


# =========================================================
#  文字クリーニング
# =========================================================
def clean_str(x) -> str | None:
    if pd.isna(x):
        return None
    s = str(x)
    # 全角スペースや連続空白も含めて整える
    s = s.replace("\u3000", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s if s != "" else None


# =========================================================
#  階層パス（在留資格側）を作る：ffill禁止のため stack 方式
# =========================================================
def build_residency_paths(raw: pd.DataFrame, cat_cols: list[str], val_cols: list[str]) -> pd.DataFrame:
    # raw はすでに columns = cat_cols + val_cols が入っている前提

    stack = [None] * len(cat_cols)
    rows = []

    for _, r in raw.iterrows():
        # 構成比・比率行の除外（どの列に入っていても除外できるように）
        cat_texts = [clean_str(r[c]) for c in cat_cols]
        joined = " ".join([t for t in cat_texts if t])
        if any(k in joined for k in ["構成比", "構成比率"]):
            continue

        # depth: 左から最初に値が入っている列
        depth = None
        for i, c in enumerate(cat_cols):
            if pd.notna(r[c]) and clean_str(r[c]) is not None:
                depth = i
                break
        if depth is None:
            continue

        name = clean_str(r[cat_cols[depth]])
        if name is None:
            continue

        # stack 更新
        stack[depth] = name
        for d in range(depth + 1, len(stack)):
            stack[d] = None

        parts = [x for x in stack if x is not None]
        path = "/".join(parts)
        parent_path = "/".join(parts[:-1])

        row_dict = {
            "path": path,
            "parent_path": parent_path,
            "depth": depth,
        }
        for c in val_cols:
            row_dict[c] = r[c]
        rows.append(row_dict)

    pdf = pd.DataFrame(rows)

    # 数値列を数値化（%行は落としているが念のため）
    for c in val_cols:
        pdf[c] = pd.to_numeric(pdf[c], errors="coerce").fillna(0)

    return pdf


# =========================================================
#  合計行(親)を削除して leaf だけにする（在留資格側）
#   ※不法入国・上陸／不法在留など「在留資格が無い」leaf は残る
# =========================================================
def keep_leaf_only(pdf: pd.DataFrame) -> pd.DataFrame:
    parent_paths = set(pdf["parent_path"].dropna()) - {""}
    leaf = pdf[~pdf["path"].isin(parent_paths)].copy()
    leaf = leaf.reset_index(drop=True)
    return leaf


# =========================================================
#  正規滞在の階層ズレ補正
#   - "正規滞在/短期滞在" を "正規滞在/正規滞在/短期滞在" にする
#   - これで (区分, 詳細, 在留資格) が不法側と同じ 3 段になる
# =========================================================
def normalize_legal_hierarchy(leaf: pd.DataFrame) -> pd.DataFrame:
    new_paths = []
    new_parents = []

    for p in leaf["path"].astype(str).tolist():
        parts = p.split("/")
        if len(parts) == 2 and parts[0] == "正規滞在":
            parts = [parts[0], "正規滞在", parts[1]]
        new_p = "/".join(parts)
        new_paths.append(new_p)
        new_parents.append("/".join(parts[:-1]) if len(parts) >= 2 else "")

    leaf = leaf.copy()
    leaf["path"] = new_paths
    leaf["parent_path"] = new_parents
    return leaf


# =========================================================
#  罪種（val_cols）の「親＋子」が同時にある箇所を検知して
#  親−子合計=その他 を作り、親列は削除する
#
#  例:
#   "凶悪犯/強盗" と "凶悪犯/強盗/侵入強盗" がある → "凶悪犯/強盗/その他" を追加し、"凶悪犯/強盗" は落とす
# =========================================================
def add_crime_others_and_drop_parents(df_wide: pd.DataFrame, val_cols: list[str], tol: float = 0.5):
    cols = list(val_cols)

    # 分割情報
    parts_map = {c: c.split("/") for c in cols}
    depth_map = {c: len(parts_map[c]) for c in cols}

    # 親候補：自分より深い子が存在するもの
    parents = []
    for c in cols:
        prefix = c + "/"
        has_child = any((cc.startswith(prefix) and depth_map[cc] == depth_map[c] + 1) for cc in cols)
        if has_child:
            parents.append(c)

    new_cols = cols[:]
    drop_cols = set()

    for parent in parents:
        parent_depth = depth_map[parent]
        prefix = parent + "/"
        children = [cc for cc in cols if cc.startswith(prefix) and depth_map[cc] == parent_depth + 1]
        if not children:
            continue

        other_col = parent + "/その他"
        parent_vals = df_wide[parent]
        children_sum = df_wide[children].sum(axis=1)
        diff = parent_vals - children_sum

        # 微小な負値は 0 扱い（丸め誤差）
        diff = diff.where(diff > tol, 0)

        df_wide[other_col] = diff
        new_cols.append(other_col)

        # 親は最終的に落とす
        drop_cols.add(parent)

    # 親列を削除
    kept_cols = [c for c in new_cols if c not in drop_cols]
    df_wide = df_wide.drop(columns=list(drop_cols), errors="ignore")

    return df_wide, kept_cols


# =========================================================
#  出力整形：在留パス→(区分/詳細/在留資格), 罪種パス→(罪種00/01/02)
# =========================================================
def finalize_tidy(df_long: pd.DataFrame, year: str) -> pd.DataFrame:
    # 在留側（3段）
    r_parts = df_long["residency_path"].astype(str).str.split("/", expand=True)
    # 足りない列は None
    while r_parts.shape[1] < 3:
        r_parts[r_parts.shape[1]] = None
    r_parts = r_parts.iloc[:, :3]
    r_parts.columns = ["正規・非正規区分", "正規・非正規詳細", "在留資格"]

    # 不法入国・上陸 / 不法在留 など在留資格が無いものは空欄に
    r_parts["在留資格"] = r_parts["在留資格"].fillna("")

    # 罪種側（最大3段：罪種00〜02）
    c_parts = df_long["crime_path"].astype(str).str.split("/", expand=True)
    while c_parts.shape[1] < 3:
        c_parts[c_parts.shape[1]] = None
    c_parts = c_parts.iloc[:, :3]
    c_parts.columns = ["罪種00", "罪種01", "罪種02"]

    out = pd.concat([r_parts, c_parts], axis=1)
    out.insert(0, "年", year)

    out["検挙人員"] = pd.to_numeric(df_long["検挙人員"], errors="coerce").fillna(0)

    # 0 は基本的に不要なら落とす（必要ならコメントアウトしてください）
    out = out[out["検挙人員"] != 0].copy()

    # 列順（あなた指定）
    out = out[["年", "正規・非正規区分", "正規・非正規詳細", "在留資格", "罪種00", "罪種01", "罪種02", "検挙人員"]]

    return out.reset_index(drop=True)


# =========================================================
#  1年分処理（複数シート対応）
# =========================================================
def process_one_year(cfg: dict) -> None:
    input_path = resolve_input_path(cfg["input_file"])
    output_path = OUTPUT_DIR / cfg["output_file"]
    year = str(cfg["year"])
    check_val = cfg.get("check_val", 0)

    all_tidy = []

    for sh in cfg["sheets"]:
        # --- 読み込み ---
        raw0 = read_table(
            input_path=input_path,
            sheet_name=sh.get("sheet_name"),
            use_row=sh["use_row"],
            usecols=sh["usecols"],
        )

        cat_cols = sh["cat_cols"]
        val_cols = sh["val_cols"]

        # 列名付与
        raw0.columns = cat_cols + val_cols

        # 文字列整形（カテゴリ側だけ）
        for c in cat_cols:
            raw0[c] = raw0[c].map(clean_str)

        # --- 在留側：階層パス生成 → leaf のみ ---
        pdf = build_residency_paths(raw0, cat_cols=cat_cols, val_cols=val_cols)
        leaf = keep_leaf_only(pdf)

        # 正規滞在の階層補正
        leaf = normalize_legal_hierarchy(leaf)

        # --- 罪種側：その他作成＆親列削除（wide のまま行う） ---
        leaf2, val_cols2 = add_crime_others_and_drop_parents(leaf, val_cols=val_cols, tol=0.5)

        # --- tidy（ロング化） ---
        df_long = leaf2.melt(
            id_vars=["path"],
            value_vars=val_cols2,
            var_name="crime_path",
            value_name="検挙人員",
        ).rename(columns={"path": "residency_path"})

        # 出力整形
        tidy = finalize_tidy(df_long, year=year)
        all_tidy.append(tidy)

    df_out = pd.concat(all_tidy, ignore_index=True)

    # ======== 合計値チェック ========
    tidy_sum = df_out["検挙人員"].sum()
    diff_val = check_val - tidy_sum

    # ======== 保存 ========
    df_out.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"処理完了: {year}年分, tidy合計={tidy_sum}, check_val={check_val}, 差分={diff_val}")


def main():
    for cfg in SHEET_CONFIGS:
        process_one_year(cfg)
    print("全ての処理が完了しました")


if __name__ == "__main__":
    main()


