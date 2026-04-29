# 2024年の定住者人口の国籍構成比を可視化するコード

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


# ======================== パス設定 ========================
BASE_PATH = Path(__file__).resolve().parents[3] / "data"
INPUT_FILE = BASE_PATH / "01_tidy" / "10_人口_在留資格別" / "10_2024_tidy.csv"
INPUT_ARRESTS_FILE = (
    BASE_PATH
    / "06_research"
    / "resident_nationality"
    / "01_tidy"
    / "01_定住者_国籍別検挙人員数_tidy.csv"
)
OUTPUT_DIR = BASE_PATH / "06_research" / "resident_nationality" / "01_tidy"
VIS_DIR = BASE_PATH / "06_research" / "resident_nationality" / "03_output" / "png"

OUTPUT_DATA = OUTPUT_DIR / "02_定住者人口_国籍構成比_2024.csv"
OUTPUT_BAR = VIS_DIR / "01_定住者人口_国籍構成比_2024_上位10.png"
OUTPUT_RATE_DATA = OUTPUT_DIR / "03_定住者_主要国籍別_1万人あたり検挙人員数_2024.csv"
OUTPUT_RATE_BAR = VIS_DIR / "02_定住者_主要国籍別_1万人あたり検挙人員数_2024.png"


# ======================== 描画設定 ========================
def setup_plot_style() -> None:
    """日本語表示を含む描画設定を行う。"""
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
        rc={
            "font.family": selected_font,
            "axes.unicode_minus": False,
        },
    )
    plt.rcParams["font.family"] = selected_font
    plt.rcParams["axes.unicode_minus"] = False


def save_figure(fig: plt.Figure, output_file: Path, note: str | None = None) -> None:
    """余白を調整して画像を保存する。"""
    if note:
        fig.text(
            0.01,
            0.015,
            note,
            ha="left",
            va="bottom",
            fontsize=8,
            color="#4D4D4D",
        )
        fig.tight_layout(rect=[0, 0.06, 1, 1])
    else:
        fig.tight_layout()
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


# ======================== データ作成 ========================
def make_resident_population_by_nationality(input_file: Path) -> pd.DataFrame:
    """2024年の定住者人口を国籍・地域別に集計し、構成比を付与する。"""
    df = pd.read_csv(input_file, encoding="utf-8-sig")
    df = df[(df["年"] == 2024) & (df["在留資格"] == "定住者")].copy()

    df = (
        df.groupby(["年", "国籍・地域"], as_index=False, dropna=False)["人口"]
        .sum()
    )
    total_population = df["人口"].sum()
    df["総人口"] = total_population
    df["構成比"] = df["人口"] / total_population
    df["構成比_pct"] = df["構成比"] * 100

    return df.sort_values("人口", ascending=False).reset_index(drop=True)


def make_top10_with_other(df: pd.DataFrame) -> pd.DataFrame:
    """上位10国籍とその他にまとめた可視化用データを作成する。"""
    top10 = df.head(10).copy()
    other = pd.DataFrame(
        [
            {
                "年": int(df["年"].iloc[0]),
                "国籍・地域": "その他",
                "人口": df.iloc[10:]["人口"].sum(),
                "総人口": df["総人口"].iloc[0],
            }
        ]
    )
    plot_df = pd.concat([top10, other], ignore_index=True)
    plot_df["構成比"] = plot_df["人口"] / plot_df["総人口"]
    plot_df["構成比_pct"] = plot_df["構成比"] * 100
    top = plot_df[plot_df["国籍・地域"] != "その他"].sort_values("人口", ascending=False)
    other = plot_df[plot_df["国籍・地域"] == "その他"]
    return pd.concat([top, other], ignore_index=True)


