# report2.md の「補足予定データ」のうち、既存データから作成できる表を出力するコード

from pathlib import Path

import pandas as pd


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
OUTPUT_DIR = BASE_PATH / "06_research" / "report_supplemental" / "01_tidy"

INPUT_ARRESTS = BASE_PATH / "04_integrated" / "09_検挙人員数_統合.csv"
INPUT_POPULATION = BASE_PATH / "04_integrated" / "15_人口_統合.csv"
INPUT_RAW_RATE = BASE_PATH / "05_analytics" / "20_1万人あたり検挙人員数及び対日本人倍率.csv"
INPUT_ADJUSTED_RATE = BASE_PATH / "05_analytics" / "33_対推定検挙人員及び年齢調整後対日本人倍率.csv"
INPUT_ILLEGAL = BASE_PATH / "02_standardized" / "14_不法残留者_名寄せ後.csv"
INPUT_ILLEGAL_MERGE = BASE_PATH / "01_tidy" / "99_merge" / "14_不法残留者_merge.csv"
INPUT_NON_VISITOR_NATIONALITY_RATE = (
    BASE_PATH
    / "06_research"
    / "non_visitor_nationality"
    / "01_tidy"
    / "03_来日外国人以外_国籍別_1万人あたり検挙人員数.csv"
)
INPUT_SPECIAL_PERMANENT_COMPOSITION = (
    BASE_PATH
    / "06_research"
    / "permanent_resident"
    / "02_intermediate"
    / "01_特別永住者_国籍構成.csv"
)
INPUT_SPECIAL_PERMANENT_RATE = (
    BASE_PATH
    / "06_research"
    / "permanent_resident"
    / "02_intermediate"
    / "04_来日外国人以外_特別永住者近似別_1万人あたり検挙人員数.csv"
)
INPUT_STATUS_POPULATION_TIDY_DIR = BASE_PATH / "01_tidy" / "10_人口_在留資格別"


STATUS_ORDER = [
    "日本人",
    "外国人計",
    "来日外国人計",
    "永住者等",
    "定住者",
    "日本人の配偶者等",
    "技能実習",
    "留学",
    "短期滞在",
    "その他",
]


def make_display_label(df: pd.DataFrame) -> pd.Series:
    """区分列からレポート表示用ラベルを作成する。"""
    label = df["在留資格"].copy()
    label = label.where(label.notna() & (label != "計"), df["区分01"])
    label = label.where(label.notna() & (label != "計"), df["区分00"])
    return label.replace(
        {
            "外国人": "外国人計",
            "来日外国人": "来日外国人計",
        }
    )


def add_display_label(df: pd.DataFrame) -> pd.DataFrame:
    """表示区分と表示順を付与する。"""
    df = df.copy()
    df["表示区分"] = make_display_label(df)
    df = df[df["表示区分"].isin(STATUS_ORDER)].copy()
    df["表示区分"] = pd.Categorical(df["表示区分"], categories=STATUS_ORDER, ordered=True)
    return df


def aggregate_arrests_for_status(df_arrests: pd.DataFrame) -> pd.DataFrame:
    """検挙人員を主要区分・在留資格別に集計する。"""
    dimensions = ["区分00", "区分01", "在留資格", "罪種00", "罪種01"]
    hierarchies = [
        ["区分00", "罪種00", "罪種01"],
        ["区分00", "区分01", "罪種00", "罪種01"],
        ["区分00", "区分01", "在留資格", "罪種00", "罪種01"],
    ]

    frames = []
    status_columns = {"区分00", "区分01", "在留資格"}
    for hierarchy in hierarchies:
        group_columns = ["年"] + hierarchy
        required_status_columns = [column for column in hierarchy if column in status_columns]
        target = df_arrests.copy()
        if required_status_columns:
            target = target.dropna(subset=required_status_columns)
        grouped = target.groupby(group_columns, as_index=False, dropna=False)["検挙人員"].sum()
        for column in dimensions:
            if column not in grouped.columns:
                grouped[column] = "計"
        frames.append(grouped[["年"] + dimensions + ["検挙人員"]])

    return add_display_label(pd.concat(frames, ignore_index=True))


def create_status_crime_composition(df_arrests: pd.DataFrame) -> pd.DataFrame:
    """在留資格別・罪種大分類別の検挙人員構成比を作成する。"""
    df = aggregate_arrests_for_status(df_arrests)
    df = (
        df.groupby(["年", "表示区分", "罪種00"], as_index=False, observed=True)["検挙人員"]
        .sum()
    )
    df["総検挙人員"] = df.groupby(["年", "表示区分"], observed=True)["検挙人員"].transform("sum")
    df["構成比"] = df["検挙人員"] / df["総検挙人員"]
    df["構成比_pct"] = df["構成比"] * 100
    return df.sort_values(["年", "表示区分", "罪種00"]).reset_index(drop=True)


