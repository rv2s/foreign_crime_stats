from pathlib import Path
import re

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator
import pandas as pd
from pypdf import PdfReader
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
RAW_PDF = BASE_PATH / "00_raw" / "999_reseach" / "シュミレーション" / "pp2023_gaiyou.pdf"
ACTUAL_POPULATION = BASE_PATH / "04_integrated" / "15_人口_統合.csv"
OUTPUT_DIR = BASE_PATH / "06_research" / "simulation" / "01_tidy"
VIS_DIR = BASE_PATH / "06_research" / "simulation" / "03_output" / "png"
OUTPUT_CSV = OUTPUT_DIR / "01_日本人外国人_人口構成比_2020_2070.csv"
OUTPUT_PNG = VIS_DIR / "01_日本人外国人_人口構成比_2020_2070.png"
OUTPUT_BAR_CSV = OUTPUT_DIR / "02_日本人外国人_人口構成比_2024_2040_2070.csv"
OUTPUT_BAR_PNG = VIS_DIR / "02_日本人外国人_人口構成比_2024_2040_2070_割合棒.png"

TOTAL_TABLE_TITLE = "表1-1 総数,年齢3区分(0～14歳,15～64歳,65歳以上) 別総人口及び年齢構造係数：出生中位(死亡中位)推計"
JAPANESE_TABLE_TITLE = "日本人参考推計表1 総数,年齢3区分(0～14歳,15～64歳 ,65歳以上)別日本人人口及び年齢構造係数：出生中位(死亡中位) 推計"
YEAR_ROW_PATTERN = re.compile(
    r"^\s*(?:令和\s*)?\d+\s+\((\d{4})\)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$"
)


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


def find_page_text(reader: PdfReader, title: str) -> str:
    for page in reader.pages:
        text = page.extract_text() or ""
        if title in text:
            return text
    raise ValueError(f"指定した表題が PDF 内に見つかりません: {title}")


def parse_population_table(page_text: str, label: str) -> pd.DataFrame:
    rows = []
    for line in page_text.splitlines():
        match = YEAR_ROW_PATTERN.match(line)
        if not match:
            continue
        year = int(match.group(1))
        total = int(match.group(2).replace(",", ""))
        age_0_14 = int(match.group(3).replace(",", ""))
        age_15_64 = int(match.group(4).replace(",", ""))
        age_65_plus = int(match.group(5).replace(",", ""))
        share_0_14 = float(match.group(6))
        share_15_64 = float(match.group(7))
        share_65_plus = float(match.group(8))
        rows.append(
            {
                "年": year,
                f"{label}人口_千人": total,
                f"{label}人口_0_14歳_千人": age_0_14,
                f"{label}人口_15_64歳_千人": age_15_64,
                f"{label}人口_65歳以上_千人": age_65_plus,
                f"{label}人口_0_14歳割合_pct": share_0_14,
                f"{label}人口_15_64歳割合_pct": share_15_64,
                f"{label}人口_65歳以上割合_pct": share_65_plus,
            }
        )

    if not rows:
        raise ValueError(f"{label}人口の表から年次データを抽出できませんでした。")

    df = pd.DataFrame(rows)
    return df[(df["年"] >= 2020) & (df["年"] <= 2070)].reset_index(drop=True)


def create_composition_data() -> pd.DataFrame:
    reader = PdfReader(str(RAW_PDF))
    total_text = find_page_text(reader, TOTAL_TABLE_TITLE)
    japanese_text = find_page_text(reader, JAPANESE_TABLE_TITLE)

    df_total = parse_population_table(total_text, "総")
    df_japanese = parse_population_table(japanese_text, "日本人")
    df = pd.merge(df_total, df_japanese, on="年", how="inner", validate="1:1")

    df["外国人人口_千人"] = df["総人口_千人"] - df["日本人人口_千人"]
    df["外国人人口_万人"] = df["外国人人口_千人"] / 10
    df["総人口_万人"] = df["総人口_千人"] / 10
    df["日本人人口_万人"] = df["日本人人口_千人"] / 10
    df["日本人構成比_pct"] = df["日本人人口_千人"] / df["総人口_千人"] * 100
    df["外国人構成比_pct"] = df["外国人人口_千人"] / df["総人口_千人"] * 100
    return df


