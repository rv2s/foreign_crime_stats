# report.md 4章向けのEDA・年齢調整比較グラフを作成するコード

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator
import pandas as pd
import seaborn as sns


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
OUTPUT_DIR = BASE_PATH / "06_research" / "age_adjustment" / "01_tidy"
VIS_DIR = BASE_PATH / "06_research" / "age_adjustment" / "03_output" / "png"

INPUT_ARRESTS = BASE_PATH / "04_integrated" / "09_検挙人員数_統合.csv"
INPUT_POPULATION = BASE_PATH / "04_integrated" / "15_人口_統合.csv"
INPUT_RAW_RATE = BASE_PATH / "05_analytics" / "20_1万人あたり検挙人員数及び対日本人倍率.csv"
INPUT_ADJUSTED_RATE = BASE_PATH / "05_analytics" / "33_対推定検挙人員及び年齢調整後対日本人倍率.csv"
INPUT_TOTAL_ARRESTS_BY_AGE = BASE_PATH / "02_standardized" / "01_検挙人員数_日本全体_名寄せ後.csv"
INPUT_SIMULATED_POPULATION = (
    BASE_PATH / "06_research" / "simulation" / "01_tidy" / "01_日本人外国人_人口構成比_2020_2070.csv"
)


STATUS_ORDER = [
    "計",
    "日本人",
    "外国人計",
    "来日外国人計",
    "永住者等",
    "定住者",
    "日本人の配偶者等",
    "技能実習",
    "留学",
    "短期滞在",
    "その他",
]

