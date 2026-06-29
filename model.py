from dataclasses import dataclass, field
from typing import Optional
import openpyxl


@dataclass
class OSSEntry:
    row_num: int
    oss_name: str
    license_name: str
    copyright: str
    license_text: str


@dataclass
class OSSData:
    entries: list[OSSEntry] = field(default_factory=list)

    def add(self, entry: OSSEntry):
        self.entries.append(entry)


# 列番号定数（1始まり）
COL_A  = 1   # 終了判定用
COL_B  = 2   # OSS名
COL_E  = 5   # ライセンス
COL_AA = 27  # Copyright
COL_AB = 28  # ライセンス原文

COLUMN_NAMES = {
    COL_B:  "B",
    COL_E:  "E",
    COL_AA: "AA",
    COL_AB: "AB",
}

START_ROW = 9


# ------------------------------------------------------------------ #
# ダミーワークシート                                                    #
# openpyxl の ws と同じ .cell(row, column).value インターフェースを持つ  #
# ------------------------------------------------------------------ #

# ダミーデータ定義
# キー: (row, col)  ※ 9行目スタート、A列(1)に連番を入れて終了判定に使う
_DUMMY_ROWS = [
    {
        COL_A:  1,
        COL_B:  "requests",
        COL_E:  "Apache-2.0",
        COL_AA: "Copyright 2023 Kenneth Reitz",
        COL_AB: (
            "Apache License\n"
            "Version 2.0, January 2004\n"
            "http://www.apache.org/licenses/\n\n"
            "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION\n"
            "（省略）"
        ),
    },
    {
        COL_A:  2,
        COL_B:  "numpy",
        COL_E:  "BSD-3-Clause",
        COL_AA: "Copyright (c) 2005-2023, NumPy Developers",
        COL_AB: (
            "BSD 3-Clause License\n\n"
            "Redistribution and use in source and binary forms, with or without\n"
            "modification, are permitted provided that the following conditions are met:\n"
            "（省略）"
        ),
    },
    {
        COL_A:  3,
        COL_B:  "flask",
        COL_E:  "BSD-3-Clause",
        COL_AA: "Copyright 2010 Pallets",
        COL_AB: (
            "BSD 3-Clause License\n\n"
            "Copyright 2010 Pallets\n\n"
            "Redistribution and use in source and binary forms ...\n"
            "（省略）"
        ),
    },
]


class _Cell:
    """openpyxl の Cell を模倣する最小実装"""
    def __init__(self, value):
        self.value = value


class DummyWorksheet:
    """
    openpyxl の Worksheet と同じ .cell(row, column) インターフェースを持つ
    ダミーワークシート。Excelファイルが無い環境でのテスト用。
    """

    def __init__(self):
        # (row, col) -> value のマップを構築
        self._data: dict[tuple[int, int], object] = {}
        for i, row_dict in enumerate(_DUMMY_ROWS):
            r = START_ROW + i
            for col, val in row_dict.items():
                self._data[(r, col)] = val
        # max_row を設定（データの最終行）
        self.max_row = START_ROW + len(_DUMMY_ROWS) - 1

    def cell(self, row: int, column: int) -> _Cell:
        return _Cell(self._data.get((row, column), None))


# ------------------------------------------------------------------ #
# Excel / ダミー読み込み                                               #
# ------------------------------------------------------------------ #

def load_excel(filepath: str, sheetname: str, use_dummy: bool = False) -> OSSData:
    if use_dummy:
        ws = DummyWorksheet()
    else:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        if sheetname not in wb.sheetnames:
            raise ValueError(
                f"シート '{sheetname}' が見つかりません。利用可能なシート: {wb.sheetnames}"
            )
        ws = wb[sheetname]

    return _parse_worksheet(ws)


def _parse_worksheet(ws) -> OSSData:
    data = OSSData()
    for row_idx in range(START_ROW, ws.max_row + 1):
        a_val = ws.cell(row=row_idx, column=COL_A).value
        if a_val is None or str(a_val).strip() == "":
            break
        entry = _read_row(ws, row_idx)
        data.add(entry)
    return data


def _read_row(ws, row_idx: int) -> OSSEntry:
    values = {}
    for col, col_name in COLUMN_NAMES.items():
        cell_val = ws.cell(row=row_idx, column=col).value
        if cell_val is None or str(cell_val).strip() == "":
            raise ValueError(
                f"{row_idx}行, {col_name}列が空欄であるため中断、空欄は無いようにしてください"
            )
        values[col] = str(cell_val).strip()

    return OSSEntry(
        row_num=row_idx,
        oss_name=values[COL_B],
        license_name=values[COL_E],
        copyright=values[COL_AA],
        license_text=values[COL_AB],
    )
