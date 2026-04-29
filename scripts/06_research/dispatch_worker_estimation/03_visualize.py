# 在留資格別の推計派遣・請負労働者割合を可視化するコード

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
INPUT_FILE = (
    BASE_PATH
    / "06_research"
    / "dispatch_worker_estimation"
    / "02_intermediate"
    / "01_在留資格別_推計派遣労働者割合.csv"
)
VIS_DIR = BASE_PATH / "06_research" / "dispatch_worker_estimation" / "03_output" / "png"
OUTPUT_BAR = VIS_DIR / "01_在留資格別_推計派遣労働者割合_2024.png"
OUTPUT_BAR_FOCUS = VIS_DIR / "02_在留資格別_推計派遣労働者割合_2024_日本全体_定住者強調.png"
OUTPUT_BAR_FOCUS_SPOUSE = VIS_DIR / "03_在留資格別_推計派遣労働者割合_2024_日本全体_日本人の配偶者等強調.png"
OUTPUT_BAR_FOCUS_PERMANENT = VIS_DIR / "04_在留資格別_推計派遣労働者割合_2024_日本全体_永住者等強調.png"


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


def plot_focus_bar(
    df: pd.DataFrame,
    *,
    focus_status: str,
    focus_color: str,
    japan_overall_pct: float,
    max_xlim: float,
    common_note: str,
    output_file: Path,
) -> None:
    focus_palette = {}
    for status in df["在留資格"]:
        if status == "日本全体":
            focus_palette[status] = "#2F5597"
        elif status == focus_status:
            focus_palette[status] = focus_color
        else:
            focus_palette[status] = "#D8D8D8"

    fig, ax = plt.subplots(figsize=(9, 5.8))
    sns.barplot(
        data=df,
        x="推計派遣労働者割合_pct",
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
        japan_overall_pct,
        color="#2F5597",
        linestyle="--",
        linewidth=1.4,
        alpha=0.9,
    )
    ax.set_title("在留資格別の推計派遣・請負労働者割合（2024年）", pad=14)
    ax.set_xlabel("推計派遣・請負労働者割合（%）")
    ax.set_ylabel("在留資格")
    ax.set_xlim(0, max_xlim)
    fig.text(0.01, 0.015, common_note, ha="left", va="bottom", fontsize=8, color="#4D4D4D")
    save_figure(fig, output_file)


if __name__ == "__main__":
    setup_plot_style()
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    df["推計派遣労働者割合_pct"] = df["推計派遣労働者割合"] * 100
    df = df.sort_values("推計派遣労働者割合", ascending=True).reset_index(drop=True)
    japan_overall_pct = df.loc[df["在留資格"] == "日本全体", "推計派遣労働者割合_pct"].iloc[0]
    max_xlim = max(35, df["推計派遣労働者割合_pct"].max() * 1.18)

    common_note = (
        "注：在留資格別は、厚生労働省「『外国人雇用状況』の届出状況まとめ（令和6年10月末時点）」の\n"
        "業種別「派遣・請負事業」割合と在留資格別業種構成比をもとに推計。日本全体は、総務省統計局"
        "「労働力調査（基本集計）」の「役員を除く雇用者」および「労働者派遣事業所の派遣社員」をもとに作成。"
    )

    # 既存配色の図（従来どおり）
    base_palette = {
        status: "#2F5597" if status == "日本全体" else "#A64B3C"
        for status in df["在留資格"]
    }
    fig, ax = plt.subplots(figsize=(9, 5.8))
    sns.barplot(
        data=df,
        x="推計派遣労働者割合_pct",
        y="在留資格",
        hue="在留資格",
        order=df["在留資格"].tolist(),
        palette=base_palette,
        dodge=False,
        legend=False,
        ax=ax,
    )
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=10)
    ax.axvline(
        japan_overall_pct,
        color="#2F5597",
        linestyle="--",
        linewidth=1.4,
        alpha=0.9,
    )
    ax.set_title("在留資格別の推計派遣・請負労働者割合（2024年）", pad=14)
    ax.set_xlabel("推計派遣・請負労働者割合（%）")
    ax.set_ylabel("在留資格")
    ax.set_xlim(0, max_xlim)
    fig.text(0.01, 0.015, common_note, ha="left", va="bottom", fontsize=8, color="#4D4D4D")
    save_figure(fig, OUTPUT_BAR)

    # 強調配色の図
    plot_focus_bar(
        df,
        focus_status="定住者",
        focus_color="#7A1F1F",
        japan_overall_pct=japan_overall_pct,
        max_xlim=max_xlim,
        common_note=common_note,
        output_file=OUTPUT_BAR_FOCUS,
    )
    plot_focus_bar(
        df,
        focus_status="日本人の配偶者等",
        focus_color="#7A1F1F",
        japan_overall_pct=japan_overall_pct,
        max_xlim=max_xlim,
        common_note=common_note,
        output_file=OUTPUT_BAR_FOCUS_SPOUSE,
    )
    plot_focus_bar(
        df,
        focus_status="永住者等",
        focus_color="#7A1F1F",
        japan_overall_pct=japan_overall_pct,
        max_xlim=max_xlim,
        common_note=common_note,
        output_file=OUTPUT_BAR_FOCUS_PERMANENT,
    )

    print(f"グラフ（従来）: {OUTPUT_BAR}")
    print(f"グラフ（定住者強調）: {OUTPUT_BAR_FOCUS}")
    print(f"グラフ（日本人の配偶者等強調）: {OUTPUT_BAR_FOCUS_SPOUSE}")
    print(f"グラフ（永住者等強調）: {OUTPUT_BAR_FOCUS_PERMANENT}")
    print("処理完了")
