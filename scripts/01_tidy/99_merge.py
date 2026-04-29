import pandas as pd
from pathlib import Path


BASE_PATH = Path(__file__).resolve().parents[2] / "data"
TIDY_PATH = BASE_PATH / "01_tidy"
OUT_DIR = TIDY_PATH / "99_merge"

def merge_tidy_csv_files(input_dir, output_path, pattern="*_tidy.csv", encoding="utf-8-sig"):
    """指定ディレクトリ内のCSVを結合して保存する。"""

    input_dir = Path(input_dir)
    output_path = Path(output_path)

    csv_files = sorted(input_dir.glob(pattern))
    if not csv_files:
        raise FileNotFoundError(f"対象ファイルが見つかりません: {input_dir / pattern}")

    dfs = [pd.read_csv(file, encoding=encoding) for file in csv_files]
    merged_df = pd.concat(dfs, ignore_index=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(output_path, index=False, encoding=encoding)

    return merged_df


if __name__ == "__main__":
    print("処理を開始します")

    # 01_検挙人員数_日本全体
    merge_tidy_csv_files(input_dir=TIDY_PATH / "01_検挙人員数_日本全体", output_path=OUT_DIR / "01_検挙人員数_日本全体_merge.csv")

    # 02_検挙人員数_外国人全体
    merge_tidy_csv_files(input_dir=TIDY_PATH / "02_検挙人員数_外国人全体", output_path=OUT_DIR / "02_検挙人員数_外国人全体_merge.csv")

    # 03_検挙人員数_来日外国人
    merge_tidy_csv_files(input_dir=TIDY_PATH / "03_検挙人員数_来日外国人", output_path=OUT_DIR / "03_検挙人員数_来日外国人_merge.csv")

    # 08_検挙人員数_在留資格別
    merge_tidy_csv_files(input_dir=TIDY_PATH / "08_検挙人員数_在留資格別", output_path=OUT_DIR / "08_検挙人員数_在留資格別_merge.csv")

    # 11_人口_日本人
    merge_tidy_csv_files(input_dir=TIDY_PATH / "11_人口_日本人", output_path=OUT_DIR / "11_人口_日本人_merge.csv")

    # 14_不法残留者
    merge_tidy_csv_files(input_dir=TIDY_PATH / "14_不法残留者", output_path=OUT_DIR / "14_不法残留者_merge.csv")

    print("処理が完了しました。")
