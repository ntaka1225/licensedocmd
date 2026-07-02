"""
テストランナー

Usage:
    python test_runner.py
"""

import sys
from model import (
    load_excel, DummyWorksheet, OSSData, OSSEntry,
    _parse_worksheet, _Cell, START_ROW, COL_A, COL_B, COL_E, COL_AA, COL_AB
)
from controller import generate_text, _build_license_groups, SEPARATOR, LICENSE_SEP, TEXT_SEP

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

results = []


def test(name: str):
    def decorator(fn):
        try:
            fn()
            print(f"  [{PASS}] {name}")
            results.append((name, True, None))
        except Exception as e:
            print(f"  [{FAIL}] {name}")
            print(f"         {e}")
            results.append((name, False, str(e)))
        return fn
    return decorator


# ------------------------------------------------------------------ #
# DummyWorksheet
# ------------------------------------------------------------------ #
print("■ DummyWorksheet")

@test("cell() が正しい値を返す")
def _():
    ws = DummyWorksheet()
    assert ws.cell(row=START_ROW, column=COL_B).value == "requests"
    assert ws.cell(row=START_ROW, column=COL_E).value == "Apache-2.0"

@test("データ範囲外は None を返す")
def _():
    ws = DummyWorksheet()
    assert ws.cell(row=1, column=1).value is None


# ------------------------------------------------------------------ #
# load_excel（ダミー）
# ------------------------------------------------------------------ #
print("■ load_excel(use_dummy=True)")

@test("OSSData が生成される（4件）")
def _():
    data = load_excel(None, None, use_dummy=True)
    assert isinstance(data, OSSData)
    assert len(data.entries) == 8, f"件数が想定と異なる: {len(data.entries)}"

@test("requests: 通常1行完結エントリ")
def _():
    data = load_excel(None, None, use_dummy=True)
    e = data.entries[0]
    assert e.oss_name == "requests"
    assert e.license_names == ["Apache-2.0"]
    assert e.copyrights == ["Copyright 2023 Kenneth Reitz"]
    assert len(e.license_texts) == 1
    assert "Apache License" in e.license_texts[0]

@test("準正常系ケース1: numpy - 著作権者が複数行にまたがる")
def _():
    data = load_excel(None, None, use_dummy=True)
    e = data.entries[1]
    assert e.oss_name == "numpy"
    assert e.copyrights == ["Copyright (c) NumPy Developers", "Copyright 2010 Pallets"], \
        f"copyrights が想定と異なる: {e.copyrights}"
    # E列・AB列はセカンド行がNoneなので増えない
    assert len(e.license_names) == 1
    assert len(e.license_texts) == 1

@test("準正常系ケース2: biglib - ライセンス原文が複数行にまたがる")
def _():
    data = load_excel(None, None, use_dummy=True)
    e = data.entries[2]
    assert e.oss_name == "biglib"
    assert len(e.license_texts) == 2, f"license_texts数が想定と異なる: {len(e.license_texts)}"
    combined = "\n".join(e.license_texts)
    assert "a copy of the Program in return for a fee." in combined
    assert "END OF TERMS AND CONDITIONS" in combined

@test("準正常系ケース3: multilic - 複数ライセンス名をもつ")
def _():
    data = load_excel(None, None, use_dummy=True)
    e = data.entries[3]
    assert e.oss_name == "multilic"
    assert e.license_names == ["MIT", "BSD-3-Clause", "GPL-2.0"], \
        f"license_names が想定と異なる: {e.license_names}"
    # AA/AB列は追加行がNoneなので1件のまま
    assert len(e.copyrights) == 1
    assert len(e.license_texts) == 1


@test("準正常系ケース5: dirtylib - _x000C_ が除去される（データ構造）")
def _():
    data = load_excel(None, None, use_dummy=True)
    e = data.entries[4]
    assert e.oss_name == "dirtylib",              f"OSS名に_x000C_が残っている: {e.oss_name!r}"
    assert e.license_names == ["MIT"],             f"ライセンス名に_x000C_が残っている: {e.license_names}"
    assert "_x000C_" not in e.copyrights[0],      f"著作権者に_x000C_が残っている: {e.copyrights}"
    assert "_x000C_" not in e.license_texts[0],   f"ライセンス原文に_x000C_が残っている: {e.license_texts}"
    # 追記行も除去されている
    assert "_x000C_" not in e.copyrights[1],      f"追記著作権者に_x000C_が残っている: {e.copyrights}"
    assert "_x000C_" not in e.license_texts[1],   f"追記ライセンス原文に_x000C_が残っている: {e.license_texts}"


