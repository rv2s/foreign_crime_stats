# 在留資格別の日本語能力を可視化するコード

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib import font_manager
import pandas as pd
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
OUTPUT_DIR = BASE_PATH / "06_research" / "japanese_ability" / "01_tidy"
VIS_DIR = BASE_PATH / "06_research" / "japanese_ability" / "03_output" / "png"
OUTPUT_DATA = OUTPUT_DIR / "01_在留資格別_日本語能力_tidy.csv"
FOCUS_TARGET_SKILLS = {"読む", "書く"}


STATUSES = [
    "全体",
    "技術・人文知識・国際業務",
    "特定技能",
    "技能実習",
    "留学",
    "家族滞在",
    "特定活動",
    "永住者",
    "日本人の配偶者等",
    "定住者",
    "その他",
]

N_BY_STATUS = {
    "全体": 7291,
    "技術・人文知識・国際業務": 1011,
    "特定技能": 532,
    "技能実習": 968,
    "留学": 611,
    "家族滞在": 634,
    "特定活動": 118,
    "永住者": 2088,
    "日本人の配偶者等": 455,
    "定住者": 462,
    "その他": 412,
}

SKILL_DATA = {
    "会話": {
        "page": 71,
        "options": [
            "どんな内容でも適切に会話を進めることができる",
            "流ちょうに自然に会話をすることができる",
            "日常生活で必要な会話ができる",
            "身近で基本的な情報交換ができる",
            "日常的な言い回しを使うことができる",
            "全くできない",
        ],
        "values": {
            "全体": [17.6, 17.5, 33.3, 13.1, 16.1, 2.4],
            "技術・人文知識・国際業務": [22.8, 24.2, 32.7, 11.1, 7.4, 1.7],
            "特定技能": [9.8, 6.8, 45.1, 18.2, 18.6, 1.5],
            "技能実習": [6.5, 3.8, 35.0, 20.1, 31.8, 2.7],
            "留学": [14.9, 20.1, 41.9, 12.3, 9.8, 1.0],
            "家族滞在": [6.2, 8.2, 30.6, 18.3, 31.7, 5.0],
            "特定活動": [11.9, 13.6, 29.7, 13.6, 21.2, 10.2],
            "永住者": [27.3, 24.9, 30.4, 8.2, 7.8, 1.3],
            "日本人の配偶者等": [19.1, 24.4, 30.5, 11.2, 12.5, 2.2],
            "定住者": [14.1, 14.1, 29.9, 14.9, 22.3, 4.8],
            "その他": [16.7, 16.5, 30.1, 12.4, 20.4, 3.9],
        },
    },
    "読む": {
        "page": 78,
        "options": [
            "どんな内容の文章でも容易に読むことができる",
            "新聞記事などを読むことができる",
            "日常生活のEメールなどを読むことができる",
            "簡単で短い文章を読むことができる",
            "掲示等の名前や言葉なら読むことができる",
            "全く分からない",
        ],
        "values": {
            "全体": [13.6, 12.6, 20.6, 29.1, 13.3, 10.7],
            "技術・人文知識・国際業務": [17.1, 21.5, 31.8, 18.0, 5.8, 5.8],
            "特定技能": [3.4, 1.3, 19.9, 50.2, 16.4, 8.8],
            "技能実習": [2.4, 1.1, 10.5, 55.3, 16.3, 14.4],
            "留学": [15.4, 31.3, 26.7, 18.5, 4.7, 3.4],
            "家族滞在": [3.8, 6.5, 20.2, 32.5, 18.9, 18.1],
            "特定活動": [11.9, 9.3, 22.9, 21.2, 11.0, 23.7],
            "永住者": [22.7, 15.2, 19.6, 21.6, 12.7, 8.2],
            "日本人の配偶者等": [13.2, 9.2, 23.7, 28.8, 15.2, 9.9],
            "定住者": [11.7, 5.6, 12.8, 24.0, 24.0, 21.9],
            "その他": [14.3, 13.8, 19.9, 24.5, 14.3, 13.1],
        },
    },
    "書く": {
        "page": 85,
        "options": [
            "明瞭で流ちょうな文章を書くことができる",
            "詳しい説明文を書くことができる",
            "日常生活のEメールなどを書くことができる",
            "短いメモやメッセージを書くことができる",
            "名前や住所などを書くことができる",
            "全くできない",
        ],
        "values": {
            "全体": [8.1, 8.8, 21.9, 30.3, 22.7, 8.1],
            "技術・人文知識・国際業務": [9.9, 15.3, 36.4, 24.4, 10.0, 4.0],
            "特定技能": [2.4, 2.1, 14.5, 48.1, 30.3, 2.6],
            "技能実習": [2.5, 1.5, 8.5, 44.9, 39.3, 3.3],
            "留学": [10.0, 17.7, 40.1, 24.5, 4.7, 2.9],
            "家族滞在": [1.9, 3.5, 15.6, 36.6, 30.6, 11.8],
            "特定活動": [5.1, 11.9, 21.2, 19.5, 20.3, 22.0],
            "永住者": [13.0, 10.7, 22.4, 25.8, 18.6, 9.5],
            "日本人の配偶者等": [5.9, 9.7, 20.7, 28.1, 25.9, 9.7],
            "定住者": [7.8, 4.3, 9.7, 20.8, 34.6, 22.7],
            "その他": [9.5, 7.3, 23.3, 26.0, 24.0, 10.0],
        },
    },
}


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


