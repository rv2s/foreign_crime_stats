# 在留資格別の推計派遣・請負労働者割合を算出するコード

from pathlib import Path

import pandas as pd


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
INPUT_DIR = BASE_PATH / "06_research" / "dispatch_worker_estimation" / "01_tidy"
OUTPUT_DIR = BASE_PATH / "06_research" / "dispatch_worker_estimation" / "02_intermediate"

INPUT_TABLE4 = INPUT_DIR / "01_別表4_業種別外国人労働者数_tidy.csv"
INPUT_TABLE6 = INPUT_DIR / "02_別表6_在留資格別業種構成比_tidy.csv"
INPUT_LABOR_FORCE_SURVEY = INPUT_DIR / "03_労働力調査_派遣労働者割合_tidy.csv"

OUTPUT_SUMMARY = OUTPUT_DIR / "01_在留資格別_推計派遣労働者割合.csv"


def choose_composition_column(df: pd.DataFrame) -> str:
    """計算に使う業種構成比列を選ぶ。"""
    if "業種構成比_pct" in df.columns:
        sums = df.groupby("在留資格")["業種構成比_pct"].sum()
        if sums.between(0.5, 1.2).all():
            return "業種構成比_pct"

    return "業種構成比"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    table4 = pd.read_csv(INPUT_TABLE4)
    table6 = pd.read_csv(INPUT_TABLE6)
    labor_force_survey = pd.read_csv(INPUT_LABOR_FORCE_SURVEY)

    composition_col = choose_composition_column(table6)

    table4_use = table4[
        [
            "年",
            "業種",
            "外国人労働者数",
            "外国人労働者数_派遣及び請負事業",
            "外国人労働者_派遣及び請負事業割合",
        ]
    ].copy()

    table6_use = table6[["年", "在留資格", "業種", composition_col]].copy()
    table6_use = table6_use.rename(columns={composition_col: "業種構成比_計算用"})

    detail = table6_use.merge(table4_use, on=["年", "業種"], how="left", validate="many_to_one")
    if detail["外国人労働者_派遣及び請負事業割合"].isna().any():
        missing_industries = sorted(detail.loc[detail["外国人労働者_派遣及び請負事業割合"].isna(), "業種"].unique())
        raise ValueError(f"別表4に存在しない業種があります: {missing_industries}")

    detail["推計派遣労働者割合寄与"] = (
        detail["業種構成比_計算用"] * detail["外国人労働者_派遣及び請負事業割合"]
    )

    covered_industries = set(table6_use["業種"].unique())
    other_table4 = table4_use[~table4_use["業種"].isin(covered_industries)].copy()
    other_worker_count = other_table4["外国人労働者数"].sum()
    other_dispatch_count = other_table4["外国人労働者数_派遣及び請負事業"].sum()
    other_dispatch_share = other_dispatch_count / other_worker_count

    covered_composition = (
        detail.groupby(["年", "在留資格"], as_index=False)["業種構成比_計算用"]
        .sum()
        .rename(columns={"業種構成比_計算用": "掲載業種構成比合計"})
    )
    other_rows = covered_composition.copy()
    other_rows["業種"] = "その他業種（別表6未掲載業種）"
    other_rows["業種構成比_計算用"] = 1 - other_rows["掲載業種構成比合計"]
    other_rows["外国人労働者数"] = other_worker_count
    other_rows["外国人労働者数_派遣及び請負事業"] = other_dispatch_count
    other_rows["外国人労働者_派遣及び請負事業割合"] = other_dispatch_share
    other_rows["推計派遣労働者割合寄与"] = (
        other_rows["業種構成比_計算用"] * other_rows["外国人労働者_派遣及び請負事業割合"]
    )
    other_rows = other_rows.drop(columns=["掲載業種構成比合計"])

    detail_with_other = pd.concat([detail, other_rows], ignore_index=True)

    summary = (
        detail_with_other.groupby(["年", "在留資格"], as_index=False)
        .agg(
            対象業種数=("業種", "count"),
            業種構成比合計=("業種構成比_計算用", "sum"),
            推計派遣労働者割合=("推計派遣労働者割合寄与", "sum"),
        )
        .sort_values("推計派遣労働者割合", ascending=False)
        .reset_index(drop=True)
    )

    labor_force_dispatch_share = labor_force_survey.loc[
        labor_force_survey["対象"] == "全体", "派遣労働者割合"
    ].iloc[0]

    overall_row = pd.DataFrame(
        [
            {
                "年": int(labor_force_survey.loc[labor_force_survey["対象"] == "全体", "年"].iloc[0]),
                "在留資格": "日本全体",
                "対象業種数": pd.NA,
                "業種構成比合計": pd.NA,
                "推計派遣労働者割合": labor_force_dispatch_share,
            }
        ]
    )
    summary = pd.concat([summary, overall_row], ignore_index=True)
    summary = summary.sort_values("推計派遣労働者割合", ascending=False).reset_index(drop=True)

    summary = summary[
        [
            "年",
            "在留資格",
            "対象業種数",
            "業種構成比合計",
            "推計派遣労働者割合",
        ]
    ]

    summary.to_csv(OUTPUT_SUMMARY, index=False, encoding="utf-8-sig")

    print(f"計算使用列: {composition_col}")
    print(f"集計 行数: {len(summary)}")
    print(f"集計 保存先: {OUTPUT_SUMMARY}")
    print(f"労働力調査 全体派遣労働者割合: {labor_force_dispatch_share:.6f}")
    print(f"その他業種 派遣・請負割合: {other_dispatch_share:.6f}")


if __name__ == "__main__":
    main()
