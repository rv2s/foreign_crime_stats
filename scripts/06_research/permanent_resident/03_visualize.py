# 永住者等の人口構成と、韓国・朝鮮籍近似別の検挙率・倍率を作成するコード

from pathlib import Path
import re
import unicodedata

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
OUTPUT_DIR = BASE_PATH / "06_research" / "permanent_resident" / "01_tidy"
VIS_DIR = BASE_PATH / "06_research" / "permanent_resident" / "03_output" / "png"

INPUT_POPULATION_2024 = BASE_PATH / "01_tidy" / "10_人口_在留資格別" / "10_2024_tidy.csv"
INPUT_AGE_MAP = BASE_PATH / "99_work" / "10_人口_在留資格別" / "02_map" / "10_人口_在留資格別_マップ_年齢.csv"
INPUT_PROXY_RATE = (
    BASE_PATH
    / "06_research"
    / "permanent_resident"
    / "02_intermediate"
    / "04_来日外国人以外_特別永住者近似別_1万人あたり検挙人員数.csv"
)
INPUT_RAW_RATE = BASE_PATH / "05_analytics" / "20_1万人あたり検挙人員数及び対日本人倍率.csv"
INPUT_ADJUSTED_RATE = BASE_PATH / "05_analytics" / "33_対推定検挙人員及び年齢調整後対日本人倍率.csv"
INPUT_TOTAL_AGE_RATE = (
    BASE_PATH
    / "06_research"
    / "age_adjustment"
    / "07_日本全体_年代別検挙人員割合_可視化用データ.csv"
)
INPUT_INTEGRATED_ARRESTS = BASE_PATH / "04_integrated" / "09_検挙人員数_統合.csv"
INPUT_TOTAL_ARRESTS_BY_AGE = BASE_PATH / "02_standardized" / "01_検挙人員数_日本全体_名寄せ後.csv"

TARGET_YEAR = 2024
PERMANENT_RESIDENT_STATUSES = ["永住者", "永住者の配偶者等", "特別永住者"]
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
CRIME_ORDER = ["凶悪犯", "粗暴犯", "窃盗犯", "知能犯", "風俗犯", "その他の刑法犯"]
CRIME_COLORS = {
    "凶悪犯": "#7A1F1F",
    "粗暴犯": "#C44E52",
    "窃盗犯": "#4C78A8",
    "知能犯": "#72B7B2",
    "風俗犯": "#B279A2",
    "その他の刑法犯": "#9D755D",
}
CRIME_ORDER_COMBINED = ["窃盗犯", "凶悪犯", "粗暴犯", "知能犯", "風俗犯", "その他の刑法犯"]
COMBINED_GROUP_ORDER = [
    "日本全体",
    "日本人",
    "外国人",
    "永住者等",
    "永住者等のうち韓国・朝鮮籍",
    "永住者等のうち韓国・朝鮮籍以外",
]
THEFT_GROUP_ORDER = [
    "日本全体",
    "日本人",
    "外国人全体",
    "永住者等のうち韓国・朝鮮籍",
    "永住者等のうち韓国・朝鮮籍以外",
]
PROXY_LABEL_MAP = {
    "特別永住者近似": "韓国・朝鮮籍",
    "特別永住者近似以外": "それ以外",
}
GROUP_ORDER = ["韓国・朝鮮籍", "それ以外"]
PROXY_NOTE = "韓国・朝鮮籍は全体から来日外国人を引いて永住者等相当として推計。人数は永住者等の14歳以上人口。"


def normalize_text(value):
    if pd.isna(value):
        return pd.NA
    return unicodedata.normalize("NFKC", str(value)).strip()


def normalize_nationality(value):
    value = normalize_text(value)
    if pd.isna(value):
        return pd.NA
    if "韓国" in value:
        return "韓国"
    if "朝鮮" in value:
        return "朝鮮"
    value = re.sub(r"^\d{2}\D+\s+\d{3}", "", value).strip()
    value = re.sub(r"^\d+", "", value).strip()
    return value


def is_korea_or_chosen(series):
    return series.fillna("").astype(str).str.contains("韓国|朝鮮", regex=True)


def setup_plot_style():
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


def save_figure(fig, output_file):
    fig.tight_layout()
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def load_population():
    df = pd.read_csv(INPUT_POPULATION_2024, encoding="utf-8-sig")
    df = df[df["年"] == TARGET_YEAR].copy()
    df["国籍・地域_名寄せ後"] = df["国籍・地域"].map(normalize_nationality)
    df["韓国・朝鮮籍フラグ"] = is_korea_or_chosen(df["国籍・地域_名寄せ後"])
    return df


def create_status_composition(df_population):
    df = df_population[df_population["在留資格"].isin(PERMANENT_RESIDENT_STATUSES)].copy()
    df_composition = (
        df.groupby("在留資格", as_index=False)["人口"]
        .sum()
        .rename(columns={"人口": "人数"})
    )
    total = df_composition["人数"].sum()
    df_composition["総数"] = total
    df_composition["構成比"] = df_composition["人数"] / total
    df_composition["構成比_pct"] = df_composition["構成比"] * 100
    df_composition["表示順"] = df_composition["在留資格"].map(
        {status: i for i, status in enumerate(PERMANENT_RESIDENT_STATUSES)}
    )
    return df_composition.sort_values("表示順").drop(columns="表示順")


