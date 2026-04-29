# 定住者・フィリピン国籍の男女別年代構成を可視化するコード

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


# ======================== パス設定 ========================
BASE_PATH = Path(__file__).resolve().parents[3] / "data"
INPUT_FILE = BASE_PATH / "01_tidy" / "10_人口_在留資格別" / "10_2024_tidy.csv"
AGE_MAP_FILE = (
    BASE_PATH
    / "99_work"
    / "10_人口_在留資格別"
    / "02_map"
    / "10_人口_在留資格別_マップ_年齢.csv"
)
OUTPUT_DIR = BASE_PATH / "06_research" / "resident_philippines_gender_age" / "01_tidy"
VIS_DIR = (
    BASE_PATH / "06_research" / "resident_philippines_gender_age" / "03_output" / "png"
)

OUTPUT_DATA = OUTPUT_DIR / "01_定住者_フィリピン_男女別年代構成_2024.csv"
OUTPUT_CHART = VIS_DIR / "01_定住者_フィリピン_男女別年代構成_積み上げ割合_2024.png"
OUTPUT_GENDER_CHART = VIS_DIR / "02_定住者_フィリピン_男女構成比_2024.png"


TARGET_YEAR = 2024
TARGET_STATUS = "定住者"
TARGET_COUNTRY = "フィリピン"
GENDER_ORDER = ["男", "女"]
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
GENDER_COLORS = {
    "男": "#4C78A8",
    "女": "#E45756",
}


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
def make_gender_age_composition(input_file: Path, age_map_file: Path) -> pd.DataFrame:
    """2024年の定住者・フィリピン国籍について、男女別の年代構成比を作成する。"""
    df = pd.read_csv(input_file, encoding="utf-8-sig")
    df = df[
        (df["年"] == TARGET_YEAR)
        & (df["在留資格"] == TARGET_STATUS)
        & (df["国籍・地域"] == TARGET_COUNTRY)
        & (df["性別"].isin(GENDER_ORDER))
    ].copy()

    age_map = pd.read_csv(age_map_file, encoding="utf-8-sig")
    df = pd.merge(df, age_map, on="年齢", how="left", validate="m:1")
    missing_age = df[df["年代"].isna()]["年齢"].drop_duplicates().tolist()
    if missing_age:
        raise ValueError("年代に変換できない年齢があります: " + ", ".join(map(str, missing_age)))

    df["年代"] = df["年代"].replace({"不詳": "70代以上"})

    df = (
        df.groupby(["年", "国籍・地域", "在留資格", "性別", "年代"], as_index=False)["人口"]
        .sum()
    )
    df["性別総人口"] = df.groupby(["年", "国籍・地域", "在留資格", "性別"])["人口"].transform("sum")
    df["構成比"] = df["人口"] / df["性別総人口"]
    df["構成比_pct"] = df["構成比"] * 100

    all_rows = pd.MultiIndex.from_product(
        [[TARGET_YEAR], [TARGET_COUNTRY], [TARGET_STATUS], GENDER_ORDER, AGE_ORDER],
        names=["年", "国籍・地域", "在留資格", "性別", "年代"],
    ).to_frame(index=False)
    df = pd.merge(
        all_rows,
        df,
        on=["年", "国籍・地域", "在留資格", "性別", "年代"],
        how="left",
    )
    df["人口"] = df["人口"].fillna(0)
    df["性別総人口"] = df.groupby(["年", "国籍・地域", "在留資格", "性別"])["人口"].transform("sum")
    df["構成比"] = df["人口"] / df["性別総人口"]
    df["構成比_pct"] = df["構成比"] * 100
    df["性別"] = pd.Categorical(df["性別"], categories=GENDER_ORDER, ordered=True)
    df["年代"] = pd.Categorical(df["年代"], categories=AGE_ORDER, ordered=True)
    return df.sort_values(["性別", "年代"]).reset_index(drop=True)


# ======================== 可視化 ========================
def plot_gender_age_composition(df: pd.DataFrame, output_file: Path) -> None:
    """男女別の年代構成を100%積み上げ横棒グラフで出力する。"""
    pivot = (
        df.pivot(index="性別", columns="年代", values="構成比_pct")
        .reindex(GENDER_ORDER)
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

    ax.set_title("定住者・フィリピン国籍の男女別年代構成（2024年）", pad=14)
    ax.set_xlabel("各性別内の構成比（%）")
    ax.set_ylabel("性別")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.invert_yaxis()
    ax.legend(
        title="年代",
        bbox_to_anchor=(0.5, -0.22),
        loc="upper center",
        ncol=4,
        frameon=False,
    )
    save_figure(
        fig,
        output_file,
        note="注：出入国在留管理庁「在留外国人統計」をもとに作成。",
    )


def make_gender_summary(df: pd.DataFrame) -> pd.DataFrame:
    """男女別人口と全体に占める構成比を作成する。"""
    summary = df[["性別", "性別総人口"]].drop_duplicates().copy()
    summary["構成比"] = summary["性別総人口"] / summary["性別総人口"].sum()
    summary["構成比_pct"] = summary["構成比"] * 100
    summary["性別"] = pd.Categorical(summary["性別"], categories=GENDER_ORDER, ordered=True)
    return summary.sort_values("性別").reset_index(drop=True)


def plot_gender_summary(summary: pd.DataFrame, output_file: Path) -> None:
    """男女別構成比を100%積み上げ横棒グラフで出力する。"""
    fig, ax = plt.subplots(figsize=(8.8, 2.8))
    left = 0.0

    for _, row in summary.iterrows():
        gender = str(row["性別"])
        value = float(row["構成比_pct"])
        ax.barh(
            ["男女計"],
            [value],
            left=left,
            color=GENDER_COLORS[gender],
            edgecolor="white",
            linewidth=1.0,
            label=gender,
        )
        ax.text(
            left + value / 2,
            0,
            f"{gender}\n{int(row['性別総人口']):,}人\n{value:.1f}%",
            ha="center",
            va="center",
            fontsize=10,
            color="white",
        )
        left += value

    ax.set_title("定住者・フィリピン国籍の男女別構成比（2024年）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    save_figure(
        fig,
        output_file,
        note="注：出入国在留管理庁「在留外国人統計」をもとに作成。",
    )


# ======================== 実行 ========================
if __name__ == "__main__":
    setup_plot_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    composition = make_gender_age_composition(INPUT_FILE, AGE_MAP_FILE)
    composition.to_csv(OUTPUT_DATA, index=False, encoding="utf-8-sig")
    plot_gender_age_composition(composition, OUTPUT_CHART)

    gender_summary = make_gender_summary(composition)
    plot_gender_summary(gender_summary, OUTPUT_GENDER_CHART)
    print(gender_summary.to_string(index=False))
    print(f"可視化用データ: {OUTPUT_DATA}")
    print(f"男女別年代構成グラフ: {OUTPUT_CHART}")
    print(f"男女構成比グラフ: {OUTPUT_GENDER_CHART}")
    print("処理完了")
