# 日本語能力と賃金の関係を可視化するコード

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
INPUT_FILE = (
    BASE_PATH
    / "06_research"
    / "japanese_ability_wage"
    / "01_tidy"
    / "01_日本語能力別_賃金_tidy.csv"
)
INPUT_STATUS_FILE = (
    BASE_PATH
    / "06_research"
    / "japanese_ability_wage"
    / "01_tidy"
    / "02_在留資格別_平均給与額_tidy.csv"
)
VIS_DIR = BASE_PATH / "06_research" / "japanese_ability_wage" / "03_output" / "png"

OUTPUT_FILES = {
    ("会話", "平均賃金_円"): VIS_DIR / "01_日本語能力_会話_平均賃金_2024.png",
    ("読解", "平均賃金_円"): VIS_DIR / "02_日本語能力_読解_平均賃金_2024.png",
    ("会話", "平均時給_所定内_円"): VIS_DIR / "03_日本語能力_会話_所定内平均時給_2024.png",
    ("読解", "平均時給_所定内_円"): VIS_DIR / "04_日本語能力_読解_所定内平均時給_2024.png",
}
OUTPUT_STATUS_FILE = VIS_DIR / "05_在留資格別_平均給与額_2024.png"


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


def save_figure(fig: plt.Figure, output_file: Path) -> None:
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_wage(
    df: pd.DataFrame,
    ability: str,
    value_column: str,
    title: str,
    xlabel: str,
    output_file: Path,
) -> None:
    plot_df = df[df["能力項目"] == ability].sort_values("能力順", ascending=True).copy()
    plot_df["表示カテゴリ"] = (
        plot_df["日本語能力カテゴリ"] + " (n=" + plot_df["度数"].astype(int).astype(str) + ")"
    )
    colors = [
        "#A64B3C" if order > 4 else "#2F5597"
        for order in plot_df["能力順"]
    ]

    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    sns.barplot(
        data=plot_df,
        x=value_column,
        y="表示カテゴリ",
        palette=colors,
        hue="表示カテゴリ",
        order=plot_df["表示カテゴリ"].tolist(),
        dodge=False,
        legend=False,
        ax=ax,
    )
    for container in ax.containers:
        ax.bar_label(container, fmt="%0.0f", padding=3, fontsize=9)

    ax.set_title(title, pad=14)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("日本語能力カテゴリ（下ほど能力低）")
    ax.margins(x=0.14)
    fig.text(
        0.01,
        0.015,
        "注: 厚生労働省「令和6年外国人雇用実態調査を用いた日本語能力と賃金に関する分析について」をもとに作成。\n"
        "一般労働者に限定。度数はウェイトなし、平均値はウェイトを乗じた復元値。上位4カテゴリを青、下位3カテゴリを赤で表示。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    save_figure(fig, output_file)


def plot_status_wage(df: pd.DataFrame, output_file: Path) -> None:
    order = [
        "外国人常用労働者計",
        "専門的・技術的分野（特定技能除く）",
        "技能実習",
        "特定技能",
        "永住者",
        "定住者",
    ]
    plot_df = df.copy()
    plot_df["在留資格"] = pd.Categorical(plot_df["在留資格"], categories=order, ordered=True)
    plot_df = plot_df.sort_values("在留資格")
    colors = ["#444444", "#2F5597", "#C0504D", "#C27C0E", "#4F81BD", "#9E480E"]

    fig, ax = plt.subplots(figsize=(10.2, 6.2))
    sns.barplot(
        data=plot_df,
        x="平均給与額_千円",
        y="在留資格",
        palette=colors,
        hue="在留資格",
        order=order,
        dodge=False,
        legend=False,
        ax=ax,
    )
    for container in ax.containers:
        ax.bar_label(container, fmt="%0.1f", padding=3, fontsize=9)

    ax.set_title("在留資格別の平均給与額（2024年）", pad=14)
    ax.set_xlabel("平均給与額（千円）")
    ax.set_ylabel("在留資格")
    ax.margins(x=0.12)
    fig.text(
        0.01,
        0.015,
        "注: 厚生労働省「令和6年外国人雇用実態調査を用いた日本語能力と賃金に関する分析について」をもとに作成。\n"
        "一般労働者に限定。在留資格別平均給与額（令和6年調査・一般のみ）。専門的・技術的分野（特定技能除く）は特別集計。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    save_figure(fig, output_file)


if __name__ == "__main__":
    setup_plot_style()
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    df_status = pd.read_csv(INPUT_STATUS_FILE, encoding="utf-8-sig")

    outputs = []
    for ability in ["会話", "読解"]:
        plot_wage(
            df=df,
            ability=ability,
            value_column="平均賃金_円",
            title=f"日本語能力（{ability}）別の平均賃金（2024年）",
            xlabel="平均賃金（円）",
            output_file=OUTPUT_FILES[(ability, "平均賃金_円")],
        )
        outputs.append(OUTPUT_FILES[(ability, "平均賃金_円")])
        plot_wage(
            df=df,
            ability=ability,
            value_column="平均時給_所定内_円",
            title=f"日本語能力（{ability}）別の所定内平均時給（2024年）",
            xlabel="所定内平均時給（円）",
            output_file=OUTPUT_FILES[(ability, "平均時給_所定内_円")],
        )
        outputs.append(OUTPUT_FILES[(ability, "平均時給_所定内_円")])

    plot_status_wage(df_status, OUTPUT_STATUS_FILE)
    outputs.append(OUTPUT_STATUS_FILE)

    for output in outputs:
        print(f"グラフ: {output}")
    print("処理完了")