def create_status_age_composition(df_population: pd.DataFrame) -> pd.DataFrame:
    """在留資格別・年代別の人口構成比を作成する。"""
    df = add_display_label(df_population)
    df = (
        df.groupby(["年", "表示区分", "年代"], as_index=False, observed=True)["人数"]
        .sum()
    )
    df["総人数"] = df.groupby(["年", "表示区分"], observed=True)["人数"].transform("sum")
    df["構成比"] = df["人数"] / df["総人数"]
    df["構成比_pct"] = df["構成比"] * 100
    return df.sort_values(["年", "表示区分", "年代"]).reset_index(drop=True)


def create_population_status_composition(df_population: pd.DataFrame) -> pd.DataFrame:
    """外国人人口の在留資格別構成比を作成する。"""
    df = add_display_label(df_population[df_population["区分00"] == "外国人"])
    df = (
        df.groupby(["年", "表示区分"], as_index=False, observed=True)["人数"]
        .sum()
    )
    df = df[~df["表示区分"].isin(["外国人計"])].copy()
    df["外国人総数"] = df.groupby("年", observed=True)["人数"].transform("sum")
    df["構成比"] = df["人数"] / df["外国人総数"]
    df["構成比_pct"] = df["構成比"] * 100
    return df.sort_values(["年", "表示区分"]).reset_index(drop=True)


def create_illegal_status_composition(df_illegal: pd.DataFrame) -> pd.DataFrame:
    """不法残留者の在留資格別構成比を作成する。"""
    df = df_illegal.dropna(subset=["在留資格"]).copy()
    df = df.groupby(["年", "在留資格"], as_index=False, dropna=False)["人数"].sum()
    df["不法残留者総数"] = df.groupby("年")["人数"].transform("sum")
    df["構成比"] = df["人数"] / df["不法残留者総数"]
    df["構成比_pct"] = df["構成比"] * 100
    return df.sort_values(["年", "在留資格"]).reset_index(drop=True)


def create_illegal_nationality_composition(df_illegal_merge: pd.DataFrame) -> pd.DataFrame:
    """不法残留者の国籍・地域別構成比を作成する。国籍列がある年のみ対象。"""
    df = df_illegal_merge.dropna(subset=["国籍・地域"]).copy()
    df = df.groupby(["年", "国籍・地域"], as_index=False, dropna=False)["人数"].sum()
    df["不法残留者総数"] = df.groupby("年")["人数"].transform("sum")
    df["構成比"] = df["人数"] / df["不法残留者総数"]
    df["構成比_pct"] = df["構成比"] * 100
    return df.sort_values(["年", "人数"], ascending=[True, False]).reset_index(drop=True)


def create_non_visitor_nationality_latest(df_rate: pd.DataFrame) -> pd.DataFrame:
    """来日外国人以外の国籍別検挙人員割合について、最新年の罪種合計を抽出する。"""
    df = df_rate[(df_rate["罪種00"] == "計") & (df_rate["罪種01"] == "計")].copy()
    latest_year = df["年"].max()
    df = df[df["年"] == latest_year].copy()
    return df.sort_values("検挙人員数_1万人あたり", ascending=False).reset_index(drop=True)


