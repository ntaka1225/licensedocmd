"""
テストランナー
各テストケースを実行し、結果を検証する。

Usage:
    python test_runner.py
"""

import sys
import traceback
from model import load_excel, DummyWorksheet, OSSData, START_ROW, COL_B, COL_E, COL_AA, COL_AB
from controller import generate_text, format_default

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

results = []


def test(name: str):
    """テストケースデコレータ"""
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
# テストケース                                                          #
# ------------------------------------------------------------------ #

@test("DummyWorksheet: cell() が正しい値を返す")
def _():
    ws = DummyWorksheet()
    assert ws.cell(row=START_ROW, column=COL_B).value == "requests", "OSS名が一致しない"
    assert ws.cell(row=START_ROW, column=COL_E).value == "Apache-2.0", "ライセンスが一致しない"
    assert ws.cell(row=START_ROW + 1, column=COL_B).value == "numpy"

@test("DummyWorksheet: データ範囲外は None を返す")
def _():
    ws = DummyWorksheet()
    assert ws.cell(row=1, column=1).value is None

@test("load_excel(use_dummy=True): OSSData が正しく生成される")
def _():
    data = load_excel(None, None, use_dummy=True)
    assert isinstance(data, OSSData)
    assert len(data.entries) == 3, f"件数が想定と異なる: {len(data.entries)}"

@test("load_excel(use_dummy=True): 各フィールドが正しく格納される")
def _():
    data = load_excel(None, None, use_dummy=True)
    e = data.entries[0]
    assert e.oss_name == "requests"
    assert e.license_name == "Apache-2.0"
    assert "Kenneth Reitz" in e.copyright
    assert "Apache License" in e.license_text

@test("generate_text: デフォルトフォーマットで出力される")
def _():
    data = load_excel(None, None, use_dummy=True)
    text = generate_text(data, None)
    assert "requests" in text
    assert "Apache-2.0" in text
    assert "Copyright" in text
    assert "---" in text
    assert "=" * 10 in text

@test("generate_text: 存在しないフォーマット名でValueError")
def _():
    data = load_excel(None, None, use_dummy=True)
    try:
        generate_text(data, "no_such_format")
        raise AssertionError("例外が発生しなかった")
    except ValueError:
        pass  # 期待通り

@test("空欄チェック: AA列が空のダミーでエラーが発生する")
def _():
    from model import _parse_worksheet, _Cell, START_ROW

    class BrokenWS:
        max_row = START_ROW
        def cell(self, row, column):
            data = {
                1: 1,        # A列
                2: "lib",    # B列
                5: "MIT",    # E列
                27: "",      # AA列 → 空欄
                28: "text",  # AB列
            }
            return _Cell(data.get(column, None))

    try:
        _parse_worksheet(BrokenWS())
        raise AssertionError("例外が発生しなかった")
    except ValueError as e:
        assert "AA列" in str(e), f"エラーメッセージに列名が含まれない: {e}"


# ------------------------------------------------------------------ #
# 集計                                                                  #
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
