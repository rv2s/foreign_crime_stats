# 注意点；来日外国人は、外国人全体と異なり、2024年分も器物損壊等ではなく器物損壊。
# 注意点：2014年分までは、凶悪犯の「強姦」は2022年分まで「不同意性交等」、2023年以降は「強制性交等」に変更されている。
# 注意点：風俗犯の「不同意わいせつ」は2023年以前は「強制わいせつ」。

print("処理を開始します")

import pandas as pd
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parents[2] / "data"
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

INPUT_DIR = BASE_PATH / "00_raw" / "03_検挙人員数_来日外国人"
OUTPUT_DIR = BASE_PATH / "01_tidy" / "03_検挙人員数_来日外国人"

print("処理中です")

# ======== 基本情報 ========
SHEET_CONFIGS = [
    {
        "input_file": "R06_131.xlsx",
        "output_file": "04_2024_tidy.csv",
        "year": "2024",
        "header": None,
        "check_val": 6368,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/不同意性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/不同意わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "R05_131.xlsx",
        "output_file": "04_2023_tidy.csv",
        "year": "2023",
        "header": None,
        "check_val": 5735,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/不同意性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/不同意わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "R04_131.xlsx",
        "output_file": "04_2022_tidy.csv",
        "year": "2022",
        "header": None,
        "check_val": 5014,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "R03_131.xlsx",
        "output_file": "04_2021_tidy.csv",
        "year": "2021",
        "header": None,
        "check_val": 5573,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "R02_131.xlsx",
        "output_file": "04_2020_tidy.csv",
        "year": "2020",
        "header": None,
        "check_val": 5634,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "R01_133.xlsx",
        "output_file": "04_2019_tidy.csv",
        "year": "2019",
        "header": None,
        "check_val": 5563,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H30_133.xls",
        "output_file": "04_2018_tidy.csv",
        "year": "2018",
        "header": None,
        "check_val": 5844,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H29_133.xls",
        "output_file": "04_2017_tidy.csv",
        "year": "2017",
        "header": None,
        "check_val": 6113,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H28_133.xls",
        "output_file": "04_2016_tidy.csv",
        "year": "2016",
        "header": None,
        "check_val": 6097,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H27_133.xls",
        "output_file": "04_2015_tidy.csv",
        "year": "2015",
        "header": None,
        "check_val": 6187,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強制性交等", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H26_134.xls",
        "output_file": "04_2014_tidy.csv",
        "year": "2014",
        "header": None,
        "check_val": 5787,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H25_134.xls",
        "output_file": "04_2013_tidy.csv",
        "year": "2013",
        "header": None,
        "check_val": 5620,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H24_135.xls",
        "output_file": "04_2012_tidy.csv",
        "year": "2012",
        "header": None,
        "check_val": 5423,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H23_135.xls",
        "output_file": "04_2011_tidy.csv",
        "year": "2011",
        "header": None,
        "check_val": 5889,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H22_135.xls",
        "output_file": "04_2010_tidy.csv",
        "year": "2010",
        "header": None,
        "check_val": 6710,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H21_135.xls",
        "output_file": "04_2009_tidy.csv",
        "year": "2009",
        "header": None,
        "check_val": 7190,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H20_135.xls",
        "output_file": "04_2008_tidy.csv",
        "year": "2008",
        "header": None,
        "check_val": 7148,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H19_135.xls",
        "output_file": "04_2007_tidy.csv",
        "year": "2007",
        "header": None,
        "check_val": 7528,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H18_135.xls",
        "output_file": "04_2006_tidy.csv",
        "year": "2006",
        "header": None,
        "check_val": 8148,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
    {
        "input_file": "H17_136.xls",
        "output_file": "04_2005_tidy.csv",
        "year": "2005",
        "header": None,
        "check_val": 8505,
        "sheet": [
            {
                "sheet_name": "01",
                "use_row": {"start": 19, "end": 49}, # startはExcelの開始位置-1(20行目からなら19と入力), endはExcelの終了位置
                "usecols": "B:C, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["凶悪犯/殺人", "凶悪犯/強盗", "凶悪犯/放火", "凶悪犯/強姦", "粗暴犯", "粗暴犯/暴行", "粗暴犯/傷害"],
            },
            {
                "sheet_name": "02",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["粗暴犯/脅迫", "粗暴犯/恐喝", "窃盗犯", "窃盗犯/侵入盗", "知能犯", "知能犯/詐欺", "知能犯/横領", "知能犯/偽造", "知能犯/偽造/通貨偽造", "知能犯/偽造/文書偽造"],
            },
            {
                "sheet_name": "03",
                "use_row": {"start": 20, "end": 50},
                "usecols": "B:C, E, G, I, K, M, P, R, T, V, X",
                "cat_cols": ["州", "国籍・地域"],
                "val_cols": ["知能犯/偽造/有価証券偽造", "風俗犯", "風俗犯/賭博", "風俗犯/強制わいせつ", "風俗犯/公然わいせつ・物", "その他の刑法犯", "その他の刑法犯/占有離脱物横領", "その他の刑法犯/公務執行妨害", "その他の刑法犯/住居侵入", "その他の刑法犯/器物損壊"],
            }
        ]
    },
]

def remove_inner_spaces(s: pd.Series) -> pd.Series:
    # 文字列化 → すべての空白（半角/全角/タブ等）を削除 → 空文字はNAへ
    s = s.astype("string").str.replace(r"\s+", "", regex=True)
    return s.replace("", pd.NA)

def build_one_sheet_wide(input_path: Path, file_cfg: dict, sh_cfg: dict) -> pd.DataFrame:
    # 1) 読み込み（header=Noneで生）
    df = pd.read_excel(
        input_path,
        sheet_name=sh_cfg["sheet_name"],
        header=file_cfg["header"],
        usecols=sh_cfg["usecols"]
    )

    # 2) 行範囲で切る（start以上 end未満）
    r0 = sh_cfg["use_row"]["start"]
    r1 = sh_cfg["use_row"]["end"]
    df = df.iloc[r0:r1].copy()

    # 3) 列名を付ける（cat_cols + val_cols）
    df.columns = sh_cfg["cat_cols"] + sh_cfg["val_cols"]

    # ======== 追加1：cat列を下方向に埋める（州/国籍・地域/属性） ========
    # ======== 文字列整形（空文字→NA） ========
    for c in sh_cfg["cat_cols"]:
        df[c] = remove_inner_spaces(df[c])

    # ======== 州を ffill（州の見出しを下方向に伝播） ========
    df["州"] = df["州"].ffill()

    # ======== 州合計行の削除（国籍・地域が空欄 ＆ その州に内訳行が存在する場合のみ削除） ========
    has_detail_by_state = df.groupby("州")["国籍・地域"].transform(lambda s: s.notna().any())
    is_total_like = df["国籍・地域"].isna()
    df = df[~(is_total_like & has_detail_by_state)].copy()

    # wide（index化）
    return df.set_index(sh_cfg["cat_cols"])


def process_one_file_cfg(cfg: dict, input_dir: Path, output_dir: Path) -> None:
    input_path = input_dir / cfg["input_file"]
    output_path = output_dir / cfg["output_file"]

    dfs_wide = [build_one_sheet_wide(input_path, cfg, sh_cfg) for sh_cfg in cfg["sheet"]]
    wide_merged = pd.concat(dfs_wide, axis=1)

    # ======== 数値化（事故防止） ========
    wide_merged = wide_merged.replace({"-": 0, "－": 0, "―": 0, "−": 0}) # ハイフン系を0に置き換え
    wide_merged = wide_merged.apply(pd.to_numeric, errors="coerce")

    # ======== 親－子合計＝その他 ========
    wide_merged = wide_merged.copy()
    cols = list(wide_merged.columns)

    for parent in cols:
        parent_depth = parent.count("/")
        child_depth = parent_depth + 1
        children = [c for c in cols if c.startswith(parent + "/") and c.count("/") == child_depth]
        if not children:
            continue

        other_col = f"{parent}/その他"
        if other_col in wide_merged.columns:
            continue

        wide_merged[other_col] = wide_merged[parent] - wide_merged[children].sum(axis=1, min_count=1)

    # ======== 親階層（子を持つ列）を削除 ========
    cols2 = list(wide_merged.columns)
    parents_to_drop = [c for c in cols2 if any((d.startswith(c + "/") for d in cols2))]
    wide_merged = wide_merged.drop(columns=parents_to_drop, errors="ignore")

    # ======== tidy化（縦持ち） ========
    cat_cols = cfg["sheet"][0]["cat_cols"]  # 全sheetで共通前提
    df_tidy = (
        wide_merged
        .reset_index()
        .melt(
            id_vars=cat_cols,
            var_name="罪種",
            value_name="検挙人員"
        )
    )

    # 年列（左に）
    df_tidy.insert(0, "年", cfg["year"])
    df_tidy["検挙人員"] = pd.to_numeric(df_tidy["検挙人員"], errors="coerce")

    # ======== 罪種を階層分解（最大3階層） ========
    crime_split = df_tidy["罪種"].astype("string").str.split("/", n=2, expand=True)
    df_tidy["罪種00"] = crime_split[0]
    df_tidy["罪種01"] = crime_split[1]
    df_tidy["罪種02"] = crime_split[2]

    # 列順
    front = ["年", "州", "国籍・地域", "罪種00", "罪種01", "罪種02", "検挙人員"]
    df_tidy = df_tidy[front]

    # 数値チェック
    diff_val = df_tidy["検挙人員"].sum() - cfg["check_val"]

    # 保存
    df_tidy.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"処理完了: {cfg['year']}年分, 差分: {diff_val}")

def main():
    # ======== 全ファイル（年）を実行 ========
    for cfg in SHEET_CONFIGS:
        process_one_file_cfg(cfg, INPUT_DIR, OUTPUT_DIR)


if __name__ == "__main__":
    main()

print("全ての処理が完了しました")