def make_resident_arrest_rate_by_nationality(
    df_population: pd.DataFrame,
    input_arrests_file: Path,
) -> pd.DataFrame:
    """主要国籍の2024年定住者1万人あたり検挙人員数を算出する。"""
    target_countries = ["ブラジル", "フィリピン", "中国"]

    df_population_target = df_population[df_population["国籍・地域"].isin(target_countries)][
        ["年", "国籍・地域", "人口"]
    ].copy()

    df_arrests = pd.read_csv(input_arrests_file, encoding="utf-8-sig")
    df_arrests = df_arrests[
        (df_arrests["年"] == 2024)
        & (df_arrests["在留資格"] == "定住者")
        & (df_arrests["国籍・地域"].isin(target_countries))
    ][["年", "国籍・地域", "検挙人員"]].copy()

    df = pd.merge(
        left=df_arrests,
        right=df_population_target,
        on=["年", "国籍・地域"],
        how="left",
        validate="1:1",
    )

    missing_population = df[df["人口"].isna()]
    if not missing_population.empty:
        raise ValueError(
            "人口データが存在しない国籍があります: "
            + ", ".join(missing_population["国籍・地域"].tolist())
        )

    df["検挙人員数_1万人あたり"] = df["検挙人員"] / df["人口"] * 10000
    return df.sort_values("検挙人員数_1万人あたり", ascending=False).reset_index(drop=True)


# ======================== 実行 ========================
if __name__ == "__main__":
    setup_plot_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    df_population = make_resident_population_by_nationality(INPUT_FILE)
    df_population.to_csv(OUTPUT_DATA, index=False, encoding="utf-8-sig")

    plot_df = make_top10_with_other(df_population)
    plot_df["国籍・地域"] = pd.Categorical(
        plot_df["国籍・地域"],
        categories=plot_df["国籍・地域"].tolist(),
        ordered=True,
    )
    highlight_countries = {"ブラジル", "フィリピン", "中国"}
    highlight_color = "#2F5597"
    muted_color = "#B7B7B7"
    palette = {
        country: highlight_color if country in highlight_countries else muted_color
        for country in plot_df["国籍・地域"].astype(str)
    }

    fig, ax = plt.subplots(figsize=(10, 6.5))
    sns.barplot(
        data=plot_df,
        x="構成比_pct",
        y="国籍・地域",
        hue="国籍・地域",
        order=plot_df["国籍・地域"].tolist(),
        palette=palette,
        dodge=False,
        legend=False,
        ax=ax,
    )
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=9)

    ax.set_title("定住者人口の国籍構成比（2024年）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("国籍・地域")
    ax.set_xlim(0, max(35, plot_df["構成比_pct"].max() * 1.2))
    save_figure(
        fig,
        OUTPUT_BAR,
        note="注：出入国在留管理庁「在留外国人統計」をもとに作成。",
    )

    df_rate = make_resident_arrest_rate_by_nationality(
        df_population=df_population,
        input_arrests_file=INPUT_ARRESTS_FILE,
    )
    df_rate.to_csv(OUTPUT_RATE_DATA, index=False, encoding="utf-8-sig")

    rate_palette = {
        "ブラジル": highlight_color,
        "フィリピン": highlight_color,
        "中国": highlight_color,
    }
    fig, ax = plt.subplots(figsize=(8, 5.5))
    sns.barplot(
        data=df_rate,
        x="検挙人員数_1万人あたり",
        y="国籍・地域",
        hue="国籍・地域",
        order=df_rate["国籍・地域"].tolist(),
        palette=rate_palette,
        dodge=False,
        legend=False,
        ax=ax,
    )
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", padding=3, fontsize=10)

    ax.set_title("定住者の国籍別1万人あたり検挙人員数（2024年）", pad=14)
    ax.set_xlabel("1万人あたり検挙人員数")
    ax.set_ylabel("国籍・地域")
    ax.set_xlim(0, max(60, df_rate["検挙人員数_1万人あたり"].max() * 1.2))
    save_figure(
        fig,
        OUTPUT_RATE_BAR,
        note="注：警察庁「犯罪統計」、出入国在留管理庁「在留外国人統計」をもとに作成。",
    )

    print(f"可視化用データ: {OUTPUT_DATA}")
    print(f"グラフ: {OUTPUT_BAR}")
    print(f"1万人あたり検挙人員数データ: {OUTPUT_RATE_DATA}")
    print(f"1万人あたり検挙人員数グラフ: {OUTPUT_RATE_BAR}")
    print("処理完了")