def create_special_permanent_summary(
    df_composition: pd.DataFrame,
    df_rate: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """特別永住者近似の国籍構成と検挙人員割合の最新年表を作成する。"""
    latest_comp_year = df_composition["年"].max()
    comp = df_composition[df_composition["年"] == latest_comp_year].copy()
    comp = comp.sort_values("人口", ascending=False).reset_index(drop=True)

    rate = df_rate[(df_rate["罪種00"] == "計") & (df_rate["罪種01"] == "計")].copy()
    latest_rate_year = rate["年"].max()
    rate = rate[rate["年"] == latest_rate_year].copy()
    rate = rate.sort_values("検挙人員数_1万人あたり", ascending=False).reset_index(drop=True)
    return comp, rate


def create_current_impact(df_raw_rate: pd.DataFrame, df_adjusted_rate: pd.DataFrame) -> pd.DataFrame:
    """現時点の外国人比率と対日本人倍率を用いた日本全体への影響倍率を作成する。"""
    raw = df_raw_rate[
        (df_raw_rate["罪種00"] == "計")
        & (df_raw_rate["罪種01"] == "計")
        & (df_raw_rate["区分00"].isin(["日本人", "外国人"]))
        & (df_raw_rate["区分01"] == "計")
        & (df_raw_rate["在留資格"] == "計")
    ].copy()
    latest_year = raw["年"].max()
    raw = raw[raw["年"] == latest_year].copy()

    japanese_population = raw.loc[raw["区分00"] == "日本人", "人数"].iloc[0]
    foreign_population = raw.loc[raw["区分00"] == "外国人", "人数"].iloc[0]
    total_population = japanese_population + foreign_population
    foreign_share = foreign_population / total_population

    foreign_raw_ratio = raw.loc[raw["区分00"] == "外国人", "対日本人倍率"].iloc[0]

    adjusted = df_adjusted_rate[
        (df_adjusted_rate["年"] == latest_year)
        & (df_adjusted_rate["罪種00"] == "計")
        & (df_adjusted_rate["罪種01"] == "計")
        & (df_adjusted_rate["区分00"] == "外国人")
        & (df_adjusted_rate["区分01"] == "計")
        & (df_adjusted_rate["在留資格"] == "計")
    ]
    foreign_adjusted_ratio = adjusted["対日本人倍率_年齢調整後"].iloc[0]

    rows = []
    for ratio_type, foreign_ratio in [
        ("年齢調整前", foreign_raw_ratio),
        ("年齢調整後", foreign_adjusted_ratio),
    ]:
        impact = (1 - foreign_share) * 1 + foreign_share * foreign_ratio
        rows.append(
            {
                "年": latest_year,
                "倍率種別": ratio_type,
                "日本人人口": japanese_population,
                "外国人人口": foreign_population,
                "総人口": total_population,
                "外国人比率": foreign_share,
                "外国人比率_pct": foreign_share * 100,
                "外国人_対日本人倍率": foreign_ratio,
                "日本全体への影響倍率": impact,
            }
        )
    return pd.DataFrame(rows)


def create_foreign_share_scenario(df_current_impact: pd.DataFrame) -> pd.DataFrame:
    """外国人比率別の単純な影響倍率表を作成する。"""
    ratios = df_current_impact[["倍率種別", "外国人_対日本人倍率"]].drop_duplicates()
    rows = []
    for foreign_share_pct in range(0, 31):
        foreign_share = foreign_share_pct / 100
        for row in ratios.itertuples(index=False):
            impact = (1 - foreign_share) * 1 + foreign_share * row.外国人_対日本人倍率
            rows.append(
                {
                    "外国人比率_pct": foreign_share_pct,
                    "倍率種別": row.倍率種別,
                    "外国人_対日本人倍率": row.外国人_対日本人倍率,
                    "日本全体への影響倍率": impact,
                }
            )
    return pd.DataFrame(rows)


def load_latest_status_population_tidy() -> pd.DataFrame:
    """国籍・都道府県・性別が残っている最新年の在留資格別人口tidyデータを読み込む。"""
    files = sorted(INPUT_STATUS_POPULATION_TIDY_DIR.glob("10_*_tidy.csv"))
    candidate_files = []
    for file in files:
        try:
            year = int(file.stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        candidate_files.append((year, file))

    if not candidate_files:
        raise FileNotFoundError("在留資格別人口のtidyファイルが見つかりません。")

    latest_year, latest_file = max(candidate_files, key=lambda item: item[0])
    df = pd.read_csv(latest_file, encoding="utf-8-sig")
    required_columns = {"年", "国籍・地域", "在留資格", "性別", "年齢", "都道府県", "人口"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"{latest_file} に必要列がありません: {sorted(missing_columns)}")

    if df["年"].max() != latest_year:
        raise ValueError(f"ファイル名の年とデータ内の年が一致しません: {latest_file}")
    return df


def normalize_status_for_latest_population(status: str) -> str:
    """最新年の細かい在留資格をレポート用区分に寄せる。"""
    if pd.isna(status):
        return "その他"
    status = str(status)
    if status.startswith("技能実習"):
        return "技能実習"
    if status in {"定住者", "日本人の配偶者等", "留学"}:
        return status
    if status in {"永住者", "特別永住者", "永住者の配偶者等"}:
        return "永住者等"
    return "その他"


def normalize_age_to_group(age: str) -> str:
    """年齢表記を分析用の年代に変換する。"""
    if pd.isna(age):
        return "不詳"
    text = str(age).strip()
    if text in {"不詳", "不明"}:
        return "不詳"
    if "以上" in text:
        number = int("".join(ch for ch in text if ch.isdigit()))
    else:
        digits = "".join(ch for ch in text if ch.isdigit())
        if not digits:
            return "不詳"
        number = int(digits)

    if number <= 13:
        return "0~13歳"
    if number <= 19:
        return "10代(14歳以上)"
    if number <= 29:
        return "20代"
    if number <= 39:
        return "30代"
    if number <= 49:
        return "40代"
    if number <= 59:
        return "50代"
    if number <= 69:
        return "60代"
    return "70代以上"


def add_latest_population_status_label(df: pd.DataFrame) -> pd.DataFrame:
    """最新年在留資格別人口にレポート用表示区分を付与する。"""
    df = df.copy()
    df["表示区分"] = df["在留資格"].map(normalize_status_for_latest_population)
    df = df[df["表示区分"].isin(["永住者等", "定住者", "日本人の配偶者等", "技能実習", "留学", "その他"])].copy()
    return df


def create_status_nationality_latest(df_latest_population: pd.DataFrame) -> pd.DataFrame:
    """最新年の在留資格別・国籍地域別人口構成比を作成する。"""
    df = add_latest_population_status_label(df_latest_population)
    df = (
        df.groupby(["年", "表示区分", "国籍・地域"], as_index=False, dropna=False)["人口"]
        .sum()
    )
    df["総人口"] = df.groupby(["年", "表示区分"])["人口"].transform("sum")
    df["構成比"] = df["人口"] / df["総人口"]
    df["構成比_pct"] = df["構成比"] * 100
    return df.sort_values(["表示区分", "人口"], ascending=[True, False]).reset_index(drop=True)


def create_status_prefecture_latest(df_latest_population: pd.DataFrame) -> pd.DataFrame:
    """最新年の在留資格別・都道府県別人口構成比を作成する。"""
    df = add_latest_population_status_label(df_latest_population)
    df = (
        df.groupby(["年", "表示区分", "都道府県"], as_index=False, dropna=False)["人口"]
        .sum()
    )
    df["総人口"] = df.groupby(["年", "表示区分"])["人口"].transform("sum")
    df["構成比"] = df["人口"] / df["総人口"]
    df["構成比_pct"] = df["構成比"] * 100
    return df.sort_values(["表示区分", "人口"], ascending=[True, False]).reset_index(drop=True)


def create_status_sex_age_latest(df_latest_population: pd.DataFrame) -> pd.DataFrame:
    """最新年の在留資格別・男女年代別人口構成比を作成する。"""
    df = add_latest_population_status_label(df_latest_population)
    df["年代"] = df["年齢"].map(normalize_age_to_group)
    df = (
        df.groupby(["年", "表示区分", "性別", "年代"], as_index=False, dropna=False)["人口"]
        .sum()
    )
    df["総人口"] = df.groupby(["年", "表示区分"])["人口"].transform("sum")
    df["構成比"] = df["人口"] / df["総人口"]
    df["構成比_pct"] = df["構成比"] * 100
    return df.sort_values(["表示区分", "性別", "年代"]).reset_index(drop=True)


def create_availability_table() -> pd.DataFrame:
    """補足予定データのうち、現プロジェクト内で作成できたものと未作成のものを整理する。"""
    rows = [
        ("技能実習・留学の罪種別構成", "作成済み", "01_在留資格別_罪種構成_年別.csv"),
        ("技能実習・留学の国籍別構成", "作成済み", "11_在留資格別_国籍地域別構成_最新年.csv"),
        ("技能実習・留学の失踪者数", "未作成", "外部データが必要"),
        ("技能実習・留学の退去強制・在留資格取消件数", "未作成", "外部データが必要"),
        ("短期滞在者の国籍別検挙人員割合", "未作成", "現データに短期滞在者の国籍別人口が不足"),
        ("短期滞在者の罪種別構成", "作成済み", "01_在留資格別_罪種構成_年別.csv"),
        ("短期滞在から不法残留へ移行した人数", "未作成", "外部データまたは個票に近い遷移情報が必要"),
        ("定住者の国籍別構成", "作成済み", "11_在留資格別_国籍地域別構成_最新年.csv"),
        ("定住者の就労形態・所得分布", "未作成", "外部データが必要"),
        ("外国籍児童生徒の不就学・日本語指導必要者数", "未作成", "外部データが必要"),
        ("日本人の配偶者等の国籍別構成", "作成済み", "11_在留資格別_国籍地域別構成_最新年.csv"),
        ("日本人の配偶者等の男女別・年代別構成", "作成済み", "13_在留資格別_男女年代構成_最新年.csv"),
        ("国際結婚・離婚件数の推移", "未作成", "外部データが必要"),
        ("DV相談・生活困窮関連データ", "未作成", "外部データが必要"),
        ("永住者等の内訳", "一部作成済み", "07_特別永住者_国籍構成_最新年.csv"),
        ("特別永住者の国籍別構成", "作成済み", "07_特別永住者_国籍構成_最新年.csv"),
        ("永住者等の国籍別検挙人員割合", "一部作成済み", "06_来日外国人以外_国籍別検挙人員割合_最新年.csv"),
        ("地域別の人口集中", "作成済み", "12_在留資格別_都道府県別構成_最新年.csv"),
        ("地域別の就労構造", "未作成", "外部データが必要"),
        ("不法残留者の在留資格別構成", "作成済み", "04_不法残留者_在留資格別構成_年別.csv"),
        ("不法残留者の国籍別構成", "作成済み", "05_不法残留者_国籍地域別構成_年別.csv"),
        ("外国人比率別の日本全体への影響倍率", "作成済み", "10_外国人比率別_日本全体への影響倍率.csv"),
    ]
    return pd.DataFrame(rows, columns=["補足予定データ", "作成状況", "出力ファイルまたは理由"])


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_arrests = pd.read_csv(INPUT_ARRESTS, encoding="utf-8-sig")
    df_population = pd.read_csv(INPUT_POPULATION, encoding="utf-8-sig")
    df_raw_rate = pd.read_csv(INPUT_RAW_RATE, encoding="utf-8-sig")
    df_adjusted_rate = pd.read_csv(INPUT_ADJUSTED_RATE, encoding="utf-8-sig")
    df_illegal = pd.read_csv(INPUT_ILLEGAL, encoding="utf-8-sig")
    df_illegal_merge = pd.read_csv(INPUT_ILLEGAL_MERGE, encoding="utf-8-sig")
    df_non_visitor_rate = pd.read_csv(INPUT_NON_VISITOR_NATIONALITY_RATE, encoding="utf-8-sig")
    df_special_comp = pd.read_csv(INPUT_SPECIAL_PERMANENT_COMPOSITION, encoding="utf-8-sig")
    df_special_rate = pd.read_csv(INPUT_SPECIAL_PERMANENT_RATE, encoding="utf-8-sig")
    df_latest_population_tidy = load_latest_status_population_tidy()

    outputs: list[Path] = []

    output = OUTPUT_DIR / "00_補足予定データ_作成可否一覧.csv"
    create_availability_table().to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "01_在留資格別_罪種構成_年別.csv"
    create_status_crime_composition(df_arrests).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "02_在留資格別_年代構成_年別.csv"
    create_status_age_composition(df_population).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "03_外国人人口_在留資格別構成_年別.csv"
    create_population_status_composition(df_population).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "04_不法残留者_在留資格別構成_年別.csv"
    create_illegal_status_composition(df_illegal).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "05_不法残留者_国籍地域別構成_年別.csv"
    create_illegal_nationality_composition(df_illegal_merge).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "06_来日外国人以外_国籍別検挙人員割合_最新年.csv"
    create_non_visitor_nationality_latest(df_non_visitor_rate).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    special_comp, special_rate = create_special_permanent_summary(df_special_comp, df_special_rate)

    output = OUTPUT_DIR / "07_特別永住者_国籍構成_最新年.csv"
    special_comp.to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "08_来日外国人以外_特別永住者近似別検挙人員割合_最新年.csv"
    special_rate.to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    current_impact = create_current_impact(df_raw_rate, df_adjusted_rate)
    output = OUTPUT_DIR / "09_現状_外国人比率と日本全体への影響倍率.csv"
    current_impact.to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "10_外国人比率別_日本全体への影響倍率.csv"
    create_foreign_share_scenario(current_impact).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "11_在留資格別_国籍地域別構成_最新年.csv"
    create_status_nationality_latest(df_latest_population_tidy).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "12_在留資格別_都道府県別構成_最新年.csv"
    create_status_prefecture_latest(df_latest_population_tidy).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    output = OUTPUT_DIR / "13_在留資格別_男女年代構成_最新年.csv"
    create_status_sex_age_latest(df_latest_population_tidy).to_csv(output, index=False, encoding="utf-8-sig")
    outputs.append(output)

    for output in outputs:
        print(output)
    print("処理完了")


if __name__ == "__main__":
    main()
