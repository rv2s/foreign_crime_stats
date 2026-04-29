# 日本人の配偶者等の人口構成比を可視化するコード

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
SUPPLEMENTAL_DIR = BASE_PATH / "06_reseach" / "report_supplemental"
OUTPUT_DIR = BASE_PATH / "06_research" / "japanese_spouse" / "01_tidy"
VIS_DIR = BASE_PATH / "06_research" / "japanese_spouse" / "03_output" / "png"

INPUT_NATIONALITY = SUPPLEMENTAL_DIR / "11_在留資格別_国籍地域別構成_最新年.csv"
INPUT_GENDER_AGE = SUPPLEMENTAL_DIR / "13_在留資格別_男女年代構成_最新年.csv"
INPUT_ARRESTS_BY_STATUS_NATIONALITY = (
    BASE_PATH / "00_raw" / "999_reseach" / "在留資格別国籍別検挙人員数" / "r6toukeisotai0316.csv"
)

TARGET_YEAR = 2024
TARGET_STATUS = "日本人の配偶者等"
TOP_N_NATIONALITIES = 10

AGE_ORDER = [
    "0~13歳",
    "10代(14歳以上)",
    "20代",
    "30代",
    "40代",
    "50代",
    "60代",
    "70代以上",
]
AGE_COLORS = {
    "0~13歳": "#4C78A8",
    "10代(14歳以上)": "#72B7B2",
    "20代": "#54A24B",
    "30代": "#F2CF5B",
    "40代": "#E45756",
    "50代": "#B279A2",
    "60代": "#F58518",
    "70代以上": "#9D755D",
}
GENDER_ORDER = ["男", "女", "その他"]
GENDER_COLORS = {
    "男": "#4C78A8",
    "女": "#E45756",
    "その他": "#7F7F7F",
}
NATIONALITY_COLORS = [
    "#4C78A8",
    "#E45756",
    "#54A24B",
    "#F2CF5B",
    "#72B7B2",
    "#B279A2",
    "#F58518",
    "#9D755D",
    "#BAB0AC",
    "#8CD17D",
    "#BFBFBF",
]
ARREST_NATIONALITY_ORDER = ["中国", "フィリピン", "韓国", "ブラジル", "トルコ", "その他"]


def convert_japanese_era_year(value) -> int:
    text = str(value).strip()
    if text.startswith("H"):
        return 1988 + int(text.replace("H", ""))
    if text.startswith("R"):
        year_text = text.replace("R", "")
        year = 1 if year_text == "元" else int(year_text)
        return 2018 + year
    raise ValueError(f"想定外の年表記です: {value}")


def to_number(value) -> int:
    if pd.isna(value):
        return 0
    text = str(value).strip().replace(",", "")
    if text in {"", "-", "－", "―", "−"}:
        return 0
    return int(float(text))


def setup_plot_style() -> None:
    selected_font = None
    for font_name in ["Yu Gothic", "Meiryo", "MS Gothic", "Noto Sans CJK JP"]:
        if any(font_name in font.name for font in font_manager.fontManager.ttflist):
            selected_font = font_name
            break
    if selected_font is None:
        selected_font = "sans-serif"

    sns.set_theme(
        style="whitegrid",
        font=selected_font,
        rc={"font.family": selected_font, "axes.unicode_minus": False},
    )
    plt.rcParams["font.family"] = selected_font
    plt.rcParams["axes.unicode_minus"] = False


def save_figure(fig: plt.Figure, output_file: Path) -> None:
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def load_age_composition() -> pd.DataFrame:
    df = pd.read_csv(INPUT_GENDER_AGE, encoding="utf-8-sig")
    df = df[(df["年"] == TARGET_YEAR) & (df["表示区分"] == TARGET_STATUS)].copy()
    df = (
        df.groupby(["年", "表示区分", "年代"], as_index=False)["人口"]
        .sum()
        .rename(columns={"人口": "人数"})
    )
    total_population = df["人数"].sum()
    df["総人数"] = total_population
    df["構成比"] = df["人数"] / total_population
    df["構成比_pct"] = df["構成比"] * 100
    df["年代"] = pd.Categorical(df["年代"], categories=AGE_ORDER, ordered=True)
    return df.sort_values("年代").reset_index(drop=True)