LINE_PALETTE = {
    "計": "#444444",
    "日本人": "#2F5597",
    "外国人計": "#C00000",
    "来日外国人計": "#E46C0A",
    "永住者等": "#7030A0",
    "定住者": "#A23E48",
    "日本人の配偶者等": "#9E480E",
    "技能実習": "#548235",
    "留学": "#00A2E8",
    "短期滞在": "#70AD47",
    "その他": "#7F7F7F",
    "その他のうち技術・人文知識・国際業務": "#5B7DB1",
    "その他のうち家族滞在": "#8C8C8C",
    "その他のうち特定技能": "#A64B3C",
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


def save_figure(fig: plt.Figure, output_file: Path) -> None:
    """余白を調整して画像を保存する。"""
    fig.tight_layout()
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def add_line_labels(ax: plt.Axes, df: pd.DataFrame, y_column: str) -> None:
    """各系列の最新年の右側にラベルを付ける。"""
    latest_year = df["年"].max()
    latest = df[df["年"] == latest_year].sort_values(y_column)
    for _, row in latest.iterrows():
        ax.text(
            row["年"] + 0.08,
            row[y_column],
            row["表示区分"],
            va="center",
            fontsize=9,
        )


def lineplot(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    ylabel: str,
    output_file: Path,
    ylim_bottom: float | None = None,
    reference_y: float | None = None,
) -> None:
    """共通形式の折れ線グラフを作成する。"""
    fig, ax = plt.subplots(figsize=(11, 6.2))
    plot_order = [label for label in STATUS_ORDER if label in df["表示区分"].unique()]
    sns.lineplot(
        data=df,
        x="年",
        y=y_column,
        hue="表示区分",
        hue_order=plot_order,
        palette={key: LINE_PALETTE[key] for key in plot_order},
        marker="o",
        linewidth=2.2,
        ax=ax,
    )
    if reference_y is not None:
        ax.axhline(reference_y, color="#333333", linewidth=1.2, linestyle="--", alpha=0.75)
    ax.set_title(title, pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(df["年"].unique()))
    if ylim_bottom is not None:
        ax.set_ylim(bottom=ylim_bottom)
    ax.legend(title="区分", bbox_to_anchor=(1.02, 0.5), loc="center left", borderaxespad=0)
    save_figure(fig, output_file)


def single_barplot(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    ylabel: str,
    output_file: Path,
    color: str = "#2F5597",
    note: str | None = None,
    y_major_step: float | None = None,
) -> None:
    """単一系列の棒グラフを作成する。"""
    fig, ax = plt.subplots(figsize=(11, 6.2))
    plot_df = df.sort_values("年").copy()
    sns.barplot(
        data=plot_df,
        x="年",
        y=y_column,
        color=color,
        width=0.72,
        ax=ax,
    )
    y_max = plot_df[y_column].max()
    if y_major_step is not None:
        y_limit = ((y_max * 1.08 + y_major_step - 1) // y_major_step) * y_major_step
    else:
        y_limit = ((y_max * 1.08 + 499) // 500) * 500
    ax.set_ylim(0, y_limit)
    if y_major_step is not None:
        ax.yaxis.set_major_locator(MultipleLocator(y_major_step))
    ax.set_title(title, pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    sns.despine(left=False, bottom=False)
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
    fig.tight_layout(rect=[0, 0.05 if note else 0, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def single_lineplot(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    ylabel: str,
    output_file: Path,
    color: str = "#2F5597",
    note: str | None = None,
    y_major_step: float | None = None,
    y_min: float | None = None,
    y_max: float | None = None,
) -> None:
    """単一系列の折れ線グラフを作成する。"""
    plot_df = df.sort_values("年").copy()
    fig, ax = plt.subplots(figsize=(11, 6.2))
    sns.lineplot(
        data=plot_df,
        x="年",
        y=y_column,
        marker="o",
        linewidth=2.4,
        color=color,
        ax=ax,
    )
    data_min = plot_df[y_column].min()
    data_max = plot_df[y_column].max()
    if y_major_step is not None:
        lower = y_min if y_min is not None else (data_min // y_major_step) * y_major_step
        upper = y_max if y_max is not None else ((data_max + y_major_step - 1) // y_major_step) * y_major_step
        if lower == upper:
            upper += y_major_step
        ax.set_ylim(lower, upper)
        ax.yaxis.set_major_locator(MultipleLocator(y_major_step))
    elif y_min is not None or y_max is not None:
        ax.set_ylim(
            y_min if y_min is not None else data_min,
            y_max if y_max is not None else data_max,
        )
    ax.set_title(title, pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(plot_df["年"].unique()))
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    sns.despine(left=False, bottom=False)
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
    fig.tight_layout(rect=[0, 0.05 if note else 0, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def japanese_rate_line_with_projection(
    df_actual: pd.DataFrame,
    df_projection: pd.DataFrame,
    y_column: str,
    title: str,
    ylabel: str,
    output_file: Path,
    color: str = "#2F5597",
    note: str | None = None,
    y_major_step: float | None = None,
) -> None:
    """日本人の実績推移に将来予測棒を付けたグラフを作成する。"""
    actual_df = df_actual.sort_values("年").reset_index(drop=True).copy()
    projection_df = df_projection.sort_values("年").reset_index(drop=True).copy()

    actual_positions = list(range(len(actual_df)))
    projection_positions = list(range(len(actual_df), len(actual_df) + len(projection_df)))

    fig, ax = plt.subplots(figsize=(11.8, 6.4))
    ax.plot(
        actual_positions,
        actual_df[y_column],
        color=color,
        marker="o",
        linewidth=2.4,
        markersize=6.5,
    )

    bars = ax.bar(
        projection_positions,
        projection_df[y_column],
        width=0.64,
        facecolor="white",
        edgecolor=color,
        linewidth=2.0,
        linestyle="--",
    )
    for bar in bars:
        bar.set_fill(False)

    all_values = pd.concat([actual_df[y_column], projection_df[y_column]], ignore_index=True)
    value_padding = max(all_values.max() * 0.02, 0.4)

    for x_pos, value in zip(actual_positions, actual_df[y_column]):
        ax.text(
            x_pos,
            value + value_padding,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=color,
        )

    for x_pos, value in zip(projection_positions, projection_df[y_column]):
        ax.text(
            x_pos,
            value + value_padding,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=color,
        )

    tick_positions = actual_positions + projection_positions
    tick_labels = actual_df["年"].astype(str).tolist() + projection_df["年"].astype(str).tolist()
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)

    y_limit = all_values.max() * 1.16
    ax.set_ylim(0, y_limit)
    if y_major_step is not None:
        ax.yaxis.set_major_locator(MultipleLocator(y_major_step))

    ax.set_title(title, pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    sns.despine(left=False, bottom=False)

    legend_handles = [
        plt.Line2D([0], [0], color=color, marker="o", linewidth=2.4, label="実績"),
        plt.Rectangle((0, 0), 1, 1, fill=False, edgecolor=color, linewidth=2.0, linestyle="--", label="予測"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", frameon=False)

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
    fig.tight_layout(rect=[0, 0.05 if note else 0, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def projected_scenario_lineplot(
    df_actual: pd.DataFrame,
    y_column: str,
    title: str,
    ylabel: str,
    output_file: Path,
    base_color: str,
    scenario_specs: list[dict[str, object]],
    note: str | None = None,
    y_major_step: float | None = None,
    y_min: float | None = None,
) -> None:
    """実績線と将来シナリオの分岐点線を描画する。"""
    actual_df = df_actual.sort_values("年").reset_index(drop=True).copy()
    fig, ax = plt.subplots(figsize=(11.4, 6.3))
    actual_positions = list(range(len(actual_df)))
    projection_years = [2040, 2070]
    projection_positions = list(range(len(actual_df), len(actual_df) + len(projection_years)))
    year_to_position = {
        **dict(zip(actual_df["年"].tolist(), actual_positions)),
        **dict(zip(projection_years, projection_positions)),
    }

    ax.plot(
        actual_positions,
        actual_df[y_column],
        color=base_color,
        marker="o",
        linewidth=2.4,
        markersize=6,
        label="実績",
    )

    latest_row = actual_df.iloc[-1]
    latest_year = int(latest_row["年"])
    latest_value = float(latest_row[y_column])

    for x_pos, value in zip(actual_positions, actual_df[y_column]):
        ax.text(
            x_pos,
            value + 0.8,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=8,
            color=base_color,
        )

    for spec in scenario_specs:
        color = str(spec["color"])
        label = str(spec["label"])
        years = [latest_year, 2040, 2070]
        x_positions = [year_to_position[year] for year in years]
        values = [latest_value, float(spec["2040"]), float(spec["2070"])]
        ax.plot(
            x_positions,
            values,
            color=color,
            linestyle="--",
            marker="o",
            linewidth=2.0,
            markersize=5.5,
            label=label,
        )
        ax.text(year_to_position[2040], float(spec["2040"]) + 0.8, f"{float(spec['2040']):.1f}", ha="center", va="bottom", fontsize=8.5, color=color)
        ax.text(year_to_position[2070], float(spec["2070"]) + 0.8, f"{float(spec['2070']):.1f}", ha="center", va="bottom", fontsize=8.5, color=color)

    all_projection_values = [
        latest_value,
        *[float(spec["2040"]) for spec in scenario_specs],
        *[float(spec["2070"]) for spec in scenario_specs],
    ]
    max_value = max(max(actual_df[y_column]), max(all_projection_values))
    upper = ((max_value * 1.12 + (y_major_step or 1) - 1) // (y_major_step or 1)) * (y_major_step or 1)

    ax.set_title(title, pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel(ylabel)
    ax.set_xticks(actual_positions + projection_positions)
    ax.set_xticklabels(actual_df["年"].astype(str).tolist() + [str(year) for year in projection_years])
    ax.set_ylim(y_min if y_min is not None else 0, upper)
    if y_major_step is not None:
        ax.yaxis.set_major_locator(MultipleLocator(y_major_step))
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.legend(loc="upper right", frameon=False)
    sns.despine(left=False, bottom=False)
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
    fig.tight_layout(rect=[0, 0.05 if note else 0, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def total_rate_scenarios_lineplot(
    base_year: int,
    base_value: float,
    scenario_specs: list[dict[str, object]],
    title: str,
    ylabel: str,
    output_file: Path,
    note: str | None = None,
    y_major_step: float | None = None,
    y_min: float | None = None,
    y_max: float | None = None,
) -> None:
    """2024年を起点に将来シナリオを分岐折れ線で示す図を作成する。"""
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    x_positions = [0, 1, 2]
    year_labels = [str(base_year), "2040", "2070"]

    for spec in scenario_specs:
        color = str(spec["color"])
        label = str(spec["label"])
        values = [base_value, float(spec["2040"]), float(spec["2070"])]
        ax.plot(
            x_positions,
            values,
            color=color,
            linestyle="--",
            marker="o",
            linewidth=2.1,
            markersize=6,
            label=label,
        )
        ax.text(
            x_positions[0],
            base_value + 0.04,
            f"{base_value:.1f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=color,
        )
        ax.text(
            x_positions[1],
            float(spec["2040"]) + 0.05,
            f"{float(spec['2040']):.1f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=color,
        )
        ax.text(
            x_positions[2],
            float(spec["2070"]) + 0.05,
            f"{float(spec['2070']):.1f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=color,
        )

    max_value = max(
        [base_value]
        + [float(spec["2040"]) for spec in scenario_specs]
        + [float(spec["2070"]) for spec in scenario_specs]
    )
    upper = y_max if y_max is not None else max_value * 1.12
    lower = y_min if y_min is not None else 0
    if y_major_step is not None and y_max is None:
        upper = ((upper + y_major_step - 1) // y_major_step) * y_major_step
        ax.yaxis.set_major_locator(MultipleLocator(y_major_step))

    legend_handles = [
        plt.Line2D([0], [0], color=str(spec["color"]), linestyle="--", marker="o", linewidth=2.1, label=str(spec["label"]))
        for spec in scenario_specs
    ]

    ax.set_title(title, pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(year_labels)
    ax.set_ylim(lower, upper)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.legend(handles=legend_handles, loc="upper left", frameon=False)
    sns.despine(left=False, bottom=False)

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
    fig.tight_layout(rect=[0, 0.05 if note else 0, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def grouped_barplot(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    ylabel: str,
    output_file: Path,
    hue_order: list[str],
    palette: dict[str, str],
    label_map: dict[str, str] | None = None,
    note: str | None = None,
    y_major_step: float | None = None,
) -> None:
    """年ごとに複数系列を横並びにした棒グラフを作成する。"""
    plot_df = df.sort_values(["年", "表示区分"]).copy()
    if label_map:
        plot_df["表示区分"] = plot_df["表示区分"].astype(str).replace(label_map)

    fig, ax = plt.subplots(figsize=(11, 6.2))
    sns.barplot(
        data=plot_df,
        x="年",
        y=y_column,
        hue="表示区分",
        hue_order=hue_order,
        palette=palette,
        width=0.78,
        ax=ax,
    )
    y_max = plot_df[y_column].max()
    if y_major_step is not None:
        y_limit = ((y_max * 1.08 + y_major_step - 1) // y_major_step) * y_major_step
    else:
        y_limit = ((y_max * 1.08 + 9999) // 10000) * 10000
    ax.set_ylim(0, y_limit)
    if y_major_step is not None:
        ax.yaxis.set_major_locator(MultipleLocator(y_major_step))
    ax.set_title(title, pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.legend(title="区分")
    sns.despine(left=False, bottom=False)
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
    fig.tight_layout(rect=[0, 0.05 if note else 0, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def ordered_barplot(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    ylabel: str,
    output_file: Path,
    order: list[str],
    palette: dict[str, str],
    note: str | None = None,
    y_major_step: float | None = None,
    ratio_base_value: float | None = None,
    ratio_ylabel: str = "対日本人倍率",
    reference_y: float | None = None,
    value_fmt: str = "%.1f",
) -> None:
    """指定順のカテゴリ棒グラフを作成する。"""
    plot_df = df[df[x_column].astype(str).isin(order)].copy()
    plot_df[x_column] = pd.Categorical(plot_df[x_column].astype(str), categories=order, ordered=True)
    plot_df = plot_df.sort_values(x_column)

    fig, ax = plt.subplots(figsize=(11, 6.2))
    sns.barplot(
        data=plot_df,
        x=x_column,
        y=y_column,
        hue=x_column,
        order=order,
        hue_order=order,
        palette=palette,
        width=0.9,
        dodge=False,
        legend=False,
        ax=ax,
    )
    y_max = plot_df[y_column].max()
    if y_max <= 5:
        y_limit = ((y_max * 1.18 + 0.49) // 0.5) * 0.5
    else:
        y_limit = ((y_max * 1.15 + 9) // 10) * 10
    ax.set_ylim(0, y_limit)
    if y_major_step is not None:
        ax.yaxis.set_major_locator(MultipleLocator(y_major_step))
    if reference_y is not None:
        ax.axhline(
            reference_y,
            color="#2F5597",
            linewidth=1.4,
            linestyle="--",
            alpha=0.85,
            zorder=5,
        )
    if ratio_base_value is not None and ratio_base_value > 0:
        ax.axhline(
            ratio_base_value,
            color=palette.get("日本人", "#2F5597"),
            linewidth=1.4,
            linestyle="--",
            alpha=0.85,
            zorder=5,
        )
        secax = ax.secondary_yaxis(
            "right",
            functions=(lambda y: y / ratio_base_value, lambda r: r * ratio_base_value),
        )
        secax.set_ylabel(ratio_ylabel)
        secax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_title(title, pad=14)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", labelrotation=35)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    for container in ax.containers:
        ax.bar_label(container, fmt=value_fmt, padding=12, fontsize=9)
    sns.despine(left=False, bottom=False)
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
    fig.tight_layout(rect=[0, 0.06 if note else 0, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def raw_rate_dual_axis_barplot(
    df: pd.DataFrame,
    output_file: Path,
    *,
    order: list[str],
    note: str | None = None,
) -> None:
    """最新年の年齢調整前1万人あたり検挙人員数を、対日本人倍率の副軸付きで描画する。"""
    plot_df = df[df["表示区分"].isin(order)].copy()
    x_column = "表示区分"
    plot_df[x_column] = pd.Categorical(plot_df[x_column].astype(str), categories=order, ordered=True)
    plot_df = plot_df.sort_values(x_column).reset_index(drop=True)

    japanese_rate = float(plot_df.loc[plot_df["表示区分"] == "日本人", "検挙人員数_1万人あたり"].iloc[0])
    y_max = float(plot_df["検挙人員数_1万人あたり"].max())
    y_upper = max(40, int(((y_max * 1.2) + 9) // 10) * 10)

    fig, ax = plt.subplots(figsize=(11.2, 6.9))
    colors = [LINE_PALETTE.get(label, "#7F7F7F") for label in plot_df["表示区分"]]
    bars = ax.bar(
        plot_df["表示区分"],
        plot_df["検挙人員数_1万人あたり"],
        color=colors,
        edgecolor="white",
        linewidth=0.9,
        width=0.86,
    )

    for bar, value in zip(bars, plot_df["検挙人員数_1万人あたり"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + y_upper * 0.01,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#666666",
        )

    ax.axhline(japanese_rate, color="#2F5597", linewidth=1.4, linestyle="--", alpha=0.85)
    ax.set_title("1万人あたり検挙人員数（全罪種合計）", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("1万人あたり検挙人員数")
    ax.set_ylim(0, y_upper)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.tick_params(axis="x", labelrotation=35)

    ax_right = ax.twinx()
    ax_right.set_ylim(0, y_upper / japanese_rate)
    ax_right.set_ylabel("対日本人倍率")
    ax_right.yaxis.set_major_locator(MultipleLocator(1))
    ax_right.grid(False)

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
    fig.tight_layout(rect=[0, 0.06 if note else 0, 1, 1])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def small_multiples_barplot(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    output_file: Path,
    panels: list[str],
    note: str,
    ylabel: str = "人数（万人）",
) -> None:
    """複数系列を小分けの棒グラフとして作成する。"""
    plot_df = df[df["表示区分"].isin(panels)].copy()
    plot_df["表示区分"] = pd.Categorical(
        plot_df["表示区分"].astype(str),
        categories=panels,
        ordered=True,
    )
    plot_df = plot_df.sort_values(["表示区分", "年"])
    y_max = plot_df[y_column].max()
    common_y_limit = ((y_max * 1.12 + 49) // 50) * 50

    fig, axes = plt.subplots(3, 3, figsize=(15, 12.6), sharex=True)
    flat_axes = axes.flatten()
    for ax in flat_axes[len(panels) :]:
        ax.axis("off")

    for ax, label in zip(flat_axes, panels, strict=False):
        target = plot_df[plot_df["表示区分"] == label].copy()
        if not target.empty:
            sns.barplot(
                data=target,
                x="年",
                y=y_column,
                color=LINE_PALETTE.get(label, "#5B5B5B"),
                width=0.72,
                ax=ax,
            )
        ax.set_ylim(0, common_y_limit)
        ax.set_title(label, fontsize=12, pad=8)
        ax.set_xlabel("")
        ax.set_ylabel(ylabel if label in [panels[0], panels[3], panels[6]] else "")
        ax.tick_params(axis="x", labelrotation=45, labelbottom=True)
        ax.grid(axis="x", visible=False)
        ax.grid(axis="y", color="#E0E0E0", linewidth=0.7)

    sns.despine(fig=fig, left=False, bottom=False)
    fig.suptitle(title, y=0.99, fontsize=17)
    fig.text(
        0.01,
        0.015,
        note,
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.055, 1, 0.95])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def three_panel_barplot(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    output_file: Path,
    panels: list[str],
    note: str,
    ylabel: str = "人数（万人）",
) -> None:
    """3系列を横並びの棒グラフとして作成する。"""
    plot_df = df[df["表示区分"].isin(panels)].copy()
    years = sorted(plot_df["年"].unique())
    index = pd.MultiIndex.from_product([panels, years], names=["表示区分", "年"])
    plot_df = (
        plot_df.set_index(["表示区分", "年"])
        .reindex(index, fill_value=0)
        .reset_index()
        .sort_values(["表示区分", "年"])
    )
    y_max = plot_df[y_column].max()
    common_y_limit = ((y_max * 1.12 + 9) // 10) * 10

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), sharex=True, sharey=True)
    for ax, label in zip(axes, panels, strict=True):
        target = plot_df[plot_df["表示区分"] == label].copy()
        sns.barplot(
            data=target,
            x="年",
            y=y_column,
            color=LINE_PALETTE.get(label, "#5B5B5B"),
            width=0.72,
            ax=ax,
        )
        ax.set_ylim(0, common_y_limit)
        ax.set_title(label.replace("その他のうち", ""), fontsize=12, pad=8)
        ax.set_xlabel("年")
        ax.set_ylabel(ylabel if label == panels[0] else "")
        ax.tick_params(axis="x", labelrotation=45, labelbottom=True)
        ax.grid(axis="x", visible=False)
        ax.grid(axis="y", color="#E0E0E0", linewidth=0.7)

    sns.despine(fig=fig, left=False, bottom=False)
    fig.suptitle(title, y=0.99, fontsize=16)
    fig.text(
        0.01,
        0.015,
        note,
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.12, 1, 0.93])
    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)


def expected_actual_arrest_barplot(
    df: pd.DataFrame,
    output_file: Path,
    note: str,
    groups: list[str] | None = None,
) -> None:
    """期待検挙人員数と実際の検挙人員数を日本人・外国人で比較する。"""
    if groups is None:
        groups = ["日本人", "外国人計"]

    plot_base = df[df["表示区分"].astype(str).isin(groups)].copy()
    plot_base["表示区分"] = pd.Categorical(
        plot_base["表示区分"].astype(str),
        categories=groups,
        ordered=True,
    )
    plot_df = plot_base.melt(
        id_vars=["年", "表示区分", "対推定値倍率"],
        value_vars=["推定検挙人員", "検挙人員"],
        var_name="区分",
        value_name="人数",
    )
    plot_df["区分"] = plot_df["区分"].replace(
        {
            "推定検挙人員": "期待検挙人員数",
            "検挙人員": "実際の検挙人員数",
        }
    )

    fig_width = 12 if len(groups) > 1 else 7.6
    fig, axes = plt.subplots(1, len(groups), figsize=(fig_width, 5.6), sharey=False)
    if len(groups) == 1:
        axes = [axes]
    palette = {"期待検挙人員数": "#BFBFBF", "実際の検挙人員数": "#2F5597"}
    for ax, label in zip(axes, groups, strict=True):
        target = plot_df[plot_df["表示区分"].astype(str) == label].copy()
        sns.barplot(
            data=target,
            x="区分",
            y="人数",
            hue="区分",
            palette=palette,
            width=0.72,
            dodge=False,
            legend=False,
            ax=ax,
        )
        y_max = target["人数"].max()
        ax.set_ylim(0, y_max * 1.22)
        ax.set_title(label, fontsize=12, pad=8)
        ax.set_xlabel("")
        ax.set_ylabel("検挙人員数" if label == groups[0] else "")
        ax.tick_params(axis="x", labelrotation=0)
        ax.grid(axis="x", visible=False)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", padding=4, fontsize=9)
        ratio = plot_base.loc[plot_base["表示区分"].astype(str) == label, "対推定値倍率"].iloc[0]
        ax.text(
            0.5,
            y_max * 1.12,
            f"実績/期待 = {ratio:.2f}倍",
            ha="center",
            va="center",
            fontsize=10,
            color="#4D4D4D",
        )

    sns.despine(fig=fig, left=False, bottom=False)
    title_suffix = "" if len(groups) > 1 else f"：{groups[0]}"
    fig.suptitle(f"期待検挙人員数と実際の検挙人員数（2024年）{title_suffix}", y=0.99, fontsize=16)
    fig.text(
        0.01,
        0.015,
        note,
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.08, 1, 0.93])
    fig.savefig(output_file, dpi=220)
    plt.close(fig)


def create_engineer_specialist_population_data() -> pd.DataFrame:
    """技術・人文知識・国際業務の人口推移をtidyデータから作成する。"""
    rows = []
    for file_path in sorted((BASE_PATH / "01_tidy" / "10_人口_在留資格別").glob("10_*_tidy.csv")):
        df = pd.read_csv(file_path, encoding="utf-8-sig", usecols=["年", "在留資格", "人口"])
        target = df[df["在留資格"] == "技術・人文知識・国際業務"]
        if target.empty:
            continue
        rows.append(
            {
                "年": int(target["年"].iloc[0]),
                "表示区分": "その他のうち技術・人文知識・国際業務",
                "人数": target["人口"].sum(),
            }
        )
    result = pd.DataFrame(rows).sort_values("年").reset_index(drop=True)
    result["人数_万人"] = result["人数"] / 10000
    return result


def create_other_substatus_population_data() -> pd.DataFrame:
    """その他区分の主な在留資格の人口推移をtidyデータから作成する。"""
    rows = []
    target_statuses = {
        "技術・人文知識・国際業務": "その他のうち技術・人文知識・国際業務",
        "家族滞在": "その他のうち家族滞在",
    }
    for file_path in sorted((BASE_PATH / "01_tidy" / "10_人口_在留資格別").glob("10_*_tidy.csv")):
        df = pd.read_csv(file_path, encoding="utf-8-sig", usecols=["年", "在留資格", "人口"])
        year = int(df["年"].iloc[0])
        for status, label in target_statuses.items():
            rows.append(
                {
                    "年": year,
                    "表示区分": label,
                    "人数": df.loc[df["在留資格"] == status, "人口"].sum(),
                }
            )
        rows.append(
            {
                "年": year,
                "表示区分": "その他のうち特定技能",
                "人数": df.loc[df["在留資格"].astype(str).str.startswith("特定技能"), "人口"].sum(),
            }
        )
    result = pd.DataFrame(rows).sort_values(["表示区分", "年"]).reset_index(drop=True)
    result["人数_万人"] = result["人数"] / 10000
    return result


def make_display_label(df: pd.DataFrame) -> pd.Series:
    """区分列からグラフ表示用のラベルを作成する。"""
    label = df["在留資格"].copy()
    label = label.where(label.notna() & (label != "計"), df["区分01"])
    label = label.where(label.notna() & (label != "計"), df["区分00"])
    label = label.replace(
        {
            "外国人": "外国人計",
            "来日外国人": "来日外国人計",
        }
    )
    return label


def filter_total_crime_rows(df: pd.DataFrame) -> pd.DataFrame:
    """全罪種合計の行に絞る。"""
    return df[(df["罪種00"] == "計") & (df["罪種01"] == "計")].copy()


def add_display_order(df: pd.DataFrame) -> pd.DataFrame:
    """表示順を付与して並べ替える。"""
    df = df.copy()
    df["表示区分"] = make_display_label(df)
    df = df[df["表示区分"].isin(STATUS_ORDER)].copy()
    df["表示区分"] = pd.Categorical(df["表示区分"], categories=STATUS_ORDER, ordered=True)
    return df.sort_values(["表示区分", "年"]).reset_index(drop=True)


def create_population_data(df_population: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """日本人人口推移と在留資格別外国人人口推移の可視化用データを作成する。"""
    df_japanese = (
        df_population[df_population["区分00"] == "日本人"]
        .groupby("年", as_index=False)["人数"]
        .sum()
    )
    df_japanese["表示区分"] = "日本人"
    df_japanese["人数_万人"] = df_japanese["人数"] / 10000

    df_foreign = df_population[df_population["区分00"] == "外国人"].copy()
    df_foreign["表示区分"] = make_display_label(df_foreign)
    df_foreign_by_status = (
        df_foreign.groupby(["年", "表示区分"], as_index=False)["人数"]
        .sum()
    )

    df_foreign_total = df_foreign.groupby("年", as_index=False)["人数"].sum()
    df_foreign_total["表示区分"] = "外国人計"

    df_visitor_total = (
        df_foreign[df_foreign["区分01"] == "来日外国人"]
        .groupby("年", as_index=False)["人数"]
        .sum()
    )
    df_visitor_total["表示区分"] = "来日外国人計"

    df_foreign = pd.concat(
        [df_foreign_total, df_visitor_total, df_foreign_by_status],
        ignore_index=True,
    )
    df_foreign = df_foreign[df_foreign["表示区分"].isin(STATUS_ORDER)].copy()
    df_foreign["表示区分"] = pd.Categorical(
        df_foreign["表示区分"],
        categories=[label for label in STATUS_ORDER if label != "計" and label != "日本人"],
        ordered=True,
    )
    df_foreign["人数_万人"] = df_foreign["人数"] / 10000
    df_foreign = df_foreign.sort_values(["表示区分", "年"]).reset_index(drop=True)

    return df_japanese, df_foreign


def create_arrest_count_data(df_arrests: pd.DataFrame) -> pd.DataFrame:
    """全体・日本人・外国人区分別の検挙人員数推移データを作成する。"""
    dimensions = ["区分00", "区分01", "在留資格"]
    hierarchies = [
        [],
        ["区分00"],
        ["区分00", "区分01"],
        ["区分00", "区分01", "在留資格"],
    ]

    frames = []
    for hierarchy in hierarchies:
        group_columns = ["年"] + hierarchy
        target = df_arrests.copy()
        if hierarchy:
            target = target.dropna(subset=hierarchy)
        grouped = target.groupby(group_columns, as_index=False, dropna=False)["検挙人員"].sum()
        for column in dimensions:
            if column not in grouped.columns:
                grouped[column] = "計"
        frames.append(grouped[["年"] + dimensions + ["検挙人員"]])

    df = pd.concat(frames, ignore_index=True)
    return add_display_order(df)


def create_age_specific_total_rate(
    df_arrests_by_age: pd.DataFrame,
    df_population: pd.DataFrame,
) -> pd.DataFrame:
    """日本全体の年代別検挙人員割合を算出する。"""
    df_arrests = df_arrests_by_age[df_arrests_by_age["年"] >= 2013].copy()
    df_arrests = (
        df_arrests.groupby(["年", "年代"], as_index=False, dropna=False)["検挙人員"]
        .sum()
    )

    df_population = df_population[df_population["年代"] != "0~13歳"].copy()
    df_population = (
        df_population.groupby(["年", "年代"], as_index=False, dropna=False)["人数"]
        .sum()
    )

    df = pd.merge(
        left=df_arrests,
        right=df_population,
        on=["年", "年代"],
        how="left",
        validate="1:1",
    )
    missing_population = df[df["人数"].isna()][["年", "年代"]].drop_duplicates()
    if not missing_population.empty:
        raise ValueError(
            "人口データが存在しない年・年代があります: "
            + ", ".join(
                f"{row.年}:{row.年代}"
                for row in missing_population.itertuples(index=False)
            )
        )

    df["検挙人員割合"] = df["検挙人員"] / df["人数"]
    df["検挙人員数_1万人あたり"] = df["検挙人員割合"] * 10000
    age_order = ["10代(14歳以上)", "20代", "30代", "40代", "50代", "60代", "70代以上"]
    df["年代"] = pd.Categorical(df["年代"], categories=age_order, ordered=True)
    return df.sort_values(["年代", "年"]).reset_index(drop=True)


def create_age_composition_data(df_population: pd.DataFrame) -> pd.DataFrame:
    """日本人と外国人全体の年代別構成比を算出する。"""
    df = df_population.copy()
    df["表示区分"] = df["区分00"].replace({"外国人": "外国人全体"})
    df = df[df["表示区分"].isin(["日本人", "外国人全体"])].copy()

    df = (
        df.groupby(["年", "表示区分", "年代"], as_index=False, dropna=False)["人数"]
        .sum()
    )
    df["総人数"] = df.groupby(["年", "表示区分"], observed=True)["人数"].transform("sum")
    df["構成比"] = df["人数"] / df["総人数"]
    df["構成比_pct"] = df["構成比"] * 100

    age_order = ["0~13歳", "10代(14歳以上)", "20代", "30代", "40代", "50代", "60代", "70代以上"]
    df["年代"] = pd.Categorical(df["年代"], categories=age_order, ordered=True)
    df["表示区分"] = pd.Categorical(df["表示区分"], categories=["日本人", "外国人全体"], ordered=True)
    return df.sort_values(["表示区分", "年代", "年"]).reset_index(drop=True)


def create_japanese_rate_projection_data(df_raw_rate_total: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """日本人の実績推移と、2024年率据え置きの将来予測データを作成する。"""
    actual_df = (
        df_raw_rate_total[df_raw_rate_total["表示区分"].astype(str) == "日本人"][
            ["年", "表示区分", "検挙人員数_1万人あたり"]
        ]
        .sort_values("年")
        .reset_index(drop=True)
        .copy()
    )
    latest_row = actual_df.sort_values("年").iloc[-1]
    latest_rate = float(latest_row["検挙人員数_1万人あたり"])

    df_simulated = pd.read_csv(INPUT_SIMULATED_POPULATION, encoding="utf-8-sig")
    target_years = [2040, 2070]
    simulated_lookup = df_simulated[df_simulated["年"].isin(target_years)][["年", "日本人人口_千人"]].copy()

    projection_df = simulated_lookup.copy()
    projection_df["表示区分"] = "日本人"
    projection_df["検挙人員数_1万人あたり"] = latest_rate
    projection_df["想定"] = "2024年率据え置き"
    projection_df["推計検挙人員"] = projection_df["日本人人口_千人"] * 1000 * latest_rate / 10000
    projection_df = projection_df[["年", "表示区分", "検挙人員数_1万人あたり", "日本人人口_千人", "推計検挙人員", "想定"]]
    return actual_df, projection_df.sort_values("年").reset_index(drop=True)


def create_japanese_rate_fixed_projection_data(
    df_raw_rate_total: pd.DataFrame,
    fixed_rate: float,
    assumption_label: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """日本人の実績推移と、指定率固定の将来予測データを作成する。"""
    actual_df = (
        df_raw_rate_total[df_raw_rate_total["表示区分"].astype(str) == "日本人"][
            ["年", "表示区分", "検挙人員数_1万人あたり"]
        ]
        .sort_values("年")
        .reset_index(drop=True)
        .copy()
    )

    df_simulated = pd.read_csv(INPUT_SIMULATED_POPULATION, encoding="utf-8-sig")
    target_years = [2040, 2070]
    simulated_lookup = df_simulated[df_simulated["年"].isin(target_years)][["年", "日本人人口_千人"]].copy()

    projection_df = simulated_lookup.copy()
    projection_df["表示区分"] = "日本人"
    projection_df["検挙人員数_1万人あたり"] = fixed_rate
    projection_df["想定"] = assumption_label
    projection_df["推計検挙人員"] = projection_df["日本人人口_千人"] * 1000 * fixed_rate / 10000
    projection_df = projection_df[["年", "表示区分", "検挙人員数_1万人あたり", "日本人人口_千人", "推計検挙人員", "想定"]]
    return actual_df, projection_df.sort_values("年").reset_index(drop=True)


def main() -> None:
    setup_plot_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    df_arrests = pd.read_csv(INPUT_ARRESTS, encoding="utf-8-sig")
    df_population = pd.read_csv(INPUT_POPULATION, encoding="utf-8-sig")
    df_raw_rate = pd.read_csv(INPUT_RAW_RATE, encoding="utf-8-sig")
    df_adjusted_rate = pd.read_csv(INPUT_ADJUSTED_RATE, encoding="utf-8-sig")
    df_arrests_by_age = pd.read_csv(INPUT_TOTAL_ARRESTS_BY_AGE, encoding="utf-8-sig")

    # 1. 日本人人口の推移
    df_japanese_population, df_foreign_population = create_population_data(df_population)
    df_japanese_population.to_csv(
        OUTPUT_DIR / "01_日本人人口推移_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    single_lineplot(
        df=df_japanese_population,
        y_column="人数_万人",
        title="日本人人口の推移",
        ylabel="人数（万人）",
        output_file=VIS_DIR / "01_日本人人口推移.png",
        note="注: 総務省統計局「人口推計」をもとに作成。各年10月1日時点。単位は万人。",
        y_major_step=1000,
        y_min=10000,
        y_max=14000,
    )

    # 2. 在留資格別外国人人口の推移
    df_foreign_population.to_csv(
        OUTPUT_DIR / "02_在留資格別外国人人口推移_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    foreign_total_population = df_foreign_population[
        df_foreign_population["表示区分"].astype(str) == "外国人計"
    ].copy()
    single_barplot(
        df=foreign_total_population,
        y_column="人数_万人",
        title="外国人人口の推移",
        ylabel="人数（万人）",
        output_file=VIS_DIR / "02_在留資格別外国人人口推移.png",
        color="#C00000",
        note="注: 出入国在留管理庁「在留外国人統計」等をもとに作成。各年10月1日時点に近い人口を使用。単位は万人。",
        y_major_step=50,
    )
    df_engineer_specialist = create_engineer_specialist_population_data()
    df_foreign_population_panels = pd.concat(
        [df_foreign_population, df_engineer_specialist],
        ignore_index=True,
    )
    small_multiples_barplot(
        df=df_foreign_population_panels,
        y_column="人数_万人",
        title="在留資格別外国人人口の推移",
        output_file=VIS_DIR / "02b_在留資格別外国人人口推移_7区分.png",
        panels=[
            "技能実習",
            "留学",
            "短期滞在",
            "定住者",
            "日本人の配偶者等",
            "永住者等",
            "その他",
        ],
        note="注: 出入国在留管理庁「在留外国人統計」等をもとに作成。短期滞在は出入国管理統計から年換算人口を推計。単位は万人。",
    )
    df_other_substatus_population = create_other_substatus_population_data()
    df_other_substatus_population.to_csv(
        OUTPUT_DIR / "02c_その他内訳人口推移_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    three_panel_barplot(
        df=df_other_substatus_population,
        y_column="人数_万人",
        title="その他区分の主な在留資格別人口の推移",
        output_file=VIS_DIR / "02c_その他内訳人口推移_3区分.png",
        panels=[
            "その他のうち技術・人文知識・国際業務",
            "その他のうち家族滞在",
            "その他のうち特定技能",
        ],
        note="注: 出入国在留管理庁「在留外国人統計」をもとに作成。特定技能は特定技能1号・2号を合算。単位は万人。",
    )

    # 3. 検挙人員数の推移
    df_arrest_count = create_arrest_count_data(df_arrests)
    df_arrest_count.to_csv(
        OUTPUT_DIR / "03_検挙人員数推移_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    arrest_note = "注: 警察庁「犯罪統計」をもとに作成。対象は一般刑法犯。特別法犯および交通業過は除く。"
    grouped_barplot(
        df=df_arrest_count[df_arrest_count["表示区分"].astype(str).isin(["計", "日本人"])],
        y_column="検挙人員",
        title="日本全体・日本人の検挙人員数の推移",
        ylabel="検挙人員",
        output_file=VIS_DIR / "03_検挙人員数推移.png",
        hue_order=["日本全体", "日本人"],
        palette={"日本全体": "#444444", "日本人": "#2F5597"},
        label_map={"計": "日本全体"},
        note=arrest_note,
        y_major_step=50000,
    )
    single_barplot(
        df=df_arrest_count[df_arrest_count["表示区分"].astype(str) == "外国人計"],
        y_column="検挙人員",
        title="外国人全体の検挙人員数の推移",
        ylabel="検挙人員",
        output_file=VIS_DIR / "03b_外国人全体_検挙人員数推移.png",
        color="#C00000",
        note=arrest_note,
        y_major_step=2000,
    )
    small_multiples_barplot(
        df=df_arrest_count,
        y_column="検挙人員",
        title="在留資格別外国人の検挙人員数の推移",
        output_file=VIS_DIR / "03c_在留資格別外国人_検挙人員数推移_7区分.png",
        panels=[
            "技能実習",
            "留学",
            "短期滞在",
            "定住者",
            "日本人の配偶者等",
            "永住者等",
            "その他",
        ],
        note=arrest_note,
        ylabel="検挙人員",
    )

    # 4. 検挙人員割合の推移
    df_raw_rate_total = add_display_order(filter_total_crime_rows(df_raw_rate))
    df_raw_rate_total["日本人との差分倍率"] = df_raw_rate_total["対日本人倍率"] - 1
    df_raw_rate_total.to_csv(
        OUTPUT_DIR / "04_検挙人員割合及び対日本人倍率_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    rate_order = [
        "日本人",
        "外国人計",
        "技能実習",
        "留学",
        "短期滞在",
        "定住者",
        "日本人の配偶者等",
        "永住者等",
        "その他",
    ]
    raw_rate_note = "注: 警察庁「犯罪統計」、総務省統計局「人口推計」、出入国在留管理庁「在留外国人統計」等をもとに作成。対象は一般刑法犯。特別法犯および交通業過は除く。"
    grouped_barplot(
        df=df_raw_rate_total[df_raw_rate_total["表示区分"].astype(str).isin(["計", "日本人"])],
        y_column="検挙人員数_1万人あたり",
        title="日本全体・日本人の1万人あたり検挙人員数の推移",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04_1万人あたり検挙人員数推移.png",
        hue_order=["日本全体", "日本人"],
        palette={"日本全体": "#444444", "日本人": "#2F5597"},
        label_map={"計": "日本全体"},
        note=raw_rate_note,
        y_major_step=10,
    )
    df_japanese_rate_actual, df_japanese_rate_projection = create_japanese_rate_projection_data(df_raw_rate_total)
    pd.concat(
        [
            df_japanese_rate_actual.assign(種別="実績"),
            df_japanese_rate_projection.assign(種別="予測"),
        ],
        ignore_index=True,
    ).to_csv(
        OUTPUT_DIR / "04d_日本人_1万人あたり検挙人員数推移_2040_2070予測_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    japanese_projection_note = (
        "注: 2024年までは警察庁「犯罪統計」、総務省統計局「人口推計」等をもとに作成。"
        " 2040年・2070年は日本人の1万人あたり検挙人員数が2024年と同水準で推移すると仮定した試算。"
        " 日本人人口は国立社会保障・人口問題研究所「日本の将来推計人口（令和5年推計）」を使用。"
    )
    japanese_rate_line_with_projection(
        df_actual=df_japanese_rate_actual,
        df_projection=df_japanese_rate_projection,
        y_column="検挙人員数_1万人あたり",
        title="日本人の1万人あたり検挙人員数の推移と将来試算",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04d_日本人_1万人あたり検挙人員数推移_2040_2070予測.png",
        color="#2F5597",
        note=japanese_projection_note,
        y_major_step=10,
    )
    df_japanese_rate_actual_15, df_japanese_rate_projection_15 = create_japanese_rate_fixed_projection_data(
        df_raw_rate_total=df_raw_rate_total,
        fixed_rate=15.0,
        assumption_label="2040年・2070年は15.0人固定",
    )
    pd.concat(
        [
            df_japanese_rate_actual_15.assign(種別="実績"),
            df_japanese_rate_projection_15.assign(種別="予測"),
        ],
        ignore_index=True,
    ).to_csv(
        OUTPUT_DIR / "04d2_日本人_1万人あたり検挙人員数推移_2040_2070予測_15人固定_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    japanese_projection_note_15 = (
        "注: 2024年までは警察庁「犯罪統計」、総務省統計局「人口推計」等をもとに作成。"
        " 2040年・2070年は日本人の1万人あたり検挙人員数が15.0人で推移すると仮定した試算。"
        " 日本人人口は国立社会保障・人口問題研究所「日本の将来推計人口（令和5年推計）」を使用。"
    )
    japanese_rate_line_with_projection(
        df_actual=df_japanese_rate_actual_15,
        df_projection=df_japanese_rate_projection_15,
        y_column="検挙人員数_1万人あたり",
        title="日本人の1万人あたり検挙人員数の推移と将来試算（15.0人固定）",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04d2_日本人_1万人あたり検挙人員数推移_2040_2070予測_15人固定.png",
        color="#2F5597",
        note=japanese_projection_note_15,
        y_major_step=10,
    )
    df_rate_2024_comparison = df_raw_rate_total[
        (df_raw_rate_total["年"] == 2024)
        & (df_raw_rate_total["表示区分"].astype(str).isin(["日本人", "外国人計", "計"]))
    ].copy()
    df_rate_2024_comparison["表示区分"] = df_rate_2024_comparison["表示区分"].astype(str).replace(
        {"外国人計": "外国人全体", "計": "日本全体"}
    )
    df_rate_2024_comparison.to_csv(
        OUTPUT_DIR / "04e_2024年_1万人あたり検挙人員数_比較_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ordered_barplot(
        df=df_rate_2024_comparison,
        x_column="表示区分",
        y_column="検挙人員数_1万人あたり",
        title="2024年の1万人あたり検挙人員数の比較",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04e_2024年_1万人あたり検挙人員数_比較.png",
        order=["日本人", "外国人全体", "日本全体"],
        palette={"日本人": "#2F5597", "外国人全体": "#C00000", "日本全体": "#444444"},
        note=raw_rate_note,
        y_major_step=10,
        value_fmt="%.1f",
    )
    df_total_rate_scenarios = pd.DataFrame(
        [
            {"表示区分": "2024年の日本全体", "検挙人員数_1万人あたり": 17.2},
            {"表示区分": "2040年の日本全体（改善）", "検挙人員数_1万人あたり": 17.0},
            {"表示区分": "2040年の日本全体（横置き）", "検挙人員数_1万人あたり": 17.3},
            {"表示区分": "2040年の日本全体（悪化）", "検挙人員数_1万人あたり": 17.5},
            {"表示区分": "2070年の日本全体（改善）", "検挙人員数_1万人あたり": 17.1},
            {"表示区分": "2070年の日本全体（横置き）", "検挙人員数_1万人あたり": 17.8},
            {"表示区分": "2070年の日本全体（悪化）", "検挙人員数_1万人あたり": 18.2},
        ]
    )
    df_total_rate_scenarios.to_csv(
        OUTPUT_DIR / "04f_日本全体_1万人あたり検挙人員数_将来シナリオ比較_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    scenario_note = (
        "注: 2024年は日本全体の実績値。2040年・2070年は、日本人の1万人あたり検挙人員数が16.8人で固定されると仮定し、"
        "外国人割合を2040年5.2%、2070年10.8%、外国人の1万人あたり検挙人員数を"
        "改善20.0・横置き26.4・悪化35.0と置いた試算。"
    )
    ordered_barplot(
        df=df_total_rate_scenarios,
        x_column="表示区分",
        y_column="検挙人員数_1万人あたり",
        title="日本全体の1万人あたり検挙人員数の将来シナリオ比較",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04f_日本全体_1万人あたり検挙人員数_将来シナリオ比較.png",
        order=[
            "2024年の日本全体",
            "2040年の日本全体（改善）",
            "2040年の日本全体（横置き）",
            "2040年の日本全体（悪化）",
            "2070年の日本全体（改善）",
            "2070年の日本全体（横置き）",
            "2070年の日本全体（悪化）",
        ],
        palette={
            "2024年の日本全体": "#444444",
            "2040年の日本全体（改善）": "#9CCB86",
            "2040年の日本全体（横置き）": "#E6B656",
            "2040年の日本全体（悪化）": "#D77A61",
            "2070年の日本全体（改善）": "#6AA84F",
            "2070年の日本全体（横置き）": "#C27C0E",
            "2070年の日本全体（悪化）": "#C0504D",
        },
        note=scenario_note,
        y_major_step=1,
        value_fmt="%.1f",
    )
    total_rate_scenarios_lineplot(
        base_year=2024,
        base_value=17.2,
        scenario_specs=[
            {"label": "改善シナリオ", "2040": 17.0, "2070": 17.1, "color": "#6AA84F"},
            {"label": "横置きシナリオ", "2040": 17.3, "2070": 17.8, "color": "#C27C0E"},
            {"label": "悪化シナリオ", "2040": 17.7, "2070": 18.8, "color": "#C0504D"},
        ],
        title="日本全体の1万人あたり検挙人員数の将来シナリオ（日本人16.8人固定）",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04g_日本全体_1万人あたり検挙人員数_将来シナリオ_分岐.png",
        note=scenario_note,
        y_major_step=1,
        y_min=15,
        y_max=20,
    )
    scenario_note_japanese_decline = (
        "注: 2024年は日本全体の実績値。2040年・2070年は、日本人の1万人あたり検挙人員数が15.0人へ低下すると仮定し、"
        "外国人割合を2040年5.2%、2070年10.8%、外国人の1万人あたり検挙人員数を"
        "改善20.0・横置き26.4・悪化35.0と置いた試算。"
    )
    total_rate_scenarios_lineplot(
        base_year=2024,
        base_value=17.2,
        scenario_specs=[
            {"label": "改善シナリオ", "2040": 15.3, "2070": 15.5, "color": "#6AA84F"},
            {"label": "横置きシナリオ", "2040": 15.6, "2070": 16.2, "color": "#C27C0E"},
            {"label": "悪化シナリオ", "2040": 16.0, "2070": 17.2, "color": "#C0504D"},
        ],
        title="日本全体の1万人あたり検挙人員数の将来シナリオ（日本人15.0人へ低下）",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04g2_日本全体_1万人あたり検挙人員数_将来シナリオ_分岐_日本人15人低下.png",
        note=scenario_note_japanese_decline,
        y_major_step=1,
        y_min=15,
        y_max=20,
    )
    single_barplot(
        df=df_raw_rate_total[df_raw_rate_total["表示区分"].astype(str) == "外国人計"],
        y_column="検挙人員数_1万人あたり",
        title="外国人全体の1万人あたり検挙人員数の推移",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04b_外国人全体_1万人あたり検挙人員数推移.png",
        color="#C00000",
        note=raw_rate_note,
        y_major_step=10,
    )
    df_foreign_rate_actual = (
        df_raw_rate_total[df_raw_rate_total["表示区分"].astype(str) == "外国人計"][
            ["年", "表示区分", "検挙人員数_1万人あたり"]
        ]
        .sort_values("年")
        .reset_index(drop=True)
        .copy()
    )
    df_foreign_rate_projection = pd.DataFrame(
        [
            {"シナリオ": "低位", "2040": 20.0, "2070": 20.0},
            {"シナリオ": "2024年同水準", "2040": 26.4, "2070": 26.4},
            {"シナリオ": "高位", "2040": 35.0, "2070": 35.0},
        ]
    )
    df_foreign_rate_projection.to_csv(
        OUTPUT_DIR / "04b2_外国人全体_1万人あたり検挙人員数推移_2040_2070シミュレーション_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    foreign_projection_note = (
        "注: 2024年までは警察庁「犯罪統計」、総務省統計局「人口推計」、出入国在留管理庁「在留外国人統計」等をもとに作成。"
        " 2040年・2070年はシミュレーション値。点線は低位20.0、2024年同水準26.4、高位35.0の3パターンを示す。"
    )
    projected_scenario_lineplot(
        df_actual=df_foreign_rate_actual,
        y_column="検挙人員数_1万人あたり",
        title="外国人全体の1万人あたり検挙人員数の推移と将来シミュレーション",
        ylabel="1万人あたり検挙人員数",
        output_file=VIS_DIR / "04b2_外国人全体_1万人あたり検挙人員数推移_2040_2070シミュレーション.png",
        base_color="#C00000",
        scenario_specs=[
            {"label": "予測: 低位", "2040": 20.0, "2070": 20.0, "color": "#F4A3A3"},
            {"label": "予測: 2024年同水準", "2040": 26.4, "2070": 26.4, "color": "#C00000"},
            {"label": "予測: 高位", "2040": 35.0, "2070": 35.0, "color": "#7A0019"},
        ],
        note=foreign_projection_note,
        y_major_step=10,
        y_min=0,
    )
    small_multiples_barplot(
        df=df_raw_rate_total,
        y_column="検挙人員数_1万人あたり",
        title="在留資格別外国人の1万人あたり検挙人員数の推移",
        output_file=VIS_DIR / "04c_在留資格別外国人_1万人あたり検挙人員数推移_7区分.png",
        panels=[
            "技能実習",
            "留学",
            "短期滞在",
            "定住者",
            "日本人の配偶者等",
            "永住者等",
            "その他",
        ],
        note=raw_rate_note,
        ylabel="1万人あたり検挙人員数",
    )

    # 5. 日本人との倍率差
    lineplot(
        df=df_raw_rate_total,
        y_column="対日本人倍率",
        title="日本人との倍率差の推移（年齢調整前、全罪種合計）",
        ylabel="対日本人倍率",
        output_file=VIS_DIR / "05_対日本人倍率推移_年齢調整前.png",
        ylim_bottom=0,
        reference_y=1,
    )
    latest_raw_rate_year = int(df_raw_rate_total["年"].max())
    df_latest_raw_rate_total = df_raw_rate_total[df_raw_rate_total["年"] == latest_raw_rate_year].copy()
    raw_rate_dual_axis_barplot(
        df=df_latest_raw_rate_total,
        output_file=VIS_DIR / "05b_1万人あたり検挙人員数_2024_年齢調整前.png",
        order=[
            "日本人",
            "外国人計",
            "技能実習",
            "留学",
            "短期滞在",
            "定住者",
            "日本人の配偶者等",
            "永住者等",
            "その他",
        ],
        note=f"注: 警察庁「犯罪統計」、総務省統計局「人口推計」、出入国在留管理庁「在留外国人統計」等をもとに作成。{latest_raw_rate_year}年。対象は一般刑法犯。特別法犯および交通業過は除く。",
    )

    # 6. 年齢調整後の対日本人倍率
    df_adjusted_total = add_display_order(filter_total_crime_rows(df_adjusted_rate))
    df_adjusted_total.to_csv(
        OUTPUT_DIR / "06_年齢調整後対日本人倍率_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    latest_adjusted_year = int(df_adjusted_total["年"].max())
    df_latest_adjusted_total = df_adjusted_total[df_adjusted_total["年"] == latest_adjusted_year].copy()
    df_expected_actual = df_latest_adjusted_total[
        df_latest_adjusted_total["表示区分"].astype(str).isin(["日本人", "外国人計"])
    ][["年", "表示区分", "推定検挙人員", "検挙人員", "対推定値倍率"]].copy()
    df_expected_actual.to_csv(
        OUTPUT_DIR / "06b_日本人外国人_期待検挙人員数と実際検挙人員数_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )
    expected_actual_arrest_barplot(
        df=df_expected_actual,
        output_file=VIS_DIR / "06b_日本人外国人_期待検挙人員数と実際検挙人員数_2024.png",
        note=f"注: 警察庁「犯罪統計」、総務省統計局「人口推計」、出入国在留管理庁「在留外国人統計」等をもとに作成。{latest_adjusted_year}年。期待検挙人員数は日本全体の年代別1万人あたり検挙人員数を各区分の年代別人口に当てはめて推計。対象は一般刑法犯。特別法犯および交通業過は除く。",
    )
    expected_actual_arrest_barplot(
        df=df_expected_actual,
        output_file=VIS_DIR / "06c_日本人_期待検挙人員数と実際検挙人員数_2024.png",
        note=f"注: 警察庁「犯罪統計」、総務省統計局「人口推計」をもとに作成。{latest_adjusted_year}年。対象は一般刑法犯。\n期待検挙人員数は、日本全体の年代別の人口に対する検挙人員の割合を\n日本人の年代別人口に乗じて推計。特別法犯および交通業過は除く。",
        groups=["日本人"],
    )
    expected_actual_arrest_barplot(
        df=df_expected_actual,
        output_file=VIS_DIR / "06d_外国人計_期待検挙人員数と実際検挙人員数_2024.png",
        note=f"注: 警察庁「犯罪統計」、総務省統計局「人口推計」、出入国在留管理庁「在留外国人統計」等をもとに作成。{latest_adjusted_year}年。\n期待検挙人員数は、日本全体の年代別の人口に対する検挙人員の割合を\n外国人の年代別人口に乗じて推計。対象は一般刑法犯。特別法犯および交通業過は除く。",
        groups=["外国人計"],
    )
    ordered_barplot(
        df=df_latest_adjusted_total,
        x_column="表示区分",
        y_column="対日本人倍率_年齢調整後",
        title="1万人あたり検挙人員数（年齢調整後）の対日本人倍率（全罪種合計）",
        ylabel="対日本人倍率",
        output_file=VIS_DIR / "06_年齢調整後対日本人倍率推移.png",
        order=rate_order,
        palette={label: LINE_PALETTE.get(label, "#5B5B5B") for label in rate_order},
        note=f"注: 警察庁「犯罪統計」、総務省統計局「人口推計」、出入国在留管理庁「在留外国人統計」等をもとに作成。{latest_adjusted_year}年。日本人=1。対象は一般刑法犯。特別法犯および交通業過は除く。",
        y_major_step=0.5,
        reference_y=1,
        value_fmt="%.2f",
    )

    # 7. 日本全体の年代別検挙人員割合
    df_age_rate = create_age_specific_total_rate(df_arrests_by_age, df_population)
    df_age_rate.to_csv(
        OUTPUT_DIR / "07_日本全体_年代別検挙人員割合_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )

    latest_age_rate_year = int(df_age_rate["年"].max())
    df_latest_age_rate = df_age_rate[df_age_rate["年"] == latest_age_rate_year].copy()
    fig, ax = plt.subplots(figsize=(11, 6.2))
    sns.lineplot(
        data=df_latest_age_rate,
        x="年代",
        y="検挙人員数_1万人あたり",
        marker="o",
        linewidth=2.4,
        color="#2F5597",
        ax=ax,
    )
    ax.set_title("日本全体の年代別1万人あたり検挙人員数（全罪種合計）", pad=14)
    ax.set_xlabel("年代")
    ax.set_ylabel("1万人あたり検挙人員数")
    ax.set_ylim(0, df_latest_age_rate["検挙人員数_1万人あたり"].max() * 1.25)
    ax.tick_params(axis="x", labelrotation=25)
    ax.grid(axis="x", visible=False)
    for _, row in df_latest_age_rate.iterrows():
        ax.text(
            row["年代"],
            row["検挙人員数_1万人あたり"] + 1.1,
            f"{row['検挙人員数_1万人あたり']:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    save_figure(fig, VIS_DIR / "07_日本全体_年代別検挙人員割合推移.png")

    df_latest_age_rate["検挙人員割合_pct"] = df_latest_age_rate["検挙人員割合"] * 100
    fig, ax = plt.subplots(figsize=(11, 6.2))
    sns.barplot(
        data=df_latest_age_rate,
        x="年代",
        y="検挙人員割合_pct",
        color="#444444",
        width=0.72,
        ax=ax,
    )
    ax.set_title("日本全体の年代別人口に対する検挙人員割合", pad=14)
    ax.set_xlabel("年代")
    ax.set_ylabel("人口に対する検挙人員割合（%）")
    ax.set_ylim(0, df_latest_age_rate["検挙人員割合_pct"].max() * 1.25)
    ax.tick_params(axis="x", labelrotation=25)
    ax.grid(axis="x", visible=False)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f%%", padding=4, fontsize=9)
    fig.text(
        0.01,
        0.015,
        "注: 警察庁「犯罪統計」、総務省統計局「人口推計」をもとに作成。2024年。対象は一般刑法犯。特別法犯および交通業過は除く。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(VIS_DIR / "07b_日本全体_年代別人口に対する検挙人員割合_2024.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    df_heatmap = df_age_rate.pivot(
        index="年代",
        columns="年",
        values="検挙人員数_1万人あたり",
    )
    fig, ax = plt.subplots(figsize=(11, 5.3))
    sns.heatmap(
        df_heatmap,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "1万人あたり検挙人員数"},
        ax=ax,
    )
    ax.set_title("日本全体の年代別検挙人員割合ヒートマップ（全罪種合計）", pad=14)
    ax.set_xlabel("年")
    ax.set_ylabel("年代")
    save_figure(fig, VIS_DIR / "08_日本全体_年代別検挙人員割合ヒートマップ.png")

    # 8. 日本人・外国人全体の年齢構成比
    df_age_composition = create_age_composition_data(df_population)
    df_age_composition.to_csv(
        OUTPUT_DIR / "08_日本人外国人全体_年齢構成比_可視化用データ.csv",
        index=False,
        encoding="utf-8-sig",
    )

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
    for ax, group_name in zip(axes, ["日本人", "外国人全体"], strict=True):
        target = df_age_composition[df_age_composition["表示区分"] == group_name].copy()
        target_pivot = target.pivot(
            index="年",
            columns="年代",
            values="構成比_pct",
        )
        target_pivot.plot(
            kind="bar",
            stacked=True,
            ax=ax,
            width=0.82,
            colormap="tab20c",
        )
        ax.set_title(group_name)
        ax.set_xlabel("年")
        ax.set_ylabel("構成比（%）")
        ax.set_ylim(0, 100)
        ax.legend().remove()

    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        title="年代",
        bbox_to_anchor=(1.01, 0.5),
        loc="center left",
        borderaxespad=0,
    )
    fig.suptitle("日本人と外国人全体の年齢構成比", y=1.02)
    save_figure(fig, VIS_DIR / "09_日本人外国人全体_年齢構成比_積み上げ棒.png")

    latest_year = df_age_composition["年"].max()
    df_latest_age_composition = df_age_composition[df_age_composition["年"] == latest_year].copy()
    df_latest_age_composition["表示区分"] = df_latest_age_composition["表示区分"].astype(str).replace(
        {"外国人全体": "外国人"}
    )
    age_order = ["0~13歳", "10代(14歳以上)", "20代", "30代", "40代", "50代", "60代", "70代以上"]
    stacked = (
        df_latest_age_composition.pivot(
            index="表示区分",
            columns="年代",
            values="構成比_pct",
        )
        .reindex(index=["日本人", "外国人"], columns=age_order)
        .fillna(0)
    )
    age_colors = {
        "0~13歳": "#F4B6B0",
        "10代(14歳以上)": "#E88E84",
        "20代": "#D65F5F",
        "30代": "#B94040",
        "40代": "#B9CBE8",
        "50代": "#8FAED8",
        "60代": "#5F86C2",
        "70代以上": "#2F5597",
    }
    fig, ax = plt.subplots(figsize=(9.2, 6.8))
    stacked.plot(
        kind="bar",
        stacked=True,
        width=0.58,
        color=[age_colors[age] for age in age_order],
        ax=ax,
    )
    for container, age in zip(ax.containers, age_order, strict=True):
        labels = [f"{value:.1f}%" if value >= 3 else "" for value in stacked[age]]
        ax.bar_label(container, labels=labels, label_type="center", fontsize=9, color="#303030")
    ax.set_title(f"日本人人口と外国人人口の年齢構成比（{latest_year}年）", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("年齢構成比（%）")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", labelrotation=0)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles[::-1],
        labels[::-1],
        title="年代",
        bbox_to_anchor=(1.02, 0.5),
        loc="center left",
        borderaxespad=0,
    )
    ax.grid(axis="x", visible=False)
    fig.text(
        0.01,
        0.015,
        "注：出入国在留管理庁「在留外国人統計」、総務省統計局「人口推計」をもとに作成。",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4D4D4D",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    fig.savefig(
        VIS_DIR / "10_日本人外国人全体_年齢構成比_最新年比較.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)

    print(f"出力先: {VIS_DIR}")
    print("処理完了")


if __name__ == "__main__":
    main()