def create_selected_year_bar_data(df_simulated: pd.DataFrame) -> pd.DataFrame:
    df_actual = pd.read_csv(ACTUAL_POPULATION, encoding="utf-8-sig")
    df_actual_2024 = (
        df_actual[df_actual["年"] == 2024]
        .groupby("区分00", as_index=False)["人数"]
        .sum()
    )
    japanese_2024 = float(df_actual_2024.loc[df_actual_2024["区分00"] == "日本人", "人数"].iloc[0])
    foreign_2024 = float(df_actual_2024.loc[df_actual_2024["区分00"] == "外国人", "人数"].iloc[0])
    total_2024 = japanese_2024 + foreign_2024

    records = [
        {
            "年": 2024,
            "出典": "実データ",
            "日本人人口": japanese_2024,
            "外国人人口": foreign_2024,
            "総人口": total_2024,
        }
    ]

    for year in [2040, 2070]:
        row = df_simulated.loc[df_simulated["年"] == year].iloc[0]
        records.append(
            {
                "年": year,
                "出典": "将来推計",
                "日本人人口": float(row["日本人人口_千人"]) * 1000,
                "外国人人口": float(row["外国人人口_千人"]) * 1000,
                "総人口": float(row["総人口_千人"]) * 1000,
            }
        )

    df = pd.DataFrame(records)
    df["日本人構成比_pct"] = df["日本人人口"] / df["総人口"] * 100
    df["外国人構成比_pct"] = df["外国人人口"] / df["総人口"] * 100
    return df.sort_values("年").reset_index(drop=True)


def plot_composition(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11.8, 6.6))
    ax.stackplot(
        df["年"],
        df["日本人構成比_pct"],
        df["外国人構成比_pct"],
        labels=["日本人", "外国人"],
        colors=["#4C78A8", "#C44E52"],
        alpha=0.96,
    )
    ax.plot(df["年"], df["日本人構成比_pct"], color="#2F5597", linewidth=1.6)
    ax.plot(df["年"], df["外国人構成比_pct"], color="#A23E48", linewidth=1.6)
    ax.set_title("日本人・外国人の人口構成比の推移（2020-2070年推計）", pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel("構成比（%）")
    ax.set_xlim(df["年"].min(), df["年"].max())
    ax.set_ylim(0, 100)
    ax.set_xticks(list(range(2020, 2071, 5)))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.grid(axis="x", color="#E6E6E6", linewidth=0.6)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.legend(loc="upper right", frameon=False)
    fig.text(
        0.01,
        0.015,
        "注: 国立社会保障・人口問題研究所「日本の将来推計人口（令和5年推計）」をもとに作成。"
        " 総人口は出生中位（死亡中位）推計、日本人人口は日本人参考推計表1を使用。"
        " 外国人人口は総人口から日本人人口を差し引いて算出。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    fig.savefig(OUTPUT_PNG, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_selected_year_bar(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 6.2))
    x = range(len(df))
    years = df["年"].astype(str).tolist()

    ax.bar(
        x,
        df["外国人構成比_pct"],
        color="#C44E52",
        edgecolor="white",
        linewidth=0.9,
        width=0.62,
        label="外国人",
    )
    ax.bar(
        x,
        df["日本人構成比_pct"],
        bottom=df["外国人構成比_pct"],
        color="#4C78A8",
        edgecolor="white",
        linewidth=0.9,
        width=0.62,
        label="日本人",
    )

    for i, row in df.iterrows():
        ax.text(i, row["外国人構成比_pct"] / 2, f"{row['外国人構成比_pct']:.1f}%", ha="center", va="center", fontsize=9, color="white")
        ax.text(i, row["外国人構成比_pct"] + row["日本人構成比_pct"] / 2, f"{row['日本人構成比_pct']:.1f}%", ha="center", va="center", fontsize=9, color="white")

    ax.set_title("日本人・外国人の人口構成比（2024・2040・2070年）", pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel("構成比（%）")
    ax.set_xticks(list(x))
    ax.set_xticklabels(years)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles[::-1],
        labels[::-1],
        loc="lower left",
        bbox_to_anchor=(0.79, 0.105),
        bbox_transform=fig.transFigure,
        frameon=False,
    )
    fig.text(
        0.01,
        0.015,
        "注: 2024年は本分析で使用の推計人口をもとに作成。\n"
        "2040年・2070年は国立社会保障・人口問題研究所「日本の将来推計人口（令和5年推計）」の\n"
        "出生中位（死亡中位）推計を使用。外国人人口は総人口から日本人人口を差し引いて算出。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0.03, 0.13, 0.97, 0.97])
    fig.savefig(OUTPUT_BAR_PNG, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    setup_plot_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    df = create_composition_data()
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    plot_composition(df)
    df_bar = create_selected_year_bar_data(df)
    df_bar.to_csv(OUTPUT_BAR_CSV, index=False, encoding="utf-8-sig")
    plot_selected_year_bar(df_bar)

    print(f"CSV: {OUTPUT_CSV}")
    print(f"PNG: {OUTPUT_PNG}")
    print(f"CSV: {OUTPUT_BAR_CSV}")
    print(f"PNG: {OUTPUT_BAR_PNG}")
    print("処理完了")


if __name__ == "__main__":
    main()