def make_tidy_data() -> pd.DataFrame:
    rows = []
    for skill, spec in SKILL_DATA.items():
        for status in STATUSES:
            for option_order, (option, value) in enumerate(
                zip(spec["options"], spec["values"][status]), start=1
            ):
                rows.append(
                    {
                        "調査年度": 2024,
                        "能力項目": skill,
                        "在留資格": status,
                        "回答者数": N_BY_STATUS[status],
                        "選択肢順": option_order,
                        "選択肢": option,
                        "割合": round(value / 100, 3),
                        "割合_pct": value,
                        "出典ファイル": "001436052.pdf",
                        "出典ページ": spec["page"],
                        "出典表": f"図表．【在留資格別】日本語能力（{skill}）（単一回答）",
                    }
                )

    return pd.DataFrame(rows)


def plot_skill(
    df: pd.DataFrame,
    skill: str,
    *,
    focused: bool = False,
    focus_statuses: set[str] | None = None,
    focus_label: str = "全体定住者強調",
) -> Path:
    skill_df = df[df["能力項目"] == skill].copy()
    sort_df = (
        skill_df[skill_df["選択肢順"].isin([1, 2, 3])]
        .groupby("在留資格", as_index=False)["割合_pct"]
        .sum()
        .rename(columns={"割合_pct": "上位3選択肢合計_pct"})
    )
    status_order = (
        sort_df.sort_values("上位3選択肢合計_pct", ascending=True)["在留資格"].tolist()
    )

    option_color_map = {
        1: "#9FB9D9",
        2: "#ACC5E1",
        3: "#B9D0E8",
        4: "#B66A5F",
        5: "#A95D52",
        6: "#9C5045",
    }
    options = SKILL_DATA[skill]["options"]

    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    left = pd.Series(0, index=status_order, dtype=float)
    highlight_statuses = focus_statuses or {"定住者"}
    for option_order in [6, 5, 4, 3, 2, 1]:
        option = options[option_order - 1]
        color = option_color_map[option_order]
        values = (
            skill_df[skill_df["選択肢"] == option]
            .set_index("在留資格")
            .loc[status_order, "割合_pct"]
        )
        bar_colors = [to_rgba(color)] * len(status_order)
        edge_colors = [
            to_rgba("#C00000")
            if focused and option_order in {4, 5, 6} and status in highlight_statuses
            else to_rgba("white")
            for status in status_order
        ]
        line_widths = [
            3.2 if focused and option_order in {4, 5, 6} and status in highlight_statuses else 0.8
            for status in status_order
        ]

        ax.barh(
            status_order,
            values,
            left=left,
            color=bar_colors,
            edgecolor=edge_colors,
            linewidth=line_widths,
            label=option,
            height=0.72,
        )
        left += values

    ax.set_title(f"在留資格別の日本語能力（{skill}）（2024年度調査）", pad=14)
    ax.set_xlabel("構成比（%）")
    ax.set_ylabel("在留資格")
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=2,
        frameon=False,
        fontsize=8,
    )
    fig.text(
        0.01,
        0.015,
        "注: 出入国在留管理庁委託事業「外国人との共生社会の実現に向けたロードマップに係る意識調査」をもとに作成。\n"
        "特別永住者は当該設問の対象外。上位3選択肢を青、下位3選択肢を赤で表示。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.14, 1, 1])

    if focused:
        output_file = VIS_DIR / f"02_在留資格別_日本語能力_{skill}_2024_{focus_label}.png"
    else:
        output_file = VIS_DIR / f"01_在留資格別_日本語能力_{skill}_2024.png"
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return output_file


if __name__ == "__main__":
    setup_plot_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    tidy = make_tidy_data()
    tidy.to_csv(OUTPUT_DATA, index=False, encoding="utf-8-sig")

    for target_skill in SKILL_DATA:
        output = plot_skill(tidy, target_skill, focused=False)
        print(f"グラフ（通常）: {output}")
        if target_skill in FOCUS_TARGET_SKILLS:
            output_focus = plot_skill(tidy, target_skill, focused=True)
            print(f"グラフ（全体・定住者強調）: {output_focus}")
        if target_skill == "書く":
            output_spouse_focus = plot_skill(
                tidy,
                target_skill,
                focused=True,
                focus_statuses={"日本人の配偶者等"},
                focus_label="全体日本人の配偶者等強調",
            )
            print(f"グラフ（全体・日本人の配偶者等強調）: {output_spouse_focus}")

    print(f"tidyデータ: {OUTPUT_DATA}")
    print("処理完了")
