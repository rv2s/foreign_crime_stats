# 法務省PDFから在留資格別ヘイトスピーチ経験割合をtidy化するコード

from pathlib import Path

import pandas as pd


BASE_PATH = Path(__file__).resolve().parents[3] / "data"
RAW_FILE = BASE_PATH / "00_raw" / "999_reseach" / "ヘイトスピーチ経験" / "001436052.pdf"
OUTPUT_DIR = BASE_PATH / "06_research" / "hate_speech" / "01_tidy"
OUTPUT_FILE = OUTPUT_DIR / "01_在留資格別_ヘイトスピーチ経験割合_tidy.csv"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = [
        ("全体", 7621, 12.7, 31.6, 38.8, 16.8),
        ("技術・人文知識・国際業務", 1011, 12.8, 40.1, 33.2, 13.9),
        ("特定技能", 532, 11.5, 27.1, 43.8, 17.7),
        ("技能実習", 968, 8.4, 21.3, 49.5, 20.9),
        ("留学", 611, 12.1, 39.1, 30.4, 18.3),
        ("家族滞在", 634, 9.3, 28.1, 41.2, 21.5),
        ("特定活動", 118, 10.2, 34.7, 36.4, 18.6),
        ("永住者", 2088, 13.4, 31.7, 39.5, 15.4),
        ("日本人の配偶者等", 455, 14.3, 25.7, 45.9, 14.1),
        ("定住者", 462, 17.3, 31.2, 36.6, 14.9),
        ("特別永住者", 330, 25.5, 44.8, 20.0, 9.7),
        ("その他", 412, 11.4, 31.1, 37.1, 20.4),
    ]

    df = pd.DataFrame(
        rows,
        columns=[
            "在留資格",
            "回答者数",
            "受けたことがある割合_pct",
            "受けたことはないが見聞きしたことはある割合_pct",
            "受けたことも見聞きしたこともない割合_pct",
            "分からない割合_pct",
        ],
    )
    df.insert(0, "調査年度", 2024)
    df["経験あり割合_pct"] = (
        df["受けたことがある割合_pct"]
        + df["受けたことはないが見聞きしたことはある割合_pct"]
    )

    pct_columns = [column for column in df.columns if column.endswith("_pct")]
    for column in pct_columns:
        df[column.replace("_pct", "")] = (df[column] / 100).round(3)
        df[column] = df[column].round(1)

    df["出典ファイル"] = RAW_FILE.name
    df["出典ページ"] = 553
    df["出典表"] = "図表．【在留資格別】ヘイトスピーチの経験（単一回答）"

    output_columns = [
        "調査年度",
        "在留資格",
        "回答者数",
        "受けたことがある割合",
        "受けたことがある割合_pct",
        "受けたことはないが見聞きしたことはある割合",
        "受けたことはないが見聞きしたことはある割合_pct",
        "経験あり割合",
        "経験あり割合_pct",
        "受けたことも見聞きしたこともない割合",
        "受けたことも見聞きしたこともない割合_pct",
        "分からない割合",
        "分からない割合_pct",
        "出典ファイル",
        "出典ページ",
        "出典表",
    ]
    df = df[output_columns]
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"行数: {len(df)}")
    print(f"保存先: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
