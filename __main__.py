"""
Usage:
    python __main__.py <filename> <sheetname> [format]   # 通常実行
    python __main__.py --test [format]                   # ダミーデータでテスト実行

Arguments:
    filename   : 読み込むExcelファイルのパス
    sheetname  : 読み込むシート名
    format     : 出力フォーマット名（省略時はデフォルト）、"aggregate" で集約フォーマット
    --test     : Excelファイル不要のダミーデータで出力確認（フォーマット指定可）
"""

import sys
import os
from model import load_excel
from controller import generate_text, write_output


def main():
    args = sys.argv[1:]

    # --test オプションの判定
    if args and args[0] == "--test":
        format_name = args[1] if len(args) >= 2 else None
        _run_test(format_name)
        return

    # 通常実行
    if len(args) < 2:
        _print_usage()
        sys.exit(1)

    filepath    = args[0]
    sheetname   = args[1]
    format_name = args[2] if len(args) >= 3 else None

    if not os.path.isfile(filepath):
        print(f"エラー: ファイル '{filepath}' が見つかりません。")
        sys.exit(1)

    data = _load(filepath, sheetname, use_dummy=False)
    _output(data, format_name, output_path=f"{os.path.splitext(os.path.basename(filepath))[0]}_{sheetname}.txt")


def _run_test(format_name: str | None):
    print("[TEST] ダミーデータを使用してテスト実行します。")
    data = _load(filepath=None, sheetname=None, use_dummy=True)
    _output(data, format_name, output_path="test_output.txt")


def _load(filepath, sheetname, use_dummy: bool):
    try:
        return load_excel(filepath, sheetname, use_dummy=use_dummy)
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: Excelファイルの読み込みに失敗しました。({e})")
        sys.exit(1)


def _output(data, format_name, output_path: str):
    if not data.entries:
        print("エラー: 9行目以降にデータが存在しません。")
        sys.exit(1)

    try:
        text = generate_text(data, format_name)
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    write_output(text, output_path)
    print(f"出力完了: {output_path}  ({len(data.entries)} 件)")


def _print_usage():
    print(
        "使い方:\n"
        "  通常実行 : python __main__.py <filename> <sheetname> [format]\n"
        "  テスト実行: python __main__.py --test [format]"
    )


if __name__ == "__main__":
    main()