@test("準正常系ケース6: complexlib - 全組み合わせ（データ構造）")
def _():
    data = load_excel(None, None, use_dummy=True)
    e = data.entries[5]
    assert e.oss_name == "complexlib"
    # 準正常系ケース3: ライセンス名が2種類
    assert e.license_names == ["LGPL-2.1", "MIT"], \
        f"license_names が想定と異なる: {e.license_names}"
    # 準正常系ケース1: 著作権者が2行
    assert e.copyrights == [
        "Copyright (C) 1991 Free Software Foundation",
        "Copyright (c) 2001 Example Contributor",
    ], f"copyrights が想定と異なる: {e.copyrights}"
    # 準正常系ケース2: 原文が3分割
    assert len(e.license_texts) == 3, \
        f"license_texts数が想定と異なる: {len(e.license_texts)}"
    assert "[part1]" in e.license_texts[0]
    assert "[part2]" in e.license_texts[1]
    assert "[part3]" in e.license_texts[2]


# ------------------------------------------------------------------ #
# generate_text（フォーマット出力）
# ------------------------------------------------------------------ #
print("■ generate_text")

@test("準正常系ケース1: Copyright が改行区切りで出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data)
    assert "Copyright (c) NumPy Developers\n           Copyright 2010 Pallets" in text, \
        "著作権者の改行＋インデント連結が出力に含まれない"

@test("準正常系ケース2: ライセンス原文が連結して出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data)
    assert "a copy of the Program in return for a fee.\nEND OF TERMS AND CONDITIONS" in text, \
        "ライセンス原文の連結が出力に含まれない"

@test("準正常系ケース3: License がカンマ区切りで出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data)
    assert "License: MIT, BSD-3-Clause, GPL-2.0" in text, \
        "複数ライセンスのカンマ区切りが出力に含まれない"

@test("準正常系ケース5: dirtylib - _x000C_ が除去されて出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data)
    assert "_x000C_" not in text, f"出力テキストに_x000C_が残っている"
    # 正しい値が含まれている
    assert "dirtylib" in text
    assert "License: MIT" in text
    assert "Copyright 2024 Dirty Corp" in text


@test("準正常系ケース6: complexlib - 準正常系ケース1～3の全組み合わせ（出力テキスト）")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data)
    # ケース2: カンマ区切りライセンス
    assert "License: LGPL-2.1, MIT" in text, \
        f"複数ライセンスのカンマ区切りが出力に含まれない"
    # ケース3: 改行区切り著作権者
    assert "Copyright (C) 1991 Free Software Foundation\n           Copyright (c) 2001 Example Contributor" in text, \
        f"著作権者の改行＋インデント連結が出力に含まれない"
    # ケース1: 原文3ブロック連結
    assert "[part1]" in text and "[part2]" in text and "[part3]" in text, \
        f"ライセンス原文の3分割連結が出力に含まれない"
    # 連結順序の確認
    idx1 = text.index("[part1]")
    idx2 = text.index("[part2]")
    idx3 = text.index("[part3]")
    assert idx1 < idx2 < idx3, "ライセンス原文の順序が正しくない"


@test("存在しないフォーマット名で ValueError")
def _():
    data = load_excel(None, None, use_dummy=True)
    try:
        generate_text(data, "no_such_format")
        raise AssertionError("例外が発生しなかった")
    except ValueError:
        pass


# ------------------------------------------------------------------ #
# 集約フォーマット（aggregate）                                         #
# ------------------------------------------------------------------ #
print("■ generate_text(aggregate)")

@test("集約[Copyrights]: 全OSSが上から順に出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, "aggregate")
    assert "[Copyrights]" in text, "[Copyrights]セクションが存在しない"
    # 全OSSが出現するか確認
    for entry in data.entries:
        assert entry.oss_name in text, f"{entry.oss_name} が出力に含まれない"

@test("集約[Copyrights]: Copyright表記が4スペースインデントで出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, "aggregate")
    # requestsの著作権者が4スペースインデントで出力されているか
    assert "    Copyright 2023 Kenneth Reitz" in text,         "Copyrightが4スペースインデントで出力されていない"

@test("集約[Copyrights]: OSS名は[Copyrights]セクションに登場順で全件出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, "aggregate")
    copyrights_section = text.split("[Licenses]")[0]
    # 全エントリのOSS名が[Copyrights]セクションに含まれる
    for entry in data.entries:
        assert entry.oss_name in copyrights_section,             f"{entry.oss_name} が[Copyrights]セクションに含まれない"

@test("集約[Licenses]: ライセンス原文が同一のエントリがグループ化される")
def _():
    data = load_excel(None, None, use_dummy=True)
    groups = _build_license_groups(data)
    # requests + requests-cache が同じApache-2.0原文 → 1グループ
    apache_groups = [g for g in groups if "Apache-2.0" in g["license_names"]]
    assert len(apache_groups) == 1,         f"Apache-2.0グループが1つになっていない: {len(apache_groups)}個"
    assert set(apache_groups[0]["oss_names"]) == {"requests", "requests-cache"},         f"Apache-2.0グループのOSS名が想定と異なる: {apache_groups[0]['oss_names']}"

@test("集約[Licenses]: ライセンス原文が異なるエントリは別グループになる")
def _():
    data = load_excel(None, None, use_dummy=True)
    groups = _build_license_groups(data)
    gpl_groups = [g for g in groups if "GPL-3.0" in g["license_names"]]
    assert len(gpl_groups) == 1
    assert gpl_groups[0]["oss_names"] == ["biglib"]

@test("集約[Licenses]: ライセンス名が重複除去されて集約される")
def _():
    data = load_excel(None, None, use_dummy=True)
    groups = _build_license_groups(data)
    multilic_text = "MIT License\n\nPermission is hereby granted..."
    mit_groups = [g for g in groups if g["license_text"] == multilic_text]
    assert len(mit_groups) == 1, f"multilic+flask の集約グループが1つになっていない"
    license_names = mit_groups[0]["license_names"]
    assert license_names.count("MIT") == 1, f"MIT が重複している: {license_names}"
    assert set(license_names) == {"MIT", "BSD-3-Clause", "GPL-2.0"},         f"ライセンス名が想定と異なる: {license_names}"
    assert set(mit_groups[0]["oss_names"]) == {"multilic", "flask"},         f"グループのOSS名が想定と異なる: {mit_groups[0]['oss_names']}"

@test("集約[Licenses]: 集約OSS名がカンマ区切りで4スペースインデント付きで出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, "aggregate")
    # requests と requests-cache が同じ原文 → 集約されてカンマ区切りで出力
    assert "    requests, requests-cache:" in text,         "集約OSS名のカンマ区切り・インデントが出力に含まれない"

@test("集約[Licenses]: 単独OSSも正しくブロック出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, "aggregate")
    licenses_section = text.split("[Licenses]")[1]
    # biglib は原文が単独 → OSS名が1件だけのブロック
    assert "    biglib:" in licenses_section,         "単独OSSのブロックが正しく出力されていない"

@test("集約[Licenses]: セクション区切り文字が正しく出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, "aggregate")
    licenses_section = text.split("[Licenses]")[1]
    assert LICENSE_SEP in licenses_section, "LICENSE_SEP（70ハイフン）が出力に含まれない"
    assert TEXT_SEP in licenses_section,    "TEXT_SEP（40ハイフン）が出力に含まれない"

@test("集約[Licenses]: [Copyrights]には無いCopyright、[Licenses]には無いOSS名の混入がない")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, "aggregate")
    copyrights_section, licenses_section = text.split("[Licenses]")
    # [Copyrights]セクションにライセンス区切り文字が混入していない
    assert LICENSE_SEP not in copyrights_section,         "[Copyrights]セクションにLICENSE_SEPが混入している"

@test("集約: defaultフォーマットはCopyrights/Licensesセクションを持たない")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, "default")
    assert "[Copyrights]" not in text, "defaultに[Copyrights]が含まれている"
    assert "[Licenses]"   not in text, "defaultに[Licenses]が含まれている"


# ------------------------------------------------------------------ #
# エラーチェック
# ------------------------------------------------------------------ #
print("■ エラーチェック")

@test("新規エントリのAA列が空欄でエラー発生・列名がメッセージに含まれる")
def _():
    class BrokenWS:
        max_row = START_ROW
        def cell(self, row, column):
            data = {COL_A: 1, COL_B: "lib", COL_E: "MIT", COL_AA: "", COL_AB: "text"}
            return _Cell(data.get(column, None))

    try:
        _parse_worksheet(BrokenWS())
        raise AssertionError("例外が発生しなかった")
    except ValueError as e:
        assert "AA列" in str(e), f"エラーメッセージに列名が含まれない: {e}"

@test("B列が空欄でエラー発生")
def _():
    class BrokenWS:
        max_row = START_ROW
        def cell(self, row, column):
            data = {COL_A: 1, COL_B: ""}
            return _Cell(data.get(column, None))

    try:
        _parse_worksheet(BrokenWS())
        raise AssertionError("例外が発生しなかった")
    except ValueError as e:
        assert "B列" in str(e)


# ------------------------------------------------------------------ #
# 集計
# ------------------------------------------------------------------ #
total  = len(results)
passed = sum(1 for _, ok, _ in results if ok)
failed = total - passed

print()
print(f"結果: {passed}/{total} passed", end="")
if failed:
    print(f"  ({failed} failed)")
    sys.exit(1)
else:
    print("  ✓ 全テスト合格")