def plot_status_composition(df_composition):
    plot_df = df_composition.copy()
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    sns.barplot(
        data=plot_df,
        x="構成比_pct",
        y="在留資格",
        hue="在留資格",
        order=PERMANENT_RESIDENT_STATUSES,
        hue_order=PERMANENT_RESIDENT_STATUSES,
        palette={
            "永住者": "#2F5597",
            "永住者の配偶者等": "#A23E48",
            "特別永住者": "#7F7F7F",
        },
        dodge=False,
        legend=False,
        ax=ax,
    )
    ax.set_title("永住者等の人口構成比（2024年）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, max(100, plot_df["構成比_pct"].max() * 1.18))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    for index, value in enumerate(plot_df["構成比_pct"]):
        ax.text(value + 1.0, index, f"{value:.1f}%", va="center", fontsize=10)
    sns.despine(left=False, bottom=False)
    fig.text(
        0.01,
        0.01,
        "注: 出入国在留管理庁「在留外国人統計」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    save_figure(fig, VIS_DIR / "01_永住者等_3区分人口構成比_2024.png")


def create_korea_chosen_composition(df_population):
    df = df_population[df_population["在留資格"].isin(PERMANENT_RESIDENT_STATUSES)].copy()
    df["国籍区分"] = df["韓国・朝鮮籍フラグ"].map({True: "韓国・朝鮮籍", False: "それ以外"})
    df_status = (
        df.groupby(["在留資格", "国籍区分"], as_index=False)["人口"]
        .sum()
        .rename(columns={"人口": "人数"})
    )
    df_status["総数"] = df_status.groupby("在留資格")["人数"].transform("sum")
    df_status["構成比"] = df_status["人数"] / df_status["総数"]
    df_status["構成比_pct"] = df_status["構成比"] * 100

    df_total = (
        df.groupby("国籍区分", as_index=False)["人口"]
        .sum()
        .rename(columns={"人口": "人数"})
    )
    df_total["在留資格"] = "永住者等全体"
    total = df_total["人数"].sum()
    df_total["総数"] = total
    df_total["構成比"] = df_total["人数"] / total
    df_total["構成比_pct"] = df_total["構成比"] * 100
    df_total = df_total[["在留資格", "国籍区分", "人数", "総数", "構成比", "構成比_pct"]]

    df_status["在留資格"] = pd.Categorical(
        df_status["在留資格"],
        categories=PERMANENT_RESIDENT_STATUSES,
        ordered=True,
    )
    df_status["国籍区分"] = pd.Categorical(df_status["国籍区分"], categories=["韓国・朝鮮籍", "それ以外"], ordered=True)
    df_status = df_status.sort_values(["在留資格", "国籍区分"]).reset_index(drop=True)
    df_total["国籍区分"] = pd.Categorical(df_total["国籍区分"], categories=["韓国・朝鮮籍", "それ以外"], ordered=True)
    df_total = df_total.sort_values("国籍区分").reset_index(drop=True)

    return df_status, df_total


def plot_stacked_korea_chosen_composition(df_composition, output_file, title):
    plot_df = df_composition.copy()
    pivot = (
        plot_df.pivot(index="在留資格", columns="国籍区分", values="構成比_pct")
        .reindex(columns=["韓国・朝鮮籍", "それ以外"])
        .fillna(0)
    )
    if set(PERMANENT_RESIDENT_STATUSES).issubset(set(pivot.index.astype(str))):
        pivot = pivot.reindex(PERMANENT_RESIDENT_STATUSES)

    fig_height = 4.8 if len(pivot) == 1 else 5.6
    fig, ax = plt.subplots(figsize=(10.5, fig_height))
    colors = {"韓国・朝鮮籍": "#A23E48", "それ以外": "#BFBFBF"}
    left = pd.Series(0, index=pivot.index)
    for column in ["韓国・朝鮮籍", "それ以外"]:
        ax.barh(pivot.index.astype(str), pivot[column], left=left, color=colors[column], label=column)
        for y_index, (base, value) in enumerate(zip(left, pivot[column])):
            if value >= 4:
                ax.text(
                    base + value / 2,
                    y_index,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="#FFFFFF" if column == "韓国・朝鮮籍" else "#333333",
                )
        left = left + pivot[column]

    ax.set_title(title, pad=14)
    ax.set_xlabel("" if len(pivot) == 1 else "構成比（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    legend_y = -0.42 if len(pivot) == 1 else -0.32
    bottom_rect = 0.2 if len(pivot) == 1 else 0.12
    ax.legend(title="国籍区分", loc="lower center", bbox_to_anchor=(0.5, legend_y), ncol=2, frameon=False)
    ax.invert_yaxis()
    sns.despine(left=False, bottom=False)
    fig.tight_layout(rect=[0, bottom_rect, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_special_permanent_only_korea_chosen_composition(df_composition):
    special_df = df_composition[df_composition["在留資格"].astype(str) == "特別永住者"].copy()
    plot_df = special_df.copy()
    pivot = (
        plot_df.pivot(index="在留資格", columns="国籍区分", values="構成比_pct")
        .reindex(columns=["韓国・朝鮮籍", "それ以外"])
        .fillna(0)
        .reindex(["特別永住者"])
    )

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    colors = {"韓国・朝鮮籍": "#A23E48", "それ以外": "#BFBFBF"}
    left = pd.Series(0, index=pivot.index)
    for column in ["韓国・朝鮮籍", "それ以外"]:
        ax.barh(pivot.index.astype(str), pivot[column], left=left, color=colors[column], label=column)
        for y_index, (base, value) in enumerate(zip(left, pivot[column])):
            if value >= 4:
                ax.text(
                    base + value / 2,
                    y_index,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="#FFFFFF" if column == "韓国・朝鮮籍" else "#333333",
                )
        left = left + pivot[column]

    ax.set_title("特別永住者の韓国・朝鮮籍人口割合（2024年）", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.legend(title="国籍区分", loc="lower center", bbox_to_anchor=(0.5, -0.24), ncol=2, frameon=False)
    ax.invert_yaxis()
    sns.despine(left=False, bottom=False)
    fig.text(
        0.01,
        0.01,
        "注: 出入国在留管理庁「在留外国人統計」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.1, 1, 1])
    fig.savefig(VIS_DIR / "03b_特別永住者_韓国朝鮮籍人口割合_2024.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def create_status_nationality_composition(df_population):
    df = df_population[df_population["在留資格"].isin(PERMANENT_RESIDENT_STATUSES)].copy()
    df = (
        df.groupby(["在留資格", "国籍・地域_名寄せ後"], as_index=False)["人口"]
        .sum()
        .rename(columns={"国籍・地域_名寄せ後": "国籍・地域", "人口": "人数"})
    )
    frames = []
    for status in PERMANENT_RESIDENT_STATUSES:
        status_df = df[df["在留資格"] == status].sort_values("人数", ascending=False).reset_index(drop=True)
        total = status_df["人数"].sum()
        top = status_df.head(TOP_N_NATIONALITIES).copy()
        others = status_df.iloc[TOP_N_NATIONALITIES:].copy()
        if not others.empty:
            top = pd.concat(
                [
                    top,
                    pd.DataFrame(
                        [
                            {
                                "在留資格": status,
                                "国籍・地域": "その他",
                                "人数": others["人数"].sum(),
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
        top["総数"] = total
        top["構成比"] = top["人数"] / total
        top["構成比_pct"] = top["構成比"] * 100
        top["順位"] = range(1, len(top) + 1)
        frames.append(top)

    result = pd.concat(frames, ignore_index=True)
    result["在留資格"] = pd.Categorical(result["在留資格"], categories=PERMANENT_RESIDENT_STATUSES, ordered=True)
    return result.sort_values(["在留資格", "順位"]).reset_index(drop=True)


def plot_status_nationality_composition(df_composition):
    plot_df = df_composition.copy()
    fig, axes = plt.subplots(
        len(PERMANENT_RESIDENT_STATUSES),
        1,
        figsize=(11.5, 8.4),
        sharex=True,
    )
    colors = sns.color_palette("tab20", n_colors=TOP_N_NATIONALITIES + 1)

    for ax, status in zip(axes, PERMANENT_RESIDENT_STATUSES):
        status_df = plot_df[plot_df["在留資格"].astype(str) == status].copy()
        left = 0.0
        for index, row in status_df.iterrows():
            label = str(row["国籍・地域"])
            value = float(row["構成比_pct"])
            color = colors[int(row["順位"]) - 1]
            ax.barh([status], [value], left=left, color=color, edgecolor="white", linewidth=0.8, label=label)
            if value >= 4:
                ax.text(
                    left + value / 2,
                    0,
                    f"{label}\n{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="#222222" if value >= 12 else "#FFFFFF",
                )
            left += value
        ax.set_ylabel("")
        ax.set_xlim(0, 100)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
        ax.legend(
            title="国籍・地域",
            bbox_to_anchor=(1.02, 0.5),
            loc="center left",
            fontsize=7.5,
            frameon=False,
        )

    axes[-1].set_xlabel("構成比（%）")
    fig.suptitle(f"永住者等3区分別の国籍別人口構成比（上位{TOP_N_NATIONALITIES}か国＋その他、2024年）", y=1.01)
    fig.tight_layout()
    fig.savefig(
        VIS_DIR / "05_永住者等_3区分別_国籍別人口構成比_2024.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)


def create_status_age_composition(df_population):
    df = df_population[df_population["在留資格"].isin(PERMANENT_RESIDENT_STATUSES)].copy()
    age_map = pd.read_csv(INPUT_AGE_MAP, encoding="utf-8-sig")
    df = pd.merge(df, age_map, on="年齢", how="left", validate="m:1")
    missing_ages = df.loc[df["年代"].isna(), "年齢"].drop_duplicates()
    if not missing_ages.empty:
        raise ValueError("年齢マップに存在しない年齢があります: " + ", ".join(missing_ages.astype(str).tolist()))
    df["年代"] = df["年代"].replace({"不詳": "70代以上"})
    df = (
        df.groupby(["在留資格", "年代"], as_index=False)["人口"]
        .sum()
        .rename(columns={"人口": "人数"})
    )
    all_rows = pd.MultiIndex.from_product(
        [PERMANENT_RESIDENT_STATUSES, AGE_ORDER],
        names=["在留資格", "年代"],
    ).to_frame(index=False)
    df = pd.merge(all_rows, df, on=["在留資格", "年代"], how="left")
    df["人数"] = df["人数"].fillna(0)
    df["総数"] = df.groupby("在留資格")["人数"].transform("sum")
    df["構成比"] = df["人数"] / df["総数"]
    df["構成比_pct"] = df["構成比"] * 100
    df["在留資格"] = pd.Categorical(df["在留資格"], categories=PERMANENT_RESIDENT_STATUSES, ordered=True)
    df["年代"] = pd.Categorical(df["年代"], categories=AGE_ORDER, ordered=True)
    return df.sort_values(["在留資格", "年代"]).reset_index(drop=True)


def plot_status_age_composition(df_composition):
    pivot = (
        df_composition.pivot(index="在留資格", columns="年代", values="構成比_pct")
        .reindex(PERMANENT_RESIDENT_STATUSES)
        .reindex(columns=AGE_ORDER)
    )

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
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
                    fontsize=8.5,
                    color="white" if age_group in {"0~13歳", "40代", "50代", "70代以上"} else "#222222",
                )
        left += values

    ax.set_title("永住者等3区分別の年代別人口構成比（2024年）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.invert_yaxis()
    ax.legend(title="年代", bbox_to_anchor=(0.5, -0.18), loc="upper center", ncol=4, frameon=False)
    save_figure(fig, VIS_DIR / "06_永住者等_3区分別_年代別人口構成比_2024.png")


def plot_special_permanent_age_composition(df_composition):
    special_df = df_composition[df_composition["在留資格"].astype(str) == "特別永住者"].copy()
    pivot = (
        special_df.pivot(index="在留資格", columns="年代", values="構成比_pct")
        .reindex(["特別永住者"])
        .reindex(columns=AGE_ORDER)
    )

    fig, ax = plt.subplots(figsize=(10.8, 3.8))
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
                    fontsize=8.5,
                    color="white" if age_group in {"0~13歳", "40代", "50代", "70代以上"} else "#222222",
                )
        left += values

    ax.set_title("特別永住者の年代別人口構成比（2024年）", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.legend(title="年代", bbox_to_anchor=(0.5, -0.2), loc="upper center", ncol=4, frameon=False)
    fig.text(
        0.01,
        0.01,
        "注: 出入国在留管理庁「在留外国人統計」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.1, 1, 1])
    fig.savefig(
        VIS_DIR / "06b_特別永住者_年代別人口構成比_2024.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)


def create_korea_chosen_status_composition(df_population):
    df = df_population[
        df_population["在留資格"].isin(PERMANENT_RESIDENT_STATUSES)
        & df_population["韓国・朝鮮籍フラグ"]
    ].copy()
    df = (
        df.groupby("在留資格", as_index=False)["人口"]
        .sum()
        .rename(columns={"人口": "人数"})
    )
    total = df["人数"].sum()
    df["総数"] = total
    df["構成比"] = df["人数"] / total
    df["構成比_pct"] = df["構成比"] * 100
    df["在留資格"] = pd.Categorical(df["在留資格"], categories=PERMANENT_RESIDENT_STATUSES, ordered=True)
    return df.sort_values("在留資格").reset_index(drop=True)


def plot_korea_chosen_status_composition(df_composition):
    plot_df = df_composition.copy()
    colors = {
        "特別永住者": "#2F5597",
        "永住者": "#A23E48",
        "永住者の配偶者等": "#7F7F7F",
    }
    segment_order = ["特別永住者", "永住者", "永住者の配偶者等"]

    fig, ax = plt.subplots(figsize=(10.5, 3.2))
    left = 0.0
    plot_df["在留資格"] = pd.Categorical(plot_df["在留資格"], categories=segment_order, ordered=True)
    plot_df = plot_df.sort_values("在留資格").reset_index(drop=True)
    for _, row in plot_df.iterrows():
        status = str(row["在留資格"])
        value = float(row["構成比_pct"])
        ax.barh(
            ["韓国・朝鮮籍人口"],
            [value],
            left=left,
            color=colors[status],
            edgecolor="white",
            linewidth=0.9,
            label=status,
        )
        if value >= 4:
            ax.text(
                left + value / 2,
                0,
                f"{status}\n{value:.1f}%",
                ha="center",
                va="center",
                fontsize=9,
                color="white",
            )
        left += value

    ax.set_title("永住者等の韓国・朝鮮籍人口の3区分構成比（2024年）", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.legend(title="在留資格", bbox_to_anchor=(0.5, -0.28), loc="upper center", ncol=3, frameon=False)
    fig.text(
        0.01,
        0.01,
        "注: 出入国在留管理庁「在留外国人統計」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.savefig(VIS_DIR / "07_永住者等_韓国朝鮮籍人口_3区分構成比_2024.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def create_crime_composition(df_rate):
    df = df_rate.copy()
    source = pd.read_csv(INPUT_PROXY_RATE, encoding="utf-8-sig")
    source = source[
        (source["年"] == TARGET_YEAR)
        & (source["罪種00"].isin(CRIME_ORDER))
        & (source["罪種01"] == "計")
    ].copy()
    source["表示区分"] = source["特別永住者近似区分"].replace(PROXY_LABEL_MAP)
    source = source[source["表示区分"].isin(GROUP_ORDER)].copy()
    source = (
        source.groupby(["表示区分", "罪種00"], as_index=False)["検挙人員"]
        .sum()
        .rename(columns={"罪種00": "罪種"})
    )
    source["総検挙人員"] = source.groupby("表示区分")["検挙人員"].transform("sum")
    source["構成比"] = source["検挙人員"] / source["総検挙人員"]
    source["構成比_pct"] = source["構成比"] * 100
    source["表示区分"] = pd.Categorical(source["表示区分"], categories=GROUP_ORDER, ordered=True)
    source["罪種"] = pd.Categorical(source["罪種"], categories=CRIME_ORDER, ordered=True)
    return source.sort_values(["表示区分", "罪種"]).reset_index(drop=True)


def plot_crime_composition(df_composition):
    pivot = (
        df_composition.pivot(index="表示区分", columns="罪種", values="構成比_pct")
        .reindex(GROUP_ORDER)
        .reindex(columns=CRIME_ORDER)
    )
    fig, ax = plt.subplots(figsize=(11, 4.8))
    left = pd.Series(0.0, index=pivot.index)
    for crime in CRIME_ORDER:
        values = pivot[crime]
        bars = ax.barh(
            pivot.index.astype(str),
            values,
            left=left,
            color=CRIME_COLORS[crime],
            edgecolor="white",
            linewidth=0.8,
            label=crime,
        )
        for bar, value, start in zip(bars, values, left):
            if value >= 6:
                ax.text(
                    start + value / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=8.5,
                    color="white" if crime in {"凶悪犯", "粗暴犯", "窃盗犯", "その他の刑法犯"} else "#222222",
                )
        left += values

    ax.set_title("永住者等の韓国・朝鮮籍別 罪種別検挙人員構成比（2024年）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.invert_yaxis()
    ax.legend(title="罪種", bbox_to_anchor=(0.5, -0.2), loc="upper center", ncol=3, frameon=False)
    fig.text(
        0.01,
        0.015,
        f"注: {PROXY_NOTE}",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.savefig(
        VIS_DIR / "08_永住者等_韓国朝鮮籍別_罪種別検挙人員構成比_2024.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)


def create_overall_crime_composition():
    source = pd.read_csv(INPUT_INTEGRATED_ARRESTS, encoding="utf-8-sig")
    source = source[
        (source["年"] == TARGET_YEAR)
        & (source["罪種00"].isin(CRIME_ORDER))
    ].copy()

    japanese = source[source["区分00"] == "日本人"].copy()
    foreign = source[
        (source["区分00"] == "外国人")
        & (
            (source["区分01"] == "永住者等")
            | ((source["区分01"] == "来日外国人") & (source["在留資格"] != ""))
        )
    ].copy()

    japanese_grouped = (
        japanese.groupby("罪種00", as_index=False)["検挙人員"]
        .sum()
        .rename(columns={"罪種00": "罪種"})
    )
    japanese_grouped["表示区分"] = "日本人"

    foreign_grouped = (
        foreign.groupby("罪種00", as_index=False)["検挙人員"]
        .sum()
        .rename(columns={"罪種00": "罪種"})
    )
    foreign_grouped["表示区分"] = "外国人全体"

    total_grouped = pd.merge(
        japanese_grouped[["罪種", "検挙人員"]],
        foreign_grouped[["罪種", "検挙人員"]],
        on="罪種",
        how="outer",
        suffixes=("_日本人", "_外国人"),
    ).fillna(0)
    total_grouped["検挙人員"] = total_grouped["検挙人員_日本人"] + total_grouped["検挙人員_外国人"]
    total_grouped["表示区分"] = "日本全体"
    total_grouped = total_grouped[["罪種", "検挙人員", "表示区分"]]

    frames = [total_grouped, japanese_grouped, foreign_grouped]
    labels = ["日本全体", "日本人", "外国人全体"]

    result = pd.concat(frames, ignore_index=True)
    result["総検挙人員"] = result.groupby("表示区分")["検挙人員"].transform("sum")
    result["構成比"] = result["検挙人員"] / result["総検挙人員"]
    result["構成比_pct"] = result["構成比"] * 100
    result["表示区分"] = pd.Categorical(result["表示区分"], categories=labels, ordered=True)
    result["罪種"] = pd.Categorical(result["罪種"], categories=CRIME_ORDER, ordered=True)
    return result.sort_values(["表示区分", "罪種"]).reset_index(drop=True)


def plot_overall_crime_composition(df_composition):
    pivot = (
        df_composition.pivot(index="表示区分", columns="罪種", values="構成比_pct")
        .reindex(["日本全体", "日本人", "外国人全体"])
        .reindex(columns=CRIME_ORDER)
    )
    fig, ax = plt.subplots(figsize=(11, 5.2))
    left = pd.Series(0.0, index=pivot.index)
    for crime in CRIME_ORDER:
        values = pivot[crime]
        bars = ax.barh(
            pivot.index.astype(str),
            values,
            left=left,
            color=CRIME_COLORS[crime],
            edgecolor="white",
            linewidth=0.8,
            label=crime,
        )
        for bar, value, start in zip(bars, values, left):
            if value >= 6:
                ax.text(
                    start + value / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=8.5,
                    color="white" if crime in {"凶悪犯", "粗暴犯", "窃盗犯", "その他の刑法犯"} else "#222222",
                )
        left += values

    ax.set_title("日本全体・日本人・外国人全体の罪種別検挙人員構成比（2024年）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.invert_yaxis()
    ax.legend(title="罪種", bbox_to_anchor=(0.5, -0.18), loc="upper center", ncol=3, frameon=False)
    save_figure(fig, VIS_DIR / "09_日本全体_日本人_外国人全体_罪種別検挙人員構成比_2024.png")


def create_combined_crime_composition(df_overall_crime, df_crime):
    overall = df_overall_crime.copy()
    overall["表示区分"] = overall["表示区分"].astype(str)
    overall["罪種"] = overall["罪種"].astype(str)
    overall["表示区分"] = overall["表示区分"].replace({"外国人全体": "外国人"})

    permanent_total = (
        df_crime.groupby("罪種", as_index=False)["検挙人員"]
        .sum()
        .assign(表示区分="永住者等")
    )
    permanent_total["総検挙人員"] = permanent_total["検挙人員"].sum()
    permanent_total["構成比"] = permanent_total["検挙人員"] / permanent_total["総検挙人員"]
    permanent_total["構成比_pct"] = permanent_total["構成比"] * 100

    korea_split = df_crime.copy()
    korea_split["表示区分"] = korea_split["表示区分"].astype(str)
    korea_split["罪種"] = korea_split["罪種"].astype(str)
    korea_split["表示区分"] = korea_split["表示区分"].replace(
        {
            "韓国・朝鮮籍": "永住者等のうち韓国・朝鮮籍",
            "それ以外": "永住者等のうち韓国・朝鮮籍以外",
        }
    )

    result = pd.concat(
        [
            overall[["表示区分", "罪種", "検挙人員", "総検挙人員", "構成比", "構成比_pct"]],
            permanent_total[["表示区分", "罪種", "検挙人員", "総検挙人員", "構成比", "構成比_pct"]],
            korea_split[["表示区分", "罪種", "検挙人員", "総検挙人員", "構成比", "構成比_pct"]],
        ],
        ignore_index=True,
    )
    result["表示区分"] = pd.Categorical(result["表示区分"], categories=COMBINED_GROUP_ORDER, ordered=True)
    result["罪種"] = pd.Categorical(result["罪種"], categories=CRIME_ORDER_COMBINED, ordered=True)
    return result.sort_values(["表示区分", "罪種"]).reset_index(drop=True)


def plot_combined_crime_composition(df_composition):
    pivot = (
        df_composition.pivot(index="表示区分", columns="罪種", values="構成比_pct")
        .reindex(COMBINED_GROUP_ORDER)
        .reindex(columns=CRIME_ORDER_COMBINED)
    )
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    left = pd.Series(0.0, index=pivot.index)
    dark_crimes = {"窃盗犯", "凶悪犯", "粗暴犯", "その他の刑法犯"}

    for crime in CRIME_ORDER_COMBINED:
        values = pivot[crime]
        bars = ax.barh(
            pivot.index.astype(str),
            values,
            left=left,
            color=CRIME_COLORS[crime],
            edgecolor="white",
            linewidth=0.8,
            label=crime,
        )
        for bar, value, start in zip(bars, values, left):
            if value >= 6:
                ax.text(
                    start + value / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=8.5,
                    color="white" if crime in dark_crimes else "#222222",
                )
        left += values

    ax.set_title("罪種別検挙人員構成比（2024年）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.invert_yaxis()
    ax.legend(title="罪種", bbox_to_anchor=(0.5, -0.16), loc="upper center", ncol=3, frameon=False)
    fig.text(
        0.01,
        0.015,
        f"注: 日本全体・日本人・外国人は統合検挙人員データ、永住者等の韓国・朝鮮籍別は {PROXY_NOTE}",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.savefig(
        VIS_DIR / "10_罪種別検挙人員構成比_2024_日本全体_日本人_外国人_永住者等_韓国朝鮮籍別.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)


def create_theft_comparison(df_combined_crime):
    df = df_combined_crime.copy()
    df["表示区分"] = df["表示区分"].astype(str)
    df["表示区分"] = df["表示区分"].replace({"外国人": "外国人全体"})
    df = df[df["罪種"].astype(str) == "窃盗犯"].copy()
    df = df[df["表示区分"].isin(THEFT_GROUP_ORDER)].copy()
    df["表示区分"] = pd.Categorical(df["表示区分"], categories=THEFT_GROUP_ORDER, ordered=True)
    return df.sort_values("表示区分").reset_index(drop=True)


def plot_theft_comparison(df_theft):
    plot_df = df_theft.copy()
    colors = {
        "日本全体": "#BFBFBF",
        "日本人": "#BFBFBF",
        "外国人全体": "#BFBFBF",
        "永住者等のうち韓国・朝鮮籍": "#4C78A8",
        "永住者等のうち韓国・朝鮮籍以外": "#BFBFBF",
    }

    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    bars = ax.barh(
        plot_df["表示区分"].astype(str),
        plot_df["構成比_pct"],
        color=[colors[label] for label in plot_df["表示区分"].astype(str)],
        edgecolor="white",
        linewidth=0.9,
        height=0.68,
    )
    for bar, value in zip(bars, plot_df["構成比_pct"]):
        ax.text(
            value + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}%",
            ha="left",
            va="center",
            fontsize=9,
            color="#222222",
        )

    ax.set_title("窃盗犯の構成比比較（2024年）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, max(55, plot_df["構成比_pct"].max() * 1.15))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.invert_yaxis()
    fig.text(
        0.01,
        0.015,
        f"注: 日本全体・日本人・外国人全体は統合検挙人員データ、永住者等の韓国・朝鮮籍別は {PROXY_NOTE}",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    fig.savefig(
        VIS_DIR / "11_窃盗犯構成比_2024_日本全体_日本人_外国人全体_韓国朝鮮籍別.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)


def create_theft_age_composition():
    df = pd.read_csv(INPUT_TOTAL_ARRESTS_BY_AGE, encoding="utf-8-sig")
    df = df[(df["年"] == TARGET_YEAR) & (df["年代"].notna())].copy()
    df = df[df["年代"] != "0~13歳"].copy()

    total = (
        df.groupby("年代", as_index=False)["検挙人員"]
        .sum()
        .rename(columns={"検挙人員": "総検挙人員"})
    )
    theft = (
        df[df["罪種00"] == "窃盗犯"]
        .groupby("年代", as_index=False)["検挙人員"]
        .sum()
        .rename(columns={"検挙人員": "窃盗犯検挙人員"})
    )
    result = pd.merge(total, theft, on="年代", how="left", validate="1:1").fillna({"窃盗犯検挙人員": 0})
    result["構成比"] = result["窃盗犯検挙人員"] / result["総検挙人員"]
    result["構成比_pct"] = result["構成比"] * 100
    result["年代"] = pd.Categorical(result["年代"], categories=AGE_ORDER[1:], ordered=True)
    return result.sort_values("年代").reset_index(drop=True)


def plot_theft_age_composition(df_theft_age):
    plot_df = df_theft_age.copy()
    fig, ax = plt.subplots(figsize=(11, 5.4))
    bars = ax.bar(
        plot_df["年代"].astype(str),
        plot_df["構成比_pct"],
        color="#4C78A8",
        edgecolor="white",
        linewidth=0.9,
        width=0.68,
    )
    for bar, value in zip(bars, plot_df["構成比_pct"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + plot_df["構成比_pct"].max() * 0.02,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#222222",
        )

    ax.set_title("日本全体の年代別 窃盗犯構成比（2024年）", pad=14)
    ax.set_xlabel("年代")
    ax.set_ylabel("構成比（%）")
    ax.set_ylim(0, plot_df["構成比_pct"].max() * 1.18)
    ax.tick_params(axis="x", labelrotation=25)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    fig.text(
        0.01,
        0.015,
        "注: 警察庁「犯罪統計」をもとに作成。2024年の各年代の全罪種合計に占める窃盗犯の割合。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    fig.savefig(
        VIS_DIR / "12_日本全体_年代別_窃盗犯構成比_2024.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)


def create_group_age_population(df_population):
    df = df_population[df_population["在留資格"].isin(PERMANENT_RESIDENT_STATUSES)].copy()
    age_map = pd.read_csv(INPUT_AGE_MAP, encoding="utf-8-sig")
    df = pd.merge(df, age_map, on="年齢", how="left", validate="m:1")
    missing_ages = df.loc[df["年代"].isna(), "年齢"].drop_duplicates()
    if not missing_ages.empty:
        raise ValueError("年齢マップに存在しない年齢があります: " + ", ".join(missing_ages.astype(str).tolist()))

    df = df[df["年代"] != "0~13歳"].copy()
    df["表示区分"] = df["韓国・朝鮮籍フラグ"].map({True: GROUP_ORDER[0], False: GROUP_ORDER[1]})
    return (
        df.groupby(["表示区分", "年代"], as_index=False)["人口"]
        .sum()
        .rename(columns={"人口": "人数"})
    )


def create_rate_table(df_population):
    df_proxy = pd.read_csv(INPUT_PROXY_RATE, encoding="utf-8-sig")
    df_proxy = df_proxy[
        (df_proxy["年"] == TARGET_YEAR)
        & (df_proxy["罪種00"] == "計")
        & (df_proxy["罪種01"] == "計")
    ].copy()
    df_proxy["表示区分"] = df_proxy["特別永住者近似区分"].replace(PROXY_LABEL_MAP)

    df_raw = pd.read_csv(INPUT_RAW_RATE, encoding="utf-8-sig")
    japanese_rate = float(
        df_raw.loc[
            (df_raw["年"] == TARGET_YEAR)
            & (df_raw["区分00"] == "日本人")
            & (df_raw["罪種00"] == "計")
            & (df_raw["罪種01"] == "計"),
            "検挙人員数_1万人あたり",
        ].iloc[0]
    )

    df_age_rate = pd.read_csv(INPUT_TOTAL_AGE_RATE, encoding="utf-8-sig")
    df_age_rate = df_age_rate[df_age_rate["年"] == TARGET_YEAR][["年代", "検挙人員数_1万人あたり"]].copy()
    df_group_age = create_group_age_population(df_population)
    df_expected = pd.merge(df_group_age, df_age_rate, on="年代", how="left", validate="m:1")
    missing_rates = df_expected.loc[df_expected["検挙人員数_1万人あたり"].isna(), "年代"].drop_duplicates()
    if not missing_rates.empty:
        raise ValueError("日本全体の年代別検挙率がない年代があります: " + ", ".join(missing_rates.astype(str).tolist()))
    df_expected["期待検挙人員"] = df_expected["人数"] * df_expected["検挙人員数_1万人あたり"] / 10000
    df_expected = df_expected.groupby("表示区分", as_index=False)["期待検挙人員"].sum()

    df_adjusted = pd.read_csv(INPUT_ADJUSTED_RATE, encoding="utf-8-sig")
    japanese_expected_ratio = float(
        df_adjusted.loc[
            (df_adjusted["年"] == TARGET_YEAR)
            & (df_adjusted["区分00"] == "日本人")
            & (df_adjusted["罪種00"] == "計")
            & (df_adjusted["罪種01"] == "計"),
            "日本人_対推定値倍率",
        ].iloc[0]
    )

    df_result = pd.merge(
        df_proxy[
            [
                "年",
                "表示区分",
                "特別永住者近似区分",
                "検挙人員",
                "人数",
                "検挙人員数_1万人あたり",
            ]
        ],
        df_expected,
        on="表示区分",
        how="left",
        validate="1:1",
    )
    df_result["日本人_検挙人員数_1万人あたり"] = japanese_rate
    df_result["対日本人倍率"] = df_result["検挙人員数_1万人あたり"] / japanese_rate
    df_result["対推定値倍率"] = df_result["検挙人員"] / df_result["期待検挙人員"]
    df_result["日本人_対推定値倍率"] = japanese_expected_ratio
    df_result["対日本人倍率_年齢調整後"] = df_result["対推定値倍率"] / japanese_expected_ratio
    df_result["注記"] = PROXY_NOTE
    df_result["表示順"] = df_result["表示区分"].map({label: i for i, label in enumerate(GROUP_ORDER)})
    return df_result.sort_values("表示順").drop(columns="表示順")


def plot_rate_table(df_rate):
    plot_df = df_rate.copy()
    plot_df["表示区分"] = pd.Categorical(plot_df["表示区分"], categories=GROUP_ORDER, ordered=True)
    plot_df = plot_df.sort_values("表示区分")

    metrics = [
        ("検挙人員数_1万人あたり", "1万人あたり検挙人員数", "人"),
        ("対日本人倍率", "対日本人倍率", "倍"),
        ("対日本人倍率_年齢調整後", "年齢調整後対日本人倍率", "倍"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    palette = [("#A23E48" if label == GROUP_ORDER[0] else "#7F7F7F") for label in GROUP_ORDER]
    for ax, (column, title, unit) in zip(axes, metrics):
        sns.barplot(
            data=plot_df,
            x="表示区分",
            y=column,
            hue="表示区分",
            order=GROUP_ORDER,
            hue_order=GROUP_ORDER,
            palette=dict(zip(GROUP_ORDER, palette)),
            dodge=False,
            legend=False,
            ax=ax,
        )
        ax.set_title(title, pad=10)
        ax.set_xlabel("")
        ax.set_ylabel(unit)
        ax.tick_params(axis="x", labelrotation=0)
        ax.grid(axis="x", visible=False)
        if "倍率" in column:
            ax.axhline(1, color="#333333", linewidth=1.1, linestyle="--", alpha=0.7)
        labels = [f"{value:.2f}" if "倍率" in column else f"{value:.1f}" for value in plot_df[column]]
        for index, (value, label) in enumerate(zip(plot_df[column], labels)):
            ax.text(index, value + plot_df[column].max() * 0.03, label, ha="center", va="bottom", fontsize=9)
    fig.suptitle("永住者等の韓国・朝鮮籍別 検挙率・倍率（2024年）", y=1.03)
    fig.text(
        0.01,
        0.01,
        "注: 警察庁「犯罪統計」、総務省統計局「人口推計」、出入国在留管理庁「在留外国人統計」等をもとに作成。"
        f"{PROXY_NOTE}",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(VIS_DIR / "02_永住者等_韓国朝鮮籍別_検挙率倍率_2024.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_rate_table_two_metrics(df_rate):
    plot_df = df_rate.copy()
    plot_df["表示区分"] = pd.Categorical(plot_df["表示区分"], categories=GROUP_ORDER, ordered=True)
    plot_df = plot_df.sort_values("表示区分")

    metrics = [
        ("検挙人員数_1万人あたり", "1万人あたり検挙人員数", "人"),
        ("対日本人倍率_年齢調整後", "年齢調整後対日本人倍率", "倍"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2))
    palette = [("#A23E48" if label == GROUP_ORDER[0] else "#7F7F7F") for label in GROUP_ORDER]
    for ax, (column, title, unit) in zip(axes, metrics):
        sns.barplot(
            data=plot_df,
            x="表示区分",
            y=column,
            hue="表示区分",
            order=GROUP_ORDER,
            hue_order=GROUP_ORDER,
            palette=dict(zip(GROUP_ORDER, palette)),
            dodge=False,
            legend=False,
            ax=ax,
        )
        ax.set_title(title, pad=10)
        ax.set_xlabel("")
        ax.set_ylabel(unit)
        ax.tick_params(axis="x", labelrotation=0)
        ax.grid(axis="x", visible=False)
        if "倍率" in column:
            ax.axhline(1, color="#333333", linewidth=1.1, linestyle="--", alpha=0.7)
        labels = [f"{value:.2f}" if "倍率" in column else f"{value:.1f}" for value in plot_df[column]]
        for index, (value, label) in enumerate(zip(plot_df[column], labels)):
            ax.text(index, value + plot_df[column].max() * 0.03, label, ha="center", va="bottom", fontsize=9)
    fig.suptitle("永住者等の韓国・朝鮮籍別 検挙率・倍率（2024年）", y=1.03)
    fig.text(
        0.01,
        0.01,
        "注: 警察庁「犯罪統計」、総務省統計局「人口推計」、出入国在留管理庁「在留外国人統計」等をもとに作成。"
        "韓国・朝鮮籍は全体から来日外国人を引いて永住者等相当として推計。人数は永住者等の14歳以上人口。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(
        VIS_DIR / "02b_永住者等_韓国朝鮮籍別_検挙率倍率_2024_2項目.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VIS_DIR.mkdir(parents=True, exist_ok=True)
    setup_plot_style()

    df_population = load_population()

    df_composition = create_status_composition(df_population)
    df_composition.to_csv(OUTPUT_DIR / "01_永住者等_3区分人口構成比_2024.csv", index=False, encoding="utf-8-sig")
    plot_status_composition(df_composition)

    df_status_korea, df_total_korea = create_korea_chosen_composition(df_population)
    df_status_korea.to_csv(
        OUTPUT_DIR / "03_永住者等_3区分別_韓国朝鮮籍人口割合_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_stacked_korea_chosen_composition(
        df_status_korea,
        VIS_DIR / "03_永住者等_3区分別_韓国朝鮮籍人口割合_2024.png",
        "永住者等3区分別 韓国・朝鮮籍人口割合（2024年）",
    )
    plot_special_permanent_only_korea_chosen_composition(df_status_korea)
    df_total_korea.to_csv(
        OUTPUT_DIR / "04_永住者等全体_韓国朝鮮籍人口割合_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_stacked_korea_chosen_composition(
        df_total_korea,
        VIS_DIR / "04_永住者等全体_韓国朝鮮籍人口割合_2024.png",
        "永住者等全体 韓国・朝鮮籍人口割合（2024年）",
    )

    df_status_nationality = create_status_nationality_composition(df_population)
    df_status_nationality.to_csv(
        OUTPUT_DIR / "05_永住者等_3区分別_国籍別人口構成比_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_status_nationality_composition(df_status_nationality)

    df_status_age = create_status_age_composition(df_population)
    df_status_age.to_csv(
        OUTPUT_DIR / "06_永住者等_3区分別_年代別人口構成比_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_status_age_composition(df_status_age)
    plot_special_permanent_age_composition(df_status_age)

    df_korea_status = create_korea_chosen_status_composition(df_population)
    df_korea_status.to_csv(
        OUTPUT_DIR / "07_永住者等_韓国朝鮮籍人口_3区分構成比_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_korea_chosen_status_composition(df_korea_status)

    df_rate = create_rate_table(df_population)
    df_rate.to_csv(OUTPUT_DIR / "02_永住者等_韓国朝鮮籍別_検挙率倍率_2024.csv", index=False, encoding="utf-8-sig")
    plot_rate_table(df_rate)
    plot_rate_table_two_metrics(df_rate)

    df_crime = create_crime_composition(df_rate)
    df_crime.to_csv(
        OUTPUT_DIR / "08_永住者等_韓国朝鮮籍別_罪種別検挙人員構成比_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_crime_composition(df_crime)

    df_overall_crime = create_overall_crime_composition()
    df_overall_crime.to_csv(
        OUTPUT_DIR / "09_日本全体_日本人_外国人全体_罪種別検挙人員構成比_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_overall_crime_composition(df_overall_crime)

    df_combined_crime = create_combined_crime_composition(df_overall_crime, df_crime)
    df_combined_crime.to_csv(
        OUTPUT_DIR / "10_罪種別検挙人員構成比_2024_日本全体_日本人_外国人_永住者等_韓国朝鮮籍別.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_combined_crime_composition(df_combined_crime)

    df_theft = create_theft_comparison(df_combined_crime)
    df_theft.to_csv(
        OUTPUT_DIR / "11_窃盗犯構成比_2024_日本全体_日本人_外国人全体_韓国朝鮮籍別.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_theft_comparison(df_theft)

    df_theft_age = create_theft_age_composition()
    df_theft_age.to_csv(
        OUTPUT_DIR / "12_日本全体_年代別_窃盗犯構成比_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    plot_theft_age_composition(df_theft_age)

    print("出力完了:")
    print(OUTPUT_DIR / "01_永住者等_3区分人口構成比_2024.csv")
    print(VIS_DIR / "01_永住者等_3区分人口構成比_2024.png")
    print(OUTPUT_DIR / "02_永住者等_韓国朝鮮籍別_検挙率倍率_2024.csv")
    print(VIS_DIR / "02_永住者等_韓国朝鮮籍別_検挙率倍率_2024.png")
    print(VIS_DIR / "02b_永住者等_韓国朝鮮籍別_検挙率倍率_2024_2項目.png")
    print(OUTPUT_DIR / "03_永住者等_3区分別_韓国朝鮮籍人口割合_2024.csv")
    print(VIS_DIR / "03_永住者等_3区分別_韓国朝鮮籍人口割合_2024.png")
    print(OUTPUT_DIR / "04_永住者等全体_韓国朝鮮籍人口割合_2024.csv")
    print(VIS_DIR / "04_永住者等全体_韓国朝鮮籍人口割合_2024.png")
    print(OUTPUT_DIR / "05_永住者等_3区分別_国籍別人口構成比_2024.csv")
    print(VIS_DIR / "05_永住者等_3区分別_国籍別人口構成比_2024.png")
    print(OUTPUT_DIR / "06_永住者等_3区分別_年代別人口構成比_2024.csv")
    print(VIS_DIR / "06_永住者等_3区分別_年代別人口構成比_2024.png")
    print(OUTPUT_DIR / "07_永住者等_韓国朝鮮籍人口_3区分構成比_2024.csv")
    print(VIS_DIR / "07_永住者等_韓国朝鮮籍人口_3区分構成比_2024.png")
    print(OUTPUT_DIR / "08_永住者等_韓国朝鮮籍別_罪種別検挙人員構成比_2024.csv")
    print(VIS_DIR / "08_永住者等_韓国朝鮮籍別_罪種別検挙人員構成比_2024.png")
    print(OUTPUT_DIR / "09_日本全体_日本人_外国人全体_罪種別検挙人員構成比_2024.csv")
    print(VIS_DIR / "09_日本全体_日本人_外国人全体_罪種別検挙人員構成比_2024.png")
    print(OUTPUT_DIR / "10_罪種別検挙人員構成比_2024_日本全体_日本人_外国人_永住者等_韓国朝鮮籍別.csv")
    print(VIS_DIR / "10_罪種別検挙人員構成比_2024_日本全体_日本人_外国人_永住者等_韓国朝鮮籍別.png")
    print(OUTPUT_DIR / "11_窃盗犯構成比_2024_日本全体_日本人_外国人全体_韓国朝鮮籍別.csv")
    print(VIS_DIR / "11_窃盗犯構成比_2024_日本全体_日本人_外国人全体_韓国朝鮮籍別.png")
    print(OUTPUT_DIR / "12_日本全体_年代別_窃盗犯構成比_2024.csv")
    print(VIS_DIR / "12_日本全体_年代別_窃盗犯構成比_2024.png")


if __name__ == "__main__":
    main()