def load_nationality_composition() -> pd.DataFrame:
    df = pd.read_csv(INPUT_NATIONALITY, encoding="utf-8-sig")
    df = df[(df["年"] == TARGET_YEAR) & (df["表示区分"] == TARGET_STATUS)].copy()
    df = df.sort_values("人口", ascending=False).reset_index(drop=True)

    top = df.head(TOP_N_NATIONALITIES).copy()
    others = df.iloc[TOP_N_NATIONALITIES:].copy()
    if not others.empty:
        other_population = others["人口"].sum()
        total_population = df["人口"].sum()
        top = pd.concat(
            [
                top,
                pd.DataFrame(
                    [
                        {
                            "年": TARGET_YEAR,
                            "表示区分": TARGET_STATUS,
                            "国籍・地域": "その他",
                            "人口": other_population,
                            "総人口": total_population,
                            "構成比": other_population / total_population,
                            "構成比_pct": other_population / total_population * 100,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return top.reset_index(drop=True)


def load_gender_composition() -> pd.DataFrame:
    df = pd.read_csv(INPUT_GENDER_AGE, encoding="utf-8-sig")
    df = df[(df["年"] == TARGET_YEAR) & (df["表示区分"] == TARGET_STATUS)].copy()
    df = (
        df.groupby(["年", "表示区分", "性別"], as_index=False)["人口"]
        .sum()
        .sort_values("人口", ascending=False)
    )
    total_population = df["人口"].sum()
    df["総人口"] = total_population
    df["構成比"] = df["人口"] / total_population
    df["構成比_pct"] = df["構成比"] * 100
    df["性別"] = pd.Categorical(df["性別"], categories=GENDER_ORDER, ordered=True)
    return df.sort_values("性別").reset_index(drop=True)


def load_gender_age_composition() -> pd.DataFrame:
    df = pd.read_csv(INPUT_GENDER_AGE, encoding="utf-8-sig")
    df = df[
        (df["年"] == TARGET_YEAR)
        & (df["表示区分"] == TARGET_STATUS)
        & (df["性別"].isin(["男", "女"]))
    ].copy()
    df = df.groupby(["年", "表示区分", "性別", "年代"], as_index=False)["人口"].sum()

    all_rows = pd.MultiIndex.from_product(
        [[TARGET_YEAR], [TARGET_STATUS], ["男", "女"], AGE_ORDER],
        names=["年", "表示区分", "性別", "年代"],
    ).to_frame(index=False)
    df = pd.merge(all_rows, df, on=["年", "表示区分", "性別", "年代"], how="left")
    df["人口"] = df["人口"].fillna(0)
    df["性別総人口"] = df.groupby(["年", "表示区分", "性別"])["人口"].transform("sum")
    df["構成比"] = df["人口"] / df["性別総人口"]
    df["構成比_pct"] = df["構成比"] * 100
    df["性別"] = pd.Categorical(df["性別"], categories=["男", "女"], ordered=True)
    df["年代"] = pd.Categorical(df["年代"], categories=AGE_ORDER, ordered=True)
    return df.sort_values(["性別", "年代"]).reset_index(drop=True)


def load_japanese_spouse_arrests_by_nationality() -> pd.DataFrame:
    raw = pd.read_csv(INPUT_ARRESTS_BY_STATUS_NATIONALITY, header=None, encoding="cp932")
    df = raw.iloc[53:61, 0:12].copy().reset_index(drop=True)
    header = df.iloc[0]
    years = [convert_japanese_era_year(value) for value in header.iloc[2:]]

    body = df.iloc[1:].copy()
    nationality_col = body.columns[1]
    body = body.rename(columns={nationality_col: "国籍・地域"})
    body["国籍・地域"] = body["国籍・地域"].astype("string").str.strip()
    body = body[(body["国籍・地域"].notna()) & (body["国籍・地域"] != "") & (body["国籍・地域"] != "総数")].copy()

    value_columns = list(body.columns[2:])
    body = body.rename(columns=dict(zip(value_columns, years, strict=True)))
    tidy = body.melt(
        id_vars=["国籍・地域"],
        value_vars=years,
        var_name="年",
        value_name="検挙人員",
    )
    tidy["検挙人員"] = tidy["検挙人員"].map(to_number)
    tidy["表示区分"] = TARGET_STATUS
    tidy = tidy[tidy["年"] == TARGET_YEAR].copy()
    tidy["国籍・地域"] = pd.Categorical(tidy["国籍・地域"], categories=ARREST_NATIONALITY_ORDER, ordered=True)
    return tidy.sort_values("国籍・地域").reset_index(drop=True)


def load_arrest_rate_by_nationality() -> pd.DataFrame:
    arrests = load_japanese_spouse_arrests_by_nationality()
    population = pd.read_csv(INPUT_NATIONALITY, encoding="utf-8-sig")
    population = population[(population["年"] == TARGET_YEAR) & (population["表示区分"] == TARGET_STATUS)].copy()

    listed_nationalities = [item for item in ARREST_NATIONALITY_ORDER if item != "その他"]
    listed_population = population[population["国籍・地域"].isin(listed_nationalities)][
        ["国籍・地域", "人口"]
    ].copy()
    other_population = population.loc[~population["国籍・地域"].isin(listed_nationalities), "人口"].sum()
    listed_population = pd.concat(
        [
            listed_population,
            pd.DataFrame([{"国籍・地域": "その他", "人口": other_population}]),
        ],
        ignore_index=True,
    )

    result = pd.merge(arrests, listed_population, on="国籍・地域", how="left", validate="1:1")
    missing_population = result.loc[result["人口"].isna(), "国籍・地域"].drop_duplicates()
    if not missing_population.empty:
        raise ValueError("人口が見つからない国籍があります: " + ", ".join(missing_population.astype(str).tolist()))

    result["検挙人員数_1万人あたり"] = result["検挙人員"] / result["人口"] * 10000
    result["国籍・地域"] = pd.Categorical(result["国籍・地域"], categories=ARREST_NATIONALITY_ORDER, ordered=True)
    return result.sort_values("国籍・地域").reset_index(drop=True)


def plot_arrest_rate_by_nationality(df: pd.DataFrame, output_file: Path) -> None:
    plot_df = df.sort_values("検挙人員数_1万人あたり", ascending=True).copy()
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    sns.barplot(
        data=plot_df,
        x="検挙人員数_1万人あたり",
        y="国籍・地域",
        hue="国籍・地域",
        palette="viridis",
        dodge=False,
        legend=False,
        ax=ax,
    )
    ax.set_title("日本人の配偶者等の国籍別1万人あたり検挙人員数（2024年）", pad=14)
    ax.set_xlabel("1万人あたり検挙人員数")
    ax.set_ylabel("国籍・地域")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    x_max = plot_df["検挙人員数_1万人あたり"].max()
    ax.set_xlim(0, x_max * 1.18)
    for index, row in enumerate(plot_df.itertuples(index=False)):
        value = getattr(row, "検挙人員数_1万人あたり")
        ax.text(
            value + x_max * 0.015,
            index,
            f"{value:.1f}",
            va="center",
            fontsize=9,
        )
    fig.text(
        0.01,
        0.01,
        "注: 国籍区分は警察庁表の区分に合わせ、中国・フィリピン・韓国・ブラジル・トルコ・その他で集計。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_gender_age_composition(df: pd.DataFrame, output_file: Path) -> None:
    pivot = (
        df.pivot(index="性別", columns="年代", values="構成比_pct")
        .reindex(["男", "女"])
        .reindex(columns=AGE_ORDER)
    )

    fig, ax = plt.subplots(figsize=(11, 4.8))
    left = pd.Series(0.0, index=pivot.index)
    for age_group in AGE_ORDER:
        values = pivot[age_group]
        bars = ax.barh(
            pivot.index.astype(str),
            values,
            left=left,
            color=AGE_COLORS[age_group],
            edgecolor="white",
            linewidth=0.8,
            label=age_group,
        )
        for bar, value, start in zip(bars, values, left):
            if value >= 5:
                ax.text(
                    start + value / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white" if age_group in {"0~13歳", "40代", "50代", "70代以上"} else "#222222",
                )
        left += values

    ax.set_title("日本人の配偶者等の男女別年代構成比（2024年）", pad=14)
    ax.set_xlabel("各性別内の構成比（%）")
    ax.set_ylabel("性別")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.invert_yaxis()
    ax.legend(title="年代", bbox_to_anchor=(0.5, -0.22), loc="upper center", ncol=4, frameon=False)
    fig.text(
        0.01,
        0.01,
        "注: 出入国在留管理庁「在留外国人統計」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    save_figure(fig, output_file)


def plot_stacked_single_bar(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    colors: dict[str, str] | list[str],
    title: str,
    output_file: Path,
    legend_title: str,
    min_label_pct: float = 4.0,
    xlabel: str = "構成比（%）",
) -> None:
    fig, ax = plt.subplots(figsize=(11, 3.8))
    left = 0.0
    for index, row in df.iterrows():
        label = str(row[label_column])
        value = float(row[value_column])
        color = colors[label] if isinstance(colors, dict) else colors[index % len(colors)]
        ax.barh(
            [TARGET_STATUS],
            [value],
            left=left,
            color=color,
            edgecolor="white",
            linewidth=0.9,
            label=label,
        )
        if value >= min_label_pct:
            ax.text(
                left + value / 2,
                0,
                f"{label}\n{value:.1f}%",
                ha="center",
                va="center",
                fontsize=9,
                color="white" if color not in {"#F2CF5B", "#BFBFBF", "#BAB0AC", "#8CD17D"} else "#222222",
            )
        left += value

    ax.set_title(title, pad=14)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.legend(title=legend_title, bbox_to_anchor=(0.5, -0.28), loc="upper center", ncol=4, frameon=False)
    fig.text(
        0.01,
        0.01,
        "注: 出入国在留管理庁「在留外国人統計」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    save_figure(fig, output_file)


def main() -> None:
    setup_plot_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    age = load_age_composition()
    age.to_csv(OUTPUT_DIR / "01_日本人の配偶者等_人口年齢構成比_2024.csv", index=False, encoding="utf-8-sig")
    plot_stacked_single_bar(
        age,
        "年代",
        "構成比_pct",
        AGE_COLORS,
        "日本人の配偶者等の人口年齢構成比（2024年）",
        VIS_DIR / "01_日本人の配偶者等_人口年齢構成比_2024.png",
        "年代",
    )

    nationality = load_nationality_composition()
    nationality.to_csv(
        OUTPUT_DIR / "02_日本人の配偶者等_国籍別人口構成比_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_stacked_single_bar(
        nationality,
        "国籍・地域",
        "構成比_pct",
        NATIONALITY_COLORS,
        f"日本人の配偶者等の国籍別人口構成比（上位{TOP_N_NATIONALITIES}か国＋その他、2024年）",
        VIS_DIR / "02_日本人の配偶者等_国籍別人口構成比_2024.png",
        "国籍・地域",
        min_label_pct=3.0,
        xlabel="",
    )

    gender = load_gender_composition()
    gender.to_csv(OUTPUT_DIR / "03_日本人の配偶者等_男女別人口構成比_2024.csv", index=False, encoding="utf-8-sig")
    plot_stacked_single_bar(
        gender,
        "性別",
        "構成比_pct",
        GENDER_COLORS,
        "日本人の配偶者等の男女別人口構成比（2024年）",
        VIS_DIR / "03_日本人の配偶者等_男女別人口構成比_2024.png",
        "性別",
        min_label_pct=1.0,
    )

    gender_age = load_gender_age_composition()
    gender_age.to_csv(
        OUTPUT_DIR / "04_日本人の配偶者等_男女別年代構成比_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_gender_age_composition(
        gender_age,
        VIS_DIR / "04_日本人の配偶者等_男女別年代構成比_2024.png",
    )

    arrest_rate = load_arrest_rate_by_nationality()
    arrest_rate.to_csv(
        OUTPUT_DIR / "05_日本人の配偶者等_国籍別_1万人あたり検挙人員数_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_arrest_rate_by_nationality(
        arrest_rate,
        VIS_DIR / "05_日本人の配偶者等_国籍別_1万人あたり検挙人員数_2024.png",
    )

    print("出力完了:")
    print(OUTPUT_DIR / "01_日本人の配偶者等_人口年齢構成比_2024.csv")
    print(VIS_DIR / "01_日本人の配偶者等_人口年齢構成比_2024.png")
    print(OUTPUT_DIR / "02_日本人の配偶者等_国籍別人口構成比_2024.csv")
    print(VIS_DIR / "02_日本人の配偶者等_国籍別人口構成比_2024.png")
    print(OUTPUT_DIR / "03_日本人の配偶者等_男女別人口構成比_2024.csv")
    print(VIS_DIR / "03_日本人の配偶者等_男女別人口構成比_2024.png")
    print(OUTPUT_DIR / "04_日本人の配偶者等_男女別年代構成比_2024.csv")
    print(VIS_DIR / "04_日本人の配偶者等_男女別年代構成比_2024.png")
    print(OUTPUT_DIR / "05_日本人の配偶者等_国籍別_1万人あたり検挙人員数_2024.csv")
    print(VIS_DIR / "05_日本人の配偶者等_国籍別_1万人あたり検挙人員数_2024.png")


if __name__ == "__main__":
    main()
