# 外国籍児童の不就学率と日本全体の不登校率、
# および外国籍児童生徒の在籍・日本語支援状況を整理・可視化するコード

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
OUTPUT_BASE = BASE_PATH / "06_research" / "school_attendance"
TIDY_DIR = OUTPUT_BASE / "01_tidy"
VIS_DIR = OUTPUT_BASE / "03_output" / "png"

OUTPUT_CSV_01 = TIDY_DIR / "01_不就学率_不登校率_比較_2024.csv"
OUTPUT_CSV_02 = TIDY_DIR / "02_外国籍児童生徒_在籍と言語支援_2023.csv"
OUTPUT_PNG_01 = VIS_DIR / "01_不就学率_不登校率_比較_2024.png"
OUTPUT_PNG_02 = VIS_DIR / "02_外国籍児童生徒_在籍と言語支援_2023.png"


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
        rc={
            "font.family": selected_font,
            "axes.unicode_minus": False,
        },
    )
    plt.rcParams["font.family"] = selected_font
    plt.rcParams["axes.unicode_minus"] = False


def create_comparison_data():
    foreign_total = 163_358
    foreign_not_enrolled_confirmed = 1_097
    foreign_possible_not_enrolled = 8_432
    japanese_non_attendance = 353_970
    japanese_non_attendance_rate_pct = 3.86

    rows = [
        {
            "年度": 2024,
            "対象": "日本全体（小中学校）",
            "指標": "不登校",
            "対象者数": pd.NA,
            "該当者数": japanese_non_attendance,
            "割合": japanese_non_attendance_rate_pct / 100,
            "割合_pct": japanese_non_attendance_rate_pct,
            "内訳・補足": "小・中学校の不登校児童生徒数。日本の学校に在籍する外国籍児童生徒も内数として含まれると考えられるが、公開統計では内訳不明。",
            "比較上の注意": "不登校は在籍児童生徒の長期欠席に関する指標であり、不就学とは定義が異なる。",
            "出典": "文部科学省「令和6年度 児童生徒の問題行動・不登校等生徒指導上の諸課題に関する調査」",
            "出典URL": "https://www.mext.go.jp/content/20260305-mxt_jidou02-100002753_3.pdf",
        },
        {
            "年度": 2024,
            "対象": "外国籍児童（学齢相当）",
            "指標": "不就学の可能性あり",
            "対象者数": foreign_total,
            "該当者数": foreign_possible_not_enrolled,
            "割合": foreign_possible_not_enrolled / foreign_total,
            "割合_pct": foreign_possible_not_enrolled / foreign_total * 100,
            "内訳・補足": "確認済み不就学者に、就学状況を確認できない者等を加えた人数。",
            "比較上の注意": "学校に接続できていない、または接続状況を把握できない層を含む。",
            "出典": "文部科学省「外国人の子供の就学状況等調査（令和6年度）」",
            "出典URL": "https://www.mext.go.jp/b_menu/houdou/31/09/1421568_00005.htm",
        },
        {
            "年度": 2024,
            "対象": "外国籍児童（学齢相当）",
            "指標": "確認済み不就学",
            "対象者数": foreign_total,
            "該当者数": foreign_not_enrolled_confirmed,
            "割合": foreign_not_enrolled_confirmed / foreign_total,
            "割合_pct": foreign_not_enrolled_confirmed / foreign_total * 100,
            "内訳・補足": "国内外の学校等への就学が確認できない不就学者として把握された人数。",
            "比較上の注意": "学校に接続できていないことが確認された層。",
            "出典": "文部科学省「外国人の子供の就学状況等調査（令和6年度）」",
            "出典URL": "https://www.mext.go.jp/b_menu/houdou/31/09/1421568_00005.htm",
        },
    ]

    return pd.DataFrame(rows)


def create_support_data():
    foreign_public_school = 129_449
    foreign_need_japanese = 57_718
    foreign_special_support = 52_176

    rows = [
        {
            "年度": 2023,
            "対象": "公立学校に在籍する外国籍児童生徒",
            "人数": foreign_public_school,
            "基準人数": foreign_public_school,
            "割合": 1.0,
            "割合_pct": 100.0,
            "注記": "学校基本調査ベースの在籍数。",
            "出典": "文部科学省「日本語指導が必要な児童生徒の受入状況等に関する調査（令和5年度）」",
            "出典URL": "https://www.mext.go.jp/content/20240808-mxt_kyokoku-000037366_3.pdf",
        },
        {
            "年度": 2023,
            "対象": "うち日本語指導が必要",
            "人数": foreign_need_japanese,
            "基準人数": foreign_public_school,
            "割合": foreign_need_japanese / foreign_public_school,
            "割合_pct": foreign_need_japanese / foreign_public_school * 100,
            "注記": "公立学校在籍の外国籍児童生徒に占める割合。",
            "出典": "文部科学省「日本語指導が必要な児童生徒の受入状況等に関する調査（令和5年度）」",
            "出典URL": "https://www.mext.go.jp/content/20240808-mxt_kyokoku-000037366_3.pdf",
        },
        {
            "年度": 2023,
            "対象": "うち特別な配慮に基づく指導を受けている",
            "人数": foreign_special_support,
            "基準人数": foreign_public_school,
            "割合": foreign_special_support / foreign_public_school,
            "割合_pct": foreign_special_support / foreign_public_school * 100,
            "注記": "公立学校在籍の外国籍児童生徒比では40.3%。日本語指導必要者比では90.4%。",
            "出典": "文部科学省「日本語指導が必要な児童生徒の受入状況等に関する調査（令和5年度）」",
            "出典URL": "https://www.mext.go.jp/content/20240808-mxt_kyokoku-000037366_3.pdf",
        },
    ]

    return pd.DataFrame(rows)


