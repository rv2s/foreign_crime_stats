# 在留資格別のヘイトスピーチを受けた経験割合を可視化するコード

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
INPUT_FILE = (
    BASE_PATH
    / "06_research"
    / "hate_speech"
    / "01_tidy"
    / "01_在留資格別_ヘイトスピーチ経験割合_tidy.csv"
)
VIS_DIR = BASE_PATH / "06_research" / "hate_speech" / "03_output" / "png"
OUTPUT_BAR = VIS_DIR / "01_在留資格別_ヘイトスピーチを受けた経験割合_2024.png"
OUTPUT_BAR_FOCUS = VIS_DIR / "02_在留資格別_ヘイトスピーチを受けた経験割合_2024_全体特別永住者強調.png"


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


if __name__ == "__main__":
    setup_plot_style()
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    df = df.sort_values("受けたことがある割合_pct", ascending=True).reset_index(drop=True)
    overall_pct = df.loc[df["在留資格"] == "全体", "受けたことがある割合_pct"].iloc[0]
    palette = {
        status: "#2F5597" if status == "全体" else "#A64B3C"
        for status in df["在留資格"]
    }

    fig, ax = plt.subplots(figsize=(9, 6.4))
    sns.barplot(
        data=df,
        x="受けたことがある割合_pct",
        y="在留資格",
        hue="在留資格",
        order=df["在留資格"].tolist(),
        palette=palette,
        dodge=False,
        legend=False,
        ax=ax,
    )

    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=10)

    ax.axvline(
        overall_pct,
        color="#2F5597",
        linestyle="--",
        linewidth=1.4,
        alpha=0.9,
    )
    ax.set_title("在留資格別のヘイトスピーチを受けた経験割合（2024年度調査）", pad=14)
    ax.set_xlabel("受けたことがある割合（%）")
    ax.set_ylabel("在留資格")
    ax.set_xlim(0, max(30, df["受けたことがある割合_pct"].max() * 1.18))
    fig.text(
        0.01,
        0.015,
        "注: 出入国在留管理庁委託事業「外国人との共生社会の実現に向けたロードマップに係る意識調査」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )

    save_figure(fig, OUTPUT_BAR)

    focus_palette = {}
    for status in df["在留資格"]:
        if status == "全体":
            focus_palette[status] = "#2F5597"
        elif status == "特別永住者":
            focus_palette[status] = "#A64B3C"
        else:
            focus_palette[status] = "#D8D8D8"

    fig, ax = plt.subplots(figsize=(9, 6.4))
    sns.barplot(
        data=df,
        x="受けたことがある割合_pct",
        y="在留資格",
        hue="在留資格",
        order=df["在留資格"].tolist(),
        palette=focus_palette,
        dodge=False,
        legend=False,
        ax=ax,
    )

    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=10, color="#303030")

    ax.axvline(
        overall_pct,
        color="#2F5597",
        linestyle="--",
        linewidth=1.4,
        alpha=0.9,
    )
    ax.set_title("在留資格別のヘイトスピーチを受けた経験割合（2024年度調査）", pad=14)
    ax.set_xlabel("受けたことがある割合（%）")
    ax.set_ylabel("在留資格")
    ax.set_xlim(0, max(30, df["受けたことがある割合_pct"].max() * 1.18))
    fig.text(
        0.01,
        0.015,
        "注: 出入国在留管理庁委託事業「外国人との共生社会の実現に向けたロードマップに係る意識調査」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    save_figure(fig, OUTPUT_BAR_FOCUS)
    print(f"グラフ: {OUTPUT_BAR}")
    print(f"グラフ（全体・特別永住者強調）: {OUTPUT_BAR_FOCUS}")
    print("処理完了")