def visualize_comparison(df):
    plot_df = df.copy()
    plot_df["表示名"] = plot_df["対象"] + "\n" + plot_df["指標"]

    def order_key(row):
        indicator = str(row["指標"])
        target = str(row["対象"])
        if "日本全体" in target:
            return 0
        if indicator == "不登校":
            return 0
        if indicator == "不就学の可能性あり":
            return 1
        if indicator == "確認済み不就学":
            return 2
        if indicator == "不就学":
            return 2
        return 99

    plot_df["順序"] = plot_df.apply(order_key, axis=1)
    plot_df = plot_df.sort_values("順序", ascending=False)

    colors = {
        "不登校": "#2F5597",
        "不就学の可能性あり": "#A64B3C",
        "確認済み不就学": "#8A8A8A",
    }

    fig, ax = plt.subplots(figsize=(10.4, 5.9))
    bars = ax.barh(
        plot_df["表示名"],
        plot_df["割合_pct"],
        color=[colors[indicator] for indicator in plot_df["指標"]],
        height=0.58,
    )

    for bar, (_, row) in zip(bars, plot_df.iterrows()):
        ax.text(
            bar.get_width() + 0.08,
            bar.get_y() + bar.get_height() / 2,
            f"{row['割合_pct']:.2f}%\n({int(row['該当者数']):,}人)",
            va="center",
            ha="left",
            fontsize=10,
            color="#333333",
        )

    ax.set_title("外国籍児童の不就学可能性と日本全体の不登校率（2024年）", fontsize=15, pad=14)
    ax.set_xlabel("割合（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, max(plot_df["割合_pct"]) * 1.3)
    ax.xaxis.set_major_formatter(lambda x, pos: f"{x:.0f}%")
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    sns.despine(left=True, bottom=False)

    note = (
        "注：文部科学省「令和6年度 児童生徒の問題行動・不登校等生徒指導上の諸課題に関する調査」"
        "\nおよび「外国人の子供の就学状況等調査（令和6年度）」をもとに作成。"
        "不登校と不就学は定義が異なる。"
    )
    fig.text(
        0.01,
        0.01,
        note,
        ha="left",
        va="bottom",
        fontsize=8.5,
        color="#555555",
    )

    fig.tight_layout(rect=[0, 0.09, 1, 1])
    fig.savefig(OUTPUT_PNG_01, dpi=200, bbox_inches="tight")
    plt.close(fig)


def visualize_support(df):
    plot_df = df.copy()
    plot_df = plot_df[plot_df["対象"] != "うち特別な配慮に基づく指導を受けている"].copy()
    plot_df["順序"] = plot_df["対象"].map(
        {
            "公立学校に在籍する外国籍児童生徒": 0,
            "うち日本語指導が必要": 1,
            "うち特別な配慮に基づく指導を受けている": 2,
        }
    )
    plot_df = plot_df.sort_values("順序", ascending=False)

    colors = {
        "公立学校に在籍する外国籍児童生徒": "#2F5597",
        "うち日本語指導が必要": "#8BA6D6",
        "うち特別な配慮に基づく指導を受けている": "#A64B3C",
    }

    fig, ax = plt.subplots(figsize=(10.4, 5.8))
    bars = ax.barh(
        plot_df["対象"],
        plot_df["割合_pct"],
        color=[colors[label] for label in plot_df["対象"]],
        height=0.58,
    )

    for bar, (_, row) in zip(bars, plot_df.iterrows()):
        label = f"{row['割合_pct']:.1f}%\n({int(row['人数']):,}人)"
        if row["対象"] == "うち特別な配慮に基づく指導を受けている":
            label += "\n※日本語指導必要者の90.4%"
        ax.text(
            bar.get_width() + 1.2,
            bar.get_y() + bar.get_height() / 2,
            label,
            va="center",
            ha="left",
            fontsize=10,
            color="#333333",
        )

    ax.set_title("公立学校に在籍する外国籍児童生徒の在籍・日本語支援状況（2023年）", fontsize=15, pad=14)
    ax.set_xlabel("公立学校在籍外国籍児童生徒に占める割合（%）")
    ax.set_ylabel("")
    ax.set_xlim(0, 114)
    ax.xaxis.set_major_formatter(lambda x, pos: f"{x:.0f}%")
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    sns.despine(left=True, bottom=False)

    note = (
        "注：文部科学省「日本語指導が必要な児童生徒の受入状況等に関する調査（令和5年度）」"
        "をもとに作成。公立学校在籍外国籍児童生徒を100とした構成。"
    )
    fig.text(
        0.01,
        0.01,
        textwrap.fill(note, width=78),
        ha="left",
        va="bottom",
        fontsize=8.5,
        color="#555555",
    )

    fig.tight_layout(rect=[0, 0.09, 1, 1])
    fig.savefig(OUTPUT_PNG_02, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    TIDY_DIR.mkdir(parents=True, exist_ok=True)
    VIS_DIR.mkdir(parents=True, exist_ok=True)
    setup_plot_style()

    comparison_df = create_comparison_data()
    support_df = create_support_data()

    comparison_df.to_csv(OUTPUT_CSV_01, index=False, encoding="utf-8-sig")
    support_df.to_csv(OUTPUT_CSV_02, index=False, encoding="utf-8-sig")

    visualize_comparison(comparison_df)
    visualize_support(support_df)

    print(f"CSV: {OUTPUT_CSV_01}")
    print(f"CSV: {OUTPUT_CSV_02}")
    print(f"PNG: {OUTPUT_PNG_01}")
    print(f"PNG: {OUTPUT_PNG_02}")


if __name__ == "__main__":
    main()
